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

from .adapted import Exercise
from ..api_utils import ApiModel


class Success(ApiModel):
    kind: Literal["success"]
    exercise: Exercise


class InvalidJsonError(ApiModel):
    kind: Literal["error"]
    error: Literal["invalid-json"]
    parsed: Any


class NotJsonError(ApiModel):
    kind: Literal["error"]
    error: Literal["not-json"]
    text: str


class UnknownError(ApiModel):
    kind: Literal["error"]
    error: Literal["unknown"]


Response = Success | InvalidJsonError | NotJsonError | UnknownError


def validate(obj: Any) -> Response:
    return pydantic.RootModel[Response].model_validate(obj).root


class Adjustment(ApiModel):
    user_prompt: str
    assistant_response: Response
