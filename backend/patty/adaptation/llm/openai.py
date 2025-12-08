# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

import json
from typing import Iterable, Literal
import unittest

import openai
import openai.types.chat
import openai.types.shared_params
import pydantic

from ... import logs
from ... import settings
from ...any_json import JsonDict
from ...test_utils import costs_money
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


# Using a global client; we'll do dependency injection at a higher abstraction level
client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class OpenAiModel(Model):
    provider: Literal["openai"]
    name: Literal[
        "gpt-4o-2024-08-06",
        "gpt-4o-mini-2024-07-18",
        "gpt-4.1-2025-04-14",
        "gpt-4.1-mini-2025-04-14",
        "gpt-4.1-nano-2025-04-14",
    ]

    async def do_complete(
        self,
        messages_: list[
            SystemMessage | UserMessage | AssistantMessage[T] | InvalidJsonAssistantMessage | NotJsonAssistantMessage
        ],
        response_format: JsonFromTextResponseFormat[T] | JsonObjectResponseFormat[T] | JsonSchemaResponseFormat[T],
    ) -> tuple[JsonDict, str]:
        messages = list(self.__make_messages(messages_))
        if isinstance(response_format, JsonSchemaResponseFormat):
            return await self.__do_complete__json_schema(messages, response_format.response_type)
        else:
            return await self.__do_complete__generic(messages, response_format)

    async def __do_complete__json_schema(
        self, messages: list[openai.types.chat.ChatCompletionMessageParam], response_format: type[T]
    ) -> tuple[JsonDict, str]:
        with logs.timer() as t:
            response = await client.beta.chat.completions.parse(
                model=self.name, messages=messages, response_format=response_format
            )
        logs.log_for_issue_129(f"'openai.AsyncOpenAI.beta.chat.completions.parse' took {t.elapsed:.1f} seconds")
        # @todo Work out the magic happening in the call above, and that does not happen in:
        # response = await client.chat.completions.create(
        #     model=self.name,
        #     messages=messages,
        #     response_format=self.__make_response_format(response_format),
        # )
        # resulting in message.content not respecting the JSON schema.
        # Then, homogenize the two calls to always use 'client.chat.completions.create'.
        raw_conversation = dict(
            method="openai.AsyncOpenAI.beta.chat.completions.parse",
            messages=messages,
            response_format=dict(kind="type", name=response_format.__name__, schema=make_schema(response_format)),
            response=response.model_dump(),
        )
        assert len(response.choices) > 0
        assert isinstance(response.choices[0].message.content, str)
        return (raw_conversation, response.choices[0].message.content)

    async def __do_complete__generic(
        self,
        messages: list[openai.types.chat.ChatCompletionMessageParam],
        response_format_: JsonFromTextResponseFormat[T] | JsonObjectResponseFormat[T],
    ) -> tuple[JsonDict, str]:
        response_format = self.__make_response_format(response_format_)
        with logs.timer() as t:
            response = await client.chat.completions.create(
                model=self.name, messages=messages, response_format=response_format
            )
        logs.log_for_issue_129(f"'openai.AsyncOpenAI.chat.completions.create' took {t.elapsed:.1f} seconds")
        raw_conversation = dict(
            method="openai.AsyncOpenAI.chat.completions.create",
            messages=messages,
            response_format=response_format,
            response=response.model_dump(),
        )
        assert len(response.choices) > 0
        assert isinstance(response.choices[0].message.content, str)
        return (raw_conversation, response.choices[0].message.content)

    def __make_messages(
        self,
        messages: Iterable[
            SystemMessage | UserMessage | AssistantMessage[T] | InvalidJsonAssistantMessage | NotJsonAssistantMessage
        ],
    ) -> Iterable[openai.types.chat.ChatCompletionMessageParam]:
        for message in messages:
            if isinstance(message, SystemMessage):
                yield openai.types.chat.ChatCompletionDeveloperMessageParam(role="developer", content=message.content)
            elif isinstance(message, UserMessage):
                yield openai.types.chat.ChatCompletionUserMessageParam(role="user", content=message.content)
            elif isinstance(message, AssistantMessage):
                yield openai.types.chat.ChatCompletionAssistantMessageParam(
                    role="assistant", content=message.content.model_dump_json()
                )
            elif isinstance(message, InvalidJsonAssistantMessage):
                yield openai.types.chat.ChatCompletionAssistantMessageParam(
                    role="assistant", content=json.dumps(message.content)
                )
            elif isinstance(message, NotJsonAssistantMessage):
                yield openai.types.chat.ChatCompletionAssistantMessageParam(role="assistant", content=message.content)
            else:
                raise ValueError(f"Unknown message type: {message}")

    def __make_response_format(
        self, response_format: JsonFromTextResponseFormat[T] | JsonObjectResponseFormat[T] | JsonSchemaResponseFormat[T]
    ) -> openai.types.chat.completion_create_params.ResponseFormat:
        if isinstance(response_format, JsonFromTextResponseFormat):
            return openai.types.shared_params.response_format_text.ResponseFormatText(type="text")
        elif isinstance(response_format, JsonObjectResponseFormat):
            return openai.types.shared_params.response_format_json_object.ResponseFormatJSONObject(type="json_object")
        # elif isinstance(response_format, JsonSchemaResponseFormat):
        #     return openai.types.shared_params.response_format_json_schema.ResponseFormatJSONSchema(
        #         type="json_schema",
        #         json_schema=openai.types.shared_params.response_format_json_schema.JSONSchema(
        #             name=response_format.response_type.__name__, schema=make_schema(response_format.response_type)
        #         ),
        #     )
        else:
            raise ValueError(f"Unknown response format: {response_format}")


class OpenAiModelTestCase(unittest.IsolatedAsyncioTestCase):
    maxDiff = None

    @costs_money
    async def test_json_schema(self) -> None:
        class Response(pydantic.BaseModel):
            prose: str

            class Structured(pydantic.BaseModel):
                cheese: str

            structured: Structured

        model = OpenAiModel(provider="openai", name="gpt-4o-mini-2024-07-18")

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
        self.assertEqual(response1.raw_conversation["method"], "openai.AsyncOpenAI.beta.chat.completions.parse")
        self.assertEqual(
            response1.raw_conversation["messages"],
            [
                {
                    "content": "Utilise le champ `prose` pour tes commentaires, et le champs `structured` pour le contenu de ta réponse. Dans ce champs, donne des réponses aussi concises que possible.",
                    "role": "developer",
                },
                {"content": "Donne-moi le nom d'un fromage.", "role": "user"},
            ],
        )
        self.assertEqual(
            response1.raw_conversation["response_format"],
            {
                "kind": "type",
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
        )

        content1 = Response.model_validate(
            json.loads(response1.raw_conversation["response"]["choices"][0]["message"]["content"])
        )
        self.assertEqual(response1.message.content, content1)

        messages.append(response1.message)
        messages.append(UserMessage(content="Un autre."))

        response2 = await model.complete(messages, JsonSchemaResponseFormat(response_type=Response))
        self.assertEqual(response2.raw_conversation["method"], "openai.AsyncOpenAI.beta.chat.completions.parse")
        self.assertEqual(
            response2.raw_conversation["messages"],
            [
                {
                    "content": "Utilise le champ `prose` pour tes commentaires, et le champs `structured` pour le contenu de ta réponse. Dans ce champs, donne des réponses aussi concises que possible.",
                    "role": "developer",
                },
                {"content": "Donne-moi le nom d'un fromage.", "role": "user"},
                {"content": content1.model_dump_json(), "role": "assistant"},
                {"content": "Un autre.", "role": "user"},
            ],
        )
        self.assertEqual(
            response2.raw_conversation["response_format"],
            {
                "kind": "type",
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
        )
        content2 = Response.model_validate(
            json.loads(response2.raw_conversation["response"]["choices"][0]["message"]["content"])
        )
        self.assertEqual(response2.message.content, content2)

        self.assertNotEqual(response1.message.content.structured.cheese, response2.message.content.structured.cheese)

    @costs_money
    async def test_json_object(self) -> None:
        class Response(pydantic.BaseModel):
            a: int
            b: int

        model = OpenAiModel(provider="openai", name="gpt-4o-mini-2024-07-18")

        messages: list[
            SystemMessage
            | UserMessage
            | AssistantMessage[Response]
            | InvalidJsonAssistantMessage
            | NotJsonAssistantMessage
        ] = [UserMessage(content="Donne-moi un objet JSON avec deux champs, `a` et `b`, contenant des entiers.")]
        response = await model.complete(messages, JsonObjectResponseFormat(response_type=Response))
        self.assertEqual(response.raw_conversation["method"], "openai.AsyncOpenAI.chat.completions.create")
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
        content = Response.model_validate(
            json.loads(response.raw_conversation["response"]["choices"][0]["message"]["content"])
        )
        self.assertEqual(response.message.content, content)

    @costs_money
    async def test_json_from_text(self) -> None:
        class Response(pydantic.BaseModel):
            a: int
            b: int

        model = OpenAiModel(provider="openai", name="gpt-4o-mini-2024-07-18")

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
        self.assertEqual(response.raw_conversation["method"], "openai.AsyncOpenAI.chat.completions.create")
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
        content = Response.model_validate(
            try_hard_to_json_loads(response.raw_conversation["response"]["choices"][0]["message"]["content"])
        )
        self.assertEqual(response.message.content, content)

    @costs_money
    async def test_bad_json_from_text(self) -> None:
        class Response(pydantic.BaseModel):
            a: int
            b: int

        model = OpenAiModel(provider="openai", name="gpt-4o-mini-2024-07-18")

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
        self.assertEqual(cm.exception.raw_conversation["method"], "openai.AsyncOpenAI.chat.completions.create")
        self.assertEqual(cm.exception.raw_conversation["messages"], [{"content": "Bonjour!", "role": "user"}])
        self.assertEqual(cm.exception.raw_conversation["response_format"], {"type": "text"})
        self.assertIn("bonjour", cm.exception.raw_conversation["response"]["choices"][0]["message"]["content"].lower())

    @costs_money
    async def test_adaptation_schema(self) -> None:
        from ..adapted import Exercise

        model = OpenAiModel(provider="openai", name="gpt-4o-mini-2024-07-18")

        response = await model.complete(
            [UserMessage(content="Donne-moi une réponse respectant le schema JSON fourni.")],
            JsonSchemaResponseFormat(response_type=Exercise),
        )
        self.assertIsInstance(response.message.content, Exercise)
