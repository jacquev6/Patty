from sqlalchemy import orm
import sqlalchemy as sql

from ..database_utils import OrmBase
from .strategy import Strategy


class Batch(OrmBase):
    __tablename__ = "adaptation_batches"

    __table_args__ = (
        # Redondant ('id' is unique by itself), but required for the foreign key in 'Adaptation'
        sql.UniqueConstraint("id", "strategy_id"),
    )

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)

    created_by: orm.Mapped[str]

    strategy_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Strategy.id))
    strategy: orm.Mapped[Strategy] = orm.relationship(Strategy)
