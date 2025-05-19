import os

import fastapi
import sqlalchemy as sql

from . import adaptation
from . import authentication
from . import database_utils
from . import llm
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


@app.get("/api/available-llm-models")
def get_available_llm_models() -> list[llm.ConcreteModel]:
    if os.environ.get("PATTY_ENVIRONMENT") == "dev":
        return [
            llm.DummyModel(name="dummy-1"),
            llm.DummyModel(name="dummy-2"),
            llm.MistralAiModel(name="mistral-large-2411"),
            llm.MistralAiModel(name="mistral-small-2501"),
            llm.OpenAiModel(name="gpt-4o-2024-08-06"),
            llm.OpenAiModel(name="gpt-4o-mini-2024-07-18"),
        ]
    else:
        return [
            llm.MistralAiModel(name="mistral-large-2411"),
            llm.MistralAiModel(name="mistral-small-2501"),
            llm.OpenAiModel(name="gpt-4o-2024-08-06"),
            llm.OpenAiModel(name="gpt-4o-mini-2024-07-18"),
            llm.DummyModel(name="dummy-1"),
            llm.DummyModel(name="dummy-2"),
        ]


app.include_router(adaptation.router, prefix="/api/adaptation")

app.include_router(authentication.router, prefix="/api")
