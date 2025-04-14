from typing import Literal
import typing

from sqlalchemy import orm
import pydantic
import sqlalchemy as sql

from .. import adapted
from .. import llm
from ..any_json import JsonDict
from ..database_utils import OrmBase
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


class Strategy(OrmBase):
    __tablename__ = "adaptation_strategies"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)

    created_by: orm.Mapped[str]

    parent_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey("adaptation_strategies.id"))

    _model: orm.Mapped[JsonDict] = orm.mapped_column("model", sql.JSON)

    class _ModelContainer(pydantic.BaseModel):
        model: llm.ConcreteModel

    @property
    def model(self) -> llm.ConcreteModel:
        return self._ModelContainer(model=self._model).model  # type: ignore[arg-type]

    @model.setter
    def model(self, value: llm.ConcreteModel) -> None:
        self._model = value.model_dump()

    system_prompt: orm.Mapped[str]

    _response_specification: orm.Mapped[JsonDict] = orm.mapped_column("response_specification", sql.JSON)

    class _LlmResponseSpecificationContainer(pydantic.BaseModel):
        specification: ConcreteLlmResponseSpecification

    @property
    def response_specification(self) -> ConcreteLlmResponseSpecification:
        return self._LlmResponseSpecificationContainer(specification=self._response_specification).specification  # type: ignore[arg-type]

    @response_specification.setter
    def response_specification(self, value: ConcreteLlmResponseSpecification) -> None:
        self._response_specification = value.model_dump()
