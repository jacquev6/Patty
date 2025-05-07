import datetime

from sqlalchemy import orm
import sqlalchemy as sql

from . import batch
from ..database_utils import OrmBase


class Textbook(OrmBase):
    __tablename__ = "adaptation_textbooks"

    __table_args__ = (sql.CheckConstraint("title != ''", name="title_not_empty"),)

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_by: orm.Mapped[str]
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))

    title: orm.Mapped[str]

    batches: orm.Mapped[list["batch.Batch"]] = orm.relationship(
        foreign_keys="Batch.textbook_id", back_populates="textbook", order_by="Batch.id"
    )
