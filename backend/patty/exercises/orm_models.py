# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import annotations

import datetime

from sqlalchemy import orm
import sqlalchemy as sql

from ..database_utils import OrmBase, annotate_new_tables


class Exercise(OrmBase):
    __tablename__ = "exercises"
    __mapper_args__ = {"polymorphic_on": "kind"}

    def __init__(self, *, created: ExerciseCreation, location: ExerciseLocation) -> None:
        super().__init__()
        self.created = created
        self.location = location

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    kind: orm.Mapped[str]

    created: orm.Mapped[ExerciseCreation] = orm.relationship(back_populates="exercise")
    location: orm.Mapped[ExerciseLocation] = orm.relationship(back_populates="exercise")


class ExerciseCreation(OrmBase):
    __tablename__ = "exercise_creations"
    __mapper_args__ = {"polymorphic_on": "kind"}

    def __init__(self, *, at: datetime.datetime) -> None:
        super().__init__()
        self.at = at

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Exercise.id), primary_key=True)
    kind: orm.Mapped[str]
    at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))

    exercise: orm.Mapped[Exercise] = orm.relationship(
        foreign_keys=[id], remote_side=[Exercise.id], back_populates="created"
    )


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

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Exercise.id), primary_key=True)
    kind: orm.Mapped[str]

    exercise: orm.Mapped[Exercise] = orm.relationship(
        foreign_keys=[id], remote_side=[Exercise.id], back_populates="location"
    )


class ExerciseLocationMaybePageAndNumber(ExerciseLocation):
    __tablename__ = "exercise_locations__maybe_page_and_number"
    __mapper_args__ = {"polymorphic_identity": "maybe_page_and_number"}

    def __init__(self, page_number: int | None, exercise_number: str | None) -> None:
        super().__init__()
        self.page_number = page_number
        self.exercise_number = exercise_number

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseLocation.id), primary_key=True)
    page_number: orm.Mapped[int | None]
    exercise_number: orm.Mapped[str | None]


class ExerciseImage(OrmBase):
    __tablename__ = "exercise_images"

    def __init__(self, *, local_identifier: str, created: ExerciseImageCreation) -> None:
        super().__init__()
        self.local_identifier = local_identifier
        self.created = created

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    local_identifier: orm.Mapped[str]

    created: orm.Mapped[ExerciseImageCreation] = orm.relationship(back_populates="image")


class ExerciseImageCreation(OrmBase):
    __tablename__ = "exercise_image_creations"
    __mapper_args__ = {"polymorphic_on": "kind"}

    def __init__(self, *, at: datetime.datetime) -> None:
        super().__init__()
        self.at = at

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseImage.id), primary_key=True)
    kind: orm.Mapped[str]
    at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))

    image: orm.Mapped[ExerciseImage] = orm.relationship(
        foreign_keys=[id], remote_side=[ExerciseImage.id], back_populates="created"
    )


annotate_new_tables("exercises")
