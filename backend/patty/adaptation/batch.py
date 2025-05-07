import datetime

from sqlalchemy import orm
import sqlalchemy as sql

from . import adaptation
from ..database_utils import OrmBase
from .strategy import Strategy
from .textbook import Textbook


class Batch(OrmBase):
    __tablename__ = "adaptation_batches"

    __table_args__ = (
        # Redondant ('id' is unique by itself), but required for the foreign key in 'Adaptation'
        sql.UniqueConstraint("id", "strategy_id"),
    )

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_by: orm.Mapped[str]
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))

    strategy_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Strategy.id))
    strategy: orm.Mapped[Strategy] = orm.relationship(Strategy, foreign_keys=[strategy_id], remote_side=[Strategy.id])

    textbook_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(Textbook.id))
    textbook: orm.Mapped[Textbook | None] = orm.relationship(
        Textbook, foreign_keys=[textbook_id], remote_side=[Textbook.id], back_populates="batches"
    )
    removed_from_textbook: orm.Mapped[bool] = orm.mapped_column(default=False, server_default="false")

    adaptations: orm.Mapped[list["adaptation.Adaptation"]] = orm.relationship(
        foreign_keys="Adaptation.batch_id", back_populates="batch", order_by="Adaptation.id"
    )
