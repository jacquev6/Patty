import io
import json
import os
import subprocess
import typing
import unittest

import google.genai.types
import PIL.Image
import pydantic

from .llm.test_utils import costs_money


client = google.genai.Client(api_key=os.environ["GEMINIAI_KEY"])


# These are needed to make extraction more robust:
# @todo Make this model stricter (forbid extra fields, enforce some fields)
# @todo Make this model simpler: remove properties, use a flat structure
# @todo Switch to english names for fields
class Exercise(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="ignore")

    id: str
    type: typing.Literal["exercice"]

    class Properties(pydantic.BaseModel):
        model_config = pydantic.ConfigDict(extra="ignore")

        numero: str | None = None
        consignes: list[str] = []
        enonce: str | None = None
        conseil: str | None = None
        exemple: str | None = None
        references: str | None = None
        autre: str | None = None

    properties: Properties | None = None


example_exercise = Exercise(
    **{  # type: ignore[arg-type]
        "id": "p47_ex4",
        "type": "exercice",
        "properties": {
            "numero": "1",
            "consignes": [
                "Additionne les nombres suivants et donne le résultat.",
                "Soustrais les nombres suivants et donne le résultat.",
            ],
            "enonce": "7 + 3, 5 + 2, 8 + 6, 4 + 9",
            "conseil": "Commence par ajouter les unités et vérifie ton résultat.",
            "exemple": "4 + 5 = 9.",
            "references": "© Source: Manuel de mathématiques, page 34.",
            "autre": "Informations additionnelles si présentes.",
        },
    }
)


extraction_prompt = f"""\
You are an expert in the extraction and structuring of educational exercises from texts. Your task is to :
1. Carefully read the input and extract exercises without modifying the text in any way. Keep the exact format, language, letters, words, punctuation, and sentence structure as in the original.
2. Extract only the exercise-related elements, structured as follows:

   JSON Schema:
{ example_exercise.model_dump_json(indent=2) }

3. Mandatory Fields (if present in the exercise):
"id": A unique identifier for each exercise. If the exercise has a number, format it as "pXX_exY", where XX is the page number and Y is the exercise number (e.g., "p47_ex4"). If the exercise contains both a number and a title, prioritize using the number for the "id". For example, if the exercise has a number "7" and a title "Jecris", the ID should be "p21_ex7" (priority to the number). If no number is given, use a descriptive title for the exercise (e.g., "p45_exDefiLangue", "p49_exJecris").
    - "numero": Exercise number (e.g., "1"). If no number is given, skip it.
    - "consignes": A **list** of all instructions that belong to the same exercise. These are often bolded or clearly marked.
    - **"exemple": Example or model solution (optional). Identify text that demonstrates how to do the exercise. Look for visual/textual cues:
        - **Position:** Often appears *between* the `consignes` and the main `enonce` (especially before lists like a., b., c...).
        - **Keywords:** May start with indicators like "Exemple:", "Ex:", etc.
        - **Formatting:** May use distinct formatting such as *italics*, indentation, parentheses, or be visually set apart (reflecting original distinctions like color or boxing).**
    - "enonce": The main content of the exercise **itself** (e.g., questions, sentences to complete, list items). This follows `consignes` and any `exemple` or `conseil`. **Crucially, ensure that text identified as `exemple` or `conseil` is *excluded* from the `enonce`.**
    - **"conseil": Helpful hints, tips, or guidance (optional). Identify text offering advice. Look for visual/textual cues:
        - **Position:** Can appear anywhere relative to the `consignes`, `exemple`, or `enonce`, but is distinct from them.
        - **Keywords:** May start with indicators like "Conseil:", "Astuce:", "Attention:", "N.B.:", "Rappel:", etc.
        - **Formatting:** May use distinct formatting such as *italics*, indentation, parentheses, or be visually set apart.**
    - "references": Source or citation (optional).
    - "autre": Other relevant information (optional).

4. Preserve the original format and layout as in the input document.
5. Group multiple instructions ("consignes") under the same `"numero"` if they belong to the same exercise.
6. Return only the JSON content without any formatting markers.
7. Do not wrap the response in <think> tags—provide the JSON directly.
8. Do not solve the exercises please, you should only extract them as-is.
9. Maintain list structures exactly as they appear.
10. Do not separate words or phrases unnecessarily.
11. Respect list ordering.
12. Return a list of exercises in strict JSON format. Use only double quotes for keys and values.
13. An image of the page is attached that contains exercise boxes—structure the content based on the visual layout.
14. In the image, the 'consigne' is typically bold. Use **all available visual and textual cues** to distinguish between `consignes`, `exemple`, `conseil`, and `enonce`. Pay close attention to:
    - **Formatting:** Bolding (often `consignes`), *italics* (often `exemple` or `conseil`), indentation, parentheses.
    - **Positioning:** Especially text located between `consignes` and list-based `enonce` (often `exemple`).
    - **Keywords:** Explicit labels like "Exemple:", "Conseil:", "Attention:", etc.
    **Assume that elements like examples and advice might have had distinct visual treatments (like color or boxing) in the source, and look for corresponding textual cues (italics, indentation, keywords) to identify them.**
15. Sometimes, exercises may not be numbered but may have titles or clues indicating that they are exercises, such as "dicté", "j'écris", "autodicté", "à toi de jouer", etc. These should be included as exercises as well.
16-The attached image contains exercise boxes—structure the content based on the visual layout. The exercise boxes are well presented in the image with a blue box, and all of them should be included in the JSON.
"""


with open("generated/default-extraction-prompt.md", "w") as f:
    f.write(extraction_prompt)


def extract(image: PIL.Image.Image) -> list[Exercise]:
    contents: list[google.genai.types.ContentUnion] = [extraction_prompt, image]
    response = client.models.generate_content(model="gemini-2.0-flash", contents=contents).text
    assert response is not None

    cleaned_response = response.strip()
    if cleaned_response.startswith("```json"):
        cleaned_response = cleaned_response.replace("```json", "").strip()
    if cleaned_response.endswith("```"):
        cleaned_response = cleaned_response[:-3].strip()

    return pydantic.RootModel[list[Exercise]](json.loads(cleaned_response)).root


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
        exercises = extract(pdf_page_as_image(self.pdf_data, 2))
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
