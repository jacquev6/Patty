from collections.abc import Iterable
from typing import Any, Literal
import base64
import hashlib
import json
import os
import urllib.parse

import fastapi

from .. import adaptation
from .. import authentication
from .. import database_utils
from .. import exercises
from .. import external_exercises
from .. import sandbox
from .. import settings
from .. import textbooks
from ..any_json import JsonDict
from ..api_utils import get_by_id
from .s3_client import s3


router = fastapi.APIRouter(dependencies=[fastapi.Depends(authentication.auth_param_dependable)])


export_batch_template_file_path = os.path.join(
    os.path.dirname(__file__), "..", "export", "templates", "batch", "index.html"
)


@router.get("/extraction-batch/{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_extraction_batch_html(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    return export_batch_html("extraction", id, get_extraction_batch_adaptations(session, id), download)


@router.get("/extraction-batch/{id}.json")
def export_extraction_batch_json(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.JSONResponse:
    return export_batch_json("extraction", id, get_extraction_batch_adaptations(session, id), download)


def get_extraction_batch_adaptations(
    session: database_utils.Session, id: str
) -> Iterable[adaptation.Adaptation | None]:
    batch = get_by_id(session, sandbox.extraction.SandboxExtractionBatch, id)
    return [
        exercise.adaptations[-1] if len(exercise.adaptations) > 0 else None
        for creation in batch.page_extraction_creations
        for exercise in creation.page_extraction.fetch_ordered_exercises()
    ]


@router.get("/classification-batch/{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_classification_batch_html(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    return export_batch_html("classification", id, get_classification_batch_adaptations(session, id), download)


@router.get("/classification-batch/{id}.json")
def export_classification_batch_json(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.JSONResponse:
    return export_batch_json("classification", id, get_classification_batch_adaptations(session, id), download)


def get_classification_batch_adaptations(
    session: database_utils.Session, id: str
) -> Iterable[adaptation.Adaptation | None]:
    return [
        classification.exercise.adaptations[-1] if len(classification.exercise.adaptations) > 0 else None
        for classification in get_by_id(
            session, sandbox.classification.SandboxClassificationBatch, id
        ).classification_chunk_creation.classification_chunk.classifications
    ]


@router.get("/adaptation-batch/{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_adaptation_batch_html(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    return export_batch_html("adaptation", id, get_adaptation_batch_adaptations(session, id), download)


@router.get("/adaptation-batch/{id}.json")
def export_adaptation_batch_json(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.JSONResponse:
    return export_batch_json("adaptation", id, get_adaptation_batch_adaptations(session, id), download)


def get_adaptation_batch_adaptations(
    session: database_utils.Session, id: str
) -> Iterable[adaptation.Adaptation | None]:
    return [
        (
            adaptation_creation.exercise_adaptation.exercise.adaptations[-1]
            if len(adaptation_creation.exercise_adaptation.exercise.adaptations) > 0
            else None
        )
        for adaptation_creation in get_by_id(
            session, sandbox.adaptation.SandboxAdaptationBatch, id
        ).adaptation_creations
    ]


def export_batch_html(
    kind: Literal["extraction", "adaptation", "classification"],
    id: str,
    adaptations: Iterable[adaptation.Adaptation | None],
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
    adaptations: Iterable[adaptation.Adaptation | None],
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
    os.path.dirname(__file__), "..", "export", "templates", "adaptation", "index.html"
)


@router.get("/adaptation/{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_adaptation(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    data = make_adapted_exercise_data(get_by_id(session, adaptation.Adaptation, id))
    assert data is not None
    content = render_template(export_adaptation_template_file_path, "ADAPTATION_EXPORT_DATA", data)

    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{data['exerciseId']}.html"'

    return fastapi.responses.HTMLResponse(content=content, headers=headers)


export_textbook_template_file_path = os.path.join(
    os.path.dirname(__file__), "..", "export", "templates", "textbook", "index.html"
)


@router.get("/textbook/{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_textbook(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    textbook = get_by_id(session, textbooks.Textbook, id)

    exercises: list[JsonDict] = []
    for exercise in textbook.fetch_ordered_exercises():
        assert isinstance(exercise.location, textbooks.ExerciseLocationTextbook)
        if not exercise.location.removed_from_textbook:
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


def make_adapted_exercise_data(exercise_adaptation: adaptation.Adaptation) -> JsonDict | None:
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
