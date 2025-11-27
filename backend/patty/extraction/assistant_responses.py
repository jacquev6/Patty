from typing import Any, Literal

import pydantic

from .extracted import ExerciseV2, ExerciseV1
from ..api_utils import ApiModel


# Legacy
class SuccessV1(ApiModel):
    kind: Literal["success"]
    version: Literal["v1"]
    exercises: list[ExerciseV1]


# Starting with #92
class SuccessV2(ApiModel):
    kind: Literal["success"]
    version: Literal["v2"]
    exercises: list[ExerciseV2]


class InvalidJsonError(ApiModel):
    kind: Literal["error"]
    error: Literal["invalid-json"]
    parsed: Any


class NotJsonError(ApiModel):
    kind: Literal["error"]
    error: Literal["not-json"]
    text: str


class UnknownError(ApiModel):
    kind: Literal["error"]
    error: Literal["unknown"]


Response = SuccessV1 | SuccessV2 | InvalidJsonError | NotJsonError | UnknownError


def validate(obj: Any) -> Response:
    return pydantic.RootModel[Response].model_validate(obj).root
