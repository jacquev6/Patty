import asyncio
import os
from typing import TypeVar

import fastapi

from .. import database_utils
from .. import llm
from ..adapted import Exercise
from ..any_json import JsonDict, JsonList
from ..api_utils import ApiModel
from ..api_utils import ApiModel
from .adaptation import Adaptation as DbAdaptation, Adjustment
from .batch import Batch
from .input import Input as DbInput
from .strategy import Strategy as DbStrategy, ConcreteLlmResponseSpecification, JsonSchemaLlmResponseSpecification


__all__ = ["router"]

router = fastapi.APIRouter()


LlmMessage = llm.UserMessage | llm.SystemMessage | llm.AssistantMessage[Exercise]


class ApiStrategy(ApiModel):
    id: str
    created_by: str
    model: llm.ConcreteModel
    system_prompt: str
    response_specification: ConcreteLlmResponseSpecification


class ApiInput(ApiModel):
    id: str
    created_by: str
    text: str


class ApiAdaptation(ApiModel):
    id: str
    created_by: str
    batch_id: str
    strategy: ApiStrategy
    input: ApiInput
    raw_llm_conversations: JsonList
    initial_assistant_error: str | None
    initial_assistant_response: Exercise | None
    adjustments: list[Adjustment]
    manual_edit: Exercise | None


@router.post("/llm-response-schema")
def get_llm_response_schema(response_specification: JsonSchemaLlmResponseSpecification) -> JsonDict:
    return response_specification.make_response_schema()


class LatestBatch(ApiModel):
    id: str
    created_by: str
    strategy: ApiStrategy
    inputs: list[ApiInput]


@router.get("/latest-batch")
def get_latest_batch(user: str, session: database_utils.SessionDependable) -> LatestBatch:
    for created_by in [user, "Patty"]:
        batch = session.query(Batch).filter(Batch.created_by == created_by).order_by(-Batch.id).first()
        if batch is not None:
            break
    assert batch is not None
    return LatestBatch(
        id=str(batch.id),
        created_by=batch.created_by,
        strategy=make_api_strategy(batch.strategy),
        inputs=[make_api_input(adaptation.input) for adaptation in batch.adaptations],
    )


class PostBatchRequest(ApiModel):
    creator: str
    strategy: ApiStrategy
    inputs: list[ApiInput]


class PostBatchResponse(ApiModel):
    id: str


@router.post("/batch")
async def post_batch(
    req: PostBatchRequest,
    engine: database_utils.EngineDependable,
    session: database_utils.SessionDependable,
    background_tasks: fastapi.BackgroundTasks,
) -> PostBatchResponse:
    strategy = session.get(DbStrategy, req.strategy.id)
    assert strategy is not None
    if (
        strategy.system_prompt != req.strategy.system_prompt
        or strategy.model != req.strategy.model
        or strategy.response_specification != req.strategy.response_specification
    ):
        strategy = DbStrategy(
            created_by=req.creator,
            model=req.strategy.model,
            system_prompt=req.strategy.system_prompt,
            response_specification=req.strategy.response_specification,
        )
        session.add(strategy)

    batch = Batch(created_by=req.creator, strategy=strategy)
    session.add(batch)

    for req_input in req.inputs:
        input = session.get(DbInput, req_input.id)
        assert input is not None
        if input.text != req_input.text:
            input = DbInput(created_by=req.creator, text=req_input.text)
            session.add(input)

        adaptation = DbAdaptation(
            created_by=req.creator,
            batch=batch,
            strategy=strategy,
            input=input,
            raw_llm_conversations=[],
            initial_assistant_error=None,
            initial_assistant_response=None,
            adjustments=[],
        )
        session.add(adaptation)

    session.flush()

    background_tasks.add_task(submit_batch, engine, batch.id)

    return PostBatchResponse(id=str(batch.id))


async def submit_batch(engine: database_utils.Engine, id: int) -> None:
    with database_utils.Session(engine) as session:
        batch = session.get(Batch, id)
        assert batch is not None

        print(f"Submitting batch {batch.id}", flush=True)
        response_format = batch.strategy.response_specification.make_response_format()

        async def submit_adaptation(adaptation: DbAdaptation) -> None:
            assert adaptation.strategy is batch.strategy

            messages: list[LlmMessage] = [
                llm.SystemMessage(content=batch.strategy.system_prompt),
                llm.UserMessage(content=adaptation.input.text),
            ]

            try:
                print(f"Submitting adaptation {adaptation.id}", flush=True)
                response = await batch.strategy.model.complete(messages, response_format)
            except llm.LlmException as error:
                print(f"Error on adaptation {adaptation.id}", flush=True)
                adaptation.raw_llm_conversations = [error.raw_conversation]
                adaptation.initial_assistant_error = error.args[0]
            else:
                print(f"Success on adaptation {adaptation.id}", flush=True)
                adaptation.raw_llm_conversations = [response.raw_conversation]
                adaptation.initial_assistant_response = response.message.content

            session.commit()

        await asyncio.gather(*(submit_adaptation(adaptation) for adaptation in batch.adaptations))


class GetBatchResponse(ApiModel):
    id: str
    created_by: str
    strategy: ApiStrategy
    adaptations: list[ApiAdaptation]


@router.get("/batch/{id}")
async def get_batch(id: str, session: database_utils.SessionDependable) -> GetBatchResponse:
    batch = get_by_id(session, Batch, id)
    return GetBatchResponse(
        id=str(batch.id),
        created_by=batch.created_by,
        strategy=make_api_strategy(batch.strategy),
        adaptations=[make_api_adaptation(adaptation) for adaptation in batch.adaptations],
    )


class PostAdaptationRequest(ApiModel):
    creator: str
    strategy: ApiStrategy
    input: ApiInput


@router.get("/{id}")
async def get_adaptation(id: str, session: database_utils.SessionDependable) -> ApiAdaptation:
    return make_api_adaptation(get_by_id(session, DbAdaptation, id))


class PostAdaptationAdjustmentRequest(ApiModel):
    adjustment: str


@router.post("/{id}/adjustment")
async def post_adaptation_adjustment(
    id: str, req: PostAdaptationAdjustmentRequest, session: database_utils.SessionDependable
) -> ApiAdaptation:
    db_adaptation = get_by_id(session, DbAdaptation, id)
    assert db_adaptation.initial_assistant_error is None
    assert db_adaptation.initial_assistant_response is not None

    messages: list[LlmMessage] = [
        llm.SystemMessage(content=db_adaptation.strategy.system_prompt),
        llm.UserMessage(content=db_adaptation.input.text),
        llm.AssistantMessage[Exercise](content=db_adaptation.initial_assistant_response),
    ]
    for adjustment in db_adaptation.adjustments:
        assert adjustment.assistant_error is None
        assert adjustment.assistant_response is not None
        messages.append(llm.UserMessage(content=adjustment.user_prompt))
        messages.append(llm.AssistantMessage[Exercise](content=adjustment.assistant_response))
    messages.append(llm.UserMessage(content=req.adjustment))

    try:
        response = await db_adaptation.strategy.model.complete(
            messages, db_adaptation.strategy.response_specification.make_response_format()
        )
    except llm.LlmException as error:
        raw_conversation = error.raw_conversation
        adjustment = Adjustment(user_prompt=req.adjustment, assistant_error=error.args[0], assistant_response=None)
    else:
        raw_conversation = response.raw_conversation
        adjustment = Adjustment(
            user_prompt=req.adjustment,
            assistant_error=None,
            assistant_response=response.message.content.model_dump(),  # type: ignore[arg-type]
        )

    raw_llm_conversations = list(db_adaptation.raw_llm_conversations)
    raw_llm_conversations.append(raw_conversation)
    db_adaptation.raw_llm_conversations = raw_llm_conversations

    adjustments = list(db_adaptation.adjustments)
    adjustments.append(adjustment)
    db_adaptation.adjustments = adjustments

    return make_api_adaptation(db_adaptation)


@router.delete("/{id}/last-adjustment")
def delete_adaptation_last_adjustment(id: str, session: database_utils.SessionDependable) -> ApiAdaptation:
    db_adaptation = get_by_id(session, DbAdaptation, id)

    raw_llm_conversations = list(db_adaptation.raw_llm_conversations)
    raw_llm_conversations.pop()
    db_adaptation.raw_llm_conversations = raw_llm_conversations

    adjustments = list(db_adaptation.adjustments)
    adjustments.pop()
    db_adaptation.adjustments = adjustments

    return make_api_adaptation(db_adaptation)


@router.put("/{id}/manual-edit")
def put_adaptation_manual_edit(id: str, req: Exercise, session: database_utils.SessionDependable) -> ApiAdaptation:
    db_adaptation = get_by_id(session, DbAdaptation, id)
    db_adaptation.manual_edit = req
    return make_api_adaptation(db_adaptation)


@router.delete("/{id}/manual-edit")
def delete_adaptation_manual_edit(id: str, session: database_utils.SessionDependable) -> ApiAdaptation:
    db_adaptation = get_by_id(session, DbAdaptation, id)
    db_adaptation.manual_edit = None
    return make_api_adaptation(db_adaptation)


Model = TypeVar("Model", bound=database_utils.OrmBase)


def get_by_id(session: database_utils.Session, model: type[Model], id: str) -> Model:
    try:
        numerical_id = int(id)
    except ValueError:
        raise fastapi.HTTPException(status_code=404, detail="Batch not found")
    db_adaptation = session.get(model, numerical_id)
    if db_adaptation is None:
        raise fastapi.HTTPException(status_code=404, detail="Batch not found")
    return db_adaptation


def make_api_adaptation(adaptation: DbAdaptation) -> ApiAdaptation:
    return ApiAdaptation(
        id=str(adaptation.id),
        created_by=adaptation.created_by,
        batch_id=str(adaptation.batch_id),
        strategy=make_api_strategy(adaptation.strategy),
        input=make_api_input(adaptation.input),
        raw_llm_conversations=adaptation.raw_llm_conversations,
        initial_assistant_error=adaptation.initial_assistant_error,
        initial_assistant_response=adaptation.initial_assistant_response,
        adjustments=adaptation.adjustments,
        manual_edit=adaptation.manual_edit,
    )


def make_api_strategy(strategy: DbStrategy) -> ApiStrategy:
    return ApiStrategy(
        id=str(strategy.id),
        created_by=strategy.created_by,
        model=strategy.model,
        system_prompt=strategy.system_prompt,
        response_specification=strategy.response_specification,
    )


def make_api_input(input: DbInput) -> ApiInput:
    return ApiInput(id=str(input.id), created_by=input.created_by, text=input.text)


export_adaptation_template_file_path = os.path.join(
    os.path.dirname(__file__), "templates", "adaptation-export", "index.html"
)


@router.get("/export/{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_adaptation(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    db_adaptation = get_by_id(session, DbAdaptation, id)
    assert db_adaptation.initial_assistant_error is None
    assert db_adaptation.initial_assistant_response is not None

    if db_adaptation.manual_edit is None:
        if len(db_adaptation.adjustments) == 0:
            exercise = db_adaptation.initial_assistant_response
        else:
            last_adjustment = db_adaptation.adjustments[-1]
            assert last_adjustment.assistant_error is None
            assert last_adjustment.assistant_response is not None
            exercise = last_adjustment.assistant_response
    else:
        exercise = db_adaptation.manual_edit

    data = exercise.model_dump_json().replace("\\", "\\\\").replace('"', '\\"')
    with open(export_adaptation_template_file_path) as f:
        template = f.read()

    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{id}.html"'

    return fastapi.responses.HTMLResponse(content=template.replace("{{ data }}", data), headers=headers)
