from typing import Literal
import fastapi
import uuid

import pydantic

from .. import database_utils
from .. import llm
from ..adapted import Exercise
from .input import Input as DbInput
from .strategy import Strategy as DbStrategy


__all__ = ["router"]

router = fastapi.APIRouter()


LlmMessage = llm.UserMessage | llm.SystemMessage | llm.AssistantMessage[Exercise]


class InitialStep(pydantic.BaseModel):
    kind: Literal["initial"]
    systemPrompt: str
    inputText: str
    messages: list[LlmMessage]
    assistantProse: str
    adaptedExercise: Exercise | None


class AdjustmentStep(pydantic.BaseModel):
    kind: Literal["adjustment"]
    userPrompt: str
    messages: list[LlmMessage]
    assistantProse: str
    adaptedExercise: Exercise | None


Step = InitialStep | AdjustmentStep


class Adaptation(pydantic.BaseModel):
    id: str
    # Abstract type `llm.AbstractModel` would be fine for backend functionality, but this type appears in the API, so it must be concrete.
    llmModel: llm.ConcreteModel
    steps: list[Step]


adaptations: dict[str, Adaptation] = {}


class Strategy(pydantic.BaseModel):
    id: int
    model: llm.ConcreteModel
    system_prompt: str


@router.get("/latest-strategy", response_model=Strategy)
def get_latest_strategy(session: database_utils.SessionDependable) -> DbStrategy:
    strategy = session.query(DbStrategy).order_by(-DbStrategy.id).first()
    assert strategy is not None
    return strategy


class Input(pydantic.BaseModel):
    id: int
    text: str


@router.get("/latest-input", response_model=Input)
def get_latest_input(session: database_utils.SessionDependable) -> DbInput:
    input = session.query(DbInput).order_by(-DbInput.id).first()
    assert input is not None
    return input


class PostAdaptationRequest(pydantic.BaseModel):
    strategyId: int
    llmModel: llm.ConcreteModel
    # @todo Let experimenter set temperature
    # @todo Let experimenter set top_p
    # @todo Let experimenter set random_seed
    systemPrompt: str
    inputId: int
    inputText: str


@router.post("")
async def post_adaptation(req: PostAdaptationRequest, session: database_utils.SessionDependable) -> Adaptation:
    strategy = session.get(DbStrategy, req.strategyId)
    assert strategy is not None
    if strategy.system_prompt != req.systemPrompt or strategy.model != req.llmModel:
        strategy = DbStrategy(parent_id=strategy.id, model=req.llmModel, system_prompt=req.systemPrompt)
        session.add(strategy)

    input = session.get(DbInput, req.inputId)
    assert input is not None
    if input.text != req.inputText:
        input = DbInput(text=req.inputText)
        session.add(input)

    adaptation_id = str(uuid.uuid4())

    messages: list[LlmMessage] = [llm.SystemMessage(message=req.systemPrompt), llm.UserMessage(message=req.inputText)]

    response = await req.llmModel.complete(messages, Exercise)
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

    response = await adaptation.llmModel.complete(previous_messages + step_messages, Exercise)
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
