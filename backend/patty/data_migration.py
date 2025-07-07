import sqlalchemy as sql

from . import database_utils
from . import orm_models


def migrate(session: database_utils.Session) -> None:
    read_all_fields(session)


def read_all_fields(session: database_utils.Session) -> None:
    for adaptation in session.execute(sql.select(orm_models.Adaptation)).scalars().all():
        adaptation.id
        adaptation.created_at
        adaptation.created_by_username
        adaptation.exercise_id
        adaptation.exercise
        adaptation.strategy_id
        adaptation.strategy
        adaptation.classification_batch_id
        adaptation.classification_batch
        adaptation.adaptation_batch_id
        adaptation.adaptation_batch
        adaptation.raw_llm_conversations
        adaptation._initial_assistant_response
        adaptation.initial_assistant_response
        adaptation._adjustments
        adaptation.adjustments
        adaptation._manual_edit
        adaptation.manual_edit

    for adaptation_batch in session.execute(sql.select(orm_models.AdaptationBatch)).scalars().all():
        adaptation_batch.id
        adaptation_batch.created_at
        adaptation_batch.created_by_username
        adaptation_batch.strategy_id
        adaptation_batch.strategy
        adaptation_batch.textbook_id
        adaptation_batch.textbook
        adaptation_batch.removed_from_textbook
        adaptation_batch.adaptations

    for adaptation_strategy in session.execute(sql.select(orm_models.AdaptationStrategy)).scalars().all():
        adaptation_strategy.id
        adaptation_strategy.created_at
        adaptation_strategy.created_by_username
        adaptation_strategy.created_by_classification_batch_id
        adaptation_strategy.created_by_classification_batch
        adaptation_strategy.settings_id
        adaptation_strategy.settings
        adaptation_strategy._model
        adaptation_strategy.model

    for adaptation_strategy_settings in (
        session.execute(sql.select(orm_models.AdaptationStrategySettings)).scalars().all()
    ):
        adaptation_strategy_settings.id
        adaptation_strategy_settings.created_at
        adaptation_strategy_settings.created_by_username
        adaptation_strategy_settings.exercise_class_id
        adaptation_strategy_settings.exercise_class
        adaptation_strategy_settings.parent_id
        adaptation_strategy_settings.parent
        adaptation_strategy_settings.system_prompt
        adaptation_strategy_settings._response_specification
        adaptation_strategy_settings.response_specification

    for base_exercise in session.execute(sql.select(orm_models.BaseExercise)).scalars().all():
        base_exercise.id
        base_exercise.kind
        base_exercise.created_at
        base_exercise.created_by_username
        base_exercise.textbook_id
        base_exercise.textbook
        base_exercise.removed_from_textbook
        base_exercise.page_number
        base_exercise.exercise_number

    for classification_batch in session.execute(sql.select(orm_models.ClassificationBatch)).scalars().all():
        classification_batch.id
        classification_batch.created_at
        classification_batch.created_by_username
        classification_batch.created_by_page_extraction_id
        classification_batch.created_by_page_extraction
        classification_batch.exercises
        classification_batch._model_for_adaptation
        classification_batch.model_for_adaptation
        classification_batch.adaptations

    for error_caught_by_frontend in session.execute(sql.select(orm_models.ErrorCaughtByFrontend)).scalars().all():
        error_caught_by_frontend.id
        error_caught_by_frontend.created_at
        error_caught_by_frontend.created_by_username
        error_caught_by_frontend.patty_version
        error_caught_by_frontend.user_agent
        error_caught_by_frontend.window_size
        error_caught_by_frontend.url
        error_caught_by_frontend.caught_by
        error_caught_by_frontend.message
        error_caught_by_frontend.code_location

    for exercise_class in session.execute(sql.select(orm_models.ExerciseClass)).scalars().all():
        exercise_class.id
        exercise_class.created_at
        exercise_class.created_by_username
        exercise_class.created_by_classification_batch_id
        exercise_class.created_by_classification_batch
        exercise_class.name
        exercise_class.latest_strategy_settings_id
        exercise_class.latest_strategy_settings

    for extraction_batch in session.execute(sql.select(orm_models.ExtractionBatch)).scalars().all():
        extraction_batch.id
        extraction_batch.created_at
        extraction_batch.created_by_username
        extraction_batch.strategy_id
        extraction_batch.strategy
        extraction_batch.range_id
        extraction_batch.range
        extraction_batch.page_extractions
        extraction_batch.run_classification
        extraction_batch._model_for_adaptation
        extraction_batch.model_for_adaptation

    for extraction_strategy in session.execute(sql.select(orm_models.ExtractionStrategy)).scalars().all():
        extraction_strategy.id
        extraction_strategy.created_at
        extraction_strategy.created_by_username
        extraction_strategy._model
        extraction_strategy.prompt

    for page_extraction in session.execute(sql.select(orm_models.PageExtraction)).scalars().all():
        page_extraction.id
        page_extraction.created_at
        page_extraction.created_by_username
        page_extraction.extraction_batch_id
        page_extraction.extraction_batch
        page_extraction.page_number
        page_extraction._assistant_response
        page_extraction.assistant_response
        page_extraction.exercises

    for pdf_file in session.execute(sql.select(orm_models.PdfFile)).scalars().all():
        pdf_file.sha256
        pdf_file.created_at
        pdf_file.created_by_username
        pdf_file.bytes_count
        pdf_file.pages_count
        pdf_file.known_file_names

    for pdf_file_range in session.execute(sql.select(orm_models.PdfFileRange)).scalars().all():
        pdf_file_range.id
        pdf_file_range.created_at
        pdf_file_range.created_by_username
        pdf_file_range.pdf_file_sha256
        pdf_file_range.pdf_file
        pdf_file_range.pdf_file_first_page_number
        pdf_file_range.pages_count

    for textbook in session.execute(sql.select(orm_models.Textbook)).scalars().all():
        textbook.id
        textbook.created_at
        textbook.created_by_username
        textbook.title
        textbook.editor
        textbook.year
        textbook.isbn
        textbook.exercises
        textbook.adaptation_batches
