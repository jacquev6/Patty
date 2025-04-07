from __future__ import annotations

from typing import Literal

import pydantic


class BaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid", json_schema_extra=lambda schema: schema.pop("title"))


class Exercise(BaseModel):
    format: Literal["v1"]
    instruction: InstructionPage
    statement: StatementPages
    references: ReferenceLine | None


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
    contents: list[PureText]


PureText = Text | Whitespace


class FreeTextInput(BaseModel):
    kind: Literal["freeTextInput"]


class PureTextContainer(BaseModel):
    contents: list[PureText]


class MultipleChoicesInput(BaseModel):
    kind: Literal["multipleChoicesInput"]
    choices: list[PureTextContainer]
    showChoicesByDefault: bool


class SelectableInput(BaseModel):
    kind: Literal["selectableInput"]
    contents: list[PureText]
    colors: list[str]
    boxed: bool


InstructionComponent = PureText | Choice
StatementComponent = PureText | Arrow | FreeTextInput | MultipleChoicesInput | SelectableInput
ReferenceComponent = PureText


InstructionLine = Line[InstructionComponent]
StatementLine = Line[StatementComponent]
ReferenceLine = Line[ReferenceComponent]

InstructionPage = Page[InstructionComponent]
StatementPage = Page[StatementComponent]

StatementPages = Pages[StatementComponent]
