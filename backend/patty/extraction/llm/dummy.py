from typing import Literal

from polyfactory.factories.pydantic_factory import ModelFactory
import PIL.Image
import pydantic

from ...extracted import Exercise
from .base import Model


ExercisesList = pydantic.RootModel[list[Exercise]]


class DummyModel(Model):
    provider: Literal["dummy"] = "dummy"
    name: Literal["dummy-1", "dummy-2", "dummy-3"]

    def do_extract(self, prompt: str, image: PIL.Image.Image) -> str:
        class ExerciseListFactory(ModelFactory[ExercisesList]):
            __model__ = ExercisesList
            __randomize_collection_length__ = True
            __min_collection_length__ = 2
            __max_collection_length__ = 5

        return ExerciseListFactory.build().model_dump_json()
