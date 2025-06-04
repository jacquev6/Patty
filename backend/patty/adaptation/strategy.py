from __future__ import annotations
from typing import Literal


from .. import adapted
from .. import llm
from ..any_json import JsonDict
from ..api_utils import ApiModel


class JsonLlmResponseSpecification(ApiModel):
    format: Literal["json"]


class JsonFromTextLlmResponseSpecification(JsonLlmResponseSpecification):
    formalism: Literal["text"]

    def make_response_format(self) -> llm.JsonFromTextResponseFormat[adapted.Exercise]:
        return llm.JsonFromTextResponseFormat(response_type=adapted.Exercise)


class JsonObjectLlmResponseSpecification(JsonLlmResponseSpecification):
    formalism: Literal["json-object"]

    def make_response_format(self) -> llm.JsonObjectResponseFormat[adapted.Exercise]:
        return llm.JsonObjectResponseFormat(response_type=adapted.Exercise)


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
        return adapted.make_exercise_type(
            self.instruction_components,
            self.example_components,
            self.hint_components,
            self.statement_components,
            self.reference_components,
        )

    def make_response_schema(self) -> JsonDict:
        return llm.make_schema(self.make_response_type())


ConcreteLlmResponseSpecification = (
    JsonFromTextLlmResponseSpecification | JsonObjectLlmResponseSpecification | JsonSchemaLlmResponseSpecification
)
