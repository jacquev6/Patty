import fastapi
import sqlalchemy as sql

from . import api_router
from . import authentication
from . import database_utils
from . import settings


openapi_router = fastapi.APIRouter()
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
