from typing import Any, TypeVar
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
from . import orm_models as db
from . import settings
from .adaptation import llm as adaptation_llm
from .adapted import Exercise
from .any_json import JsonDict, JsonList
from .api_utils import ApiModel
from .adaptation.adaptation import (
    Adjustment,
    AssistantInvalidJsonError,
    AssistantNotJsonError,
    AssistantResponse,
    AssistantSuccess,
)
from .adaptation.strategy import ConcreteLlmResponseSpecification, JsonSchemaLlmResponseSpecification
from .adaptation.submission import LlmMessage
from .extraction import llm as extraction_llm
from .extraction import assistant_responses as extraction_responses

__all__ = ["router"]

s3 = boto3.client("s3", config=botocore.client.Config(region_name="eu-west-3", signature_version="s3v4"))

api_router = fastapi.APIRouter(dependencies=[fastapi.Depends(authentication.auth_bearer_dependable)])


@api_router.get("/available-adaptation-llm-models")
def get_available_adaptation_llm_models() -> list[adaptation_llm.ConcreteModel]:
    if settings.ENVIRONMENT == "dev":
        return [
            adaptation_llm.DummyModel(name="dummy-1"),
            adaptation_llm.DummyModel(name="dummy-2"),
            adaptation_llm.MistralAiModel(name="mistral-large-2411"),
            adaptation_llm.MistralAiModel(name="mistral-small-2501"),
            adaptation_llm.OpenAiModel(name="gpt-4o-2024-08-06"),
            adaptation_llm.OpenAiModel(name="gpt-4o-mini-2024-07-18"),
        ]
    else:
        return [
            adaptation_llm.MistralAiModel(name="mistral-large-2411"),
            adaptation_llm.MistralAiModel(name="mistral-small-2501"),
            adaptation_llm.OpenAiModel(name="gpt-4o-2024-08-06"),
            adaptation_llm.OpenAiModel(name="gpt-4o-mini-2024-07-18"),
            adaptation_llm.DummyModel(name="dummy-1"),
            adaptation_llm.DummyModel(name="dummy-2"),
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
    created_by: str | None
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


class LatestAdaptationBatch(ApiModel):
    id: str
    strategy: ApiStrategy
    inputs: list[ApiInput]
    available_strategy_settings: list[ApiStrategySettings]


@api_router.get("/latest-adaptation-batch")
def get_latest_adaptation_batch(user: str, session: database_utils.SessionDependable) -> LatestAdaptationBatch:
    for created_by in [user, "Patty"]:
        adaptation_batch = (
            session.query(db.AdaptationBatch)
            .filter(db.AdaptationBatch.created_by_username == created_by)
            .order_by(-db.AdaptationBatch.id)
            .first()
        )
        if adaptation_batch is not None:
            break
    assert adaptation_batch is not None
    available_strategy_settings = []
    for exercise_class in (
        session.execute(
            sql.select(db.ExerciseClass)
            .where(db.ExerciseClass.latest_strategy_settings != sql.null())
            .order_by(db.ExerciseClass.name)
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
    return LatestAdaptationBatch(
        id=str(adaptation_batch.id),
        strategy=make_api_strategy(adaptation_batch.strategy),
        inputs=[make_api_input(adaptation.exercise) for adaptation in adaptation_batch.adaptations],
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
        else:
            branch_name = req.strategy.settings.name
        exercise_class = session.query(db.ExerciseClass).filter(db.ExerciseClass.name == branch_name).first()
        if exercise_class is None:
            assert branch_name == req.strategy.settings.name
            base_settings = None
            exercise_class = db.ExerciseClass(
                name=branch_name,
                created_by_username=req.creator,
                created_by_classification_batch=None,
                created_at=now,
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
        created_by_username=req.creator,
        created_by_classification_batch=None,
        created_at=now,
        model=req.strategy.model,
        settings=settings,
    )
    session.add(strategy)

    adaptation_batch = db.AdaptationBatch(
        created_by_username=req.creator, created_at=now, strategy=strategy, textbook=None, removed_from_textbook=False
    )
    session.add(adaptation_batch)

    for req_input in req.inputs:
        exercise = db.AdaptableExercise(
            created_by_username=req.creator,
            created_by_page_extraction=None,
            created_at=now,
            textbook=None,
            removed_from_textbook=False,
            page_number=req_input.page_number,
            exercise_number=req_input.exercise_number,
            full_text=req_input.text,
            instruction_hint_example_text=None,
            statement_text=None,
            classified_at=now,
            classified_by_username=req.creator,
            classified_by_classification_batch=None,
            exercise_class=exercise_class,
        )
        session.add(exercise)

        adaptation = db.Adaptation(
            created_by_username=req.creator,
            created_at=now,
            classification_batch=None,
            adaptation_batch=adaptation_batch,
            strategy=strategy,
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
    adaptation_batch = get_by_id(session, db.AdaptationBatch, id)
    return GetAdaptationBatchResponse(
        id=str(adaptation_batch.id),
        created_by=adaptation_batch.created_by_username,
        strategy=make_api_strategy(adaptation_batch.strategy),
        adaptations=[make_api_adaptation(adaptation) for adaptation in adaptation_batch.adaptations],
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


T = typing.TypeVar("T", bound=db.AdaptationBatch | db.ClassificationBatch | db.ExtractionBatch)


def paginate(
    model: type[T], request: sql.Select[tuple[T]], session: database_utils.SessionDependable, chunk_id: str | None
) -> tuple[list[T], str | None]:
    chunk_size = 20
    request = request.order_by(-model.id).limit(chunk_size + 1)

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
    (batches, next_chunk_id) = paginate(
        db.AdaptationBatch,
        sql.select(db.AdaptationBatch).filter(db.AdaptationBatch.textbook_id == sql.null()),
        session,
        chunkId,
    )

    return GetAdaptationBatchesResponse(
        adaptation_batches=[
            GetAdaptationBatchesResponse.AdaptationBatch(
                id=str(adaptation_batch.id),
                created_by=adaptation_batch.created_by_username,
                created_at=adaptation_batch.created_at,
                model=adaptation_batch.strategy.model,
                strategy_settings_name=make_api_strategy_settings_name(adaptation_batch.strategy.settings),
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
    classification_batch = db.ClassificationBatch(
        created_by_username=req.creator,
        created_by_page_extraction=None,
        created_at=now,
        model_for_adaptation=req.model_for_adaptation,
    )
    session.add(classification_batch)

    for req_input in req.inputs:
        exercise = db.AdaptableExercise(
            created_by_username=req.creator,
            created_by_page_extraction=None,
            created_at=now,
            textbook=None,
            removed_from_textbook=False,
            page_number=req_input.page_number,
            exercise_number=req_input.exercise_number,
            full_text=req_input.instruction_hint_example_text + "\n" + req_input.statement_text,
            instruction_hint_example_text=req_input.instruction_hint_example_text,
            statement_text=req_input.statement_text,
            classified_at=None,
            classified_by_username=None,
            classified_by_classification_batch=classification_batch,
            exercise_class=None,
        )
        session.add(exercise)

    session.flush()

    return PostClassificationBatchResponse(id=str(classification_batch.id))


class GetClassificationBatchResponse(ApiModel):
    id: str
    created_by: str | None
    model_for_adaptation: adaptation_llm.ConcreteModel | None

    class Exercise(ApiModel):
        page_number: int | None
        exercise_number: str | None
        full_text: str
        exercise_class: str | None
        exercise_class_has_settings: bool
        adaptation: ApiAdaptation | None

    exercises: list[Exercise]


@api_router.get("/classification-batches/{id}")
async def get_classification_batch(
    id: str, session: database_utils.SessionDependable
) -> GetClassificationBatchResponse:
    classification_batch = get_by_id(session, db.ClassificationBatch, id)
    return GetClassificationBatchResponse(
        id=str(classification_batch.id),
        created_by=classification_batch.created_by_username,
        model_for_adaptation=classification_batch.model_for_adaptation,
        exercises=[
            GetClassificationBatchResponse.Exercise(
                page_number=exercise.page_number,
                exercise_number=exercise.exercise_number,
                full_text=exercise.full_text,
                exercise_class=None if exercise.exercise_class is None else exercise.exercise_class.name,
                exercise_class_has_settings=(
                    exercise.exercise_class is not None and exercise.exercise_class.latest_strategy_settings is not None
                ),
                adaptation=None if exercise.adaptation is None else make_api_adaptation(exercise.adaptation),
            )
            for exercise in classification_batch.exercises
        ],
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
    (batches, next_chunk_id) = paginate(
        db.ClassificationBatch,
        sql.select(db.ClassificationBatch).filter(db.ClassificationBatch.created_by_username != sql.null()),
        session,
        chunkId,
    )

    return GetClassificationBatchesResponse(
        classification_batches=[
            GetClassificationBatchesResponse.ClassificationBatch(
                id=str(classification_batch.id),
                created_by=classification_batch.created_by_username,
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
    pdf_file = session.get(db.PdfFile, req.sha256)
    if pdf_file is None:
        pdf_file = db.PdfFile(
            sha256=req.sha256,
            created_by_username=req.creator,
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
    if settings.ENVIRONMENT == "dev":
        return [
            extraction_llm.DummyModel(name="dummy-1"),
            extraction_llm.DummyModel(name="dummy-2"),
            extraction_llm.GeminiModel(name="gemini-2.0-flash"),
        ]
    else:
        return [
            extraction_llm.GeminiModel(name="gemini-2.0-flash"),
            extraction_llm.DummyModel(name="dummy-1"),
            extraction_llm.DummyModel(name="dummy-2"),
        ]


class ApiExtractionStrategy(ApiModel):
    id: str
    model: extraction_llm.ConcreteModel
    prompt: str


@api_router.get("/latest-extraction-strategy")
def get_latest_extraction_strategy(session: database_utils.SessionDependable) -> ApiExtractionStrategy:
    strategy = session.execute(sql.select(db.ExtractionStrategy).order_by(-db.ExtractionStrategy.id)).scalars().first()
    assert strategy is not None
    return ApiExtractionStrategy(id=str(strategy.id), model=strategy.model, prompt=strategy.prompt)


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
    pdf_file_range = db.PdfFileRange(
        created_by_username=req.creator,
        created_at=now,
        pdf_file_sha256=req.pdf_file_sha256,
        pdf_file_first_page_number=req.first_page,
        pages_count=req.pages_count,
    )
    session.add(pdf_file_range)
    strategy = session.get(db.ExtractionStrategy, req.strategy.id)
    if strategy is None or strategy.model != req.strategy.model or strategy.prompt != req.strategy.prompt:
        strategy = db.ExtractionStrategy(
            created_by_username=req.creator, created_at=now, model=req.strategy.model, prompt=req.strategy.prompt
        )
        session.add(strategy)
    extraction_batch = db.ExtractionBatch(
        created_by_username=req.creator,
        created_at=now,
        strategy=strategy,
        range=pdf_file_range,
        run_classification=req.run_classification,
        model_for_adaptation=req.model_for_adaptation,
    )
    session.add(extraction_batch)
    for page_number in range(req.first_page, req.first_page + req.pages_count):
        page = db.PageExtraction(
            created_by_username=req.creator,
            created_at=now,
            extraction_batch=extraction_batch,
            page_number=page_number,
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
            page_number: int | None
            exercise_number: str | None
            full_text: str
            exercise_class: str | None
            exercise_class_has_settings: bool
            adaptation: ApiAdaptation | None

        exercises: list[Exercise]

    pages: list[Page]


@api_router.get("/extraction-batches/{id}")
async def get_extraction_batch(id: str, session: database_utils.SessionDependable) -> GetExtractionBatchResponse:
    extraction_batch = get_by_id(session, db.ExtractionBatch, id)
    pages = [
        GetExtractionBatchResponse.Page(
            page_number=page_extraction.page_number,
            assistant_response=page_extraction.assistant_response,
            exercises=[
                GetExtractionBatchResponse.Page.Exercise(
                    page_number=exercise.page_number,
                    exercise_number=exercise.exercise_number,
                    full_text=exercise.full_text,
                    exercise_class=None if exercise.exercise_class is None else exercise.exercise_class.name,
                    exercise_class_has_settings=(
                        exercise.exercise_class is not None
                        and exercise.exercise_class.latest_strategy_settings is not None
                    ),
                    adaptation=None if exercise.adaptation is None else make_api_adaptation(exercise.adaptation),
                )
                for exercise in page_extraction.exercises
            ],
        )
        for page_extraction in extraction_batch.page_extractions
    ]
    return GetExtractionBatchResponse(
        id=str(extraction_batch.id),
        created_by=extraction_batch.created_by_username,
        strategy=ApiExtractionStrategy(
            id=str(extraction_batch.strategy.id),
            model=extraction_batch.strategy.model,
            prompt=extraction_batch.strategy.prompt,
        ),
        run_classification=extraction_batch.run_classification,
        model_for_adaptation=extraction_batch.model_for_adaptation,
        pages=pages,
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
    (batches, next_chunk_id) = paginate(
        db.ExtractionBatch,
        sql.select(db.ExtractionBatch).filter(db.ExtractionBatch.created_by_username != sql.null()),
        session,
        chunkId,
    )
    return GetExtractionBatchesResponse(
        extraction_batches=[
            GetExtractionBatchesResponse.ExtractionBatch(
                id=str(extraction_batch.id),
                created_by=extraction_batch.created_by_username,
                created_at=extraction_batch.created_at,
            )
            for extraction_batch in batches
        ],
        next_chunk_id=next_chunk_id,
    )


class PostTextbookRequest(ApiModel):
    creator: str
    title: str


class PostTextbookResponse(ApiModel):
    id: str


@api_router.post("/textbooks")
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

    class AdaptationBatch(ApiModel):
        id: str
        strategy: ApiStrategy
        adaptations: list[ApiAdaptation]
        removed_from_textbook: bool

    adaptation_batches: list[AdaptationBatch]

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


class PostTextbookAdaptationBatchRequest(ApiModel):
    creator: str
    model: adaptation_llm.ConcreteModel
    branch_name: str
    inputs: list[ApiInput]


@api_router.post("/textbooks/{id}/adaptation-batches")
def post_textbook_adaptation_batch(
    id: str,
    req: PostTextbookAdaptationBatchRequest,
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
        created_by_classification_batch=None,
        created_at=now,
        model=req.model,
        settings=exercise_class.latest_strategy_settings,
    )
    session.add(strategy)

    adaptation_batch = db.AdaptationBatch(
        textbook=textbook,
        removed_from_textbook=False,
        created_by_username=req.creator,
        created_at=now,
        strategy=strategy,
    )
    session.add(adaptation_batch)

    for req_input in req.inputs:
        exercise = db.AdaptableExercise(
            created_by_username=req.creator,
            created_by_page_extraction=None,
            created_at=now,
            textbook=textbook,
            removed_from_textbook=False,
            page_number=req_input.page_number,
            exercise_number=req_input.exercise_number,
            full_text=req_input.text,
            instruction_hint_example_text=None,
            statement_text=None,
            classified_at=now,
            classified_by_username=req.creator,
            classified_by_classification_batch=None,
            exercise_class=exercise_class,
        )
        session.add(exercise)

        adaptation = db.Adaptation(
            created_by_username=req.creator,
            created_at=now,
            classification_batch=None,
            adaptation_batch=adaptation_batch,
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


@api_router.put("/textbooks/{textbook_id}/adaptation-batches/{adaptation_batch_id}/removed")
def put_textbook_adaptation_batch_removed(
    textbook_id: str, adaptation_batch_id: str, removed: bool, session: database_utils.SessionDependable
) -> ApiTextbook:
    textbook = get_by_id(session, db.Textbook, textbook_id)
    adaptation_batch = get_by_id(session, db.AdaptationBatch, adaptation_batch_id)
    assert adaptation_batch.textbook == textbook
    adaptation_batch.removed_from_textbook = removed
    return make_api_textbook(textbook)


@api_router.put("/textbooks/{textbook_id}/adaptations/{adaptation_id}/removed")
def put_textbook_adaptation_removed(
    textbook_id: str, adaptation_id: str, removed: bool, session: database_utils.SessionDependable
) -> ApiTextbook:
    textbook = get_by_id(session, db.Textbook, textbook_id)
    adaptation = get_by_id(session, db.Adaptation, adaptation_id)
    assert adaptation.adaptation_batch is not None
    assert adaptation.adaptation_batch.textbook == textbook
    adaptation.exercise.removed_from_textbook = removed
    return make_api_textbook(textbook)


class PostTextbookExternalExercisesRequest(ApiModel):
    creator: str
    page_number: int | None
    exercise_number: str | None
    original_file_name: str


class PostTextbookExternalExercisesResponse(ApiModel):
    put_url: str


@api_router.post("/textbooks/{textbook_id}/external-exercises")
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


@api_router.put("/textbooks/{textbook_id}/external-exercises/{external_exercise_id}/removed")
def put_textbook_external_exercises_removed(
    textbook_id: str, external_exercise_id: str, removed: bool, session: database_utils.SessionDependable
) -> ApiTextbook:
    textbook = get_by_id(session, db.Textbook, textbook_id)
    external_exercise = get_by_id(session, db.ExternalExercise, external_exercise_id)
    assert external_exercise.textbook == textbook
    external_exercise.removed_from_textbook = removed
    return make_api_textbook(textbook)


@api_router.get("/adaptations/{id}")
async def get_adaptation(id: str, session: database_utils.SessionDependable) -> ApiAdaptation:
    return make_api_adaptation(get_by_id(session, db.Adaptation, id))


class PostAdaptationAdjustmentRequest(ApiModel):
    adjustment: str


@api_router.post("/adaptations/{id}/adjustment")
async def post_adaptation_adjustment(
    id: str, req: PostAdaptationAdjustmentRequest, session: database_utils.SessionDependable
) -> ApiAdaptation:
    adaptation = get_by_id(session, db.Adaptation, id)
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
        adaptation_llm.SystemMessage(content=adaptation.strategy.settings.system_prompt),
        adaptation_llm.UserMessage(content=adaptation.exercise.full_text),
        make_assistant_message(adaptation.initial_assistant_response),
    ]
    for adjustment in adaptation.adjustments:
        assert isinstance(adjustment.assistant_response, AssistantSuccess)
        messages.append(adaptation_llm.UserMessage(content=adjustment.user_prompt))
        make_assistant_message(adjustment.assistant_response)
    messages.append(adaptation_llm.UserMessage(content=req.adjustment))

    try:
        response = await adaptation.strategy.model.complete(
            messages, adaptation.strategy.settings.response_specification.make_response_format()
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
    adaptation = get_by_id(session, db.Adaptation, id)

    raw_llm_conversations = list(adaptation.raw_llm_conversations)
    raw_llm_conversations.pop()
    adaptation.raw_llm_conversations = raw_llm_conversations

    adjustments = list(adaptation.adjustments)
    adjustments.pop()
    adaptation.adjustments = adjustments

    return make_api_adaptation(adaptation)


@api_router.put("/adaptations/{id}/manual-edit")
def put_adaptation_manual_edit(id: str, req: Exercise, session: database_utils.SessionDependable) -> ApiAdaptation:
    adaptation = get_by_id(session, db.Adaptation, id)
    adaptation.manual_edit = req
    return make_api_adaptation(adaptation)


@api_router.delete("/adaptations/{id}/manual-edit")
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
        classification_batch_id=(
            None if adaptation.classification_batch_id is None else str(adaptation.classification_batch_id)
        ),
        adaptation_batch_id=None if adaptation.adaptation_batch_id is None else str(adaptation.adaptation_batch_id),
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
        adaptation_batches=[
            ApiTextbook.AdaptationBatch(
                id=str(adaptation_batch.id),
                strategy=make_api_strategy(adaptation_batch.strategy),
                adaptations=[make_api_adaptation(adaptation) for adaptation in adaptation_batch.adaptations],
                removed_from_textbook=adaptation_batch.removed_from_textbook,
            )
            for adaptation_batch in textbook.adaptation_batches
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
            if isinstance(external_exercise, db.ExternalExercise)
        ],
    )


export_router = fastapi.APIRouter(dependencies=[fastapi.Depends(authentication.auth_param_dependable)])


export_batch_template_file_path = os.path.join(os.path.dirname(__file__), "export", "templates", "batch", "index.html")


@export_router.get("/extraction-batch/{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_extraction_batch(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    data = list(
        filter(
            None,
            (
                make_adapted_exercise_data(exercise.adaptation)
                for page in get_by_id(session, db.ExtractionBatch, id).page_extractions
                for exercise in page.exercises
                if exercise.adaptation is not None
            ),
        )
    )

    content = render_template(export_batch_template_file_path, "BATCH_EXPORT_DATA", data)

    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="test-extraction-batch-{id}.html"'

    return fastapi.responses.HTMLResponse(content=content, headers=headers)


@export_router.get("/adaptation-batch/{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_adaptation_batch(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    data = list(
        filter(
            None,
            (
                make_adapted_exercise_data(adaptation)
                for adaptation in get_by_id(session, db.AdaptationBatch, id).adaptations
            ),
        )
    )

    content = render_template(export_batch_template_file_path, "BATCH_EXPORT_DATA", data)

    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="test-adaptation-batch-{id}.html"'

    return fastapi.responses.HTMLResponse(content=content, headers=headers)


@export_router.get("/classification-batch/{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_classification_batch(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    data = list(
        filter(
            None,
            (
                make_adapted_exercise_data(exercise.adaptation)
                for exercise in get_by_id(session, db.ClassificationBatch, id).exercises
                if exercise.adaptation is not None
            ),
        )
    )

    content = render_template(export_batch_template_file_path, "BATCH_EXPORT_DATA", data)

    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="test-classification-batch-{id}.html"'

    return fastapi.responses.HTMLResponse(content=content, headers=headers)


export_adaptation_template_file_path = os.path.join(
    os.path.dirname(__file__), "export", "templates", "adaptation", "index.html"
)


@export_router.get("/adaptation/{id}.html", response_class=fastapi.responses.HTMLResponse)
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


export_textbook_template_file_path = os.path.join(
    os.path.dirname(__file__), "export", "templates", "textbook", "index.html"
)


@export_router.get("/textbook/{id}.html", response_class=fastapi.responses.HTMLResponse)
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
                        exercise.adaptation.adaptation_batch is not None
                        and exercise.adaptation.adaptation_batch.removed_from_textbook
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


class ApiTestCase(database_utils.TestCaseWithDatabase):
    def setUp(self) -> None:
        super().setUp()
        self.app = fastapi.FastAPI(database_engine=self.engine)
        self.app.include_router(router)
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
        self.assertEqual(self.get_model(db.PdfFile, sha).known_file_names, ["foo.pdf"])

        r = self.client.post(
            "/pdf-files",
            json={"creator": "UnitTest", "fileName": "bar.pdf", "bytesCount": 0, "pagesCount": 0, "sha256": sha},
        )
        self.assertEqual(r.status_code, 200, r.text)
        upload_url = r.json()["uploadUrl"]
        self.assertIsNotNone(upload_url)
        requests.put(upload_url, data=b"")
        s3.head_object(Bucket="jacquev6", Key=f"patty/dev/pdf-files/{sha}")
        self.assertEqual(self.get_model(db.PdfFile, sha).known_file_names, ["foo.pdf", "bar.pdf"])

        r = self.client.post(
            "/pdf-files",
            json={"creator": "UnitTest", "fileName": "foo.pdf", "bytesCount": 0, "pagesCount": 0, "sha256": sha},
        )
        self.assertEqual(r.status_code, 200, r.text)
        self.assertIsNone(r.json()["uploadUrl"])
        self.assertEqual(self.get_model(db.PdfFile, sha).known_file_names, ["foo.pdf", "bar.pdf"])
