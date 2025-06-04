import datetime

from sqlalchemy import orm
import sqlalchemy as sql

from . import batch
from ..database_utils import OrmBase


class OldTextbook(OrmBase):
    __tablename__ = "old_adaptation_textbooks"

    __table_args__ = (sql.CheckConstraint("title != ''", name="title_not_empty"),)

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_by: orm.Mapped[str]
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))

    title: orm.Mapped[str]

    batches: orm.Mapped[list["batch.OldBatch"]] = orm.relationship(
        foreign_keys="OldBatch.textbook_id", back_populates="textbook", order_by="OldBatch.id"
    )

    external_exercises: orm.Mapped[list["OldExternalExercise"]] = orm.relationship(
        foreign_keys="OldExternalExercise.textbook_id", back_populates="textbook", order_by="OldExternalExercise.id"
    )


class OldExternalExercise(OrmBase):
    __tablename__ = "old_adaptation_external_exercises"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_by: orm.Mapped[str]
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))

    textbook_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(OldTextbook.id))
    textbook: orm.Mapped[OldTextbook] = orm.relationship(back_populates="external_exercises")
    removed_from_textbook: orm.Mapped[bool]

    page_number: orm.Mapped[int | None]
    exercise_number: orm.Mapped[str | None] = orm.mapped_column(sql.String(collation="exercise_number"))
    original_file_name: orm.Mapped[str]
