# MALIN Platform https://malin.cahiersfantastiques.fr/
# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

import datetime

from sqlalchemy import orm
import sqlalchemy as sql

from ..database_utils import OrmBase, annotate_new_tables


class ErrorCaughtByFrontend(OrmBase):
    __tablename__ = "errors_caught_by_frontend"

    def __init__(
        self,
        *,
        created_at: datetime.datetime,
        created_by_username: str | None,
        patty_version: str,
        user_agent: str,
        window_size: str,
        url: str,
        caught_by: str,
        message: str,
        code_location: str | None,
        github_issue_number: int | None,
    ) -> None:
        super().__init__()
        self.created_at = created_at
        self.created_by_username = created_by_username
        self.patty_version = patty_version
        self.user_agent = user_agent
        self.window_size = window_size
        self.url = url
        self.caught_by = caught_by
        self.message = message
        self.code_location = code_location
        self.github_issue_number = github_issue_number

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str | None]

    patty_version: orm.Mapped[str]
    user_agent: orm.Mapped[str]
    window_size: orm.Mapped[str]
    url: orm.Mapped[str]

    caught_by: orm.Mapped[str]
    message: orm.Mapped[str]
    code_location: orm.Mapped[str | None]

    github_issue_number: orm.Mapped[int | None]


annotate_new_tables("errors")
