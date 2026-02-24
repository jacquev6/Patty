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

from typing import Any, Literal

import pydantic

from .extracted import ExerciseV1, ExerciseV2, ExerciseV3
from ..api_utils import ApiModel


# Legacy
class SuccessV1(ApiModel):
    kind: Literal["success"]
    version: Literal["v1"]
    exercises: list[ExerciseV1]


# Starting with #92
class SuccessV2(ApiModel):
    kind: Literal["success"]
    version: Literal["v2"]
    exercises: list[ExerciseV2]


# Starting with #176
class SuccessV3(ApiModel):
    kind: Literal["success"]
    version: Literal["v3"]
    raw_response: str
    cleaned_response: str
    exercises: list[ExerciseV3]


class InvalidJsonErrorV2(ApiModel):
    kind: Literal["error"]
    error: Literal["invalid-json"]
    version: Literal["v2"]
    parsed: Any


class InvalidJsonErrorV3(ApiModel):
    kind: Literal["error"]
    error: Literal["invalid-json"]
    version: Literal["v3"]
    raw_response: str
    cleaned_response: str
    parsed: Any


class NotJsonErrorV2(ApiModel):
    kind: Literal["error"]
    error: Literal["not-json"]
    version: Literal["v2"]
    text: str


class NotJsonErrorV3(ApiModel):
    kind: Literal["error"]
    error: Literal["not-json"]
    version: Literal["v3"]
    raw_response: str
    cleaned_response: str


class UnknownError(ApiModel):
    kind: Literal["error"]
    error: Literal["unknown"]


Success = SuccessV1 | SuccessV2 | SuccessV3

InvalidJsonError = InvalidJsonErrorV2 | InvalidJsonErrorV3

NotJsonError = NotJsonErrorV2 | NotJsonErrorV3

Response = Success | InvalidJsonError | NotJsonError | UnknownError


def validate(obj: Any) -> Response:
    return pydantic.RootModel[Response].model_validate(obj).root
