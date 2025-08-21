from __future__ import annotations

import datetime
import typing

from sqlalchemy import orm
import sqlalchemy as sql

from .. import adaptation
from .. import extraction
from ..any_json import JsonDict
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

    extraction_batches: orm.Mapped[list[TextbookExtractionBatch]] = orm.relationship(back_populates="textbook")


class ExerciseLocationTextbook(ExerciseLocation):
    __tablename__ = "exercise_locations__textbook"
    __mapper_args__ = {"polymorphic_identity": "textbook"}

    def __init__(
        self, *, textbook: Textbook, page_number: int, exercise_number: str, removed_from_textbook: bool
    ) -> None:
        super().__init__()
        self.textbook = textbook
        self.page_number = page_number
        self.exercise_number = exercise_number
        self.removed_from_textbook = removed_from_textbook

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExerciseLocation.id), primary_key=True)

    textbook_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Textbook.id))
    textbook: orm.Mapped[Textbook] = orm.relationship(foreign_keys=[textbook_id], remote_side=[Textbook.id])

    page_number: orm.Mapped[int]
    # Custom collation: migrations/versions/429d2fb463dd_exercise_number_collation.py
    exercise_number: orm.Mapped[str] = orm.mapped_column(sql.String(collation="exercise_number"))
    removed_from_textbook: orm.Mapped[bool]


class TextbookExtractionBatch(OrmBase, CreatedByUserMixin):
    __tablename__ = "textbook_extraction_batches"

    def __init__(
        self,
        *,
        created_at: datetime.datetime,
        created_by: str,
        pdf_file_range: PdfFileRange,
        textbook: Textbook,
        removed_from_textbook: bool,
        first_textbook_page_number: int,
        model_for_extraction: extraction.llm.ConcreteModel,
        model_for_adaptation: adaptation.llm.ConcreteModel,
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by = created_by
        self.pdf_file_range = pdf_file_range
        self.textbook = textbook
        self.removed_from_textbook = removed_from_textbook
        self.first_textbook_page_number = first_textbook_page_number
        self.model_for_extraction = model_for_extraction
        self.model_for_adaptation = model_for_adaptation

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    pdf_file_range_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(PdfFileRange.id))
    pdf_file_range: orm.Mapped[PdfFileRange] = orm.relationship(
        foreign_keys=[pdf_file_range_id], remote_side=[PdfFileRange.id]
    )

    textbook_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Textbook.id))
    textbook: orm.Mapped[Textbook] = orm.relationship(
        foreign_keys=[textbook_id], remote_side=[Textbook.id], back_populates="extraction_batches"
    )
    removed_from_textbook: orm.Mapped[bool]

    first_textbook_page_number: orm.Mapped[int]

    _model_for_extraction: orm.Mapped[JsonDict] = orm.mapped_column("model_for_extraction", sql.JSON)

    @property
    def model_for_extraction(self) -> extraction.llm.ConcreteModel:
        return extraction.llm.validate(self._model_for_extraction)

    @model_for_extraction.setter
    def model_for_extraction(self, value: extraction.llm.ConcreteModel) -> None:
        self._model_for_extraction = value.model_dump()

    _model_for_adaptation: orm.Mapped[JsonDict] = orm.mapped_column("model_for_adaptation", sql.JSON)

    @property
    def model_for_adaptation(self) -> adaptation.llm.ConcreteModel:
        return adaptation.llm.validate(self._model_for_adaptation)

    @model_for_adaptation.setter
    def model_for_adaptation(self, value: adaptation.llm.ConcreteModel) -> None:
        self._model_for_adaptation = value.model_dump()

    page_extraction_creations: orm.Mapped[list[PageExtractionCreationByTextbook]] = orm.relationship(
        back_populates="textbook_extraction_batch"
    )


class PageExtractionCreationByTextbook(PageExtractionCreation):
    __tablename__ = "page_extraction_creations__by_textbook"
    __mapper_args__ = {"polymorphic_identity": "by_textbook"}

    def __init__(self, *, at: datetime.datetime, textbook_extraction_batch: TextbookExtractionBatch) -> None:
        super().__init__(at=at)
        self.textbook_extraction_batch = textbook_extraction_batch

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(PageExtractionCreation.id), primary_key=True)

    textbook_extraction_batch_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(TextbookExtractionBatch.id))
    textbook_extraction_batch: orm.Mapped[TextbookExtractionBatch] = orm.relationship(
        foreign_keys=[textbook_extraction_batch_id],
        remote_side=[TextbookExtractionBatch.id],
        back_populates="page_extraction_creations",
    )


annotate_new_tables("textbooks")
