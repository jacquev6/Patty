import base64
import urllib.parse
import typing

from .. import adaptation
from .. import dispatching as dispatch
from .. import extraction
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


def gather_images_urls(
    kind: typing.Literal["s3", "data"], exercise: adaptation.AdaptableExercise
) -> adaptation.adapted.ImagesUrls:
    def gather(creation: extraction.ExerciseCreationByPageExtraction) -> adaptation.adapted.ImagesUrls:
        page = creation.page_extraction
        images = page.extracted_images
        urls: adaptation.adapted.ImagesUrls = {}
        for image in images:
            target = urllib.parse.urlparse(f"{settings.EXTRACTED_IMAGES_URL}/{image.id}.png")
            if kind == "data":
                object = s3.get_object(Bucket=target.netloc, Key=target.path[1:])
                data = base64.b64encode(object["Body"].read()).decode("ascii")
                url = f"data:image/png;base64,{data}"
            elif kind == "s3":
                url = s3.generate_presigned_url(
                    "get_object", Params={"Bucket": target.netloc, "Key": target.path[1:]}, ExpiresIn=3600
                )
            else:
                assert False
            urls[image.page_local_id] = url
        return urls

    return dispatch.exercise_creation(exercise.created, by_user=lambda ec: {}, by_page_extraction=gather)


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

    status: (
        AdaptationInProgress
        | AdaptationInvalidJsonError
        | AdaptationNotJsonError
        | AdaptationUnknownError
        | AdaptationSuccess
    )
    if exercise_adaptation.manual_edit is not None:
        status = AdaptationSuccess(
            kind="success", success="manual", id=adaptation_id, adapted_exercise=exercise_adaptation.manual_edit
        )
    elif isinstance(llm_status, AdaptationLlmSuccess):
        status = AdaptationSuccess(
            kind="success", success="llm", id=adaptation_id, adapted_exercise=llm_status.adapted_exercise
        )
    else:
        status = llm_status

    return status
