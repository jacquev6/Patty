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

from __future__ import annotations
from typing import Any, Literal

import pydantic

from . import adapted
from . import llm
from ..api_utils import ApiModel


class JsonLlmResponseSpecification(ApiModel):
    format: Literal["json"]


class JsonFromTextLlmResponseSpecification(JsonLlmResponseSpecification):
    formalism: Literal["text"]

    def make_response_format(self) -> llm.JsonFromTextResponseFormat[adapted.Exercise]:
        return llm.JsonFromTextResponseFormat(response_type=self.make_response_type())

    def make_response_type(self) -> type[adapted.Exercise]:
        return adapted.Exercise


class JsonObjectLlmResponseSpecification(JsonLlmResponseSpecification):
    formalism: Literal["json-object"]

    def make_response_format(self) -> llm.JsonObjectResponseFormat[adapted.Exercise]:
        return llm.JsonObjectResponseFormat(response_type=self.make_response_type())

    def make_response_type(self) -> type[adapted.Exercise]:
        return adapted.Exercise


class JsonSchemaLlmResponseSpecification(JsonLlmResponseSpecification):
    formalism: Literal["json-schema"]
    instruction_components: adapted.InstructionComponents
    example_components: adapted.ExampleComponents
    hint_components: adapted.HintComponents
    statement_components: adapted.StatementComponents
    reference_components: adapted.ReferenceComponents

    def make_response_format(self) -> llm.JsonSchemaResponseFormat[adapted.Exercise]:
        return llm.JsonSchemaResponseFormat(response_type=self.make_response_type())

    def make_response_type(self) -> type[adapted.Exercise]:
        return adapted.make_partial_exercise_type(
            adapted.Components(
                instruction=self.instruction_components,
                example=self.example_components,
                hint=self.hint_components,
                statement=self.statement_components,
                reference=self.reference_components,
            )
        )


ConcreteLlmResponseSpecification = (
    JsonFromTextLlmResponseSpecification | JsonObjectLlmResponseSpecification | JsonSchemaLlmResponseSpecification
)


def validate(obj: Any) -> ConcreteLlmResponseSpecification:
    return pydantic.RootModel[ConcreteLlmResponseSpecification].model_validate(obj).root
