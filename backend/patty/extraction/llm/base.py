# MALIN Platform https://malin.cahiersfantastiques.fr/
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

import abc
import json
import typing

import PIL.Image
import pydantic
import json_repair

from .. import extracted


class LlmException(RuntimeError):
    pass


class InvalidJsonLlmException(LlmException):
    def __init__(self, raw_response: str, cleaned_response: str, parsed: typing.Any) -> None:
        super().__init__("Failed to validate JSON response")
        self.raw_response = raw_response
        self.cleaned_response = cleaned_response
        self.parsed = parsed


class NotJsonLlmException(LlmException):
    def __init__(self, raw_response: str, cleaned_response: str) -> None:
        super().__init__("Failed to parse JSON response")
        self.raw_response = raw_response
        self.cleaned_response = cleaned_response


class Model(abc.ABC, pydantic.BaseModel):
    def extract_v2(self, prompt: str, image: PIL.Image.Image) -> list[extracted.ExerciseV2]:
        return self._extract(extracted.ExercisesV2List, prompt, image, lambda s: s, json.loads)[2]

    def extract_v3(
        self, prompt: str, image: PIL.Image.Image, pre_cleanup: typing.Callable[[str], str]
    ) -> tuple[str, str, list[extracted.ExerciseV3]]:
        return self._extract(extracted.ExercisesV3List, prompt, image, pre_cleanup, json_repair.loads)

    def _extract[T](
        self,
        t: type[pydantic.RootModel[T]],
        prompt: str,
        image: PIL.Image.Image,
        pre_cleanup: typing.Callable[[str], str],
        json_loads: typing.Callable[[str], typing.Any],
    ) -> tuple[str, str, T]:
        raw_response = self.do_extract(prompt, image)

        cleaned_response = raw_response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:].strip()
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:].strip()
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3].strip()
        cleaned_response = pre_cleanup(cleaned_response)

        try:
            parsed = json_loads(cleaned_response)
            if parsed == "":
                raise NotJsonLlmException(raw_response=raw_response, cleaned_response=cleaned_response)
        except json.JSONDecodeError:
            raise NotJsonLlmException(raw_response=raw_response, cleaned_response=cleaned_response)

        try:
            validated = t.model_validate(parsed).root
            return raw_response, cleaned_response, validated
        except pydantic.ValidationError:
            raise InvalidJsonLlmException(raw_response=raw_response, cleaned_response=cleaned_response, parsed=parsed)

    @abc.abstractmethod
    def do_extract(self, prompt: str, image: PIL.Image.Image) -> str: ...
