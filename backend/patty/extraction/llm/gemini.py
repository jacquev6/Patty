from typing import Literal
import unittest

import google.genai.types
import PIL.Image

from ... import settings
from ...test_utils import costs_money
from .base import Model


client = google.genai.Client(api_key=settings.GEMINIAI_KEY)


class GeminiModel(Model):
    provider: Literal["gemini"]
    name: Literal["gemini-2.0-flash", "gemini-2.5-flash"]

    def do_extract(self, prompt: str, image: PIL.Image.Image) -> str:
        contents: list[google.genai.types.ContentUnion] = [prompt, image]
        response = client.models.generate_content(model=self.name, contents=contents).text
        assert response is not None
        return response


class GeminiModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        with open("../frontend/e2e-tests/inputs/test.pdf", "rb") as f:
            self.pdf_data = f.read()

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
        ("p7_ex5", "p7_ex6", "p7_ex7", "p7_ex8", "p7_ex9", "p7_ex10", "p7_ex11", "p7_ex12", "p7_ex13", "p7_ex14"),
        (
            "p007_ex5",
            "p007_ex6",
            "p007_ex7",
            "p007_ex8",
            "p007_ex_defi_langue",
            "p007_ex9",
            "p007_ex10",
            "p007_ex11",
            "p007_ex12",
            "p007_ex13",
            "p007_ex14",
        ),
        (
            "p07_ex5",
            "p07_ex6",
            "p07_ex7",
            "p07_ex8",
            "p07_ex_defi_langue",
            "p07_ex9",
            "p07_ex10",
            "p07_ex11",
            "p07_ex12",
            "p07_ex13",
            "p07_ex14",
        ),
        (
            "p007_ex5",
            "p007_ex6",
            "p007_ex7",
            "p007_ex8",
            "p007_ex9",
            "p007_ex10",
            "p007_ex11",
            "p007_ex12",
            "p007_ex13",
            "p007_ex14",
        ),
        (
            "p007_ex5",
            "p007_ex6",
            "p007_ex7",
            "p007_ex8",
            "p007_defi_langue",
            "p007_ex9",
            "p007_ex10",
            "p007_ex11",
            "p007_ex12",
            "p007_ex13",
            "p007_ex14",
        ),
        (
            "p7_ex5",
            "p7_ex6",
            "p7_ex7",
            "p7_ex8",
            "p7_defilangue",
            "p7_ex9",
            "p7_ex10",
            "p7_ex11",
            "p7_ex12",
            "p7_ex13",
            "p7_ex14",
        ),
    ]

    @costs_money
    def test_extract_2_0_flash(self) -> None:
        from ...fixtures import make_default_extraction_prompt
        from ..submission import pdf_page_as_image

        exercises = GeminiModel(provider="gemini", name="gemini-2.0-flash").extract_v2(
            make_default_extraction_prompt(), pdf_page_as_image(self.pdf_data, 2)
        )
        actual_ids = tuple(exercise.id for exercise in exercises)
        self.assertIn(actual_ids, self.possible_expected_ids)

    @costs_money
    def test_extract_2_5_flash(self) -> None:
        from ...fixtures import make_default_extraction_prompt
        from ..submission import pdf_page_as_image

        exercises = GeminiModel(provider="gemini", name="gemini-2.5-flash").extract_v2(
            make_default_extraction_prompt(), pdf_page_as_image(self.pdf_data, 2)
        )
        actual_ids = tuple(exercise.id for exercise in exercises)
        self.assertIn(actual_ids, self.possible_expected_ids)
