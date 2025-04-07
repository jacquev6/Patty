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


class Choice(pydantic.BaseModel):
    kind: Literal["choice"]
    contents: list[Text | Whitespace]


PassiveAtomicComponent = Text | Whitespace | Arrow | Choice
PassiveComponent = PassiveAtomicComponent


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


AnyComponent = PassiveAtomicComponent | FreeTextInput | MultipleChoicesInput | SelectableInput
