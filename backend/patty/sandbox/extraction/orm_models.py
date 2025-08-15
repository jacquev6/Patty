from __future__ import annotations

import datetime

from sqlalchemy import orm
import sqlalchemy as sql

from ... import adaptation
from ... import extraction
from ...any_json import JsonDict
from ...classification import ModelForAdaptationMixin
from ...database_utils import OrmBase, CreatedByUserMixin, annotate_new_tables


class SandboxExtractionBatch(OrmBase, CreatedByUserMixin, ModelForAdaptationMixin):
    __tablename__ = "sandbox_extraction_batches"

    def __init__(
        self,
        *,
        created_by: str,
        created_at: datetime.datetime,
        pdf_range: extraction.PdfFileRange,
        settings: extraction.ExtractionSettings,
        model: extraction.llm.ConcreteModel,
        run_classification: bool,
        model_for_adaptation: adaptation.llm.ConcreteModel | None,
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

    pdf_range_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(extraction.PdfFileRange.id))
    pdf_range: orm.Mapped[extraction.PdfFileRange] = orm.relationship(
        foreign_keys=[pdf_range_id], remote_side=[extraction.PdfFileRange.id]
    )

    settings_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(extraction.ExtractionSettings.id))
    settings: orm.Mapped[extraction.ExtractionSettings] = orm.relationship(
        foreign_keys=[settings_id], remote_side=[extraction.ExtractionSettings.id]
    )

    _model: orm.Mapped[JsonDict] = orm.mapped_column("model", sql.JSON)

    @property
    def model(self) -> extraction.llm.ConcreteModel:
        return extraction.llm.validate(self._model)

    @model.setter
    def model(self, value: extraction.llm.ConcreteModel) -> None:
        self._model = value.model_dump()

    run_classification: orm.Mapped[bool]

    page_extraction_creations: orm.Mapped[list[PageExtractionCreationBySandboxExtractionBatch]] = orm.relationship(
        back_populates="sandbox_extraction_batch"
    )


class PageExtractionCreationBySandboxExtractionBatch(extraction.PageExtractionCreation):
    __tablename__ = "page_extraction_creations__by_sandbox_batch"
    __mapper_args__ = {"polymorphic_identity": "by_sandbox_batch"}

    def __init__(self, *, at: datetime.datetime, sandbox_extraction_batch: SandboxExtractionBatch) -> None:
        super().__init__(at=at)
        self.sandbox_extraction_batch = sandbox_extraction_batch

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(extraction.PageExtractionCreation.id), primary_key=True)

    sandbox_extraction_batch_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(SandboxExtractionBatch.id))
    sandbox_extraction_batch: orm.Mapped[SandboxExtractionBatch] = orm.relationship(
        foreign_keys=[sandbox_extraction_batch_id],
        remote_side=[SandboxExtractionBatch.id],
        back_populates="page_extraction_creations",
    )


annotate_new_tables("extraction", "sandbox")
