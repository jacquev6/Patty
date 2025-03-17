from typing import Literal, Type
import unittest

from polyfactory.factories.pydantic_factory import ModelFactory
import pydantic


from .base import Model, SystemMessage, UserMessage, AssistantMessage
from .utils import T


class DummyModel(Model):
    provider: Literal["dummy"] = "dummy"
    name: Literal["dummy-1", "dummy-2", "dummy-3"]

    async def complete(
        self, messages: list[SystemMessage | UserMessage | AssistantMessage[T]], structured_type: Type[T]
    ) -> AssistantMessage[T]:
        class StructuredTypeFactory(ModelFactory[T]):  # type: ignore
            __model__ = structured_type
            __randomize_collection_length__ = True
            __min_collection_length__ = 2
            __max_collection_length__ = 5

        return AssistantMessage[T](prose="Hello", structured=StructuredTypeFactory.build())


class DummyModelTestCase(unittest.IsolatedAsyncioTestCase):
    class Structured(pydantic.BaseModel):
        cheese: str

    async def test(self) -> None:
        model = DummyModel(name="dummy-1")
        response = await model.complete(messages=[], structured_type=DummyModelTestCase.Structured)
        self.assertIsInstance(response.structured, DummyModelTestCase.Structured)
