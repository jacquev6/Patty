# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

import datetime
import typing

import fastapi
import sqlalchemy as sql

from . import previewable_exercise
from .. import adaptation
from .. import classification
from .. import database_utils
from .. import dispatching as dispatch
from .. import exercises
from .. import logs
from .. import sandbox
from .. import textbooks
from ..any_json import JsonDict
from ..api_utils import ApiModel, get_by_id, paginate
from ..version import PATTY_VERSION
from .adaptations import (
    ApiStrategySettings,
    ApiStrategy,
    ApiInput,
    make_api_strategy,
    make_api_strategy_settings,
    make_api_strategy_settings_identity,
    make_api_input,
)


router = fastapi.APIRouter()


@router.get("/available-adaptation-llm-models")
def get_available_adaptation_llm_models() -> (
    list[tuple[adaptation.llm.ConcreteModel, list[typing.Literal["text", "json-object", "json-schema"]]]]
):
    if PATTY_VERSION == "dev":
        return [
            (adaptation.llm.DummyModel(provider="dummy", name="dummy-1"), ["text", "json-object", "json-schema"]),
            (adaptation.llm.DummyModel(provider="dummy", name="dummy-2"), ["text", "json-object", "json-schema"]),
            (adaptation.llm.DummyModel(provider="dummy", name="dummy-3"), ["text", "json-object", "json-schema"]),
            (
                adaptation.llm.DummyModel(provider="dummy", name="dummy-for-images"),
                ["text", "json-object", "json-schema"],
            ),
            (adaptation.llm.GeminiModel(provider="gemini", name="gemini-2.5-flash"), ["text", "json-object"]),
            (adaptation.llm.GeminiModel(provider="gemini", name="gemini-2.0-flash"), ["text", "json-object"]),
            (
                adaptation.llm.MistralAiModel(provider="mistralai", name="mistral-large-2411"),
                ["text", "json-object", "json-schema"],
            ),
            (
                adaptation.llm.MistralAiModel(provider="mistralai", name="mistral-medium-2505"),
                ["text", "json-object", "json-schema"],
            ),
            (
                adaptation.llm.MistralAiModel(provider="mistralai", name="mistral-medium-2508"),
                ["text", "json-object", "json-schema"],
            ),
            (
                adaptation.llm.MistralAiModel(provider="mistralai", name="mistral-small-2501"),
                ["text", "json-object", "json-schema"],
            ),
            (
                adaptation.llm.MistralAiModel(provider="mistralai", name="mistral-small-2503"),
                ["text", "json-object", "json-schema"],
            ),
            (
                adaptation.llm.MistralAiModel(provider="mistralai", name="mistral-small-2506"),
                ["text", "json-object", "json-schema"],
            ),
            (
                adaptation.llm.OpenAiModel(provider="openai", name="gpt-4o-2024-08-06"),
                ["text", "json-object", "json-schema"],
            ),
            (
                adaptation.llm.OpenAiModel(provider="openai", name="gpt-4o-mini-2024-07-18"),
                ["text", "json-object", "json-schema"],
            ),
            (
                adaptation.llm.OpenAiModel(provider="openai", name="gpt-4.1-2025-04-14"),
                ["text", "json-object", "json-schema"],
            ),
            (
                adaptation.llm.OpenAiModel(provider="openai", name="gpt-4.1-mini-2025-04-14"),
                ["text", "json-object", "json-schema"],
            ),
            (
                adaptation.llm.OpenAiModel(provider="openai", name="gpt-4.1-nano-2025-04-14"),
                ["text", "json-object", "json-schema"],
            ),
        ]
    else:
        return [
            (adaptation.llm.GeminiModel(provider="gemini", name="gemini-2.5-flash"), ["text", "json-object"]),
            (adaptation.llm.GeminiModel(provider="gemini", name="gemini-2.0-flash"), ["text", "json-object"]),
            (
                adaptation.llm.MistralAiModel(provider="mistralai", name="mistral-large-2411"),
                ["text", "json-object", "json-schema"],
            ),
            (
                adaptation.llm.MistralAiModel(provider="mistralai", name="mistral-small-2501"),
                ["text", "json-object", "json-schema"],
            ),
            (
                adaptation.llm.OpenAiModel(provider="openai", name="gpt-4o-2024-08-06"),
                ["text", "json-object", "json-schema"],
            ),
            (
                adaptation.llm.OpenAiModel(provider="openai", name="gpt-4o-mini-2024-07-18"),
                ["text", "json-object", "json-schema"],
            ),
            (adaptation.llm.DummyModel(provider="dummy", name="dummy-1"), ["text", "json-object", "json-schema"]),
            (adaptation.llm.DummyModel(provider="dummy", name="dummy-2"), ["text", "json-object", "json-schema"]),
        ]


@router.post("/adaptation-llm-response-schema")
def make_adaptation_llm_response_schema(
    response_specification: adaptation.strategy.ConcreteLlmResponseSpecification,
) -> JsonDict:
    return response_specification.make_response_type().model_json_schema()


class BaseAdaptationBatch(ApiModel):
    id: str
    strategy: ApiStrategy
    inputs: list[ApiInput]
    available_strategy_settings: list[ApiStrategySettings]


@router.get("/base-adaptation-batch")
def get_base_adaptation_batch(
    user: str, session: database_utils.SessionDependable, base: str | None = None
) -> BaseAdaptationBatch:
    request = sql.select(sandbox.adaptation.SandboxAdaptationBatch)
    if base is None:
        request = request.where(
            (sandbox.adaptation.SandboxAdaptationBatch.created_by == user)
            | (sandbox.adaptation.SandboxAdaptationBatch.id == 1)
        ).order_by(-sandbox.adaptation.SandboxAdaptationBatch.id)
    else:
        try:
            base_id = int(base)
        except ValueError:
            raise fastapi.HTTPException(status_code=404, detail="Base adaptation batch not found")
        else:
            request = request.where(sandbox.adaptation.SandboxAdaptationBatch.id == base_id)

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


@router.post("/adaptation-batches")
async def post_adaptation_batch(
    req: PostAdaptationBatchRequest, session: database_utils.SessionDependable
) -> PostAdaptationBatchResponse:
    now = datetime.datetime.now(datetime.timezone.utc)

    if req.strategy.settings.identity is None:
        base_settings = None
        exercise_class = None
    else:
        branch_name = req.strategy.settings.identity.name
        exercise_class = (
            session.query(adaptation.ExerciseClass).filter(adaptation.ExerciseClass.name == branch_name).first()
        )
        if exercise_class is None:
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
            elif req.strategy.settings.identity.version == "current":
                base_settings = exercise_class.latest_strategy_settings
            else:
                base_settings = exercise_class.latest_strategy_settings.parent

    if (
        base_settings is None
        or base_settings.system_prompt != req.strategy.settings.system_prompt
        or base_settings.response_specification != req.strategy.settings.response_specification
    ):
        settings = adaptation.AdaptationSettings(
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

    adaptation_batch = sandbox.adaptation.SandboxAdaptationBatch(
        created_by=req.creator, created_at=now, settings=settings, model=req.strategy.model
    )
    session.add(adaptation_batch)

    for req_input in req.inputs:
        exercise = adaptation.AdaptableExercise(
            created=exercises.ExerciseCreationByUser(at=now, username=req.creator),
            location=exercises.ExerciseLocationMaybePageAndNumber(
                page_number=req_input.page_number, exercise_number=req_input.exercise_number
            ),
            full_text=req_input.text,
            instruction_hint_example_text=None,
            statement_text=None,
        )
        session.add(exercise)

        if exercise_class is not None:
            session.add(
                classification.ClassificationByUser(
                    exercise=exercise, at=now, username=req.creator, exercise_class=exercise_class
                )
            )

        session.add(
            adaptation.Adaptation(
                created=sandbox.adaptation.AdaptationCreationBySandboxBatch(
                    at=now, sandbox_adaptation_batch=adaptation_batch
                ),
                settings=settings,
                model=req.strategy.model,
                exercise=exercise,
                raw_llm_conversations=[],
                initial_assistant_response=None,
                initial_timing=None,
                adjustments=[],
                manual_edit=None,
                approved_by=None,
                approved_at=None,
            )
        )

    session.flush()

    return PostAdaptationBatchResponse(id=str(adaptation_batch.id))


class GetAdaptationBatchResponse(ApiModel):
    id: str
    needs_refresh: bool
    created_by: str
    strategy: ApiStrategy

    class Exercise(previewable_exercise.PreviewableExercise):
        pass

    exercises: list[Exercise]

    class Timing(ApiModel):
        adaptations: list[logs.TimingData | None]

    timing: Timing


@router.get("/adaptation-batches/{id}")
async def get_adaptation_batch(id: str, session: database_utils.SessionDependable) -> GetAdaptationBatchResponse:
    adaptation_batch = get_by_id(session, sandbox.adaptation.SandboxAdaptationBatch, id)

    api_exercises: list[GetAdaptationBatchResponse.Exercise] = []
    timing = GetAdaptationBatchResponse.Timing(adaptations=[])
    needs_refresh = False
    for adaptation_creation in adaptation_batch.adaptation_creations:
        adaptation_status = previewable_exercise.make_api_adaptation_status(adaptation_creation.exercise_adaptation)

        if adaptation_status.kind == "inProgress":
            needs_refresh = True

        exercise = adaptation_creation.exercise_adaptation.exercise
        assert isinstance(
            exercise.location, (textbooks.ExerciseLocationTextbook, exercises.ExerciseLocationMaybePageAndNumber)
        )

        api_exercises.append(
            GetAdaptationBatchResponse.Exercise(
                id=str(exercise.id),
                page_number=exercise.location.page_number,
                exercise_number=exercise.location.exercise_number,
                full_text=exercise.full_text,
                images_urls=previewable_exercise.gather_images_urls("http", exercise),
                classification_status=previewable_exercise.NotRequested(kind="notRequested"),
                adaptation_status=adaptation_status,
            )
        )

        timing.adaptations.append(adaptation_creation.exercise_adaptation.initial_timing)

    return GetAdaptationBatchResponse(
        id=str(adaptation_batch.id),
        needs_refresh=needs_refresh,
        created_by=adaptation_batch.created_by,
        strategy=make_api_strategy(adaptation_batch.settings, adaptation_batch.model),
        exercises=api_exercises,
        timing=timing,
    )


class GetAdaptationBatchesResponse(ApiModel):
    class AdaptationBatch(ApiModel):
        id: str
        created_by: str
        created_at: datetime.datetime
        model: adaptation.llm.ConcreteModel
        strategy_settings_identity: ApiStrategySettings.Identity | None

    adaptation_batches: list[AdaptationBatch]
    next_chunk_id: str | None


@router.get("/exercise-classes")
def get_exercise_classes(session: database_utils.SessionDependable) -> list[str]:
    request = sql.select(adaptation.ExerciseClass).order_by(adaptation.ExerciseClass.name)
    return [exercise_class.name for exercise_class in session.execute(request).scalars().all()]


class PutAdaptableExerciseClassRequest(ApiModel):
    creator: str
    className: str


@router.put("/adaptable-exercises/{id}/exercise-class")
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

    session.add(
        classification.ClassificationByUser(
            exercise=exercise, at=now, username=req.creator, exercise_class=exercise_class
        )
    )

    if exercise_class.latest_strategy_settings is not None:
        adaptation_model: adaptation.llm.ConcreteModel | None = None
        created: adaptation.AdaptationCreation | None = None

        if len(exercise.adaptations) != 0:
            some_previous_adaptation = exercise.adaptations[0]
            adaptation_model = some_previous_adaptation.model
            created = dispatch.adaptation_creation(
                some_previous_adaptation.created,
                by_chunk=lambda ac: classification.AdaptationCreationByChunk(
                    at=now, classification_chunk=ac.classification_chunk
                ),
                by_sandbox_batch=lambda ac: sandbox.adaptation.AdaptationCreationBySandboxBatch(
                    at=now, sandbox_adaptation_batch=ac.sandbox_adaptation_batch
                ),
            )
        elif len(exercise.classifications) != 0:
            automatic_classifications = list(
                filter(lambda c: isinstance(c, classification.ClassificationByChunk), exercise.classifications)
            )
            if len(automatic_classifications) != 0:
                some_classification = automatic_classifications[0]
                assert isinstance(some_classification, classification.ClassificationByChunk)
                adaptation_model = some_classification.classification_chunk.model_for_adaptation
                created = classification.AdaptationCreationByChunk(
                    at=now, classification_chunk=some_classification.classification_chunk
                )

        if adaptation_model is not None and created is not None:
            session.add(
                adaptation.Adaptation(
                    created=created,
                    settings=exercise_class.latest_strategy_settings,
                    model=adaptation_model,
                    exercise=exercise,
                    raw_llm_conversations=[],
                    initial_assistant_response=None,
                    initial_timing=None,
                    adjustments=[],
                    manual_edit=None,
                    approved_by=None,
                    approved_at=None,
                )
            )


@router.get("/adaptation-batches")
async def get_adaptation_batches(
    session: database_utils.SessionDependable, chunkId: str | None = None
) -> GetAdaptationBatchesResponse:
    (batches, next_chunk_id) = paginate(sandbox.adaptation.SandboxAdaptationBatch, session, chunkId)

    return GetAdaptationBatchesResponse(
        adaptation_batches=[
            GetAdaptationBatchesResponse.AdaptationBatch(
                id=str(adaptation_batch.id),
                created_by=adaptation_batch.created_by,
                created_at=adaptation_batch.created_at,
                model=adaptation_batch.model,
                strategy_settings_identity=make_api_strategy_settings_identity(adaptation_batch.settings),
            )
            for adaptation_batch in batches
        ],
        next_chunk_id=next_chunk_id,
    )
