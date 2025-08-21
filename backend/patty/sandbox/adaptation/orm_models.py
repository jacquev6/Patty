from __future__ import annotations

import datetime

from sqlalchemy import orm
import sqlalchemy as sql

from ... import adaptation
from ...any_json import JsonDict
from ...database_utils import CreatedByUserMixin, OrmBase, annotate_new_tables


class SandboxAdaptationBatch(OrmBase, CreatedByUserMixin):
    __tablename__ = "sandbox_adaptation_batches"

    def __init__(
        self,
        *,
        created_by: str,
        created_at: datetime.datetime,
        settings: adaptation.AdaptationSettings,
        model: adaptation.llm.ConcreteModel,
    ) -> None:
        super().__init__()
        self.created_by = created_by
        self.created_at = created_at
        self.settings = settings
        self.model = model

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    settings_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(adaptation.AdaptationSettings.id))
    settings: orm.Mapped[adaptation.AdaptationSettings] = orm.relationship(
        foreign_keys=[settings_id], remote_side=[adaptation.AdaptationSettings.id]
    )

    _model: orm.Mapped[JsonDict] = orm.mapped_column("model", sql.JSON)

    @property
    def model(self) -> adaptation.llm.ConcreteModel:
        return adaptation.llm.validate(self._model)

    @model.setter
    def model(self, value: adaptation.llm.ConcreteModel) -> None:
        self._model = value.model_dump()

    adaptation_creations: orm.Mapped[list[AdaptationCreationBySandboxBatch]] = orm.relationship(
        back_populates="sandbox_adaptation_batch"
    )


class AdaptationCreationBySandboxBatch(adaptation.AdaptationCreation):
    __tablename__ = "adaptation_creations__by_sandbox_batch"
    __mapper_args__ = {"polymorphic_identity": "by_sandbox_batch"}

    def __init__(self, *, at: datetime.datetime, sandbox_adaptation_batch: SandboxAdaptationBatch) -> None:
        super().__init__(at=at)
        self.sandbox_adaptation_batch = sandbox_adaptation_batch

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(adaptation.AdaptationCreation.id), primary_key=True)

    sandbox_adaptation_batch_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(SandboxAdaptationBatch.id))
    sandbox_adaptation_batch: orm.Mapped[SandboxAdaptationBatch] = orm.relationship(
        foreign_keys=[sandbox_adaptation_batch_id],
        remote_side=[SandboxAdaptationBatch.id],
        back_populates="adaptation_creations",
    )


annotate_new_tables("adaptation", "sandbox")
