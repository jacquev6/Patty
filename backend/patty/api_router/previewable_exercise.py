import base64
import datetime
import urllib.parse
import typing

from .. import adaptation
from .. import dispatching as dispatch
from .. import exercises
from .. import settings
from ..api_utils import ApiModel
from .s3_client import s3


class NotRequested(ApiModel):
    kind: typing.Literal["notRequested"]


class AdaptationNotStarted(ApiModel):
    kind: typing.Literal["notStarted"]


class AdaptationInProgress(ApiModel):
    kind: typing.Literal["inProgress"]
    id: str


class AdaptationInvalidJsonError(ApiModel):
    kind: typing.Literal["error"]
    error: typing.Literal["invalid-json"]
    id: str
    parsed: typing.Any


class AdaptationNotJsonError(ApiModel):
    kind: typing.Literal["error"]
    error: typing.Literal["not-json"]
    id: str
    text: str


class AdaptationUnknownError(ApiModel):
    kind: typing.Literal["error"]
    id: str
    error: typing.Literal["unknown"]


class AdaptationLlmSuccess(ApiModel):
    kind: typing.Literal["success"]
    adapted_exercise: adaptation.adapted.Exercise


class AdaptationSuccess(ApiModel):
    kind: typing.Literal["success"]
    success: typing.Literal["llm", "manual"]
    id: str
    adapted_exercise: adaptation.adapted.Exercise

    class AdaptationApproval(ApiModel):
        by: str
        at: datetime.datetime

    approved: AdaptationApproval | None


AdaptationStatus = (
    NotRequested
    | AdaptationNotStarted
    | AdaptationInProgress
    | AdaptationInvalidJsonError
    | AdaptationNotJsonError
    | AdaptationUnknownError
    | AdaptationSuccess
)


class ClassificationInProgress(ApiModel):
    kind: typing.Literal["inProgress"]


class ClassifiedByModel(ApiModel):
    kind: typing.Literal["byModel"]
    exercise_class: str
    class_has_settings: bool


class ReclassifiedByUser(ApiModel):
    kind: typing.Literal["byUser"]
    exercise_class: str
    class_has_settings: bool
    by: str


ClassificationStatus = NotRequested | ClassificationInProgress | ClassifiedByModel | ReclassifiedByUser


class PreviewableExercise(ApiModel):
    id: str
    page_number: int | None
    exercise_number: str | None
    full_text: str
    images_urls: adaptation.adapted.ImagesUrls
    classification_status: ClassificationStatus
    adaptation_status: AdaptationStatus


def _gather_lines_of_exercise(
    exercise: adaptation.adapted.ExerciseAsUnion,
) -> typing.Iterable[
    adaptation.adapted.InstructionLine
    | adaptation.adapted.StatementLine
    | adaptation.adapted.ExampleLine
    | adaptation.adapted.HintLine
]:
    if isinstance(exercise, adaptation.adapted.ExerciseV1):
        yield from exercise.instruction.lines
        if exercise.hint is not None:
            yield from exercise.hint.lines
        if exercise.example is not None:
            yield from exercise.example.lines
        for page in exercise.statement.pages:
            yield from page.lines
        if exercise.reference is not None:
            yield exercise.reference
    elif isinstance(exercise, adaptation.adapted.ExerciseV2):
        for phase in exercise.phases:
            yield from phase.instruction.lines
            if phase.hint is not None:
                yield from phase.hint.lines
            if phase.example is not None:
                yield from phase.example.lines
            if isinstance(phase.statement, adaptation.adapted.Pages):
                for page in phase.statement.pages:
                    yield from page.lines
        if exercise.reference is not None:
            yield exercise.reference
    else:
        assert False


def _gather_required_image_identifiers_from_adapted_exercise(
    exercise: adaptation.adapted.Exercise,
) -> typing.Iterable[str]:
    for line in _gather_lines_of_exercise(exercise.root):
        for component in line.contents:
            if isinstance(component, adaptation.adapted.Image):
                yield component.identifier


def _gather_required_image_identifiers_from_adaptation(adaptation_: adaptation.Adaptation) -> typing.Iterable[str]:
    if isinstance(adaptation_.initial_assistant_response, adaptation.assistant_responses.Success):
        yield from _gather_required_image_identifiers_from_adapted_exercise(
            adaptation_.initial_assistant_response.exercise
        )
    for adjustment in adaptation_.adjustments:
        if isinstance(adjustment.assistant_response, adaptation.assistant_responses.Success):
            yield from _gather_required_image_identifiers_from_adapted_exercise(adjustment.assistant_response.exercise)
    if adaptation_.manual_edit is not None:
        yield from _gather_required_image_identifiers_from_adapted_exercise(adaptation_.manual_edit)


def make_image_url(kind: typing.Literal["s3", "data"], image: exercises.ExerciseImage) -> str:
    target = urllib.parse.urlparse(f"{settings.EXERCISE_IMAGES_URL}/{image.id}.png")
    if kind == "data":
        object = s3.get_object(Bucket=target.netloc, Key=target.path[1:])
        data = base64.b64encode(object["Body"].read()).decode("ascii")
        return f"data:image/png;base64,{data}"
    elif kind == "s3":
        return typing.cast(
            str,
            s3.generate_presigned_url(
                "get_object", Params={"Bucket": target.netloc, "Key": target.path[1:]}, ExpiresIn=3600
            ),
        )
    else:
        assert False


def gather_images_urls(
    kind: typing.Literal["s3", "data"], exercise: adaptation.AdaptableExercise
) -> adaptation.adapted.ImagesUrls:
    available_images = dispatch.exercise_creation(
        exercise.created,
        by_user=lambda ec: [],
        by_page_extraction=lambda ec: [creation.image for creation in ec.page_extraction.extracted_images],
    )

    required_image_identifiers = {
        identifier
        for adaptation_ in exercise.adaptations
        for identifier in _gather_required_image_identifiers_from_adaptation(adaptation_)
    }

    urls: adaptation.adapted.ImagesUrls = {}
    for image in available_images:
        if image.local_identifier in required_image_identifiers:
            urls[image.local_identifier] = make_image_url(kind, image)

    return urls


def make_api_adaptation_status(exercise_adaptation: adaptation.Adaptation) -> AdaptationStatus:
    adaptation_id = str(exercise_adaptation.id)

    last_assistant_response = exercise_adaptation.initial_assistant_response
    if exercise_adaptation.adjustments:
        last_assistant_response = exercise_adaptation.adjustments[-1].assistant_response

    llm_status: (
        AdaptationInProgress
        | AdaptationInvalidJsonError
        | AdaptationNotJsonError
        | AdaptationUnknownError
        | AdaptationLlmSuccess
    )
    if last_assistant_response is None:
        llm_status = AdaptationInProgress(kind="inProgress", id=adaptation_id)
    elif isinstance(last_assistant_response, adaptation.assistant_responses.Success):
        llm_status = AdaptationLlmSuccess(kind="success", adapted_exercise=last_assistant_response.exercise)
    elif isinstance(last_assistant_response, adaptation.assistant_responses.InvalidJsonError):
        llm_status = AdaptationInvalidJsonError(
            kind="error", error="invalid-json", id=adaptation_id, parsed=last_assistant_response.parsed
        )
    elif isinstance(last_assistant_response, adaptation.assistant_responses.NotJsonError):
        llm_status = AdaptationNotJsonError(
            kind="error", error="not-json", id=adaptation_id, text=last_assistant_response.text
        )
    elif isinstance(last_assistant_response, adaptation.assistant_responses.UnknownError):
        llm_status = AdaptationUnknownError(kind="error", error="unknown", id=adaptation_id)
    else:
        assert False

    if exercise_adaptation.approved_by is None:
        approved = None
    else:
        assert exercise_adaptation.approved_at is not None
        approved = AdaptationSuccess.AdaptationApproval(
            by=exercise_adaptation.approved_by, at=exercise_adaptation.approved_at
        )

    status: (
        AdaptationInProgress
        | AdaptationInvalidJsonError
        | AdaptationNotJsonError
        | AdaptationUnknownError
        | AdaptationSuccess
    )
    if exercise_adaptation.manual_edit is not None:
        status = AdaptationSuccess(
            kind="success",
            success="manual",
            id=adaptation_id,
            adapted_exercise=exercise_adaptation.manual_edit,
            approved=approved,
        )
    elif isinstance(llm_status, AdaptationLlmSuccess):
        status = AdaptationSuccess(
            kind="success",
            success="llm",
            id=adaptation_id,
            adapted_exercise=llm_status.adapted_exercise,
            approved=approved,
        )
    else:
        status = llm_status

    return status
