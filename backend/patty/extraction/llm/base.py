import abc
import json

import PIL.Image
import pydantic

from ... import extracted


class Model(abc.ABC, pydantic.BaseModel):
    def extract(self, prompt: str, image: PIL.Image.Image) -> list[extracted.Exercise]:
        response = self.do_extract(prompt, image)

        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response.replace("```json", "").strip()
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3].strip()

        return pydantic.RootModel[list[extracted.Exercise]](json.loads(cleaned_response)).root

    @abc.abstractmethod
    def do_extract(self, prompt: str, image: PIL.Image.Image) -> str: ...
