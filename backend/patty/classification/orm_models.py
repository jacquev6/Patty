from __future__ import annotations

import datetime

from sqlalchemy import orm
import sqlalchemy as sql

from ..database_utils import OrmBase, CreatedByUserMixin, annotate_new_tables
from ..adaptation.orm_models import ExerciseClass, AdaptableExercise, ExerciseAdaptationCreation
from ..adaptation import llm as adaptation_llm
from ..any_json import JsonDict


class ModelForAdaptationMixin:
    _model_for_adaptation: orm.Mapped[JsonDict | None] = orm.mapped_column("model_for_adaptation", sql.JSON)

    @property
    def model_for_adaptation(self) -> adaptation_llm.ConcreteModel | None:
        if self._model_for_adaptation is None:
            return None
        else:
            return adaptation_llm.validate(self._model_for_adaptation)

    @model_for_adaptation.setter
    def model_for_adaptation(self, value: adaptation_llm.ConcreteModel | None) -> None:
        if value is None:
            self._model_for_adaptation = sql.null()
        else:
            self._model_for_adaptation = value.model_dump()


class ExerciseClassCreation(OrmBase):
    __tablename__ = "exercise_class_creations"
    __mapper_args__ = {"polymorphic_on": "kind"}

    def __init__(self, *, at: datetime.datetime) -> None:
        super().__init__()
        self.at = at

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseClass.id), primary_key=True)
    kind: orm.Mapped[str] = orm.mapped_column()
    at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))

    exercise_class: orm.Mapped[ExerciseClass] = orm.relationship(
        foreign_keys=[id], remote_side=[ExerciseClass.id], back_populates="created"
    )


class ExerciseClassCreationByUser(ExerciseClassCreation):
    __tablename__ = "exercise_class_creations__by_user"
    __mapper_args__ = {"polymorphic_identity": "by_user"}

    def __init__(self, *, at: datetime.datetime, username: str) -> None:
        super().__init__(at=at)
        self.username = username

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseClassCreation.id), primary_key=True)
    username: orm.Mapped[str] = orm.mapped_column()


class ExerciseClassification(OrmBase):
    __tablename__ = "exercise_classifications"
    __mapper_args__ = {"polymorphic_on": "kind"}

    def __init__(
        self, *, exercise: AdaptableExercise, at: datetime.datetime, exercise_class: ExerciseClass | None
    ) -> None:
        super().__init__()
        self.exercise = exercise
        self.at = at
        self.exercise_class = exercise_class

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    kind: orm.Mapped[str]

    exercise_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(AdaptableExercise.id))
    exercise: orm.Mapped[AdaptableExercise] = orm.relationship(
        foreign_keys=[exercise_id], remote_side=[AdaptableExercise.id], back_populates="classifications"
    )

    at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))

    exercise_class_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(ExerciseClass.id))
    exercise_class: orm.Mapped[ExerciseClass | None] = orm.relationship(
        foreign_keys=[exercise_class_id], remote_side=[ExerciseClass.id]
    )


class ExerciseClassificationByUser(ExerciseClassification):
    __tablename__ = "exercise_classifications__by_user"
    __mapper_args__ = {"polymorphic_identity": "by_user"}

    def __init__(
        self, *, exercise: AdaptableExercise, at: datetime.datetime, username: str, exercise_class: ExerciseClass | None
    ) -> None:
        super().__init__(exercise=exercise, at=at, exercise_class=exercise_class)
        self.username = username

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseClassification.id), primary_key=True)
    username: orm.Mapped[str]


class ExerciseClassificationChunk(OrmBase, ModelForAdaptationMixin):
    __tablename__ = "exercise_classification_chunks"

    def __init__(
        self, *, created: ExerciseClassificationChunkCreation, model_for_adaptation: adaptation_llm.ConcreteModel | None
    ) -> None:
        super().__init__()
        self.created = created
        self.model_for_adaptation = model_for_adaptation

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created: orm.Mapped[ExerciseClassificationChunkCreation] = orm.relationship(back_populates="classification_chunk")

    classifications: orm.Mapped[list[ExerciseClassificationByClassificationChunk]] = orm.relationship(
        back_populates="classification_chunk"
    )


class ExerciseClassificationChunkCreation(OrmBase):
    __tablename__ = "exercise_classification_chunk_creations"
    __mapper_args__ = {"polymorphic_on": "kind"}

    def __init__(self, *, at: datetime.datetime) -> None:
        super().__init__()
        self.at = at

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseClassificationChunk.id), primary_key=True)
    kind: orm.Mapped[str]

    at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))

    classification_chunk: orm.Mapped[ExerciseClassificationChunk] = orm.relationship(
        foreign_keys=[id], remote_side=[ExerciseClassificationChunk.id], back_populates="created"
    )


class ExerciseClassificationByClassificationChunk(ExerciseClassification):
    __tablename__ = "exercise_classifications__by_classification_chunk"
    __mapper_args__ = {"polymorphic_identity": "by_classification_chunk"}

    def __init__(
        self,
        *,
        exercise: AdaptableExercise,
        at: datetime.datetime,
        classification_chunk: ExerciseClassificationChunk,
        exercise_class: ExerciseClass | None,
    ) -> None:
        super().__init__(exercise=exercise, at=at, exercise_class=exercise_class)
        self.classification_chunk = classification_chunk

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseClassification.id), primary_key=True)

    classification_chunk_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseClassificationChunk.id))
    classification_chunk: orm.Mapped[ExerciseClassificationChunk] = orm.relationship(
        foreign_keys=[classification_chunk_id],
        remote_side=[ExerciseClassificationChunk.id],
        back_populates="classifications",
    )


class ExerciseClassCreationByClassificationChunk(ExerciseClassCreation):
    __tablename__ = "exercise_class_creations__by_classification_chunk"
    __mapper_args__ = {"polymorphic_identity": "by_classification_chunk"}

    def __init__(self, *, at: datetime.datetime, classification_chunk: ExerciseClassificationChunk) -> None:
        super().__init__(at=at)
        self.classification_chunk = classification_chunk

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseClassCreation.id), primary_key=True)
    classification_chunk_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseClassificationChunk.id))
    classification_chunk: orm.Mapped[ExerciseClassificationChunk] = orm.relationship(
        foreign_keys=[classification_chunk_id], remote_side=[ExerciseClassificationChunk.id]
    )


class ExerciseAdaptationCreationByClassificationChunk(ExerciseAdaptationCreation):
    __tablename__ = "exercise_adaptation_creations__by_classification_chunk"
    __mapper_args__ = {"polymorphic_identity": "by_classification_chunk"}

    def __init__(self, *, at: datetime.datetime, classification_chunk: ExerciseClassificationChunk) -> None:
        super().__init__(at=at)
        self.classification_chunk = classification_chunk

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseAdaptationCreation.id), primary_key=True)

    classification_chunk_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseClassificationChunk.id))
    classification_chunk: orm.Mapped[ExerciseClassificationChunk] = orm.relationship(
        foreign_keys=[classification_chunk_id], remote_side=[ExerciseClassificationChunk.id]
    )


annotate_new_tables("classification")


class SandboxClassificationBatch(OrmBase, CreatedByUserMixin, ModelForAdaptationMixin):
    __tablename__ = "sandbox_classification_batches"

    def __init__(
        self,
        *,
        created_by: str,
        created_at: datetime.datetime,
        model_for_adaptation: adaptation_llm.ConcreteModel | None,
    ) -> None:
        super().__init__()
        self.created_by = created_by
        self.created_at = created_at
        self.model_for_adaptation = model_for_adaptation

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    classification_chunk_creation: orm.Mapped[ExerciseClassificationChunkCreationBySandboxClassificationBatch] = (
        orm.relationship(back_populates="sandbox_classification_batch")
    )


class ExerciseClassificationChunkCreationBySandboxClassificationBatch(ExerciseClassificationChunkCreation):
    __tablename__ = "exercise_classification_chunk_creations__by_sandbox_batch"
    __mapper_args__ = {"polymorphic_identity": "by_sandbox_batch"}

    def __init__(self, *, at: datetime.datetime, sandbox_classification_batch: SandboxClassificationBatch) -> None:
        super().__init__(at=at)
        self.sandbox_classification_batch = sandbox_classification_batch

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseClassificationChunkCreation.id), primary_key=True)

    sandbox_classification_batch_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(SandboxClassificationBatch.id))
    sandbox_classification_batch: orm.Mapped[SandboxClassificationBatch] = orm.relationship(
        foreign_keys=[sandbox_classification_batch_id],
        remote_side=[SandboxClassificationBatch.id],
        back_populates="classification_chunk_creation",
    )


annotate_new_tables("classification", "sandbox")
