from typing import Any, Literal, TypeVar
import abc
import json

import pydantic

from ...any_json import JsonDict


T = TypeVar("T", bound=pydantic.BaseModel)


class SystemMessage(pydantic.BaseModel):
    role: Literal["system"] = "system"
    content: str


class UserMessage(pydantic.BaseModel):
    role: Literal["user"] = "user"
    content: str


class AssistantMessage[T](pydantic.BaseModel):
    role: Literal["assistant"] = "assistant"
    content: T


class InvalidJsonAssistantMessage(pydantic.BaseModel):
    role: Literal["assistant"] = "assistant"
    content: Any


class NotJsonAssistantMessage(pydantic.BaseModel):
    role: Literal["assistant"] = "assistant"
    content: str


class CompletionResponse[T](pydantic.BaseModel):
    raw_conversation: JsonDict
    message: AssistantMessage[T]


class JsonFromTextResponseFormat[T](pydantic.BaseModel):
    response_type: type[T]


class JsonObjectResponseFormat[T](pydantic.BaseModel):
    response_type: type[T]


class JsonSchemaResponseFormat[T](pydantic.BaseModel):
    response_type: type[T]


class LlmException(RuntimeError):
    def __init__(self, *args: object, raw_conversation: JsonDict) -> None:
        super().__init__(*args)
        self.raw_conversation = raw_conversation


class InvalidJsonLlmException(LlmException):
    def __init__(self, parsed: Any, raw_conversation: JsonDict) -> None:
        super().__init__("Failed to validate JSON response", raw_conversation=raw_conversation)
        self.parsed = parsed


class NotJsonLlmException(LlmException):
    def __init__(self, text: str, raw_conversation: JsonDict) -> None:
        super().__init__("Failed to parse JSON response", raw_conversation=raw_conversation)
        self.text = text


def try_hard_to_json_loads(s: str) -> Any:
    preprocessed = s
    if preprocessed.startswith("```json") and preprocessed.endswith("```"):
        preprocessed = preprocessed[7:-3]
    elif preprocessed.startswith("```") and preprocessed.endswith("```"):
        preprocessed = preprocessed[3:-3]

    return json.loads(preprocessed)


class Model(abc.ABC, pydantic.BaseModel):
    async def complete(
        self,
        /,
        messages: list[
            SystemMessage | UserMessage | AssistantMessage[T] | InvalidJsonAssistantMessage | NotJsonAssistantMessage
        ],
        response_format: JsonFromTextResponseFormat[T] | JsonObjectResponseFormat[T] | JsonSchemaResponseFormat[T],
    ) -> CompletionResponse[T]:
        (raw_conversation, response) = await self.do_complete(messages, response_format)

        try:
            parsed_content = try_hard_to_json_loads(response)
        except json.JSONDecodeError:
            raise NotJsonLlmException(response, raw_conversation)

        try:
            validated_content = response_format.response_type(**parsed_content)
        except pydantic.ValidationError:
            raise InvalidJsonLlmException(parsed_content, raw_conversation)

        return CompletionResponse(
            raw_conversation=raw_conversation, message=AssistantMessage(content=validated_content)
        )

    @abc.abstractmethod
    async def do_complete(
        self,
        messages: list[
            SystemMessage | UserMessage | AssistantMessage[T] | InvalidJsonAssistantMessage | NotJsonAssistantMessage
        ],
        response_format: JsonFromTextResponseFormat[T] | JsonObjectResponseFormat[T] | JsonSchemaResponseFormat[T],
    ) -> tuple[JsonDict, str]: ...
