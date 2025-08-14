from __future__ import annotations

import datetime
import typing

from sqlalchemy import orm
import sqlalchemy as sql

from ..database_utils import OrmBase, CreatedByUserMixin, annotate_new_tables
from ..exercises import Exercise, ExerciseLocation
from ..extraction import PdfFileRange, PageExtractionCreation


class Textbook(OrmBase, CreatedByUserMixin):
    __tablename__ = "textbooks"

    def __init__(
        self,
        *,
        created_at: datetime.datetime,
        created_by: str,
        title: str,
        publisher: str | None,
        year: int | None,
        isbn: str | None,
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by = created_by
        self.title = title
        self.publisher = publisher
        self.year = year
        self.isbn = isbn

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    title: orm.Mapped[str]
    publisher: orm.Mapped[str | None]
    year: orm.Mapped[int | None]
    isbn: orm.Mapped[str | None]

    @staticmethod
    def make_ordered_exercises_request(id: int) -> sql.Select[tuple[Exercise]]:
        return (
            sql.select(Exercise)
            .join(ExerciseLocationTextbook)
            .where(ExerciseLocationTextbook.textbook_id == id)
            .order_by(ExerciseLocationTextbook.page_number, ExerciseLocationTextbook.exercise_number)
        )

    def fetch_ordered_exercises(self) -> typing.Iterable[Exercise]:
        session = orm.object_session(self)
        assert session is not None
        return session.execute(self.make_ordered_exercises_request(self.id)).scalars().all()


class ExerciseLocationTextbook(ExerciseLocation):
    __tablename__ = "exercise_locations__textbook"
    __mapper_args__ = {"polymorphic_identity": "textbook"}

    def __init__(self, *, textbook: Textbook, page_number: int, exercise_number: str) -> None:
        super().__init__()
        self.textbook = textbook
        self.page_number = page_number
        self.exercise_number = exercise_number

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseLocation.id), primary_key=True)

    textbook_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Textbook.id))
    textbook: orm.Mapped[Textbook] = orm.relationship(foreign_keys=[textbook_id], remote_side=[Textbook.id])

    page_number: orm.Mapped[int]
    # Custom collation: migrations/versions/429d2fb463dd_exercise_number_collation.py
    exercise_number: orm.Mapped[str] = orm.mapped_column(sql.String(collation="exercise_number"))


class TextbookStartingPoint(OrmBase, CreatedByUserMixin):
    __tablename__ = "textbook_starting_points"

    def __init__(
        self, *, created_at: datetime.datetime, created_by: str, textbook: Textbook, first_page_number: int
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by = created_by
        self.textbook = textbook
        self.first_page_number = first_page_number

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    textbook_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Textbook.id))
    textbook: orm.Mapped[Textbook] = orm.relationship(foreign_keys=[textbook_id], remote_side=[Textbook.id])

    first_page_number: orm.Mapped[int]


class PdfFileTextbookMapping(OrmBase, CreatedByUserMixin):
    __tablename__ = "pdf_file_textbook_mappings"

    def __init__(
        self,
        *,
        created_at: datetime.datetime,
        created_by: str,
        pdf_file_range: PdfFileRange,
        textbook_starting_point: TextbookStartingPoint,
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by = created_by
        self.pdf_file_range = pdf_file_range
        self.textbook_starting_point = textbook_starting_point

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    pdf_file_range_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(PdfFileRange.id))
    pdf_file_range: orm.Mapped[PdfFileRange] = orm.relationship(
        foreign_keys=[pdf_file_range_id], remote_side=[PdfFileRange.id]
    )

    textbook_starting_point_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(TextbookStartingPoint.id))
    textbook_starting_point: orm.Mapped[TextbookStartingPoint] = orm.relationship(
        foreign_keys=[textbook_starting_point_id], remote_side=[TextbookStartingPoint.id]
    )


class PageExtractionCreationByTextbook(PageExtractionCreation):
    __tablename__ = "page_extraction_creations__by_textbook"
    __mapper_args__ = {"polymorphic_identity": "by_textbook"}

    def __init__(self, *, at: datetime.datetime, pdf_file_textbook_mapping: PdfFileTextbookMapping) -> None:
        super().__init__(at=at)
        self.pdf_file_textbook_mapping = pdf_file_textbook_mapping

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(PageExtractionCreation.id), primary_key=True)

    pdf_file_textbook_mapping_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(PdfFileTextbookMapping.id))
    pdf_file_textbook_mapping: orm.Mapped[PdfFileTextbookMapping] = orm.relationship(
        foreign_keys=[pdf_file_textbook_mapping_id], remote_side=[PdfFileTextbookMapping.id]
    )


annotate_new_tables("textbooks")
