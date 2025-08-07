from __future__ import annotations

import datetime
from typing import Iterable

from sqlalchemy import orm
import sqlalchemy as sql
import pydantic

from .extraction import assistant_responses as extraction_responses
from .adaptation import adaptation as adaptation_responses
from .adaptation import llm as adaptation_llm
from .adaptation.strategy import ConcreteLlmResponseSpecification
from .adapted import Exercise as AdaptedExercise
from .any_json import JsonDict, JsonList
from .database_utils import OrmBase, annotate_new_tables
from .extraction import llm as extraction_llm


# @todo(After schema migration d710f60075da and data migration) Remove attributes suffixed '__to_be_deleted'


class CreatedByUserMixin:
    # @todo Rename "created_by_username" to "created_by"
    created_by_username: orm.Mapped[str] = orm.mapped_column()
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))


# Base exercises
# ##############


class ExerciseCreation(OrmBase):
    __tablename__ = "exercise_creations"
    __mapper_args__ = {"polymorphic_on": "kind"}

    def __init__(self, *, at: datetime.datetime) -> None:
        super().__init__()
        self.at = at

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    kind: orm.Mapped[str]
    at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))

    exercise: orm.Mapped[BaseExercise] = orm.relationship(back_populates="created")


class ExerciseCreationByUser(ExerciseCreation):
    __tablename__ = "exercise_creations__by_user"
    __mapper_args__ = {"polymorphic_identity": "by_user"}

    def __init__(self, *, at: datetime.datetime, username: str) -> None:
        super().__init__(at=at)
        self.username = username

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseCreation.id), primary_key=True)
    username: orm.Mapped[str] = orm.mapped_column()


class ExerciseLocation(OrmBase):
    __tablename__ = "exercise_locations"
    __mapper_args__ = {"polymorphic_on": "kind"}

    def __init__(self) -> None:
        super().__init__()

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    kind: orm.Mapped[str]

    exercise: orm.Mapped[BaseExercise] = orm.relationship(back_populates="location")


class ExerciseLocationMaybePageAndNumber(ExerciseLocation):
    __tablename__ = "exercise_locations__maybe_page_and_number"
    __mapper_args__ = {"polymorphic_identity": "maybe_page_and_number"}

    def __init__(self, page_number: int | None, exercise_number: str | None) -> None:
        super().__init__()
        self.page_number = page_number
        self.exercise_number = exercise_number

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseLocation.id), primary_key=True)
    page_number: orm.Mapped[int | None]
    # Custom collation: migrations/versions/429d2fb463dd_exercise_number_collation.py
    exercise_number: orm.Mapped[str | None] = orm.mapped_column(sql.String(collation="exercise_number"))


class BaseExercise(OrmBase):
    __tablename__ = "exercises"
    __mapper_args__ = {"polymorphic_on": "kind"}

    def __init__(self, *, created: ExerciseCreation, location: ExerciseLocation, removed_from_textbook: bool) -> None:
        super().__init__()
        self.created = created
        self.location = location
        self.removed_from_textbook = removed_from_textbook

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    kind: orm.Mapped[str]

    created_at__to_be_deleted: orm.Mapped[datetime.datetime | None] = orm.mapped_column(
        "created_at", sql.DateTime(timezone=True)
    )
    created_by_username__to_be_deleted: orm.Mapped[str | None] = orm.mapped_column("created_by_username")

    textbook_id__to_be_deleted: orm.Mapped[int | None] = orm.mapped_column("textbook_id")
    removed_from_textbook: orm.Mapped[bool]
    page_number__to_be_deleted: orm.Mapped[int | None] = orm.mapped_column("page_number")
    exercise_number__to_be_deleted: orm.Mapped[str | None] = orm.mapped_column(
        "exercise_number", sql.String(collation="exercise_number")
    )

    # @todo(After schema migration d710f60075da and data migration) Make 'created_id' non-nullable
    created_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(ExerciseCreation.id))
    created: orm.Mapped[ExerciseCreation | None] = orm.relationship(
        foreign_keys=[created_id], remote_side=[ExerciseCreation.id], back_populates="exercise"
    )
    # @todo(After schema migration d710f60075da and data migration) Make 'location_id' non-nullable
    location_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(ExerciseLocation.id))
    location: orm.Mapped[ExerciseLocation | None] = orm.relationship(
        foreign_keys=[location_id], remote_side=[ExerciseLocation.id], back_populates="exercise"
    )


annotate_new_tables("exercises")


# External exercises
# ##################


class ExternalExercise(BaseExercise):
    __tablename__ = "external_exercises"
    __mapper_args__ = {"polymorphic_identity": "external"}

    def __init__(
        self,
        *,
        created: ExerciseCreation,
        location: ExerciseLocation,
        removed_from_textbook: bool,
        original_file_name: str,
    ) -> None:
        super().__init__(created=created, location=location, removed_from_textbook=removed_from_textbook)
        self.original_file_name = original_file_name

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(BaseExercise.id), primary_key=True)

    original_file_name: orm.Mapped[str]


annotate_new_tables("external")


# Extraction
# ##########


class PdfFile(OrmBase, CreatedByUserMixin):
    __tablename__ = "pdf_files"

    def __init__(
        self,
        *,
        created_at: datetime.datetime,
        created_by_username: str,
        sha256: str,
        bytes_count: int,
        pages_count: int,
        known_file_names: list[str],
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by_username = created_by_username
        self.sha256 = sha256
        self.bytes_count = bytes_count
        self.pages_count = pages_count
        self.known_file_names = known_file_names

    sha256: orm.Mapped[str] = orm.mapped_column(primary_key=True)
    bytes_count: orm.Mapped[int]
    pages_count: orm.Mapped[int]
    known_file_names: orm.Mapped[list[str]] = orm.mapped_column(sql.JSON)


class PdfFileRange(OrmBase, CreatedByUserMixin):
    __tablename__ = "pdf_file_ranges"

    def __init__(
        self,
        *,
        created_at: datetime.datetime,
        created_by_username: str,
        pdf_file_sha256: str,
        pdf_file_first_page_number: int,
        pages_count: int,
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by_username = created_by_username
        self.pdf_file_sha256 = pdf_file_sha256
        self.pdf_file_first_page_number = pdf_file_first_page_number
        self.pages_count = pages_count

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    pdf_file_sha256: orm.Mapped[str] = orm.mapped_column(sql.ForeignKey(PdfFile.sha256))
    pdf_file: orm.Mapped[PdfFile] = orm.relationship(foreign_keys=[pdf_file_sha256], remote_side=[PdfFile.sha256])
    pdf_file_first_page_number: orm.Mapped[int]
    pages_count: orm.Mapped[int]


class ExtractionStrategy(OrmBase, CreatedByUserMixin):
    __tablename__ = "extraction_strategies"

    def __init__(
        self,
        *,
        created_at: datetime.datetime,
        created_by_username: str,
        model: extraction_llm.ConcreteModel,
        prompt: str,
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by_username = created_by_username
        self.model = model
        self.prompt = prompt

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    _model: orm.Mapped[JsonDict] = orm.mapped_column("model", sql.JSON)

    @property
    def model(self) -> extraction_llm.ConcreteModel:
        return pydantic.RootModel[extraction_llm.ConcreteModel](self._model).root  # type: ignore[arg-type]

    @model.setter
    def model(self, value: extraction_llm.ConcreteModel) -> None:
        self._model = value.model_dump()

    prompt: orm.Mapped[str]


class PageExtractionCreation(OrmBase):
    __tablename__ = "page_extraction_creations"
    __mapper_args__ = {"polymorphic_on": "kind"}

    def __init__(self, *, at: datetime.datetime) -> None:
        super().__init__()
        self.at = at

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    kind: orm.Mapped[str]
    at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))

    page_extraction: orm.Mapped[PageExtraction] = orm.relationship(back_populates="created")


class PageExtraction(OrmBase):
    __tablename__ = "page_extractions"

    def __init__(
        self,
        *,
        created: PageExtractionCreation,
        page_number: int,
        range: PdfFileRange,
        strategy: ExtractionStrategy,
        run_classification: bool,
        model_for_adaptation: adaptation_llm.ConcreteModel | None,
        assistant_response: extraction_responses.AssistantResponse | None,
    ) -> None:
        super().__init__()
        self.created = created
        self.page_number = page_number
        self.range = range
        self.strategy = strategy
        self.run_classification = run_classification
        self.model_for_adaptation = model_for_adaptation
        self.assistant_response = assistant_response

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(PageExtractionCreation.id))
    created: orm.Mapped[PageExtractionCreation | None] = orm.relationship(
        foreign_keys=[created_id], remote_side=[PageExtractionCreation.id], back_populates="page_extraction"
    )
    created_at__to_be_deleted: orm.Mapped[datetime.datetime | None] = orm.mapped_column(
        "created_at", sql.DateTime(timezone=True)
    )
    created_by_username__to_be_deleted: orm.Mapped[str | None] = orm.mapped_column("created_by_username")
    extraction_batch_id__to_be_deleted: orm.Mapped[int | None] = orm.mapped_column("extraction_batch_id")

    page_number: orm.Mapped[int]

    # @todo(After schema migration d710f60075da and data migration) Make 'range_id' non-nullable
    range_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(PdfFileRange.id))
    range: orm.Mapped[PdfFileRange | None] = orm.relationship(foreign_keys=[range_id], remote_side=[PdfFileRange.id])

    # @todo(After schema migration d710f60075da and data migration) Make 'strategy_id' non-nullable
    strategy_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(ExtractionStrategy.id))
    strategy: orm.Mapped[ExtractionStrategy | None] = orm.relationship(
        foreign_keys=[strategy_id], remote_side=[ExtractionStrategy.id]
    )

    # @todo(After schema migration d710f60075da and data migration) Make 'run_classification' non-nullable
    run_classification: orm.Mapped[bool | None]

    _model_for_adaptation: orm.Mapped[JsonDict | None] = orm.mapped_column("model_for_adaptation", sql.JSON)

    @property
    def model_for_adaptation(self) -> adaptation_llm.ConcreteModel | None:
        if self._model_for_adaptation is None:
            return None
        else:
            return pydantic.RootModel[adaptation_llm.ConcreteModel](self._model_for_adaptation).root  # type: ignore[arg-type]

    @model_for_adaptation.setter
    def model_for_adaptation(self, value: adaptation_llm.ConcreteModel | None) -> None:
        if value is None:
            self._model_for_adaptation = sql.null()
        else:
            self._model_for_adaptation = value.model_dump()

    _assistant_response: orm.Mapped[JsonDict | None] = orm.mapped_column("assistant_response", sql.JSON)

    @property
    def assistant_response(self) -> extraction_responses.AssistantResponse | None:
        if self._assistant_response is None:
            return None
        else:
            return pydantic.RootModel[extraction_responses.AssistantResponse](self._assistant_response).root  # type: ignore[arg-type]

    @assistant_response.setter
    def assistant_response(self, value: extraction_responses.AssistantResponse | None) -> None:
        if value is None:
            self._assistant_response = sql.null()
        else:
            self._assistant_response = value.model_dump()

    exercise_creations__unordered: orm.Mapped[list[ExerciseCreationByPageExtraction]] = orm.relationship(
        back_populates="page_extraction"
    )

    @staticmethod
    def make_ordered_exercises_request__maybe_page_and_number(id: int) -> sql.Select[tuple[AdaptableExercise]]:
        return (
            sql.select(AdaptableExercise)
            .join(ExerciseCreationByPageExtraction)
            .join(ExerciseLocationMaybePageAndNumber)
            .where(ExerciseCreationByPageExtraction.page_extraction_id == id)
            .order_by(
                ExerciseLocationMaybePageAndNumber.page_number, ExerciseLocationMaybePageAndNumber.exercise_number
            )
        )

    @staticmethod
    def make_ordered_exercises_request__textbook(id: int) -> sql.Select[tuple[AdaptableExercise]]:
        return (
            sql.select(AdaptableExercise)
            .join(ExerciseCreationByPageExtraction)
            .join(ExerciseLocationTextbook)
            .where(ExerciseCreationByPageExtraction.page_extraction_id == id)
            .order_by(ExerciseLocationTextbook.page_number, ExerciseLocationTextbook.exercise_number)
        )

    def fetch_ordered_exercises(self) -> Iterable[AdaptableExercise]:
        if len(self.exercise_creations__unordered) == 0:
            return []
        else:
            first_location = self.exercise_creations__unordered[0].exercise.location
            # A page extraction creates all its exercises with the same type of ExerciseLocation
            if isinstance(first_location, ExerciseLocationMaybePageAndNumber):
                request = self.make_ordered_exercises_request__maybe_page_and_number(self.id)
            else:
                request = self.make_ordered_exercises_request__textbook(self.id)
            session = orm.object_session(self)
            assert session is not None
            return session.execute(request).scalars().all()


class ExerciseCreationByPageExtraction(ExerciseCreation):
    __tablename__ = "exercise_creations__by_page_extraction"
    __mapper_args__ = {"polymorphic_identity": "by_page_extraction"}

    def __init__(self, *, at: datetime.datetime, page_extraction: PageExtraction) -> None:
        super().__init__(at=at)
        self.page_extraction = page_extraction

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseCreation.id), primary_key=True)
    page_extraction_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(PageExtraction.id))
    page_extraction: orm.Mapped[PageExtraction] = orm.relationship(
        foreign_keys=[page_extraction_id],
        remote_side=[PageExtraction.id],
        back_populates="exercise_creations__unordered",
    )


annotate_new_tables("extraction")


class SandboxExtractionBatch(OrmBase, CreatedByUserMixin):
    __tablename__ = "sandbox_extraction_batches"

    def __init__(
        self,
        *,
        created_at: datetime.datetime,
        created_by_username: str,
        strategy: ExtractionStrategy,
        range: PdfFileRange,
        run_classification: bool,
        model_for_adaptation: adaptation_llm.ConcreteModel | None,
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by_username = created_by_username
        self.strategy = strategy
        self.range = range
        self.run_classification = run_classification
        self.model_for_adaptation = model_for_adaptation

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    strategy_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExtractionStrategy.id))
    strategy: orm.Mapped[ExtractionStrategy] = orm.relationship(
        foreign_keys=[strategy_id], remote_side=[ExtractionStrategy.id]
    )

    range_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(PdfFileRange.id))
    range: orm.Mapped[PdfFileRange] = orm.relationship(foreign_keys=[range_id], remote_side=[PdfFileRange.id])

    run_classification: orm.Mapped[bool]

    _model_for_adaptation: orm.Mapped[JsonDict | None] = orm.mapped_column("model_for_adaptation", sql.JSON)

    @property
    def model_for_adaptation(self) -> adaptation_llm.ConcreteModel | None:
        if self._model_for_adaptation is None:
            return None
        else:
            return pydantic.RootModel[adaptation_llm.ConcreteModel](self._model_for_adaptation).root  # type: ignore[arg-type]

    @model_for_adaptation.setter
    def model_for_adaptation(self, value: adaptation_llm.ConcreteModel | None) -> None:
        if value is None:
            self._model_for_adaptation = sql.null()
        else:
            self._model_for_adaptation = value.model_dump()

    page_extraction_creations: orm.Mapped[list[PageExtractionCreationBySandboxExtractionBatch]] = orm.relationship(
        back_populates="extraction_batch"
    )


class PageExtractionCreationBySandboxExtractionBatch(PageExtractionCreation):
    __tablename__ = "page_extraction_creations__by_sandbox_extraction_batch"
    __mapper_args__ = {"polymorphic_identity": "by_sandbox_extraction_batch"}

    def __init__(self, *, at: datetime.datetime, extraction_batch: SandboxExtractionBatch):
        super().__init__(at=at)
        self.extraction_batch = extraction_batch

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(PageExtractionCreation.id), primary_key=True)
    sandbox_extraction_batch_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(SandboxExtractionBatch.id))
    extraction_batch: orm.Mapped[SandboxExtractionBatch] = orm.relationship(
        foreign_keys=[sandbox_extraction_batch_id],
        remote_side=[SandboxExtractionBatch.id],
        back_populates="page_extraction_creations",
    )


annotate_new_tables("extraction", "sandbox")


# Classification
# ##############


class ClassificationBatch(OrmBase):
    __tablename__ = "classification_batches"

    def __init__(
        self,
        *,
        created_at: datetime.datetime,
        created_by_username: str | None,
        created_by_page_extraction: PageExtraction | None,
        model_for_adaptation: adaptation_llm.ConcreteModel | None,
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by_username = created_by_username
        self.created_by_page_extraction = created_by_page_extraction
        self.model_for_adaptation = model_for_adaptation

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str | None]  # Some 'ClassificationBatch's are created by a 'PageExtraction'
    created_by_page_extraction_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(PageExtraction.id))
    created_by_page_extraction: orm.Mapped[PageExtraction | None] = orm.relationship(
        foreign_keys=[created_by_page_extraction_id], remote_side=[PageExtraction.id]
    )

    exercises: orm.Mapped[list[AdaptableExercise]] = orm.relationship(
        back_populates="classified_by_classification_batch", order_by=lambda: [AdaptableExercise.id]
    )

    _model_for_adaptation: orm.Mapped[JsonDict | None] = orm.mapped_column("model_for_adaptation", sql.JSON)

    @property
    def model_for_adaptation(self) -> adaptation_llm.ConcreteModel | None:
        if self._model_for_adaptation is None:
            return None
        else:
            return pydantic.RootModel[adaptation_llm.ConcreteModel](self._model_for_adaptation).root  # type: ignore[arg-type]

    @model_for_adaptation.setter
    def model_for_adaptation(self, value: adaptation_llm.ConcreteModel | None) -> None:
        if value is None:
            self._model_for_adaptation = sql.null()
        else:
            self._model_for_adaptation = value.model_dump()

    adaptations: orm.Mapped[list[Adaptation]] = orm.relationship(
        back_populates="classification_batch", order_by="Adaptation.id"
    )


annotate_new_tables("classification")


# Textbooks
# #########


class Textbook(OrmBase):
    __tablename__ = "textbooks"

    def __init__(
        self,
        *,
        created_at: datetime.datetime,
        created_by_username: str,
        title: str,
        publisher: str | None,
        year: int | None,
        isbn: str | None,
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by_username = created_by_username
        self.title = title
        self.publisher = publisher
        self.year = year
        self.isbn = isbn

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]  # All 'Textbook's are created manually

    title: orm.Mapped[str]
    publisher: orm.Mapped[str | None]
    year: orm.Mapped[int | None]
    isbn: orm.Mapped[str | None]

    adaptation_batches: orm.Mapped[list[AdaptationBatch]] = orm.relationship(
        back_populates="textbook", order_by=lambda: [AdaptationBatch.id]
    )

    @staticmethod
    def make_ordered_exercises_request(id: int) -> sql.Select[tuple[BaseExercise]]:
        return (
            sql.select(BaseExercise)
            .join(ExerciseLocationTextbook)
            .where(ExerciseLocationTextbook.textbook_id == id)
            .order_by(ExerciseLocationTextbook.page_number, ExerciseLocationTextbook.exercise_number)
        )

    def fetch_ordered_exercises(self) -> Iterable[BaseExercise]:
        session = orm.object_session(self)
        assert session is not None
        return session.execute(self.make_ordered_exercises_request(self.id)).scalars().all()


class ExerciseLocationTextbook(ExerciseLocation):
    __tablename__ = "exercise_locations__textbook"
    __mapper_args__ = {"polymorphic_identity": "textbook"}

    def __init__(self, textbook: Textbook, page_number: int, exercise_number: str) -> None:
        super().__init__()
        self.textbook = textbook
        self.page_number = page_number
        self.exercise_number = exercise_number

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseLocation.id), primary_key=True)
    textbook_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Textbook.id))
    textbook: orm.Mapped[Textbook] = orm.relationship(foreign_keys=[textbook_id], remote_side=[Textbook.id])
    page_number: orm.Mapped[int]
    # Custom collation: migrations/versions/429d2fb463dd_exercise_number_collation.py
    exercise_number: orm.Mapped[str] = orm.mapped_column(sql.String(collation="exercise_number"))


class TextbookStartingPoint(OrmBase, CreatedByUserMixin):
    __tablename__ = "textbook_starting_points"

    def __init__(
        self,
        *,
        created_at: datetime.datetime,
        created_by_username: str,
        textbook_id: int | None,
        textbook_first_page_number: int | None,
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by_username = created_by_username
        self.textbook_id = textbook_id
        self.textbook_first_page_number = textbook_first_page_number

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    textbook_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(Textbook.id))
    textbook_first_page_number: orm.Mapped[int | None]


class PdfFileTextbookMapping(OrmBase, CreatedByUserMixin):
    __tablename__ = "pdf_file_textbook_mappings"

    def __init__(
        self,
        *,
        created_at: datetime.datetime,
        created_by_username: str,
        pdf_file_range_id: int,
        textbook_starting_point_id: int | None,
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by_username = created_by_username
        self.pdf_file_range_id = pdf_file_range_id
        self.textbook_starting_point_id = textbook_starting_point_id

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    pdf_file_range_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(PdfFileRange.id))
    textbook_starting_point_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(TextbookStartingPoint.id))


class PageExtractionCreationByPdfFileTextbookMapping(PageExtractionCreation):
    __tablename__ = "page_extraction_creations__by_pdf_file_textbook_mapping"
    __mapper_args__ = {"polymorphic_identity": "by_pdf_file_textbook_mapping"}

    def __init__(self, *, at: datetime.datetime, pdf_file_textbook_mapping: PdfFileTextbookMapping) -> None:
        super().__init__(at=at)
        self.pdf_file_textbook_mapping = pdf_file_textbook_mapping

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(PageExtractionCreation.id), primary_key=True)
    pdf_file_textbook_mapping_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(PdfFileTextbookMapping.id))


annotate_new_tables("textbooks")


# Adaptation
# ##########


class ExerciseClass(OrmBase):
    __tablename__ = "exercise_classes"

    def __init__(
        self,
        *,
        created_at: datetime.datetime,
        created_by_username: str | None,
        created_by_classification_batch: ClassificationBatch | None,
        name: str,
        latest_strategy_settings: AdaptationStrategySettings | None,
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by_username = created_by_username
        self.created_by_classification_batch = created_by_classification_batch
        self.name = name
        self.latest_strategy_settings = latest_strategy_settings

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str | None]  # Some 'ExerciseClass's are created by a 'ClassificationBatch'
    created_by_classification_batch_id: orm.Mapped[int | None] = orm.mapped_column(
        sql.ForeignKey(ClassificationBatch.id)
    )
    created_by_classification_batch: orm.Mapped[ClassificationBatch | None] = orm.relationship(
        foreign_keys=[created_by_classification_batch_id], remote_side=[ClassificationBatch.id]
    )

    name: orm.Mapped[str]

    latest_strategy_settings_id: orm.Mapped[int | None] = orm.mapped_column(
        sql.ForeignKey("adaptation_strategy_settings.id", use_alter=True)
    )
    latest_strategy_settings: orm.Mapped[AdaptationStrategySettings | None] = orm.relationship(
        foreign_keys=[latest_strategy_settings_id], remote_side=lambda: [AdaptationStrategySettings.id]
    )


class AdaptableExercise(BaseExercise):
    __tablename__ = "adaptable_exercises"
    __mapper_args__ = {"polymorphic_identity": "adaptable"}

    def __init__(
        self,
        created: ExerciseCreation,
        location: ExerciseLocation,
        removed_from_textbook: bool,
        full_text: str,
        instruction_hint_example_text: str | None,
        statement_text: str | None,
        classified_at: datetime.datetime | None,
        classified_by_classification_batch: ClassificationBatch | None,
        classified_by_username: str | None,
        exercise_class: ExerciseClass | None,
    ):
        super().__init__(created=created, location=location, removed_from_textbook=removed_from_textbook)
        self.full_text = full_text
        self.instruction_hint_example_text = instruction_hint_example_text
        self.statement_text = statement_text
        self.classified_at = classified_at
        self.classified_by_classification_batch = classified_by_classification_batch
        self.classified_by_username = classified_by_username
        self.exercise_class = exercise_class

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(BaseExercise.id), primary_key=True)

    created_by_page_extraction_id__to_be_deleted: orm.Mapped[int | None] = orm.mapped_column(
        "created_by_page_extraction_id"
    )

    full_text: orm.Mapped[str]
    instruction_hint_example_text: orm.Mapped[str | None]
    statement_text: orm.Mapped[str | None]

    classified_at: orm.Mapped[datetime.datetime | None] = orm.mapped_column(sql.DateTime(timezone=True))
    classified_by_classification_batch_id: orm.Mapped[int | None] = orm.mapped_column(
        sql.ForeignKey(ClassificationBatch.id)
    )
    classified_by_classification_batch: orm.Mapped[ClassificationBatch | None] = orm.relationship(
        foreign_keys=[classified_by_classification_batch_id],
        remote_side=[ClassificationBatch.id],
        back_populates="exercises",
    )
    classified_by_username: orm.Mapped[str | None]
    exercise_class_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(ExerciseClass.id))
    exercise_class: orm.Mapped[ExerciseClass | None] = orm.relationship(
        foreign_keys=[exercise_class_id], remote_side=[ExerciseClass.id]
    )

    adaptation: orm.Mapped[Adaptation | None] = orm.relationship(back_populates="exercise")


class AdaptationStrategySettings(OrmBase):
    __tablename__ = "adaptation_strategy_settings"

    def __init__(
        self,
        *,
        created_at: datetime.datetime,
        created_by_username: str,
        exercise_class: ExerciseClass | None,
        parent: AdaptationStrategySettings | None,
        system_prompt: str,
        response_specification: ConcreteLlmResponseSpecification,
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by_username = created_by_username
        self.exercise_class = exercise_class
        self.parent = parent
        self.system_prompt = system_prompt
        self.response_specification = response_specification

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]  # All 'AdaptationStrategySettings's are created manually

    exercise_class_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(ExerciseClass.id))
    exercise_class: orm.Mapped[ExerciseClass | None] = orm.relationship(
        foreign_keys=[exercise_class_id], remote_side=[ExerciseClass.id]
    )

    parent_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey("adaptation_strategy_settings.id"))
    parent: orm.Mapped[AdaptationStrategySettings | None] = orm.relationship(
        foreign_keys=[parent_id], remote_side=lambda: [AdaptationStrategySettings.id]
    )

    system_prompt: orm.Mapped[str]
    _response_specification: orm.Mapped[JsonDict] = orm.mapped_column("response_specification", sql.JSON)

    @property
    def response_specification(self) -> ConcreteLlmResponseSpecification:
        return pydantic.RootModel[ConcreteLlmResponseSpecification](self._response_specification).root  # type: ignore[arg-type]

    @response_specification.setter
    def response_specification(self, value: ConcreteLlmResponseSpecification) -> None:
        self._response_specification = value.model_dump()


class AdaptationStrategy(OrmBase):
    __tablename__ = "adaptation_strategies"

    def __init__(
        self,
        *,
        created_at: datetime.datetime,
        created_by_username: str | None,
        created_by_classification_batch: ClassificationBatch | None,
        settings: AdaptationStrategySettings,
        model: adaptation_llm.ConcreteModel,
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by_username = created_by_username
        self.created_by_classification_batch = created_by_classification_batch
        self.settings = settings
        self.model = model

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str | None]  # Some 'AdaptationStrategy's are created by a 'ClassificationBatch'
    created_by_classification_batch_id: orm.Mapped[int | None] = orm.mapped_column(
        sql.ForeignKey(ClassificationBatch.id)
    )
    created_by_classification_batch: orm.Mapped[ClassificationBatch | None] = orm.relationship(
        foreign_keys=[created_by_classification_batch_id], remote_side=[ClassificationBatch.id]
    )

    settings_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(AdaptationStrategySettings.id))
    settings: orm.Mapped[AdaptationStrategySettings] = orm.relationship(
        foreign_keys=[settings_id], remote_side=[AdaptationStrategySettings.id]
    )

    _model: orm.Mapped[JsonDict] = orm.mapped_column("model", sql.JSON)

    @property
    def model(self) -> adaptation_llm.ConcreteModel:
        return pydantic.RootModel[adaptation_llm.ConcreteModel](self._model).root  # type: ignore[arg-type]

    @model.setter
    def model(self, value: adaptation_llm.ConcreteModel) -> None:
        self._model = value.model_dump()


annotate_new_tables("adaptation")


class AdaptationBatch(OrmBase):
    __tablename__ = "adaptation_batches"

    def __init__(
        self,
        *,
        created_at: datetime.datetime,
        created_by_username: str,
        strategy: AdaptationStrategy,
        textbook: Textbook | None,
        removed_from_textbook: bool,
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by_username = created_by_username
        self.strategy = strategy
        self.textbook = textbook
        self.removed_from_textbook = removed_from_textbook

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]  # All 'AdaptationBatch's are created manually

    strategy_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(AdaptationStrategy.id))
    strategy: orm.Mapped[AdaptationStrategy] = orm.relationship(
        foreign_keys=[strategy_id], remote_side=[AdaptationStrategy.id]
    )

    textbook_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(Textbook.id))
    textbook: orm.Mapped[Textbook | None] = orm.relationship(
        foreign_keys=[textbook_id], remote_side=[Textbook.id], back_populates="adaptation_batches"
    )
    removed_from_textbook: orm.Mapped[bool]

    adaptations: orm.Mapped[list[Adaptation]] = orm.relationship(
        back_populates="adaptation_batch", order_by="Adaptation.id"
    )


annotate_new_tables("adaptation", "sandbox")


class Adaptation(OrmBase):
    __tablename__ = "adaptations"

    def __init__(
        self,
        *,
        created_at: datetime.datetime,
        created_by_username: str | None,
        exercise: AdaptableExercise,
        strategy: AdaptationStrategy,
        classification_batch: ClassificationBatch | None,
        adaptation_batch: AdaptationBatch | None,
        raw_llm_conversations: JsonList,
        initial_assistant_response: adaptation_responses.AssistantResponse | None,
        adjustments: list[adaptation_responses.Adjustment],
        manual_edit: AdaptedExercise | None,
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by_username = created_by_username
        self.exercise = exercise
        self.strategy = strategy
        self.classification_batch = classification_batch
        self.adaptation_batch = adaptation_batch
        self.raw_llm_conversations = raw_llm_conversations
        self.initial_assistant_response = initial_assistant_response
        self.adjustments = adjustments
        self.manual_edit = manual_edit

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str | None]  # Some 'Adaptation's are created by a 'ClassificationBatch'

    exercise_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(AdaptableExercise.id))
    exercise: orm.Mapped[AdaptableExercise] = orm.relationship(
        foreign_keys=[exercise_id], remote_side=[AdaptableExercise.id], back_populates="adaptation"
    )

    strategy_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(AdaptationStrategy.id))
    strategy: orm.Mapped[AdaptationStrategy] = orm.relationship(
        foreign_keys=[strategy_id], remote_side=[AdaptationStrategy.id]
    )

    classification_batch_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(ClassificationBatch.id))
    classification_batch: orm.Mapped[ClassificationBatch | None] = orm.relationship(
        foreign_keys=[classification_batch_id], remote_side=[ClassificationBatch.id], back_populates="adaptations"
    )

    adaptation_batch_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(AdaptationBatch.id))
    adaptation_batch: orm.Mapped[AdaptationBatch | None] = orm.relationship(
        foreign_keys=[adaptation_batch_id], remote_side=[AdaptationBatch.id], back_populates="adaptations"
    )

    # Help investigation of future issues
    raw_llm_conversations: orm.Mapped[JsonList] = orm.mapped_column(sql.JSON)

    _initial_assistant_response: orm.Mapped[JsonDict | None] = orm.mapped_column("initial_assistant_response", sql.JSON)

    @property
    def initial_assistant_response(self) -> adaptation_responses.AssistantResponse | None:
        if self._initial_assistant_response is None:
            return None
        else:
            return pydantic.RootModel[adaptation_responses.AssistantResponse](self._initial_assistant_response).root  # type: ignore[arg-type]

    @initial_assistant_response.setter
    def initial_assistant_response(self, value: adaptation_responses.AssistantResponse | None) -> None:
        if value is None:
            self._initial_assistant_response = sql.null()
        else:
            self._initial_assistant_response = value.model_dump()

    _adjustments: orm.Mapped[JsonList] = orm.mapped_column("adjustments", sql.JSON)

    @property
    def adjustments(self) -> list[adaptation_responses.Adjustment]:
        return [adaptation_responses.Adjustment(**adjustment) for adjustment in self._adjustments]

    @adjustments.setter
    def adjustments(self, value: list[adaptation_responses.Adjustment]) -> None:
        self._adjustments = [adjustment.model_dump() for adjustment in value]

    _manual_edit: orm.Mapped[JsonDict | None] = orm.mapped_column("manual_edit", sql.JSON)

    @property
    def manual_edit(self) -> AdaptedExercise | None:
        if self._manual_edit is None:
            return None
        else:
            return AdaptedExercise(**self._manual_edit)

    @manual_edit.setter
    def manual_edit(self, value: AdaptedExercise | None) -> None:
        if value is None:
            self._manual_edit = sql.null()
        else:
            self._manual_edit = value.model_dump()


annotate_new_tables("adaptation")


# Fundamentals
# ############


class ErrorCaughtByFrontend(OrmBase):
    __tablename__ = "errors_caught_by_frontend"

    def __init__(
        self,
        *,
        created_at: datetime.datetime,
        created_by_username: str | None,
        patty_version: str,
        user_agent: str,
        window_size: str,
        url: str,
        caught_by: str,
        message: str,
        code_location: str | None,
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by_username = created_by_username
        self.patty_version = patty_version
        self.user_agent = user_agent
        self.window_size = window_size
        self.url = url
        self.caught_by = caught_by
        self.message = message
        self.code_location = code_location

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str | None]

    patty_version: orm.Mapped[str]
    user_agent: orm.Mapped[str]
    window_size: orm.Mapped[str]
    url: orm.Mapped[str]

    caught_by: orm.Mapped[str]
    message: orm.Mapped[str]
    code_location: orm.Mapped[str | None]


annotate_new_tables("fundamentals")
