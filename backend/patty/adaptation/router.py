from typing import Literal
import fastapi
import uuid

import pydantic

from ..api_utils import ApiModel
from .. import database_utils
from .. import llm
from ..adapted import Exercise
from .input import Input as DbInput
from .strategy import Strategy as DbStrategy


__all__ = ["router"]

router = fastapi.APIRouter()


class ProseAndExercise(pydantic.BaseModel):
    prose: str
    structured: Exercise


LlmMessage = llm.UserMessage | llm.SystemMessage | llm.AssistantMessage[ProseAndExercise]


class InitialStep(ApiModel):
    kind: Literal["initial"]
    system_prompt: str
    input_text: str
    messages: list[LlmMessage]
    assistant_prose: str
    adapted_exercise: Exercise | None


class AdjustmentStep(ApiModel):
    kind: Literal["adjustment"]
    userPrompt: str
    messages: list[LlmMessage]
    assistant_prose: str
    adapted_exercise: Exercise | None


Step = InitialStep | AdjustmentStep


class Adaptation(ApiModel):
    id: str
    # Abstract type `llm.AbstractModel` would be fine for backend functionality, but this type appears in the API, so it must be concrete.
    llm_model: llm.ConcreteModel
    steps: list[Step]


adaptations: dict[str, Adaptation] = {}


class Strategy(ApiModel):
    id: int
    model: llm.ConcreteModel
    system_prompt: str


@router.get("/latest-strategy", response_model=Strategy)
def get_latest_strategy(session: database_utils.SessionDependable) -> DbStrategy:
    strategy = session.query(DbStrategy).order_by(-DbStrategy.id).first()
    assert strategy is not None
    return strategy


class Input(ApiModel):
    id: int
    text: str


@router.get("/latest-input", response_model=Input)
def get_latest_input(session: database_utils.SessionDependable) -> DbInput:
    input = session.query(DbInput).order_by(-DbInput.id).first()
    assert input is not None
    return input


class PostAdaptationRequest(ApiModel):
    strategy_id: int
    llm_model: llm.ConcreteModel
    # @todo Let experimenter set temperature
    # @todo Let experimenter set top_p
    # @todo Let experimenter set random_seed
    system_prompt: str
    input_id: int
    input_text: str


@router.post("")
async def post_adaptation(req: PostAdaptationRequest, session: database_utils.SessionDependable) -> Adaptation:
    strategy = session.get(DbStrategy, req.strategy_id)
    assert strategy is not None
    if strategy.system_prompt != req.system_prompt or strategy.model != req.llm_model:
        strategy = DbStrategy(parent_id=strategy.id, model=req.llm_model, system_prompt=req.system_prompt)
        session.add(strategy)

    input = session.get(DbInput, req.input_id)
    assert input is not None
    if input.text != req.input_text:
        input = DbInput(text=req.input_text)
        session.add(input)

    adaptation_id = str(uuid.uuid4())

    messages: list[LlmMessage] = [llm.SystemMessage(message=req.system_prompt), llm.UserMessage(message=req.input_text)]

    response = await req.llm_model.complete(messages, ProseAndExercise)
    messages.append(response)

    adaptation = Adaptation(
        id=adaptation_id,
        llm_model=req.llm_model,
        steps=[
            InitialStep(
                kind="initial",
                system_prompt=req.system_prompt,
                input_text=req.input_text,
                messages=messages,
                assistant_prose=response.message.prose,
                adapted_exercise=response.message.structured,
            )
        ],
    )

    adaptations[adaptation.id] = adaptation
    return adaptation


@router.get("/{id}")
async def get_adaptation(id: str) -> Adaptation:
    return adaptations[id]


class PostAdaptationAdjustmentRequest(ApiModel):
    adjustment: str


@router.post("/{id}/adjustment")
async def post_adaptation_adjustment(id: str, req: PostAdaptationAdjustmentRequest) -> Adaptation:
    adaptation = adaptations[id]

    previous_messages: list[LlmMessage] = []
    for step in adaptation.steps:
        previous_messages.extend(step.messages)
    step_messages: list[LlmMessage] = [llm.UserMessage(message=req.adjustment)]

    response = await adaptation.llm_model.complete(previous_messages + step_messages, ProseAndExercise)
    step_messages.append(response)

    adaptation.steps.append(
        AdjustmentStep(
            kind="adjustment",
            userPrompt=req.adjustment,
            messages=step_messages,
            assistant_prose=response.message.prose,
            adapted_exercise=response.message.structured,
        )
    )

    return adaptation


@router.delete("/{id}/last-step")
def delete_adaptation_last_step(id: str) -> Adaptation:
    adaptation = adaptations[id]
    adaptation.steps.pop()
    return adaptation
