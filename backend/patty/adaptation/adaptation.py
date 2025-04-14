import typing

from sqlalchemy import orm
import sqlalchemy as sql

from ..adapted import Exercise
from ..database_utils import OrmBase
from .input import Input
from .strategy import Strategy
from ..any_json import JsonDict, JsonList
from ..api_utils import ApiModel


class Adjustment(ApiModel):
    user_prompt: str
    assistant_error: str | None
    assistant_response: Exercise | None


class Adaptation(OrmBase):
    __tablename__ = "adaptation_adaptations"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)

    created_by: orm.Mapped[str]

    strategy_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Strategy.id))
    strategy: orm.Mapped[Strategy] = orm.relationship(Strategy)
    input_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Input.id))
    input: orm.Mapped[Input] = orm.relationship(Input)

    # Kept only to help investigating future issues
    raw_llm_conversations: orm.Mapped[JsonList] = orm.mapped_column(sql.JSON)

    initial_assistant_error: orm.Mapped[str | None]
    _initial_assistant_response: orm.Mapped[JsonDict | None] = orm.mapped_column("initial_assistant_response", sql.JSON)

    @property
    def initial_assistant_response(self) -> Exercise | None:
        if self._initial_assistant_response is None:
            return None
        else:
            return Exercise(**self._initial_assistant_response)

    @initial_assistant_response.setter
    def initial_assistant_response(self, value: Exercise | None) -> None:
        if value is None:
            self._initial_assistant_response = None
        else:
            self._initial_assistant_response = value.model_dump()

    _adjustments: orm.Mapped[JsonList] = orm.mapped_column("adjustments", sql.JSON)

    @property
    def adjustments(self) -> list[Adjustment]:
        return [Adjustment(**adjustment) for adjustment in self._adjustments]

    @adjustments.setter
    def adjustments(self, value: list[Adjustment]) -> None:
        self._adjustments = [adjustment.model_dump() for adjustment in value]

    _manual_edit: orm.Mapped[JsonDict | None] = orm.mapped_column("manual_edit", sql.JSON)

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
