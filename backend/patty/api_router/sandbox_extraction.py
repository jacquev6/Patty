import datetime

import fastapi
import sqlalchemy as sql

from . import previewable_exercise
from .. import adaptation
from .. import classification
from .. import database_utils
from .. import exercises
from .. import extraction
from .. import sandbox
from ..any_json import JsonDict
from ..api_utils import ApiModel, get_by_id, paginate, assert_isinstance
from ..version import PATTY_VERSION


router = fastapi.APIRouter()


@router.get("/extraction-llm-response-schema")
def get_extraction_llm_response_schema() -> JsonDict:
    return extraction.extracted.ExercisesList.model_json_schema()


@router.get("/available-extraction-llm-models")
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


@router.get("/latest-extraction-strategy")
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


@router.post("/extraction-batches")
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
    extraction_batch = sandbox.extraction.SandboxExtractionBatch(
        created_by=req.creator,
        created_at=now,
        settings=settings,
        model=model,
        pdf_file_range=pdf_file_range,
        run_classification=req.run_classification,
        model_for_adaptation=req.model_for_adaptation,
    )
    session.add(extraction_batch)
    for page_number in range(req.first_page, req.first_page + req.pages_count):
        page = extraction.PageExtraction(
            created=sandbox.extraction.PageExtractionCreationBySandboxBatch(
                at=now, sandbox_extraction_batch=extraction_batch
            ),
            pdf_file_range=pdf_file_range,
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
    needs_refresh: bool
    created_by: str
    strategy: ApiExtractionStrategy
    run_classification: bool
    model_for_adaptation: adaptation.llm.ConcreteModel | None

    class Page(ApiModel):
        page_number: int
        assistant_response: extraction.assistant_responses.Response | None

        class Exercise(previewable_exercise.PreviewableExercise):
            pass

        exercises: list[Exercise]

    pages: list[Page]


@router.get("/extraction-batches/{id}")
async def get_extraction_batch(id: str, session: database_utils.SessionDependable) -> GetExtractionBatchResponse:
    extraction_batch = get_by_id(session, sandbox.extraction.SandboxExtractionBatch, id)
    needs_refresh = False
    pages: list[GetExtractionBatchResponse.Page] = []

    for page_extraction_creation in extraction_batch.page_extraction_creations:
        page_extraction = page_extraction_creation.page_extraction
        if page_extraction.assistant_response is None:
            needs_refresh = True

        exercises_ = list(page_extraction.fetch_ordered_exercises())
        api_exercises: list[GetExtractionBatchResponse.Page.Exercise] = []

        for exercise in exercises_:
            assert isinstance(exercise, adaptation.AdaptableExercise)
            latest_classification = exercise.classifications[-1] if exercise.classifications else None

            latest_adaptation = (
                None
                if latest_classification is None or latest_classification.exercise_class is None
                else exercise.fetch_latest_adaptation(latest_classification.exercise_class)
            )

            exercise_class = (
                latest_classification.exercise_class.name
                if latest_classification is not None and latest_classification.exercise_class is not None
                else None
            )

            if extraction_batch.run_classification and exercise_class is None:
                needs_refresh = True

            exercise_class_has_settings = (
                latest_classification is not None
                and latest_classification.exercise_class is not None
                and latest_classification.exercise_class.latest_strategy_settings is not None
            )

            classification_status: previewable_exercise.ClassificationStatus
            if not extraction_batch.run_classification:
                classification_status = previewable_exercise.NotRequested(kind="notRequested")
            elif exercise_class is None:
                classification_status = previewable_exercise.ClassificationInProgress(kind="inProgress")
            elif isinstance(latest_classification, classification.ClassificationByUser):
                classification_status = previewable_exercise.ReclassifiedByUser(
                    kind="byUser",
                    by=latest_classification.username,
                    exercise_class=exercise_class,
                    class_has_settings=exercise_class_has_settings,
                )
            else:
                classification_status = previewable_exercise.ClassifiedByModel(
                    kind="byModel", exercise_class=exercise_class, class_has_settings=exercise_class_has_settings
                )

            adaptation_status: previewable_exercise.AdaptationStatus
            if extraction_batch.model_for_adaptation is None:
                adaptation_status = previewable_exercise.NotRequested(kind="notRequested")
            elif latest_adaptation is None:
                adaptation_status = previewable_exercise.AdaptationNotStarted(kind="notStarted")
            else:
                adaptation_status = previewable_exercise.make_api_adaptation_status(latest_adaptation)

            if adaptation_status.kind == "inProgress":
                needs_refresh = True

            api_exercises.append(
                GetExtractionBatchResponse.Page.Exercise(
                    id=str(exercise.id),
                    page_number=assert_isinstance(
                        exercise.location, exercises.ExerciseLocationMaybePageAndNumber
                    ).page_number,
                    exercise_number=assert_isinstance(
                        exercise.location, exercises.ExerciseLocationMaybePageAndNumber
                    ).exercise_number,
                    full_text=exercise.full_text,
                    classification_status=classification_status,
                    adaptation_status=adaptation_status,
                )
            )

        pages.append(
            GetExtractionBatchResponse.Page(
                page_number=page_extraction.pdf_page_number,
                assistant_response=page_extraction.assistant_response,
                exercises=api_exercises,
            )
        )

    return GetExtractionBatchResponse(
        id=str(extraction_batch.id),
        needs_refresh=needs_refresh,
        created_by=extraction_batch.created_by,
        strategy=ApiExtractionStrategy(
            id=str(extraction_batch.settings.id), model=extraction_batch.model, prompt=extraction_batch.settings.prompt
        ),
        run_classification=extraction_batch.run_classification,
        model_for_adaptation=extraction_batch.model_for_adaptation,
        pages=pages,
    )


@router.post("/extraction-batches/{id}/submit-adaptations-with-recent-settings")
def submit_adaptations_with_recent_settings_in_extraction_batch(
    id: str, session: database_utils.SessionDependable
) -> None:
    extraction_batch = get_by_id(session, sandbox.extraction.SandboxExtractionBatch, id)
    assert extraction_batch.model_for_adaptation is not None
    now = datetime.datetime.now(datetime.timezone.utc)
    for page_extraction_creation in extraction_batch.page_extraction_creations:
        page_extraction = page_extraction_creation.page_extraction
        classification_chunk = (
            session.execute(
                sql.select(classification.ClassificationChunk)
                .join(extraction.ClassificationChunkCreationByPageExtraction)
                .where(extraction.ClassificationChunkCreationByPageExtraction.page_extraction == page_extraction)
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
            assert isinstance(exercise_classification, classification.ClassificationByChunk)
            assert exercise_classification.classification_chunk == classification_chunk

            if (
                len(exercise.adaptations) == 0
                and exercise_classification.exercise_class is not None
                and exercise_classification.exercise_class.latest_strategy_settings is not None
            ):
                session.add(
                    adaptation.Adaptation(
                        created=classification.AdaptationCreationByChunk(
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


@router.put("/extraction-batches/{id}/run-classification")
def put_extraction_batch_run_classification(id: str, session: database_utils.SessionDependable) -> None:
    extraction_batch = get_by_id(session, sandbox.extraction.SandboxExtractionBatch, id)
    assert extraction_batch.run_classification is False
    extraction_batch.run_classification = True
    now = datetime.datetime.now(datetime.timezone.utc)

    for page_extraction_creation in extraction_batch.page_extraction_creations:
        page_extraction = page_extraction_creation.page_extraction
        assert page_extraction.run_classification is False
        page_extraction.run_classification = True
        classification_chunk = classification.ClassificationChunk(
            created=extraction.ClassificationChunkCreationByPageExtraction(at=now, page_extraction=page_extraction),
            model_for_adaptation=None,
        )
        session.add(classification_chunk)

        for exercise_creation in page_extraction.exercise_creations__unordered:
            exercise = exercise_creation.exercise
            assert isinstance(exercise, adaptation.AdaptableExercise)
            session.add(
                classification.ClassificationByChunk(
                    exercise=exercise, at=now, classification_chunk=classification_chunk, exercise_class=None
                )
            )


@router.put("/extraction-batches/{id}/model-for-adaptation")
def put_extraction_batch_model_for_adaptation(
    id: str, req: adaptation.llm.ConcreteModel, session: database_utils.SessionDependable
) -> None:
    extraction_batch = get_by_id(session, sandbox.extraction.SandboxExtractionBatch, id)
    assert extraction_batch.model_for_adaptation is None
    extraction_batch.model_for_adaptation = req
    now = datetime.datetime.now(datetime.timezone.utc)
    for page_extraction_creation in extraction_batch.page_extraction_creations:
        page_extraction = page_extraction_creation.page_extraction
        classification_chunk = (
            session.execute(
                sql.select(classification.ClassificationChunk)
                .join(extraction.ClassificationChunkCreationByPageExtraction)
                .where(extraction.ClassificationChunkCreationByPageExtraction.page_extraction == page_extraction)
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
            assert isinstance(exercise_classification, classification.ClassificationByChunk)
            assert exercise_classification.classification_chunk == classification_chunk

            if (
                len(exercise.adaptations) == 0
                and exercise_classification.exercise_class is not None
                and exercise_classification.exercise_class.latest_strategy_settings is not None
            ):
                session.add(
                    adaptation.Adaptation(
                        created=classification.AdaptationCreationByChunk(
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


@router.get("/extraction-batches")
async def get_extraction_batches(
    session: database_utils.SessionDependable, chunkId: str | None = None
) -> GetExtractionBatchesResponse:
    (batches, next_chunk_id) = paginate(sandbox.extraction.SandboxExtractionBatch, session, chunkId)
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
