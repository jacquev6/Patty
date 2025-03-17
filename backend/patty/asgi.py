import fastapi

from . import llm
from . import tokenization


app = fastapi.FastAPI()


@app.get("/api/available-llm-models")
def get_available_llm_models() -> list[llm.ConcreteModel]:
    # @todo Hide DummyModel in production
    return [
        llm.DummyModel(name="dummy-1"),
        llm.DummyModel(name="dummy-2"),
        llm.DummyModel(name="dummy-3"),
        llm.MistralAiModel(name="mistral-large-2411"),
        llm.MistralAiModel(name="mistral-small-2501"),
        llm.OpenAiModel(name="gpt-4o-2024-08-06"),
        llm.OpenAiModel(name="gpt-4o-mini-2024-07-18"),
    ]


app.include_router(tokenization.router, prefix="/api/tokenization")
