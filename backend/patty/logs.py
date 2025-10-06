import contextlib
import dataclasses
import datetime
import time
import typing

# @todo Use standard `logging` module

from . import settings


@dataclasses.dataclass
class _Timer:
    start: float
    end: float | None

    @property
    def elapsed(self) -> float:
        if self.end is None:
            raise RuntimeError("Timer has not been stopped yet")
        return self.end - self.start


@contextlib.contextmanager
def timer() -> typing.Generator[_Timer, None, None]:
    t = _Timer(start=time.perf_counter(), end=None)
    try:
        yield t
    finally:
        t.end = time.perf_counter()


def log(message: str) -> None:
    print(datetime.datetime.now(), message, flush=True)


def log_for_issue_129(message: str) -> None:
    if settings.INVESTIGATING_ISSUE_129:
        log(message)
