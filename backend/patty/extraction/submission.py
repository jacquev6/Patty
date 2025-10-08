import datetime
import io
import subprocess
import traceback
import typing
import urllib.parse

import boto3
import botocore
import cachetools
import PIL.Image
import sqlalchemy as sql

from . import assistant_responses
from . import orm_models as db
from .. import adaptation
from .. import classification
from .. import database_utils
from .. import exercises
from .. import logs
from .. import settings
from .images_detection import detect_images
from .llm import InvalidJsonLlmException, NotJsonLlmException


def log(message: str) -> None:
    # @todo Use actual logging
    print(datetime.datetime.now(), message, flush=True)


s3 = boto3.client("s3", config=botocore.client.Config(region_name="eu-west-3", signature_version="s3v4"))

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
        log(
            f"Found {len(extractions)} pending page extractions: {' '.join(str(extraction.id) for extraction in extractions)}"
        )
    return [submit_extraction(session, extraction) for extraction in extractions]


async def submit_extraction(session: database_utils.Session, page_extraction: db.PageExtraction) -> None:
    from .. import textbooks
    from ..sandbox import extraction as sandbox_extraction  # noqa: F401 to populate ORM metadata

    assert page_extraction.pdf_file_range is not None
    sha256 = page_extraction.pdf_file_range.pdf_file.sha256
    if sha256 in pdf_data_cache:
        log(f"Found PDF data for page extraction {page_extraction.id} in cache")
        pdf_data = pdf_data_cache[sha256]
    else:
        target = urllib.parse.urlparse(f"{settings.PDF_FILES_URL}/{sha256}")
        log(f"Fetching PDF data for page extraction {page_extraction.id} from {target.geturl()}")
        pdf_data = s3.get_object(Bucket=target.netloc, Key=target.path[1:])["Body"].read()
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
        target = urllib.parse.urlparse(f"{settings.EXERCISE_IMAGES_URL}/{extracted_image.id}.png")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)
        s3.put_object(Bucket=target.netloc, Key=target.path[1:], Body=image_bytes, ContentType="image/png")

    # All branches must set 'extraction.assistant_response' to avoid infinite loop
    # (re-submitting failing extraction again and again)
    try:
        log(f"Submitting page extraction {page_extraction.id}")
        with logs.timer() as timing:
            extracted_exercises = page_extraction.model.extract(
                page_extraction.settings.prompt, annotated_pdf_page_image
            )
    except InvalidJsonLlmException as error:
        log(f"Error 'invalid JSON' on page extraction {page_extraction.id} in {timing.elapsed:.1f} seconds")
        page_extraction.assistant_response = assistant_responses.InvalidJsonError(
            kind="error", error="invalid-json", parsed=error.parsed
        )
    except NotJsonLlmException as error:
        log(f"Error 'not JSON' on page extraction {page_extraction.id} in {timing.elapsed:.1f} seconds")
        page_extraction.assistant_response = assistant_responses.NotJsonError(
            kind="error", error="not-json", text=error.text
        )
    except Exception:
        log(f"UNEXPECTED ERROR on page extraction {page_extraction.id} in {timing.elapsed:.1f} seconds")
        traceback.print_exc()
        page_extraction.assistant_response = assistant_responses.UnknownError(kind="error", error="unknown")
    else:
        log(f"Success on page extraction {page_extraction.id} in {timing.elapsed:.1f} seconds")

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

            if extracted_exercise.properties.numero is not None:
                location: exercises.ExerciseLocation
                if isinstance(page_extraction.created, textbooks.PageExtractionCreationByTextbook):
                    extraction_batch = page_extraction.created.textbook_extraction_batch
                    location = textbooks.ExerciseLocationTextbook(
                        textbook=extraction_batch.textbook,
                        page_number=extraction_batch.first_textbook_page_number
                        + page_extraction.pdf_page_number
                        - extraction_batch.pdf_file_range.first_page_number,
                        exercise_number=extracted_exercise.properties.numero,
                        removed_from_textbook=False,
                    )
                else:
                    location = exercises.ExerciseLocationMaybePageAndNumber(
                        page_number=page_extraction.pdf_page_number,
                        exercise_number=extracted_exercise.properties.numero,
                    )

                exercise = adaptation.AdaptableExercise(
                    created=db.ExerciseCreationByPageExtraction(at=created_at, page_extraction=page_extraction),
                    location=location,
                    full_text=full_text,
                    instruction_hint_example_text=instruction_hint_example_text,
                    statement_text=extracted_exercise.properties.enonce,
                )
                session.add(exercise)

                if classification_chunk is not None:
                    session.add(
                        classification.ClassificationByChunk(
                            exercise=exercise,
                            at=created_at,
                            classification_chunk=classification_chunk,
                            exercise_class=None,
                        )
                    )

        page_extraction.assistant_response = assistant_responses.Success(kind="success", exercises=extracted_exercises)
    finally:
        page_extraction.timing = timing


def pdf_page_as_image(pdf_data: bytes, page_number: int) -> PIL.Image.Image:
    # Not using PyMuPDF or pdf2image:
    #  - MuPDF allegedly has lesser rendering fidelity than Poppler's pdftoppm
    #  - pdf2image writes the PDF to disk (in /tmp), which can be slow on a Raspberry Pi's SD card
    #  - this is simple enough anyway
    page = str(page_number)
    process = subprocess.run(["pdftoppm", "-f", page, "-l", page], input=pdf_data, capture_output=True, check=True)
    return PIL.Image.open(io.BytesIO(process.stdout))
