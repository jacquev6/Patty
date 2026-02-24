# MALIN Platform https://malin.cahiersfantastiques.fr/
# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sqlalchemy as sql

from . import adaptation
from . import api_router
from . import classification
from . import database_utils
from . import extraction
from . import sandbox
from . import textbooks


def migrate(session: database_utils.Session) -> None:
    pass


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
