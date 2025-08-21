from __future__ import annotations

import datetime

from sqlalchemy import orm
import sqlalchemy as sql

from ... import adaptation
from ... import classification
from ...database_utils import OrmBase, CreatedByUserMixin, annotate_new_tables


class SandboxClassificationBatch(OrmBase, CreatedByUserMixin, classification.ModelForAdaptationMixin):
    __tablename__ = "sandbox_classification_batches"

    def __init__(
        self,
        *,
        created_by: str,
        created_at: datetime.datetime,
        model_for_adaptation: adaptation.llm.ConcreteModel | None,
    ) -> None:
        super().__init__()
        self.created_by = created_by
        self.created_at = created_at
        self.model_for_adaptation = model_for_adaptation

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    classification_chunk_creation: orm.Mapped[ClassificationChunkCreationBySandboxBatch] = orm.relationship(
        back_populates="sandbox_classification_batch"
    )


class ClassificationChunkCreationBySandboxBatch(classification.ClassificationChunkCreation):
    __tablename__ = "classification_chunk_creations__by_sandbox_batch"
    __mapper_args__ = {"polymorphic_identity": "by_sandbox_batch"}

    def __init__(self, *, at: datetime.datetime, sandbox_classification_batch: SandboxClassificationBatch) -> None:
        super().__init__(at=at)
        self.sandbox_classification_batch = sandbox_classification_batch

    id: orm.Mapped[int] = orm.mapped_column(
        sql.ForeignKey(classification.ClassificationChunkCreation.id), primary_key=True
    )

    sandbox_classification_batch_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(SandboxClassificationBatch.id))
    sandbox_classification_batch: orm.Mapped[SandboxClassificationBatch] = orm.relationship(
        foreign_keys=[sandbox_classification_batch_id],
        remote_side=[SandboxClassificationBatch.id],
        back_populates="classification_chunk_creation",
    )


annotate_new_tables("classification", "sandbox")
