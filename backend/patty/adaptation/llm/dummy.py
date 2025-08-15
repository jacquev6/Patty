from typing import Literal
import asyncio
import unittest

from polyfactory.factories.pydantic_factory import ModelFactory


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


class DummyModel(Model):
    provider: Literal["dummy"]
    name: Literal["dummy-1", "dummy-2", "dummy-3"]

    async def do_complete(
        self,
        messages: list[
            SystemMessage | UserMessage | AssistantMessage | InvalidJsonAssistantMessage | NotJsonAssistantMessage
        ],
        response_format: JsonFromTextResponseFormat | JsonObjectResponseFormat | JsonSchemaResponseFormat,
    ) -> tuple[JsonDict, str]:
        class MessageTypeFactory(ModelFactory[adapted.Exercise]):
            __model__ = response_format.response_type
            __randomize_collection_length__ = True
            __min_collection_length__ = 2
            __max_collection_length__ = 5

        assert len(messages) != 0
        assert messages[-1].role == "user"
        content = messages[-1].content

        def raise_exception() -> str:
            raise Exception("Unknown error from DummyModel")

        if self.name == "dummy-3":
            MessageTypeFactory.seed_random(42)

        response = {
            "Not JSON": lambda: "This is not JSON.",
            "Invalid JSON": lambda: "{}",
            "Unknown error": raise_exception,
        }.get(content, lambda: MessageTypeFactory.build().model_dump_json())()

        duration = 0.1
        if content.startswith("Sleep "):
            duration = float(content[6:])

        await asyncio.sleep(duration)

        return ({"dummy": "conversation"}, response)


class DummyModelTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_adaptation_schema(self) -> None:
        from ..adapted import Exercise

        model = DummyModel(provider="dummy", name="dummy-1")

        response = await model.complete(
            [UserMessage(content="Donne-moi une réponse respectant le schema JSON fourni.")],
            JsonSchemaResponseFormat(response_type=Exercise),
        )
        self.assertIsInstance(response.message.content, Exercise)
