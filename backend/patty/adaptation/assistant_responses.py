from typing import Any, Literal

import pydantic

from .adapted import Exercise
from ..api_utils import ApiModel


class Success(ApiModel):
    kind: Literal["success"]
    exercise: Exercise


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


Response = Success | InvalidJsonError | NotJsonError | UnknownError


def validate(obj: Any) -> Response:
    return pydantic.RootModel[Response].model_validate(obj).root


class Adjustment(ApiModel):
    user_prompt: str
    assistant_response: Response
