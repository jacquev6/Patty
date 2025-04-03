from typing import Literal, Type, TypeVar
import abc

import pydantic


T = TypeVar("T", bound=pydantic.BaseModel)


class SystemMessage(pydantic.BaseModel):
    role: Literal["system"] = "system"
    message: str


class UserMessage(pydantic.BaseModel):
    role: Literal["user"] = "user"
    message: str


class AssistantMessage[T](pydantic.BaseModel):
    role: Literal["assistant"] = "assistant"
    message: T


class Model(abc.ABC, pydantic.BaseModel):
    @abc.abstractmethod
    async def complete(
        self, messages: list[SystemMessage | UserMessage | AssistantMessage[T]], response_type: Type[T]
    ) -> AssistantMessage[T]: ...
