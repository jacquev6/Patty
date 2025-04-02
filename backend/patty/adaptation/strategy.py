import typing

from sqlalchemy import orm
import pydantic
import sqlalchemy as sql

from ..database_utils import OrmBase
from ..llm import ConcreteModel


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
