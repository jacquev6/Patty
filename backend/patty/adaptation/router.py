from typing import Literal
import fastapi

from .. import database_utils
from .. import llm
from ..adapted import ProseAndExercise, Exercise
from ..api_utils import ApiModel
from ..api_utils import ApiModel
from .adaptation import Adaptation as DbAdaptation, Adjustment
from .input import Input as DbInput
from .strategy import Strategy as DbStrategy


__all__ = ["router"]

router = fastapi.APIRouter()


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
    id: int
    # Abstract type `llm.AbstractModel` would be fine for backend functionality, but this type appears in the API, so it must be concrete.
    llm_model: llm.ConcreteModel
    steps: list[Step]
    manual_edit: Exercise | None


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
    strategy: Strategy
    input: Input


@router.post("")
async def post_adaptation(req: PostAdaptationRequest, session: database_utils.SessionDependable) -> Adaptation:
    strategy = session.get(DbStrategy, req.strategy.id)
    assert strategy is not None
    if strategy.system_prompt != req.strategy.system_prompt or strategy.model != req.strategy.model:
        strategy = DbStrategy(parent_id=strategy.id, model=req.strategy.model, system_prompt=req.strategy.system_prompt)
        session.add(strategy)

    input = session.get(DbInput, req.input.id)
    assert input is not None
    if input.text != req.input.text:
        input = DbInput(text=req.input.text)
        session.add(input)

    messages: list[LlmMessage] = [
        llm.SystemMessage(message=strategy.system_prompt),
        llm.UserMessage(message=input.text),
    ]

    response = await strategy.model.complete(messages, ProseAndExercise)
    messages.append(response)

    db_adaptation = DbAdaptation(
        strategy_id=strategy.id, input_id=input.id, initial_response=response.message, adjustments=[]
    )
    session.add(db_adaptation)
    session.flush()

    return make_output_adaptation(db_adaptation)


@router.get("/{id}")
async def get_adaptation(id: str, session: database_utils.SessionDependable) -> Adaptation:
    db_adaptation = session.get(DbAdaptation, id)
    assert db_adaptation is not None
    return make_output_adaptation(db_adaptation)


class PostAdaptationAdjustmentRequest(ApiModel):
    adjustment: str


@router.post("/{id}/adjustment")
async def post_adaptation_adjustment(
    id: str, req: PostAdaptationAdjustmentRequest, session: database_utils.SessionDependable
) -> Adaptation:
    db_adaptation = session.get(DbAdaptation, id)
    assert db_adaptation is not None
    assert db_adaptation.initial_response is not None

    previous_messages: list[LlmMessage] = [
        llm.SystemMessage(message=db_adaptation.strategy.system_prompt),
        llm.UserMessage(message=db_adaptation.input.text),
        llm.AssistantMessage[ProseAndExercise](message=db_adaptation.initial_response),
    ]
    for adjustment in db_adaptation.adjustments:
        previous_messages.append(llm.UserMessage(message=adjustment.user_prompt))
        previous_messages.append(llm.AssistantMessage[ProseAndExercise](message=adjustment.assistant_response))
    step_messages: list[LlmMessage] = [llm.UserMessage(message=req.adjustment)]

    response = await db_adaptation.strategy.model.complete(previous_messages + step_messages, ProseAndExercise)

    adjustments = list(db_adaptation.adjustments)
    adjustments.append(Adjustment(user_prompt=req.adjustment, assistant_response=response.message))
    db_adaptation.adjustments = adjustments

    return make_output_adaptation(db_adaptation)


@router.delete("/{id}/last-step")
def delete_adaptation_last_step(id: str, session: database_utils.SessionDependable) -> Adaptation:
    db_adaptation = session.get(DbAdaptation, id)
    assert db_adaptation is not None
    adjustments = list(db_adaptation.adjustments)
    adjustments.pop()
    db_adaptation.adjustments = adjustments
    return make_output_adaptation(db_adaptation)


@router.put("/{id}/manual-edit")
def put_adaptation_manual_edit(id: str, req: Exercise, session: database_utils.SessionDependable) -> Adaptation:
    db_adaptation = session.get(DbAdaptation, id)
    assert db_adaptation is not None
    db_adaptation.manual_edit = req
    return make_output_adaptation(db_adaptation)


@router.delete("/{id}/manual-edit")
def delete_adaptation_manual_edit(id: str, session: database_utils.SessionDependable) -> Adaptation:
    db_adaptation = session.get(DbAdaptation, id)
    assert db_adaptation is not None
    db_adaptation.manual_edit = None
    return make_output_adaptation(db_adaptation)


def make_output_adaptation(db_adaptation: DbAdaptation) -> Adaptation:
    assert db_adaptation.initial_response is not None
    return Adaptation(
        id=db_adaptation.id,
        llm_model=db_adaptation.strategy.model,
        steps=[
            InitialStep(
                kind="initial",
                system_prompt=db_adaptation.strategy.system_prompt,
                input_text=db_adaptation.input.text,
                messages=[
                    llm.SystemMessage(message=db_adaptation.strategy.system_prompt),
                    llm.UserMessage(message=db_adaptation.input.text),
                    llm.AssistantMessage[ProseAndExercise](message=db_adaptation.initial_response),
                ],
                assistant_prose=db_adaptation.initial_response.prose,
                adapted_exercise=db_adaptation.initial_response.structured,
            )
        ]
        + [
            AdjustmentStep(
                kind="adjustment",
                userPrompt=adjustment.user_prompt,
                messages=[
                    llm.UserMessage(message=adjustment.user_prompt),
                    llm.AssistantMessage[ProseAndExercise](message=adjustment.assistant_response),
                ],
                assistant_prose=adjustment.assistant_response.prose,
                adapted_exercise=adjustment.assistant_response.structured,
            )
            for adjustment in db_adaptation.adjustments
        ],
        manual_edit=db_adaptation.manual_edit,
    )
