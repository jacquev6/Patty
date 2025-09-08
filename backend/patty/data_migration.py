import sqlalchemy as sql

from . import adaptation
from . import classification
from . import database_utils
from . import errors
from . import extraction
from . import sandbox
from . import textbooks


def migrate(session: database_utils.Session) -> None:
    add_github_issue_numbers(session)
    parse_all_json_fields(session)


def add_github_issue_numbers(session: database_utils.Session) -> None:
    known_errors: dict[tuple[str | None, int], int] = {
        ("Sarah", 23): 99,
        ("Sarah", 22): 99,
        ("Sarah", 21): 99,
        ("Vincent", 20): 77,
        ("Vincent", 19): 77,
        ("Vincent", 18): 77,
        ("Sarah", 17): 99,
        ("Sarah", 16): 99,
        ("Sarah", 15): 99,
        ("Sarah", 14): 99,
        ("Sarah", 13): 99,
        ("Elise", 12): 103,
        ("Elise", 11): 103,
        ("Elise", 10): 103,
        ("Elise", 9): 103,
        ("Elise", 8): 103,
        ("Elise", 7): 103,
        ("Elise", 6): 103,
        ("Elise", 5): 103,
        ("Elise", 4): 103,
        ("Sarah", 3): 99,
        ("Sarah", 2): 96,
        ("Vincent", 1): 77,
    }

    for error in session.execute(sql.select(errors.ErrorCaughtByFrontend)).scalars():
        error.github_issue_number = known_errors.get((error.created_by_username, error.id))


def parse_all_json_fields(session: database_utils.Session) -> None:
    for adaptation_settings in session.execute(sql.select(adaptation.AdaptationSettings)).scalars():
        adaptation_settings.response_specification
    for adaptation_ in session.execute(sql.select(adaptation.Adaptation)).scalars():
        adaptation_.adjustments
        adaptation_.initial_assistant_response
        adaptation_.manual_edit
        adaptation_.model
    for classification_chunk in session.execute(sql.select(classification.ClassificationChunk)).scalars():
        classification_chunk.model_for_adaptation
    for page_extraction in session.execute(sql.select(extraction.PageExtraction)).scalars():
        page_extraction.assistant_response
        page_extraction.model
        page_extraction.model_for_adaptation
    for sandbox_adaptation_batch in session.execute(sql.select(sandbox.adaptation.SandboxAdaptationBatch)).scalars():
        sandbox_adaptation_batch.model
    for sandbox_classification_batch in session.execute(
        sql.select(sandbox.classification.SandboxClassificationBatch)
    ).scalars():
        sandbox_classification_batch.model_for_adaptation
    for sandbox_extraction_batch in session.execute(sql.select(sandbox.extraction.SandboxExtractionBatch)).scalars():
        sandbox_extraction_batch.model
        sandbox_extraction_batch.model_for_adaptation
    for textbook_extraction_batch in session.execute(sql.select(textbooks.TextbookExtractionBatch)).scalars():
        textbook_extraction_batch.model_for_adaptation
        textbook_extraction_batch.model_for_extraction
