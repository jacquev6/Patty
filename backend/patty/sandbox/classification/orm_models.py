# MALIN Platform https://malin.cahiersfantastiques.fr/
# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
