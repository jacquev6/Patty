import json
from typing import Iterable, Literal
import os
import unittest

import mistralai

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
client = mistralai.Mistral(api_key=os.environ["MISTRALAI_API_KEY"])


class MistralAiModel(Model):
    provider: Literal["mistralai"]
    name: Literal["mistral-large-2411", "mistral-small-2501"]

    async def do_complete(
        self,
        messages_: list[
            SystemMessage | UserMessage | AssistantMessage | InvalidJsonAssistantMessage | NotJsonAssistantMessage
        ],
        response_format_: JsonFromTextResponseFormat | JsonObjectResponseFormat | JsonSchemaResponseFormat,
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
            SystemMessage | UserMessage | AssistantMessage | InvalidJsonAssistantMessage | NotJsonAssistantMessage
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
        self, response_format: JsonFromTextResponseFormat | JsonObjectResponseFormat | JsonSchemaResponseFormat
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
    async def test_adaptation_schema(self) -> None:
        model = MistralAiModel(provider="mistralai", name="mistral-small-2501")

        response = await model.complete(
            [UserMessage(content="Donne-moi une réponse respectant le schema JSON fourni.")],
            JsonSchemaResponseFormat(response_type=adapted.Exercise),
        )
        self.assertIsInstance(response.message.content, adapted.Exercise)
