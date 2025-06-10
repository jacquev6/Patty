import datetime
import io
import json
import os
import subprocess
import traceback
import typing
import unittest

import boto3
import botocore
import cachetools
import google.genai.types
import PIL.Image
import pydantic
import sqlalchemy as sql
import urllib.parse

from . import database_utils
from . import extracted
from . import settings
from .fixtures import make_default_extraction_prompt
from .test_utils import costs_money
from .orm_models import PageExtraction, AdaptableExercise, ExtractionStrategy


def log(message: str) -> None:
    # @todo Use actual logging
    print(datetime.datetime.now(), message, flush=True)


client = google.genai.Client(api_key=os.environ["GEMINIAI_KEY"])

s3 = boto3.client("s3", config=botocore.client.Config(region_name="eu-west-3", signature_version="s3v4"))

pdf_data_cache = cachetools.TTLCache[str, bytes](maxsize=5, ttl=60 * 60)


def submit_extractions(session: database_utils.Session, parallelism: int) -> list[typing.Coroutine[None, None, None]]:
    extractions = (
        session.execute(sql.select(PageExtraction).where(PageExtraction.status == "pending").limit(parallelism))
        .scalars()
        .all()
    )
    log(
        f"Found {len(extractions)} pending page extractions: {' '.join(str(extraction.id) for extraction in extractions)}"
    )
    return [submit_extraction(session, extraction) for extraction in extractions]


async def submit_extraction(session: database_utils.Session, extraction: PageExtraction) -> None:
    sha256 = extraction.extraction_batch.range.pdf_file.sha256
    if sha256 in pdf_data_cache:
        log(f"Found PDF data for page extraction {extraction.id} in cache")
        pdf_data = pdf_data_cache[sha256]
    else:
        target = urllib.parse.urlparse(f"{settings.PDF_FILES_URL}/{sha256}")
        log(f"Fetching PDF data for page extraction {extraction.id} from {target.geturl()}")
        pdf_data = s3.get_object(Bucket=target.netloc, Key=target.path[1:])["Body"].read()
        pdf_data_cache[sha256] = pdf_data
    image = pdf_page_as_image(pdf_data, extraction.page_number)

    # All branches must set 'extraction.status' to avoid infinite loop
    # (re-submitting failing extraction again and again)
    try:
        log(f"Submitting page extraction {extraction.id}")
        # @todo Use Gemini with an asynchronous client
        extracted_exercises = extract(image, extraction.extraction_batch.strategy)
    except Exception:
        log(f"UNEXPECTED ERROR on page extraction {extraction.id}")
        traceback.print_exc()
        extraction.status = "failure"
    else:
        log(f"Success on page extraction {extraction.id}")
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
            exercise = AdaptableExercise(
                created_at=datetime.datetime.now(),
                created_by_username="Extraction",
                textbook=None,
                removed_from_textbook=False,
                page_number=extraction.page_number,
                exercise_number=extracted_exercise.numero,
                created_by_page_extraction=extraction,
                full_text=full_text,
                instruction_hint_example_text=instruction_hint_example_text,
                statement_text=extracted_exercise.enonce,
                classified_at=None,
                classified_by_classification_batch=None,
                classified_by_username=None,
                exercise_class=None,
            )
            session.add(exercise)
        extraction.status = "success"


def extract(image: PIL.Image.Image, strategy: ExtractionStrategy) -> list[extracted.Exercise]:
    contents: list[google.genai.types.ContentUnion] = [strategy.prompt, image]
    response = client.models.generate_content(model="gemini-2.0-flash", contents=contents).text
    assert response is not None

    cleaned_response = response.strip()
    if cleaned_response.startswith("```json"):
        cleaned_response = cleaned_response.replace("```json", "").strip()
    if cleaned_response.endswith("```"):
        cleaned_response = cleaned_response[:-3].strip()

    return pydantic.RootModel[list[extracted.Exercise]](json.loads(cleaned_response)).root


def pdf_page_as_image(pdf_data: bytes, page_number: int) -> PIL.Image.Image:
    # Not using PyMuPDF or pdf2image:
    #  - MuPDF allegedly has lesser rendering fidelity than Poppler's pdftoppm
    #  - pdf2image writes the PDF to disk (in /tmp), which can be slow on a Raspberry Pi's SD card
    #  - this is simple enough anyway
    page = str(page_number)
    process = subprocess.run(["pdftoppm", "-f", page, "-l", page], input=pdf_data, capture_output=True, check=True)
    return PIL.Image.open(io.BytesIO(process.stdout))


class ExtractionTestCase(unittest.TestCase):
    def setUp(self) -> None:
        with open("../frontend/e2e-tests/inputs/test.pdf", "rb") as f:
            self.pdf_data = f.read()

    def test_pdf_page_as_image(self) -> None:
        self.assertIsInstance(pdf_page_as_image(self.pdf_data, 1), PIL.Image.Image)

    @costs_money
    def test_extract(self) -> None:
        exercises = extract(
            pdf_page_as_image(self.pdf_data, 2), ExtractionStrategy(prompt=make_default_extraction_prompt())
        )
        actual_ids = tuple(exercise.id for exercise in exercises)
        possible_expected_ids = [
            (
                "p7_ex5",
                "p7_ex6",
                "p7_ex7",
                "p7_ex8",
                "p7_exDefiLangue",
                "p7_ex9",
                "p7_ex10",
                "p7_ex11",
                "p7_ex12",
                "p7_ex13",
                "p7_ex14",
            ),
            (
                "p7_ex5",
                "p7_ex6",
                "p7_ex7",
                "p7_ex8",
                "p7_exDefiLangue",
                "p7_ex9",
                "p7_ex10",
                "p7_ex11",
                "p7_ex12",
                "p7_exJecris13",
                "p7_ex14",
            ),
            (
                "p7_ex5",
                "p7_ex6",
                "p7_ex7",
                "p7_ex8",
                "p7_exDefiLangue",
                "p7_ex9",
                "p7_ex10",
                "p7_ex11",
                "p7_ex12",
                "p7_exJecris",
                "p7_ex14",
            ),
        ]
        self.assertIn(actual_ids, possible_expected_ids)
