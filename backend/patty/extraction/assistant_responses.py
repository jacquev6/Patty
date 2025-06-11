from typing import Any, Literal

from ..extracted import Exercise
from ..api_utils import ApiModel


class AssistantSuccess(ApiModel):
    kind: Literal["success"]
    exercises: list[Exercise]


class AssistantInvalidJsonError(ApiModel):
    kind: Literal["error"]
    error: Literal["invalid-json"]
    parsed: Any


class AssistantNotJsonError(ApiModel):
    kind: Literal["error"]
    error: Literal["not-json"]
    text: str


class AssistantUnknownError(ApiModel):
    kind: Literal["error"]
    error: Literal["unknown"]


AssistantResponse = AssistantSuccess | AssistantInvalidJsonError | AssistantNotJsonError | AssistantUnknownError
