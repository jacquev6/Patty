import datetime

import sqlalchemy as sql

from . import database_utils
from . import orm_models as db
from .any_json import JsonDict


epoch = datetime.datetime.fromtimestamp(0, datetime.timezone.utc)


def migrate(session: database_utils.Session) -> None:
    for exercise in session.execute(sql.select(db.BaseExercise)).scalars().all():
        if exercise.created is None:
            if exercise.created_by_username__to_be_deleted is None:
                assert isinstance(exercise, db.AdaptableExercise)
                assert exercise.created_by_page_extraction__to_be_deleted is not None
                exercise.created = db.ExerciseCreationByPageExtraction(
                    at=exercise.created_at__to_be_deleted, by=exercise.created_by_page_extraction__to_be_deleted
                )
            else:
                exercise.created = db.ExerciseCreationByUser(
                    at=exercise.created_at__to_be_deleted, by=exercise.created_by_username__to_be_deleted
                )
                if isinstance(exercise, db.AdaptableExercise):
                    assert exercise.created_by_page_extraction__to_be_deleted is None
        exercise.created_at__to_be_deleted = epoch
        exercise.created_by_username__to_be_deleted = None
        if isinstance(exercise, db.AdaptableExercise):
            exercise.created_by_page_extraction__to_be_deleted = None


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

    return data
