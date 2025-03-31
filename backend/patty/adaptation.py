from __future__ import annotations

from typing import Literal, TypeVar
import fastapi
import uuid

import pydantic

from . import database_utils
from . import llm
from . import orm_models


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


PassiveAtomicComponent = Text | Whitespace | Arrow
PassiveComponent = PassiveAtomicComponent | PassiveSequence


class FreeTextInput(pydantic.BaseModel):
    kind: Literal["freeTextInput"]


class MultipleChoicesInput(pydantic.BaseModel):
    kind: Literal["multipleChoicesInput"]
    choices: list[Line[PassiveComponent]]
    showChoicesByDefault: bool


class SelectableInput(pydantic.BaseModel):
    kind: Literal["selectableInput"]
    contents: list[PassiveComponent]
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


AnyComponent = PassiveAtomicComponent | FreeTextInput | MultipleChoicesInput | SelectableInput | AnySequence


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


@router.get("/default-system-prompt")
def get_default_system_prompt(session: database_utils.SessionDependable) -> str:
    strategy = session.query(orm_models.AdaptationStrategy).first()
    assert strategy is not None
    return strategy.system_prompt


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
