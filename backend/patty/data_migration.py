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
                    at=exercise.created_at__to_be_deleted, by=page_extraction
                )
            else:
                exercise.created = db.ExerciseCreationByUser(
                    at=exercise.created_at__to_be_deleted, by=exercise.created_by_username__to_be_deleted
                )
                if isinstance(exercise, db.AdaptableExercise):
                    assert exercise.created_by_page_extraction_id__to_be_deleted is None
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
        exercise.textbook_id__to_be_deleted = None
        exercise.page_number__to_be_deleted = None
        exercise.exercise_number__to_be_deleted = None


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
            exercise_data_by_id[exercise.id]["created_by_username"] = exercise.created.by
        elif isinstance(exercise.created, db.ExerciseCreationByPageExtraction):
            adaptable_exercise_data_by_id[exercise.id]["created_by_page_extraction_id"] = exercise.created.by.id
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

    return data
