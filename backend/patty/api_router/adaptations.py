# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

import datetime
from typing import Literal
import typing

import fastapi
from starlette import status

from . import previewable_exercise
from .. import adaptation
from .. import classification
from ..retry import RetryableError
from ..sandbox import adaptation as sandbox_adaptation
from .. import database_utils
from .. import dispatching as dispatch
from .. import exercises
from .. import textbooks
from ..any_json import JsonList
from ..api_utils import ApiModel, get_by_id


router = fastapi.APIRouter()


class ApiStrategySettings(ApiModel):
    class Identity(ApiModel):
        name: str
        version: Literal["current", "previous", "older"]

    identity: Identity | None
    system_prompt: str
    response_specification: adaptation.strategy.ConcreteLlmResponseSpecification


class ApiStrategy(ApiModel):
    model: adaptation.llm.ConcreteModel
    settings: ApiStrategySettings


class ApiInput(ApiModel):
    page_number: int | None
    exercise_number: str | None
    text: str


class ApiInputOut(ApiModel):
    page_number: int | None
    exercise_number: str | None
    text: list[str]


class ApiAdaptation(ApiModel):
    id: str

    class BelongsToExtractionBatch(ApiModel):
        kind: Literal["extraction-batch"]
        id: str

    class BelongsToClassificationBatch(ApiModel):
        kind: Literal["classification-batch"]
        id: str

    class BelongsToAdaptationBatch(ApiModel):
        kind: Literal["adaptation-batch"]
        id: str

    class BelongsToTextbook(ApiModel):
        kind: Literal["textbook"]
        id: str
        title: str
        page: int

    belongs_to: BelongsToExtractionBatch | BelongsToClassificationBatch | BelongsToAdaptationBatch | BelongsToTextbook

    strategy: ApiStrategy
    input: ApiInputOut
    raw_llm_conversations: JsonList
    images_urls: adaptation.adapted.ImagesUrls
    adjustment_prompts: list[str]
    manual_edit: adaptation.adapted.Exercise | None
    marked_as_removed: bool

    class InProgress(ApiModel):
        kind: Literal["inProgress"]

    class InvalidJsonError(ApiModel):
        kind: Literal["error"]
        error: Literal["invalid-json"]
        parsed: typing.Any

    class NotJsonError(ApiModel):
        kind: Literal["error"]
        error: Literal["not-json"]
        text: str

    class UnknownError(ApiModel):
        kind: Literal["error"]
        error: Literal["unknown"]

    class LlmSuccess(ApiModel):
        kind: Literal["success"]
        adapted_exercise: adaptation.adapted.Exercise

    llm_status: InProgress | InvalidJsonError | NotJsonError | UnknownError | LlmSuccess

    class Success(ApiModel):
        kind: Literal["success"]
        success: Literal["llm", "manual"]
        adapted_exercise: adaptation.adapted.Exercise

    status: InProgress | InvalidJsonError | NotJsonError | UnknownError | Success


@router.get("/adaptations/{id}")
async def get_adaptation(id: str, session: database_utils.SessionDependable) -> ApiAdaptation:
    return make_api_adaptation(get_by_id(session, adaptation.Adaptation, id))


class PostAdaptationAdjustmentRequest(ApiModel):
    adjustment: str


@router.post("/adaptations/{id}/adjustment")
async def post_adaptation_adjustment(
    id: str, req: PostAdaptationAdjustmentRequest, session: database_utils.SessionDependable
) -> None:
    exercise_adaptation = get_by_id(session, adaptation.Adaptation, id)
    assert exercise_adaptation.initial_assistant_response is not None
    exercise_adaptation.approved_by = None
    exercise_adaptation.approved_at = None

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
    except RetryableError:
        raise fastapi.HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=[dict(type="retryable", msg="LLM service temporarily unavailable")],
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
            kind="success", exercise=adaptation.adapted.Exercise.model_validate(response.message.content.model_dump())
        )

    raw_llm_conversations = list(exercise_adaptation.raw_llm_conversations)
    raw_llm_conversations.append(raw_conversation)
    exercise_adaptation.raw_llm_conversations = raw_llm_conversations

    adjustments = list(exercise_adaptation.adjustments)
    adjustments.append(
        adaptation.assistant_responses.Adjustment(user_prompt=req.adjustment, assistant_response=assistant_response)
    )
    exercise_adaptation.adjustments = adjustments


@router.delete("/adaptations/{id}/last-adjustment")
def delete_adaptation_last_adjustment(id: str, session: database_utils.SessionDependable) -> None:
    exercise_adaptation = get_by_id(session, adaptation.Adaptation, id)
    exercise_adaptation.approved_by = None
    exercise_adaptation.approved_at = None

    raw_llm_conversations = list(exercise_adaptation.raw_llm_conversations)
    raw_llm_conversations.pop()
    exercise_adaptation.raw_llm_conversations = raw_llm_conversations

    adjustments = list(exercise_adaptation.adjustments)
    adjustments.pop()
    exercise_adaptation.adjustments = adjustments


@router.put("/adaptations/{id}/manual-edit")
def put_adaptation_manual_edit(
    id: str, req: adaptation.adapted.Exercise, session: database_utils.SessionDependable
) -> None:
    exercise_adaptation = get_by_id(session, adaptation.Adaptation, id)
    exercise_adaptation.manual_edit = req
    exercise_adaptation.approved_by = None
    exercise_adaptation.approved_at = None


@router.delete("/adaptations/{id}/manual-edit")
def delete_adaptation_manual_edit(id: str, session: database_utils.SessionDependable) -> None:
    exercise_adaptation = get_by_id(session, adaptation.Adaptation, id)
    exercise_adaptation.manual_edit = None
    exercise_adaptation.approved_by = None
    exercise_adaptation.approved_at = None


class ApprovalRequest(ApiModel):
    approved: bool
    by: str


@router.put("/adaptations/{id}/approved")
def set_adaptation_approved(id: str, session: database_utils.SessionDependable, req: ApprovalRequest) -> None:
    exercise_adaptation = get_by_id(session, adaptation.Adaptation, id)
    if req.approved:
        exercise_adaptation.approved_by = req.by
        exercise_adaptation.approved_at = datetime.datetime.now()
    else:
        exercise_adaptation.approved_by = None
        exercise_adaptation.approved_at = None


@router.post("/adaptations/{id}/retry")
def retry_adaptation(id: str, session: database_utils.SessionDependable) -> None:
    previous_adaptation = get_by_id(session, adaptation.Adaptation, id)
    now = datetime.datetime.now()
    new_created = dispatch.adaptation_creation(
        previous_adaptation.created,
        by_chunk=lambda ac: classification.AdaptationCreationByChunk(
            at=now, classification_chunk=ac.classification_chunk
        ),
        by_sandbox_batch=lambda ac: sandbox_adaptation.AdaptationCreationBySandboxBatch(
            at=now, sandbox_adaptation_batch=ac.sandbox_adaptation_batch
        ),
        by_textbook=lambda ac: textbooks.AdaptationCreationByTextbook(at=now, textbook=ac.textbook),
    )
    new_adaptation = adaptation.Adaptation(
        created=new_created,
        exercise=previous_adaptation.exercise,
        model=previous_adaptation.model,
        settings=previous_adaptation.settings,
        raw_llm_conversations=[],
        initial_assistant_response=None,
        initial_timing=None,
        adjustments=[],
        manual_edit=None,
        approved_by=None,
        approved_at=None,
    )
    session.add(new_adaptation)
    session.flush()


def make_api_adaptation(exercise_adaptation: adaptation.Adaptation) -> ApiAdaptation:
    last_assistant_response = exercise_adaptation.initial_assistant_response
    if exercise_adaptation.adjustments:
        last_assistant_response = exercise_adaptation.adjustments[-1].assistant_response

    llm_status: (
        ApiAdaptation.InProgress
        | ApiAdaptation.InvalidJsonError
        | ApiAdaptation.NotJsonError
        | ApiAdaptation.UnknownError
        | ApiAdaptation.LlmSuccess
    )
    if last_assistant_response is None:
        llm_status = ApiAdaptation.InProgress(kind="inProgress")
    elif isinstance(last_assistant_response, adaptation.assistant_responses.Success):
        llm_status = ApiAdaptation.LlmSuccess(kind="success", adapted_exercise=last_assistant_response.exercise)
    elif isinstance(last_assistant_response, adaptation.assistant_responses.InvalidJsonError):
        llm_status = ApiAdaptation.InvalidJsonError(
            kind="error", error="invalid-json", parsed=last_assistant_response.parsed
        )
    elif isinstance(last_assistant_response, adaptation.assistant_responses.NotJsonError):
        llm_status = ApiAdaptation.NotJsonError(kind="error", error="not-json", text=last_assistant_response.text)
    elif isinstance(last_assistant_response, adaptation.assistant_responses.UnknownError):
        llm_status = ApiAdaptation.UnknownError(kind="error", error="unknown")
    else:
        assert False

    status: (
        ApiAdaptation.InProgress
        | ApiAdaptation.InvalidJsonError
        | ApiAdaptation.NotJsonError
        | ApiAdaptation.UnknownError
        | ApiAdaptation.Success
    )
    if exercise_adaptation.manual_edit is not None:
        status = ApiAdaptation.Success(
            kind="success", success="manual", adapted_exercise=exercise_adaptation.manual_edit
        )
    elif isinstance(llm_status, ApiAdaptation.LlmSuccess):
        status = ApiAdaptation.Success(kind="success", success="llm", adapted_exercise=llm_status.adapted_exercise)
    else:
        status = llm_status

    return ApiAdaptation(
        id=str(exercise_adaptation.id),
        belongs_to=make_api_adaptation_belongs_to(exercise_adaptation),
        strategy=make_api_strategy(exercise_adaptation.settings, exercise_adaptation.model),
        input=make_api_input_out(exercise_adaptation.exercise),
        raw_llm_conversations=exercise_adaptation.raw_llm_conversations,
        adjustment_prompts=[prompt.user_prompt for prompt in exercise_adaptation.adjustments],
        manual_edit=exercise_adaptation.manual_edit,
        marked_as_removed=isinstance(exercise_adaptation.exercise.location, textbooks.ExerciseLocationTextbook)
        and exercise_adaptation.exercise.location.marked_as_removed,
        images_urls=previewable_exercise.gather_images_urls("http", exercise_adaptation.exercise),
        llm_status=llm_status,
        status=status,
    )


def make_api_adaptation_belongs_to(
    adaptation_: adaptation.Adaptation,
) -> (
    ApiAdaptation.BelongsToExtractionBatch
    | ApiAdaptation.BelongsToClassificationBatch
    | ApiAdaptation.BelongsToAdaptationBatch
    | ApiAdaptation.BelongsToTextbook
):
    return dispatch.exercise_creation(
        adaptation_.exercise.created,
        by_user=lambda _: dispatch.adaptation_creation(
            adaptation_.created,
            by_chunk=lambda ac: dispatch.classification_chunk_creation(
                ac.classification_chunk.created,
                by_page_extraction=None,  # The exercise has been created by a user, so the classification chunk cannot have been created by a page extraction
                by_sandbox_batch=lambda ccc: ApiAdaptation.BelongsToClassificationBatch(
                    kind="classification-batch", id=str(ccc.sandbox_classification_batch.id)
                ),
            ),
            by_sandbox_batch=lambda ac: ApiAdaptation.BelongsToAdaptationBatch(
                kind="adaptation-batch", id=str(ac.sandbox_adaptation_batch.id)
            ),
            by_textbook=lambda ac: ApiAdaptation.BelongsToTextbook(
                kind="textbook",
                id=str(ac.textbook.id),
                title=ac.textbook.title,
                page=dispatch.exercise_location(
                    adaptation_.exercise.location, textbook=lambda el: el.page_number, maybe_page_and_number=None
                ),
            ),
        ),
        by_page_extraction=lambda ec: dispatch.page_extraction_creation(
            ec.page_extraction.created,
            by_sandbox_batch=lambda pec: ApiAdaptation.BelongsToExtractionBatch(
                kind="extraction-batch", id=str(pec.sandbox_extraction_batch.id)
            ),
            by_textbook=lambda pec: ApiAdaptation.BelongsToTextbook(
                kind="textbook",
                id=str(pec.textbook_extraction_batch.textbook.id),
                title=pec.textbook_extraction_batch.textbook.title,
                page=dispatch.exercise_location(
                    adaptation_.exercise.location, textbook=lambda el: el.page_number, maybe_page_and_number=None
                ),
            ),
        ),
    )


def make_api_strategy(settings: adaptation.AdaptationSettings, model: adaptation.llm.ConcreteModel) -> ApiStrategy:
    return ApiStrategy(model=model, settings=make_api_strategy_settings(settings))


def make_api_strategy_settings(settings: adaptation.AdaptationSettings) -> ApiStrategySettings:
    return ApiStrategySettings(
        identity=make_api_strategy_settings_identity(settings),
        system_prompt=settings.system_prompt,
        response_specification=settings.response_specification,
    )


def make_api_strategy_settings_identity(settings: adaptation.AdaptationSettings) -> ApiStrategySettings.Identity | None:
    if settings.exercise_class is None:
        return None
    else:
        assert settings.exercise_class.latest_strategy_settings is not None
        if settings.exercise_class.latest_strategy_settings.id == settings.id:
            return ApiStrategySettings.Identity(name=settings.exercise_class.name, version="current")
        elif settings.exercise_class.latest_strategy_settings.parent_id == settings.id:
            return ApiStrategySettings.Identity(name=settings.exercise_class.name, version="previous")
        else:
            return ApiStrategySettings.Identity(name=settings.exercise_class.name, version="older")


def make_api_input(exercise: adaptation.AdaptableExercise) -> ApiInput:
    assert isinstance(
        exercise.location, (textbooks.ExerciseLocationTextbook, exercises.ExerciseLocationMaybePageAndNumber)
    )
    return ApiInput(
        page_number=exercise.location.page_number,
        exercise_number=exercise.location.exercise_number,
        text=exercise.full_text,
    )


def make_api_input_out(exercise: adaptation.AdaptableExercise) -> ApiInputOut:
    assert isinstance(
        exercise.location, (textbooks.ExerciseLocationTextbook, exercises.ExerciseLocationMaybePageAndNumber)
    )
    return ApiInputOut(
        page_number=exercise.location.page_number,
        exercise_number=exercise.location.exercise_number,
        text=exercise.full_text.split("\n"),
    )
