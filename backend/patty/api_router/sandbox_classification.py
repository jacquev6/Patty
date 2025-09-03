import datetime

import fastapi

from .. import adaptation
from .. import classification
from .. import database_utils
from .. import exercises
from .. import sandbox
from ..api_utils import ApiModel, get_by_id, paginate, assert_isinstance
from .adaptations import ApiAdaptation, make_api_adaptation


router = fastapi.APIRouter()


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


@router.post("/classification-batches")
def create_classification_batch(
    req: PostClassificationBatchRequest, session: database_utils.SessionDependable
) -> PostClassificationBatchResponse:
    now = datetime.datetime.now(datetime.timezone.utc)
    classification_batch = sandbox.classification.SandboxClassificationBatch(
        created_by=req.creator, created_at=now, model_for_adaptation=req.model_for_adaptation
    )
    session.add(classification_batch)

    classification_chunk = classification.ClassificationChunk(
        created=sandbox.classification.ClassificationChunkCreationBySandboxBatch(
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
            full_text=req_input.instruction_hint_example_text + "\n" + req_input.statement_text,
            instruction_hint_example_text=req_input.instruction_hint_example_text,
            statement_text=req_input.statement_text,
        )
        session.add(exercise)
        session.add(
            classification.ClassificationByChunk(
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


@router.get("/classification-batches/{id}")
async def get_classification_batch(
    id: str, session: database_utils.SessionDependable
) -> GetClassificationBatchResponse:
    classification_batch = get_by_id(session, sandbox.classification.SandboxClassificationBatch, id)

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
                    if isinstance(latest_classification, classification.ClassificationByUser)
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


@router.post(
    "/classification-batches/{id}/submit-adaptations-with-recent-settings", status_code=fastapi.status.HTTP_200_OK
)
def submit_adaptations_with_recent_settings_in_classification_batch(
    id: str, session: database_utils.SessionDependable
) -> None:
    classification_batch = get_by_id(session, sandbox.classification.SandboxClassificationBatch, id)
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
                adaptation.Adaptation(
                    created=classification.AdaptationCreationByChunk(at=now, classification_chunk=classification_chunk),
                    exercise=exercise,
                    settings=exercise_classification.exercise_class.latest_strategy_settings,
                    model=classification_batch.model_for_adaptation,
                    raw_llm_conversations=[],
                    initial_assistant_response=None,
                    adjustments=[],
                    manual_edit=None,
                )
            )


@router.put("/classification-batches/{id}/model-for-adaptation", status_code=fastapi.status.HTTP_200_OK)
def put_classification_batch_model_for_adaptation(
    id: str, req: adaptation.llm.ConcreteModel, session: database_utils.SessionDependable
) -> None:
    classification_batch = get_by_id(session, sandbox.classification.SandboxClassificationBatch, id)
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
                adaptation.Adaptation(
                    created=classification.AdaptationCreationByChunk(at=now, classification_chunk=classification_chunk),
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


@router.get("/classification-batches")
async def get_classification_batches(
    session: database_utils.SessionDependable, chunkId: str | None = None
) -> GetClassificationBatchesResponse:
    (batches, next_chunk_id) = paginate(sandbox.classification.SandboxClassificationBatch, session, chunkId)

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
