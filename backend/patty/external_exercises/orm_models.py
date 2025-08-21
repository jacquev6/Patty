from __future__ import annotations

from sqlalchemy import orm
import sqlalchemy as sql

from ..database_utils import annotate_new_tables
from ..exercises import Exercise, ExerciseCreation, ExerciseLocation


class ExternalExercise(Exercise):
    __tablename__ = "exercises__external"
    __mapper_args__ = {"polymorphic_identity": "external"}

    def __init__(self, *, created: ExerciseCreation, location: ExerciseLocation, original_file_name: str) -> None:
        super().__init__(created=created, location=location)
        self.original_file_name = original_file_name

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Exercise.id), primary_key=True)

    original_file_name: orm.Mapped[str]


annotate_new_tables("external")
