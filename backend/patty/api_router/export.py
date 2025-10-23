from collections.abc import Iterable
from typing import Any, Literal
import base64
import csv
import hashlib
import io
import json
import os

import fastapi
import sqlalchemy as sql

from . import previewable_exercise
from .. import adaptation
from .. import alpha_numerical_sorting as alnum
from .. import authentication
from .. import classification
from .. import database_utils
from .. import exercises
from .. import external_exercises
from .. import sandbox
from .. import file_storage
from .. import textbooks
from ..any_json import JsonDict
from ..api_utils import get_by_id


router = fastapi.APIRouter(dependencies=[fastapi.Depends(authentication.auth_param_dependable)])


export_batch_template_file_path = os.path.join(
    os.path.dirname(__file__), "..", "export", "templates", "batch", "index.html"
)


@router.get("/sandbox-extraction-batch-{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_extraction_batch_html(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    return export_batch_html("extraction", id, get_extraction_batch_adaptations(session, id), download)


class TsvResponse(fastapi.responses.Response):
    media_type = "text/tab-separated-values"


@router.get("/sandbox-extraction-batch-{id}-extracted-exercises.json")
def export_extraction_batch_extracted_exercises_json(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.JSONResponse:
    batch = get_by_id(session, sandbox.extraction.SandboxExtractionBatch, id)

    content = []
    for page_creation in batch.page_extraction_creations:
        page = page_creation.page_extraction
        assert page.assistant_response is not None
        content.append(
            {
                "pdfPageNumber": page.pdf_page_number,
                "response": page.assistant_response.model_dump(),
                "imagesUrls": {
                    creation.image.local_identifier: previewable_exercise.make_image_url("data", creation.image)
                    for creation in page.extracted_images
                },
            }
        )

    return fastapi.responses.JSONResponse(
        content=content, headers=make_export_header(download, f"sandbox-extraction-batch-{id}-extracted-exercises.json")
    )


@router.get("/sandbox-extraction-batch-{id}-extracted-exercises.tsv")
def export_extraction_batch_extracted_exercises_tsv(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> TsvResponse:
    batch = get_by_id(session, sandbox.extraction.SandboxExtractionBatch, id)

    headers = ("page", "num", "instruction_hint_example", "statement")
    data = []
    for page in batch.page_extraction_creations:
        for ec in page.page_extraction.exercise_creations__ordered_by_id:
            exercise = ec.exercise
            assert isinstance(exercise, adaptation.AdaptableExercise)
            assert isinstance(exercise.location, exercises.ExerciseLocationMaybePageAndNumber)
            data.append(
                (
                    exercise.location.page_number,
                    exercise.location.exercise_number,
                    exercise.instruction_hint_example_text,
                    exercise.statement_text,
                )
            )

    return make_tsv_response(headers, data, download, f"sandbox-extraction-batch-{id}-extracted-exercises.tsv")


def make_tsv_response(
    headers: tuple[str, ...], data: list[tuple[Any, ...]], download: bool, filename: str
) -> TsvResponse:
    string_file = io.StringIO()
    writer = csv.writer(string_file, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(headers)
    writer.writerows(data)
    content = string_file.getvalue()

    return TsvResponse(content=content, headers=make_export_header(download, filename))


@router.get("/sandbox-extraction-batch-{id}-classified-exercises.tsv")
def export_extraction_batch_classified_exercises_tsv(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> TsvResponse:
    batch = get_by_id(session, sandbox.extraction.SandboxExtractionBatch, id)

    classifications: list[classification.ClassificationByChunk] = []
    if batch.run_classification:
        for page_creation in batch.page_extraction_creations:
            for chunk_creation in page_creation.page_extraction.classification_chunk_creations:
                classifications.extend(chunk_creation.classification_chunk.classifications)

    return export_batch_classified_exercises_tsv("extraction", id, classifications, download)


@router.get("/sandbox-extraction-batch-{id}-adapted-exercises.json")
def export_extraction_batch_adapted_exercises_json(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.JSONResponse:
    return export_batch_adapted_exercises_json(
        "extraction", id, get_extraction_batch_adaptations(session, id), download
    )


def get_extraction_batch_adaptations(
    session: database_utils.Session, id: str
) -> Iterable[adaptation.Adaptation | None]:
    batch = get_by_id(session, sandbox.extraction.SandboxExtractionBatch, id)
    return [
        ec.exercise.adaptations[-1] if len(ec.exercise.adaptations) > 0 else None
        for pec in batch.page_extraction_creations
        for ec in pec.page_extraction.exercise_creations__ordered_by_id
        if isinstance(ec.exercise, adaptation.AdaptableExercise)
    ]


@router.get("/sandbox-classification-batch-{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_classification_batch_html(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    return export_batch_html("classification", id, get_classification_batch_adaptations(session, id), download)


@router.get("/sandbox-classification-batch-{id}-classified-exercises.tsv")
def export_classification_batch_classified_exercises_tsv(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> TsvResponse:
    batch = get_by_id(session, sandbox.classification.SandboxClassificationBatch, id)

    return export_batch_classified_exercises_tsv(
        "classification", id, batch.classification_chunk_creation.classification_chunk.classifications, download
    )


@router.get("/sandbox-classification-batch-{id}-adapted-exercises.json")
def export_classification_batch_adapted_exercises_json(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.JSONResponse:
    return export_batch_adapted_exercises_json(
        "classification", id, get_classification_batch_adaptations(session, id), download
    )


def get_classification_batch_adaptations(
    session: database_utils.Session, id: str
) -> Iterable[adaptation.Adaptation | None]:
    return [
        classification.exercise.adaptations[-1] if len(classification.exercise.adaptations) > 0 else None
        for classification in get_by_id(
            session, sandbox.classification.SandboxClassificationBatch, id
        ).classification_chunk_creation.classification_chunk.classifications
    ]


@router.get("/sandbox-adaptation-batch-{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_adaptation_batch_html(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    return export_batch_html("adaptation", id, get_adaptation_batch_adaptations(session, id), download)


@router.get("/sandbox-adaptation-batch-{id}-adapted-exercises.json")
def export_adaptation_batch_adapted_exercises_json(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.JSONResponse:
    return export_batch_adapted_exercises_json(
        "adaptation", id, get_adaptation_batch_adaptations(session, id), download
    )


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

    return fastapi.responses.HTMLResponse(
        content=content, headers=make_export_header(download, f"sandbox-{kind}-batch-{id}.html")
    )


def export_batch_adapted_exercises_json(
    kind: Literal["extraction", "classification", "adaptation"],
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

    return fastapi.responses.JSONResponse(
        content=content, headers=make_export_header(download, f"sandbox-{kind}-batch-{id}-adapted-exercises.json")
    )


def export_batch_classified_exercises_tsv(
    kind: Literal["extraction", "classification"],
    id: str,
    classifications: Iterable[classification.ClassificationByChunk],
    download: bool,
) -> TsvResponse:
    headers = ("page", "num", "instruction_hint_example", "statement", "class_name")

    data: list[tuple[int | None, str | None, str | None, str | None, str]] = []
    for classification_ in classifications:
        exercise = classification_.exercise
        assert isinstance(exercise.location, exercises.ExerciseLocationMaybePageAndNumber)
        if classification_.exercise_class is not None:
            data.append(
                (
                    exercise.location.page_number,
                    exercise.location.exercise_number,
                    exercise.instruction_hint_example_text,
                    exercise.statement_text,
                    classification_.exercise_class.name,
                )
            )

    return make_tsv_response(headers, data, download, f"sandbox-{kind}-batch-{id}-classified-exercises.tsv")


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

    return fastapi.responses.HTMLResponse(
        content=content, headers=make_export_header(download, f"{data['exerciseId']}.html")
    )


export_textbook_template_file_path = os.path.join(
    os.path.dirname(__file__), "..", "export", "templates", "textbook", "index.html"
)


@router.get("/textbook/{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_textbook(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    textbook = get_by_id(session, textbooks.Textbook, id)

    exercises: list[JsonDict] = []
    for location in session.execute(
        sql.select(textbooks.ExerciseLocationTextbook)
        .where(textbooks.ExerciseLocationTextbook.textbook == textbook)
        .order_by(textbooks.ExerciseLocationTextbook.id)
    ).scalars():
        if not location.removed_from_textbook:
            exercise = location.exercise
            if isinstance(exercise, adaptation.AdaptableExercise):
                if len(exercise.adaptations) != 0:
                    adapted_exercise_data = make_adapted_exercise_data(exercise.adaptations[-1])
                    if adapted_exercise_data is not None:
                        exercises.append(adapted_exercise_data)
            elif isinstance(exercise, external_exercises.ExternalExercise):
                exercises.append(make_external_exercise_data(exercise))
            else:
                assert False

    data = dict(
        title=textbook.title,
        exercises=sorted(exercises, key=lambda ex: (ex["pageNumber"], alnum.key(ex["exerciseNumber"]))),
    )

    content = render_template(export_textbook_template_file_path, "TEXTBOOK_EXPORT_DATA", data)

    return fastapi.responses.HTMLResponse(
        content=content, headers=make_export_header(download, f"{textbook.title}.html")
    )


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
        "imagesUrls": previewable_exercise.gather_images_urls("data", exercise_adaptation.exercise),
    }


def make_external_exercise_data(external_exercise: external_exercises.ExternalExercise) -> JsonDict:
    location = external_exercise.location
    assert isinstance(location, textbooks.ExerciseLocationTextbook)
    data = base64.b64encode(file_storage.external_exercises.load(str(external_exercise.id))).decode("ascii")
    return {
        "exerciseId": f"P{location.page_number}Ex{location.exercise_number}",
        "pageNumber": location.page_number,
        "exerciseNumber": location.exercise_number,
        "kind": "external",
        "originalFileName": external_exercise.original_file_name,
        "data": data,
    }


def make_export_header(download: bool, filename: str) -> dict[str, str]:
    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return headers
