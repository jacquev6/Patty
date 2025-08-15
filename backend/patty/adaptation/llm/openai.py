import json
from typing import Iterable, Literal
import os
import unittest

import openai
import openai.types.chat
import openai.types.shared_params

from .. import adapted
from ...any_json import JsonDict
from .base import (
    AssistantMessage,
    InvalidJsonAssistantMessage,
    JsonFromTextResponseFormat,
    JsonObjectResponseFormat,
    JsonSchemaResponseFormat,
    Model,
    NotJsonAssistantMessage,
    SystemMessage,
    UserMessage,
)
from .schema import make_schema
from ...test_utils import costs_money


# Using a global client; we'll do dependency injection at a higher abstraction level
client = openai.AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])


class OpenAiModel(Model):
    provider: Literal["openai"]
    name: Literal["gpt-4o-2024-08-06", "gpt-4o-mini-2024-07-18"]

    async def do_complete(
        self,
        messages_: list[
            SystemMessage | UserMessage | AssistantMessage | InvalidJsonAssistantMessage | NotJsonAssistantMessage
        ],
        response_format: JsonFromTextResponseFormat | JsonObjectResponseFormat | JsonSchemaResponseFormat,
    ) -> tuple[JsonDict, str]:
        messages = list(self.__make_messages(messages_))
        if isinstance(response_format, JsonSchemaResponseFormat):
            return await self.__do_complete__json_schema(messages, response_format.response_type)
        else:
            return await self.__do_complete__generic(messages, response_format)

    async def __do_complete__json_schema(
        self, messages: list[openai.types.chat.ChatCompletionMessageParam], response_format: type[adapted.Exercise]
    ) -> tuple[JsonDict, str]:
        response = await client.beta.chat.completions.parse(
            model=self.name, messages=messages, response_format=response_format
        )
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
        response_format_: JsonFromTextResponseFormat | JsonObjectResponseFormat,
    ) -> tuple[JsonDict, str]:
        response_format = self.__make_response_format(response_format_)
        response = await client.chat.completions.create(
            model=self.name, messages=messages, response_format=response_format
        )
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
            SystemMessage | UserMessage | AssistantMessage | InvalidJsonAssistantMessage | NotJsonAssistantMessage
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
        self, response_format: JsonFromTextResponseFormat | JsonObjectResponseFormat | JsonSchemaResponseFormat
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
    async def test_adaptation_schema(self) -> None:
        model = OpenAiModel(provider="openai", name="gpt-4o-mini-2024-07-18")

        response = await model.complete(
            [UserMessage(content="Donne-moi une réponse respectant le schema JSON fourni.")],
            JsonSchemaResponseFormat(response_type=adapted.Exercise),
        )
        self.assertIsInstance(response.message.content, adapted.Exercise)
