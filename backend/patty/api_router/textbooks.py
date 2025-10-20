from __future__ import annotations
from typing import Literal
import datetime

import fastapi
import sqlalchemy as sql

from . import previewable_exercise
from .. import adaptation
from .. import classification
from .. import database_utils
from .. import exercises
from .. import external_exercises
from .. import extraction
from .. import file_storage
from .. import textbooks
from ..api_utils import ApiModel, get_by_id


router = fastapi.APIRouter()


class PostTextbookRequest(ApiModel):
    creator: str
    title: str
    publisher: str | None
    year: int | None
    isbn: str | None
    pages_count: int | None

    class SinglePdf(ApiModel):
        pdf_file_sha256: str
        pdf_to_textbook_page_numbers_delta: int  # Textbook page = PDF page + delta
        textbook_pages_ranges: list[tuple[int, int]]
        model_for_extraction: extraction.llm.ConcreteModel
        model_for_adaptation: adaptation.llm.ConcreteModel

    single_pdf: SinglePdf | None


class PostTextbookResponse(ApiModel):
    id: str


@router.post("/textbooks")
def post_textbook(
    req: PostTextbookRequest, engine: database_utils.EngineDependable, session: database_utils.SessionDependable
) -> PostTextbookResponse:
    now = datetime.datetime.now(datetime.timezone.utc)

    if req.single_pdf is None:
        single_pdf_file = None
    else:
        single_pdf_file = session.get(extraction.PdfFile, req.single_pdf.pdf_file_sha256)
        if single_pdf_file is None:
            raise fastapi.HTTPException(status_code=404, detail="PDF file not found")

    textbook = textbooks.Textbook(
        created_by=req.creator,
        created_at=now,
        title=req.title,
        publisher=req.publisher,
        year=req.year,
        isbn=req.isbn,
        pages_count=req.pages_count,
        single_pdf_file=single_pdf_file,
    )
    session.add(textbook)
    session.flush()

    if single_pdf_file is not None:
        assert req.single_pdf is not None

        settings = (
            session.execute(sql.select(extraction.ExtractionSettings).order_by(extraction.ExtractionSettings.id.desc()))
            .scalars()
            .first()
        )
        assert settings is not None

        if req.single_pdf.textbook_pages_ranges:
            for first_textbook_page, last_textbook_page in req.single_pdf.textbook_pages_ranges:
                pdf_file_range = extraction.PdfFileRange(
                    created_at=now,
                    created_by=req.creator,
                    pdf_file=single_pdf_file,
                    first_page_number=first_textbook_page - req.single_pdf.pdf_to_textbook_page_numbers_delta,
                    pages_count=last_textbook_page - first_textbook_page + 1,
                )
                session.add(pdf_file_range)
                extraction_batch = textbooks.TextbookExtractionBatch(
                    created_at=now,
                    created_by=req.creator,
                    pdf_file_range=pdf_file_range,
                    textbook=textbook,
                    first_textbook_page_number=first_textbook_page,
                    model_for_extraction=req.single_pdf.model_for_extraction,
                    model_for_adaptation=req.single_pdf.model_for_adaptation,
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
                            model=req.single_pdf.model_for_extraction,
                            run_classification=True,
                            model_for_adaptation=req.single_pdf.model_for_adaptation,
                            assistant_response=None,
                            timing=None,
                        )
                    )
        else:
            # Nothing to extract yet, but we need to keep the pdf_to_textbook_page_numbers_delta
            # so we create a zero-length extraction batch
            pdf_file_range = extraction.PdfFileRange(
                created_at=now, created_by=req.creator, pdf_file=single_pdf_file, first_page_number=1, pages_count=0
            )
            session.add(pdf_file_range)
            extraction_batch = textbooks.TextbookExtractionBatch(
                created_at=now,
                created_by=req.creator,
                pdf_file_range=pdf_file_range,
                textbook=textbook,
                first_textbook_page_number=1 + req.single_pdf.pdf_to_textbook_page_numbers_delta,
                model_for_extraction=req.single_pdf.model_for_extraction,
                model_for_adaptation=req.single_pdf.model_for_adaptation,
                removed_from_textbook=False,
            )
            session.add(extraction_batch)

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
    pages_with_exercises: list[int]

    class SinglePdf(ApiModel):
        sha256: str
        known_names: list[str]
        pages_count: int
        pdf_to_textbook_page_numbers_delta: int

    single_pdf: SinglePdf | None

    class KnownPdf(ApiModel):
        pdf_to_textbook_page_numbers_delta: int
        extracted_textbook_pages: list[int]

    known_pdfs: dict[str, KnownPdf]  # Keyed by sha256

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

    pages_with_exercises: set[int] = set()

    external_exercises_: list[GetTextbookResponse.ExternalExercise] = []
    for exercise in textbook.fetch_ordered_external_exercises():
        assert isinstance(exercise.location, textbooks.ExerciseLocationTextbook)
        pages_with_exercises.add(exercise.location.page_number)
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
    delta_py_pdf = {}
    extracted_textbook_pages_by_pdf: dict[str, set[int]] = {}
    for extraction_batch in textbook.extraction_batches:
        if extraction_batch.pdf_file_range.pages_count == 0:
            continue  # Hide zero-length extraction batches created to store the pdf_to_textbook_page_numbers_delta

        delta_py_pdf[extraction_batch.pdf_file_range.pdf_file.sha256] = (
            extraction_batch.first_textbook_page_number - extraction_batch.pdf_file_range.first_page_number
        )

        pages = []
        for page_extraction_creation in extraction_batch.page_extraction_creations:
            in_progress = page_extraction_creation.page_extraction.assistant_response is None
            if in_progress:
                needs_refresh = True
            page_number = (
                extraction_batch.first_textbook_page_number
                + page_extraction_creation.page_extraction.pdf_page_number
                - extraction_batch.pdf_file_range.first_page_number
            )
            pages.append(
                GetTextbookResponse.Range.Page(
                    id=str(page_extraction_creation.id),
                    page_number=page_number,
                    in_progress=in_progress,
                    removed_from_textbook=page_extraction_creation.removed_from_textbook,
                )
            )
            if not page_extraction_creation.removed_from_textbook:
                extracted_textbook_pages_by_pdf.setdefault(extraction_batch.pdf_file_range.pdf_file.sha256, set()).add(
                    page_number
                )
            if (
                not extraction_batch.removed_from_textbook
                and not page_extraction_creation.removed_from_textbook
                and isinstance(
                    page_extraction_creation.page_extraction.assistant_response,
                    (extraction.assistant_responses.SuccessWithoutImages | extraction.assistant_responses.Success),
                )
            ):
                for exercise_creation in page_extraction_creation.page_extraction.exercise_creations__unordered:
                    assert isinstance(exercise_creation.exercise.location, textbooks.ExerciseLocationTextbook)
                    if not exercise_creation.exercise.location.removed_from_textbook:
                        pages_with_exercises.add(page_number)
                        break

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

    if textbook.single_pdf_file is None:
        single_pdf = None
    else:
        assert len(textbook.extraction_batches) > 0
        batch = textbook.extraction_batches[0]
        single_pdf = GetTextbookResponse.SinglePdf(
            sha256=textbook.single_pdf_file.sha256,
            known_names=textbook.single_pdf_file.known_file_names,
            pdf_to_textbook_page_numbers_delta=batch.first_textbook_page_number
            - batch.pdf_file_range.first_page_number,
            pages_count=textbook.single_pdf_file.pages_count,
        )

    known_pdfs = {
        sha256: GetTextbookResponse.KnownPdf(
            pdf_to_textbook_page_numbers_delta=delta_py_pdf[sha256],
            extracted_textbook_pages=sorted(extracted_textbook_pages),
        )
        for sha256, extracted_textbook_pages in extracted_textbook_pages_by_pdf.items()
    }

    return GetTextbookResponse(
        id=str(textbook.id),
        needs_refresh=needs_refresh,
        created_by=textbook.created_by,
        title=textbook.title,
        publisher=textbook.publisher,
        year=textbook.year,
        isbn=textbook.isbn,
        pages_count=textbook.pages_count,
        pages_with_exercises=sorted(pages_with_exercises),
        external_exercises=external_exercises_,
        ranges=ranges,
        single_pdf=single_pdf,
        known_pdfs=known_pdfs,
    )


class GetTextbookPageResponse(ApiModel):
    id: str | None  # Filled when all exercises come from the same PageExtractionCreationByTextbook
    number: int
    needs_refresh: bool

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

    for extraction_batch in textbook.extraction_batches:
        if extraction_batch.removed_from_textbook:
            continue
        if number < extraction_batch.first_textbook_page_number:
            continue
        if number >= extraction_batch.first_textbook_page_number + extraction_batch.pdf_file_range.pages_count:
            continue
        page_extraction_creation = next(
            (
                pec
                for pec in extraction_batch.page_extraction_creations
                if pec.page_extraction.pdf_page_number
                == extraction_batch.pdf_file_range.first_page_number
                + (number - extraction_batch.first_textbook_page_number)
            ),
            None,
        )
        if page_extraction_creation is None:
            continue
        if page_extraction_creation.removed_from_textbook:
            continue
        if page_extraction_creation.page_extraction.assistant_response is None:
            needs_refresh = True

    page_extraction_ids = set()
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

            page_extraction_ids.add(str(exercise.created.page_extraction.created.id))
            exercises_.append(
                GetTextbookPageResponse.AdaptableExercise(
                    kind="adaptable",
                    id=str(exercise.id),
                    page_number=exercise.location.page_number,
                    exercise_number=exercise.location.exercise_number,
                    full_text=exercise.full_text,
                    images_urls=previewable_exercise.gather_images_urls("http", exercise),
                    classification_status=classification_status,
                    adaptation_status=adaptation_status,
                    removed_from_textbook=exercise.location.removed_from_textbook,
                )
            )
        else:
            assert False

    page_id = page_extraction_ids.pop() if len(page_extraction_ids) == 1 else None

    return GetTextbookPageResponse(id=page_id, number=number, needs_refresh=needs_refresh, exercises=exercises_)


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
    return PostTextbookExternalExercisesResponse(
        put_url=file_storage.external_exercises.get_put_url(str(external_exercise.id))
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
    if isinstance(exercise, adaptation.AdaptableExercise):
        classification = exercise.classifications[-1] if exercise.classifications else None
        if classification is not None and classification.exercise_class is not None:
            adaptation_ = exercise.fetch_latest_adaptation(classification.exercise_class)
            if adaptation_ is not None:
                adaptation_.approved_by = None
                adaptation_.approved_at = None


class PostTextbookRangesRequest(ApiModel):
    creator: str
    pdf_file_sha256: str
    pdf_to_textbook_page_numbers_delta: int
    textbook_pages_ranges: list[tuple[int, int]]
    model_for_extraction: extraction.llm.ConcreteModel
    model_for_adaptation: adaptation.llm.ConcreteModel


@router.post("/textbooks/{id}/ranges")
async def post_textbook_ranges(
    id: str, req: PostTextbookRangesRequest, session: database_utils.SessionDependable
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

    for first_textbook_page, last_textbook_page in req.textbook_pages_ranges:
        pdf_file_range = extraction.PdfFileRange(
            created_at=now,
            created_by=req.creator,
            pdf_file=pdf_file,
            first_page_number=first_textbook_page - req.pdf_to_textbook_page_numbers_delta,
            pages_count=last_textbook_page - first_textbook_page + 1,
        )
        session.add(pdf_file_range)
        extraction_batch = textbooks.TextbookExtractionBatch(
            created_at=now,
            created_by=req.creator,
            pdf_file_range=pdf_file_range,
            textbook=textbook,
            first_textbook_page_number=first_textbook_page,
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
                    timing=None,
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
