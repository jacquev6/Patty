from typing import Any

import pydantic
from .base import (
    AssistantMessage,
    CompletionResponse,
    InvalidJsonAssistantMessage,
    InvalidJsonLlmException,
    JsonFromTextResponseFormat,
    JsonObjectResponseFormat,
    JsonSchemaResponseFormat,
    LlmException,
    NotJsonAssistantMessage,
    NotJsonLlmException,
    SystemMessage,
    UserMessage,
)
from .dummy import DummyModel
from .mistralai import MistralAiModel
from .openai import OpenAiModel
from .schema import make_schema


__all__ = [
    "AssistantMessage",
    "CompletionResponse",
    "ConcreteModel",
    "DummyModel",
    "InvalidJsonAssistantMessage",
    "InvalidJsonLlmException",
    "JsonFromTextResponseFormat",
    "JsonObjectResponseFormat",
    "JsonSchemaResponseFormat",
    "LlmException",
    "make_schema",
    "MistralAiModel",
    "NotJsonAssistantMessage",
    "NotJsonLlmException",
    "OpenAiModel",
    "SystemMessage",
    "UserMessage",
]


ConcreteModel = DummyModel | MistralAiModel | OpenAiModel


def validate(obj: Any) -> ConcreteModel:
    return pydantic.RootModel[ConcreteModel].model_validate(obj).root
