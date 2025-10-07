from __future__ import annotations
import json
import typing
import unittest

import google.genai.types
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


client = google.genai.Client(api_key=settings.GEMINIAI_KEY)


class GeminiModel(Model):
    provider: typing.Literal["gemini"]
    name: typing.Literal["gemini-2.0-flash"]

    async def do_complete(
        self,
        messages: list[
            SystemMessage | UserMessage | AssistantMessage[T] | InvalidJsonAssistantMessage | NotJsonAssistantMessage
        ],
        response_format: JsonFromTextResponseFormat[T] | JsonObjectResponseFormat[T] | JsonSchemaResponseFormat[T],
    ) -> tuple[JsonDict, str]:
        if isinstance(messages[0], SystemMessage):
            system_instruction = messages[0].content
            messages = messages[1:]
        else:
            system_instruction = None

        contents = list(self.__make_messages(messages))

        if isinstance(response_format, JsonFromTextResponseFormat):
            response_mime_type = "text/plain"
            # response_schema = None
            # response_json_schema = None
        elif isinstance(response_format, JsonObjectResponseFormat):
            response_mime_type = "application/json"
            # response_schema = None
            # response_json_schema = None
        elif isinstance(response_format, JsonSchemaResponseFormat):
            logs.log("WARNING: Using JSON Schema is not supported by Gemini. Falling back to JSON object.")
            response_mime_type = "application/json"
            # response_schema = response_format.response_type
            # response_json_schema = replace_const_with_enum(make_non_recursive_schema(response_format.response_type))
            # print("Response JSON Schema:", json.dumps(response_json_schema, indent=2, ensure_ascii=False))
        else:
            assert False

        response = client.models.generate_content(
            model=self.name,
            contents=typing.cast(list[google.genai.types.ContentUnion], contents),
            config=google.genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type=response_mime_type,
                # response_schema=response_schema,
                # response_json_schema=response_json_schema,
            ),
        )
        raw_conversation: dict[str, typing.Any] = dict(
            method="google.genai.Client.models.generate_content",
            config=dict(
                system_instruction=system_instruction,
                response_mime_type=response_mime_type,
                # response_json_schema=response_json_schema,
            ),
            contents=[m.model_dump() for m in contents],
            response=response.model_dump(),
        )
        response_text = response.text
        assert isinstance(response_text, str)
        return raw_conversation, response_text

    def __make_messages(
        self,
        messages: typing.Iterable[
            SystemMessage | UserMessage | AssistantMessage[T] | InvalidJsonAssistantMessage | NotJsonAssistantMessage
        ],
    ) -> typing.Iterable[google.genai.types.Content]:
        for message in messages:
            if isinstance(message, UserMessage):
                yield google.genai.types.Content(
                    role="user", parts=[google.genai.types.Part.from_text(text=message.content)]
                )
            elif isinstance(message, AssistantMessage):
                yield google.genai.types.Content(
                    role="model", parts=[google.genai.types.Part.from_text(text=message.content.model_dump_json())]
                )
            elif isinstance(message, InvalidJsonAssistantMessage):
                yield google.genai.types.Content(
                    role="model", parts=[google.genai.types.Part.from_text(text=json.dumps(message.content))]
                )
            elif isinstance(message, NotJsonAssistantMessage):
                yield google.genai.types.Content(
                    role="model", parts=[google.genai.types.Part.from_text(text=message.content)]
                )
            else:
                raise ValueError(f"Unknown message type: {message}")


class GeminiModelTestCase(unittest.IsolatedAsyncioTestCase):
    maxDiff = None

    # @costs_money
    # async def test_json_schema(self) -> None:
    #     class Response(pydantic.BaseModel):
    #         prose: str

    #         class Structured(pydantic.BaseModel):
    #             cheese: str

    #         structured: Structured

    #     model = GeminiModel(provider="gemini", name="gemini-2.0-flash")

    #     messages: list[
    #         SystemMessage
    #         | UserMessage
    #         | AssistantMessage[Response]
    #         | InvalidJsonAssistantMessage
    #         | NotJsonAssistantMessage
    #     ] = [
    #         SystemMessage(
    #             content="Utilise le champ `prose` pour tes commentaires, et le champs `structured` pour le contenu de ta réponse. Dans ce champs, donne des réponses aussi concises que possible."
    #         ),
    #         UserMessage(content="Donne-moi le nom d'un fromage."),
    #     ]

    #     response1 = await model.complete(messages, JsonSchemaResponseFormat(response_type=Response))
    #     self.assertEqual(response1.raw_conversation["method"], "google.genai.Client.models.generate_content")
    #     self.assertEqual(
    #         response1.raw_conversation["config"]["system_instruction"],
    #         "Utilise le champ `prose` pour tes commentaires, et le champs `structured` pour le contenu de ta réponse. Dans ce champs, donne des réponses aussi concises que possible.",
    #     )
    #     self.assertEqual(response1.raw_conversation["config"]["response_mime_type"], "application/json")
    #     self.assertEqual(
    #         response1.raw_conversation["config"]["response_json_schema"],
    #         {
    #             "$defs": {
    #                 "Structured": {
    #                     "additionalProperties": False,
    #                     "properties": {"cheese": {"title": "Cheese", "type": "string"}},
    #                     "required": ["cheese"],
    #                     "title": "Structured",
    #                     "type": "object",
    #                 }
    #             },
    #             "additionalProperties": False,
    #             "properties": {
    #                 "prose": {"title": "Prose", "type": "string"},
    #                 "structured": {"$ref": "#/$defs/Structured"},
    #             },
    #             "required": ["prose", "structured"],
    #             "title": "Response",
    #             "type": "object",
    #         },
    #     )
    #     self.assertEqual(
    #         response1.raw_conversation["contents"],
    #         [
    #             {
    #                 "parts": [
    #                     {
    #                         "video_metadata": None,
    #                         "thought": None,
    #                         "inline_data": None,
    #                         "file_data": None,
    #                         "thought_signature": None,
    #                         "code_execution_result": None,
    #                         "executable_code": None,
    #                         "function_call": None,
    #                         "function_response": None,
    #                         "text": "Donne-moi le nom d'un fromage.",
    #                     }
    #                 ],
    #                 "role": "user",
    #             }
    #         ],
    #     )
    #     content1 = Response(
    #         **json.loads(response1.raw_conversation["response"]["candidates"][0]["content"]["parts"][0]["text"])
    #     )
    #     self.assertEqual(response1.message.content, content1)

    #     messages.append(response1.message)
    #     messages.append(UserMessage(content="Un autre."))

    #     response2 = await model.complete(messages, JsonSchemaResponseFormat(response_type=Response))
    #     self.assertEqual(response2.raw_conversation["method"], "google.genai.Client.models.generate_content")
    #     self.assertEqual(
    #         response2.raw_conversation["config"]["system_instruction"],
    #         "Utilise le champ `prose` pour tes commentaires, et le champs `structured` pour le contenu de ta réponse. Dans ce champs, donne des réponses aussi concises que possible.",
    #     )
    #     self.assertEqual(response2.raw_conversation["config"]["response_mime_type"], "application/json")
    #     self.assertEqual(
    #         response2.raw_conversation["config"]["response_json_schema"],
    #         {
    #             "$defs": {
    #                 "Structured": {
    #                     "additionalProperties": False,
    #                     "properties": {"cheese": {"title": "Cheese", "type": "string"}},
    #                     "required": ["cheese"],
    #                     "title": "Structured",
    #                     "type": "object",
    #                 }
    #             },
    #             "additionalProperties": False,
    #             "properties": {
    #                 "prose": {"title": "Prose", "type": "string"},
    #                 "structured": {"$ref": "#/$defs/Structured"},
    #             },
    #             "required": ["prose", "structured"],
    #             "title": "Response",
    #             "type": "object",
    #         },
    #     )
    #     self.assertEqual(
    #         response2.raw_conversation["contents"],
    #         [
    #             {
    #                 "parts": [
    #                     {
    #                         "video_metadata": None,
    #                         "thought": None,
    #                         "inline_data": None,
    #                         "file_data": None,
    #                         "thought_signature": None,
    #                         "code_execution_result": None,
    #                         "executable_code": None,
    #                         "function_call": None,
    #                         "function_response": None,
    #                         "text": "Donne-moi le nom d'un fromage.",
    #                     }
    #                 ],
    #                 "role": "user",
    #             },
    #             {
    #                 "parts": [
    #                     {
    #                         "video_metadata": None,
    #                         "thought": None,
    #                         "inline_data": None,
    #                         "file_data": None,
    #                         "thought_signature": None,
    #                         "code_execution_result": None,
    #                         "executable_code": None,
    #                         "function_call": None,
    #                         "function_response": None,
    #                         "text": content1.model_dump_json(),
    #                     }
    #                 ],
    #                 "role": "model",
    #             },
    #             {
    #                 "parts": [
    #                     {
    #                         "video_metadata": None,
    #                         "thought": None,
    #                         "inline_data": None,
    #                         "file_data": None,
    #                         "thought_signature": None,
    #                         "code_execution_result": None,
    #                         "executable_code": None,
    #                         "function_call": None,
    #                         "function_response": None,
    #                         "text": "Un autre.",
    #                     }
    #                 ],
    #                 "role": "user",
    #             },
    #         ],
    #     )
    #     content2 = Response(
    #         **json.loads(response2.raw_conversation["response"]["candidates"][0]["content"]["parts"][0]["text"])
    #     )
    #     self.assertEqual(response2.message.content, content2)

    #     self.assertNotEqual(response2.message.content.structured.cheese, response1.message.content.structured.cheese)

    @costs_money
    async def test_json_object(self) -> None:
        class Response(pydantic.BaseModel):
            a: int
            b: int

        model = GeminiModel(provider="gemini", name="gemini-2.0-flash")

        messages: list[
            SystemMessage
            | UserMessage
            | AssistantMessage[Response]
            | InvalidJsonAssistantMessage
            | NotJsonAssistantMessage
        ] = [UserMessage(content="Donne-moi un objet JSON avec deux champs, `a` et `b`, contenant des entiers.")]
        response = await model.complete(messages, JsonObjectResponseFormat(response_type=Response))
        self.assertEqual(response.raw_conversation["method"], "google.genai.Client.models.generate_content")
        self.assertIsNone(response.raw_conversation["config"]["system_instruction"])
        self.assertEqual(response.raw_conversation["config"]["response_mime_type"], "application/json")
        # self.assertIsNone(response.raw_conversation["config"]["response_json_schema"])
        self.assertEqual(
            response.raw_conversation["contents"],
            [
                {
                    "parts": [
                        {
                            "video_metadata": None,
                            "thought": None,
                            "inline_data": None,
                            "file_data": None,
                            "thought_signature": None,
                            "code_execution_result": None,
                            "executable_code": None,
                            "function_call": None,
                            "function_response": None,
                            "text": "Donne-moi un objet JSON avec deux champs, `a` et `b`, contenant des entiers.",
                        }
                    ],
                    "role": "user",
                }
            ],
        )
        content = Response(
            **json.loads(response.raw_conversation["response"]["candidates"][0]["content"]["parts"][0]["text"])
        )
        self.assertEqual(response.message.content, content)

    @costs_money
    async def test_bad_json_object(self) -> None:
        class Response(pydantic.BaseModel):
            a: str
            b: str

        model = GeminiModel(provider="gemini", name="gemini-2.0-flash")

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
        self.assertEqual(cm.exception.raw_conversation["method"], "google.genai.Client.models.generate_content")
        self.assertIsNone(cm.exception.raw_conversation["config"]["system_instruction"])
        self.assertEqual(cm.exception.raw_conversation["config"]["response_mime_type"], "application/json")
        # self.assertIsNone(cm.exception.raw_conversation["config"]["response_json_schema"])
        self.assertEqual(
            cm.exception.raw_conversation["contents"],
            [
                {
                    "parts": [
                        {
                            "video_metadata": None,
                            "thought": None,
                            "inline_data": None,
                            "file_data": None,
                            "thought_signature": None,
                            "code_execution_result": None,
                            "executable_code": None,
                            "function_call": None,
                            "function_response": None,
                            "text": "Donne-moi un objet JSON avec deux champs, `a` et `b`, contenant des entiers.",
                        }
                    ],
                    "role": "user",
                }
            ],
        )

    @costs_money
    async def test_json_from_text(self) -> None:
        class Response(pydantic.BaseModel):
            a: int
            b: int

        model = GeminiModel(provider="gemini", name="gemini-2.0-flash")

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
        self.assertEqual(response.raw_conversation["method"], "google.genai.Client.models.generate_content")
        self.assertIsNone(response.raw_conversation["config"]["system_instruction"])
        self.assertEqual(response.raw_conversation["config"]["response_mime_type"], "text/plain")
        # self.assertIsNone(response.raw_conversation["config"]["response_json_schema"])
        self.assertEqual(
            response.raw_conversation["contents"],
            [
                {
                    "parts": [
                        {
                            "video_metadata": None,
                            "thought": None,
                            "inline_data": None,
                            "file_data": None,
                            "thought_signature": None,
                            "code_execution_result": None,
                            "executable_code": None,
                            "function_call": None,
                            "function_response": None,
                            "text": "Donne-moi un objet JSON avec deux champs, `a` et `b`, contenant des entiers. Donne-moi uniquement cet objet, sans aucun commentaire.",
                        }
                    ],
                    "role": "user",
                }
            ],
        )
        content = Response(
            **try_hard_to_json_loads(
                response.raw_conversation["response"]["candidates"][0]["content"]["parts"][0]["text"]
            )
        )
        self.assertEqual(response.message.content, content)

    @costs_money
    async def test_bad_json_from_text(self) -> None:
        class Response(pydantic.BaseModel):
            a: int
            b: int

        model = GeminiModel(provider="gemini", name="gemini-2.0-flash")

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
        self.assertEqual(cm.exception.raw_conversation["method"], "google.genai.Client.models.generate_content")
        self.assertIsNone(cm.exception.raw_conversation["config"]["system_instruction"])
        self.assertEqual(cm.exception.raw_conversation["config"]["response_mime_type"], "text/plain")
        # self.assertIsNone(cm.exception.raw_conversation["config"]["response_json_schema"])
        self.assertEqual(
            cm.exception.raw_conversation["contents"],
            [
                {
                    "parts": [
                        {
                            "video_metadata": None,
                            "thought": None,
                            "inline_data": None,
                            "file_data": None,
                            "thought_signature": None,
                            "code_execution_result": None,
                            "executable_code": None,
                            "function_call": None,
                            "function_response": None,
                            "text": "Bonjour!",
                        }
                    ],
                    "role": "user",
                }
            ],
        )
        self.assertIn(
            "bonjour", cm.exception.raw_conversation["response"]["candidates"][0]["content"]["parts"][0]["text"].lower()
        )

    # @costs_money
    # async def test_schema_with_single_valued_literal(self) -> None:
    #     class Response(pydantic.BaseModel):
    #         a: typing.Literal["foo"]

    #     model = GeminiModel(provider="gemini", name="gemini-2.0-flash")

    #     response = await model.complete(
    #         [UserMessage(content="Donne-moi une réponse respectant le schema JSON fourni.")],
    #         JsonSchemaResponseFormat(response_type=Response),
    #     )
    #     self.assertIsInstance(response.message.content, Response)
    #     self.assertEqual(response.message.content.a, "foo")

    # @costs_money
    # async def test_schema_with_multiple_valued_literal(self) -> None:
    #     class Response(pydantic.BaseModel):
    #         a: typing.Literal["foo", "bar"]

    #     model = GeminiModel(provider="gemini", name="gemini-2.0-flash")

    #     response = await model.complete(
    #         [UserMessage(content="Donne-moi une réponse respectant le schema JSON fourni.")],
    #         JsonSchemaResponseFormat(response_type=Response),
    #     )
    #     self.assertIsInstance(response.message.content, Response)
    #     self.assertIn(response.message.content.a, ["foo", "bar"])

    # @costs_money
    # async def test_recursive_schema_1(self) -> None:
    #     class A(pydantic.BaseModel):
    #         t: A | None

    #     model = GeminiModel(provider="gemini", name="gemini-2.0-flash")

    #     response = await model.complete(
    #         [UserMessage(content="Donne-moi une réponse respectant le schema JSON fourni.")],
    #         JsonSchemaResponseFormat(response_type=A),
    #     )
    #     self.assertIsInstance(response.message.content, A)
    #     print(response.message.content)

    # @costs_money
    # async def test_recursive_schema_2(self) -> None:
    #     class A(pydantic.BaseModel):
    #         b: B | None

    #     class B(pydantic.BaseModel):
    #         a: A | None

    #     model = GeminiModel(provider="gemini", name="gemini-2.0-flash")

    #     response = await model.complete(
    #         [UserMessage(content="Donne-moi une réponse respectant le schema JSON fourni.")],
    #         JsonSchemaResponseFormat(response_type=A),
    #     )
    #     self.assertIsInstance(response.message.content, A)
    #     print(response.message.content)

    # @costs_money
    # async def test_minimal_adaptation_schema(self) -> None:
    #     from .. import adapted

    #     Exercise = adapted.make_partial_exercise_type(
    #         adapted.Components(
    #             instruction=adapted.InstructionComponents(
    #                 text=True, whitespace=True, arrow=True, formatted=True, image=True, choice=False
    #             ),
    #             example=adapted.ExampleComponents(
    #                 text=True, whitespace=True, arrow=True, formatted=True, image=True
    #             ),
    #             hint=adapted.HintComponents(text=True, whitespace=True, arrow=True, formatted=True, image=True),
    #             statement=adapted.StatementComponents(
    #                 text=True,
    #                 whitespace=True,
    #                 arrow=True,
    #                 formatted=True,
    #                 image=True,
    #                 free_text_input=False,
    #                 multiple_choices_input=False,
    #                 selectable_input=False,
    #                 swappable_input=False,
    #                 editable_text_input=False,
    #                 split_word_input=False,
    #             ),
    #             reference=adapted.ReferenceComponents(
    #                 text=True, whitespace=True, arrow=True, formatted=True, image=True
    #             ),
    #         )
    #     )

    #     model = GeminiModel(provider="gemini", name="gemini-2.0-flash")

    #     response = await model.complete(
    #         [UserMessage(content="Donne-moi une réponse respectant le schema JSON fourni.")],
    #         JsonSchemaResponseFormat(response_type=Exercise),
    #     )
    #     self.assertIsInstance(response.message.content, Exercise)
    #     print("Response:", response.message.content.model_dump())

    # @costs_money
    # async def test_full_adaptation_schema(self) -> None:
    #     from .. import adapted

    #     Exercise = adapted.make_partial_exercise_type(
    #         adapted.Components(
    #             instruction=adapted.InstructionComponents(
    #                 text=True, whitespace=True, arrow=True, formatted=True, image=True, choice=True
    #             ),
    #             example=adapted.ExampleComponents(
    #                 text=True, whitespace=True, arrow=True, formatted=True, image=True
    #             ),
    #             hint=adapted.HintComponents(text=True, whitespace=True, arrow=True, formatted=True, image=True),
    #             statement=adapted.StatementComponents(
    #                 text=True,
    #                 whitespace=True,
    #                 arrow=True,
    #                 formatted=True,
    #                 image=True,
    #                 free_text_input=True,
    #                 multiple_choices_input=True,
    #                 selectable_input=True,
    #                 swappable_input=True,
    #                 editable_text_input=True,
    #                 split_word_input=True,
    #             ),
    #             reference=adapted.ReferenceComponents(
    #                 text=True, whitespace=True, arrow=True, formatted=True, image=True
    #             ),
    #         )
    #     )

    #     model = GeminiModel(provider="gemini", name="gemini-2.0-flash")

    #     response = await model.complete(
    #         [UserMessage(content="Donne-moi une réponse respectant le schema JSON fourni.")],
    #         JsonSchemaResponseFormat(response_type=Exercise),
    #     )
    #     self.assertIsInstance(response.message.content, Exercise)
    #     print("Response:", response.message.content.model_dump())

    # @costs_money
    # async def test_adaptation_schema_v1(self) -> None:
    #     from ..adapted import ExerciseV1

    #     model = GeminiModel(provider="gemini", name="gemini-2.0-flash")

    #     response = await model.complete(
    #         [UserMessage(content="Donne-moi une réponse respectant le schema JSON fourni.")],
    #         JsonSchemaResponseFormat(response_type=ExerciseV1),
    #     )
    #     self.assertIsInstance(response.message.content, ExerciseV1)
    #     print("Response:", response.message.content.model_dump())

    # @costs_money
    # async def test_adaptation_schema_v2(self) -> None:
    #     from ..adapted import ExerciseV2

    #     model = GeminiModel(provider="gemini", name="gemini-2.0-flash")

    #     response = await model.complete(
    #         [UserMessage(content="Donne-moi une réponse respectant le schema JSON fourni.")],
    #         JsonSchemaResponseFormat(response_type=ExerciseV2),
    #     )
    #     self.assertIsInstance(response.message.content, ExerciseV2)
    #     print("Response:", response.message.content.model_dump())

    # @costs_money
    # async def test_adaptation_schema(self) -> None:
    #     from ..adapted import Exercise

    #     model = GeminiModel(provider="gemini", name="gemini-2.0-flash")

    #     response = await model.complete(
    #         [UserMessage(content="Donne-moi une réponse respectant le schema JSON fourni.")],
    #         JsonSchemaResponseFormat(response_type=Exercise),
    #     )
    #     self.assertIsInstance(response.message.content, Exercise)
    #     print("Response:", response.message.content.model_dump())
