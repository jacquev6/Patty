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

from . import assistant_responses as assistant_responses
from . import extracted as extracted
from . import llm as llm
from . import submission as submission
from .orm_models import (
    ClassificationChunkCreationByPageExtraction as ClassificationChunkCreationByPageExtraction,
    ExerciseCreationByPageExtraction as ExerciseCreationByPageExtraction,
    ExerciseImageCreationByPageExtraction as ExerciseImageCreationByPageExtraction,
    ExtractionSettings as ExtractionSettings,
    PageExtraction as PageExtraction,
    PageExtractionCreation as PageExtractionCreation,
    PdfFile as PdfFile,
    PdfFileRange as PdfFileRange,
    OutputSchemaVersion as OutputSchemaVersion,
    OutputSchemaDescription as OutputSchemaDescription,
    OutputSchemaDescriptionV2 as OutputSchemaDescriptionV2,
    OutputSchemaDescriptionV3 as OutputSchemaDescriptionV3,
)
