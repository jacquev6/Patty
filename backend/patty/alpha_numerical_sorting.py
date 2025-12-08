# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

import random
import typing
import unittest


# To the best of my current knowledge, the sorting key defined here implements a sort order that
# cannot be achieved using a PostgreSQL (15-17) collation.
# The "compare sequences of digits as numbers" part requires using a collation with a locale with "kn-true",
# and the "put letters before digits" part requires using a locale with rules, but using rules disables "kn-true".


Key = list[tuple[typing.Literal["b"], int] | tuple[typing.Literal["a"], str]]


def key(s: str) -> Key:
    current_number: str | None = None
    parts: Key = []
    for c in s:
        if c.isdigit():
            if current_number is None:
                current_number = c
            else:
                current_number += c
        else:
            if current_number is not None:
                parts.append(("b", int(current_number)))
                current_number = None
            parts.append(("a", c))
    if current_number is not None:
        parts.append(("b", int(current_number)))
    return parts


class SortingTestCase(unittest.TestCase):
    def assert_is_sorted(self, items: list[str]) -> None:
        self.assertEqual(sorted(random.sample(items, len(items)), key=key), items)

    def test_letters(self) -> None:
        self.assert_is_sorted(["a", "b", "c", "d", "e"])

    def test_numbers(self) -> None:
        self.assert_is_sorted(["1", "2", "10", "20", "100"])

    def test_prefixed_numbers(self) -> None:
        self.assert_is_sorted(["a1", "a2", "a10", "a20", "a100"])

    def test_mixed(self) -> None:
        self.assert_is_sorted(
            ["a", "b", "c", "ca", "cz", "c0", "c1", "c2", "c10", "c20", "c100", "d", "e", "1", "2", "10", "20", "100"]
        )
