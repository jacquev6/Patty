from __future__ import annotations

import datetime

from sqlalchemy import orm
import sqlalchemy as sql

from . import assistant_responses
from . import llm
from .. import adaptation
from ..any_json import JsonDict
from ..classification import ClassificationChunkCreation, ModelForAdaptationMixin
from ..database_utils import OrmBase, CreatedByUserMixin, annotate_new_tables
from ..exercises import ExerciseCreation, ExerciseImageCreation
from ..logs import TimingData


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
        pdf_file_range: PdfFileRange,
        pdf_page_number: int,
        settings: ExtractionSettings,
        model: llm.ConcreteModel,
        run_classification: bool,
        model_for_adaptation: adaptation.llm.ConcreteModel | None,
        assistant_response: assistant_responses.Response | None,
        timing: TimingData | None,
    ) -> None:
        super().__init__()
        self.created = created
        self.pdf_file_range = pdf_file_range
        self.pdf_page_number = pdf_page_number
        self.settings = settings
        self.model = model
        self.run_classification = run_classification
        self.model_for_adaptation = model_for_adaptation
        self.assistant_response = assistant_response
        self.timing = timing

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created: orm.Mapped[PageExtractionCreation] = orm.relationship(back_populates="page_extraction")

    pdf_file_range_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(PdfFileRange.id))
    pdf_file_range: orm.Mapped[PdfFileRange] = orm.relationship(
        foreign_keys=[pdf_file_range_id], remote_side=[PdfFileRange.id]
    )
    pdf_page_number: orm.Mapped[int]

    settings_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExtractionSettings.id))
    settings: orm.Mapped[ExtractionSettings] = orm.relationship(
        foreign_keys=[settings_id], remote_side=[ExtractionSettings.id]
    )

    _model: orm.Mapped[JsonDict] = orm.mapped_column("model", sql.JSON)

    @property
    def model(self) -> llm.ConcreteModel:
        return llm.validate(self._model)

    @model.setter
    def model(self, value: llm.ConcreteModel) -> None:
        self._model = value.model_dump()

    run_classification: orm.Mapped[bool]

    _assistant_response: orm.Mapped[JsonDict | None] = orm.mapped_column("assistant_response", sql.JSON)

    @property
    def assistant_response(self) -> assistant_responses.Response | None:
        if self._assistant_response is None:
            return None
        else:
            return assistant_responses.validate(self._assistant_response)

    @assistant_response.setter
    def assistant_response(self, value: assistant_responses.Response | None) -> None:
        if value is None:
            self._assistant_response = sql.null()
        else:
            self._assistant_response = value.model_dump()

    _timing: orm.Mapped[JsonDict | None] = orm.mapped_column("timing", sql.JSON, nullable=True)

    @property
    def timing(self) -> TimingData | None:
        if self._timing is None:
            return None
        else:
            return TimingData.model_validate(self._timing)

    @timing.setter
    def timing(self, value: TimingData | None) -> None:
        if value is None:
            self._timing = sql.null()
        else:
            self._timing = value.model_dump()

    exercise_creations__ordered_by_id: orm.Mapped[list[ExerciseCreationByPageExtraction]] = orm.relationship(
        back_populates="page_extraction", order_by="ExerciseCreationByPageExtraction.id"
    )

    classification_chunk_creations: orm.Mapped[list[ClassificationChunkCreationByPageExtraction]] = orm.relationship(
        back_populates="page_extraction"
    )

    extracted_images: orm.Mapped[list[ExerciseImageCreationByPageExtraction]] = orm.relationship(
        back_populates="page_extraction"
    )


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
        back_populates="exercise_creations__ordered_by_id",
    )


class ClassificationChunkCreationByPageExtraction(ClassificationChunkCreation):
    __tablename__ = "classification_chunk_creations__by_page_extraction"
    __mapper_args__ = {"polymorphic_identity": "by_page_extraction"}

    def __init__(self, *, at: datetime.datetime, page_extraction: PageExtraction) -> None:
        super().__init__(at=at)
        self.page_extraction = page_extraction

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ClassificationChunkCreation.id), primary_key=True)

    page_extraction_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(PageExtraction.id))
    page_extraction: orm.Mapped[PageExtraction] = orm.relationship(
        foreign_keys=[page_extraction_id],
        remote_side=[PageExtraction.id],
        back_populates="classification_chunk_creations",
    )


class ExerciseImageCreationByPageExtraction(ExerciseImageCreation):
    __tablename__ = "exercise_image_creations__by_page_extraction"
    __mapper_args__ = {"polymorphic_identity": "by_page_extraction"}

    def __init__(self, *, at: datetime.datetime, page_extraction: PageExtraction) -> None:
        super().__init__(at=at)
        self.page_extraction = page_extraction

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseImageCreation.id), primary_key=True)

    page_extraction_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(PageExtraction.id))
    page_extraction: orm.Mapped[PageExtraction] = orm.relationship(
        foreign_keys=[page_extraction_id], remote_side=[PageExtraction.id], back_populates="extracted_images"
    )


annotate_new_tables("extraction")
