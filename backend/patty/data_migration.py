import copy
import sqlalchemy as sql

from . import adaptation
from . import api_router
from . import classification
from . import database_utils
from . import extraction
from . import fixtures
from . import sandbox
from . import textbooks


def migrate(session: database_utils.Session) -> None:
    fix_type_of_legacy_extraction_assistant_responses(session)
    add_image_to_response_specifications(session)
    fixtures.FixturesCreator(session).create_extraction_seed_data()


def fix_type_of_legacy_extraction_assistant_responses(session: database_utils.Session) -> None:
    for page_extraction in session.execute(sql.select(extraction.PageExtraction)).scalars():
        if (
            page_extraction._assistant_response is not None
            and page_extraction._assistant_response.get("kind") == "success"
        ):
            response = copy.deepcopy(page_extraction._assistant_response)
            response["kind"] = "success-without-images"
            page_extraction._assistant_response = response


def add_image_to_response_specifications(session: database_utils.Session) -> None:
    for adaptation_settings in session.execute(sql.select(adaptation.AdaptationSettings)).scalars():
        assert adaptation_settings._response_specification["format"] == "json"
        if adaptation_settings._response_specification["formalism"] == "json-schema":
            spec = copy.deepcopy(adaptation_settings._response_specification)
            spec["instruction_components"]["image"] = True
            spec["example_components"]["image"] = True
            spec["hint_components"]["image"] = True
            spec["statement_components"]["image"] = True
            spec["reference_components"]["image"] = True
            adaptation_settings._response_specification = spec


def validate(session: database_utils.Session) -> None:
    parse_all_json_fields(session)
    make_all_api_objects(session)


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


def make_all_api_objects(session: database_utils.Session) -> None:
    for adaptation_ in session.execute(sql.select(adaptation.Adaptation)).scalars():
        api_router.adaptations.make_api_adaptation(adaptation_)
