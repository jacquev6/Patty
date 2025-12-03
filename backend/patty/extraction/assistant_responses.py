from typing import Any, Literal

import pydantic

from .extracted import ExerciseV1, ExerciseV2, ExerciseV3
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


# Starting with #176
class SuccessV3(ApiModel):
    kind: Literal["success"]
    version: Literal["v3"]
    raw_response: str
    cleaned_response: str
    exercises: list[ExerciseV3]


class InvalidJsonErrorV2(ApiModel):
    kind: Literal["error"]
    error: Literal["invalid-json"]
    version: Literal["v2"]
    parsed: Any


class InvalidJsonErrorV3(ApiModel):
    kind: Literal["error"]
    error: Literal["invalid-json"]
    version: Literal["v3"]
    raw_response: str
    cleaned_response: str
    parsed: Any


class NotJsonErrorV2(ApiModel):
    kind: Literal["error"]
    error: Literal["not-json"]
    version: Literal["v2"]
    text: str


class NotJsonErrorV3(ApiModel):
    kind: Literal["error"]
    error: Literal["not-json"]
    version: Literal["v3"]
    raw_response: str
    cleaned_response: str


class UnknownError(ApiModel):
    kind: Literal["error"]
    error: Literal["unknown"]


Response = (
    SuccessV1
    | SuccessV2
    | SuccessV3
    | InvalidJsonErrorV2
    | InvalidJsonErrorV3
    | NotJsonErrorV2
    | NotJsonErrorV3
    | UnknownError
)


def validate(obj: Any) -> Response:
    return pydantic.RootModel[Response].model_validate(obj).root
