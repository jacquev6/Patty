from typing import Any
import typing

from sqlalchemy import orm
import pydantic
import sqlalchemy as sql

from ..database_utils import OrmBase
from ..llm import ConcreteModel
from .. import adapted
from .. import llm


class Strategy(OrmBase):
    __tablename__ = "adaptation_strategies"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)

    parent_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey("adaptation_strategies.id"))

    _model: orm.Mapped[dict[str, typing.Any]] = orm.mapped_column("model", sql.JSON)

    class _ModelContainer(pydantic.BaseModel):
        model: ConcreteModel

    @property
    def model(self) -> ConcreteModel:
        return self._ModelContainer(model=self._model).model  # type: ignore[arg-type]

    @model.setter
    def model(self, value: ConcreteModel) -> None:
        self._model = value.model_dump()

    system_prompt: orm.Mapped[str]

    allow_choice_in_instruction: orm.Mapped[bool]
    allow_arrow_in_statement: orm.Mapped[bool]
    allow_free_text_input_in_statement: orm.Mapped[bool]
    allow_multiple_choices_input_in_statement: orm.Mapped[bool]
    allow_selectable_input_in_statement: orm.Mapped[bool]

    def make_llm_response_type(self) -> type[adapted.Exercise]:
        return adapted.make_exercise_type(
            adapted.InstructionComponents(text=True, whitespace=True, choice=self.allow_choice_in_instruction),
            adapted.StatementComponents(
                text=True,
                whitespace=True,
                arrow=self.allow_arrow_in_statement,
                free_text_input=self.allow_free_text_input_in_statement,
                multiple_choices_input=self.allow_multiple_choices_input_in_statement,
                selectable_input=self.allow_selectable_input_in_statement,
            ),
            adapted.ReferenceComponents(text=True, whitespace=True),
        )

    def make_llm_response_schema(self) -> dict[str, Any]:
        return llm.make_schema(self.make_llm_response_type())
