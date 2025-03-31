import os

import fastapi

from . import adaptation
from . import llm


app = fastapi.FastAPI()


@app.get("/api/available-llm-models")
def get_available_llm_models() -> list[llm.ConcreteModel]:
    if os.environ.get("PATTY_ENVIRONMENT") == "dev":
        return [
            llm.DummyModel(name="dummy-1"),
            llm.DummyModel(name="dummy-2"),
            llm.OpenAiModel(name="gpt-4o-2024-08-06"),
            llm.OpenAiModel(name="gpt-4o-mini-2024-07-18"),
            llm.MistralAiModel(name="mistral-large-2411"),
            llm.MistralAiModel(name="mistral-small-2501"),
        ]
    else:
        return [
            llm.OpenAiModel(name="gpt-4o-2024-08-06"),
            llm.OpenAiModel(name="gpt-4o-mini-2024-07-18"),
            llm.MistralAiModel(name="mistral-large-2411"),
            llm.MistralAiModel(name="mistral-small-2501"),
            llm.DummyModel(name="dummy-1"),
            llm.DummyModel(name="dummy-2"),
        ]


app.include_router(adaptation.router, prefix="/api/adaptation")
