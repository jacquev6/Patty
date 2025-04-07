from __future__ import annotations

from typing import Literal

import pydantic


class BaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid", json_schema_extra=lambda schema: schema.pop("title"))


class Exercise(BaseModel):
    format: Literal["v1"]
    instruction: Page[PassiveComponent]
    statement: Pages[AnyComponent]
    references: Line[PassiveComponent] | None


class Pages[Component](BaseModel):
    pages: list[Page[Component]]


class Page[Component](BaseModel):
    lines: list[Line[Component]]


class Line[Component](BaseModel):
    contents: list[Component]


class Text(BaseModel):
    kind: Literal["text"]
    text: str


class Whitespace(BaseModel):
    kind: Literal["whitespace"]


class Arrow(BaseModel):
    kind: Literal["arrow"]


class Choice(BaseModel):
    kind: Literal["choice"]
    contents: list[Text | Whitespace]


PassiveAtomicComponent = Text | Whitespace | Arrow | Choice
PassiveComponent = PassiveAtomicComponent


class FreeTextInput(BaseModel):
    kind: Literal["freeTextInput"]


class MultipleChoicesInput(BaseModel):
    kind: Literal["multipleChoicesInput"]
    choices: list[Line[Text | Whitespace]]
    showChoicesByDefault: bool


class SelectableInput(BaseModel):
    kind: Literal["selectableInput"]
    contents: list[Text | Whitespace]
    colors: list[str]
    boxed: bool


AnyComponent = PassiveAtomicComponent | FreeTextInput | MultipleChoicesInput | SelectableInput
