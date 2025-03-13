from __future__ import annotations
import textwrap
from typing import Literal
import uuid

from fastapi import FastAPI
import pydantic

from .llm import SystemMessage, UserMessage, AssistantMessage, Model as LlmModel, MistralAiModel, OpenAiModel


app = FastAPI()


class TokenizedText(pydantic.BaseModel):
    sentences: list[Sentence]


class Sentence(pydantic.BaseModel):
    tokens: list[Token]


class Word(pydantic.BaseModel):
    kind: Literal["word"]
    text: str


class Punctuation(pydantic.BaseModel):
    kind: Literal["punctuation"]
    text: str


Token = Word | Punctuation

Message = UserMessage | SystemMessage | AssistantMessage[TokenizedText]


class InitialStep(pydantic.BaseModel):
    kind: Literal["initial"]
    system_prompt: str
    input_text: str
    messages: list[Message]
    assistant_prose: str
    tokenized_text: TokenizedText | None


class AdjustmentStep(pydantic.BaseModel):
    kind: Literal["adjustment"]
    user_prompt: str
    messages: list[Message]
    assistant_prose: str
    tokenized_text: TokenizedText | None


Step = InitialStep | AdjustmentStep


class Tokenization(pydantic.BaseModel):
    id: str
    llm_model: LlmModel
    steps: list[Step]


tokenizations: dict[str, Tokenization] = {}


default_tokenization_system_prompt = textwrap.dedent(
    """\
    Le premier message de l'utilisateur sera un texte, que tu dois diviser en phrases et tokens.
    Les tokens peuvent être des mots ou de la ponctuation.
    On appelle le résultat de cette division une tokenisation.

    Dans ses messages suivants, l'utilisateur te demandera de faire des ajustements à la tokenisation du texte initial.
    A chaque ajustement, tu dois répondre avec la nouvelle tokenisation du texte initial,
    en respectant les consignes de ce messages système et les ajustements demandés par l'utilisateur.

    Tu dois séparer les phrases selon la ponctuation.

    Le format pour tes réponses comporte deux champs: `prose` et `tokenized_text`.
    Tu dois utiliser `prose` pour interagir avec l'utilisateur, et `tokenized_text` pour renvoyer la tokenisation.
    Par exemple, si les instructions sont ambiguës, ou contradictoire, tu peux demander des clarifications dans `prose`.
    Tu peux aussi indiquer brièvement les ajustements que tu as faits dans `prose`.
    Tu dois utiliser `tokenized_text` pour renvoyer la tokenisation du texte initial, après les ajustements demandés par l'utilisateur.
    Ce champs comporte une liste de phrases, et chaque phrase comporte une liste de tokens.
    Les types de tokens sont distingués par le champ `kind`.
    Utilise des tokens de type `word` pour les mots, et de type `punctuation` pour la ponctuation.
    Tu peux laisser le champ `tokenized_text` null si le message de l'utilisateur ne demande pas de changement à la tokenisation.
    """
)


@app.get("/api/default-tokenization-system-prompt")
def get_default_tokenization_system_prompt() -> str:
    return default_tokenization_system_prompt


class PostTokenizationRequest(pydantic.BaseModel):
    llm_model: MistralAiModel | OpenAiModel
    # @todo Let experimenter set temperature
    # @todo Let experimenter set top_p
    # @todo Let experimenter set random_seed
    system_prompt: str
    input_text: str


@app.post("/api/tokenization")
async def post_tokenization(req: PostTokenizationRequest) -> Tokenization:
    tokenization_id = str(uuid.uuid4())

    messages: list[Message] = [SystemMessage(message=req.system_prompt), UserMessage(message=req.input_text)]

    response = await req.llm_model.complete(messages, TokenizedText)
    messages.append(response)

    tokenization = Tokenization(
        id=tokenization_id,
        llm_model=req.llm_model,
        steps=[
            InitialStep(
                kind="initial",
                system_prompt=req.system_prompt,
                input_text=req.input_text,
                messages=messages,
                assistant_prose=response.prose,
                tokenized_text=response.structured,
            )
        ],
    )

    tokenizations[tokenization.id] = tokenization
    return tokenization


@app.get("/api/tokenization/{id}")
async def get_tokenization(id: str) -> Tokenization:
    return tokenizations[id]


class PostTokenizationAdjustmentRequest(pydantic.BaseModel):
    adjustment: str


@app.post("/api/tokenization/{id}/adjustment")
async def post_tokenization_adjustment(id: str, req: PostTokenizationAdjustmentRequest) -> Tokenization:
    tokenization = tokenizations[id]

    previous_messages: list[Message] = []
    for step in tokenization.steps:
        previous_messages.extend(step.messages)
    step_messages: list[Message] = [UserMessage(message=req.adjustment)]

    response = await tokenization.llm_model.complete(previous_messages + step_messages, TokenizedText)
    step_messages.append(response)

    tokenization.steps.append(
        AdjustmentStep(
            kind="adjustment",
            user_prompt=req.adjustment,
            messages=step_messages,
            assistant_prose=response.prose,
            tokenized_text=response.structured,
        )
    )

    return tokenization


@app.delete("/api/tokenization/{id}/last-step")
def delete_tokenization_last_step(id: str) -> Tokenization:
    tokenization = tokenizations[id]
    tokenization.steps.pop()
    return tokenization
