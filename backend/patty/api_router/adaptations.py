from typing import Literal

import fastapi

from .. import adaptation
from .. import classification
from .. import database_utils
from .. import exercises
from .. import extraction
from .. import sandbox
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


class ApiAdaptation(ApiModel):
    id: str
    extraction_batch_id: str | None
    classification_batch_id: str | None
    adaptation_batch_id: str | None
    textbook_id: str | None
    textbook_title: str | None
    strategy: ApiStrategy
    input: ApiInput
    raw_llm_conversations: JsonList
    initial_assistant_response: adaptation.assistant_responses.Response | None
    adjustments: list[adaptation.assistant_responses.Adjustment]
    manual_edit: adaptation.adapted.Exercise | None
    removed_from_textbook: bool


@router.get("/adaptations/{id}")
async def get_adaptation(id: str, session: database_utils.SessionDependable) -> ApiAdaptation:
    return make_api_adaptation(get_by_id(session, adaptation.Adaptation, id))


class PostAdaptationAdjustmentRequest(ApiModel):
    adjustment: str


@router.post("/adaptations/{id}/adjustment")
async def post_adaptation_adjustment(
    id: str, req: PostAdaptationAdjustmentRequest, session: database_utils.SessionDependable
) -> ApiAdaptation:
    exercise_adaptation = get_by_id(session, adaptation.Adaptation, id)
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

    return make_api_adaptation(exercise_adaptation)


@router.delete("/adaptations/{id}/last-adjustment")
def delete_adaptation_last_adjustment(id: str, session: database_utils.SessionDependable) -> ApiAdaptation:
    exercise_adaptation = get_by_id(session, adaptation.Adaptation, id)

    raw_llm_conversations = list(exercise_adaptation.raw_llm_conversations)
    raw_llm_conversations.pop()
    exercise_adaptation.raw_llm_conversations = raw_llm_conversations

    adjustments = list(exercise_adaptation.adjustments)
    adjustments.pop()
    exercise_adaptation.adjustments = adjustments

    return make_api_adaptation(exercise_adaptation)


@router.put("/adaptations/{id}/manual-edit")
def put_adaptation_manual_edit(
    id: str, req: adaptation.adapted.Exercise, session: database_utils.SessionDependable
) -> ApiAdaptation:
    exercise_adaptation = get_by_id(session, adaptation.Adaptation, id)
    exercise_adaptation.manual_edit = req
    return make_api_adaptation(exercise_adaptation)


@router.delete("/adaptations/{id}/manual-edit")
def delete_adaptation_manual_edit(id: str, session: database_utils.SessionDependable) -> ApiAdaptation:
    exercise_adaptation = get_by_id(session, adaptation.Adaptation, id)
    exercise_adaptation.manual_edit = None
    return make_api_adaptation(exercise_adaptation)


def make_api_adaptation(exercise_adaptation: adaptation.Adaptation) -> ApiAdaptation:
    textbook = (
        exercise_adaptation.exercise.location.textbook
        if isinstance(exercise_adaptation.exercise.location, textbooks.ExerciseLocationTextbook)
        else None
    )

    return ApiAdaptation(
        id=str(exercise_adaptation.id),
        extraction_batch_id=(
            str(exercise_adaptation.exercise.created.page_extraction.created.sandbox_extraction_batch.id)
            if isinstance(exercise_adaptation.exercise.created, extraction.ExerciseCreationByPageExtraction)
            and isinstance(
                exercise_adaptation.exercise.created.page_extraction.created,
                sandbox.extraction.PageExtractionCreationBySandboxBatch,
            )
            else None
        ),
        classification_batch_id=(
            str(exercise_adaptation.created.classification_chunk.created.sandbox_classification_batch.id)
            if isinstance(exercise_adaptation.created, classification.AdaptationCreationByChunk)
            and isinstance(
                exercise_adaptation.created.classification_chunk.created,
                sandbox.classification.ClassificationChunkCreationBySandboxBatch,
            )
            else None
        ),
        adaptation_batch_id=(
            str(exercise_adaptation.created.sandbox_adaptation_batch.id)
            if isinstance(exercise_adaptation.created, sandbox.adaptation.AdaptationCreationBySandboxBatch)
            else None
        ),
        textbook_id=None if textbook is None else str(textbook.id),
        textbook_title=None if textbook is None else textbook.title,
        strategy=make_api_strategy(exercise_adaptation.settings, exercise_adaptation.model),
        input=make_api_input(exercise_adaptation.exercise),
        raw_llm_conversations=exercise_adaptation.raw_llm_conversations,
        initial_assistant_response=exercise_adaptation.initial_assistant_response,
        adjustments=exercise_adaptation.adjustments,
        manual_edit=exercise_adaptation.manual_edit,
        removed_from_textbook=isinstance(exercise_adaptation.exercise.location, textbooks.ExerciseLocationTextbook)
        and exercise_adaptation.exercise.location.removed_from_textbook,
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
