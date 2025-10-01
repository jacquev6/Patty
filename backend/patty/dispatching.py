import inspect
import typing
import unittest

from sqlalchemy import orm

from . import adaptation
from . import classification
from . import exercises
from . import extraction
from . import sandbox
from . import textbooks
from .database_utils import OrmBase


T1 = typing.TypeVar("T1")
T2 = typing.TypeVar("T2")
T3 = typing.TypeVar("T3")


def exercise_creation(
    exercise_creation: exercises.ExerciseCreation,
    *,
    by_user: typing.Callable[[exercises.ExerciseCreationByUser], T1] | None,
    by_page_extraction: typing.Callable[[extraction.ExerciseCreationByPageExtraction], T2] | None,
) -> T1 | T2:
    if isinstance(exercise_creation, exercises.ExerciseCreationByUser):
        assert by_user is not None
        return by_user(exercise_creation)
    elif isinstance(exercise_creation, extraction.ExerciseCreationByPageExtraction):
        assert by_page_extraction is not None
        return by_page_extraction(exercise_creation)
    else:
        assert False


def exercise_location(
    exercise_location: exercises.ExerciseLocation,
    *,
    textbook: typing.Callable[[textbooks.ExerciseLocationTextbook], T1] | None,
    maybe_page_and_number: typing.Callable[[exercises.ExerciseLocationMaybePageAndNumber], T2] | None,
) -> T1 | T2:
    if isinstance(exercise_location, textbooks.ExerciseLocationTextbook):
        assert textbook is not None
        return textbook(exercise_location)
    elif isinstance(exercise_location, exercises.ExerciseLocationMaybePageAndNumber):
        assert maybe_page_and_number is not None
        return maybe_page_and_number(exercise_location)
    else:
        assert False


def page_extraction_creation(
    page_extraction_creation: extraction.PageExtractionCreation,
    *,
    by_sandbox_batch: typing.Callable[[sandbox.extraction.PageExtractionCreationBySandboxBatch], T1] | None,
    by_textbook: typing.Callable[[textbooks.PageExtractionCreationByTextbook], T2] | None,
) -> T1 | T2:
    if isinstance(page_extraction_creation, sandbox.extraction.PageExtractionCreationBySandboxBatch):
        assert by_sandbox_batch is not None
        return by_sandbox_batch(page_extraction_creation)
    elif isinstance(page_extraction_creation, textbooks.PageExtractionCreationByTextbook):
        assert by_textbook is not None
        return by_textbook(page_extraction_creation)
    else:
        assert False


def classification_chunk_creation(
    classification_chunk_creation: classification.ClassificationChunkCreation,
    *,
    by_sandbox_batch: typing.Callable[[sandbox.classification.ClassificationChunkCreationBySandboxBatch], T1] | None,
    by_page_extraction: typing.Callable[[extraction.ClassificationChunkCreationByPageExtraction], T2] | None,
) -> T1 | T2:
    if isinstance(classification_chunk_creation, sandbox.classification.ClassificationChunkCreationBySandboxBatch):
        assert by_sandbox_batch is not None
        return by_sandbox_batch(classification_chunk_creation)
    elif isinstance(classification_chunk_creation, extraction.ClassificationChunkCreationByPageExtraction):
        assert by_page_extraction is not None
        return by_page_extraction(classification_chunk_creation)
    else:
        assert False


def adaptation_creation(
    adaptation_creation: adaptation.AdaptationCreation,
    *,
    by_chunk: typing.Callable[[classification.AdaptationCreationByChunk], T1] | None,
    by_sandbox_batch: typing.Callable[[sandbox.adaptation.AdaptationCreationBySandboxBatch], T2] | None,
) -> T1 | T2:
    if isinstance(adaptation_creation, classification.AdaptationCreationByChunk):
        assert by_chunk is not None
        return by_chunk(adaptation_creation)
    elif isinstance(adaptation_creation, sandbox.adaptation.AdaptationCreationBySandboxBatch):
        assert by_sandbox_batch is not None
        return by_sandbox_batch(adaptation_creation)
    else:
        assert False


class DispatchingTestCase(unittest.TestCase):
    def check(self, base: type[OrmBase], fn: typing.Any, missing: set[str] = set(), extra: set[str] = set()) -> None:
        actual = set(
            name for (name, param) in inspect.signature(fn).parameters.items() if param.kind is param.KEYWORD_ONLY
        )
        expected = set(orm.class_mapper(base).polymorphic_map.keys())
        self.assertSetEqual(actual | missing, expected | extra)

    def test_exercise_creation(self) -> None:
        self.check(exercises.ExerciseCreation, exercise_creation)

    def test_page_extraction_creation(self) -> None:
        self.check(extraction.PageExtractionCreation, page_extraction_creation)

    def test_classification_chunk_creation(self) -> None:
        self.check(classification.ClassificationChunkCreation, classification_chunk_creation)

    def test_adaptation_creation(self) -> None:
        self.check(adaptation.AdaptationCreation, adaptation_creation, missing={"by_user"})
