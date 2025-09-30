from __future__ import annotations
from typing import Literal
import datetime
import urllib.parse

import fastapi
import sqlalchemy as sql

from . import previewable_exercise
from .. import adaptation
from .. import classification
from .. import database_utils
from .. import exercises
from .. import external_exercises
from .. import extraction
from .. import settings
from .. import textbooks
from ..api_utils import ApiModel, get_by_id
from .s3_client import s3


router = fastapi.APIRouter()


class PostTextbookRequest(ApiModel):
    creator: str
    title: str
    publisher: str | None
    year: int | None
    isbn: str | None
    pages_count: int | None


class PostTextbookResponse(ApiModel):
    id: str


@router.post("/textbooks")
def post_textbook(
    req: PostTextbookRequest, engine: database_utils.EngineDependable, session: database_utils.SessionDependable
) -> PostTextbookResponse:
    textbook = textbooks.Textbook(
        created_by=req.creator,
        created_at=datetime.datetime.now(datetime.timezone.utc),
        title=req.title,
        publisher=req.publisher,
        year=req.year,
        isbn=req.isbn,
        pages_count=req.pages_count,
    )
    session.add(textbook)
    session.flush()
    return PostTextbookResponse(id=str(textbook.id))


class GetTextbookResponse(ApiModel):
    id: str
    needs_refresh: bool
    created_by: str
    title: str
    publisher: str | None
    year: int | None
    isbn: str | None
    pages_count: int | None

    class AdaptableExercise(previewable_exercise.PreviewableExercise):
        kind: Literal["adaptable"]

    class ExternalExercise(ApiModel):
        kind: Literal["external"]
        id: str
        page_number: int
        exercise_number: str
        original_file_name: str
        removed_from_textbook: bool

    external_exercises: list[ExternalExercise]

    class Range(ApiModel):
        id: str
        pdf_file_names: list[str]
        pdf_first_page_number: int
        textbook_first_page_number: int
        pages_count: int
        model_for_extraction: extraction.llm.ConcreteModel
        model_for_adaptation: adaptation.llm.ConcreteModel

        class Page(ApiModel):
            id: str
            page_number: int
            in_progress: bool
            removed_from_textbook: bool

        pages: list[Page]
        removed_from_textbook: bool

    ranges: list[Range]


@router.get("/textbooks/{id}")
async def get_textbook(id: str, session: database_utils.SessionDependable) -> GetTextbookResponse:
    textbook = get_by_id(session, textbooks.Textbook, id)

    external_exercises_: list[GetTextbookResponse.ExternalExercise] = []
    for exercise in textbook.fetch_ordered_external_exercises():
        assert isinstance(exercise.location, textbooks.ExerciseLocationTextbook)
        external_exercises_.append(
            GetTextbookResponse.ExternalExercise(
                kind="external",
                id=str(exercise.id),
                page_number=exercise.location.page_number,
                exercise_number=exercise.location.exercise_number,
                original_file_name=exercise.original_file_name,
                removed_from_textbook=exercise.location.removed_from_textbook,
            )
        )

    needs_refresh = False
    ranges = []
    for extraction_batch in textbook.extraction_batches:
        pages = []
        for page_extraction_creation in extraction_batch.page_extraction_creations:
            in_progress = page_extraction_creation.page_extraction.assistant_response is None
            if in_progress:
                needs_refresh = True
            pages.append(
                GetTextbookResponse.Range.Page(
                    id=str(page_extraction_creation.id),
                    page_number=extraction_batch.first_textbook_page_number
                    + page_extraction_creation.page_extraction.pdf_page_number
                    - extraction_batch.pdf_file_range.first_page_number,
                    in_progress=in_progress,
                    removed_from_textbook=page_extraction_creation.removed_from_textbook,
                )
            )

        ranges.append(
            GetTextbookResponse.Range(
                id=str(extraction_batch.id),
                pdf_file_names=extraction_batch.pdf_file_range.pdf_file.known_file_names,
                pdf_first_page_number=extraction_batch.pdf_file_range.first_page_number,
                textbook_first_page_number=extraction_batch.first_textbook_page_number,
                pages_count=extraction_batch.pdf_file_range.pages_count,
                model_for_extraction=extraction_batch.model_for_extraction,
                model_for_adaptation=extraction_batch.model_for_adaptation,
                pages=pages,
                removed_from_textbook=extraction_batch.removed_from_textbook,
            )
        )

    return GetTextbookResponse(
        id=str(textbook.id),
        needs_refresh=needs_refresh,
        created_by=textbook.created_by,
        title=textbook.title,
        publisher=textbook.publisher,
        year=textbook.year,
        isbn=textbook.isbn,
        pages_count=textbook.pages_count,
        external_exercises=external_exercises_,
        ranges=ranges,
    )


class GetTextbookPageResponse(ApiModel):
    number: int
    needs_refresh: bool

    class Textbook(ApiModel):
        id: str
        title: str

    textbook: Textbook

    class AdaptableExercise(previewable_exercise.PreviewableExercise):
        kind: Literal["adaptable"]
        removed_from_textbook: bool

    class ExternalExercise(ApiModel):
        kind: Literal["external"]
        id: str
        page_number: int
        exercise_number: str
        original_file_name: str
        removed_from_textbook: bool

    exercises: list[AdaptableExercise | ExternalExercise]


@router.get("/textbooks/{id}/pages/{number}")
async def get_textbook_page(id: str, number: int, session: database_utils.SessionDependable) -> GetTextbookPageResponse:
    textbook = get_by_id(session, textbooks.Textbook, id)
    if number < 1 or (textbook.pages_count is not None and number > textbook.pages_count):
        raise fastapi.HTTPException(status_code=404, detail="Page not found")

    needs_refresh = False
    exercises_: list[GetTextbookPageResponse.AdaptableExercise | GetTextbookPageResponse.ExternalExercise] = []
    for exercise in textbook.fetch_ordered_exercises_on_page(number):
        assert isinstance(exercise.location, textbooks.ExerciseLocationTextbook)

        if isinstance(exercise, external_exercises.ExternalExercise):
            exercises_.append(
                GetTextbookPageResponse.ExternalExercise(
                    kind="external",
                    id=str(exercise.id),
                    page_number=exercise.location.page_number,
                    exercise_number=exercise.location.exercise_number,
                    original_file_name=exercise.original_file_name,
                    removed_from_textbook=exercise.location.removed_from_textbook,
                )
            )
        elif isinstance(exercise, adaptation.AdaptableExercise):
            assert isinstance(exercise.created, extraction.ExerciseCreationByPageExtraction)
            assert isinstance(exercise.created.page_extraction.created, textbooks.PageExtractionCreationByTextbook)
            if exercise.created.page_extraction.created.removed_from_textbook:
                continue
            if exercise.created.page_extraction.created.textbook_extraction_batch.removed_from_textbook:
                continue

            latest_classification = exercise.classifications[-1] if exercise.classifications else None

            exercise_class = (
                latest_classification.exercise_class.name
                if latest_classification is not None and latest_classification.exercise_class is not None
                else None
            )

            if exercise_class is None:
                needs_refresh = True

            exercise_class_has_settings = (
                latest_classification is not None
                and latest_classification.exercise_class is not None
                and latest_classification.exercise_class.latest_strategy_settings is not None
            )

            classification_status: previewable_exercise.ClassificationStatus
            if exercise_class is None:
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
            if len(exercise.adaptations) == 0:
                adaptation_status = previewable_exercise.AdaptationNotStarted(kind="notStarted")
            else:
                adaptation_status = previewable_exercise.make_api_adaptation_status(exercise.adaptations[-1])

            if adaptation_status.kind == "inProgress":
                needs_refresh = True

            exercises_.append(
                GetTextbookPageResponse.AdaptableExercise(
                    kind="adaptable",
                    id=str(exercise.id),
                    page_number=exercise.location.page_number,
                    exercise_number=exercise.location.exercise_number,
                    full_text=exercise.full_text,
                    images_urls=previewable_exercise.gather_images_urls("s3", exercise),
                    classification_status=classification_status,
                    adaptation_status=adaptation_status,
                    removed_from_textbook=exercise.location.removed_from_textbook,
                )
            )
        else:
            assert False

    return GetTextbookPageResponse(
        number=number,
        needs_refresh=needs_refresh,
        textbook=GetTextbookPageResponse.Textbook(id=str(textbook.id), title=textbook.title),
        exercises=exercises_,
    )


class GetTextbooksResponse(ApiModel):
    class Textbook(ApiModel):
        id: str
        created_by: str
        created_at: datetime.datetime
        title: str
        publisher: str | None
        year: int | None
        pages_count: int | None

    textbooks: list[Textbook]


@router.get("/textbooks")
async def get_textbooks(session: database_utils.SessionDependable) -> GetTextbooksResponse:
    textbooks_ = session.query(textbooks.Textbook).order_by(-textbooks.Textbook.id).all()
    return GetTextbooksResponse(
        textbooks=[
            GetTextbooksResponse.Textbook(
                id=str(textbook.id),
                created_by=textbook.created_by,
                created_at=textbook.created_at,
                title=textbook.title,
                publisher=textbook.publisher,
                year=textbook.year,
                pages_count=textbook.pages_count,
            )
            for textbook in textbooks_
        ]
    )


class PostTextbookExternalExercisesRequest(ApiModel):
    creator: str
    page_number: int
    exercise_number: str
    original_file_name: str


class PostTextbookExternalExercisesResponse(ApiModel):
    put_url: str


@router.post("/textbooks/{textbook_id}/external-exercises")
def post_textbook_external_exercises(
    textbook_id: str, req: PostTextbookExternalExercisesRequest, session: database_utils.SessionDependable
) -> PostTextbookExternalExercisesResponse:
    textbook = get_by_id(session, textbooks.Textbook, textbook_id)
    now = datetime.datetime.now(datetime.timezone.utc)
    external_exercise = external_exercises.ExternalExercise(
        created=exercises.ExerciseCreationByUser(at=now, username=req.creator),
        location=textbooks.ExerciseLocationTextbook(
            textbook=textbook,
            page_number=req.page_number,
            exercise_number=req.exercise_number,
            removed_from_textbook=False,
        ),
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


@router.put("/textbooks/{textbook_id}/exercises/{exercise_id}/removed")
def put_textbook_exercises_removed(
    textbook_id: str, exercise_id: str, removed: bool, session: database_utils.SessionDependable
) -> None:
    textbook = get_by_id(session, textbooks.Textbook, textbook_id)
    exercise = get_by_id(session, exercises.Exercise, exercise_id)
    assert isinstance(exercise.location, textbooks.ExerciseLocationTextbook)
    assert exercise.location.textbook == textbook
    exercise.location.removed_from_textbook = removed


class PostTextbookRangeRequest(ApiModel):
    creator: str
    pdf_file_sha256: str
    pdf_first_page_number: int
    textbook_first_page_number: int
    pages_count: int
    model_for_extraction: extraction.llm.ConcreteModel
    model_for_adaptation: adaptation.llm.ConcreteModel


@router.post("/textbooks/{id}/ranges")
async def post_textbook_range(
    id: str, req: PostTextbookRangeRequest, session: database_utils.SessionDependable
) -> None:
    textbook = get_by_id(session, textbooks.Textbook, id)
    pdf_file = session.get(extraction.PdfFile, req.pdf_file_sha256)
    if pdf_file is None:
        raise fastapi.HTTPException(status_code=404, detail="PDF file not found")
    now = datetime.datetime.now(datetime.timezone.utc)

    settings = (
        session.execute(sql.select(extraction.ExtractionSettings).order_by(extraction.ExtractionSettings.id.desc()))
        .scalars()
        .first()
    )
    assert settings is not None

    pdf_file_range = extraction.PdfFileRange(
        created_at=now,
        created_by=req.creator,
        pdf_file=pdf_file,
        first_page_number=req.pdf_first_page_number,
        pages_count=req.pages_count,
    )
    session.add(pdf_file_range)
    extraction_batch = textbooks.TextbookExtractionBatch(
        created_at=now,
        created_by=req.creator,
        pdf_file_range=pdf_file_range,
        textbook=textbook,
        first_textbook_page_number=req.textbook_first_page_number,
        model_for_extraction=req.model_for_extraction,
        model_for_adaptation=req.model_for_adaptation,
        removed_from_textbook=False,
    )
    session.add(extraction_batch)

    for page_number in range(
        pdf_file_range.first_page_number, pdf_file_range.first_page_number + pdf_file_range.pages_count
    ):
        session.add(
            extraction.PageExtraction(
                created=textbooks.PageExtractionCreationByTextbook(
                    at=now, textbook_extraction_batch=extraction_batch, removed_from_textbook=False
                ),
                pdf_file_range=pdf_file_range,
                pdf_page_number=page_number,
                settings=settings,
                model=req.model_for_extraction,
                run_classification=True,
                model_for_adaptation=req.model_for_adaptation,
                assistant_response=None,
            )
        )


@router.put("/textbooks/{textbook_id}/ranges/{range_id}/removed")
def put_textbook_ranges_removed(
    textbook_id: str, range_id: str, removed: bool, session: database_utils.SessionDependable
) -> None:
    textbook = get_by_id(session, textbooks.Textbook, textbook_id)
    batch = get_by_id(session, textbooks.TextbookExtractionBatch, range_id)
    assert batch.textbook == textbook
    batch.removed_from_textbook = removed


@router.put("/textbooks/{textbook_id}/pages/{page_id}/removed")
def put_textbook_pages_removed(
    textbook_id: str, page_id: str, removed: bool, session: database_utils.SessionDependable
) -> None:
    textbook = get_by_id(session, textbooks.Textbook, textbook_id)
    page = get_by_id(session, textbooks.PageExtractionCreationByTextbook, page_id)
    assert page.textbook_extraction_batch.textbook == textbook
    page.removed_from_textbook = removed
