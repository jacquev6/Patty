from sqlalchemy import orm

from ..database_utils import OrmBase


class Input(OrmBase):
    __tablename__ = "adaptation_input"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)

    text: orm.Mapped[str]
