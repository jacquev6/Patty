# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

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
