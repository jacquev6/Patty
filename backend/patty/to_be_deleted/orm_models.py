from __future__ import annotations

import datetime

from sqlalchemy import orm
import sqlalchemy as sql

from ..any_json import JsonDict, JsonList
from ..database_utils import OrmBase, annotate_new_tables


class OldTextbook(OrmBase):
    __tablename__ = "old_textbooks"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]
    title: orm.Mapped[str]
    editor: orm.Mapped[str | None]
    year: orm.Mapped[int | None]
    isbn: orm.Mapped[str | None]


class OldBaseExercise(OrmBase):
    __tablename__ = "old_exercises"
    __mapper_args__ = {"polymorphic_on": "kind"}

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    kind: orm.Mapped[str]
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str | None]
    textbook_id: orm.Mapped[int | None] = orm.mapped_column()
    removed_from_textbook: orm.Mapped[bool]
    page_number: orm.Mapped[int | None] = orm.mapped_column()
    exercise_number: orm.Mapped[str | None] = orm.mapped_column(sql.String(collation="exercise_number"))


class OldExternalExercise(OldBaseExercise):
    __tablename__ = "old_external_exercises"
    __mapper_args__ = {"polymorphic_identity": "external"}

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(OldBaseExercise.id), primary_key=True)
    original_file_name: orm.Mapped[str]


class OldPdfFile(OrmBase):
    __tablename__ = "old_pdf_files"

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]  # All 'PdfFile's are created manually
    sha256: orm.Mapped[str] = orm.mapped_column(primary_key=True)
    bytes_count: orm.Mapped[int]
    pages_count: orm.Mapped[int]
    known_file_names: orm.Mapped[list[str]] = orm.mapped_column(sql.JSON)


class OldPdfFileRange(OrmBase):
    __tablename__ = "old_pdf_file_ranges"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]
    pdf_file_sha256: orm.Mapped[str]
    pdf_file_first_page_number: orm.Mapped[int]
    pages_count: orm.Mapped[int]


class OldExtractionStrategy(OrmBase):
    __tablename__ = "old_extraction_strategies"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]
    model: orm.Mapped[JsonDict] = orm.mapped_column(sql.JSON)
    prompt: orm.Mapped[str]


class OldExtractionBatch(OrmBase):
    __tablename__ = "old_extraction_batches"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]
    strategy_id: orm.Mapped[int]
    range_id: orm.Mapped[int]
    run_classification: orm.Mapped[bool]
    model_for_adaptation: orm.Mapped[JsonDict | None] = orm.mapped_column(sql.JSON)


class OldPageExtraction(OrmBase):
    __tablename__ = "old_page_extractions"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]
    extraction_batch_id: orm.Mapped[int]
    page_number: orm.Mapped[int]
    assistant_response: orm.Mapped[JsonDict | None] = orm.mapped_column(sql.JSON)


class OldClassificationBatch(OrmBase):
    __tablename__ = "old_classification_batches"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str | None]
    created_by_page_extraction_id: orm.Mapped[int | None]
    model_for_adaptation: orm.Mapped[JsonDict | None] = orm.mapped_column(sql.JSON)


class OldExerciseClass(OrmBase):
    __tablename__ = "old_exercise_classes"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str | None]
    created_by_classification_batch_id: orm.Mapped[int | None]
    name: orm.Mapped[str]
    latest_strategy_settings_id: orm.Mapped[int | None]


class OldAdaptableExercise(OldBaseExercise):
    __tablename__ = "old_adaptable_exercises"
    __mapper_args__ = {"polymorphic_identity": "adaptable"}

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(OldBaseExercise.id), primary_key=True)
    created_by_page_extraction_id: orm.Mapped[int | None]
    full_text: orm.Mapped[str]
    instruction_hint_example_text: orm.Mapped[str | None]
    statement_text: orm.Mapped[str | None]
    classified_at: orm.Mapped[datetime.datetime | None] = orm.mapped_column(sql.DateTime(timezone=True))
    classified_by_classification_batch_id: orm.Mapped[int | None]
    classified_by_username: orm.Mapped[str | None]
    exercise_class_id: orm.Mapped[int | None]


class OldAdaptationStrategySettings(OrmBase):
    __tablename__ = "old_adaptation_strategy_settings"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]
    exercise_class_id: orm.Mapped[int | None]
    parent_id: orm.Mapped[int | None]
    system_prompt: orm.Mapped[str]
    response_specification: orm.Mapped[JsonDict] = orm.mapped_column(sql.JSON)


class OldAdaptationStrategy(OrmBase):
    __tablename__ = "old_adaptation_strategies"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str | None]
    created_by_classification_batch_id: orm.Mapped[int | None]
    settings_id: orm.Mapped[int]
    model: orm.Mapped[JsonDict] = orm.mapped_column(sql.JSON)


class OldAdaptationBatch(OrmBase):
    __tablename__ = "old_adaptation_batches"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]
    strategy_id: orm.Mapped[int]
    textbook_id: orm.Mapped[int | None]
    removed_from_textbook: orm.Mapped[bool]


class OldAdaptation(OrmBase):
    __tablename__ = "old_adaptations"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str | None]
    exercise_id: orm.Mapped[int]
    strategy_id: orm.Mapped[int]
    classification_batch_id: orm.Mapped[int | None]
    adaptation_batch_id: orm.Mapped[int | None]
    raw_llm_conversations: orm.Mapped[JsonList] = orm.mapped_column(sql.JSON)
    initial_assistant_response: orm.Mapped[JsonDict | None] = orm.mapped_column(sql.JSON)
    adjustments: orm.Mapped[JsonList] = orm.mapped_column(sql.JSON)
    manual_edit: orm.Mapped[JsonDict | None] = orm.mapped_column(sql.JSON)


annotate_new_tables("old")
