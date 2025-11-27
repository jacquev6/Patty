import abc
import json
import typing

import PIL.Image
import pydantic

from .. import extracted


class LlmException(RuntimeError):
    pass


class InvalidJsonLlmException(LlmException):
    def __init__(self, parsed: typing.Any) -> None:
        super().__init__("Failed to validate JSON response")
        self.parsed = parsed


class NotJsonLlmException(LlmException):
    def __init__(self, text: str) -> None:
        super().__init__("Failed to parse JSON response")
        self.text = text


class Model(abc.ABC, pydantic.BaseModel):
    def extract_v2(self, prompt: str, image: PIL.Image.Image) -> list[extracted.ExerciseV2]:
        parsed = self._extract(prompt, image)

        try:
            return extracted.ExercisesV2List(parsed).root
        except pydantic.ValidationError:
            raise InvalidJsonLlmException(parsed=parsed)

    def extract_v3(self, prompt: str, image: PIL.Image.Image) -> list[extracted.ExerciseV3]:
        parsed = self._extract(prompt, image)

        try:
            return extracted.ExercisesV3List(parsed).root
        except pydantic.ValidationError:
            raise InvalidJsonLlmException(parsed=parsed)

    def _extract(self, prompt: str, image: PIL.Image.Image) -> typing.Any:
        response = self.do_extract(prompt, image)

        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response.replace("```json", "").strip()
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3].strip()

        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            raise NotJsonLlmException(text=response)

    @abc.abstractmethod
    def do_extract(self, prompt: str, image: PIL.Image.Image) -> str: ...
