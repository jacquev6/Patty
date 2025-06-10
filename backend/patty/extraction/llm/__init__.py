from .dummy import DummyModel
from .gemini import GeminiModel


__all__ = ["ConcreteModel", "DummyModel", "GeminiModel"]

ConcreteModel = DummyModel | GeminiModel
