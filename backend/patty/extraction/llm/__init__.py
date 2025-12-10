# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

from typing import Any

import pydantic

from .base import InvalidJsonLlmException, NotJsonLlmException
from .dummy import DummyModel
from .gemini import GeminiModel


__all__ = ["ConcreteModel", "DummyModel", "GeminiModel", "InvalidJsonLlmException", "NotJsonLlmException"]

ConcreteModel = DummyModel | GeminiModel


def validate(obj: Any) -> ConcreteModel:
    return pydantic.RootModel[ConcreteModel].model_validate(obj).root
