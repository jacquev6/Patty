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

import fastapi
import sqlalchemy as sql

from . import api_router
from . import authentication
from . import database_utils
from . import errors
from . import settings
from .file_storage import file_system_engine


openapi_router = fastapi.APIRouter()
openapi_router.include_router(errors.router, prefix="/api/errors-caught-by-frontend")
openapi_router.include_router(api_router.api_router, prefix="/api")
openapi_router.include_router(authentication.router, prefix="/api")

app = fastapi.FastAPI(database_engine=database_utils.create_engine(settings.DATABASE_URL))


@app.get("/api/health")
@app.head("/api/health")
def get_health(session: database_utils.SessionDependable) -> dict[str, str]:
    alambic_version = session.execute(
        sql.select(sql.text("version_num")).select_from(sql.text("alembic_version"))
    ).scalar()
    assert alambic_version is not None
    return {"alambic_version": alambic_version, "status": "ok"}


app.include_router(openapi_router)
app.include_router(api_router.export_router, prefix="/api/export")
app.include_router(file_system_engine.router)
