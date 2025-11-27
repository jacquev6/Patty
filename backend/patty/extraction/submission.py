import datetime
import io
import subprocess
import traceback
import typing

import cachetools
import PIL.Image
import sqlalchemy as sql

from . import assistant_responses
from . import orm_models as db
from .. import adaptation
from .. import classification
from .. import database_utils
from .. import exercises
from .. import file_storage
from .. import logs
from .. import settings
from .images_detection import detect_images
from .llm import InvalidJsonLlmException, NotJsonLlmException
from .text_and_styles_extraction import extract_text_and_styles_from_pdf_page


pdf_data_cache = cachetools.TTLCache[str, bytes](maxsize=5, ttl=60 * 60)


def submit_extractions(session: database_utils.Session, parallelism: int) -> list[typing.Coroutine[None, None, None]]:
    extractions = (
        session.execute(
            sql.select(db.PageExtraction).where(db.PageExtraction._assistant_response == sql.null()).limit(parallelism)
        )
        .scalars()
        .all()
    )
    if len(extractions) > 0:
        logs.log(
            f"Found {len(extractions)} pending page extractions: {' '.join(str(extraction.id) for extraction in extractions)}"
        )
    return [submit_extraction(session, extraction) for extraction in extractions]


async def submit_extraction(session: database_utils.Session, page_extraction: db.PageExtraction) -> None:
    from ..sandbox import extraction as sandbox_extraction  # noqa: F401 to populate ORM metadata

    assert page_extraction.pdf_file_range is not None
    sha256 = page_extraction.pdf_file_range.pdf_file.sha256
    if sha256 in pdf_data_cache:
        logs.log(f"Found PDF data for page extraction {page_extraction.id} in cache")
        pdf_data = pdf_data_cache[sha256]
    else:
        logs.log(f"Loading PDF data for page extraction {page_extraction.id}")
        pdf_data = file_storage.pdf_files.load(sha256)
        pdf_data_cache[sha256] = pdf_data
    pdf_page_image = pdf_page_as_image(pdf_data, page_extraction.pdf_page_number)

    annotated_pdf_page_image, detected_images = detect_images(f"p{page_extraction.pdf_page_number}", pdf_page_image)

    if settings.DETECTED_IMAGES_SAVE_PATH is not None:
        pdf_page_image.save(f"{settings.DETECTED_IMAGES_SAVE_PATH}/{sha256}.p{page_extraction.pdf_page_number}.png")
        annotated_pdf_page_image.save(
            f"{settings.DETECTED_IMAGES_SAVE_PATH}/{sha256}.p{page_extraction.pdf_page_number}.annotated.png"
        )
        for identifier, image in detected_images.items():
            image.save(
                f"{settings.DETECTED_IMAGES_SAVE_PATH}/{sha256}.p{page_extraction.pdf_page_number}.extracted.{identifier}.png"
            )

    created_at = datetime.datetime.now(tz=datetime.timezone.utc)

    extracted_images: list[tuple[exercises.ExerciseImage, PIL.Image.Image]] = []
    for identifier, image in detected_images.items():
        extracted_image = exercises.ExerciseImage(
            local_identifier=identifier,
            created=db.ExerciseImageCreationByPageExtraction(at=created_at, page_extraction=page_extraction),
        )
        session.add(extracted_image)
        extracted_images.append((extracted_image, image))
    session.flush()  # To get all extracted image ids
    for extracted_image, image in extracted_images:
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)
        file_storage.exercise_images.store(f"{extracted_image.id}.png", image_bytes.getvalue())

    if page_extraction.settings.append_text_and_styles_to_prompt:
        assert page_extraction.settings.output_schema_version == "v3"
        text_and_styles = extract_text_and_styles_from_pdf_page(pdf_data, page_extraction.pdf_page_number)
        if settings.DETECTED_IMAGES_SAVE_PATH is not None:
            with open(
                f"{settings.DETECTED_IMAGES_SAVE_PATH}/{sha256}.p{page_extraction.pdf_page_number}.text_and_styles.csv",
                "w",
                encoding="utf-8",
            ) as f:
                f.write(text_and_styles)
    else:
        text_and_styles = None

    if page_extraction.settings.output_schema_version == "v2":
        submit_extraction_v2(session, page_extraction, annotated_pdf_page_image)
    elif page_extraction.settings.output_schema_version == "v3":
        submit_extraction_v3(session, page_extraction, text_and_styles, annotated_pdf_page_image)
    else:
        assert False


def submit_extraction_v2(
    session: database_utils.Session, page_extraction: db.PageExtraction, annotated_pdf_page_image: PIL.Image.Image
) -> None:

    # All branches must set 'extraction.assistant_response' to avoid infinite loop
    # (re-submitting failing extraction again and again)
    try:
        logs.log(f"Submitting page extraction {page_extraction.id}")
        with logs.timer() as timing:
            extracted_exercises = page_extraction.model.extract_v2(
                page_extraction.settings.prompt, annotated_pdf_page_image
            )
    except InvalidJsonLlmException as error:
        logs.log(f"Error 'invalid JSON' on page extraction {page_extraction.id} in {timing.elapsed:.1f} seconds")
        page_extraction.assistant_response = assistant_responses.InvalidJsonError(
            kind="error", error="invalid-json", parsed=error.parsed
        )
    except NotJsonLlmException as error:
        logs.log(f"Error 'not JSON' on page extraction {page_extraction.id} in {timing.elapsed:.1f} seconds")
        page_extraction.assistant_response = assistant_responses.NotJsonError(
            kind="error", error="not-json", text=error.text
        )
    except Exception:
        logs.log(f"UNEXPECTED ERROR on page extraction {page_extraction.id} in {timing.elapsed:.1f} seconds")
        traceback.print_exc()
        page_extraction.assistant_response = assistant_responses.UnknownError(kind="error", error="unknown")
    else:
        logs.log(f"Success on page extraction {page_extraction.id} in {timing.elapsed:.1f} seconds")

        extracted_exercises_parts = []
        for extracted_exercise in extracted_exercises:
            instruction_hint_example_text = "\n".join(
                filter(
                    None,
                    extracted_exercise.properties.consignes
                    + [extracted_exercise.properties.conseil, extracted_exercise.properties.exemple],
                )
            )
            full_text = "\n".join(
                filter(
                    None,
                    [
                        instruction_hint_example_text,
                        extracted_exercise.properties.enonce,
                        extracted_exercise.properties.references,
                        extracted_exercise.properties.autre,
                    ],
                )
            )
            extracted_exercises_parts.append(
                (
                    extracted_exercise.properties.numero,
                    instruction_hint_example_text,
                    extracted_exercise.properties.enonce,
                    full_text,
                )
            )

        submit_follow_ups(session, page_extraction, extracted_exercises_parts)

        page_extraction.assistant_response = assistant_responses.SuccessV2(
            kind="success", version="v2", exercises=extracted_exercises
        )
    finally:
        page_extraction.timing = timing


def submit_extraction_v3(
    session: database_utils.Session,
    page_extraction: db.PageExtraction,
    text_and_styles: str | None,
    annotated_pdf_page_image: PIL.Image.Image,
) -> None:
    if text_and_styles is None:
        prompt = page_extraction.settings.prompt
    else:
        prompt = f'{page_extraction.settings.prompt}\n\n--- {{ CSV input :  "\n{text_and_styles}\n"}}'

    # All branches must set 'extraction.assistant_response' to avoid infinite loop
    # (re-submitting failing extraction again and again)
    try:
        logs.log(f"Submitting page extraction {page_extraction.id}")
        with logs.timer() as timing:
            extracted_exercises = page_extraction.model.extract_v3(prompt, annotated_pdf_page_image)
    except InvalidJsonLlmException as error:
        logs.log(f"Error 'invalid JSON' on page extraction {page_extraction.id} in {timing.elapsed:.1f} seconds")
        page_extraction.assistant_response = assistant_responses.InvalidJsonError(
            kind="error", error="invalid-json", parsed=error.parsed
        )
    except NotJsonLlmException as error:
        logs.log(f"Error 'not JSON' on page extraction {page_extraction.id} in {timing.elapsed:.1f} seconds")
        page_extraction.assistant_response = assistant_responses.NotJsonError(
            kind="error", error="not-json", text=error.text
        )
    except Exception:
        logs.log(f"UNEXPECTED ERROR on page extraction {page_extraction.id} in {timing.elapsed:.1f} seconds")
        traceback.print_exc()
        page_extraction.assistant_response = assistant_responses.UnknownError(kind="error", error="unknown")
    else:
        logs.log(f"Success on page extraction {page_extraction.id} in {timing.elapsed:.1f} seconds")

        extracted_exercises_parts = []
        for extracted_exercise in extracted_exercises:
            instruction_hint_example_text = "\n".join(
                filter(
                    None,
                    [
                        extracted_exercise.properties.instruction,
                        (
                            f"Catégories: {', '.join(extracted_exercise.properties.labels)}"
                            if extracted_exercise.properties.labels
                            else ""
                        ),
                        extracted_exercise.properties.hint,
                        extracted_exercise.properties.example,
                    ],
                )
            )
            full_text = "\n".join(
                filter(
                    None,
                    [
                        instruction_hint_example_text,
                        extracted_exercise.properties.statement,
                        extracted_exercise.properties.references,
                    ],
                )
            )
            extracted_exercises_parts.append(
                (
                    extracted_exercise.properties.number,
                    instruction_hint_example_text,
                    extracted_exercise.properties.statement,
                    full_text,
                )
            )

        submit_follow_ups(session, page_extraction, extracted_exercises_parts)

        page_extraction.assistant_response = assistant_responses.SuccessV3(
            kind="success", version="v3", exercises=extracted_exercises
        )
    finally:
        page_extraction.timing = timing


def submit_follow_ups(
    session: database_utils.Session,
    page_extraction: db.PageExtraction,
    extracted_exercises_parts: list[tuple[str | None, str, str | None, str]],
) -> None:
    from .. import textbooks

    created_at = datetime.datetime.now(tz=datetime.timezone.utc)

    if page_extraction.run_classification:
        classification_chunk = classification.ClassificationChunk(
            created=db.ClassificationChunkCreationByPageExtraction(at=created_at, page_extraction=page_extraction),
            model_for_adaptation=page_extraction.model_for_adaptation,
            timing=None,
        )
        session.add(classification_chunk)
    else:
        classification_chunk = None

    for number, instruction_hint_example_text, statement_text, full_text in extracted_exercises_parts:
        if number is not None:
            location: exercises.ExerciseLocation
            if isinstance(page_extraction.created, textbooks.PageExtractionCreationByTextbook):
                extraction_batch = page_extraction.created.textbook_extraction_batch
                location = textbooks.ExerciseLocationTextbook(
                    textbook=extraction_batch.textbook,
                    page_number=extraction_batch.first_textbook_page_number
                    + page_extraction.pdf_page_number
                    - extraction_batch.pdf_file_range.first_page_number,
                    exercise_number=number,
                    marked_as_removed=False,
                )
            else:
                location = exercises.ExerciseLocationMaybePageAndNumber(
                    page_number=page_extraction.pdf_page_number, exercise_number=number
                )

            exercise = adaptation.AdaptableExercise(
                created=db.ExerciseCreationByPageExtraction(at=created_at, page_extraction=page_extraction),
                location=location,
                full_text=full_text,
                instruction_hint_example_text=instruction_hint_example_text,
                statement_text=statement_text,
            )
            session.add(exercise)

            if classification_chunk is not None:
                session.add(
                    classification.ClassificationByChunk(
                        exercise=exercise, at=created_at, classification_chunk=classification_chunk, exercise_class=None
                    )
                )


def pdf_page_as_image(pdf_data: bytes, page_number: int) -> PIL.Image.Image:
    # Not using PyMuPDF or pdf2image:
    #  - MuPDF allegedly has lesser rendering fidelity than Poppler's pdftoppm
    #  - pdf2image writes the PDF to disk (in /tmp), which can be slow on a Raspberry Pi's SD card
    #  - this is simple enough anyway
    page = str(page_number)
    process = subprocess.run(["pdftoppm", "-f", page, "-l", page], input=pdf_data, capture_output=True, check=True)
    return PIL.Image.open(io.BytesIO(process.stdout))
