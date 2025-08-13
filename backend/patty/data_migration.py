import datetime
import itertools
import typing

from recursive_diff import recursive_diff
from sqlalchemy import orm
import pydantic
import sqlalchemy as sql

from . import adapted
from . import database_utils
from .adaptation import llm as adaptation_llm
from .adaptation import orm_models as adaptation_orm_models
from .adaptation import responses as adaptation_responses
from .adaptation import strategy as adaptation_strategy
from .classification import orm_models as classification_orm_models
from .exercises import orm_models as exercises_orm_models
from .external_exercises import orm_models as external_exercises_orm_models
from .extraction import llm as extraction_llm
from .extraction import orm_models as extraction_orm_models
from .extraction import assistant_responses as extraction_responses
from .textbooks import orm_models as textbooks_orm_models
from .to_be_deleted import orm_models as to_be_deleted_orm_models


the_only_extraction_model = extraction_llm.GeminiModel(provider="gemini", name="gemini-2.0-flash")


def migrate(session: database_utils.Session) -> None:
    expected_data = gather_expected_data(session)
    reset_auto_increments(session)
    do_migrate_data(session)
    fix_auto_increments(session)
    actual_data = gather_actual_data(session)

    for data in (expected_data, actual_data):
        data.pop("adaptation_strategies", None)  # Because we've removed the notion of strategy

        for row in data["adaptation_batches"]:
            row.pop("strategy_id", None)  # Because we've removed the notion of strategy
            row.pop("textbook_id", None)  # Because we've removed adaptation batches from textbooks
            row.pop("removed_from_textbook", None)  # Because we've removed adaptation batches from textbooks

        for row in data["adaptations"]:
            row.pop("strategy_id", None)  # Because we've removed the notion of strategy

        for rows in data.values():
            if len(rows) > 0:
                if "id" in rows[0]:
                    rows.sort(key=lambda row: row["id"])
                elif "sha256" in rows[0]:
                    rows.sort(key=lambda row: row["sha256"])
                else:
                    assert False

    diffs = list(
        itertools.islice(
            filter(
                lambda x: all(
                    ignored not in x
                    for ignored in (
                        "Pair increaseHorizontalSpace:False is in RHS only",
                        "Pair subscript:False is in RHS only",
                        "Pair superscript:False is in RHS only",
                    )
                ),
                recursive_diff(expected_data, actual_data),
            ),
            20,
        )
    )
    if diffs:
        for diff in diffs:
            print(diff)
        raise ValueError("Data migration failed due to differences in expected and actual data.")


def gather_expected_data(session: database_utils.Session) -> dict[str, list[typing.Any]]:
    return {
        table.name[4:]: [row._asdict() for row in session.execute(sql.select(table)).all()]
        for table in database_utils.OrmBase.metadata.sorted_tables
        if table.name.startswith("old_")
    }


def reset_auto_increments(session: database_utils.Session) -> None:
    for table in database_utils.OrmBase.metadata.sorted_tables:
        if any(col.name == "id" and col.autoincrement is True for col in table.columns):
            session.execute(sql.text(f"ALTER SEQUENCE {table.name}_id_seq RESTART WITH 1"))


def do_migrate_data(session: database_utils.Session) -> None:
    def add(id: int, obj: typing.Any) -> None:
        obj.id = id
        session.add(obj)

    with session.no_autoflush:
        for old_pdf_file in session.execute(sql.select(to_be_deleted_orm_models.OldPdfFile)).scalars():
            session.add(
                extraction_orm_models.PdfFile(
                    created_at=old_pdf_file.created_at,
                    created_by=old_pdf_file.created_by_username,
                    sha256=old_pdf_file.sha256,
                    bytes_count=old_pdf_file.bytes_count,
                    pages_count=old_pdf_file.pages_count,
                    known_file_names=old_pdf_file.known_file_names,
                )
            )

        session.flush()

        for old_pdf_file_range in session.execute(
            sql.select(to_be_deleted_orm_models.OldPdfFileRange).order_by(to_be_deleted_orm_models.OldPdfFileRange.id)
        ).scalars():
            pdf_file = session.get_one(extraction_orm_models.PdfFile, old_pdf_file_range.pdf_file_sha256)
            assert pdf_file is not None
            add(
                old_pdf_file_range.id,
                extraction_orm_models.PdfFileRange(
                    pdf_file=pdf_file,
                    first_page_number=old_pdf_file_range.pdf_file_first_page_number,
                    pages_count=old_pdf_file_range.pages_count,
                    created_at=old_pdf_file_range.created_at,
                    created_by=old_pdf_file_range.created_by_username,
                ),
            )

        for old_textbook in session.execute(
            sql.select(to_be_deleted_orm_models.OldTextbook).order_by(to_be_deleted_orm_models.OldTextbook.id)
        ).scalars():
            add(
                old_textbook.id,
                textbooks_orm_models.Textbook(
                    created_at=old_textbook.created_at,
                    created_by=old_textbook.created_by_username,
                    title=old_textbook.title,
                    publisher=old_textbook.editor,
                    year=old_textbook.year,
                    isbn=old_textbook.isbn,
                ),
            )

        for old_extraction_strategy in session.execute(
            sql.select(to_be_deleted_orm_models.OldExtractionStrategy).order_by(
                to_be_deleted_orm_models.OldExtractionStrategy.id
            )
        ).scalars():
            assert old_extraction_strategy.model == the_only_extraction_model.model_dump()
            add(
                old_extraction_strategy.id,
                extraction_orm_models.ExtractionSettings(
                    created_by=old_extraction_strategy.created_by_username,
                    created_at=old_extraction_strategy.created_at,
                    prompt=old_extraction_strategy.prompt,
                ),
            )

        session.flush()

        for old_extraction_batch in session.execute(
            sql.select(to_be_deleted_orm_models.OldExtractionBatch).order_by(
                to_be_deleted_orm_models.OldExtractionBatch.id
            )
        ).scalars():
            pdf_range = session.get_one(extraction_orm_models.PdfFileRange, old_extraction_batch.range_id)
            settings = session.get_one(extraction_orm_models.ExtractionSettings, old_extraction_batch.strategy_id)
            add(
                old_extraction_batch.id,
                extraction_orm_models.SandboxExtractionBatch(
                    created_at=old_extraction_batch.created_at,
                    created_by=old_extraction_batch.created_by_username,
                    pdf_range=pdf_range,
                    settings=settings,
                    model=the_only_extraction_model,
                    run_classification=old_extraction_batch.run_classification,
                    model_for_adaptation=(
                        None
                        if old_extraction_batch.model_for_adaptation is None
                        else pydantic.RootModel[adaptation_llm.ConcreteModel]
                        .model_validate(old_extraction_batch.model_for_adaptation)
                        .root
                    ),
                ),
            )

        session.flush()

        for old_page_extraction in session.execute(
            sql.select(to_be_deleted_orm_models.OldPageExtraction).order_by(
                to_be_deleted_orm_models.OldPageExtraction.id
            )
        ).scalars():
            sandbox_extraction_batch = session.get_one(
                extraction_orm_models.SandboxExtractionBatch, old_page_extraction.extraction_batch_id
            )
            add(
                old_page_extraction.id,
                extraction_orm_models.PageExtraction(
                    created=extraction_orm_models.PageExtractionCreationBySandboxExtractionBatch(
                        at=old_page_extraction.created_at, sandbox_extraction_batch=sandbox_extraction_batch
                    ),
                    pdf_range=sandbox_extraction_batch.pdf_range,
                    pdf_page_number=old_page_extraction.page_number,
                    settings=sandbox_extraction_batch.settings,
                    model=sandbox_extraction_batch.model,
                    run_classification=sandbox_extraction_batch.run_classification,
                    model_for_adaptation=sandbox_extraction_batch.model_for_adaptation,
                    assistant_response=(
                        None
                        if old_page_extraction.assistant_response is None
                        else pydantic.RootModel[extraction_responses.AssistantResponse]
                        .model_validate(old_page_extraction.assistant_response)
                        .root
                    ),
                ),
            )

        for old_external_exercise in session.execute(
            sql.select(to_be_deleted_orm_models.OldExternalExercise).order_by(
                to_be_deleted_orm_models.OldExternalExercise.id
            )
        ).scalars():
            assert False

        session.flush()

        for old_classification_batch in session.execute(
            sql.select(to_be_deleted_orm_models.OldClassificationBatch).order_by(
                to_be_deleted_orm_models.OldClassificationBatch.id
            )
        ).scalars():
            model_for_adaptation = (
                None
                if old_classification_batch.model_for_adaptation is None
                else pydantic.RootModel[adaptation_llm.ConcreteModel]
                .model_validate(old_classification_batch.model_for_adaptation)
                .root
            )

            classification_chunk_created: classification_orm_models.ExerciseClassificationChunkCreation
            if old_classification_batch.created_by_username is not None:
                classification_batch = classification_orm_models.SandboxClassificationBatch(
                    created_at=old_classification_batch.created_at,
                    created_by=old_classification_batch.created_by_username,
                    model_for_adaptation=model_for_adaptation,
                )
                add(old_classification_batch.id, classification_batch)
                classification_chunk_created = (
                    classification_orm_models.ExerciseClassificationChunkCreationBySandboxClassificationBatch(
                        at=old_classification_batch.created_at, sandbox_classification_batch=classification_batch
                    )
                )
            elif old_classification_batch.created_by_page_extraction_id is not None:
                page_extraction = session.get_one(
                    extraction_orm_models.PageExtraction, old_classification_batch.created_by_page_extraction_id
                )
                classification_chunk_created = (
                    extraction_orm_models.ExerciseClassificationChunkCreationByPageExtraction(
                        at=old_classification_batch.created_at, page_extraction=page_extraction
                    )
                )
            else:
                assert False

            add(
                old_classification_batch.id,
                classification_orm_models.ExerciseClassificationChunk(
                    created=classification_chunk_created, model_for_adaptation=model_for_adaptation
                ),
            )

        session.flush()

        for old_exercise_class in session.execute(
            sql.select(to_be_deleted_orm_models.OldExerciseClass).order_by(to_be_deleted_orm_models.OldExerciseClass.id)
        ).scalars():
            exercise_class_created: classification_orm_models.ExerciseClassCreation
            if old_exercise_class.created_by_username is not None:
                exercise_class_created = classification_orm_models.ExerciseClassCreationByUser(
                    at=old_exercise_class.created_at, username=old_exercise_class.created_by_username
                )
            elif old_exercise_class.created_by_classification_batch_id is not None:
                classification_chunk = session.get_one(
                    classification_orm_models.ExerciseClassificationChunk,
                    old_exercise_class.created_by_classification_batch_id,
                )
                exercise_class_created = classification_orm_models.ExerciseClassCreationByClassificationChunk(
                    at=old_exercise_class.created_at, classification_chunk=classification_chunk
                )

            add(
                old_exercise_class.id,
                adaptation_orm_models.ExerciseClass(
                    created=exercise_class_created, name=old_exercise_class.name, latest_strategy_settings=None
                ),
            )

        session.flush()

        for old_adaptation_strategy_settings in session.execute(
            sql.select(to_be_deleted_orm_models.OldAdaptationStrategySettings).order_by(
                to_be_deleted_orm_models.OldAdaptationStrategySettings.id
            )
        ).scalars():
            exercise_class: adaptation_orm_models.ExerciseClass | None
            if old_adaptation_strategy_settings.exercise_class_id is None:
                exercise_class = None
            else:
                exercise_class = session.get_one(
                    adaptation_orm_models.ExerciseClass, old_adaptation_strategy_settings.exercise_class_id
                )

            parent: adaptation_orm_models.ExerciseAdaptationSettings | None
            if old_adaptation_strategy_settings.parent_id is None:
                parent = None
            else:
                session.flush()
                parent = session.get_one(
                    adaptation_orm_models.ExerciseAdaptationSettings, old_adaptation_strategy_settings.parent_id
                )

            add(
                old_adaptation_strategy_settings.id,
                adaptation_orm_models.ExerciseAdaptationSettings(
                    created_at=old_adaptation_strategy_settings.created_at,
                    created_by=old_adaptation_strategy_settings.created_by_username,
                    exercise_class=exercise_class,
                    parent=parent,
                    system_prompt=old_adaptation_strategy_settings.system_prompt,
                    response_specification=pydantic.RootModel[adaptation_strategy.ConcreteLlmResponseSpecification]
                    .model_validate(old_adaptation_strategy_settings.response_specification)
                    .root,
                ),
            )

        session.flush()

        for old_exercise_class in session.execute(
            sql.select(to_be_deleted_orm_models.OldExerciseClass).order_by(to_be_deleted_orm_models.OldExerciseClass.id)
        ).scalars():
            exercise_class = session.get_one(adaptation_orm_models.ExerciseClass, old_exercise_class.id)
            if old_exercise_class.latest_strategy_settings_id is not None:
                exercise_class.latest_strategy_settings = session.get_one(
                    adaptation_orm_models.ExerciseAdaptationSettings, old_exercise_class.latest_strategy_settings_id
                )

        for old_adaptation_batch in session.execute(
            sql.select(to_be_deleted_orm_models.OldAdaptationBatch).order_by(
                to_be_deleted_orm_models.OldAdaptationBatch.id
            )
        ).scalars():
            strategy = session.get_one(to_be_deleted_orm_models.OldAdaptationStrategy, old_adaptation_batch.strategy_id)
            model = pydantic.RootModel[adaptation_llm.ConcreteModel].model_validate(strategy.model).root
            adaptation_settings = session.get_one(
                adaptation_orm_models.ExerciseAdaptationSettings, strategy.settings_id
            )

            add(
                old_adaptation_batch.id,
                adaptation_orm_models.SandboxAdaptationBatch(
                    created_by=old_adaptation_batch.created_by_username,
                    created_at=old_adaptation_batch.created_at,
                    settings=adaptation_settings,
                    model=model,
                ),
            )

        session.flush()

        for old_adaptable_exercise in session.execute(
            sql.select(to_be_deleted_orm_models.OldAdaptableExercise).order_by(
                to_be_deleted_orm_models.OldAdaptableExercise.id
            )
        ).scalars():
            exercise_created: exercises_orm_models.ExerciseCreation
            if old_adaptable_exercise.created_by_username is not None:
                exercise_created = exercises_orm_models.ExerciseCreationByUser(
                    at=old_adaptable_exercise.created_at, username=old_adaptable_exercise.created_by_username
                )
            elif old_adaptable_exercise.created_by_page_extraction_id is not None:
                page_extraction = session.get_one(
                    extraction_orm_models.PageExtraction, old_adaptable_exercise.created_by_page_extraction_id
                )
                exercise_created = extraction_orm_models.ExerciseCreationByPageExtraction(
                    at=old_adaptable_exercise.created_at, page_extraction=page_extraction
                )
            else:
                assert False

            exercise_location: exercises_orm_models.ExerciseLocation
            if old_adaptable_exercise.textbook_id is None:
                exercise_location = exercises_orm_models.ExerciseLocationMaybePageAndNumber(
                    page_number=old_adaptable_exercise.page_number,
                    exercise_number=old_adaptable_exercise.exercise_number,
                )
            else:
                textbook = session.get_one(textbooks_orm_models.Textbook, old_adaptable_exercise.textbook_id)
                assert old_adaptable_exercise.page_number is not None
                assert old_adaptable_exercise.exercise_number is not None
                exercise_location = textbooks_orm_models.ExerciseLocationTextbook(
                    textbook=textbook,
                    page_number=old_adaptable_exercise.page_number,
                    exercise_number=old_adaptable_exercise.exercise_number,
                )

            exercise = adaptation_orm_models.AdaptableExercise(
                created=exercise_created,
                location=exercise_location,
                removed_from_textbook=old_adaptable_exercise.removed_from_textbook,
                full_text=old_adaptable_exercise.full_text,
                instruction_hint_example_text=old_adaptable_exercise.instruction_hint_example_text,
                statement_text=old_adaptable_exercise.statement_text,
            )
            add(old_adaptable_exercise.id, exercise)
            session.flush()

            if old_adaptable_exercise.classified_at is not None:
                exercise_class = (
                    None
                    if old_adaptable_exercise.exercise_class_id is None
                    else session.get_one(adaptation_orm_models.ExerciseClass, old_adaptable_exercise.exercise_class_id)
                )
                if (
                    old_adaptable_exercise.classified_by_username is not None
                    and old_adaptable_exercise.classified_by_classification_batch_id is not None
                ):
                    classification_chunk = session.get_one(
                        classification_orm_models.ExerciseClassificationChunk,
                        old_adaptable_exercise.classified_by_classification_batch_id,
                    )
                    session.add(
                        classification_orm_models.ExerciseClassificationByClassificationChunk(
                            exercise=exercise,
                            at=old_adaptable_exercise.classified_at - datetime.timedelta(seconds=1),
                            classification_chunk=classification_chunk,
                            exercise_class=exercise_class,
                        )
                    )
                    session.add(
                        classification_orm_models.ExerciseClassificationByUser(
                            exercise=exercise,
                            at=old_adaptable_exercise.classified_at,
                            username=old_adaptable_exercise.classified_by_username,
                            exercise_class=exercise_class,
                        )
                    )
                elif (
                    old_adaptable_exercise.classified_by_username is None
                    and old_adaptable_exercise.classified_by_classification_batch_id is not None
                ):
                    classification_chunk = session.get_one(
                        classification_orm_models.ExerciseClassificationChunk,
                        old_adaptable_exercise.classified_by_classification_batch_id,
                    )
                    session.add(
                        classification_orm_models.ExerciseClassificationByClassificationChunk(
                            exercise=exercise,
                            at=old_adaptable_exercise.classified_at,
                            classification_chunk=classification_chunk,
                            exercise_class=exercise_class,
                        )
                    )
                elif (
                    old_adaptable_exercise.classified_by_username is not None
                    and old_adaptable_exercise.classified_by_classification_batch_id is None
                ):
                    session.add(
                        classification_orm_models.ExerciseClassificationByUser(
                            exercise=exercise,
                            at=old_adaptable_exercise.classified_at,
                            username=old_adaptable_exercise.classified_by_username,
                            exercise_class=exercise_class,
                        )
                    )
                else:
                    assert False

        session.flush()

        for old_adaptation in session.execute(
            sql.select(to_be_deleted_orm_models.OldAdaptation).order_by(to_be_deleted_orm_models.OldAdaptation.id)
        ).scalars():
            exercise = session.get_one(adaptation_orm_models.AdaptableExercise, old_adaptation.exercise_id)
            strategy = session.get_one(to_be_deleted_orm_models.OldAdaptationStrategy, old_adaptation.strategy_id)
            adaptation_model = pydantic.RootModel[adaptation_llm.ConcreteModel].model_validate(strategy.model).root
            adaptation_settings = session.get_one(
                adaptation_orm_models.ExerciseAdaptationSettings, strategy.settings_id
            )

            adaptation_created: adaptation_orm_models.ExerciseAdaptationCreation
            if old_adaptation.adaptation_batch_id is not None:
                adaptation_batch = session.get_one(
                    adaptation_orm_models.SandboxAdaptationBatch, old_adaptation.adaptation_batch_id
                )
                adaptation_created = adaptation_orm_models.ExerciseAdaptationCreationBySandboxAdaptationBatch(
                    at=old_adaptation.created_at, sandbox_adaptation_batch=adaptation_batch
                )
            elif old_adaptation.classification_batch_id is not None:
                classification_chunk = session.get_one(
                    classification_orm_models.ExerciseClassificationChunk, old_adaptation.classification_batch_id
                )
                adaptation_created = classification_orm_models.ExerciseAdaptationCreationByClassificationChunk(
                    at=old_adaptation.created_at, classification_chunk=classification_chunk
                )
            elif old_adaptation.created_by_username is not None:
                adaptation_created = adaptation_orm_models.ExerciseAdaptationCreationByUser(
                    at=old_adaptation.created_at, username=old_adaptation.created_by_username
                )
            else:
                assert False

            add(
                old_adaptation.id,
                adaptation_orm_models.ExerciseAdaptation(
                    created=adaptation_created,
                    exercise=exercise,
                    model=adaptation_model,
                    settings=adaptation_settings,
                    raw_llm_conversations=old_adaptation.raw_llm_conversations,
                    initial_assistant_response=(
                        None
                        if old_adaptation.initial_assistant_response is None
                        else pydantic.RootModel[adaptation_responses.AssistantResponse]
                        .model_validate(old_adaptation.initial_assistant_response)
                        .root
                    ),
                    adjustments=pydantic.RootModel[list[adaptation_responses.Adjustment]]
                    .model_validate(old_adaptation.adjustments)
                    .root,
                    manual_edit=(
                        None
                        if old_adaptation.manual_edit is None
                        else pydantic.RootModel[adapted.Exercise].model_validate(old_adaptation.manual_edit).root
                    ),
                ),
            )

    session.flush()


def fix_auto_increments(session: database_utils.Session) -> None:
    for table in database_utils.OrmBase.metadata.sorted_tables:
        if any(col.name == "id" and col.autoincrement is True for col in table.columns):
            max_id = session.execute(sql.select(sql.func.max(table.c.id))).scalar_one()
            if max_id is None:  # When a table is empty
                max_id = 0
            session.execute(sql.text(f"ALTER SEQUENCE {table.name}_id_seq RESTART WITH {max_id + 1}"))


def gather_actual_data(session: database_utils.Session) -> dict[str, list[typing.Any]]:
    data: dict[str, list[typing.Any]] = {
        "adaptable_exercises": [],
        "adaptation_batches": [],
        "adaptation_strategy_settings": [],
        "adaptations": [],
        "classification_batches": [],
        "exercise_classes": [],
        "exercises": [],
        "external_exercises": [],
        "extraction_batches": [],
        "extraction_strategies": [],
        "page_extractions": [],
        "pdf_file_ranges": [],
        "pdf_files": [],
        "textbooks": [],
    }

    for pdf_file in session.execute(sql.select(extraction_orm_models.PdfFile)).scalars():
        row = asdict(pdf_file)
        row["created_by_username"] = row.pop("created_by")
        data["pdf_files"].append(row)

    for pdf_file_range in session.execute(sql.select(extraction_orm_models.PdfFileRange)).scalars():
        row = asdict(pdf_file_range)
        row["created_by_username"] = row.pop("created_by")
        row["pdf_file_first_page_number"] = row.pop("first_page_number")
        data["pdf_file_ranges"].append(row)

    for textbook in session.execute(sql.select(textbooks_orm_models.Textbook)).scalars():
        row = asdict(textbook)
        row["created_by_username"] = row.pop("created_by")
        row["editor"] = row.pop("publisher")
        data["textbooks"].append(row)

    for extraction_settings in session.execute(sql.select(extraction_orm_models.ExtractionSettings)).scalars():
        row = asdict(extraction_settings)
        row["created_by_username"] = row.pop("created_by")
        row["model"] = the_only_extraction_model.model_dump()
        data["extraction_strategies"].append(row)

    for sandbox_extraction_batch in session.execute(sql.select(extraction_orm_models.SandboxExtractionBatch)).scalars():
        row = asdict(sandbox_extraction_batch)
        row["created_by_username"] = row.pop("created_by")
        row["range_id"] = row.pop("pdf_range_id")
        row["strategy_id"] = row.pop("settings_id")
        row.pop("model")
        data["extraction_batches"].append(row)

    for exercise in session.execute(sql.select(exercises_orm_models.Exercise)).scalars():
        row = asdict(exercise)
        if isinstance(exercise.created, exercises_orm_models.ExerciseCreationByUser):
            row["created_at"] = asdict(exercise.created)["at"]
            row["created_by_username"] = exercise.created.username
        elif isinstance(exercise.created, extraction_orm_models.ExerciseCreationByPageExtraction):
            row["created_at"] = asdict(exercise.created)["at"]
            row["created_by_username"] = None
        else:
            assert False
        if isinstance(exercise.location, exercises_orm_models.ExerciseLocationMaybePageAndNumber):
            row["exercise_number"] = exercise.location.exercise_number
            row["page_number"] = exercise.location.page_number
            row["textbook_id"] = None
        elif isinstance(exercise.location, textbooks_orm_models.ExerciseLocationTextbook):
            row["exercise_number"] = exercise.location.exercise_number
            row["page_number"] = exercise.location.page_number
            row["textbook_id"] = exercise.location.textbook.id
        else:
            assert False
        row.pop("full_text", None)
        row.pop("instruction_hint_example_text", None)
        row.pop("statement_text", None)
        data["exercises"].append(row)

    for adaptable_exercise in session.execute(sql.select(adaptation_orm_models.AdaptableExercise)).scalars():
        row = asdict(adaptable_exercise)
        row["classified_at"] = None
        row["classified_by_classification_batch_id"] = None
        row["classified_by_username"] = None
        row["exercise_class_id"] = None
        for classification in adaptable_exercise.classifications:
            row["exercise_class_id"] = (
                None if classification.exercise_class is None else classification.exercise_class.id
            )
            if isinstance(classification, classification_orm_models.ExerciseClassificationByUser):
                row["classified_at"] = asdict(classification)["at"]
                row["classified_by_username"] = classification.username
                # row["classified_by_classification_b
                # atch_id"] = None
            elif isinstance(classification, classification_orm_models.ExerciseClassificationByClassificationChunk):
                row["classified_at"] = asdict(classification)["at"]
                row["classified_by_username"] = None
                row["classified_by_classification_batch_id"] = classification.classification_chunk.id
            else:
                assert False
        if isinstance(adaptable_exercise.created, exercises_orm_models.ExerciseCreationByUser):
            row["created_by_page_extraction_id"] = None
        elif isinstance(adaptable_exercise.created, extraction_orm_models.ExerciseCreationByPageExtraction):
            row["created_by_page_extraction_id"] = adaptable_exercise.created.page_extraction.id
        else:
            assert False
        row.pop("kind")
        row.pop("removed_from_textbook")
        data["adaptable_exercises"].append(row)

    for external_exercise in session.execute(sql.select(external_exercises_orm_models.ExternalExercise)).scalars():
        assert False

    for page_extraction in session.execute(sql.select(extraction_orm_models.PageExtraction)).scalars():
        row = asdict(page_extraction)
        assert isinstance(page_extraction.created, extraction_orm_models.PageExtractionCreationBySandboxExtractionBatch)
        row["created_at"] = asdict(page_extraction.created)["at"]
        row["created_by_username"] = page_extraction.created.sandbox_extraction_batch.created_by
        row["extraction_batch_id"] = page_extraction.created.sandbox_extraction_batch.id
        row["page_number"] = row.pop("pdf_page_number")
        row.pop("pdf_range_id")
        row.pop("settings_id")
        row.pop("model")
        row.pop("run_classification")
        row.pop("model_for_adaptation")
        data["page_extractions"].append(row)

    for classification_chunk in session.execute(
        sql.select(classification_orm_models.ExerciseClassificationChunk)
    ).scalars():
        row = asdict(classification_chunk)
        if isinstance(
            classification_chunk.created,
            classification_orm_models.ExerciseClassificationChunkCreationBySandboxClassificationBatch,
        ):
            row["created_at"] = asdict(classification_chunk.created)["at"]
            row["created_by_username"] = classification_chunk.created.sandbox_classification_batch.created_by
            row["created_by_page_extraction_id"] = None
        elif isinstance(
            classification_chunk.created, extraction_orm_models.ExerciseClassificationChunkCreationByPageExtraction
        ):
            row["created_at"] = asdict(classification_chunk.created)["at"]
            row["created_by_username"] = None
            row["created_by_page_extraction_id"] = classification_chunk.created.page_extraction.id
        else:
            assert False
        data["classification_batches"].append(row)

    for exercise_class in session.execute(sql.select(adaptation_orm_models.ExerciseClass)).scalars():
        row = asdict(exercise_class)
        if isinstance(exercise_class.created, classification_orm_models.ExerciseClassCreationByUser):
            row["created_at"] = asdict(exercise_class.created)["at"]
            row["created_by_username"] = exercise_class.created.username
            row["created_by_classification_batch_id"] = None
        elif isinstance(exercise_class.created, classification_orm_models.ExerciseClassCreationByClassificationChunk):
            row["created_at"] = asdict(exercise_class.created)["at"]
            row["created_by_username"] = None
            row["created_by_classification_batch_id"] = exercise_class.created.classification_chunk.id
        else:
            assert False
        data["exercise_classes"].append(row)

    for adaptation_strategy_settings in session.execute(
        sql.select(adaptation_orm_models.ExerciseAdaptationSettings)
    ).scalars():
        row = asdict(adaptation_strategy_settings)
        row["created_by_username"] = row.pop("created_by")
        if adaptation_strategy_settings.exercise_class is not None:
            row["exercise_class_id"] = adaptation_strategy_settings.exercise_class.id
        else:
            row["exercise_class_id"] = None
        if adaptation_strategy_settings.parent is not None:
            row["parent_id"] = adaptation_strategy_settings.parent.id
        else:
            row["parent_id"] = None
        row["response_specification"] = adaptation_strategy_settings.response_specification.model_dump()
        data["adaptation_strategy_settings"].append(row)

    for sandbox_adaptation_batch in session.execute(sql.select(adaptation_orm_models.SandboxAdaptationBatch)).scalars():
        row = asdict(sandbox_adaptation_batch)
        row["created_by_username"] = row.pop("created_by")
        row["textbook_id"] = None
        row["removed_from_textbook"] = False
        row.pop("settings_id")
        row.pop("model")
        data["adaptation_batches"].append(row)

    for adaptation in session.execute(sql.select(adaptation_orm_models.ExerciseAdaptation)).scalars():
        row = asdict(adaptation)
        row["created_at"] = asdict(adaptation.created)["at"]
        if isinstance(adaptation.created, adaptation_orm_models.ExerciseAdaptationCreationByUser):
            row["created_by_username"] = adaptation.created.username
            row["adaptation_batch_id"] = None
            row["classification_batch_id"] = None
        elif isinstance(adaptation.created, adaptation_orm_models.ExerciseAdaptationCreationBySandboxAdaptationBatch):
            row["created_by_username"] = adaptation.created.sandbox_adaptation_batch.created_by
            row["adaptation_batch_id"] = adaptation.created.sandbox_adaptation_batch.id
            row["classification_batch_id"] = None
        elif isinstance(adaptation.created, classification_orm_models.ExerciseAdaptationCreationByClassificationChunk):
            row["created_by_username"] = None
            row["adaptation_batch_id"] = None
            row["classification_batch_id"] = adaptation.created.classification_chunk.id
        else:
            assert False
        row.pop("settings_id")
        row.pop("model")
        data["adaptations"].append(row)

    return data


def asdict(obj: orm.DeclarativeBase) -> dict[str, typing.Any]:
    assert isinstance(obj, orm.DeclarativeBase)
    insp = sql.inspect(obj)
    return {attr.columns[0].name: getattr(obj, attr.key) for attr in insp.mapper.column_attrs}
