from . import database_utils
from . import orm_models


def migrate(session: database_utils.Session) -> None:
    check_parsed_fields(session)


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
