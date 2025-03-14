from typing import Type, TypeVar
import typing

import pydantic

T = TypeVar("T")


class ResponseFormat[E](pydantic.BaseModel):
    prose: str
    structured: E | None


def make_response_format_type(structured_type: Type[T]) -> Type[ResponseFormat[T]]:
    return typing.cast(
        Type[ResponseFormat[T]],
        pydantic.create_model("ResponseFormat", prose=(str, ...), structured=(structured_type, ...)),
    )
