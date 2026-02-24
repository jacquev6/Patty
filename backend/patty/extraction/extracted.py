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

import typing
import pydantic


class Base(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="ignore")


# Legacy
class ExerciseV1(Base):
    id: str | None = None
    numero: str | None = None
    consignes: list[str] = []
    conseil: str | None = None
    exemple: str | None = None
    enonce: str | None = None
    references: str | None = None
    autre: str | None = None


# Starting with #92
class ExerciseV2(Base):
    id: str | None = None
    type: typing.Literal["exercice"] = "exercice"
    images: bool = False
    type_images: typing.Literal["none", "unique", "ordered", "unordered", "composite"] = "none"

    class Properties(Base):
        numero: str | None = None
        consignes: list[str] = []
        enonce: str | None = None
        conseil: str | None = None
        exemple: str | None = None
        references: str | None = None
        autre: str | None = None

    properties: Properties = Properties()


ExercisesV2List = pydantic.RootModel[list[ExerciseV2]]


# Starting with #176
class ExerciseV3(Base):
    id: str | None = None
    type: typing.Literal["exercise"] = "exercise"
    images: bool = False
    image_type: typing.Literal["none", "single", "ordered", "unordered", "composite"] = "none"

    class Properties(Base):
        number: str | None = None
        instruction: str | None = None
        labels: list[str] = []
        statement: str | None = None
        hint: str | None = None
        example: str | None = None
        references: str | None = None

    properties: Properties = Properties()


ExercisesV3List = pydantic.RootModel[list[ExerciseV3]]
