# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

import contextlib
import datetime
import time
import typing

# @todo Use standard `logging` module

from . import settings
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


def log_for_issue_129(message: str) -> None:
    if settings.INVESTIGATING_ISSUE_129:
        log(message)
