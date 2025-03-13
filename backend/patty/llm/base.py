from typing import Literal, Type
import abc

import pydantic

from .utils import T


class SystemMessage(pydantic.BaseModel):
    role: Literal["system"] = "system"
    message: str


class UserMessage(pydantic.BaseModel):
    role: Literal["user"] = "user"
    message: str


class AssistantMessage[E](pydantic.BaseModel):
    role: Literal["assistant"] = "assistant"
    prose: str
    structured: E


class Model(abc.ABC, pydantic.BaseModel):
    @abc.abstractmethod
    async def complete(
        self, messages: list[SystemMessage | UserMessage | AssistantMessage[T]], structured_type: Type[T]
    ) -> AssistantMessage[T]: ...
