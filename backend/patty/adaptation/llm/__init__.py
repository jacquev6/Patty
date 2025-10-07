from typing import Any

import pydantic
from .base import (
    AssistantMessage as AssistantMessage,
    CompletionResponse as CompletionResponse,
    InvalidJsonAssistantMessage as InvalidJsonAssistantMessage,
    InvalidJsonLlmException as InvalidJsonLlmException,
    JsonFromTextResponseFormat as JsonFromTextResponseFormat,
    JsonObjectResponseFormat as JsonObjectResponseFormat,
    JsonSchemaResponseFormat as JsonSchemaResponseFormat,
    LlmException as LlmException,
    NotJsonAssistantMessage as NotJsonAssistantMessage,
    NotJsonLlmException as NotJsonLlmException,
    SystemMessage as SystemMessage,
    UserMessage as UserMessage,
)
from .dummy import DummyModel as DummyModel
from .gemini import GeminiModel as GeminiModel
from .mistralai import MistralAiModel as MistralAiModel
from .openai import OpenAiModel as OpenAiModel
from .schema import make_schema as make_schema


ConcreteModel = DummyModel | MistralAiModel | OpenAiModel | GeminiModel


def validate(obj: Any) -> ConcreteModel:
    return pydantic.RootModel[ConcreteModel].model_validate(obj).root
