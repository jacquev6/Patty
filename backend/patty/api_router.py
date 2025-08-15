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

from . import adaptation
from . import authentication
from . import classification
from . import database_utils
from . import errors
from . import exercises
from . import external_exercises
from . import extraction
from . import settings
from . import textbooks
from .any_json import JsonDict, JsonList
from .api_utils import ApiModel
from .version import PATTY_VERSION

__all__ = ["api_router", "export_router"]

s3 = boto3.client("s3", config=botocore.client.Config(region_name="eu-west-3", signature_version="s3v4"))

api_router = fastapi.APIRouter(dependencies=[fastapi.Depends(authentication.auth_bearer_dependable)])

api_router.include_router(errors.router, prefix="/errors-caught-by-frontend")


T1 = TypeVar("T1")


def assert_isinstance(value: Any, type_: type[T1]) -> T1:
    assert isinstance(value, type_)
    return value


@api_router.get("/available-adaptation-llm-models")
def get_available_adaptation_llm_models() -> list[adaptation.llm.ConcreteModel]:
    if PATTY_VERSION == "dev":
        return [
            adaptation.llm.DummyModel(provider="dummy", name="dummy-1"),
            adaptation.llm.DummyModel(provider="dummy", name="dummy-2"),
            adaptation.llm.DummyModel(provider="dummy", name="dummy-3"),
            adaptation.llm.MistralAiModel(provider="mistralai", name="mistral-large-2411"),
            adaptation.llm.MistralAiModel(provider="mistralai", name="mistral-small-2501"),
            adaptation.llm.OpenAiModel(provider="openai", name="gpt-4o-2024-08-06"),
            adaptation.llm.OpenAiModel(provider="openai", name="gpt-4o-mini-2024-07-18"),
        ]
    else:
        return [
            adaptation.llm.MistralAiModel(provider="mistralai", name="mistral-large-2411"),
            adaptation.llm.MistralAiModel(provider="mistralai", name="mistral-small-2501"),
            adaptation.llm.OpenAiModel(provider="openai", name="gpt-4o-2024-08-06"),
            adaptation.llm.OpenAiModel(provider="openai", name="gpt-4o-mini-2024-07-18"),
            adaptation.llm.DummyModel(provider="dummy", name="dummy-1"),
            adaptation.llm.DummyModel(provider="dummy", name="dummy-2"),
        ]


class ApiStrategySettings(ApiModel):
    name: str | None
    system_prompt: str
    response_specification: adaptation.strategy.ConcreteLlmResponseSpecification


class ApiStrategy(ApiModel):
    model: adaptation.llm.ConcreteModel
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
    initial_assistant_response: adaptation.assistant_responses.Response | None
    adjustments: list[adaptation.assistant_responses.Adjustment]
    manual_edit: adaptation.adapted.Exercise | None
    removed_from_textbook: bool


@api_router.post("/adaptation-llm-response-schema")
def make_adaptation_llm_response_schema(
    response_specification: adaptation.strategy.JsonSchemaLlmResponseSpecification,
) -> JsonDict:
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
    request = sql.select(adaptation.SandboxAdaptationBatch)
    if base is None:
        request = request.where(
            (adaptation.SandboxAdaptationBatch.created_by == user) | (adaptation.SandboxAdaptationBatch.id == 1)
        ).order_by(-adaptation.SandboxAdaptationBatch.id)
    else:
        try:
            base_id = int(base)
        except ValueError:
            raise fastapi.HTTPException(status_code=404, detail="Base adaptation batch not found")
        else:
            request = request.where(adaptation.SandboxAdaptationBatch.id == base_id)

    adaptation_batch = session.execute(request).scalars().first()
    if adaptation_batch is None:
        raise fastapi.HTTPException(status_code=404, detail="Base adaptation batch not found")

    available_strategy_settings = []
    for exercise_class in (
        session.execute(
            sql.select(adaptation.ExerciseClass)
            .where(adaptation.ExerciseClass.latest_strategy_settings != sql.null())
            .order_by(adaptation.ExerciseClass.name)
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
            session.query(adaptation.ExerciseClass).filter(adaptation.ExerciseClass.name == branch_name).first()
        )
        if exercise_class is None:
            assert branch_name == req.strategy.settings.name
            base_settings = None
            exercise_class = adaptation.ExerciseClass(
                created=classification.ExerciseClassCreationByUser(at=now, username=req.creator),
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
        settings = adaptation.ExerciseAdaptationSettings(
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

    adaptation_batch = adaptation.SandboxAdaptationBatch(
        created_by=req.creator, created_at=now, settings=settings, model=req.strategy.model
    )
    session.add(adaptation_batch)

    for req_input in req.inputs:
        exercise = adaptation.AdaptableExercise(
            created=exercises.ExerciseCreationByUser(at=now, username=req.creator),
            location=exercises.ExerciseLocationMaybePageAndNumber(
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
                classification.ExerciseClassificationByUser(
                    exercise=exercise, at=now, username=req.creator, exercise_class=exercise_class
                )
            )

        session.add(
            adaptation.ExerciseAdaptation(
                created=adaptation.ExerciseAdaptationCreationBySandboxAdaptationBatch(
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
        )

    session.flush()

    return PostAdaptationBatchResponse(id=str(adaptation_batch.id))


class GetAdaptationBatchResponse(ApiModel):
    id: str
    created_by: str
    strategy: ApiStrategy
    adaptations: list[ApiAdaptation]


@api_router.get("/adaptation-batches/{id}")
async def get_adaptation_batch(id: str, session: database_utils.SessionDependable) -> GetAdaptationBatchResponse:
    adaptation_batch = get_by_id(session, adaptation.SandboxAdaptationBatch, id)
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
        model: adaptation.llm.ConcreteModel
        strategy_settings_name: str | None

    adaptation_batches: list[AdaptationBatch]
    next_chunk_id: str | None


@api_router.get("/exercise-classes")
def get_exercise_classes(session: database_utils.SessionDependable) -> list[str]:
    request = sql.select(adaptation.ExerciseClass).order_by(adaptation.ExerciseClass.name)
    return [exercise_class.name for exercise_class in session.execute(request).scalars().all()]


class PutAdaptableExerciseClassRequest(ApiModel):
    creator: str
    className: str


@api_router.put("/adaptable-exercises/{id}/exercise-class")
def put_adaptable_exercise_class(
    id: str, req: PutAdaptableExerciseClassRequest, session: database_utils.SessionDependable
) -> None:
    now = datetime.datetime.now(datetime.timezone.utc)
    exercise = get_by_id(session, adaptation.AdaptableExercise, id)
    exercise_class = (
        session.query(adaptation.ExerciseClass).filter(adaptation.ExerciseClass.name == req.className).first()
    )
    if exercise_class is None:
        raise fastapi.HTTPException(status_code=404, detail="Exercise class not found")

    if len(exercise.adaptations) != 0:
        adaptation_model: adaptation.llm.ConcreteModel | None = exercise.adaptations[-1].model
    elif len(exercise.classifications) != 0 and isinstance(
        exercise.classifications[-1], classification.ExerciseClassificationByClassificationChunk
    ):
        adaptation_model = exercise.classifications[-1].classification_chunk.model_for_adaptation
    else:
        adaptation_model = None

    session.add(
        classification.ExerciseClassificationByUser(
            exercise=exercise, at=now, username=req.creator, exercise_class=exercise_class
        )
    )

    if adaptation_model is not None and exercise_class.latest_strategy_settings is not None:
        session.add(
            adaptation.ExerciseAdaptation(
                created=adaptation.ExerciseAdaptationCreationByUser(at=now, username=req.creator),
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
    bound=adaptation.SandboxAdaptationBatch
    | classification.SandboxClassificationBatch
    | extraction.SandboxExtractionBatch,
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
    (batches, next_chunk_id) = paginate(adaptation.SandboxAdaptationBatch, session, chunkId)

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
    model_for_adaptation: adaptation.llm.ConcreteModel | None


class PostClassificationBatchResponse(ApiModel):
    id: str


@api_router.post("/classification-batches")
def create_classification_batch(
    req: PostClassificationBatchRequest, session: database_utils.SessionDependable
) -> PostClassificationBatchResponse:
    now = datetime.datetime.now(datetime.timezone.utc)
    classification_batch = classification.SandboxClassificationBatch(
        created_by=req.creator, created_at=now, model_for_adaptation=req.model_for_adaptation
    )
    session.add(classification_batch)

    classification_chunk = classification.ExerciseClassificationChunk(
        created=classification.ExerciseClassificationChunkCreationBySandboxClassificationBatch(
            at=now, sandbox_classification_batch=classification_batch
        ),
        model_for_adaptation=req.model_for_adaptation,
    )
    session.add(classification_chunk)

    for req_input in req.inputs:
        exercise = adaptation.AdaptableExercise(
            created=exercises.ExerciseCreationByUser(at=now, username=req.creator),
            location=exercises.ExerciseLocationMaybePageAndNumber(
                page_number=req_input.page_number, exercise_number=req_input.exercise_number
            ),
            removed_from_textbook=False,
            full_text=req_input.instruction_hint_example_text + "\n" + req_input.statement_text,
            instruction_hint_example_text=req_input.instruction_hint_example_text,
            statement_text=req_input.statement_text,
        )
        session.add(exercise)
        session.add(
            classification.ExerciseClassificationByClassificationChunk(
                at=now, exercise=exercise, classification_chunk=classification_chunk, exercise_class=None
            )
        )

    session.flush()

    return PostClassificationBatchResponse(id=str(classification_batch.id))


class GetClassificationBatchResponse(ApiModel):
    id: str
    created_by: str | None
    model_for_adaptation: adaptation.llm.ConcreteModel | None

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
    classification_batch = get_by_id(session, classification.SandboxClassificationBatch, id)

    exercises_ = [
        classification.exercise
        for classification in classification_batch.classification_chunk_creation.classification_chunk.classifications
    ]

    latest_classifications = [
        exercise.classifications[-1] if exercise.classifications else None for exercise in exercises_
    ]

    latest_adaptations = [
        (
            None
            if latest_classification is None or latest_classification.exercise_class is None
            else exercise.fetch_latest_adaptation(latest_classification.exercise_class)
        )
        for (exercise, latest_classification) in zip(exercises_, latest_classifications)
    ]

    return GetClassificationBatchResponse(
        id=str(classification_batch.id),
        created_by=classification_batch.created_by,
        model_for_adaptation=classification_batch.model_for_adaptation,
        exercises=[
            GetClassificationBatchResponse.Exercise(
                id=str(exercise.id),
                page_number=assert_isinstance(
                    exercise.location, exercises.ExerciseLocationMaybePageAndNumber
                ).page_number,
                exercise_number=assert_isinstance(
                    exercise.location, exercises.ExerciseLocationMaybePageAndNumber
                ).exercise_number,
                full_text=exercise.full_text,
                exercise_class=(
                    latest_classification.exercise_class.name
                    if latest_classification is not None and latest_classification.exercise_class is not None
                    else None
                ),
                reclassified_by=(
                    latest_classification.username
                    if isinstance(latest_classification, classification.ExerciseClassificationByUser)
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
                exercises_, latest_classifications, latest_adaptations
            )
        ],
    )


@api_router.post(
    "/classification-batches/{id}/submit-adaptations-with-recent-settings", status_code=fastapi.status.HTTP_200_OK
)
def submit_adaptations_with_recent_settings_in_classification_batch(
    id: str, session: database_utils.SessionDependable
) -> None:
    classification_batch = get_by_id(session, classification.SandboxClassificationBatch, id)
    assert classification_batch.model_for_adaptation is not None
    now = datetime.datetime.now(datetime.timezone.utc)
    classification_chunk = classification_batch.classification_chunk_creation.classification_chunk
    for exercise_classification in classification_chunk.classifications:
        exercise = exercise_classification.exercise
        if (
            len(exercise.adaptations) == 0
            and exercise_classification.exercise_class is not None
            and exercise_classification.exercise_class.latest_strategy_settings is not None
        ):
            session.add(
                adaptation.ExerciseAdaptation(
                    created=classification.ExerciseAdaptationCreationByClassificationChunk(
                        at=now, classification_chunk=classification_chunk
                    ),
                    exercise=exercise,
                    settings=exercise_classification.exercise_class.latest_strategy_settings,
                    model=classification_batch.model_for_adaptation,
                    raw_llm_conversations=[],
                    initial_assistant_response=None,
                    adjustments=[],
                    manual_edit=None,
                )
            )


@api_router.put("/classification-batches/{id}/model-for-adaptation", status_code=fastapi.status.HTTP_200_OK)
def put_classification_batch_model_for_adaptation(
    id: str, req: adaptation.llm.ConcreteModel, session: database_utils.SessionDependable
) -> None:
    classification_batch = get_by_id(session, classification.SandboxClassificationBatch, id)
    assert classification_batch.model_for_adaptation is None
    classification_batch.model_for_adaptation = req
    now = datetime.datetime.now(datetime.timezone.utc)
    classification_chunk = classification_batch.classification_chunk_creation.classification_chunk
    classification_chunk.model_for_adaptation = req
    for exercise_classification in classification_chunk.classifications:
        exercise = exercise_classification.exercise
        if (
            len(exercise.adaptations) == 0
            and exercise_classification.exercise_class is not None
            and exercise_classification.exercise_class.latest_strategy_settings is not None
        ):
            session.add(
                adaptation.ExerciseAdaptation(
                    created=classification.ExerciseAdaptationCreationByClassificationChunk(
                        at=now, classification_chunk=classification_chunk
                    ),
                    exercise=exercise,
                    settings=exercise_classification.exercise_class.latest_strategy_settings,
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
    (batches, next_chunk_id) = paginate(classification.SandboxClassificationBatch, session, chunkId)

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
    pdf_file = session.get(extraction.PdfFile, req.sha256)
    if pdf_file is None:
        pdf_file = extraction.PdfFile(
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
    return extraction.extracted.ExercisesList.model_json_schema()


@api_router.get("/available-extraction-llm-models")
def get_available_extraction_llm_models() -> list[extraction.llm.ConcreteModel]:
    if PATTY_VERSION == "dev":
        return [
            extraction.llm.DummyModel(provider="dummy", name="dummy-1"),
            extraction.llm.DummyModel(provider="dummy", name="dummy-2"),
            extraction.llm.GeminiModel(provider="gemini", name="gemini-2.0-flash"),
        ]
    else:
        return [
            extraction.llm.GeminiModel(provider="gemini", name="gemini-2.0-flash"),
            extraction.llm.DummyModel(provider="dummy", name="dummy-1"),
            extraction.llm.DummyModel(provider="dummy", name="dummy-2"),
        ]


class ApiExtractionStrategy(ApiModel):
    id: str
    model: extraction.llm.ConcreteModel
    prompt: str


@api_router.get("/latest-extraction-strategy")
def get_latest_extraction_strategy(session: database_utils.SessionDependable) -> ApiExtractionStrategy:
    settings = (
        session.execute(sql.select(extraction.ExtractionSettings).order_by(-extraction.ExtractionSettings.id))
        .scalars()
        .first()
    )
    assert settings is not None
    if PATTY_VERSION == "dev":
        model: extraction.llm.ConcreteModel = extraction.llm.DummyModel(provider="dummy", name="dummy-1")
    else:
        model = extraction.llm.GeminiModel(provider="gemini", name="gemini-2.0-flash")
    return ApiExtractionStrategy(id=str(settings.id), model=model, prompt=settings.prompt)


class PostExtractionBatchRequest(ApiModel):
    creator: str
    pdf_file_sha256: str
    first_page: int
    pages_count: int
    strategy: ApiExtractionStrategy
    run_classification: bool
    model_for_adaptation: adaptation.llm.ConcreteModel | None


class PostExtractionBatchResponse(ApiModel):
    id: str


@api_router.post("/extraction-batches")
def create_extraction_batch(
    req: PostExtractionBatchRequest, session: database_utils.SessionDependable
) -> PostExtractionBatchResponse:
    now = datetime.datetime.now(datetime.timezone.utc)
    pdf_file = session.get(extraction.PdfFile, req.pdf_file_sha256)
    if pdf_file is None:
        raise fastapi.HTTPException(status_code=404, detail="PDF file not found")
    pdf_file_range = extraction.PdfFileRange(
        created_by=req.creator,
        created_at=now,
        pdf_file=pdf_file,
        first_page_number=req.first_page,
        pages_count=req.pages_count,
    )
    session.add(pdf_file_range)
    settings = session.get(extraction.ExtractionSettings, req.strategy.id)
    if settings is None or settings.prompt != req.strategy.prompt:
        settings = extraction.ExtractionSettings(created_by=req.creator, created_at=now, prompt=req.strategy.prompt)
        session.add(settings)
    model = req.strategy.model
    extraction_batch = extraction.SandboxExtractionBatch(
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
        page = extraction.PageExtraction(
            created=extraction.PageExtractionCreationBySandboxExtractionBatch(
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
    model_for_adaptation: adaptation.llm.ConcreteModel | None

    class Page(ApiModel):
        page_number: int
        assistant_response: extraction.assistant_responses.Response | None

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
    extraction_batch = get_by_id(session, extraction.SandboxExtractionBatch, id)
    pages: list[GetExtractionBatchResponse.Page] = []

    for page_extraction_creation in extraction_batch.page_extraction_creations:
        page_extraction = page_extraction_creation.page_extraction

        exercises_ = list(page_extraction.fetch_ordered_exercises())

        latest_classifications = [
            exercise.classifications[-1] if exercise.classifications else None for exercise in exercises_
        ]

        latest_adaptations = [
            (
                None
                if latest_classification is None or latest_classification.exercise_class is None
                else exercise.fetch_latest_adaptation(latest_classification.exercise_class)
            )
            for (exercise, latest_classification) in zip(exercises_, latest_classifications)
        ]

        pages.append(
            GetExtractionBatchResponse.Page(
                page_number=page_extraction.pdf_page_number,
                assistant_response=page_extraction.assistant_response,
                exercises=[
                    GetExtractionBatchResponse.Page.Exercise(
                        id=str(exercise.id),
                        page_number=assert_isinstance(
                            exercise.location, exercises.ExerciseLocationMaybePageAndNumber
                        ).page_number,
                        exercise_number=assert_isinstance(
                            exercise.location, exercises.ExerciseLocationMaybePageAndNumber
                        ).exercise_number,
                        full_text=exercise.full_text,
                        exercise_class=(
                            latest_classification.exercise_class.name
                            if latest_classification is not None and latest_classification.exercise_class is not None
                            else None
                        ),
                        reclassified_by=(
                            latest_classification.username
                            if isinstance(latest_classification, classification.ExerciseClassificationByUser)
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
                        exercises_, latest_classifications, latest_adaptations
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
    extraction_batch = get_by_id(session, extraction.SandboxExtractionBatch, id)
    assert extraction_batch.model_for_adaptation is not None
    now = datetime.datetime.now(datetime.timezone.utc)
    for page_extraction_creation in extraction_batch.page_extraction_creations:
        page_extraction = page_extraction_creation.page_extraction
        classification_chunk = (
            session.execute(
                sql.select(classification.ExerciseClassificationChunk)
                .join(extraction.ExerciseClassificationChunkCreationByPageExtraction)
                .where(
                    extraction.ExerciseClassificationChunkCreationByPageExtraction.page_extraction == page_extraction
                )
            )
            .scalars()
            .first()
        )
        assert classification_chunk is not None
        assert classification_chunk.model_for_adaptation is not None
        for exercise_creation in page_extraction.exercise_creations__unordered:
            exercise = exercise_creation.exercise
            assert isinstance(exercise, adaptation.AdaptableExercise)

            exercise_classification = exercise.classifications[-1]
            assert isinstance(exercise_classification, classification.ExerciseClassificationByClassificationChunk)
            assert exercise_classification.classification_chunk == classification_chunk

            if (
                len(exercise.adaptations) == 0
                and exercise_classification.exercise_class is not None
                and exercise_classification.exercise_class.latest_strategy_settings is not None
            ):
                session.add(
                    adaptation.ExerciseAdaptation(
                        created=classification.ExerciseAdaptationCreationByClassificationChunk(
                            at=now, classification_chunk=classification_chunk
                        ),
                        exercise=exercise,
                        settings=exercise_classification.exercise_class.latest_strategy_settings,
                        model=classification_chunk.model_for_adaptation,
                        raw_llm_conversations=[],
                        initial_assistant_response=None,
                        adjustments=[],
                        manual_edit=None,
                    )
                )


@api_router.put("/extraction-batches/{id}/run-classification", status_code=fastapi.status.HTTP_200_OK)
def put_extraction_batch_run_classification(id: str, session: database_utils.SessionDependable) -> None:
    extraction_batch = get_by_id(session, extraction.SandboxExtractionBatch, id)
    assert extraction_batch.run_classification is False
    extraction_batch.run_classification = True
    now = datetime.datetime.now(datetime.timezone.utc)

    for page_extraction_creation in extraction_batch.page_extraction_creations:
        page_extraction = page_extraction_creation.page_extraction
        assert page_extraction.run_classification is False
        page_extraction.run_classification = True
        classification_chunk = classification.ExerciseClassificationChunk(
            created=extraction.ExerciseClassificationChunkCreationByPageExtraction(
                at=now, page_extraction=page_extraction
            ),
            model_for_adaptation=None,
        )
        session.add(classification_chunk)

        for exercise_creation in page_extraction.exercise_creations__unordered:
            exercise = exercise_creation.exercise
            assert isinstance(exercise, adaptation.AdaptableExercise)
            session.add(
                classification.ExerciseClassificationByClassificationChunk(
                    exercise=exercise, at=now, classification_chunk=classification_chunk, exercise_class=None
                )
            )


@api_router.put("/extraction-batches/{id}/model-for-adaptation", status_code=fastapi.status.HTTP_200_OK)
def put_extraction_batch_model_for_adaptation(
    id: str, req: adaptation.llm.ConcreteModel, session: database_utils.SessionDependable
) -> None:
    extraction_batch = get_by_id(session, extraction.SandboxExtractionBatch, id)
    assert extraction_batch.model_for_adaptation is None
    extraction_batch.model_for_adaptation = req
    now = datetime.datetime.now(datetime.timezone.utc)
    for page_extraction_creation in extraction_batch.page_extraction_creations:
        page_extraction = page_extraction_creation.page_extraction
        classification_chunk = (
            session.execute(
                sql.select(classification.ExerciseClassificationChunk)
                .join(extraction.ExerciseClassificationChunkCreationByPageExtraction)
                .where(
                    extraction.ExerciseClassificationChunkCreationByPageExtraction.page_extraction == page_extraction
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
            assert isinstance(exercise, adaptation.AdaptableExercise)

            exercise_classification = exercise.classifications[-1]
            assert isinstance(exercise_classification, classification.ExerciseClassificationByClassificationChunk)
            assert exercise_classification.classification_chunk == classification_chunk

            if (
                len(exercise.adaptations) == 0
                and exercise_classification.exercise_class is not None
                and exercise_classification.exercise_class.latest_strategy_settings is not None
            ):
                session.add(
                    adaptation.ExerciseAdaptation(
                        created=classification.ExerciseAdaptationCreationByClassificationChunk(
                            at=now, classification_chunk=classification_chunk
                        ),
                        exercise=exercise,
                        settings=exercise_classification.exercise_class.latest_strategy_settings,
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
    (batches, next_chunk_id) = paginate(extraction.SandboxExtractionBatch, session, chunkId)
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
    textbook = textbooks.Textbook(
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
    textbook = get_by_id(session, textbooks.Textbook, id)
    return GetTextbookResponse(
        textbook=make_api_textbook(textbook),
        available_strategy_settings=[
            exercise_class.name
            for exercise_class in session.query(adaptation.ExerciseClass).order_by(adaptation.ExerciseClass.name).all()
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
    textbooks_ = session.query(textbooks.Textbook).order_by(-textbooks.Textbook.id).all()
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
            for textbook in textbooks_
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
    textbook = get_by_id(session, textbooks.Textbook, textbook_id)
    now = datetime.datetime.now(datetime.timezone.utc)
    external_exercise = external_exercises.ExternalExercise(
        created=exercises.ExerciseCreationByUser(at=now, username=req.creator),
        location=textbooks.ExerciseLocationTextbook(
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
    textbook = get_by_id(session, textbooks.Textbook, textbook_id)
    external_exercise = get_by_id(session, external_exercises.ExternalExercise, external_exercise_id)
    assert isinstance(external_exercise.location, textbooks.ExerciseLocationTextbook)
    assert external_exercise.location.textbook == textbook
    external_exercise.removed_from_textbook = removed
    return make_api_textbook(textbook)


@api_router.get("/adaptations/{id}")
async def get_adaptation(id: str, session: database_utils.SessionDependable) -> ApiAdaptation:
    return make_api_adaptation(get_by_id(session, adaptation.ExerciseAdaptation, id))


class PostAdaptationAdjustmentRequest(ApiModel):
    adjustment: str


@api_router.post("/adaptations/{id}/adjustment")
async def post_adaptation_adjustment(
    id: str, req: PostAdaptationAdjustmentRequest, session: database_utils.SessionDependable
) -> ApiAdaptation:
    exercise_adaptation = get_by_id(session, adaptation.ExerciseAdaptation, id)
    assert exercise_adaptation.initial_assistant_response is not None

    def make_assistant_message(
        assistant_response: adaptation.assistant_responses.Response,
    ) -> adaptation.submission.LlmMessage:
        if isinstance(assistant_response, adaptation.assistant_responses.Success):
            return adaptation.llm.AssistantMessage[adaptation.adapted.Exercise](content=assistant_response.exercise)
        elif isinstance(assistant_response, adaptation.assistant_responses.InvalidJsonError):
            return adaptation.llm.InvalidJsonAssistantMessage(content=assistant_response.parsed)
        elif isinstance(assistant_response, adaptation.assistant_responses.NotJsonError):
            return adaptation.llm.NotJsonAssistantMessage(content=assistant_response.text)
        else:
            raise ValueError("Unknown assistant response type")

    messages: list[adaptation.submission.LlmMessage] = [
        adaptation.llm.SystemMessage(content=exercise_adaptation.settings.system_prompt),
        adaptation.llm.UserMessage(content=exercise_adaptation.exercise.full_text),
        make_assistant_message(exercise_adaptation.initial_assistant_response),
    ]
    for adjustment in exercise_adaptation.adjustments:
        assert isinstance(adjustment.assistant_response, adaptation.assistant_responses.Success)
        messages.append(adaptation.llm.UserMessage(content=adjustment.user_prompt))
        make_assistant_message(adjustment.assistant_response)
    messages.append(adaptation.llm.UserMessage(content=req.adjustment))

    try:
        response = await exercise_adaptation.model.complete(
            messages, exercise_adaptation.settings.response_specification.make_response_format()
        )
    except adaptation.llm.InvalidJsonLlmException as error:
        raw_conversation = error.raw_conversation
        assistant_response: adaptation.assistant_responses.Response = adaptation.assistant_responses.InvalidJsonError(
            kind="error", error="invalid-json", parsed=error.parsed
        )
    except adaptation.llm.NotJsonLlmException as error:
        raw_conversation = error.raw_conversation
        assistant_response = adaptation.assistant_responses.NotJsonError(
            kind="error", error="not-json", text=error.text
        )
    else:
        raw_conversation = response.raw_conversation
        assistant_response = adaptation.assistant_responses.Success(
            kind="success", exercise=adaptation.adapted.Exercise(**response.message.content.model_dump())
        )

    raw_llm_conversations = list(exercise_adaptation.raw_llm_conversations)
    raw_llm_conversations.append(raw_conversation)
    exercise_adaptation.raw_llm_conversations = raw_llm_conversations

    adjustments = list(exercise_adaptation.adjustments)
    adjustments.append(
        adaptation.assistant_responses.Adjustment(user_prompt=req.adjustment, assistant_response=assistant_response)
    )
    exercise_adaptation.adjustments = adjustments

    return make_api_adaptation(exercise_adaptation)


@api_router.delete("/adaptations/{id}/last-adjustment")
def delete_adaptation_last_adjustment(id: str, session: database_utils.SessionDependable) -> ApiAdaptation:
    exercise_adaptation = get_by_id(session, adaptation.ExerciseAdaptation, id)

    raw_llm_conversations = list(exercise_adaptation.raw_llm_conversations)
    raw_llm_conversations.pop()
    exercise_adaptation.raw_llm_conversations = raw_llm_conversations

    adjustments = list(exercise_adaptation.adjustments)
    adjustments.pop()
    exercise_adaptation.adjustments = adjustments

    return make_api_adaptation(exercise_adaptation)


@api_router.put("/adaptations/{id}/manual-edit")
def put_adaptation_manual_edit(
    id: str, req: adaptation.adapted.Exercise, session: database_utils.SessionDependable
) -> ApiAdaptation:
    exercise_adaptation = get_by_id(session, adaptation.ExerciseAdaptation, id)
    exercise_adaptation.manual_edit = req
    return make_api_adaptation(exercise_adaptation)


@api_router.delete("/adaptations/{id}/manual-edit")
def delete_adaptation_manual_edit(id: str, session: database_utils.SessionDependable) -> ApiAdaptation:
    exercise_adaptation = get_by_id(session, adaptation.ExerciseAdaptation, id)
    exercise_adaptation.manual_edit = None
    return make_api_adaptation(exercise_adaptation)


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


def make_api_adaptation(exercise_adaptation: adaptation.ExerciseAdaptation) -> ApiAdaptation:
    return ApiAdaptation(
        id=str(exercise_adaptation.id),
        extraction_batch_id=(
            str(exercise_adaptation.exercise.created.page_extraction.created.sandbox_extraction_batch.id)
            if isinstance(exercise_adaptation.exercise.created, extraction.ExerciseCreationByPageExtraction)
            and isinstance(
                exercise_adaptation.exercise.created.page_extraction.created,
                extraction.PageExtractionCreationBySandboxExtractionBatch,
            )
            else None
        ),
        classification_batch_id=(
            str(exercise_adaptation.created.classification_chunk.created.sandbox_classification_batch.id)
            if isinstance(exercise_adaptation.created, classification.ExerciseAdaptationCreationByClassificationChunk)
            and isinstance(
                exercise_adaptation.created.classification_chunk.created,
                classification.ExerciseClassificationChunkCreationBySandboxClassificationBatch,
            )
            else None
        ),
        adaptation_batch_id=(
            str(exercise_adaptation.created.sandbox_adaptation_batch.id)
            if isinstance(exercise_adaptation.created, adaptation.ExerciseAdaptationCreationBySandboxAdaptationBatch)
            else None
        ),
        strategy=make_api_strategy(exercise_adaptation.settings, exercise_adaptation.model),
        input=make_api_input(exercise_adaptation.exercise),
        raw_llm_conversations=exercise_adaptation.raw_llm_conversations,
        initial_assistant_response=exercise_adaptation.initial_assistant_response,
        adjustments=exercise_adaptation.adjustments,
        manual_edit=exercise_adaptation.manual_edit,
        removed_from_textbook=exercise_adaptation.exercise.removed_from_textbook,
    )


def make_api_strategy(
    settings: adaptation.ExerciseAdaptationSettings, model: adaptation.llm.ConcreteModel
) -> ApiStrategy:
    return ApiStrategy(model=model, settings=make_api_strategy_settings(settings))


def make_api_strategy_settings(settings: adaptation.ExerciseAdaptationSettings) -> ApiStrategySettings:
    return ApiStrategySettings(
        name=make_api_strategy_settings_name(settings),
        system_prompt=settings.system_prompt,
        response_specification=settings.response_specification,
    )


def make_api_strategy_settings_name(settings: adaptation.ExerciseAdaptationSettings) -> str | None:
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


def make_api_input(exercise: adaptation.AdaptableExercise) -> ApiInput:
    assert isinstance(
        exercise.location, (textbooks.ExerciseLocationTextbook, exercises.ExerciseLocationMaybePageAndNumber)
    )
    return ApiInput(
        page_number=exercise.location.page_number,
        exercise_number=exercise.location.exercise_number,
        text=exercise.full_text,
    )


def make_api_textbook(textbook: textbooks.Textbook) -> ApiTextbook:
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
                    external_exercise.location, textbooks.ExerciseLocationTextbook
                ).page_number,
                exercise_number=assert_isinstance(
                    external_exercise.location, textbooks.ExerciseLocationTextbook
                ).exercise_number,
                original_file_name=external_exercise.original_file_name,
                removed_from_textbook=external_exercise.removed_from_textbook,
            )
            for external_exercise in textbook.fetch_ordered_exercises()
            if isinstance(external_exercise, external_exercises.ExternalExercise)
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
) -> Iterable[adaptation.ExerciseAdaptation | None]:
    batch = get_by_id(session, extraction.SandboxExtractionBatch, id)
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
) -> Iterable[adaptation.ExerciseAdaptation | None]:
    return [
        classification.exercise.adaptations[-1] if len(classification.exercise.adaptations) > 0 else None
        for classification in get_by_id(
            session, classification.SandboxClassificationBatch, id
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
) -> Iterable[adaptation.ExerciseAdaptation | None]:
    return [
        (
            adaptation_creation.exercise_adaptation.exercise.adaptations[-1]
            if len(adaptation_creation.exercise_adaptation.exercise.adaptations) > 0
            else None
        )
        for adaptation_creation in get_by_id(session, adaptation.SandboxAdaptationBatch, id).adaptation_creations
    ]


def export_batch_html(
    kind: Literal["extraction", "adaptation", "classification"],
    id: str,
    adaptations: Iterable[adaptation.ExerciseAdaptation | None],
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
    adaptations: Iterable[adaptation.ExerciseAdaptation | None],
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
    data = make_adapted_exercise_data(get_by_id(session, adaptation.ExerciseAdaptation, id))
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
    textbook = get_by_id(session, textbooks.Textbook, id)

    exercises: list[JsonDict] = []
    for exercise in textbook.fetch_ordered_exercises():
        if not exercise.removed_from_textbook:
            if isinstance(exercise, adaptation.AdaptableExercise):
                if len(exercise.adaptations) != 0:
                    adapted_exercise_data = make_adapted_exercise_data(exercise.adaptations[-1])
                    if adapted_exercise_data is not None:
                        exercises.append(adapted_exercise_data)
            elif isinstance(exercise, external_exercises.ExternalExercise):
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


def make_adapted_exercise_data(exercise_adaptation: adaptation.ExerciseAdaptation) -> JsonDict | None:
    location = exercise_adaptation.exercise.location
    assert isinstance(location, (exercises.ExerciseLocationMaybePageAndNumber, textbooks.ExerciseLocationTextbook))
    if location.page_number is not None and location.exercise_number is not None:
        exercise_id = f"P{location.page_number}Ex{location.exercise_number}"
    else:
        exercise_id = f"exercice-{exercise_adaptation.id}"

    if exercise_adaptation.manual_edit is None:
        if len(exercise_adaptation.adjustments) == 0:
            if not isinstance(exercise_adaptation.initial_assistant_response, adaptation.assistant_responses.Success):
                return None
            adapted_exercise = exercise_adaptation.initial_assistant_response.exercise
        else:
            last_adjustment = exercise_adaptation.adjustments[-1]
            if not isinstance(last_adjustment.assistant_response, adaptation.assistant_responses.Success):
                return None
            adapted_exercise = last_adjustment.assistant_response.exercise
    else:
        adapted_exercise = exercise_adaptation.manual_edit

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


def make_external_exercise_data(external_exercise: external_exercises.ExternalExercise) -> JsonDict:
    location = external_exercise.location
    assert isinstance(location, textbooks.ExerciseLocationTextbook)
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
        self.assertEqual(self.get_model(extraction.PdfFile, sha).known_file_names, ["foo.pdf"])

        r = self.client.post(
            "/pdf-files",
            json={"creator": "UnitTest", "fileName": "bar.pdf", "bytesCount": 0, "pagesCount": 0, "sha256": sha},
        )
        self.assertEqual(r.status_code, 200, r.text)
        upload_url = r.json()["uploadUrl"]
        self.assertIsNotNone(upload_url)
        requests.put(upload_url, data=b"")
        s3.head_object(Bucket="jacquev6", Key=f"patty/dev/pdf-files/{sha}")
        self.assertEqual(self.get_model(extraction.PdfFile, sha).known_file_names, ["foo.pdf", "bar.pdf"])

        r = self.client.post(
            "/pdf-files",
            json={"creator": "UnitTest", "fileName": "foo.pdf", "bytesCount": 0, "pagesCount": 0, "sha256": sha},
        )
        self.assertEqual(r.status_code, 200, r.text)
        self.assertIsNone(r.json()["uploadUrl"])
        self.assertEqual(self.get_model(extraction.PdfFile, sha).known_file_names, ["foo.pdf", "bar.pdf"])
