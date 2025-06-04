import datetime

from sqlalchemy import orm
import sqlalchemy as sql

from . import adaptation
from ..database_utils import OrmBase
from .strategy import OldStrategy
from .textbook import OldTextbook


class OldBatch(OrmBase):
    __tablename__ = "old_adaptation_batches"

    __table_args__ = (
        # Redondant ('id' is unique by itself), but required for the foreign key in 'Adaptation'
        sql.UniqueConstraint("id", "strategy_id"),
    )

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_by: orm.Mapped[str]
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))

    strategy_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(OldStrategy.id))
    strategy: orm.Mapped[OldStrategy] = orm.relationship(
        OldStrategy, foreign_keys=[strategy_id], remote_side=[OldStrategy.id]
    )

    textbook_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(OldTextbook.id))
    textbook: orm.Mapped[OldTextbook | None] = orm.relationship(
        OldTextbook, foreign_keys=[textbook_id], remote_side=[OldTextbook.id], back_populates="batches"
    )
    removed_from_textbook: orm.Mapped[bool] = orm.mapped_column(default=False, server_default="false")

    adaptations: orm.Mapped[list["adaptation.OldAdaptation"]] = orm.relationship(
        foreign_keys="OldAdaptation.batch_id", back_populates="batch", order_by="OldAdaptation.id"
    )
