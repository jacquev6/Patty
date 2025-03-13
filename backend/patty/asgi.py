import fastapi

from . import tokenization


app = fastapi.FastAPI()

app.include_router(tokenization.router, prefix="/api/tokenization")
