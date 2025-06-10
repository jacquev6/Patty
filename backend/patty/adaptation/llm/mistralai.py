import json
from typing import Iterable, Literal
import os
import unittest

import mistralai
import pydantic

from ...any_json import JsonDict
from .base import (
    AssistantMessage,
    InvalidJsonAssistantMessage,
    JsonFromTextResponseFormat,
    JsonObjectResponseFormat,
    JsonSchemaResponseFormat,
    LlmException,
    Model,
    NotJsonAssistantMessage,
    SystemMessage,
    T,
    try_hard_to_json_loads,
    UserMessage,
)
from .schema import make_schema
from ...test_utils import costs_money


# Using a global client; we'll do dependency injection at a higher abstraction level
client = mistralai.Mistral(api_key=os.environ["MISTRALAI_API_KEY"])


class MistralAiModel(Model):
    provider: Literal["mistralai"] = "mistralai"
    name: Literal["mistral-large-2411", "mistral-small-2501"]

    async def do_complete(
        self,
        messages_: list[
            SystemMessage | UserMessage | AssistantMessage[T] | InvalidJsonAssistantMessage | NotJsonAssistantMessage
        ],
        response_format_: JsonFromTextResponseFormat[T] | JsonObjectResponseFormat[T] | JsonSchemaResponseFormat[T],
    ) -> tuple[JsonDict, str]:
        messages = list(self.__make_messages(messages_))
        response_format = self.__make_response_format(response_format_)
        response = await client.chat.complete_async(model=self.name, messages=messages, response_format=response_format)
        raw_conversation = dict(
            method="mistralai.Mistral.chat.complete_async",
            messages=[m.model_dump() for m in messages],
            response_format=response_format.model_dump(by_alias=True),
            response=response.model_dump(),
        )
        assert response.choices is not None
        assert len(response.choices) > 0
        assert response.choices[0].message is not None
        assert isinstance(response.choices[0].message.content, str)
        return (raw_conversation, response.choices[0].message.content)

    def __make_messages(
        self,
        messages: Iterable[
            SystemMessage | UserMessage | AssistantMessage[T] | InvalidJsonAssistantMessage | NotJsonAssistantMessage
        ],
    ) -> Iterable[mistralai.models.Messages]:
        for message in messages:
            if isinstance(message, SystemMessage):
                yield mistralai.models.SystemMessage(content=message.content)
            elif isinstance(message, UserMessage):
                yield mistralai.models.UserMessage(content=message.content)
            elif isinstance(message, AssistantMessage):
                yield mistralai.models.AssistantMessage(content=message.content.model_dump_json())
            elif isinstance(message, InvalidJsonAssistantMessage):
                yield mistralai.models.AssistantMessage(content=json.dumps(message.content))
            elif isinstance(message, NotJsonAssistantMessage):
                yield mistralai.models.AssistantMessage(content=message.content)
            else:
                raise ValueError(f"Unknown message type: {message}")

    def __make_response_format(
        self, response_format: JsonFromTextResponseFormat[T] | JsonObjectResponseFormat[T] | JsonSchemaResponseFormat[T]
    ) -> mistralai.ResponseFormat:
        if isinstance(response_format, JsonFromTextResponseFormat):
            return mistralai.ResponseFormat(type="text")
        elif isinstance(response_format, JsonObjectResponseFormat):
            return mistralai.ResponseFormat(type="json_object")
        elif isinstance(response_format, JsonSchemaResponseFormat):
            return mistralai.ResponseFormat(
                type="json_schema",
                json_schema=mistralai.JSONSchema(
                    name=response_format.response_type.__name__,
                    schema_definition=make_schema(response_format.response_type),
                ),
            )
        else:
            raise ValueError(f"Unknown response format: {response_format}")


class MistralAiModelTestCase(unittest.IsolatedAsyncioTestCase):
    maxDiff = None

    def setUp(self) -> None:
        super().setUp()
        # Avoid "RuntimeError: Event loop is closed" (see https://stackoverflow.com/a/76249506/905845)
        global client
        client = mistralai.Mistral(api_key=os.environ["MISTRALAI_API_KEY"])

    @costs_money
    async def test_json_schema(self) -> None:
        class Response(pydantic.BaseModel):
            prose: str

            class Structured(pydantic.BaseModel):
                cheese: str

            structured: Structured

        model = MistralAiModel(name="mistral-small-2501")

        messages: list[
            SystemMessage
            | UserMessage
            | AssistantMessage[Response]
            | InvalidJsonAssistantMessage
            | NotJsonAssistantMessage
        ] = [
            SystemMessage(
                content="Utilise le champ `prose` pour tes commentaires, et le champs `structured` pour le contenu de ta réponse. Dans ce champs, donne des réponses aussi concises que possible."
            ),
            UserMessage(content="Donne-moi le nom d'un fromage."),
        ]

        response1 = await model.complete(messages, JsonSchemaResponseFormat(response_type=Response))
        self.assertEqual(response1.raw_conversation["method"], "mistralai.Mistral.chat.complete_async")
        self.assertEqual(
            response1.raw_conversation["messages"],
            [
                {
                    "content": "Utilise le champ `prose` pour tes commentaires, et le champs `structured` pour le contenu de ta réponse. Dans ce champs, donne des réponses aussi concises que possible.",
                    "role": "system",
                },
                {"content": "Donne-moi le nom d'un fromage.", "role": "user"},
            ],
        )
        self.assertEqual(
            response1.raw_conversation["response_format"],
            {
                "type": "json_schema",
                "json_schema": {
                    "name": "Response",
                    "schema": {
                        "$defs": {
                            "Structured": {
                                "additionalProperties": False,
                                "properties": {"cheese": {"title": "Cheese", "type": "string"}},
                                "required": ["cheese"],
                                "title": "Structured",
                                "type": "object",
                            }
                        },
                        "additionalProperties": False,
                        "properties": {
                            "prose": {"title": "Prose", "type": "string"},
                            "structured": {"$ref": "#/$defs/Structured"},
                        },
                        "required": ["prose", "structured"],
                        "title": "Response",
                        "type": "object",
                    },
                },
            },
        )
        content1 = Response(**json.loads(response1.raw_conversation["response"]["choices"][0]["message"]["content"]))
        self.assertEqual(response1.message.content, content1)

        messages.append(response1.message)
        messages.append(UserMessage(content="Un autre."))

        response2 = await model.complete(messages, JsonSchemaResponseFormat(response_type=Response))
        self.assertEqual(response2.raw_conversation["method"], "mistralai.Mistral.chat.complete_async")
        self.assertEqual(
            response2.raw_conversation["messages"],
            [
                {
                    "content": "Utilise le champ `prose` pour tes commentaires, et le champs `structured` pour le contenu de ta réponse. Dans ce champs, donne des réponses aussi concises que possible.",
                    "role": "system",
                },
                {"content": "Donne-moi le nom d'un fromage.", "role": "user"},
                {"content": content1.model_dump_json(), "prefix": False, "role": "assistant"},
                {"content": "Un autre.", "role": "user"},
            ],
        )
        self.assertEqual(
            response2.raw_conversation["response_format"],
            {
                "type": "json_schema",
                "json_schema": {
                    "name": "Response",
                    "schema": {
                        "$defs": {
                            "Structured": {
                                "additionalProperties": False,
                                "properties": {"cheese": {"title": "Cheese", "type": "string"}},
                                "required": ["cheese"],
                                "title": "Structured",
                                "type": "object",
                            }
                        },
                        "additionalProperties": False,
                        "properties": {
                            "prose": {"title": "Prose", "type": "string"},
                            "structured": {"$ref": "#/$defs/Structured"},
                        },
                        "required": ["prose", "structured"],
                        "title": "Response",
                        "type": "object",
                    },
                },
            },
        )
        content2 = Response(**json.loads(response2.raw_conversation["response"]["choices"][0]["message"]["content"]))
        self.assertEqual(response2.message.content, content2)

        self.assertNotEqual(response2.message.content.structured.cheese, response1.message.content.structured.cheese)

    @costs_money
    async def test_json_object(self) -> None:
        class Response(pydantic.BaseModel):
            a: int
            b: int

        model = MistralAiModel(name="mistral-small-2501")

        messages: list[
            SystemMessage
            | UserMessage
            | AssistantMessage[Response]
            | InvalidJsonAssistantMessage
            | NotJsonAssistantMessage
        ] = [UserMessage(content="Donne-moi un objet JSON avec deux champs, `a` et `b`, contenant des entiers.")]
        response = await model.complete(messages, JsonObjectResponseFormat(response_type=Response))
        self.assertEqual(response.raw_conversation["method"], "mistralai.Mistral.chat.complete_async")
        self.assertEqual(
            response.raw_conversation["messages"],
            [
                {
                    "content": "Donne-moi un objet JSON avec deux champs, `a` et `b`, contenant des entiers.",
                    "role": "user",
                }
            ],
        )
        self.assertEqual(response.raw_conversation["response_format"], {"type": "json_object"})
        content = Response(**json.loads(response.raw_conversation["response"]["choices"][0]["message"]["content"]))
        self.assertEqual(response.message.content, content)

    @costs_money
    async def test_bad_json_object(self) -> None:
        class Response(pydantic.BaseModel):
            a: str
            b: str

        model = MistralAiModel(name="mistral-small-2501")

        messages: list[
            SystemMessage
            | UserMessage
            | AssistantMessage[Response]
            | InvalidJsonAssistantMessage
            | NotJsonAssistantMessage
        ] = [UserMessage(content="Donne-moi un objet JSON avec deux champs, `a` et `b`, contenant des entiers.")]
        with self.assertRaises(LlmException) as cm:
            await model.complete(messages, JsonObjectResponseFormat(response_type=Response))
        self.assertEqual(cm.exception.args[0], "Failed to validate JSON response")
        self.assertEqual(cm.exception.raw_conversation["method"], "mistralai.Mistral.chat.complete_async")
        self.assertEqual(
            cm.exception.raw_conversation["messages"],
            [
                {
                    "content": "Donne-moi un objet JSON avec deux champs, `a` et `b`, contenant des entiers.",
                    "role": "user",
                }
            ],
        )
        self.assertEqual(cm.exception.raw_conversation["response_format"], {"type": "json_object"})

    @costs_money
    async def test_json_from_text(self) -> None:
        class Response(pydantic.BaseModel):
            a: int
            b: int

        model = MistralAiModel(name="mistral-small-2501")

        messages: list[
            SystemMessage
            | UserMessage
            | AssistantMessage[Response]
            | InvalidJsonAssistantMessage
            | NotJsonAssistantMessage
        ] = [
            UserMessage(
                content="Donne-moi un objet JSON avec deux champs, `a` et `b`, contenant des entiers. Donne-moi uniquement cet objet, sans aucun commentaire."
            )
        ]
        response = await model.complete(messages, JsonFromTextResponseFormat(response_type=Response))
        self.assertEqual(response.raw_conversation["method"], "mistralai.Mistral.chat.complete_async")
        self.assertEqual(
            response.raw_conversation["messages"],
            [
                {
                    "content": "Donne-moi un objet JSON avec deux champs, `a` et `b`, contenant des entiers. Donne-moi uniquement cet objet, sans aucun commentaire.",
                    "role": "user",
                }
            ],
        )
        self.assertEqual(response.raw_conversation["response_format"], {"type": "text"})
        content = Response(
            **try_hard_to_json_loads(response.raw_conversation["response"]["choices"][0]["message"]["content"])
        )
        self.assertEqual(response.message.content, content)

    @costs_money
    async def test_bad_json_from_text(self) -> None:
        class Response(pydantic.BaseModel):
            a: int
            b: int

        model = MistralAiModel(name="mistral-small-2501")

        messages: list[
            SystemMessage
            | UserMessage
            | AssistantMessage[Response]
            | InvalidJsonAssistantMessage
            | NotJsonAssistantMessage
        ] = [UserMessage(content="Bonjour!")]

        with self.assertRaises(LlmException) as cm:
            await model.complete(messages, JsonFromTextResponseFormat(response_type=Response))
        self.assertEqual(cm.exception.args[0], "Failed to parse JSON response")
        self.assertEqual(cm.exception.raw_conversation["method"], "mistralai.Mistral.chat.complete_async")
        self.assertEqual(cm.exception.raw_conversation["messages"], [{"content": "Bonjour!", "role": "user"}])
        self.assertEqual(cm.exception.raw_conversation["response_format"], {"type": "text"})
        self.assertIn("bonjour", cm.exception.raw_conversation["response"]["choices"][0]["message"]["content"].lower())

    @costs_money
    async def test_adaptation_schema(self) -> None:
        from ...adapted import Exercise

        model = MistralAiModel(name="mistral-small-2501")

        response = await model.complete(
            [UserMessage(content="Donne-moi une réponse respectant le schema JSON fourni.")],
            JsonSchemaResponseFormat(response_type=Exercise),
        )
        self.assertIsInstance(response.message.content, Exercise)
