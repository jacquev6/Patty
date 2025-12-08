# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import annotations

import datetime

from sqlalchemy import orm
import sqlalchemy as sql

from .. import adaptation
from ..adaptation import ExerciseClass, AdaptableExercise, AdaptationCreation
from ..any_json import JsonDict
from ..database_utils import OrmBase, annotate_new_tables
from ..logs import TimingData


class ModelForAdaptationMixin:
    _model_for_adaptation: orm.Mapped[JsonDict | None] = orm.mapped_column("model_for_adaptation", sql.JSON)

    @property
    def model_for_adaptation(self) -> adaptation.llm.ConcreteModel | None:
        if self._model_for_adaptation is None:
            return None
        else:
            return adaptation.llm.validate(self._model_for_adaptation)

    @model_for_adaptation.setter
    def model_for_adaptation(self, value: adaptation.llm.ConcreteModel | None) -> None:
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


class Classification(OrmBase):
    __tablename__ = "classifications"
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


class ClassificationByUser(Classification):
    __tablename__ = "classifications__by_user"
    __mapper_args__ = {"polymorphic_identity": "by_user"}

    def __init__(
        self, *, exercise: AdaptableExercise, at: datetime.datetime, username: str, exercise_class: ExerciseClass | None
    ) -> None:
        super().__init__(exercise=exercise, at=at, exercise_class=exercise_class)
        self.username = username

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Classification.id), primary_key=True)
    username: orm.Mapped[str]


class ClassificationChunk(OrmBase, ModelForAdaptationMixin):
    __tablename__ = "classification_chunks"

    def __init__(
        self,
        *,
        created: ClassificationChunkCreation,
        model_for_adaptation: adaptation.llm.ConcreteModel | None,
        timing: TimingData | None,
    ) -> None:
        super().__init__()
        self.created = created
        self.model_for_adaptation = model_for_adaptation
        self.timing = timing

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created: orm.Mapped[ClassificationChunkCreation] = orm.relationship(back_populates="classification_chunk")

    classifications: orm.Mapped[list[ClassificationByChunk]] = orm.relationship(back_populates="classification_chunk")

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


class ClassificationChunkCreation(OrmBase):
    __tablename__ = "classification_chunk_creations"
    __mapper_args__ = {"polymorphic_on": "kind"}

    def __init__(self, *, at: datetime.datetime) -> None:
        super().__init__()
        self.at = at

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ClassificationChunk.id), primary_key=True)
    kind: orm.Mapped[str]

    at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))

    classification_chunk: orm.Mapped[ClassificationChunk] = orm.relationship(
        foreign_keys=[id], remote_side=[ClassificationChunk.id], back_populates="created"
    )


class ClassificationByChunk(Classification):
    __tablename__ = "classifications__by_chunk"
    __mapper_args__ = {"polymorphic_identity": "by_chunk"}

    def __init__(
        self,
        *,
        exercise: AdaptableExercise,
        at: datetime.datetime,
        classification_chunk: ClassificationChunk,
        exercise_class: ExerciseClass | None,
    ) -> None:
        super().__init__(exercise=exercise, at=at, exercise_class=exercise_class)
        self.classification_chunk = classification_chunk

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Classification.id), primary_key=True)

    classification_chunk_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ClassificationChunk.id))
    classification_chunk: orm.Mapped[ClassificationChunk] = orm.relationship(
        foreign_keys=[classification_chunk_id], remote_side=[ClassificationChunk.id], back_populates="classifications"
    )


class ExerciseClassCreationByChunk(ExerciseClassCreation):
    __tablename__ = "exercise_class_creations__by_chunk"
    __mapper_args__ = {"polymorphic_identity": "by_chunk"}

    def __init__(self, *, at: datetime.datetime, classification_chunk: ClassificationChunk) -> None:
        super().__init__(at=at)
        self.classification_chunk = classification_chunk

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseClassCreation.id), primary_key=True)
    classification_chunk_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ClassificationChunk.id))
    classification_chunk: orm.Mapped[ClassificationChunk] = orm.relationship(
        foreign_keys=[classification_chunk_id], remote_side=[ClassificationChunk.id]
    )


class AdaptationCreationByChunk(AdaptationCreation):
    __tablename__ = "adaptation_creations__by_chunk"
    __mapper_args__ = {"polymorphic_identity": "by_chunk"}

    def __init__(self, *, at: datetime.datetime, classification_chunk: ClassificationChunk) -> None:
        super().__init__(at=at)
        self.classification_chunk = classification_chunk

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(AdaptationCreation.id), primary_key=True)

    classification_chunk_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ClassificationChunk.id))
    classification_chunk: orm.Mapped[ClassificationChunk] = orm.relationship(
        foreign_keys=[classification_chunk_id], remote_side=[ClassificationChunk.id]
    )


annotate_new_tables("classification")
