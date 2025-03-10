import random

from fastapi import FastAPI
import pydantic


app = FastAPI()


class Hello(pydantic.BaseModel):
    hello: str


@app.get("/api")
async def get_api_root() -> Hello:
    return Hello(hello=random.choice(["world", "you", "me"]))
