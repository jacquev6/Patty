import sqlalchemy as sql

from . import database_utils
from . import orm_models as db
from .any_json import JsonDict


def migrate(session: database_utils.Session) -> None:
    for exercise in session.execute(sql.select(db.BaseExercise)).scalars().all():
        if exercise.created is None:
            assert exercise.created_at__to_be_deleted is not None
            if exercise.created_by_username__to_be_deleted is None:
                assert isinstance(exercise, db.AdaptableExercise)
                assert exercise.created_by_page_extraction_id__to_be_deleted is not None
                page_extraction = session.get(db.PageExtraction, exercise.created_by_page_extraction_id__to_be_deleted)
                assert page_extraction is not None
                exercise.created = db.ExerciseCreationByPageExtraction(
                    at=exercise.created_at__to_be_deleted, page_extraction=page_extraction
                )
            else:
                exercise.created = db.ExerciseCreationByUser(
                    at=exercise.created_at__to_be_deleted, username=exercise.created_by_username__to_be_deleted
                )
                if isinstance(exercise, db.AdaptableExercise):
                    assert exercise.created_by_page_extraction_id__to_be_deleted is None
        assert exercise.created is not None
        exercise.created_at__to_be_deleted = None
        exercise.created_by_username__to_be_deleted = None
        if isinstance(exercise, db.AdaptableExercise):
            exercise.created_by_page_extraction_id__to_be_deleted = None

        if exercise.location is None:
            if exercise.textbook_id__to_be_deleted is None:
                exercise.location = db.ExerciseLocationMaybePageAndNumber(
                    page_number=exercise.page_number__to_be_deleted,
                    exercise_number=exercise.exercise_number__to_be_deleted,
                )
            else:
                assert exercise.page_number__to_be_deleted is not None
                assert exercise.exercise_number__to_be_deleted is not None
                textbook = session.get(db.Textbook, exercise.textbook_id__to_be_deleted)
                assert textbook is not None
                exercise.location = db.ExerciseLocationTextbook(
                    textbook=textbook,
                    page_number=exercise.page_number__to_be_deleted,
                    exercise_number=exercise.exercise_number__to_be_deleted,
                )
        assert exercise.location is not None
        exercise.textbook_id__to_be_deleted = None
        exercise.page_number__to_be_deleted = None
        exercise.exercise_number__to_be_deleted = None

    for page_extraction in session.execute(sql.select(db.PageExtraction)).scalars().all():
        if page_extraction.created is None:
            assert page_extraction.created_at__to_be_deleted is not None
            assert page_extraction.extraction_batch_id__to_be_deleted is not None
            assert page_extraction.created_by_username__to_be_deleted is not None
            extraction_batch = session.get(
                db.SandboxExtractionBatch, page_extraction.extraction_batch_id__to_be_deleted
            )
            assert extraction_batch is not None
            assert page_extraction.created_by_username__to_be_deleted == extraction_batch.created_by_username
            page_extraction.created = db.PageExtractionCreationBySandboxExtractionBatch(
                at=page_extraction.created_at__to_be_deleted, extraction_batch=extraction_batch
            )
        page_extraction.created_at__to_be_deleted = None
        page_extraction.extraction_batch_id__to_be_deleted = None
        page_extraction.created_by_username__to_be_deleted = None

    for exercise_class in session.execute(sql.select(db.ExerciseClass)).scalars().all():
        if exercise_class.created is None:
            assert exercise_class.created_at__to_be_deleted is not None
            if exercise_class.created_by_username__to_be_deleted is not None:
                assert exercise_class.created_by_classification_batch_id__to_be_deleted is None
                exercise_class.created = db.ExerciseClassCreationByUser(
                    at=exercise_class.created_at__to_be_deleted,
                    username=exercise_class.created_by_username__to_be_deleted,
                )
            else:
                assert exercise_class.created_by_classification_batch_id__to_be_deleted is not None
                classification_batch = session.get(
                    db.SandboxClassificationBatch, exercise_class.created_by_classification_batch_id__to_be_deleted
                )
                assert classification_batch is not None
                exercise_class.created = db.ExerciseClassCreationBySandboxClassificationBatch(
                    at=exercise_class.created_at__to_be_deleted, sandbox_classification_batch=classification_batch
                )
        assert exercise_class.created is not None
        exercise_class.created_at__to_be_deleted = None
        exercise_class.created_by_username__to_be_deleted = None
        exercise_class.created_by_classification_batch_id__to_be_deleted = None

    for exercise_adaptation in session.execute(sql.select(db.Adaptation)).scalars().all():
        if exercise_adaptation.created is None:
            assert exercise_adaptation.created_at__to_be_deleted is not None
            if exercise_adaptation.adaptation_batch_id__to_be_deleted is not None:
                assert exercise_adaptation.classification_batch_id__to_be_deleted is None
                adaptation_batch = session.get(
                    db.SandboxAdaptationBatch, exercise_adaptation.adaptation_batch_id__to_be_deleted
                )
                assert adaptation_batch is not None
                exercise_adaptation.created = db.ExerciseAdaptationCreationBySandboxAdaptationBatch(
                    at=exercise_adaptation.created_at__to_be_deleted, sandbox_adaptation_batch=adaptation_batch
                )
            elif exercise_adaptation.classification_batch_id__to_be_deleted is not None:
                classification_batch = session.get(
                    db.SandboxClassificationBatch, exercise_adaptation.classification_batch_id__to_be_deleted
                )
                assert classification_batch is not None
                exercise_adaptation.created = db.ExerciseAdaptationCreationBySandboxClassificationBatch(
                    at=exercise_adaptation.created_at__to_be_deleted, sandbox_classification_batch=classification_batch
                )
            else:
                assert exercise_adaptation.created_by_username__to_be_deleted is not None
                exercise_adaptation.created = db.ExerciseAdaptationCreationByUser(
                    at=exercise_adaptation.created_at__to_be_deleted,
                    username=exercise_adaptation.created_by_username__to_be_deleted,
                )
        assert exercise_adaptation.created is not None
        exercise_adaptation.created_at__to_be_deleted = None
        exercise_adaptation.created_by_username__to_be_deleted = None
        exercise_adaptation.adaptation_batch_id__to_be_deleted = None
        exercise_adaptation.classification_batch_id__to_be_deleted = None


def dump(session: database_utils.Session) -> JsonDict:
    data = {
        table.name: [row._asdict() for row in session.execute(sql.select(table)).all()]
        for table in database_utils.OrmBase.metadata.sorted_tables
    }

    for rows in data.values():
        if len(rows) > 0:
            if "id" in rows[0]:
                rows.sort(key=lambda row: row["id"])
            elif "sha256" in rows[0]:
                rows.sort(key=lambda row: row["sha256"])
            else:
                assert False

    exercise_data_by_id = {exercise["id"]: exercise for exercise in data["exercises"]}
    adaptable_exercise_data_by_id = {exercise["id"]: exercise for exercise in data["adaptable_exercises"]}
    for exercise in session.execute(sql.select(db.BaseExercise)).scalars().all():
        assert exercise.created is not None
        exercise_data_by_id[exercise.id]["created_at"] = exercise.created.at
        if isinstance(exercise.created, db.ExerciseCreationByUser):
            exercise_data_by_id[exercise.id]["created_by_username"] = exercise.created.username
        elif isinstance(exercise.created, db.ExerciseCreationByPageExtraction):
            adaptable_exercise_data_by_id[exercise.id][
                "created_by_page_extraction_id"
            ] = exercise.created.page_extraction.id
        else:
            assert False

        assert exercise.location is not None
        if isinstance(exercise.location, db.ExerciseLocationMaybePageAndNumber):
            exercise_data_by_id[exercise.id]["page_number"] = exercise.location.page_number
            exercise_data_by_id[exercise.id]["exercise_number"] = exercise.location.exercise_number
            exercise_data_by_id[exercise.id]["textbook_id"] = None
        elif isinstance(exercise.location, db.ExerciseLocationTextbook):
            exercise_data_by_id[exercise.id]["page_number"] = exercise.location.page_number
            exercise_data_by_id[exercise.id]["exercise_number"] = exercise.location.exercise_number
            exercise_data_by_id[exercise.id]["textbook_id"] = exercise.location.textbook_id
        else:
            assert False

    page_extraction_data_by_id = {
        page_extraction["id"]: page_extraction for page_extraction in data["page_extractions"]
    }
    for page_extraction in session.execute(sql.select(db.PageExtraction)).scalars().all():
        assert page_extraction.created is not None
        page_extraction_data_by_id[page_extraction.id]["created_at"] = page_extraction.created.at
        if isinstance(page_extraction.created, db.PageExtractionCreationBySandboxExtractionBatch):
            page_extraction_data_by_id[page_extraction.id][
                "extraction_batch_id"
            ] = page_extraction.created.extraction_batch.id
            page_extraction_data_by_id[page_extraction.id][
                "created_by_username"
            ] = page_extraction.created.extraction_batch.created_by_username
        else:
            assert False

    return data
