import random

from fastapi import FastAPI
import mistralai
import pydantic


mistral = mistralai.Mistral(api_key="9iLjdlvUZDpc77IgNn005O2ggLO6a9Gi")


app = FastAPI()


class Cheese(pydantic.BaseModel):
    name: str


messages: list[mistralai.models.Messages] = [
    mistralai.SystemMessage(content="Please answer each question with a single word."),
    mistralai.UserMessage(content="Please name a French cheese."),
]


@app.get("/api/get-cheese")
async def get_cheese() -> Cheese:
    response = await mistral.chat.complete_async(model="mistral-small-latest", messages=messages, max_tokens=4000)
    assert response.choices is not None
    assert isinstance(response.choices[0].message.content, str)

    messages.append(response.choices[0].message)
    messages.append(mistralai.UserMessage(content="Please name another French cheese."))

    return Cheese(name=response.choices[0].message.content)
