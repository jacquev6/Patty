from typing import Any, Literal

from ..adapted import Exercise
from ..api_utils import ApiModel


class AssistantSuccess(ApiModel):
    kind: Literal["success"]
    exercise: Exercise


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


class Adjustment(ApiModel):
    user_prompt: str
    assistant_response: AssistantResponse
