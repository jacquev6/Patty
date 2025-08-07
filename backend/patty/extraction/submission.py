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

from .. import database_utils
from .. import settings
from .. import orm_models as db
from .assistant_responses import (
    AssistantSuccess,
    AssistantUnknownError,
    AssistantInvalidJsonError,
    AssistantNotJsonError,
)
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
    assert page_extraction.range is not None
    sha256 = page_extraction.range.pdf_file.sha256
    if sha256 in pdf_data_cache:
        log(f"Found PDF data for page extraction {page_extraction.id} in cache")
        pdf_data = pdf_data_cache[sha256]
    else:
        target = urllib.parse.urlparse(f"{settings.PDF_FILES_URL}/{sha256}")
        log(f"Fetching PDF data for page extraction {page_extraction.id} from {target.geturl()}")
        pdf_data = s3.get_object(Bucket=target.netloc, Key=target.path[1:])["Body"].read()
        pdf_data_cache[sha256] = pdf_data
    image = pdf_page_as_image(pdf_data, page_extraction.page_number)

    # All branches must set 'extraction.assistant_response' to avoid infinite loop
    # (re-submitting failing extraction again and again)
    try:
        log(f"Submitting page extraction {page_extraction.id}")
        assert page_extraction.strategy is not None
        extracted_exercises = page_extraction.strategy.model.extract(page_extraction.strategy.prompt, image)
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
            classification_batch = db.SandboxClassificationBatch(
                created_at=created_at,
                created_by_username=None,
                created_by_page_extraction=page_extraction,
                model_for_adaptation=page_extraction.model_for_adaptation,
            )
            session.add(classification_batch)
        else:
            classification_batch = None

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
            exercise = db.AdaptableExercise(
                created=db.ExerciseCreationByPageExtraction(at=created_at, page_extraction=page_extraction),
                location=db.ExerciseLocationMaybePageAndNumber(
                    page_number=page_extraction.page_number, exercise_number=extracted_exercise.numero
                ),
                removed_from_textbook=False,
                full_text=full_text,
                instruction_hint_example_text=instruction_hint_example_text,
                statement_text=extracted_exercise.enonce,
                classified_at=None,
                classified_by_classification_batch=classification_batch,
                classified_by_username=None,
                exercise_class=None,
            )
            session.add(exercise)
        page_extraction.assistant_response = AssistantSuccess(kind="success", exercises=extracted_exercises)


def pdf_page_as_image(pdf_data: bytes, page_number: int) -> PIL.Image.Image:
    # Not using PyMuPDF or pdf2image:
    #  - MuPDF allegedly has lesser rendering fidelity than Poppler's pdftoppm
    #  - pdf2image writes the PDF to disk (in /tmp), which can be slow on a Raspberry Pi's SD card
    #  - this is simple enough anyway
    page = str(page_number)
    process = subprocess.run(["pdftoppm", "-f", page, "-l", page], input=pdf_data, capture_output=True, check=True)
    return PIL.Image.open(io.BytesIO(process.stdout))
