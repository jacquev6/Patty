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
from ..api_utils import ApiModel, get_by_id, assert_isinstance
from .s3_client import s3


router = fastapi.APIRouter()


class PostTextbookRequest(ApiModel):
    creator: str
    title: str
    publisher: str | None
    year: int | None
    isbn: str | None


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
    )
    session.add(textbook)
    session.flush()
    return PostTextbookResponse(id=str(textbook.id))


class ApiTextbookAdaptableExercise(previewable_exercise.PreviewableExercise):
    kind: Literal["adaptable"]


class ApiTextbookExternalExercise(ApiModel):
    kind: Literal["external"]
    id: str
    page_number: int
    exercise_number: str
    original_file_name: str
    removed_from_textbook: bool


class ApiTextbook(ApiModel):
    id: str
    created_by: str
    title: str
    publisher: str | None
    year: int | None
    isbn: str | None

    external_exercises: list[ApiTextbookExternalExercise]

    class Range(ApiModel):
        id: str
        pdf_file_names: list[str]
        pdf_file_sha256: str
        pdf_first_page_number: int
        textbook_first_page_number: int
        pages_count: int
        model_for_extraction: extraction.llm.ConcreteModel
        model_for_adaptation: adaptation.llm.ConcreteModel

        class Page(ApiModel):
            id: str
            page_number: int
            in_progress: bool

            class Exercise(previewable_exercise.PreviewableExercise):
                removed_from_textbook: bool

            exercises: list[Exercise]
            removed_from_textbook: bool

        pages: list[Page]
        removed_from_textbook: bool

    ranges: list[Range]

    class Page(ApiModel):
        number: int
        exercises: list[ApiTextbookAdaptableExercise | ApiTextbookExternalExercise]

    pages: list[Page]


class GetTextbookResponse(ApiModel):
    needs_refresh: bool
    textbook: ApiTextbook
    available_strategy_settings: list[str]


@router.get("/textbooks/{id}")
async def get_textbook(id: str, session: database_utils.SessionDependable) -> GetTextbookResponse:
    textbook = get_by_id(session, textbooks.Textbook, id)

    (api_textbook, needs_refresh) = make_api_textbook(textbook)

    return GetTextbookResponse(
        needs_refresh=needs_refresh,
        textbook=api_textbook,
        available_strategy_settings=[
            exercise_class.name
            for exercise_class in session.query(adaptation.ExerciseClass).order_by(adaptation.ExerciseClass.name).all()
        ],
    )


class GetTextbooksResponse(ApiModel):
    class Textbook(ApiModel):
        id: str
        created_by: str
        created_at: datetime.datetime
        title: str
        publisher: str | None
        year: int | None

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


def make_api_textbook(textbook: textbooks.Textbook) -> tuple[ApiTextbook, bool]:
    needs_refresh = False
    external_exercises_: list[ApiTextbookExternalExercise] = []
    textbook_pages: list[ApiTextbook.Page] = []
    for exercise in textbook.fetch_ordered_exercises():
        assert isinstance(exercise.location, textbooks.ExerciseLocationTextbook)
        if len(textbook_pages) == 0 or textbook_pages[-1].number != exercise.location.page_number:
            textbook_pages.append(ApiTextbook.Page(number=exercise.location.page_number, exercises=[]))
        page = textbook_pages[-1]

        if isinstance(exercise, external_exercises.ExternalExercise):
            external_exercise = ApiTextbookExternalExercise(
                kind="external",
                id=str(exercise.id),
                page_number=exercise.location.page_number,
                exercise_number=exercise.location.exercise_number,
                original_file_name=exercise.original_file_name,
                removed_from_textbook=exercise.location.removed_from_textbook,
            )
            external_exercises_.append(external_exercise)
            if not exercise.location.removed_from_textbook:
                page.exercises.append(external_exercise)
        elif isinstance(exercise, adaptation.AdaptableExercise):
            assert isinstance(exercise.created, extraction.ExerciseCreationByPageExtraction)
            assert isinstance(exercise.created.page_extraction.created, textbooks.PageExtractionCreationByTextbook)
            removed = (
                exercise.location.removed_from_textbook
                or exercise.created.page_extraction.created.removed_from_textbook
                or exercise.created.page_extraction.created.textbook_extraction_batch.removed_from_textbook
            )
            if len(exercise.adaptations) > 0 and not removed:
                page.exercises.append(
                    ApiTextbookAdaptableExercise(
                        kind="adaptable",
                        id=str(exercise.id),
                        page_number=exercise.location.page_number,
                        exercise_number=exercise.location.exercise_number,
                        full_text=exercise.full_text,
                        images_urls=previewable_exercise.gather_images_urls("s3", exercise),
                        classification_status=previewable_exercise.NotRequested(kind="notRequested"),
                        adaptation_status=previewable_exercise.make_api_adaptation_status(exercise.adaptations[-1]),
                    )
                )
        else:
            assert False
    textbook_pages = list(filter(lambda page: len(page.exercises) > 0, textbook_pages))

    ranges: list[ApiTextbook.Range] = []
    for extraction_batch in textbook.extraction_batches:
        range_pages: list[ApiTextbook.Range.Page] = []
        for page_extraction_creation in extraction_batch.page_extraction_creations:
            page_exercises: list[ApiTextbook.Range.Page.Exercise] = []
            for page_exercise in page_extraction_creation.page_extraction.fetch_ordered_exercises():
                latest_classification = page_exercise.classifications[-1] if page_exercise.classifications else None

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
                if len(page_exercise.adaptations) == 0:
                    adaptation_status = previewable_exercise.AdaptationNotStarted(kind="notStarted")
                else:
                    adaptation_status = previewable_exercise.make_api_adaptation_status(page_exercise.adaptations[-1])

                if adaptation_status.kind == "inProgress":
                    needs_refresh = True

                page_exercises.append(
                    ApiTextbook.Range.Page.Exercise(
                        id=str(page_exercise.id),
                        page_number=assert_isinstance(
                            page_exercise.location, textbooks.ExerciseLocationTextbook
                        ).page_number,
                        exercise_number=assert_isinstance(
                            page_exercise.location, textbooks.ExerciseLocationTextbook
                        ).exercise_number,
                        full_text=page_exercise.full_text,
                        removed_from_textbook=assert_isinstance(
                            page_exercise.location, textbooks.ExerciseLocationTextbook
                        ).removed_from_textbook,
                        images_urls=previewable_exercise.gather_images_urls("s3", page_exercise),
                        classification_status=classification_status,
                        adaptation_status=adaptation_status,
                    )
                )

            in_progress = page_extraction_creation.page_extraction.assistant_response is None
            if in_progress:
                needs_refresh = True
            range_pages.append(
                ApiTextbook.Range.Page(
                    id=str(page_extraction_creation.id),
                    page_number=extraction_batch.first_textbook_page_number
                    + page_extraction_creation.page_extraction.pdf_page_number
                    - extraction_batch.pdf_file_range.first_page_number,
                    in_progress=in_progress,
                    exercises=page_exercises,
                    removed_from_textbook=page_extraction_creation.removed_from_textbook,
                )
            )

        ranges.append(
            ApiTextbook.Range(
                id=str(extraction_batch.id),
                pdf_file_names=extraction_batch.pdf_file_range.pdf_file.known_file_names,
                pdf_file_sha256=extraction_batch.pdf_file_range.pdf_file.sha256,
                pdf_first_page_number=extraction_batch.pdf_file_range.first_page_number,
                textbook_first_page_number=extraction_batch.first_textbook_page_number,
                pages_count=extraction_batch.pdf_file_range.pages_count,
                model_for_extraction=extraction_batch.model_for_extraction,
                model_for_adaptation=extraction_batch.model_for_adaptation,
                pages=range_pages,
                removed_from_textbook=extraction_batch.removed_from_textbook,
            )
        )

    return (
        ApiTextbook(
            id=str(textbook.id),
            created_by=textbook.created_by,
            title=textbook.title,
            publisher=textbook.publisher,
            year=textbook.year,
            isbn=textbook.isbn,
            external_exercises=external_exercises_,
            ranges=ranges,
            pages=textbook_pages,
        ),
        needs_refresh,
    )
