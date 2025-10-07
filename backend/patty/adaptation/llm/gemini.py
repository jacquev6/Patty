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
        elif isinstance(response_format, JsonObjectResponseFormat):
            response_mime_type = "application/json"
        elif isinstance(response_format, JsonSchemaResponseFormat):
            logs.log("WARNING: Using JSON Schema is not supported by Gemini. Falling back to JSON object.")
            response_mime_type = "application/json"
        else:
            assert False

        response = client.models.generate_content(
            model=self.name,
            contents=typing.cast(list[google.genai.types.ContentUnion], contents),
            config=google.genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type=response_mime_type,
            ),
        )
        raw_conversation: dict[str, typing.Any] = dict(
            method="google.genai.Client.models.generate_content",
            config=dict(
                system_instruction=system_instruction,
                response_mime_type=response_mime_type,
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
