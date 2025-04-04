from .base import Model as AbstractModel, SystemMessage, UserMessage, AssistantMessage
from .dummy import DummyModel
from .mistralai import MistralAiModel
from .openai import OpenAiModel


__all__ = [
    "AbstractModel",
    "AssistantMessage",
    "ConcreteModel",
    "DummyModel",
    "MistralAiModel",
    "OpenAiModel",
    "SystemMessage",
    "UserMessage",
]


ConcreteModel = DummyModel | MistralAiModel | OpenAiModel
