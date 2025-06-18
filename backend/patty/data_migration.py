import sqlalchemy as sql

from . import database_utils
from . import orm_models


def migrate(session: database_utils.Session) -> None:
    fix_issue_59(session)
    check_parsed_fields(session)


def fix_issue_59(session: database_utils.Session) -> None:
    for bad_exercise_class in (
        session.execute(
            sql.select(orm_models.ExerciseClass).where(orm_models.ExerciseClass.name.endswith(" (older version)"))
        )
        .scalars()
        .all()
    ):
        print(f"Fixing ExerciseClass {bad_exercise_class.name}...")
        good_exercise_class = session.execute(
            sql.select(orm_models.ExerciseClass).where(orm_models.ExerciseClass.name == bad_exercise_class.name[:-16])
        ).scalar_one()

        for exercise in (
            session.execute(
                sql.select(orm_models.AdaptableExercise).where(
                    orm_models.AdaptableExercise.exercise_class_id == bad_exercise_class.id
                )
            )
            .scalars()
            .all()
        ):
            exercise.exercise_class = good_exercise_class

        for settings in (
            session.execute(
                sql.select(orm_models.AdaptationStrategySettings).where(
                    orm_models.AdaptationStrategySettings.exercise_class_id == bad_exercise_class.id
                )
            )
            .scalars()
            .all()
        ):
            settings.exercise_class = good_exercise_class

        session.flush()

        session.delete(bad_exercise_class)


def check_parsed_fields(session: database_utils.Session) -> None:
    for adaptation in session.query(orm_models.Adaptation).all():
        adaptation.created_at
        adaptation.raw_llm_conversations
        adaptation.initial_assistant_response
        adaptation.adjustments
        adaptation.manual_edit
    for adapted_exercise in session.query(orm_models.AdaptableExercise).all():
        adapted_exercise.created_at
        adapted_exercise.classified_at
    for external_exercise in session.query(orm_models.ExternalExercise).all():
        external_exercise.created_at
    for exercise_class in session.query(orm_models.ExerciseClass).all():
        exercise_class.created_at
    for strategy_settings in session.query(orm_models.AdaptationStrategySettings).all():
        strategy_settings.created_at
        strategy_settings.response_specification
    for adaptation_batch in session.query(orm_models.AdaptationBatch).all():
        adaptation_batch.created_at
    for strategy in session.query(orm_models.AdaptationStrategy).all():
        strategy.created_at
    for textbook in session.query(orm_models.Textbook).all():
        textbook.created_at
