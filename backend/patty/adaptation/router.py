from typing import Any, TypeVar
import asyncio
import datetime
import hashlib
import json
import os

import fastapi

from .. import database_utils
from .. import llm
from ..adapted import Exercise
from ..any_json import JsonDict, JsonList
from ..api_utils import ApiModel
from ..api_utils import ApiModel
from .adaptation import (
    Adaptation as DbAdaptation,
    Adjustment,
    AssistantInvalidJsonError,
    AssistantNotJsonError,
    AssistantResponse,
    AssistantSuccess,
)
from .batch import Batch
from .input import Input as DbInput
from .strategy import (
    Strategy as DbStrategy,
    StrategySettingsBranch,
    StrategySettings,
    ConcreteLlmResponseSpecification,
    JsonSchemaLlmResponseSpecification,
)


__all__ = ["router"]

router = fastapi.APIRouter()


LlmMessage = (
    llm.UserMessage
    | llm.SystemMessage
    | llm.AssistantMessage[Exercise]
    | llm.InvalidJsonAssistantMessage
    | llm.NotJsonAssistantMessage
)


class ApiStrategySettings(ApiModel):
    name: str | None
    system_prompt: str
    response_specification: ConcreteLlmResponseSpecification


class ApiStrategy(ApiModel):
    model: llm.ConcreteModel
    settings: ApiStrategySettings


class ApiInput(ApiModel):
    page_number: int | None
    exercise_number: str | None
    text: str


class ApiAdaptation(ApiModel):
    id: str
    created_by: str
    batch_id: str
    strategy: ApiStrategy
    input: ApiInput
    raw_llm_conversations: JsonList
    initial_assistant_response: AssistantResponse | None
    adjustments: list[Adjustment]
    manual_edit: Exercise | None


@router.post("/llm-response-schema")
def get_llm_response_schema(response_specification: JsonSchemaLlmResponseSpecification) -> JsonDict:
    return response_specification.make_response_schema()


class LatestBatch(ApiModel):
    id: str
    strategy: ApiStrategy
    inputs: list[ApiInput]
    available_strategy_settings: list[ApiStrategySettings]


@router.get("/latest-batch")
def get_latest_batch(user: str, session: database_utils.SessionDependable) -> LatestBatch:
    for created_by in [user, "Patty"]:
        batch = session.query(Batch).filter(Batch.created_by == created_by).order_by(-Batch.id).first()
        if batch is not None:
            break
    assert batch is not None
    available_strategy_settings = []
    for branch in session.query(StrategySettingsBranch).order_by(StrategySettingsBranch.name).all():
        assert branch.head is not None
        available_strategy_settings.append(make_api_strategy_settings(branch.head))
        if branch.head.parent is not None:
            available_strategy_settings.append(make_api_strategy_settings(branch.head.parent))
    return LatestBatch(
        id=str(batch.id),
        strategy=make_api_strategy(batch.strategy),
        inputs=[make_api_input(adaptation.input) for adaptation in batch.adaptations],
        available_strategy_settings=available_strategy_settings,
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
    if req.strategy.settings.name is None:
        base_settings = None
        branch = None
    else:
        # @todo Move this string manipulation to the frontend. In particular, this will break with i18n.
        if req.strategy.settings.name.endswith(" (previous version)"):
            branch_name = req.strategy.settings.name[:-19]
        else:
            branch_name = req.strategy.settings.name
        branch = session.query(StrategySettingsBranch).filter(StrategySettingsBranch.name == branch_name).first()
        if branch is None:
            assert branch_name == req.strategy.settings.name
            base_settings = None
            branch = StrategySettingsBranch(name=branch_name)
            session.add(branch)
            # session.flush()
        else:
            assert branch.head is not None
            if branch_name == req.strategy.settings.name:
                base_settings = branch.head
            else:
                base_settings = branch.head.parent

    if (
        base_settings is None
        or base_settings.system_prompt != req.strategy.settings.system_prompt
        or base_settings.response_specification != req.strategy.settings.response_specification
    ):
        settings = StrategySettings(
            branch=branch,
            parent=base_settings,
            created_by=req.creator,
            system_prompt=req.strategy.settings.system_prompt,
            response_specification=req.strategy.settings.response_specification,
        )
        session.add(settings)
    else:
        settings = base_settings
    if branch is not None:
        session.flush()
        branch.head = settings
    strategy = DbStrategy(created_by=req.creator, model=req.strategy.model, settings=settings)
    session.add(strategy)

    batch = Batch(created_by=req.creator, created_at=datetime.datetime.now(datetime.timezone.utc), strategy=strategy)
    session.add(batch)

    for req_input in req.inputs:
        input = DbInput(
            created_by=req.creator,
            page_number=req_input.page_number,
            exercise_number=req_input.exercise_number,
            text=req_input.text,
        )
        session.add(input)

        adaptation = DbAdaptation(
            created_by=req.creator,
            batch=batch,
            strategy=strategy,
            input=input,
            raw_llm_conversations=[],
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
        response_format = batch.strategy.settings.response_specification.make_response_format()

        async def submit_adaptation(adaptation: DbAdaptation) -> None:
            assert adaptation.strategy is batch.strategy

            messages: list[LlmMessage] = [
                llm.SystemMessage(content=batch.strategy.settings.system_prompt),
                llm.UserMessage(content=adaptation.input.text),
            ]

            try:
                print(f"Submitting adaptation {adaptation.id}", flush=True)
                response = await batch.strategy.model.complete(messages, response_format)
            except llm.InvalidJsonLlmException as error:
                print(f"Error 'invalid JSON' on adaptation {adaptation.id}", flush=True)
                adaptation.raw_llm_conversations = [error.raw_conversation]
                adaptation.initial_assistant_response = AssistantInvalidJsonError(
                    kind="error", error="invalid-json", parsed=error.parsed
                )
            except llm.NotJsonLlmException as error:
                print(f"Error 'not JSON' on adaptation {adaptation.id}", flush=True)
                adaptation.raw_llm_conversations = [error.raw_conversation]
                adaptation.initial_assistant_response = AssistantNotJsonError(
                    kind="error", error="not-json", text=error.text
                )
            else:
                print(f"Success on adaptation {adaptation.id}", flush=True)
                adaptation.raw_llm_conversations = [response.raw_conversation]
                adaptation.initial_assistant_response = AssistantSuccess(
                    kind="success", exercise=Exercise(**response.message.content.model_dump())
                )

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


class GetBatchesResponse(ApiModel):
    class Batch(ApiModel):
        id: str
        created_by: str
        created_at: datetime.datetime

    batches: list[Batch]


@router.get("/batches")
async def get_batches(session: database_utils.SessionDependable) -> GetBatchesResponse:
    batches = session.query(Batch).order_by(-Batch.id).all()
    return GetBatchesResponse(
        batches=[
            GetBatchesResponse.Batch(id=str(batch.id), created_by=batch.created_by, created_at=batch.created_at)
            for batch in batches
        ]
    )


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
    assert db_adaptation.initial_assistant_response is not None

    def make_assistant_message(assistant_response: AssistantResponse) -> LlmMessage:
        if isinstance(assistant_response, AssistantSuccess):
            return llm.AssistantMessage[Exercise](content=assistant_response.exercise)
        elif isinstance(assistant_response, AssistantInvalidJsonError):
            return llm.InvalidJsonAssistantMessage(content=assistant_response.parsed)
        elif isinstance(assistant_response, AssistantNotJsonError):
            return llm.NotJsonAssistantMessage(content=assistant_response.text)
        else:
            raise ValueError("Unknown assistant response type")

    messages: list[LlmMessage] = [
        llm.SystemMessage(content=db_adaptation.strategy.settings.system_prompt),
        llm.UserMessage(content=db_adaptation.input.text),
        make_assistant_message(db_adaptation.initial_assistant_response),
    ]
    for adjustment in db_adaptation.adjustments:
        assert isinstance(adjustment.assistant_response, AssistantSuccess)
        messages.append(llm.UserMessage(content=adjustment.user_prompt))
        make_assistant_message(adjustment.assistant_response)
    messages.append(llm.UserMessage(content=req.adjustment))

    try:
        response = await db_adaptation.strategy.model.complete(
            messages, db_adaptation.strategy.settings.response_specification.make_response_format()
        )
    except llm.InvalidJsonLlmException as error:
        raw_conversation = error.raw_conversation
        assistant_response: AssistantResponse = AssistantInvalidJsonError(
            kind="error", error="invalid-json", parsed=error.parsed
        )
    except llm.NotJsonLlmException as error:
        raw_conversation = error.raw_conversation
        assistant_response = AssistantNotJsonError(kind="error", error="not-json", text=error.text)
    else:
        raw_conversation = response.raw_conversation
        assistant_response = AssistantSuccess(
            kind="success", exercise=Exercise(**response.message.content.model_dump())
        )

    raw_llm_conversations = list(db_adaptation.raw_llm_conversations)
    raw_llm_conversations.append(raw_conversation)
    db_adaptation.raw_llm_conversations = raw_llm_conversations

    adjustments = list(db_adaptation.adjustments)
    adjustments.append(Adjustment(user_prompt=req.adjustment, assistant_response=assistant_response))
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
        initial_assistant_response=adaptation.initial_assistant_response,
        adjustments=adaptation.adjustments,
        manual_edit=adaptation.manual_edit,
    )


def make_api_strategy(strategy: DbStrategy) -> ApiStrategy:
    return ApiStrategy(model=strategy.model, settings=make_api_strategy_settings(strategy.settings))


def make_api_strategy_settings(settings: StrategySettings) -> ApiStrategySettings:
    if settings.branch is None:
        name = None
    elif settings.branch.head_id == settings.id:
        name = settings.branch.name
    else:
        # @todo Move this string manipulation to the frontend. In particular, this will break with i18n.
        name = f"{settings.branch.name} (previous version)"

    return ApiStrategySettings(
        name=name, system_prompt=settings.system_prompt, response_specification=settings.response_specification
    )


def make_api_input(input: DbInput) -> ApiInput:
    return ApiInput(page_number=input.page_number, exercise_number=input.exercise_number, text=input.text)


export_adaptation_template_file_path = os.path.join(
    os.path.dirname(__file__), "templates", "adaptation-export", "index.html"
)


@router.get("/export/adaptation-{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_adaptation(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    data = make_exercise_data(get_by_id(session, DbAdaptation, id))
    assert data is not None
    content = render_template(export_adaptation_template_file_path, "ADAPTATION_EXPORT_DATA", data)

    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{data['exerciseId']}.html"'

    return fastapi.responses.HTMLResponse(content=content, headers=headers)


export_batch_template_file_path = os.path.join(os.path.dirname(__file__), "templates", "batch-export", "index.html")


@router.get("/export/batch-{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_batch(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    data = list(
        filter(None, (make_exercise_data(adaptation) for adaptation in get_by_id(session, Batch, id).adaptations))
    )

    content = render_template(export_batch_template_file_path, "BATCH_EXPORT_DATA", data)

    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="test-batch-{id}.html"'

    return fastapi.responses.HTMLResponse(content=content, headers=headers)


def render_template(template: str, placeholder: str, data: Any) -> str:
    with open(template) as f:
        template = f.read()
    return template.replace(
        f"##TO_BE_SUBSTITUTED_{placeholder}##", json.dumps(data).replace("\\", "\\\\").replace('"', '\\"')
    )


def make_exercise_data(adaptation: DbAdaptation) -> JsonDict | None:
    if adaptation.input.page_number is not None and adaptation.input.exercise_number is not None:
        exercise_id = f"P{adaptation.input.page_number}Ex{adaptation.input.exercise_number}"
    else:
        exercise_id = f"exercice-{adaptation.id}"

    if adaptation.manual_edit is None:
        if len(adaptation.adjustments) == 0:
            if not isinstance(adaptation.initial_assistant_response, AssistantSuccess):
                return None
            exercise = adaptation.initial_assistant_response.exercise
        else:
            last_adjustment = adaptation.adjustments[-1]
            if not isinstance(last_adjustment.assistant_response, AssistantSuccess):
                return None
            exercise = last_adjustment.assistant_response.exercise
    else:
        exercise = adaptation.manual_edit

    exercise_dump = exercise.model_dump()
    return {
        "exerciseId": exercise_id,
        "studentAnswersStorageKey": hashlib.md5(
            json.dumps(exercise_dump, separators=(",", ":"), indent=None).encode()
        ).hexdigest(),
        "adaptedExercise": exercise_dump,
    }
