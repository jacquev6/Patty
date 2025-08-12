import datetime
import io
import subprocess
import traceback
import typing

import boto3
import botocore
import cachetools
import PIL.Image
import sqlalchemy as sql
import urllib.parse

from . import orm_models as extraction_orm_models
from .assistant_responses import (
    AssistantSuccess,
    AssistantUnknownError,
    AssistantInvalidJsonError,
    AssistantNotJsonError,
)
from .llm import InvalidJsonLlmException, NotJsonLlmException
from .. import database_utils
from .. import settings
from ..adaptation import orm_models as adaptation_orm_models
from ..classification import orm_models as classification_orm_models
from ..exercises import orm_models as exercises_orm_models


def log(message: str) -> None:
    # @todo Use actual logging
    print(datetime.datetime.now(), message, flush=True)


s3 = boto3.client("s3", config=botocore.client.Config(region_name="eu-west-3", signature_version="s3v4"))

pdf_data_cache = cachetools.TTLCache[str, bytes](maxsize=5, ttl=60 * 60)


def submit_extractions(session: database_utils.Session, parallelism: int) -> list[typing.Coroutine[None, None, None]]:
    extractions = (
        session.execute(
            sql.select(extraction_orm_models.PageExtraction)
            .where(extraction_orm_models.PageExtraction._assistant_response == sql.null())
            .limit(parallelism)
        )
        .scalars()
        .all()
    )
    if len(extractions) > 0:
        log(
            f"Found {len(extractions)} pending page extractions: {' '.join(str(extraction.id) for extraction in extractions)}"
        )
    return [submit_extraction(session, extraction) for extraction in extractions]


async def submit_extraction(
    session: database_utils.Session, page_extraction: extraction_orm_models.PageExtraction
) -> None:
    assert page_extraction.pdf_range is not None
    sha256 = page_extraction.pdf_range.pdf_file.sha256
    if sha256 in pdf_data_cache:
        log(f"Found PDF data for page extraction {page_extraction.id} in cache")
        pdf_data = pdf_data_cache[sha256]
    else:
        target = urllib.parse.urlparse(f"{settings.PDF_FILES_URL}/{sha256}")
        log(f"Fetching PDF data for page extraction {page_extraction.id} from {target.geturl()}")
        pdf_data = s3.get_object(Bucket=target.netloc, Key=target.path[1:])["Body"].read()
        pdf_data_cache[sha256] = pdf_data
    image = pdf_page_as_image(pdf_data, page_extraction.pdf_page_number)

    # All branches must set 'extraction.assistant_response' to avoid infinite loop
    # (re-submitting failing extraction again and again)
    try:
        log(f"Submitting page extraction {page_extraction.id}")
        extracted_exercises = page_extraction.model.extract(page_extraction.settings.prompt, image)
    except InvalidJsonLlmException as error:
        log(f"Error 'invalid JSON' on page extraction {page_extraction.id}")
        page_extraction.assistant_response = AssistantInvalidJsonError(
            kind="error", error="invalid-json", parsed=error.parsed
        )
    except NotJsonLlmException as error:
        log(f"Error 'not JSON' on page extraction {page_extraction.id}")
        page_extraction.assistant_response = AssistantNotJsonError(kind="error", error="not-json", text=error.text)
    except Exception:
        log(f"UNEXPECTED ERROR on page extraction {page_extraction.id}")
        traceback.print_exc()
        page_extraction.assistant_response = AssistantUnknownError(kind="error", error="unknown")
    else:
        log(f"Success on page extraction {page_extraction.id}")

        created_at = datetime.datetime.now(tz=datetime.timezone.utc)

        if page_extraction.run_classification:
            classification_chunk = classification_orm_models.ExerciseClassificationChunk(
                created=extraction_orm_models.ExerciseClassificationChunkCreationByPageExtraction(
                    at=created_at, page_extraction=page_extraction
                ),
                model_for_adaptation=page_extraction.model_for_adaptation,
            )
            session.add(classification_chunk)
        else:
            classification_chunk = None

        for extracted_exercise in extracted_exercises:
            instruction_hint_example_text = "\n".join(
                filter(None, extracted_exercise.consignes + [extracted_exercise.conseil, extracted_exercise.exemple])
            )
            full_text = "\n".join(
                filter(
                    None,
                    [
                        instruction_hint_example_text,
                        extracted_exercise.enonce,
                        extracted_exercise.references,
                        extracted_exercise.autre,
                    ],
                )
            )
            exercise = adaptation_orm_models.AdaptableExercise(
                created=extraction_orm_models.ExerciseCreationByPageExtraction(
                    at=created_at, page_extraction=page_extraction
                ),
                location=exercises_orm_models.ExerciseLocationMaybePageAndNumber(
                    page_number=page_extraction.pdf_page_number, exercise_number=extracted_exercise.numero
                ),
                removed_from_textbook=False,
                full_text=full_text,
                instruction_hint_example_text=instruction_hint_example_text,
                statement_text=extracted_exercise.enonce,
            )
            session.add(exercise)

            if classification_chunk is not None:
                session.add(
                    classification_orm_models.ExerciseClassificationByClassificationChunk(
                        exercise=exercise, at=created_at, classification_chunk=classification_chunk, exercise_class=None
                    )
                )

        page_extraction.assistant_response = AssistantSuccess(kind="success", exercises=extracted_exercises)


def pdf_page_as_image(pdf_data: bytes, page_number: int) -> PIL.Image.Image:
    # Not using PyMuPDF or pdf2image:
    #  - MuPDF allegedly has lesser rendering fidelity than Poppler's pdftoppm
    #  - pdf2image writes the PDF to disk (in /tmp), which can be slow on a Raspberry Pi's SD card
    #  - this is simple enough anyway
    page = str(page_number)
    process = subprocess.run(["pdftoppm", "-f", page, "-l", page], input=pdf_data, capture_output=True, check=True)
    return PIL.Image.open(io.BytesIO(process.stdout))
