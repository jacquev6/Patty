from __future__ import annotations

from typing import Literal, TypeVar
import fastapi
import textwrap
import uuid

import pydantic

from . import llm


__all__ = ["router"]

router = fastapi.APIRouter()


class AdaptedExercise(pydantic.BaseModel):
    format: Literal["v1"]
    instructions: Page[PassiveComponent]
    wording: Pages[AnyComponent]
    references: Line[PassiveComponent] | None


Component = TypeVar("Component")


class Pages[Component](pydantic.BaseModel):
    pages: list[Page[Component]]


class Page[Component](pydantic.BaseModel):
    lines: list[Line[Component]]


class Line[Component](pydantic.BaseModel):
    contents: list[Component]


class Text(pydantic.BaseModel):
    kind: Literal["text"]
    text: str


class Whitespace(pydantic.BaseModel):
    kind: Literal["whitespace"]


class Arrow(pydantic.BaseModel):
    kind: Literal["arrow"]


# @todo Find a way to define a generic Sequence[Component] type. Currently this breaks the polyfactory used in llm.dummy.
# In the mean time, keep PassiveSequence and AnySequence consistent.
class PassiveSequence(pydantic.BaseModel):
    kind: Literal["sequence"]
    contents: list[PassiveComponent]
    bold: bool
    italic: bool
    highlighted: str | None
    boxed: bool
    vertical: bool


PassiveComponent = Text | Whitespace | Arrow | PassiveSequence


class FreeTextInput(pydantic.BaseModel):
    kind: Literal["freeTextInput"]


class MultipleChoicesInput(pydantic.BaseModel):
    kind: Literal["multipleChoicesInput"]
    choices: list[Line[PassiveComponent]]
    showChoicesByDefault: bool


class SelectableInput(pydantic.BaseModel):
    kind: Literal["selectableInput"]
    contents: Line[PassiveComponent]
    colors: list[str]
    boxed: bool


# Keep AnySequence and PassiveSequence consistent.
class AnySequence(pydantic.BaseModel):
    kind: Literal["sequence"]
    contents: list[AnyComponent]
    bold: bool
    italic: bool
    highlighted: str | None
    boxed: bool
    vertical: bool


AnyComponent = PassiveComponent | FreeTextInput | MultipleChoicesInput | SelectableInput | AnySequence


LlmMessage = llm.UserMessage | llm.SystemMessage | llm.AssistantMessage[AdaptedExercise]


class InitialStep(pydantic.BaseModel):
    kind: Literal["initial"]
    systemPrompt: str
    inputText: str
    messages: list[LlmMessage]
    assistantProse: str
    adaptedExercise: AdaptedExercise | None


class AdjustmentStep(pydantic.BaseModel):
    kind: Literal["adjustment"]
    userPrompt: str
    messages: list[LlmMessage]
    assistantProse: str
    adaptedExercise: AdaptedExercise | None


Step = InitialStep | AdjustmentStep


class Adaptation(pydantic.BaseModel):
    id: str
    # Abstract type `llm.AbstractModel` would be fine for backend functionality, but this type appears in the API, so it must be concrete.
    llmModel: llm.ConcreteModel
    steps: list[Step]


adaptations: dict[str, Adaptation] = {}


default_system_prompt = textwrap.dedent(
    """\
    Le premier message de l'utilisateur sera un exercice scolaire.
    Tu dois répondre en séparant et explicitant la consigne et l'énoncé de cet exercice.
    On appelle cette opération une "adaptation".

    Tu ne dois jamais résoudre les exercices, seulement les adapter.

    Dans ses messages suivants, l'utilisateur te demandera de faire des ajustements à ta réponse.
    A chaque ajustement, tu dois répondre avec la nouvelle adaptation de l'exercice initial,
    en respectant les consignes de ce messages système et les ajustements demandés par l'utilisateur.

    Le format pour tes réponses comporte deux champs: `prose` et `structured`.
    Tu dois utiliser `prose` pour interagir avec l'utilisateur, et `structured` pour renvoyer la séparation.
    Par exemple, si les instructions sont ambiguës, ou contradictoire, tu peux demander des clarifications dans `prose`.
    Tu peux aussi utiliser `prose` pour décrire brièvement les ajustements que tu as faits.
    Tu dois utiliser `structured` pour renvoyer l'adaptation de l'exercice initial, après les ajustements demandés par l'utilisateur.
    Tu peux laisser le champ `structured` null si le message de l'utilisateur ne demande pas de changement à l'adaptation."""
)


@router.get("/default-system-prompt")
def get_default_system_prompt() -> str:
    return default_system_prompt


class PostAdaptationRequest(pydantic.BaseModel):
    llmModel: llm.ConcreteModel
    # @todo Let experimenter set temperature
    # @todo Let experimenter set top_p
    # @todo Let experimenter set random_seed
    systemPrompt: str
    inputText: str


@router.post("")
async def post_adaptation(req: PostAdaptationRequest) -> Adaptation:
    adaptation_id = str(uuid.uuid4())

    messages: list[LlmMessage] = [llm.SystemMessage(message=req.systemPrompt), llm.UserMessage(message=req.inputText)]

    response = await req.llmModel.complete(messages, AdaptedExercise)
    messages.append(response)

    adaptation = Adaptation(
        id=adaptation_id,
        llmModel=req.llmModel,
        steps=[
            InitialStep(
                kind="initial",
                systemPrompt=req.systemPrompt,
                inputText=req.inputText,
                messages=messages,
                assistantProse=response.prose,
                adaptedExercise=response.structured,
            )
        ],
    )

    adaptations[adaptation.id] = adaptation
    return adaptation


@router.get("/{id}")
async def get_adaptation(id: str) -> Adaptation:
    return adaptations[id]


class PostAdaptationAdjustmentRequest(pydantic.BaseModel):
    adjustment: str


@router.post("/{id}/adjustment")
async def post_adaptation_adjustment(id: str, req: PostAdaptationAdjustmentRequest) -> Adaptation:
    adaptation = adaptations[id]

    previous_messages: list[LlmMessage] = []
    for step in adaptation.steps:
        previous_messages.extend(step.messages)
    step_messages: list[LlmMessage] = [llm.UserMessage(message=req.adjustment)]

    response = await adaptation.llmModel.complete(previous_messages + step_messages, AdaptedExercise)
    step_messages.append(response)

    adaptation.steps.append(
        AdjustmentStep(
            kind="adjustment",
            userPrompt=req.adjustment,
            messages=step_messages,
            assistantProse=response.prose,
            adaptedExercise=response.structured,
        )
    )

    return adaptation


@router.delete("/{id}/last-step")
def delete_adaptation_last_step(id: str) -> Adaptation:
    adaptation = adaptations[id]
    adaptation.steps.pop()
    return adaptation
