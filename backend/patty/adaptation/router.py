from typing import Any, TypeVar
import base64
import datetime
import hashlib
import json
import os
import urllib.parse

import boto3
import botocore.client
import fastapi
import fastapi.testclient

from .. import authentication
from .. import database_utils
from .. import llm
from .. import settings
from ..adapted import Exercise
from ..any_json import JsonDict, JsonList
from ..api_utils import ApiModel
from . import orm_models as db
from .adaptation import (
    Adjustment,
    AssistantInvalidJsonError,
    AssistantNotJsonError,
    AssistantResponse,
    AssistantSuccess,
)
from .strategy import ConcreteLlmResponseSpecification, JsonSchemaLlmResponseSpecification


__all__ = ["router"]

s3 = boto3.client("s3", config=botocore.client.Config(region_name="eu-west-3", signature_version="s3v4"))

api_router = fastapi.APIRouter(dependencies=[fastapi.Depends(authentication.auth_bearer_dependable)])


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
    removed_from_textbook: bool


@api_router.post("/llm-response-schema")
def get_llm_response_schema(response_specification: JsonSchemaLlmResponseSpecification) -> JsonDict:
    return response_specification.make_response_schema()


class LatestBatch(ApiModel):
    id: str
    strategy: ApiStrategy
    inputs: list[ApiInput]
    available_strategy_settings: list[ApiStrategySettings]


@api_router.get("/latest-batch")
def get_latest_batch(user: str, session: database_utils.SessionDependable) -> LatestBatch:
    for created_by in [user, "Patty"]:
        batch = (
            session.query(db.SandboxAdaptationBatch)
            .filter(db.SandboxAdaptationBatch.created_by_username == created_by)
            .order_by(-db.SandboxAdaptationBatch.id)
            .first()
        )
        if batch is not None:
            break
    assert batch is not None
    available_strategy_settings = []
    for exercise_class in session.query(db.ExerciseClass).order_by(db.ExerciseClass.name).all():
        assert exercise_class.latest_strategy_settings is not None
        available_strategy_settings.append(make_api_strategy_settings(exercise_class.latest_strategy_settings))
        if exercise_class.latest_strategy_settings.parent is not None:
            available_strategy_settings.append(
                make_api_strategy_settings(exercise_class.latest_strategy_settings.parent)
            )
    return LatestBatch(
        id=str(batch.id),
        strategy=make_api_strategy(batch.strategy),
        inputs=[make_api_input(adaptation.exercise) for adaptation in batch.adaptations],
        available_strategy_settings=available_strategy_settings,
    )


class PostBatchRequest(ApiModel):
    creator: str
    strategy: ApiStrategy
    inputs: list[ApiInput]


class PostBatchResponse(ApiModel):
    id: str


@api_router.post("/batch")
async def post_batch(
    req: PostBatchRequest, engine: database_utils.EngineDependable, session: database_utils.SessionDependable
) -> PostBatchResponse:
    now = datetime.datetime.now(datetime.timezone.utc)

    if req.strategy.settings.name is None:
        base_settings = None
        exercise_class = None
    else:
        # @todo Move this string manipulation to the frontend. In particular, this will break with i18n.
        if req.strategy.settings.name.endswith(" (previous version)"):
            branch_name = req.strategy.settings.name[:-19]
        else:
            branch_name = req.strategy.settings.name
        exercise_class = session.query(db.ExerciseClass).filter(db.ExerciseClass.name == branch_name).first()
        if exercise_class is None:
            assert branch_name == req.strategy.settings.name
            base_settings = None
            exercise_class = db.ExerciseClass(
                name=branch_name, created_by_username=req.creator, created_at=now, latest_strategy_settings=None
            )
            session.add(exercise_class)
        else:
            assert exercise_class.latest_strategy_settings is not None
            if branch_name == req.strategy.settings.name:
                base_settings = exercise_class.latest_strategy_settings
            else:
                base_settings = exercise_class.latest_strategy_settings.parent

    if (
        base_settings is None
        or base_settings.system_prompt != req.strategy.settings.system_prompt
        or base_settings.response_specification != req.strategy.settings.response_specification
    ):
        settings = db.AdaptationStrategySettings(
            exercise_class=exercise_class,
            parent=base_settings,
            created_by_username=req.creator,
            created_at=now,
            system_prompt=req.strategy.settings.system_prompt,
            response_specification=req.strategy.settings.response_specification,
        )
        session.add(settings)
    else:
        settings = base_settings
    if exercise_class is not None:
        session.flush()
        exercise_class.latest_strategy_settings = settings
    strategy = db.AdaptationStrategy(
        created_by_username=req.creator, created_at=now, model=req.strategy.model, settings=settings
    )
    session.add(strategy)

    batch = db.SandboxAdaptationBatch(
        created_by_username=req.creator, created_at=now, strategy=strategy, textbook=None, removed_from_textbook=False
    )
    session.add(batch)

    for req_input in req.inputs:
        exercise = db.AdaptableExercise(
            created_by_username=req.creator,
            created_by_extraction_id=None,
            created_at=now,
            textbook=None,
            removed_from_textbook=False,
            page_number=req_input.page_number,
            exercise_number=req_input.exercise_number,
            full_text=req_input.text,
            classified_at=now,
            classified_by_username=req.creator,
            classified_by_classification_id=None,
            exercise_class=exercise_class,
        )
        session.add(exercise)

        adaptation = db.Adaptation(
            created_by_username=req.creator,
            created_at=now,
            sandbox_batch=batch,
            strategy=strategy,
            exercise=exercise,
            raw_llm_conversations=[],
            initial_assistant_response=None,
            adjustments=[],
            manual_edit=None,
        )
        session.add(adaptation)

    session.flush()

    return PostBatchResponse(id=str(batch.id))


class GetBatchResponse(ApiModel):
    id: str
    created_by: str
    strategy: ApiStrategy
    adaptations: list[ApiAdaptation]


@api_router.get("/batch/{id}")
async def get_batch(id: str, session: database_utils.SessionDependable) -> GetBatchResponse:
    batch = get_by_id(session, db.SandboxAdaptationBatch, id)
    return GetBatchResponse(
        id=str(batch.id),
        created_by=batch.created_by_username,
        strategy=make_api_strategy(batch.strategy),
        adaptations=[make_api_adaptation(adaptation) for adaptation in batch.adaptations],
    )


class GetBatchesResponse(ApiModel):
    class Batch(ApiModel):
        id: str
        created_by: str
        created_at: datetime.datetime
        model: llm.ConcreteModel
        strategy_settings_name: str | None

    batches: list[Batch]


@api_router.get("/batches")
async def get_batches(session: database_utils.SessionDependable) -> GetBatchesResponse:
    batches = (
        session.query(db.SandboxAdaptationBatch)
        .filter(db.SandboxAdaptationBatch.textbook_id == None)
        .order_by(-db.SandboxAdaptationBatch.id)
        .all()
    )
    return GetBatchesResponse(
        batches=[
            GetBatchesResponse.Batch(
                id=str(batch.id),
                created_by=batch.created_by_username,
                created_at=batch.created_at,
                model=batch.strategy.model,
                strategy_settings_name=make_api_strategy_settings_name(batch.strategy.settings),
            )
            for batch in batches
        ]
    )


class PostTextbookRequest(ApiModel):
    creator: str
    title: str


class PostTextbookResponse(ApiModel):
    id: str


@api_router.post("/textbook")
def post_textbook(
    req: PostTextbookRequest, engine: database_utils.EngineDependable, session: database_utils.SessionDependable
) -> PostTextbookResponse:
    textbook = db.Textbook(
        title=req.title, created_by_username=req.creator, created_at=datetime.datetime.now(datetime.timezone.utc)
    )
    session.add(textbook)
    session.flush()
    return PostTextbookResponse(id=str(textbook.id))


class ApiTextbook(ApiModel):
    id: str
    created_by: str
    title: str

    class Batch(ApiModel):
        id: str
        strategy: ApiStrategy
        adaptations: list[ApiAdaptation]
        removed_from_textbook: bool

    batches: list[Batch]

    class ExternalExercise(ApiModel):
        id: str
        page_number: int | None
        exercise_number: str | None
        original_file_name: str
        removed_from_textbook: bool

    external_exercises: list[ExternalExercise]


class GetTextbookResponse(ApiModel):
    textbook: ApiTextbook
    available_strategy_settings: list[str]


@api_router.get("/textbook/{id}")
async def get_textbook(id: str, session: database_utils.SessionDependable) -> GetTextbookResponse:
    textbook = get_by_id(session, db.Textbook, id)
    return GetTextbookResponse(
        textbook=make_api_textbook(textbook),
        available_strategy_settings=[
            exercise_class.name
            for exercise_class in session.query(db.ExerciseClass).order_by(db.ExerciseClass.name).all()
        ],
    )


class GetTextbooksResponse(ApiModel):
    class Textbook(ApiModel):
        id: str
        created_by: str
        created_at: datetime.datetime
        title: str

    textbooks: list[Textbook]


@api_router.get("/textbooks")
async def get_textbooks(session: database_utils.SessionDependable) -> GetTextbooksResponse:
    textbooks = session.query(db.Textbook).order_by(-db.Textbook.id).all()
    return GetTextbooksResponse(
        textbooks=[
            GetTextbooksResponse.Textbook(
                id=str(textbook.id),
                created_by=textbook.created_by_username,
                created_at=textbook.created_at,
                title=textbook.title,
            )
            for textbook in textbooks
        ]
    )


class PostTextbookBatchRequest(ApiModel):
    creator: str
    model: llm.ConcreteModel
    branch_name: str
    inputs: list[ApiInput]


@api_router.post("/textbook/{id}/batches")
def post_textbook_batch(
    id: str,
    req: PostTextbookBatchRequest,
    engine: database_utils.EngineDependable,
    session: database_utils.SessionDependable,
) -> ApiTextbook:
    textbook = get_by_id(session, db.Textbook, id)

    now = datetime.datetime.now(datetime.timezone.utc)

    exercise_class = session.query(db.ExerciseClass).filter(db.ExerciseClass.name == req.branch_name).first()
    assert exercise_class is not None
    assert exercise_class.latest_strategy_settings is not None

    strategy = db.AdaptationStrategy(
        created_by_username=req.creator,
        created_at=now,
        model=req.model,
        settings=exercise_class.latest_strategy_settings,
    )
    session.add(strategy)

    batch = db.SandboxAdaptationBatch(
        textbook=textbook,
        removed_from_textbook=False,
        created_by_username=req.creator,
        created_at=now,
        strategy=strategy,
    )
    session.add(batch)

    for req_input in req.inputs:
        exercise = db.AdaptableExercise(
            created_by_username=req.creator,
            created_by_extraction_id=None,
            created_at=now,
            textbook=textbook,
            removed_from_textbook=False,
            page_number=req_input.page_number,
            exercise_number=req_input.exercise_number,
            full_text=req_input.text,
            classified_at=now,
            classified_by_username=req.creator,
            classified_by_classification_id=None,
            exercise_class=exercise_class,
        )
        session.add(exercise)

        adaptation = db.Adaptation(
            created_by_username=req.creator,
            created_at=now,
            sandbox_batch=batch,
            strategy=strategy,
            exercise=exercise,
            raw_llm_conversations=[],
            initial_assistant_response=None,
            adjustments=[],
            manual_edit=None,
        )
        session.add(adaptation)

    session.flush()

    return make_api_textbook(textbook)


@api_router.put("/textbook/{textbook_id}/batch/{batch_id}/removed")
def put_textbook_batch_removed(
    textbook_id: str, batch_id: str, removed: bool, session: database_utils.SessionDependable
) -> ApiTextbook:
    textbook = get_by_id(session, db.Textbook, textbook_id)
    batch = get_by_id(session, db.SandboxAdaptationBatch, batch_id)
    assert batch.textbook == textbook
    batch.removed_from_textbook = removed
    return make_api_textbook(textbook)


@api_router.put("/textbook/{textbook_id}/adaptation/{adaptation_id}/removed")
def put_textbook_adaptation_removed(
    textbook_id: str, adaptation_id: str, removed: bool, session: database_utils.SessionDependable
) -> ApiTextbook:
    textbook = get_by_id(session, db.Textbook, textbook_id)
    adaptation = get_by_id(session, db.Adaptation, adaptation_id)
    assert adaptation.sandbox_batch.textbook == textbook
    adaptation.exercise.removed_from_textbook = removed
    return make_api_textbook(textbook)


class PostTextbookExternalExercisesRequest(ApiModel):
    creator: str
    page_number: int | None
    exercise_number: str | None
    original_file_name: str


class PostTextbookExternalExercisesResponse(ApiModel):
    put_url: str


@api_router.post("/textbook/{textbook_id}/external-exercises")
def post_textbook_external_exercises(
    textbook_id: str, req: PostTextbookExternalExercisesRequest, session: database_utils.SessionDependable
) -> PostTextbookExternalExercisesResponse:
    textbook = get_by_id(session, db.Textbook, textbook_id)
    external_exercise = db.ExternalExercise(
        created_at=datetime.datetime.now(datetime.timezone.utc),
        created_by_username=req.creator,
        textbook=textbook,
        removed_from_textbook=False,
        page_number=req.page_number,
        exercise_number=req.exercise_number,
        original_file_name=req.original_file_name,
    )
    session.add(external_exercise)
    session.flush()
    target = urllib.parse.urlparse(f"{settings.EXTERNAL_EXERCISES_URL}/{external_exercise.id}")
    return PostTextbookExternalExercisesResponse(
        put_url=s3.generate_presigned_url(
            "put_object", Params={"Bucket": target.netloc, "Key": target.path[1:]}, ExpiresIn=300
        )
    )


@api_router.put("/textbook/{textbook_id}/external-exercises/{external_exercise_id}/removed")
def put_textbook_external_exercises_removed(
    textbook_id: str, external_exercise_id: str, removed: bool, session: database_utils.SessionDependable
) -> ApiTextbook:
    textbook = get_by_id(session, db.Textbook, textbook_id)
    external_exercise = get_by_id(session, db.ExternalExercise, external_exercise_id)
    assert external_exercise.textbook == textbook
    external_exercise.removed_from_textbook = removed
    return make_api_textbook(textbook)


@api_router.get("/{id}")
async def get_adaptation(id: str, session: database_utils.SessionDependable) -> ApiAdaptation:
    return make_api_adaptation(get_by_id(session, db.Adaptation, id))


class PostAdaptationAdjustmentRequest(ApiModel):
    adjustment: str


@api_router.post("/{id}/adjustment")
async def post_adaptation_adjustment(
    id: str, req: PostAdaptationAdjustmentRequest, session: database_utils.SessionDependable
) -> ApiAdaptation:
    adaptation = get_by_id(session, db.Adaptation, id)
    assert adaptation.initial_assistant_response is not None

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
        llm.SystemMessage(content=adaptation.strategy.settings.system_prompt),
        llm.UserMessage(content=adaptation.exercise.full_text),
        make_assistant_message(adaptation.initial_assistant_response),
    ]
    for adjustment in adaptation.adjustments:
        assert isinstance(adjustment.assistant_response, AssistantSuccess)
        messages.append(llm.UserMessage(content=adjustment.user_prompt))
        make_assistant_message(adjustment.assistant_response)
    messages.append(llm.UserMessage(content=req.adjustment))

    try:
        response = await adaptation.strategy.model.complete(
            messages, adaptation.strategy.settings.response_specification.make_response_format()
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

    raw_llm_conversations = list(adaptation.raw_llm_conversations)
    raw_llm_conversations.append(raw_conversation)
    adaptation.raw_llm_conversations = raw_llm_conversations

    adjustments = list(adaptation.adjustments)
    adjustments.append(Adjustment(user_prompt=req.adjustment, assistant_response=assistant_response))
    adaptation.adjustments = adjustments

    return make_api_adaptation(adaptation)


@api_router.delete("/{id}/last-adjustment")
def delete_adaptation_last_adjustment(id: str, session: database_utils.SessionDependable) -> ApiAdaptation:
    adaptation = get_by_id(session, db.Adaptation, id)

    raw_llm_conversations = list(adaptation.raw_llm_conversations)
    raw_llm_conversations.pop()
    adaptation.raw_llm_conversations = raw_llm_conversations

    adjustments = list(adaptation.adjustments)
    adjustments.pop()
    adaptation.adjustments = adjustments

    return make_api_adaptation(adaptation)


@api_router.put("/{id}/manual-edit")
def put_adaptation_manual_edit(id: str, req: Exercise, session: database_utils.SessionDependable) -> ApiAdaptation:
    adaptation = get_by_id(session, db.Adaptation, id)
    adaptation.manual_edit = req
    return make_api_adaptation(adaptation)


@api_router.delete("/{id}/manual-edit")
def delete_adaptation_manual_edit(id: str, session: database_utils.SessionDependable) -> ApiAdaptation:
    adaptation = get_by_id(session, db.Adaptation, id)
    adaptation.manual_edit = None
    return make_api_adaptation(adaptation)


Model = TypeVar("Model", bound=database_utils.OrmBase)


def get_by_id(session: database_utils.Session, model: type[Model], id: str) -> Model:
    try:
        numerical_id = int(id)
    except ValueError:
        raise fastapi.HTTPException(status_code=404, detail=f"{model.__name__} not found")
    instance = session.get(model, numerical_id)
    if instance is None:
        raise fastapi.HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return instance


def make_api_adaptation(adaptation: db.Adaptation) -> ApiAdaptation:
    return ApiAdaptation(
        id=str(adaptation.id),
        created_by=adaptation.created_by_username,
        batch_id=str(adaptation.sandbox_batch_id),
        strategy=make_api_strategy(adaptation.strategy),
        input=make_api_input(adaptation.exercise),
        raw_llm_conversations=adaptation.raw_llm_conversations,
        initial_assistant_response=adaptation.initial_assistant_response,
        adjustments=adaptation.adjustments,
        manual_edit=adaptation.manual_edit,
        removed_from_textbook=adaptation.exercise.removed_from_textbook,
    )


def make_api_strategy(strategy: db.AdaptationStrategy) -> ApiStrategy:
    return ApiStrategy(model=strategy.model, settings=make_api_strategy_settings(strategy.settings))


def make_api_strategy_settings(settings: db.AdaptationStrategySettings) -> ApiStrategySettings:
    return ApiStrategySettings(
        name=make_api_strategy_settings_name(settings),
        system_prompt=settings.system_prompt,
        response_specification=settings.response_specification,
    )


def make_api_strategy_settings_name(settings: db.AdaptationStrategySettings) -> str | None:
    if settings.exercise_class is None:
        return None
    else:
        assert settings.exercise_class.latest_strategy_settings is not None
        if settings.exercise_class.latest_strategy_settings.id == settings.id:
            return settings.exercise_class.name
        # @todo Move this string manipulation to the frontend. In particular, this will break with i18n.
        elif settings.exercise_class.latest_strategy_settings.parent_id == settings.id:
            return f"{settings.exercise_class.name} (previous version)"
        else:
            return f"{settings.exercise_class.name} (older version)"


def make_api_input(exercise: db.AdaptableExercise) -> ApiInput:
    return ApiInput(page_number=exercise.page_number, exercise_number=exercise.exercise_number, text=exercise.full_text)


def make_api_textbook(textbook: db.Textbook) -> ApiTextbook:
    return ApiTextbook(
        id=str(textbook.id),
        created_by=textbook.created_by_username,
        title=textbook.title,
        batches=[
            ApiTextbook.Batch(
                id=str(batch.id),
                strategy=make_api_strategy(batch.strategy),
                adaptations=[make_api_adaptation(adaptation) for adaptation in batch.adaptations],
                removed_from_textbook=batch.removed_from_textbook,
            )
            for batch in textbook.batches
        ],
        external_exercises=[
            ApiTextbook.ExternalExercise(
                id=str(external_exercise.id),
                page_number=external_exercise.page_number,
                exercise_number=external_exercise.exercise_number,
                original_file_name=external_exercise.original_file_name,
                removed_from_textbook=external_exercise.removed_from_textbook,
            )
            for external_exercise in textbook.exercises
            if isinstance(external_exercise, db.ExternalExercise)  # @todo Filter in DBMS
        ],
    )


export_adaptation_template_file_path = os.path.join(
    os.path.dirname(__file__), "templates", "adaptation-export", "index.html"
)

export_router = fastapi.APIRouter(dependencies=[fastapi.Depends(authentication.auth_param_dependable)])


@export_router.get("/adaptation-{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_adaptation(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    data = make_adapted_exercise_data(get_by_id(session, db.Adaptation, id))
    assert data is not None
    content = render_template(export_adaptation_template_file_path, "ADAPTATION_EXPORT_DATA", data)

    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{data['exerciseId']}.html"'

    return fastapi.responses.HTMLResponse(content=content, headers=headers)


export_batch_template_file_path = os.path.join(os.path.dirname(__file__), "templates", "batch-export", "index.html")


@export_router.get("/batch-{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_batch(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    data = list(
        filter(
            None,
            (
                make_adapted_exercise_data(adaptation)
                for adaptation in get_by_id(session, db.SandboxAdaptationBatch, id).adaptations
            ),
        )
    )

    content = render_template(export_batch_template_file_path, "BATCH_EXPORT_DATA", data)

    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="test-batch-{id}.html"'

    return fastapi.responses.HTMLResponse(content=content, headers=headers)


export_textbook_template_file_path = os.path.join(
    os.path.dirname(__file__), "templates", "textbook-export", "index.html"
)


@export_router.get("/textbook-{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_textbook(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    textbook = get_by_id(session, db.Textbook, id)

    exercises: list[JsonDict] = []
    for exercise in textbook.exercises:
        if not exercise.removed_from_textbook:
            if isinstance(exercise, db.AdaptableExercise):
                if exercise.adaptation is not None:
                    if (
                        exercise.adaptation.sandbox_batch is not None
                        and exercise.adaptation.sandbox_batch.removed_from_textbook
                    ):
                        adapted_exercise_data = None
                    else:
                        adapted_exercise_data = make_adapted_exercise_data(exercise.adaptation)
                if adapted_exercise_data is not None:
                    exercises.append(adapted_exercise_data)
            elif isinstance(exercise, db.ExternalExercise):
                exercises.append(make_external_exercise_data(exercise))
            else:
                assert False

    data = dict(title=textbook.title, exercises=exercises)

    content = render_template(export_textbook_template_file_path, "TEXTBOOK_EXPORT_DATA", data)

    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{textbook.title}.html"'

    return fastapi.responses.HTMLResponse(content=content, headers=headers)


def render_template(template: str, placeholder: str, data: Any) -> str:
    with open(template) as f:
        template = f.read()
    return template.replace(
        f"##TO_BE_SUBSTITUTED_{placeholder}##", json.dumps(data).replace("\\", "\\\\").replace('"', '\\"')
    )


def make_adapted_exercise_data(adaptation: db.Adaptation) -> JsonDict | None:
    if adaptation.exercise.page_number is not None and adaptation.exercise.exercise_number is not None:
        exercise_id = f"P{adaptation.exercise.page_number}Ex{adaptation.exercise.exercise_number}"
    else:
        exercise_id = f"exercice-{adaptation.id}"

    if adaptation.manual_edit is None:
        if len(adaptation.adjustments) == 0:
            if not isinstance(adaptation.initial_assistant_response, AssistantSuccess):
                return None
            adapted_exercise = adaptation.initial_assistant_response.exercise
        else:
            last_adjustment = adaptation.adjustments[-1]
            if not isinstance(last_adjustment.assistant_response, AssistantSuccess):
                return None
            adapted_exercise = last_adjustment.assistant_response.exercise
    else:
        adapted_exercise = adaptation.manual_edit

    adapted_exercise_dump = adapted_exercise.model_dump()
    return {
        "exerciseId": exercise_id,
        "pageNumber": adaptation.exercise.page_number,
        "exerciseNumber": adaptation.exercise.exercise_number,
        "kind": "adapted",
        "studentAnswersStorageKey": hashlib.md5(
            json.dumps(adapted_exercise_dump, separators=(",", ":"), indent=None).encode()
        ).hexdigest(),
        "adaptedExercise": adapted_exercise_dump,
    }


def make_external_exercise_data(external_exercise: db.ExternalExercise) -> JsonDict:
    assert external_exercise.page_number is not None and external_exercise.exercise_number is not None
    exercise_id = f"P{external_exercise.page_number}Ex{external_exercise.exercise_number}"
    target = urllib.parse.urlparse(f"{settings.EXTERNAL_EXERCISES_URL}/{external_exercise.id}")
    # @todo Download asynchronously from S3
    object = s3.get_object(Bucket=target.netloc, Key=target.path[1:])
    data = base64.b64encode(object["Body"].read()).decode("ascii")
    return {
        "exerciseId": exercise_id,
        "pageNumber": external_exercise.page_number,
        "exerciseNumber": external_exercise.exercise_number,
        "kind": "external",
        "originalFileName": external_exercise.original_file_name,
        "data": data,
    }


router = fastapi.APIRouter()
router.include_router(api_router)
router.include_router(export_router, prefix="/export")


class AdaptationApiTestCase(database_utils.TestCaseWithDatabase):
    def setUp(self) -> None:
        super().setUp()
        self.app = fastapi.FastAPI(database_engine=self.engine)
        self.app.include_router(router)
        access_token = authentication.login(authentication.PostTokenRequest(password="password")).access_token
        self.client = fastapi.testclient.TestClient(self.app, headers={"Authorization": f"Bearer {access_token}"})

    def test_get_no_textbooks(self) -> None:
        self.assertEqual(self.client.get("/textbooks").json(), {"textbooks": []})
