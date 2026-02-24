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

from alembic import context

from patty import database_utils
from patty import errors  # noqa: F401 to populate the metadata
from patty import external_exercises  # noqa: F401
from patty import sandbox  # noqa: F401
from patty import settings
from patty import textbooks  # noqa: F401


assert not context.is_offline_mode()

engine = database_utils.create_engine(settings.DATABASE_URL)

with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=database_utils.OrmBase.metadata)

    with context.begin_transaction():
        context.run_migrations()
