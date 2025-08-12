from __future__ import annotations

import datetime
import typing

import pydantic
from sqlalchemy import orm
import sqlalchemy as sql

from . import llm
from ..adaptation import llm as adaptation_llm
from ..adaptation.orm_models import AdaptableExercise
from ..any_json import JsonDict
from ..classification.orm_models import ExerciseClassificationChunkCreation, ModelForAdaptationMixin
from ..database_utils import OrmBase, CreatedByUserMixin, annotate_new_tables
from ..exercises.orm_models import ExerciseCreation, ExerciseLocationMaybePageAndNumber
from .assistant_responses import AssistantResponse


class PdfFile(OrmBase, CreatedByUserMixin):
    __tablename__ = "pdf_files"

    def __init__(
        self,
        *,
        created_at: datetime.datetime,
        created_by: str,
        sha256: str,
        bytes_count: int,
        pages_count: int,
        known_file_names: list[str],
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by = created_by
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
        created_by: str,
        first_page_number: int,
        pages_count: int,
        pdf_file: PdfFile,
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by = created_by
        self.first_page_number = first_page_number
        self.pages_count = pages_count
        self.pdf_file = pdf_file

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    first_page_number: orm.Mapped[int]
    pages_count: orm.Mapped[int]

    pdf_file_sha256: orm.Mapped[str] = orm.mapped_column(sql.ForeignKey(PdfFile.sha256))
    pdf_file: orm.Mapped[PdfFile] = orm.relationship(foreign_keys=[pdf_file_sha256], remote_side=[PdfFile.sha256])


class ExtractionSettings(OrmBase, CreatedByUserMixin):
    __tablename__ = "extraction_settings"

    def __init__(self, *, created_by: str, created_at: datetime.datetime, prompt: str) -> None:
        super().__init__()
        self.created_by = created_by
        self.created_at = created_at
        self.prompt = prompt

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    prompt: orm.Mapped[str]


class PageExtraction(OrmBase, ModelForAdaptationMixin):
    __tablename__ = "page_extractions"

    def __init__(
        self,
        *,
        created: PageExtractionCreation,
        pdf_range: PdfFileRange,
        pdf_page_number: int,
        settings: ExtractionSettings,
        model: llm.ConcreteModel,
        run_classification: bool,
        model_for_adaptation: adaptation_llm.ConcreteModel | None,
        assistant_response: AssistantResponse | None,
    ) -> None:
        super().__init__()
        self.created = created
        self.pdf_range = pdf_range
        self.pdf_page_number = pdf_page_number
        self.settings = settings
        self.model = model
        self.run_classification = run_classification
        self.model_for_adaptation = model_for_adaptation
        self.assistant_response = assistant_response

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created: orm.Mapped[PageExtractionCreation] = orm.relationship(back_populates="page_extraction")

    pdf_range_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(PdfFileRange.id))
    pdf_range: orm.Mapped[PdfFileRange] = orm.relationship(foreign_keys=[pdf_range_id], remote_side=[PdfFileRange.id])
    pdf_page_number: orm.Mapped[int]

    settings_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExtractionSettings.id))
    settings: orm.Mapped[ExtractionSettings] = orm.relationship(
        foreign_keys=[settings_id], remote_side=[ExtractionSettings.id]
    )

    _model: orm.Mapped[JsonDict] = orm.mapped_column("model", sql.JSON)

    @property
    def model(self) -> llm.ConcreteModel:
        return pydantic.RootModel[llm.ConcreteModel].model_validate(self._model).root

    @model.setter
    def model(self, value: llm.ConcreteModel) -> None:
        self._model = value.model_dump()

    run_classification: orm.Mapped[bool]

    _assistant_response: orm.Mapped[JsonDict | None] = orm.mapped_column("assistant_response", sql.JSON)

    @property
    def assistant_response(self) -> AssistantResponse | None:
        if self._assistant_response is None:
            return None
        else:
            return pydantic.RootModel[AssistantResponse].model_validate(self._assistant_response).root

    @assistant_response.setter
    def assistant_response(self, value: AssistantResponse | None) -> None:
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
        from ..textbooks.orm_models import ExerciseLocationTextbook

        return (
            sql.select(AdaptableExercise)
            .join(ExerciseCreationByPageExtraction)
            .join(ExerciseLocationTextbook)
            .where(ExerciseCreationByPageExtraction.page_extraction_id == id)
            .order_by(ExerciseLocationTextbook.page_number, ExerciseLocationTextbook.exercise_number)
        )

    def fetch_ordered_exercises(self) -> typing.Iterable[AdaptableExercise]:
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


class PageExtractionCreation(OrmBase):
    __tablename__ = "page_extraction_creations"
    __mapper_args__ = {"polymorphic_on": "kind"}

    def __init__(self, *, at: datetime.datetime) -> None:
        super().__init__()
        self.at = at

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(PageExtraction.id), primary_key=True)
    kind: orm.Mapped[str]

    at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))

    page_extraction: orm.Mapped[PageExtraction] = orm.relationship(
        foreign_keys=[id], remote_side=[PageExtraction.id], back_populates="created"
    )


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


class ExerciseClassificationChunkCreationByPageExtraction(ExerciseClassificationChunkCreation):
    __tablename__ = "exercise_classification_chunk_creations__by_page_extraction"
    __mapper_args__ = {"polymorphic_identity": "by_page_extraction"}

    def __init__(self, *, at: datetime.datetime, page_extraction: PageExtraction) -> None:
        super().__init__(at=at)
        self.page_extraction = page_extraction

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseClassificationChunkCreation.id), primary_key=True)

    page_extraction_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(PageExtraction.id))
    page_extraction: orm.Mapped[PageExtraction] = orm.relationship(
        foreign_keys=[page_extraction_id], remote_side=[PageExtraction.id]
    )


annotate_new_tables("extraction")


class SandboxExtractionBatch(OrmBase, CreatedByUserMixin, ModelForAdaptationMixin):
    __tablename__ = "sandbox_extraction_batches"

    def __init__(
        self,
        *,
        created_by: str,
        created_at: datetime.datetime,
        pdf_range: PdfFileRange,
        settings: ExtractionSettings,
        model: llm.ConcreteModel,
        run_classification: bool,
        model_for_adaptation: adaptation_llm.ConcreteModel | None,
    ) -> None:
        super().__init__()
        self.created_by = created_by
        self.created_at = created_at
        self.pdf_range = pdf_range
        self.settings = settings
        self.model = model
        self.run_classification = run_classification
        self.model_for_adaptation = model_for_adaptation

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    pdf_range_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(PdfFileRange.id))
    pdf_range: orm.Mapped[PdfFileRange] = orm.relationship(foreign_keys=[pdf_range_id], remote_side=[PdfFileRange.id])

    settings_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExtractionSettings.id))
    settings: orm.Mapped[ExtractionSettings] = orm.relationship(
        foreign_keys=[settings_id], remote_side=[ExtractionSettings.id]
    )

    _model: orm.Mapped[JsonDict] = orm.mapped_column("model", sql.JSON)

    @property
    def model(self) -> llm.ConcreteModel:
        return pydantic.RootModel[llm.ConcreteModel].model_validate(self._model).root

    @model.setter
    def model(self, value: llm.ConcreteModel) -> None:
        self._model = value.model_dump()

    run_classification: orm.Mapped[bool]

    page_extraction_creations: orm.Mapped[list[PageExtractionCreationBySandboxExtractionBatch]] = orm.relationship(
        back_populates="sandbox_extraction_batch"
    )


class PageExtractionCreationBySandboxExtractionBatch(PageExtractionCreation):
    __tablename__ = "page_extraction_creations__by_sandbox_batch"
    __mapper_args__ = {"polymorphic_identity": "by_sandbox_batch"}

    def __init__(self, *, at: datetime.datetime, sandbox_extraction_batch: SandboxExtractionBatch) -> None:
        super().__init__(at=at)
        self.sandbox_extraction_batch = sandbox_extraction_batch

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(PageExtractionCreation.id), primary_key=True)

    sandbox_extraction_batch_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(SandboxExtractionBatch.id))
    sandbox_extraction_batch: orm.Mapped[SandboxExtractionBatch] = orm.relationship(
        foreign_keys=[sandbox_extraction_batch_id],
        remote_side=[SandboxExtractionBatch.id],
        back_populates="page_extraction_creations",
    )


annotate_new_tables("extraction", "sandbox")
