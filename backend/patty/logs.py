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

import contextlib
import datetime
import time
import typing

# @todo Use standard `logging` module

from .api_utils import ApiModel


class TimingData(ApiModel):
    start: float
    end: float | None

    @property
    def elapsed(self) -> float | None:
        if self.end is None:
            return None
        return self.end - self.start


@contextlib.contextmanager
def timer() -> typing.Generator[TimingData, None, None]:
    t = TimingData(start=time.time(), end=None)
    try:
        yield t
    finally:
        t.end = time.time()


def log(message: str) -> None:
    print(datetime.datetime.now(), message, flush=True)
