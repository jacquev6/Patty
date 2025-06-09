import io
import subprocess
import unittest

import PIL.Image


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
