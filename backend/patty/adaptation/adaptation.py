import typing

from sqlalchemy import orm
import pydantic
import sqlalchemy as sql

from ..adapted import ProseAndExercise, Exercise
from ..database_utils import OrmBase
from .input import Input
from .strategy import Strategy


class Adjustment(pydantic.BaseModel):
    user_prompt: str
    assistant_response: ProseAndExercise


class Adaptation(OrmBase):
    __tablename__ = "adaptation_adaptations"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)

    strategy_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Strategy.id))
    strategy: orm.Mapped[Strategy] = orm.relationship(Strategy)
    input_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Input.id))
    input: orm.Mapped[Input] = orm.relationship(Input)

    _initial_response: orm.Mapped[dict[str, typing.Any] | None] = orm.mapped_column("initial_response", sql.JSON)

    @property
    def initial_response(self) -> ProseAndExercise | None:
        if self._initial_response is None:
            return None
        else:
            return ProseAndExercise(**self._initial_response)

    @initial_response.setter
    def initial_response(self, value: ProseAndExercise | None) -> None:
        if value is None:
            self._initial_response = None
        else:
            self._initial_response = value.model_dump()

    _adjustments: orm.Mapped[list[dict[str, typing.Any]]] = orm.mapped_column(
        "adjustments", sql.JSON, default=[], server_default="[]"
    )

    @property
    def adjustments(self) -> list[Adjustment]:
        return [Adjustment(**adjustment) for adjustment in self._adjustments]

    @adjustments.setter
    def adjustments(self, value: list[Adjustment]) -> None:
        self._adjustments = [adjustment.model_dump() for adjustment in value]

    _manual_edit: orm.Mapped[dict[str, typing.Any] | None] = orm.mapped_column("manual_edit", sql.JSON)

    @property
    def manual_edit(self) -> Exercise | None:
        if self._manual_edit is None:
            return None
        else:
            return Exercise(**self._manual_edit)

    @manual_edit.setter
    def manual_edit(self, value: Exercise | None) -> None:
        if value is None:
            self._manual_edit = None
        else:
            self._manual_edit = value.model_dump()
