import datetime

import sqlalchemy as sql

from . import database_utils
from .any_json import JsonDict


epoch = datetime.datetime.fromtimestamp(0, datetime.timezone.utc)


def migrate(session: database_utils.Session) -> None:
    pass


def dump(session: database_utils.Session) -> JsonDict:
    data = {
        table.name: [row._asdict() for row in session.execute(sql.select(table)).all()]
        for table in database_utils.OrmBase.metadata.sorted_tables
    }

    for rows in data.values():
        if len(rows) > 0:
            if "id" in rows[0]:
                rows.sort(key=lambda row: row["id"])
            elif "sha256" in rows[0]:
                rows.sort(key=lambda row: row["sha256"])
            else:
                assert False

    return data
