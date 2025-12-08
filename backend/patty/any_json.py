# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

from typing import Any


# These are not really type-safe, but act as documentation

JsonDict = dict[str, Any]

JsonList = list[Any]

JsonType = str | int | float | bool | None | JsonDict | JsonList
