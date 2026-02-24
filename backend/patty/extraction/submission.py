# MALIN Platform https://malin.cahiersfantastiques.fr/
# Copyright 2025 Mohamed-Amine Lasheb <mohamed-amine.lasheb@lecnam.net>
# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
from ..retry import RetryableError
from .images_detection import detect_images
from .postprocessing import cleanup_slashes, remove_styles
from .llm import InvalidJsonLlmException, NotJsonLlmException
from .text_and_styles_extraction import extract_text_and_styles_from_pdf_page


pdf_data_cache = cachetools.TTLCache[str, bytes](maxsize=5, ttl=60 * 60)


def submit_next_extraction(
    can_retry: bool, session: database_utils.Session
) -> typing.Coroutine[None, None, None] | None:
    extraction = (
        session.execute(sql.select(db.PageExtraction).where(db.PageExtraction._assistant_response == sql.null()))
        .scalars()
        .first()
    )
    if extraction is None:
        return None
    else:
        logs.log(f"Found pending page extraction: {extraction.id}")
        return submit_extraction(can_retry, session, extraction)


async def submit_extraction(
    can_retry: bool, session: database_utils.Session, page_extraction: db.PageExtraction
) -> None:
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

    if page_extraction.settings.output_schema_description.version == "v2":
        submit_extraction_v2(can_retry, session, page_extraction, annotated_pdf_page_image)
    elif page_extraction.settings.output_schema_description.version == "v3":
        if page_extraction.settings.output_schema_description.append_text_and_styles_to_prompt:
            page_extraction.extracted_text_and_styles = extract_text_and_styles_from_pdf_page(
                pdf_data, page_extraction.pdf_page_number
            )
            if settings.DETECTED_IMAGES_SAVE_PATH is not None:
                with open(
                    f"{settings.DETECTED_IMAGES_SAVE_PATH}/{sha256}.p{page_extraction.pdf_page_number}.text_and_styles.csv",
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(page_extraction.extracted_text_and_styles)
        else:
            page_extraction.extracted_text_and_styles = None
        submit_extraction_v3(can_retry, session, page_extraction, annotated_pdf_page_image)
    else:
        assert False


def submit_extraction_v2(
    can_retry: bool,
    session: database_utils.Session,
    page_extraction: db.PageExtraction,
    annotated_pdf_page_image: PIL.Image.Image,
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
        page_extraction.assistant_response = assistant_responses.InvalidJsonErrorV2(
            kind="error", error="invalid-json", version="v2", parsed=error.parsed
        )
    except NotJsonLlmException as error:
        logs.log(f"Error 'not JSON' on page extraction {page_extraction.id} in {timing.elapsed:.1f} seconds")
        page_extraction.assistant_response = assistant_responses.NotJsonErrorV2(
            kind="error", error="not-json", version="v2", text=error.raw_response
        )
    except RetryableError:
        if can_retry:
            logs.log(f"RETRYABLE ERROR on page extraction {page_extraction.id} in {timing.elapsed:.1f} seconds")
            raise
        else:
            logs.log(
                f"Too many RETRYABLE ERRORS on page extraction {page_extraction.id} in {timing.elapsed:.1f} seconds"
            )
            page_extraction.assistant_response = assistant_responses.UnknownError(kind="error", error="unknown")
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
    can_retry: bool,
    session: database_utils.Session,
    page_extraction: db.PageExtraction,
    annotated_pdf_page_image: PIL.Image.Image,
) -> None:
    assert page_extraction.settings.output_schema_description.version == "v3"

    if page_extraction.settings.output_schema_description.append_text_and_styles_to_prompt:
        assert page_extraction.extracted_text_and_styles is not None
        prompt = f'{page_extraction.settings.prompt}\n\n--- {{ CSV input :  "\n{page_extraction.extracted_text_and_styles}\n"}}'
    else:
        assert page_extraction.extracted_text_and_styles is None
        prompt = page_extraction.settings.prompt

    if page_extraction.settings.output_schema_description.cleanup_slashes:
        pre_cleanup = cleanup_slashes
    else:

        def pre_cleanup(s: str, /) -> str:
            return s

    # All branches must set 'extraction.assistant_response' to avoid infinite loop
    # (re-submitting failing extraction again and again)
    try:
        logs.log(f"Submitting page extraction {page_extraction.id}")
        with logs.timer() as timing:
            raw_response, cleaned_response, extracted_exercises = page_extraction.model.extract_v3(
                prompt, annotated_pdf_page_image, pre_cleanup
            )
    except InvalidJsonLlmException as error:
        logs.log(f"Error 'invalid JSON' on page extraction {page_extraction.id} in {timing.elapsed:.1f} seconds")
        page_extraction.assistant_response = assistant_responses.InvalidJsonErrorV3(
            kind="error",
            error="invalid-json",
            version="v3",
            raw_response=error.raw_response,
            cleaned_response=error.cleaned_response,
            parsed=error.parsed,
        )
    except NotJsonLlmException as error:
        logs.log(f"Error 'not JSON' on page extraction {page_extraction.id} in {timing.elapsed:.1f} seconds")
        page_extraction.assistant_response = assistant_responses.NotJsonErrorV3(
            kind="error",
            error="not-json",
            version="v3",
            raw_response=error.raw_response,
            cleaned_response=error.cleaned_response,
        )
    except RetryableError:
        if can_retry:
            logs.log(f"RETRYABLE ERROR on page extraction {page_extraction.id} in {timing.elapsed:.1f} seconds")
            raise
        else:
            logs.log(
                f"Too many RETRYABLE ERRORS on page extraction {page_extraction.id} in {timing.elapsed:.1f} seconds"
            )
            page_extraction.assistant_response = assistant_responses.UnknownError(kind="error", error="unknown")
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
                            if len(extracted_exercise.properties.labels) > 0
                            else None
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
                    remove_styles(instruction_hint_example_text),
                    (
                        None
                        if extracted_exercise.properties.statement is None
                        else remove_styles(extracted_exercise.properties.statement)
                    ),
                    full_text,
                )
            )

        submit_follow_ups(session, page_extraction, extracted_exercises_parts)

        page_extraction.assistant_response = assistant_responses.SuccessV3(
            kind="success",
            version="v3",
            raw_response=raw_response,
            cleaned_response=cleaned_response,
            exercises=extracted_exercises,
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
