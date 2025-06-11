from typing import Literal
import os
import unittest

import google.genai.types
import PIL.Image

from .base import Model
from ...test_utils import costs_money


client = google.genai.Client(api_key=os.environ["GEMINIAI_KEY"])


class GeminiModel(Model):
    provider: Literal["gemini"] = "gemini"
    name: Literal["gemini-2.0-flash"]

    def do_extract(self, prompt: str, image: PIL.Image.Image) -> str:
        contents: list[google.genai.types.ContentUnion] = [prompt, image]
        response = client.models.generate_content(model=self.name, contents=contents).text
        assert response is not None
        return response


class GeminiModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        with open("../frontend/e2e-tests/inputs/test.pdf", "rb") as f:
            self.pdf_data = f.read()

    @costs_money
    def test_extract(self) -> None:
        from ...fixtures import make_default_extraction_prompt
        from ..submission import pdf_page_as_image

        exercises = GeminiModel(name="gemini-2.0-flash").extract(
            make_default_extraction_prompt(), pdf_page_as_image(self.pdf_data, 2)
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
