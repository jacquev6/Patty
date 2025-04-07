from __future__ import annotations

from typing import Literal, TypeVar

import pydantic


class Exercise(pydantic.BaseModel):
    format: Literal["v1"]
    instruction: Page[PassiveComponent]
    statement: Pages[AnyComponent]
    references: Line[PassiveComponent] | None


Component = TypeVar("Component")


class Pages[Component](pydantic.BaseModel):
    pages: list[Page[Component]]


class Page[Component](pydantic.BaseModel):
    lines: list[Line[Component]]


class Line[Component](pydantic.BaseModel):
    contents: list[Component]


class Text(pydantic.BaseModel):
    kind: Literal["text"]
    text: str


class Whitespace(pydantic.BaseModel):
    kind: Literal["whitespace"]


class Arrow(pydantic.BaseModel):
    kind: Literal["arrow"]


# @todo Find a way to define a generic Sequence[Component] type. Currently this breaks the polyfactory used in llm.dummy.
# In the mean time, keep PassiveSequence and AnySequence consistent.
class PassiveSequence(pydantic.BaseModel):
    kind: Literal["sequence"]
    contents: list[PassiveComponent]
    bold: bool
    italic: bool
    highlighted: str | None
    boxed: bool


PassiveAtomicComponent = Text | Whitespace | Arrow
PassiveComponent = PassiveAtomicComponent | PassiveSequence


class FreeTextInput(pydantic.BaseModel):
    kind: Literal["freeTextInput"]


class MultipleChoicesInput(pydantic.BaseModel):
    kind: Literal["multipleChoicesInput"]
    choices: list[Line[PassiveComponent]]
    showChoicesByDefault: bool


class SelectableInput(pydantic.BaseModel):
    kind: Literal["selectableInput"]
    contents: list[PassiveComponent]
    colors: list[str]
    boxed: bool


# Keep AnySequence and PassiveSequence consistent.
class AnySequence(pydantic.BaseModel):
    kind: Literal["sequence"]
    contents: list[AnyComponent]
    bold: bool
    italic: bool
    highlighted: str | None
    boxed: bool


AnyComponent = PassiveAtomicComponent | FreeTextInput | MultipleChoicesInput | SelectableInput | AnySequence
