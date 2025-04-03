from typing import Literal, Type
import unittest

from polyfactory.factories.pydantic_factory import ModelFactory
import pydantic


from .base import T, Model, SystemMessage, UserMessage, AssistantMessage


class DummyModel(Model):
    provider: Literal["dummy"] = "dummy"
    name: Literal["dummy-1", "dummy-2", "dummy-3"]

    async def complete(
        self, messages: list[SystemMessage | UserMessage | AssistantMessage[T]], response_type: Type[T]
    ) -> AssistantMessage[T]:
        class MessageTypeFactory(ModelFactory[T]):
            __model__ = response_type
            __randomize_collection_length__ = True
            __min_collection_length__ = 2
            __max_collection_length__ = 5

        return AssistantMessage[T](message=MessageTypeFactory.build())


class DummyModelTestCase(unittest.IsolatedAsyncioTestCase):
    class Message(pydantic.BaseModel):
        cheese: str

    async def test(self) -> None:
        model = DummyModel(name="dummy-1")
        response = await model.complete(messages=[], response_type=DummyModelTestCase.Message)
        self.assertIsInstance(response.message, DummyModelTestCase.Message)

    async def test_adaptation_schema(self) -> None:
        from ..adapted import Exercise

        model = DummyModel(name="dummy-1")

        response = await model.complete(
            [UserMessage(message="Donne-moi une réponse respectant le schema JSON fourni.")], Exercise
        )
        self.assertIsInstance(response.message, Exercise)
