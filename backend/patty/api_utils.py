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

from sqlalchemy import orm
import fastapi
import pydantic.alias_generators
import sqlalchemy as sql

from . import database_utils


class ApiModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        alias_generator=pydantic.alias_generators.to_camel, populate_by_name=True, extra="forbid"
    )


Model = typing.TypeVar("Model", bound=database_utils.OrmBase)


def get_by_id(session: database_utils.Session, model: type[Model], id: str) -> Model:
    try:
        numerical_id = int(id)
    except ValueError:
        raise fastapi.HTTPException(status_code=404, detail=f"{model.__name__} not found")
    instance = session.get(model, numerical_id)
    if instance is None:
        raise fastapi.HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return instance


class HasIntId(typing.Protocol):
    id: typing.ClassVar[orm.Mapped[int]]


T = typing.TypeVar("T", bound=HasIntId)


def paginate(
    model: type[T], session: database_utils.SessionDependable, chunk_id: str | None
) -> tuple[list[T], str | None]:
    chunk_size = 20
    request = sql.select(model).order_by(-model.id).limit(chunk_size + 1)

    if chunk_id is not None:
        try:
            numerical_chunk_id = int(chunk_id)
        except ValueError:
            raise fastapi.HTTPException(status_code=400, detail="Invalid chunk ID")
        request = request.filter(model.id < numerical_chunk_id)

    instances = list(session.execute(request).scalars().all())

    if len(instances) <= chunk_size:
        next_chunk_id = None
    else:
        next_chunk_id = str(typing.cast(HasIntId, instances[-2]).id)

    return instances[:chunk_size], next_chunk_id


T1 = typing.TypeVar("T1")


def assert_isinstance(value: typing.Any, type_: type[T1]) -> T1:
    assert isinstance(value, type_)
    return value
