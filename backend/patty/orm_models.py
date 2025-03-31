import pydantic
from sqlalchemy import orm
import sqlalchemy as sql

from .database_utils import OrmBase
from .llm import ConcreteModel


class AdaptationStrategy(OrmBase):
    __tablename__ = "adaptation_strategies"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)

    _model = orm.mapped_column(sql.JSON, name="model", nullable=False)

    class _ModelContainer(pydantic.BaseModel):
        model: ConcreteModel

    @property
    def model(self) -> ConcreteModel:
        return self._ModelContainer(model=self._model).model

    @model.setter
    def model(self, value: ConcreteModel) -> None:
        self._model = value.model_dump()

    system_prompt: orm.Mapped[str]
