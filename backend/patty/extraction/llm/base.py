import abc
import json
import typing

import PIL.Image
import pydantic

from ... import extracted


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
    def extract(self, prompt: str, image: PIL.Image.Image) -> list[extracted.Exercise]:
        response = self.do_extract(prompt, image)

        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response.replace("```json", "").strip()
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3].strip()

        try:
            parsed = json.loads(cleaned_response)
        except json.JSONDecodeError:
            raise NotJsonLlmException(text=response)

        try:
            return extracted.ExercisesList(parsed).root
        except pydantic.ValidationError:
            raise InvalidJsonLlmException(parsed=parsed)

    @abc.abstractmethod
    def do_extract(self, prompt: str, image: PIL.Image.Image) -> str: ...
