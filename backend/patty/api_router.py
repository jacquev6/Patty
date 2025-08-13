from collections.abc import Iterable
from typing import Any, Literal, TypeVar
import base64
import datetime
import hashlib
import json
import os
import typing
import urllib.parse

import boto3
import botocore.client
import fastapi
import fastapi.testclient
import requests
import sqlalchemy as sql

from . import authentication
from . import database_utils
from . import extracted
from . import settings
from .adaptation import llm as adaptation_llm
from .adaptation import orm_models as adaptation_orm_models
from .adaptation.strategy import ConcreteLlmResponseSpecification, JsonSchemaLlmResponseSpecification
from .adapted import Exercise
from .any_json import JsonDict, JsonList
from .api_utils import ApiModel
from .adaptation.responses import (
    Adjustment,
    AssistantInvalidJsonError,
    AssistantNotJsonError,
    AssistantResponse,
    AssistantSuccess,
)
from .adaptation.submission import LlmMessage
from .classification import orm_models as classification_orm_models
from .errors import orm_models as errors_orm_models
from .exercises import orm_models as exercises_orm_models
from .external_exercises import orm_models as external_exercises_orm_models
from .extraction import assistant_responses as extraction_responses
from .extraction import llm as extraction_llm
from .extraction import orm_models as extraction_orm_models
from .mailing import send_mail
from .version import PATTY_VERSION
from .textbooks import orm_models as textbooks_orm_models

__all__ = ["api_router", "export_router"]

s3 = boto3.client("s3", config=botocore.client.Config(region_name="eu-west-3", signature_version="s3v4"))

api_router = fastapi.APIRouter(dependencies=[fastapi.Depends(authentication.auth_bearer_dependable)])


T1 = TypeVar("T1")


def assert_isinstance(value: Any, type_: type[T1]) -> T1:
    assert isinstance(value, type_)
    return value


class PostErrorsCaughtByFrontendRequest(ApiModel):
    creator: str | None
    user_agent: str
    window_size: str
    url: str
    caught_by: str
    message: str
    code_location: str | None


class PostErrorsCaughtByFrontendResponse(ApiModel):
    pass


@api_router.post("/errors-caught-by-frontend")
def post_errors_caught_by_frontend(
    req: PostErrorsCaughtByFrontendRequest, session: database_utils.SessionDependable
) -> PostErrorsCaughtByFrontendResponse:
    if PATTY_VERSION != "dev":
        send_mail(
            to=settings.MAIL_SENDER,
            subject=f"Patty version {PATTY_VERSION}: error caught by frontend",
            body=req.model_dump_json(indent=2),
        )
    session.add(
        errors_orm_models.ErrorCaughtByFrontend(
            created_at=datetime.datetime.now(datetime.timezone.utc),
            created_by_username=req.creator,
            patty_version=PATTY_VERSION,
            user_agent=req.user_agent,
            window_size=req.window_size,
            url=req.url,
            caught_by=req.caught_by,
            message=req.message,
            code_location=req.code_location,
        )
    )
    return PostErrorsCaughtByFrontendResponse()


class GetErrorsCaughtByFrontendResponse(ApiModel):
    class Error(ApiModel):
        id: str
        created_by: str | None
        created_at: datetime.datetime
        patty_version: str
        user_agent: str
        window_size: str
        url: str
        caught_by: str
        message: str
        code_location: str | None

    errors: list[Error]


@api_router.get("/errors-caught-by-frontend")
def get_errors_caught_by_frontend(session: database_utils.SessionDependable) -> GetErrorsCaughtByFrontendResponse:
    return GetErrorsCaughtByFrontendResponse(
        errors=[
            GetErrorsCaughtByFrontendResponse.Error(
                id=str(error.id),
                created_by=error.created_by_username,
                created_at=error.created_at,
                patty_version=error.patty_version,
                user_agent=error.user_agent,
                window_size=error.window_size,
                url=error.url,
                caught_by=error.caught_by,
                message=error.message,
                code_location=error.code_location,
            )
            for error in session.execute(
                sql.select(errors_orm_models.ErrorCaughtByFrontend).order_by(
                    -errors_orm_models.ErrorCaughtByFrontend.id
                )
            )
            .scalars()
            .all()
        ]
    )


@api_router.get("/available-adaptation-llm-models")
def get_available_adaptation_llm_models() -> list[adaptation_llm.ConcreteModel]:
    if PATTY_VERSION == "dev":
        return [
            adaptation_llm.DummyModel(provider="dummy", name="dummy-1"),
            adaptation_llm.DummyModel(provider="dummy", name="dummy-2"),
            adaptation_llm.DummyModel(provider="dummy", name="dummy-3"),
            adaptation_llm.MistralAiModel(provider="mistralai", name="mistral-large-2411"),
            adaptation_llm.MistralAiModel(provider="mistralai", name="mistral-small-2501"),
            adaptation_llm.OpenAiModel(provider="openai", name="gpt-4o-2024-08-06"),
            adaptation_llm.OpenAiModel(provider="openai", name="gpt-4o-mini-2024-07-18"),
        ]
    else:
        return [
            adaptation_llm.MistralAiModel(provider="mistralai", name="mistral-large-2411"),
            adaptation_llm.MistralAiModel(provider="mistralai", name="mistral-small-2501"),
            adaptation_llm.OpenAiModel(provider="openai", name="gpt-4o-2024-08-06"),
            adaptation_llm.OpenAiModel(provider="openai", name="gpt-4o-mini-2024-07-18"),
            adaptation_llm.DummyModel(provider="dummy", name="dummy-1"),
            adaptation_llm.DummyModel(provider="dummy", name="dummy-2"),
        ]


class ApiStrategySettings(ApiModel):
    name: str | None
    system_prompt: str
    response_specification: ConcreteLlmResponseSpecification


class ApiStrategy(ApiModel):
    model: adaptation_llm.ConcreteModel
    settings: ApiStrategySettings


class ApiInput(ApiModel):
    page_number: int | None
    exercise_number: str | None
    text: str


class ApiAdaptation(ApiModel):
    id: str
    extraction_batch_id: str | None
    classification_batch_id: str | None
    adaptation_batch_id: str | None
    strategy: ApiStrategy
    input: ApiInput
    raw_llm_conversations: JsonList
    initial_assistant_response: AssistantResponse | None
    adjustments: list[Adjustment]
    manual_edit: Exercise | None
    removed_from_textbook: bool


@api_router.post("/adaptation-llm-response-schema")
def make_adaptation_llm_response_schema(response_specification: JsonSchemaLlmResponseSpecification) -> JsonDict:
    return response_specification.make_response_schema()


class BaseAdaptationBatch(ApiModel):
    id: str
    strategy: ApiStrategy
    inputs: list[ApiInput]
    available_strategy_settings: list[ApiStrategySettings]


@api_router.get("/base-adaptation-batch")
def get_base_adaptation_batch(
    user: str, session: database_utils.SessionDependable, base: str | None = None
) -> BaseAdaptationBatch:
    request = sql.select(adaptation_orm_models.SandboxAdaptationBatch)
    if base is None:
        request = request.where(
            (adaptation_orm_models.SandboxAdaptationBatch.created_by == user)
            | (adaptation_orm_models.SandboxAdaptationBatch.id == 1)
        ).order_by(-adaptation_orm_models.SandboxAdaptationBatch.id)
    else:
        try:
            base_id = int(base)
        except ValueError:
            raise fastapi.HTTPException(status_code=404, detail="Base adaptation batch not found")
        else:
            request = request.where(adaptation_orm_models.SandboxAdaptationBatch.id == base_id)

    adaptation_batch = session.execute(request).scalars().first()
    if adaptation_batch is None:
        raise fastapi.HTTPException(status_code=404, detail="Base adaptation batch not found")

    available_strategy_settings = []
    for exercise_class in (
        session.execute(
            sql.select(adaptation_orm_models.ExerciseClass)
            .where(adaptation_orm_models.ExerciseClass.latest_strategy_settings != sql.null())
            .order_by(adaptation_orm_models.ExerciseClass.name)
        )
        .scalars()
        .all()
    ):
        assert exercise_class.latest_strategy_settings is not None
        available_strategy_settings.append(make_api_strategy_settings(exercise_class.latest_strategy_settings))
        if exercise_class.latest_strategy_settings.parent is not None:
            available_strategy_settings.append(
                make_api_strategy_settings(exercise_class.latest_strategy_settings.parent)
            )
    return BaseAdaptationBatch(
        id=str(adaptation_batch.id),
        strategy=make_api_strategy(adaptation_batch.settings, adaptation_batch.model),
        inputs=[
            make_api_input(adaptation_creation.exercise_adaptation.exercise)
            for adaptation_creation in adaptation_batch.adaptation_creations
        ],
        available_strategy_settings=available_strategy_settings,
    )


class PostAdaptationBatchRequest(ApiModel):
    creator: str
    strategy: ApiStrategy
    inputs: list[ApiInput]


class PostAdaptationBatchResponse(ApiModel):
    id: str


@api_router.post("/adaptation-batches")
async def post_adaptation_batch(
    req: PostAdaptationBatchRequest, session: database_utils.SessionDependable
) -> PostAdaptationBatchResponse:
    now = datetime.datetime.now(datetime.timezone.utc)

    if req.strategy.settings.name is None:
        base_settings = None
        exercise_class = None
    else:
        # @todo Move this string manipulation to the frontend. In particular, this will break with i18n.
        if req.strategy.settings.name.endswith(" (previous version)"):
            branch_name = req.strategy.settings.name[:-19]
        elif req.strategy.settings.name.endswith(" (older version)"):
            branch_name = req.strategy.settings.name[:-16]
        else:
            branch_name = req.strategy.settings.name
        exercise_class = (
            session.query(adaptation_orm_models.ExerciseClass)
            .filter(adaptation_orm_models.ExerciseClass.name == branch_name)
            .first()
        )
        if exercise_class is None:
            assert branch_name == req.strategy.settings.name
            base_settings = None
            exercise_class = adaptation_orm_models.ExerciseClass(
                created=classification_orm_models.ExerciseClassCreationByUser(at=now, username=req.creator),
                name=branch_name,
                latest_strategy_settings=None,
            )
            session.add(exercise_class)
        else:
            if exercise_class.latest_strategy_settings is None:
                base_settings = None
            elif branch_name == req.strategy.settings.name:
                base_settings = exercise_class.latest_strategy_settings
            else:
                base_settings = exercise_class.latest_strategy_settings.parent

    if (
        base_settings is None
        or base_settings.system_prompt != req.strategy.settings.system_prompt
        or base_settings.response_specification != req.strategy.settings.response_specification
    ):
        settings = adaptation_orm_models.ExerciseAdaptationSettings(
            exercise_class=exercise_class,
            parent=base_settings,
            created_by=req.creator,
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

    adaptation_batch = adaptation_orm_models.SandboxAdaptationBatch(
        created_by=req.creator, created_at=now, settings=settings, model=req.strategy.model
    )
    session.add(adaptation_batch)

    for req_input in req.inputs:
        exercise = adaptation_orm_models.AdaptableExercise(
            created=exercises_orm_models.ExerciseCreationByUser(at=now, username=req.creator),
            location=exercises_orm_models.ExerciseLocationMaybePageAndNumber(
                page_number=req_input.page_number, exercise_number=req_input.exercise_number
            ),
            removed_from_textbook=False,
            full_text=req_input.text,
            instruction_hint_example_text=None,
            statement_text=None,
        )
        session.add(exercise)

        if exercise_class is not None:
            session.add(
                classification_orm_models.ExerciseClassificationByUser(
                    exercise=exercise, at=now, username=req.creator, exercise_class=exercise_class
                )
            )

        adaptation = adaptation_orm_models.ExerciseAdaptation(
            created=adaptation_orm_models.ExerciseAdaptationCreationBySandboxAdaptationBatch(
                at=now, sandbox_adaptation_batch=adaptation_batch
            ),
            settings=settings,
            model=req.strategy.model,
            exercise=exercise,
            raw_llm_conversations=[],
            initial_assistant_response=None,
            adjustments=[],
            manual_edit=None,
        )
        session.add(adaptation)

    session.flush()

    return PostAdaptationBatchResponse(id=str(adaptation_batch.id))


class GetAdaptationBatchResponse(ApiModel):
    id: str
    created_by: str
    strategy: ApiStrategy
    adaptations: list[ApiAdaptation]


@api_router.get("/adaptation-batches/{id}")
async def get_adaptation_batch(id: str, session: database_utils.SessionDependable) -> GetAdaptationBatchResponse:
    adaptation_batch = get_by_id(session, adaptation_orm_models.SandboxAdaptationBatch, id)
    return GetAdaptationBatchResponse(
        id=str(adaptation_batch.id),
        created_by=adaptation_batch.created_by,
        strategy=make_api_strategy(adaptation_batch.settings, adaptation_batch.model),
        adaptations=[
            make_api_adaptation(adaptation_creation.exercise_adaptation)
            for adaptation_creation in adaptation_batch.adaptation_creations
        ],
    )


class GetAdaptationBatchesResponse(ApiModel):
    class AdaptationBatch(ApiModel):
        id: str
        created_by: str
        created_at: datetime.datetime
        model: adaptation_llm.ConcreteModel
        strategy_settings_name: str | None

    adaptation_batches: list[AdaptationBatch]
    next_chunk_id: str | None


@api_router.get("/exercise-classes")
def get_exercise_classes(session: database_utils.SessionDependable) -> list[str]:
    request = sql.select(adaptation_orm_models.ExerciseClass).order_by(adaptation_orm_models.ExerciseClass.name)
    return [exercise_class.name for exercise_class in session.execute(request).scalars().all()]


class PutAdaptableExerciseClassRequest(ApiModel):
    creator: str
    className: str


@api_router.put("/adaptable-exercises/{id}/exercise-class")
def put_adaptable_exercise_class(
    id: str, req: PutAdaptableExerciseClassRequest, session: database_utils.SessionDependable
) -> None:
    now = datetime.datetime.now(datetime.timezone.utc)
    exercise = get_by_id(session, adaptation_orm_models.AdaptableExercise, id)
    exercise_class = (
        session.query(adaptation_orm_models.ExerciseClass)
        .filter(adaptation_orm_models.ExerciseClass.name == req.className)
        .first()
    )
    if exercise_class is None:
        raise fastapi.HTTPException(status_code=404, detail="Exercise class not found")

    if len(exercise.adaptations) != 0:
        adaptation_model: adaptation_llm.ConcreteModel | None = exercise.adaptations[-1].model
    elif len(exercise.classifications) != 0 and isinstance(
        exercise.classifications[-1], classification_orm_models.ExerciseClassificationByClassificationChunk
    ):
        adaptation_model = exercise.classifications[-1].classification_chunk.model_for_adaptation
    else:
        adaptation_model = None

    session.add(
        classification_orm_models.ExerciseClassificationByUser(
            exercise=exercise, at=now, username=req.creator, exercise_class=exercise_class
        )
    )

    if adaptation_model is not None and exercise_class.latest_strategy_settings is not None:
        session.add(
            adaptation_orm_models.ExerciseAdaptation(
                created=adaptation_orm_models.ExerciseAdaptationCreationByUser(at=now, username=req.creator),
                settings=exercise_class.latest_strategy_settings,
                model=adaptation_model,
                exercise=exercise,
                raw_llm_conversations=[],
                initial_assistant_response=None,
                adjustments=[],
                manual_edit=None,
            )
        )


T = typing.TypeVar(
    "T",
    bound=adaptation_orm_models.SandboxAdaptationBatch
    | classification_orm_models.SandboxClassificationBatch
    | extraction_orm_models.SandboxExtractionBatch,
)


def paginate(
    model: type[T], session: database_utils.SessionDependable, chunk_id: str | None
) -> tuple[list[T], str | None]:
    chunk_size = 20
    request = sql.select(model).order_by(-model.id).limit(chunk_size + 1)

    if chunk_id is not None:
        try:
            numerical_chunk_id = int(chunk_id)
        except ValueError:
            raise fastapi.HTTPException(status_code=400, detail="Invalid chunk ID")
        request = request.filter(model.id < numerical_chunk_id)

    batches = list(session.execute(request).scalars().all())

    if len(batches) <= chunk_size:
        next_chunk_id = None
    else:
        next_chunk_id = str(batches[-2].id)

    return batches[:chunk_size], next_chunk_id


@api_router.get("/adaptation-batches")
async def get_adaptation_batches(
    session: database_utils.SessionDependable, chunkId: str | None = None
) -> GetAdaptationBatchesResponse:
    (batches, next_chunk_id) = paginate(adaptation_orm_models.SandboxAdaptationBatch, session, chunkId)

    return GetAdaptationBatchesResponse(
        adaptation_batches=[
            GetAdaptationBatchesResponse.AdaptationBatch(
                id=str(adaptation_batch.id),
                created_by=adaptation_batch.created_by,
                created_at=adaptation_batch.created_at,
                model=adaptation_batch.model,
                strategy_settings_name=make_api_strategy_settings_name(adaptation_batch.settings),
            )
            for adaptation_batch in batches
        ],
        next_chunk_id=next_chunk_id,
    )


class ClassificationInput(ApiModel):
    page_number: int | None
    exercise_number: str | None
    instruction_hint_example_text: str
    statement_text: str


class PostClassificationBatchRequest(ApiModel):
    creator: str
    inputs: list[ClassificationInput]
    model_for_adaptation: adaptation_llm.ConcreteModel | None


class PostClassificationBatchResponse(ApiModel):
    id: str


@api_router.post("/classification-batches")
def create_classification_batch(
    req: PostClassificationBatchRequest, session: database_utils.SessionDependable
) -> PostClassificationBatchResponse:
    now = datetime.datetime.now(datetime.timezone.utc)
    classification_batch = classification_orm_models.SandboxClassificationBatch(
        created_by=req.creator, created_at=now, model_for_adaptation=req.model_for_adaptation
    )
    session.add(classification_batch)

    classification_chunk = classification_orm_models.ExerciseClassificationChunk(
        created=classification_orm_models.ExerciseClassificationChunkCreationBySandboxClassificationBatch(
            at=now, sandbox_classification_batch=classification_batch
        ),
        model_for_adaptation=req.model_for_adaptation,
    )
    session.add(classification_chunk)

    for req_input in req.inputs:
        exercise = adaptation_orm_models.AdaptableExercise(
            created=exercises_orm_models.ExerciseCreationByUser(at=now, username=req.creator),
            location=exercises_orm_models.ExerciseLocationMaybePageAndNumber(
                page_number=req_input.page_number, exercise_number=req_input.exercise_number
            ),
            removed_from_textbook=False,
            full_text=req_input.instruction_hint_example_text + "\n" + req_input.statement_text,
            instruction_hint_example_text=req_input.instruction_hint_example_text,
            statement_text=req_input.statement_text,
        )
        session.add(exercise)
        session.add(
            classification_orm_models.ExerciseClassificationByClassificationChunk(
                at=now, exercise=exercise, classification_chunk=classification_chunk, exercise_class=None
            )
        )

    session.flush()

    return PostClassificationBatchResponse(id=str(classification_batch.id))


class GetClassificationBatchResponse(ApiModel):
    id: str
    created_by: str | None
    model_for_adaptation: adaptation_llm.ConcreteModel | None

    class Exercise(ApiModel):
        id: str
        page_number: int | None
        exercise_number: str | None
        full_text: str
        exercise_class: str | None
        reclassified_by: str | None
        exercise_class_has_settings: bool
        adaptation: ApiAdaptation | None

    exercises: list[Exercise]


@api_router.get("/classification-batches/{id}")
async def get_classification_batch(
    id: str, session: database_utils.SessionDependable
) -> GetClassificationBatchResponse:
    classification_batch = get_by_id(session, classification_orm_models.SandboxClassificationBatch, id)

    exercises = [
        classification.exercise
        for classification in classification_batch.classification_chunk_creation.classification_chunk.classifications
    ]

    latest_classifications = [
        exercise.classifications[-1] if exercise.classifications else None for exercise in exercises
    ]

    latest_adaptations = [
        (
            None
            if latest_classification is None or latest_classification.exercise_class is None
            else exercise.fetch_latest_adaptation(latest_classification.exercise_class)
        )
        for (exercise, latest_classification) in zip(exercises, latest_classifications)
    ]

    return GetClassificationBatchResponse(
        id=str(classification_batch.id),
        created_by=classification_batch.created_by,
        model_for_adaptation=classification_batch.model_for_adaptation,
        exercises=[
            GetClassificationBatchResponse.Exercise(
                id=str(exercise.id),
                page_number=assert_isinstance(
                    exercise.location, exercises_orm_models.ExerciseLocationMaybePageAndNumber
                ).page_number,
                exercise_number=assert_isinstance(
                    exercise.location, exercises_orm_models.ExerciseLocationMaybePageAndNumber
                ).exercise_number,
                full_text=exercise.full_text,
                exercise_class=(
                    latest_classification.exercise_class.name
                    if latest_classification is not None and latest_classification.exercise_class is not None
                    else None
                ),
                reclassified_by=(
                    latest_classification.username
                    if isinstance(latest_classification, classification_orm_models.ExerciseClassificationByUser)
                    else None
                ),
                exercise_class_has_settings=(
                    latest_classification is not None
                    and latest_classification.exercise_class is not None
                    and latest_classification.exercise_class.latest_strategy_settings is not None
                ),
                adaptation=None if latest_adaptation is None else make_api_adaptation(latest_adaptation),
            )
            for (exercise, latest_classification, latest_adaptation) in zip(
                exercises, latest_classifications, latest_adaptations
            )
        ],
    )


@api_router.post(
    "/classification-batches/{id}/submit-adaptations-with-recent-settings", status_code=fastapi.status.HTTP_200_OK
)
def submit_adaptations_with_recent_settings_in_classification_batch(
    id: str, session: database_utils.SessionDependable
) -> None:
    classification_batch = get_by_id(session, classification_orm_models.SandboxClassificationBatch, id)
    assert classification_batch.model_for_adaptation is not None
    now = datetime.datetime.now(datetime.timezone.utc)
    classification_chunk = classification_batch.classification_chunk_creation.classification_chunk
    for classification in classification_chunk.classifications:
        exercise = classification.exercise
        if (
            len(exercise.adaptations) == 0
            and classification.exercise_class is not None
            and classification.exercise_class.latest_strategy_settings is not None
        ):
            session.add(
                adaptation_orm_models.ExerciseAdaptation(
                    created=classification_orm_models.ExerciseAdaptationCreationByClassificationChunk(
                        at=now, classification_chunk=classification_chunk
                    ),
                    exercise=exercise,
                    settings=classification.exercise_class.latest_strategy_settings,
                    model=classification_batch.model_for_adaptation,
                    raw_llm_conversations=[],
                    initial_assistant_response=None,
                    adjustments=[],
                    manual_edit=None,
                )
            )


@api_router.put("/classification-batches/{id}/model-for-adaptation", status_code=fastapi.status.HTTP_200_OK)
def put_classification_batch_model_for_adaptation(
    id: str, req: adaptation_llm.ConcreteModel, session: database_utils.SessionDependable
) -> None:
    classification_batch = get_by_id(session, classification_orm_models.SandboxClassificationBatch, id)
    assert classification_batch.model_for_adaptation is None
    classification_batch.model_for_adaptation = req
    now = datetime.datetime.now(datetime.timezone.utc)
    classification_chunk = classification_batch.classification_chunk_creation.classification_chunk
    classification_chunk.model_for_adaptation = req
    for classification in classification_chunk.classifications:
        exercise = classification.exercise
        if (
            len(exercise.adaptations) == 0
            and classification.exercise_class is not None
            and classification.exercise_class.latest_strategy_settings is not None
        ):
            session.add(
                adaptation_orm_models.ExerciseAdaptation(
                    created=classification_orm_models.ExerciseAdaptationCreationByClassificationChunk(
                        at=now, classification_chunk=classification_chunk
                    ),
                    exercise=exercise,
                    settings=classification.exercise_class.latest_strategy_settings,
                    model=classification_batch.model_for_adaptation,
                    raw_llm_conversations=[],
                    initial_assistant_response=None,
                    adjustments=[],
                    manual_edit=None,
                )
            )


class GetClassificationBatchesResponse(ApiModel):
    class ClassificationBatch(ApiModel):
        id: str
        created_by: str | None
        created_at: datetime.datetime

    classification_batches: list[ClassificationBatch]
    next_chunk_id: str | None


@api_router.get("/classification-batches")
async def get_classification_batches(
    session: database_utils.SessionDependable, chunkId: str | None = None
) -> GetClassificationBatchesResponse:
    (batches, next_chunk_id) = paginate(classification_orm_models.SandboxClassificationBatch, session, chunkId)

    return GetClassificationBatchesResponse(
        classification_batches=[
            GetClassificationBatchesResponse.ClassificationBatch(
                id=str(classification_batch.id),
                created_by=classification_batch.created_by,
                created_at=classification_batch.created_at,
            )
            for classification_batch in batches
        ],
        next_chunk_id=next_chunk_id,
    )


class CreatePdfFileRequest(ApiModel):
    creator: str
    file_name: str
    bytes_count: int
    pages_count: int
    sha256: str


class CreatePdfFileResponse(ApiModel):
    upload_url: str | None


@api_router.post("/pdf-files")
def create_pdf_file(req: CreatePdfFileRequest, session: database_utils.SessionDependable) -> CreatePdfFileResponse:
    now = datetime.datetime.now(datetime.timezone.utc)
    pdf_file = session.get(extraction_orm_models.PdfFile, req.sha256)
    if pdf_file is None:
        pdf_file = extraction_orm_models.PdfFile(
            sha256=req.sha256,
            created_by=req.creator,
            created_at=now,
            bytes_count=req.bytes_count,
            pages_count=req.pages_count,
            known_file_names=[],
        )
        session.add(pdf_file)

    if req.file_name not in pdf_file.known_file_names:
        pdf_file.known_file_names = pdf_file.known_file_names + [req.file_name]

    target = urllib.parse.urlparse(f"{settings.PDF_FILES_URL}/{pdf_file.sha256}")
    try:
        s3.head_object(Bucket=target.netloc, Key=target.path[1:])
    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "404":
            upload_url = s3.generate_presigned_url(
                "put_object", Params={"Bucket": target.netloc, "Key": target.path[1:]}, ExpiresIn=300
            )
        else:
            raise
    else:
        upload_url = None

    return CreatePdfFileResponse(upload_url=upload_url)


@api_router.get("/extraction-llm-response-schema")
def get_extraction_llm_response_schema() -> JsonDict:
    return extracted.ExercisesList.model_json_schema()


@api_router.get("/available-extraction-llm-models")
def get_available_extraction_llm_models() -> list[extraction_llm.ConcreteModel]:
    if PATTY_VERSION == "dev":
        return [
            extraction_llm.DummyModel(provider="dummy", name="dummy-1"),
            extraction_llm.DummyModel(provider="dummy", name="dummy-2"),
            extraction_llm.GeminiModel(provider="gemini", name="gemini-2.0-flash"),
        ]
    else:
        return [
            extraction_llm.GeminiModel(provider="gemini", name="gemini-2.0-flash"),
            extraction_llm.DummyModel(provider="dummy", name="dummy-1"),
            extraction_llm.DummyModel(provider="dummy", name="dummy-2"),
        ]


class ApiExtractionStrategy(ApiModel):
    id: str
    model: extraction_llm.ConcreteModel
    prompt: str


@api_router.get("/latest-extraction-strategy")
def get_latest_extraction_strategy(session: database_utils.SessionDependable) -> ApiExtractionStrategy:
    settings = (
        session.execute(
            sql.select(extraction_orm_models.ExtractionSettings).order_by(-extraction_orm_models.ExtractionSettings.id)
        )
        .scalars()
        .first()
    )
    assert settings is not None
    if PATTY_VERSION == "dev":
        model: extraction_llm.ConcreteModel = extraction_llm.DummyModel(provider="dummy", name="dummy-1")
    else:
        model = extraction_llm.GeminiModel(provider="gemini", name="gemini-2.0-flash")
    return ApiExtractionStrategy(id=str(settings.id), model=model, prompt=settings.prompt)


class PostExtractionBatchRequest(ApiModel):
    creator: str
    pdf_file_sha256: str
    first_page: int
    pages_count: int
    strategy: ApiExtractionStrategy
    run_classification: bool
    model_for_adaptation: adaptation_llm.ConcreteModel | None


class PostExtractionBatchResponse(ApiModel):
    id: str


@api_router.post("/extraction-batches")
def create_extraction_batch(
    req: PostExtractionBatchRequest, session: database_utils.SessionDependable
) -> PostExtractionBatchResponse:
    now = datetime.datetime.now(datetime.timezone.utc)
    pdf_file = session.get(extraction_orm_models.PdfFile, req.pdf_file_sha256)
    if pdf_file is None:
        raise fastapi.HTTPException(status_code=404, detail="PDF file not found")
    pdf_file_range = extraction_orm_models.PdfFileRange(
        created_by=req.creator,
        created_at=now,
        pdf_file=pdf_file,
        first_page_number=req.first_page,
        pages_count=req.pages_count,
    )
    session.add(pdf_file_range)
    settings = session.get(extraction_orm_models.ExtractionSettings, req.strategy.id)
    if settings is None or settings.prompt != req.strategy.prompt:
        settings = extraction_orm_models.ExtractionSettings(
            created_by=req.creator, created_at=now, prompt=req.strategy.prompt
        )
        session.add(settings)
    model = req.strategy.model
    extraction_batch = extraction_orm_models.SandboxExtractionBatch(
        created_by=req.creator,
        created_at=now,
        settings=settings,
        model=model,
        pdf_range=pdf_file_range,
        run_classification=req.run_classification,
        model_for_adaptation=req.model_for_adaptation,
    )
    session.add(extraction_batch)
    for page_number in range(req.first_page, req.first_page + req.pages_count):
        page = extraction_orm_models.PageExtraction(
            created=extraction_orm_models.PageExtractionCreationBySandboxExtractionBatch(
                at=now, sandbox_extraction_batch=extraction_batch
            ),
            pdf_range=pdf_file_range,
            pdf_page_number=page_number,
            settings=settings,
            model=model,
            run_classification=req.run_classification,
            model_for_adaptation=req.model_for_adaptation,
            assistant_response=None,
        )
        session.add(page)

    session.flush()

    return PostExtractionBatchResponse(id=str(extraction_batch.id))


class GetExtractionBatchResponse(ApiModel):
    id: str
    created_by: str
    strategy: ApiExtractionStrategy
    run_classification: bool
    model_for_adaptation: adaptation_llm.ConcreteModel | None

    class Page(ApiModel):
        page_number: int
        assistant_response: extraction_responses.AssistantResponse | None

        class Exercise(ApiModel):
            id: str
            page_number: int | None
            exercise_number: str | None
            full_text: str
            exercise_class: str | None
            reclassified_by: str | None
            exercise_class_has_settings: bool
            adaptation: ApiAdaptation | None

        exercises: list[Exercise]

    pages: list[Page]


@api_router.get("/extraction-batches/{id}")
async def get_extraction_batch(id: str, session: database_utils.SessionDependable) -> GetExtractionBatchResponse:
    extraction_batch = get_by_id(session, extraction_orm_models.SandboxExtractionBatch, id)
    pages: list[GetExtractionBatchResponse.Page] = []

    for page_extraction_creation in extraction_batch.page_extraction_creations:
        page_extraction = page_extraction_creation.page_extraction

        exercises = list(page_extraction.fetch_ordered_exercises())

        latest_classifications = [
            exercise.classifications[-1] if exercise.classifications else None for exercise in exercises
        ]

        latest_adaptations = [
            (
                None
                if latest_classification is None or latest_classification.exercise_class is None
                else exercise.fetch_latest_adaptation(latest_classification.exercise_class)
            )
            for (exercise, latest_classification) in zip(exercises, latest_classifications)
        ]

        pages.append(
            GetExtractionBatchResponse.Page(
                page_number=page_extraction.pdf_page_number,
                assistant_response=page_extraction.assistant_response,
                exercises=[
                    GetExtractionBatchResponse.Page.Exercise(
                        id=str(exercise.id),
                        page_number=assert_isinstance(
                            exercise.location, exercises_orm_models.ExerciseLocationMaybePageAndNumber
                        ).page_number,
                        exercise_number=assert_isinstance(
                            exercise.location, exercises_orm_models.ExerciseLocationMaybePageAndNumber
                        ).exercise_number,
                        full_text=exercise.full_text,
                        exercise_class=(
                            latest_classification.exercise_class.name
                            if latest_classification is not None and latest_classification.exercise_class is not None
                            else None
                        ),
                        reclassified_by=(
                            latest_classification.username
                            if isinstance(latest_classification, classification_orm_models.ExerciseClassificationByUser)
                            else None
                        ),
                        exercise_class_has_settings=(
                            latest_classification is not None
                            and latest_classification.exercise_class is not None
                            and latest_classification.exercise_class.latest_strategy_settings is not None
                        ),
                        adaptation=None if latest_adaptation is None else make_api_adaptation(latest_adaptation),
                    )
                    for exercise, latest_classification, latest_adaptation in zip(
                        exercises, latest_classifications, latest_adaptations
                    )
                ],
            )
        )

    return GetExtractionBatchResponse(
        id=str(extraction_batch.id),
        created_by=extraction_batch.created_by,
        strategy=ApiExtractionStrategy(
            id=str(extraction_batch.settings.id), model=extraction_batch.model, prompt=extraction_batch.settings.prompt
        ),
        run_classification=extraction_batch.run_classification,
        model_for_adaptation=extraction_batch.model_for_adaptation,
        pages=pages,
    )


@api_router.post(
    "/extraction-batches/{id}/submit-adaptations-with-recent-settings", status_code=fastapi.status.HTTP_200_OK
)
def submit_adaptations_with_recent_settings_in_extraction_batch(
    id: str, session: database_utils.SessionDependable
) -> None:
    extraction_batch = get_by_id(session, extraction_orm_models.SandboxExtractionBatch, id)
    assert extraction_batch.model_for_adaptation is not None
    now = datetime.datetime.now(datetime.timezone.utc)
    for page_extraction_creation in extraction_batch.page_extraction_creations:
        page_extraction = page_extraction_creation.page_extraction
        classification_chunk = (
            session.execute(
                sql.select(classification_orm_models.ExerciseClassificationChunk)
                .join(extraction_orm_models.ExerciseClassificationChunkCreationByPageExtraction)
                .where(
                    extraction_orm_models.ExerciseClassificationChunkCreationByPageExtraction.page_extraction
                    == page_extraction
                )
            )
            .scalars()
            .first()
        )
        assert classification_chunk is not None
        assert classification_chunk.model_for_adaptation is not None
        for exercise_creation in page_extraction.exercise_creations__unordered:
            exercise = exercise_creation.exercise
            assert isinstance(exercise, adaptation_orm_models.AdaptableExercise)

            classification = exercise.classifications[-1]
            assert isinstance(classification, classification_orm_models.ExerciseClassificationByClassificationChunk)
            assert classification.classification_chunk == classification_chunk

            if (
                len(exercise.adaptations) == 0
                and classification.exercise_class is not None
                and classification.exercise_class.latest_strategy_settings is not None
            ):
                session.add(
                    adaptation_orm_models.ExerciseAdaptation(
                        created=classification_orm_models.ExerciseAdaptationCreationByClassificationChunk(
                            at=now, classification_chunk=classification_chunk
                        ),
                        exercise=exercise,
                        settings=classification.exercise_class.latest_strategy_settings,
                        model=classification_chunk.model_for_adaptation,
                        raw_llm_conversations=[],
                        initial_assistant_response=None,
                        adjustments=[],
                        manual_edit=None,
                    )
                )


@api_router.put("/extraction-batches/{id}/run-classification", status_code=fastapi.status.HTTP_200_OK)
def put_extraction_batch_run_classification(id: str, session: database_utils.SessionDependable) -> None:
    extraction_batch = get_by_id(session, extraction_orm_models.SandboxExtractionBatch, id)
    assert extraction_batch.run_classification is False
    extraction_batch.run_classification = True
    now = datetime.datetime.now(datetime.timezone.utc)

    for page_extraction_creation in extraction_batch.page_extraction_creations:
        page_extraction = page_extraction_creation.page_extraction
        assert page_extraction.run_classification is False
        page_extraction.run_classification = True
        classification_chunk = classification_orm_models.ExerciseClassificationChunk(
            created=extraction_orm_models.ExerciseClassificationChunkCreationByPageExtraction(
                at=now, page_extraction=page_extraction
            ),
            model_for_adaptation=None,
        )
        session.add(classification_chunk)

        for exercise_creation in page_extraction.exercise_creations__unordered:
            exercise = exercise_creation.exercise
            assert isinstance(exercise, adaptation_orm_models.AdaptableExercise)
            session.add(
                classification_orm_models.ExerciseClassificationByClassificationChunk(
                    exercise=exercise, at=now, classification_chunk=classification_chunk, exercise_class=None
                )
            )


@api_router.put("/extraction-batches/{id}/model-for-adaptation", status_code=fastapi.status.HTTP_200_OK)
def put_extraction_batch_model_for_adaptation(
    id: str, req: adaptation_llm.ConcreteModel, session: database_utils.SessionDependable
) -> None:
    extraction_batch = get_by_id(session, extraction_orm_models.SandboxExtractionBatch, id)
    assert extraction_batch.model_for_adaptation is None
    extraction_batch.model_for_adaptation = req
    now = datetime.datetime.now(datetime.timezone.utc)
    for page_extraction_creation in extraction_batch.page_extraction_creations:
        page_extraction = page_extraction_creation.page_extraction
        classification_chunk = (
            session.execute(
                sql.select(classification_orm_models.ExerciseClassificationChunk)
                .join(extraction_orm_models.ExerciseClassificationChunkCreationByPageExtraction)
                .where(
                    extraction_orm_models.ExerciseClassificationChunkCreationByPageExtraction.page_extraction
                    == page_extraction
                )
            )
            .scalars()
            .first()
        )
        assert classification_chunk is not None
        assert classification_chunk.model_for_adaptation is None
        classification_chunk.model_for_adaptation = req
        for exercise_creation in page_extraction.exercise_creations__unordered:
            exercise = exercise_creation.exercise
            assert isinstance(exercise, adaptation_orm_models.AdaptableExercise)

            classification = exercise.classifications[-1]
            assert isinstance(classification, classification_orm_models.ExerciseClassificationByClassificationChunk)
            assert classification.classification_chunk == classification_chunk

            if (
                len(exercise.adaptations) == 0
                and classification.exercise_class is not None
                and classification.exercise_class.latest_strategy_settings is not None
            ):
                session.add(
                    adaptation_orm_models.ExerciseAdaptation(
                        created=classification_orm_models.ExerciseAdaptationCreationByClassificationChunk(
                            at=now, classification_chunk=classification_chunk
                        ),
                        exercise=exercise,
                        settings=classification.exercise_class.latest_strategy_settings,
                        model=classification_chunk.model_for_adaptation,
                        raw_llm_conversations=[],
                        initial_assistant_response=None,
                        adjustments=[],
                        manual_edit=None,
                    )
                )


class GetExtractionBatchesResponse(ApiModel):
    class ExtractionBatch(ApiModel):
        id: str
        created_by: str
        created_at: datetime.datetime

    extraction_batches: list[ExtractionBatch]
    next_chunk_id: str | None


@api_router.get("/extraction-batches")
async def get_extraction_batches(
    session: database_utils.SessionDependable, chunkId: str | None = None
) -> GetExtractionBatchesResponse:
    (batches, next_chunk_id) = paginate(extraction_orm_models.SandboxExtractionBatch, session, chunkId)
    return GetExtractionBatchesResponse(
        extraction_batches=[
            GetExtractionBatchesResponse.ExtractionBatch(
                id=str(extraction_batch.id),
                created_by=extraction_batch.created_by,
                created_at=extraction_batch.created_at,
            )
            for extraction_batch in batches
        ],
        next_chunk_id=next_chunk_id,
    )


class PostTextbookRequest(ApiModel):
    creator: str
    title: str
    publisher: str | None
    year: int | None
    isbn: str | None


class PostTextbookResponse(ApiModel):
    id: str


@api_router.post("/textbooks")
def post_textbook(
    req: PostTextbookRequest, engine: database_utils.EngineDependable, session: database_utils.SessionDependable
) -> PostTextbookResponse:
    textbook = textbooks_orm_models.Textbook(
        created_by=req.creator,
        created_at=datetime.datetime.now(datetime.timezone.utc),
        title=req.title,
        publisher=req.publisher,
        year=req.year,
        isbn=req.isbn,
    )
    session.add(textbook)
    session.flush()
    return PostTextbookResponse(id=str(textbook.id))


class ApiTextbook(ApiModel):
    id: str
    created_by: str
    title: str
    publisher: str | None
    year: int | None
    isbn: str | None

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


@api_router.get("/textbooks/{id}")
async def get_textbook(id: str, session: database_utils.SessionDependable) -> GetTextbookResponse:
    textbook = get_by_id(session, textbooks_orm_models.Textbook, id)
    return GetTextbookResponse(
        textbook=make_api_textbook(textbook),
        available_strategy_settings=[
            exercise_class.name
            for exercise_class in session.query(adaptation_orm_models.ExerciseClass)
            .order_by(adaptation_orm_models.ExerciseClass.name)
            .all()
        ],
    )


class GetTextbooksResponse(ApiModel):
    class Textbook(ApiModel):
        id: str
        created_by: str
        created_at: datetime.datetime
        title: str
        publisher: str | None
        year: int | None

    textbooks: list[Textbook]


@api_router.get("/textbooks")
async def get_textbooks(session: database_utils.SessionDependable) -> GetTextbooksResponse:
    textbooks = session.query(textbooks_orm_models.Textbook).order_by(-textbooks_orm_models.Textbook.id).all()
    return GetTextbooksResponse(
        textbooks=[
            GetTextbooksResponse.Textbook(
                id=str(textbook.id),
                created_by=textbook.created_by,
                created_at=textbook.created_at,
                title=textbook.title,
                publisher=textbook.publisher,
                year=textbook.year,
            )
            for textbook in textbooks
        ]
    )


class PostTextbookExternalExercisesRequest(ApiModel):
    creator: str
    page_number: int
    exercise_number: str
    original_file_name: str


class PostTextbookExternalExercisesResponse(ApiModel):
    put_url: str


@api_router.post("/textbooks/{textbook_id}/external-exercises")
def post_textbook_external_exercises(
    textbook_id: str, req: PostTextbookExternalExercisesRequest, session: database_utils.SessionDependable
) -> PostTextbookExternalExercisesResponse:
    textbook = get_by_id(session, textbooks_orm_models.Textbook, textbook_id)
    now = datetime.datetime.now(datetime.timezone.utc)
    external_exercise = external_exercises_orm_models.ExternalExercise(
        created=exercises_orm_models.ExerciseCreationByUser(at=now, username=req.creator),
        location=textbooks_orm_models.ExerciseLocationTextbook(
            textbook=textbook, page_number=req.page_number, exercise_number=req.exercise_number
        ),
        removed_from_textbook=False,
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


@api_router.put("/textbooks/{textbook_id}/external-exercises/{external_exercise_id}/removed")
def put_textbook_external_exercises_removed(
    textbook_id: str, external_exercise_id: str, removed: bool, session: database_utils.SessionDependable
) -> ApiTextbook:
    textbook = get_by_id(session, textbooks_orm_models.Textbook, textbook_id)
    external_exercise = get_by_id(session, external_exercises_orm_models.ExternalExercise, external_exercise_id)
    assert isinstance(external_exercise.location, textbooks_orm_models.ExerciseLocationTextbook)
    assert external_exercise.location.textbook == textbook
    external_exercise.removed_from_textbook = removed
    return make_api_textbook(textbook)


@api_router.get("/adaptations/{id}")
async def get_adaptation(id: str, session: database_utils.SessionDependable) -> ApiAdaptation:
    return make_api_adaptation(get_by_id(session, adaptation_orm_models.ExerciseAdaptation, id))


class PostAdaptationAdjustmentRequest(ApiModel):
    adjustment: str


@api_router.post("/adaptations/{id}/adjustment")
async def post_adaptation_adjustment(
    id: str, req: PostAdaptationAdjustmentRequest, session: database_utils.SessionDependable
) -> ApiAdaptation:
    adaptation = get_by_id(session, adaptation_orm_models.ExerciseAdaptation, id)
    assert adaptation.initial_assistant_response is not None

    def make_assistant_message(assistant_response: AssistantResponse) -> LlmMessage:
        if isinstance(assistant_response, AssistantSuccess):
            return adaptation_llm.AssistantMessage[Exercise](content=assistant_response.exercise)
        elif isinstance(assistant_response, AssistantInvalidJsonError):
            return adaptation_llm.InvalidJsonAssistantMessage(content=assistant_response.parsed)
        elif isinstance(assistant_response, AssistantNotJsonError):
            return adaptation_llm.NotJsonAssistantMessage(content=assistant_response.text)
        else:
            raise ValueError("Unknown assistant response type")

    messages: list[LlmMessage] = [
        adaptation_llm.SystemMessage(content=adaptation.settings.system_prompt),
        adaptation_llm.UserMessage(content=adaptation.exercise.full_text),
        make_assistant_message(adaptation.initial_assistant_response),
    ]
    for adjustment in adaptation.adjustments:
        assert isinstance(adjustment.assistant_response, AssistantSuccess)
        messages.append(adaptation_llm.UserMessage(content=adjustment.user_prompt))
        make_assistant_message(adjustment.assistant_response)
    messages.append(adaptation_llm.UserMessage(content=req.adjustment))

    try:
        response = await adaptation.model.complete(
            messages, adaptation.settings.response_specification.make_response_format()
        )
    except adaptation_llm.InvalidJsonLlmException as error:
        raw_conversation = error.raw_conversation
        assistant_response: AssistantResponse = AssistantInvalidJsonError(
            kind="error", error="invalid-json", parsed=error.parsed
        )
    except adaptation_llm.NotJsonLlmException as error:
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


@api_router.delete("/adaptations/{id}/last-adjustment")
def delete_adaptation_last_adjustment(id: str, session: database_utils.SessionDependable) -> ApiAdaptation:
    adaptation = get_by_id(session, adaptation_orm_models.ExerciseAdaptation, id)

    raw_llm_conversations = list(adaptation.raw_llm_conversations)
    raw_llm_conversations.pop()
    adaptation.raw_llm_conversations = raw_llm_conversations

    adjustments = list(adaptation.adjustments)
    adjustments.pop()
    adaptation.adjustments = adjustments

    return make_api_adaptation(adaptation)


@api_router.put("/adaptations/{id}/manual-edit")
def put_adaptation_manual_edit(id: str, req: Exercise, session: database_utils.SessionDependable) -> ApiAdaptation:
    adaptation = get_by_id(session, adaptation_orm_models.ExerciseAdaptation, id)
    adaptation.manual_edit = req
    return make_api_adaptation(adaptation)


@api_router.delete("/adaptations/{id}/manual-edit")
def delete_adaptation_manual_edit(id: str, session: database_utils.SessionDependable) -> ApiAdaptation:
    adaptation = get_by_id(session, adaptation_orm_models.ExerciseAdaptation, id)
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


def make_api_adaptation(adaptation: adaptation_orm_models.ExerciseAdaptation) -> ApiAdaptation:
    return ApiAdaptation(
        id=str(adaptation.id),
        extraction_batch_id=(
            str(adaptation.exercise.created.page_extraction.created.sandbox_extraction_batch.id)
            if isinstance(adaptation.exercise.created, extraction_orm_models.ExerciseCreationByPageExtraction)
            and isinstance(
                adaptation.exercise.created.page_extraction.created,
                extraction_orm_models.PageExtractionCreationBySandboxExtractionBatch,
            )
            else None
        ),
        classification_batch_id=(
            str(adaptation.created.classification_chunk.created.sandbox_classification_batch.id)
            if isinstance(adaptation.created, classification_orm_models.ExerciseAdaptationCreationByClassificationChunk)
            and isinstance(
                adaptation.created.classification_chunk.created,
                classification_orm_models.ExerciseClassificationChunkCreationBySandboxClassificationBatch,
            )
            else None
        ),
        adaptation_batch_id=(
            str(adaptation.created.sandbox_adaptation_batch.id)
            if isinstance(adaptation.created, adaptation_orm_models.ExerciseAdaptationCreationBySandboxAdaptationBatch)
            else None
        ),
        strategy=make_api_strategy(adaptation.settings, adaptation.model),
        input=make_api_input(adaptation.exercise),
        raw_llm_conversations=adaptation.raw_llm_conversations,
        initial_assistant_response=adaptation.initial_assistant_response,
        adjustments=adaptation.adjustments,
        manual_edit=adaptation.manual_edit,
        removed_from_textbook=adaptation.exercise.removed_from_textbook,
    )


def make_api_strategy(
    settings: adaptation_orm_models.ExerciseAdaptationSettings, model: adaptation_llm.ConcreteModel
) -> ApiStrategy:
    return ApiStrategy(model=model, settings=make_api_strategy_settings(settings))


def make_api_strategy_settings(settings: adaptation_orm_models.ExerciseAdaptationSettings) -> ApiStrategySettings:
    return ApiStrategySettings(
        name=make_api_strategy_settings_name(settings),
        system_prompt=settings.system_prompt,
        response_specification=settings.response_specification,
    )


def make_api_strategy_settings_name(settings: adaptation_orm_models.ExerciseAdaptationSettings) -> str | None:
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


def make_api_input(exercise: adaptation_orm_models.AdaptableExercise) -> ApiInput:
    assert isinstance(
        exercise.location,
        (textbooks_orm_models.ExerciseLocationTextbook, exercises_orm_models.ExerciseLocationMaybePageAndNumber),
    )
    return ApiInput(
        page_number=exercise.location.page_number,
        exercise_number=exercise.location.exercise_number,
        text=exercise.full_text,
    )


def make_api_textbook(textbook: textbooks_orm_models.Textbook) -> ApiTextbook:
    return ApiTextbook(
        id=str(textbook.id),
        created_by=textbook.created_by,
        title=textbook.title,
        publisher=textbook.publisher,
        year=textbook.year,
        isbn=textbook.isbn,
        external_exercises=[
            ApiTextbook.ExternalExercise(
                id=str(external_exercise.id),
                page_number=assert_isinstance(
                    external_exercise.location, textbooks_orm_models.ExerciseLocationTextbook
                ).page_number,
                exercise_number=assert_isinstance(
                    external_exercise.location, textbooks_orm_models.ExerciseLocationTextbook
                ).exercise_number,
                original_file_name=external_exercise.original_file_name,
                removed_from_textbook=external_exercise.removed_from_textbook,
            )
            for external_exercise in textbook.fetch_ordered_exercises()
            if isinstance(external_exercise, external_exercises_orm_models.ExternalExercise)
        ],
    )


export_router = fastapi.APIRouter(dependencies=[fastapi.Depends(authentication.auth_param_dependable)])


export_batch_template_file_path = os.path.join(os.path.dirname(__file__), "export", "templates", "batch", "index.html")


@export_router.get("/extraction-batch/{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_extraction_batch_html(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    return export_batch_html("extraction", id, get_extraction_batch_adaptations(session, id), download)


@export_router.get("/extraction-batch/{id}.json")
def export_extraction_batch_json(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.JSONResponse:
    return export_batch_json("extraction", id, get_extraction_batch_adaptations(session, id), download)


def get_extraction_batch_adaptations(
    session: database_utils.Session, id: str
) -> Iterable[adaptation_orm_models.ExerciseAdaptation | None]:
    batch = get_by_id(session, extraction_orm_models.SandboxExtractionBatch, id)
    return [
        exercise.adaptations[-1] if len(exercise.adaptations) > 0 else None
        for creation in batch.page_extraction_creations
        for exercise in creation.page_extraction.fetch_ordered_exercises()
    ]


@export_router.get("/classification-batch/{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_classification_batch_html(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    return export_batch_html("classification", id, get_classification_batch_adaptations(session, id), download)


@export_router.get("/classification-batch/{id}.json")
def export_classification_batch_json(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.JSONResponse:
    return export_batch_json("classification", id, get_classification_batch_adaptations(session, id), download)


def get_classification_batch_adaptations(
    session: database_utils.Session, id: str
) -> Iterable[adaptation_orm_models.ExerciseAdaptation | None]:
    return [
        classification.exercise.adaptations[-1] if len(classification.exercise.adaptations) > 0 else None
        for classification in get_by_id(
            session, classification_orm_models.SandboxClassificationBatch, id
        ).classification_chunk_creation.classification_chunk.classifications
    ]


@export_router.get("/adaptation-batch/{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_adaptation_batch_html(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    return export_batch_html("adaptation", id, get_adaptation_batch_adaptations(session, id), download)


@export_router.get("/adaptation-batch/{id}.json")
def export_adaptation_batch_json(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.JSONResponse:
    return export_batch_json("adaptation", id, get_adaptation_batch_adaptations(session, id), download)


def get_adaptation_batch_adaptations(
    session: database_utils.Session, id: str
) -> Iterable[adaptation_orm_models.ExerciseAdaptation | None]:
    return [
        (
            adaptation_creation.exercise_adaptation.exercise.adaptations[-1]
            if len(adaptation_creation.exercise_adaptation.exercise.adaptations) > 0
            else None
        )
        for adaptation_creation in get_by_id(
            session, adaptation_orm_models.SandboxAdaptationBatch, id
        ).adaptation_creations
    ]


def export_batch_html(
    kind: Literal["extraction", "adaptation", "classification"],
    id: str,
    adaptations: Iterable[adaptation_orm_models.ExerciseAdaptation | None],
    download: bool,
) -> fastapi.responses.HTMLResponse:
    data = list(
        adapted_exercise_data
        for adapted_exercise_data in (
            make_adapted_exercise_data(adaptation) for adaptation in adaptations if adaptation is not None
        )
        if adapted_exercise_data is not None
    )

    content = render_template(export_batch_template_file_path, "BATCH_EXPORT_DATA", data)

    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="test-{kind}-batch-{id}.html"'

    return fastapi.responses.HTMLResponse(content=content, headers=headers)


def export_batch_json(
    kind: Literal["extraction", "adaptation", "classification"],
    id: str,
    adaptations: Iterable[adaptation_orm_models.ExerciseAdaptation | None],
    download: bool,
) -> fastapi.responses.JSONResponse:
    content = list(
        adapted_exercise_data
        for adapted_exercise_data in (
            make_adapted_exercise_data(adaptation) for adaptation in adaptations if adaptation is not None
        )
        if adapted_exercise_data is not None
    )

    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="test-{kind}-batch-{id}.json"'

    return fastapi.responses.JSONResponse(content=content, headers=headers)


export_adaptation_template_file_path = os.path.join(
    os.path.dirname(__file__), "export", "templates", "adaptation", "index.html"
)


@export_router.get("/adaptation/{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_adaptation(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    data = make_adapted_exercise_data(get_by_id(session, adaptation_orm_models.ExerciseAdaptation, id))
    assert data is not None
    content = render_template(export_adaptation_template_file_path, "ADAPTATION_EXPORT_DATA", data)

    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{data['exerciseId']}.html"'

    return fastapi.responses.HTMLResponse(content=content, headers=headers)


export_textbook_template_file_path = os.path.join(
    os.path.dirname(__file__), "export", "templates", "textbook", "index.html"
)


@export_router.get("/textbook/{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_textbook(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    textbook = get_by_id(session, textbooks_orm_models.Textbook, id)

    exercises: list[JsonDict] = []
    for exercise in textbook.fetch_ordered_exercises():
        if not exercise.removed_from_textbook:
            if isinstance(exercise, adaptation_orm_models.AdaptableExercise):
                if len(exercise.adaptations) != 0:
                    adapted_exercise_data = make_adapted_exercise_data(exercise.adaptations[-1])
                    if adapted_exercise_data is not None:
                        exercises.append(adapted_exercise_data)
            elif isinstance(exercise, external_exercises_orm_models.ExternalExercise):
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


def make_adapted_exercise_data(adaptation: adaptation_orm_models.ExerciseAdaptation) -> JsonDict | None:
    location = adaptation.exercise.location
    assert isinstance(
        location,
        (exercises_orm_models.ExerciseLocationMaybePageAndNumber, textbooks_orm_models.ExerciseLocationTextbook),
    )
    if location.page_number is not None and location.exercise_number is not None:
        exercise_id = f"P{location.page_number}Ex{location.exercise_number}"
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
        "pageNumber": location.page_number,
        "exerciseNumber": location.exercise_number,
        "kind": "adapted",
        "studentAnswersStorageKey": hashlib.md5(
            json.dumps(adapted_exercise_dump, separators=(",", ":"), indent=None).encode()
        ).hexdigest(),
        "adaptedExercise": adapted_exercise_dump,
    }


def make_external_exercise_data(external_exercise: external_exercises_orm_models.ExternalExercise) -> JsonDict:
    location = external_exercise.location
    assert isinstance(location, textbooks_orm_models.ExerciseLocationTextbook)
    exercise_id = f"P{location.page_number}Ex{location.exercise_number}"
    target = urllib.parse.urlparse(f"{settings.EXTERNAL_EXERCISES_URL}/{external_exercise.id}")
    object = s3.get_object(Bucket=target.netloc, Key=target.path[1:])
    data = base64.b64encode(object["Body"].read()).decode("ascii")
    return {
        "exerciseId": exercise_id,
        "pageNumber": location.page_number,
        "exerciseNumber": location.exercise_number,
        "kind": "external",
        "originalFileName": external_exercise.original_file_name,
        "data": data,
    }


class ApiTestCase(database_utils.TestCaseWithDatabase):
    def setUp(self) -> None:
        super().setUp()
        self.app = fastapi.FastAPI(database_engine=self.engine)
        self.app.include_router(api_router)
        access_token = authentication.login(authentication.PostTokenRequest(password="password")).access_token
        self.client = fastapi.testclient.TestClient(self.app, headers={"Authorization": f"Bearer {access_token}"})

    def test_create_the_same_pdf_file_several_times(self) -> None:
        sha = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

        try:
            s3.delete_object(Bucket="jacquev6", Key=f"patty/dev/pdf-files/{sha}")
        except botocore.exceptions.ClientError:
            pass

        r = self.client.post(
            "/pdf-files",
            json={"creator": "UnitTest", "fileName": "foo.pdf", "bytesCount": 0, "pagesCount": 0, "sha256": sha},
        )
        self.assertEqual(r.status_code, 200, r.text)
        self.assertIsNotNone(r.json()["uploadUrl"])
        self.assertEqual(self.get_model(extraction_orm_models.PdfFile, sha).known_file_names, ["foo.pdf"])

        r = self.client.post(
            "/pdf-files",
            json={"creator": "UnitTest", "fileName": "bar.pdf", "bytesCount": 0, "pagesCount": 0, "sha256": sha},
        )
        self.assertEqual(r.status_code, 200, r.text)
        upload_url = r.json()["uploadUrl"]
        self.assertIsNotNone(upload_url)
        requests.put(upload_url, data=b"")
        s3.head_object(Bucket="jacquev6", Key=f"patty/dev/pdf-files/{sha}")
        self.assertEqual(self.get_model(extraction_orm_models.PdfFile, sha).known_file_names, ["foo.pdf", "bar.pdf"])

        r = self.client.post(
            "/pdf-files",
            json={"creator": "UnitTest", "fileName": "foo.pdf", "bytesCount": 0, "pagesCount": 0, "sha256": sha},
        )
        self.assertEqual(r.status_code, 200, r.text)
        self.assertIsNone(r.json()["uploadUrl"])
        self.assertEqual(self.get_model(extraction_orm_models.PdfFile, sha).known_file_names, ["foo.pdf", "bar.pdf"])
