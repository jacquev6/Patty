import fastapi
import sqlalchemy as sql

from . import api_router
from . import authentication
from . import database_utils
from . import settings


app = fastapi.FastAPI(database_engine=database_utils.create_engine(settings.DATABASE_URL))


@app.get("/api/health")
@app.head("/api/health")
def get_health(session: database_utils.SessionDependable) -> dict[str, str]:
    alambic_version = session.execute(
        sql.select(sql.text("version_num")).select_from(sql.text("alembic_version"))
    ).scalar()
    assert alambic_version is not None
    return {"alambic_version": alambic_version, "status": "ok"}


app.include_router(api_router.router, prefix="/api")

app.include_router(authentication.router, prefix="/api")
