from __future__ import annotations

from typing import Any, Iterable, Literal
import typing

import pydantic

from .api_utils import ApiModel


class BaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="ignore", json_schema_extra=lambda schema: schema.pop("title"))


class Exercise(BaseModel):
    # WARNING: keep 'make_exercise_type' below consistent with this class
    format: Literal["v1"]
    instruction: InstructionPage
    statement: StatementPages
    reference: ReferenceLine | None


class Pages[Component](BaseModel):
    # WARNING: keep 'make_pages_type' below consistent with this class
    pages: list[Page[Component]]


class Page[Component](BaseModel):
    # WARNING: keep 'make_page_type' below consistent with this class
    lines: list[Line[Component]]


class Line[Component](BaseModel):
    # WARNING: keep 'make_line_type' below consistent with this class
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


# WARNING: keep 'PureText' and 'PureTextComponents' consistent
PureText = Text | Whitespace


class PureTextComponents(ApiModel):
    text: Literal[True]
    whitespace: Literal[True]

    def gather(self) -> Iterable[type]:
        yield Text
        yield Whitespace


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


# WANRING: keep 'InstructionComponent' and 'InstructionComponents' consistent
InstructionComponent = PureText | Choice


class InstructionComponents(PureTextComponents):
    choice: bool

    def gather(self) -> Iterable[type]:
        yield from super().gather()
        if self.choice:
            yield Choice


# WARNING: keep 'StatementComponent' and 'StatementComponents' consistent
StatementComponent = PureText | Arrow | FreeTextInput | MultipleChoicesInput | SelectableInput


class StatementComponents(PureTextComponents):
    arrow: bool
    free_text_input: bool
    multiple_choices_input: bool
    selectable_input: bool

    def gather(self) -> Iterable[type]:
        yield from super().gather()
        if self.arrow:
            yield Arrow
        if self.free_text_input:
            yield FreeTextInput
        if self.multiple_choices_input:
            yield MultipleChoicesInput
        if self.selectable_input:
            yield SelectableInput


# WARNING: keep 'ReferenceComponent' and 'ReferenceComponents' consistent
ReferenceComponent = PureText


class ReferenceComponents(PureTextComponents):
    pass


InstructionLine = Line[InstructionComponent]
StatementLine = Line[StatementComponent]
ReferenceLine = Line[ReferenceComponent]

InstructionPage = Page[InstructionComponent]
StatementPage = Page[StatementComponent]

StatementPages = Pages[StatementComponent]


def make_exercise_type(
    instruction_components: InstructionComponents,
    statement_components: StatementComponents,
    reference_components: ReferenceComponents,
) -> type[Exercise]:
    # WARNING: typing dynamic types is a nightmare, so THIS FUNCTION IS MOSTLY UNTYPED
    # and relies on a final cast of its return value.

    def make_line_type(name: str, contents_type: Any) -> Any:
        contents = (list[contents_type], pydantic.Field())
        return pydantic.create_model(f"{name}Line", __base__=BaseModel, contents=contents)

    def make_page_type(name: str, contents_type: Any) -> Any:
        line_type: Any = make_line_type(name, contents_type)
        lines = (list[line_type], pydantic.Field())
        return pydantic.create_model(f"{name}Page", __base__=BaseModel, lines=lines)

    def make_pages_type(name: str, contents_type: Any) -> Any:
        page_type: Any = make_page_type(name, contents_type)
        pages = (list[page_type], pydantic.Field())
        return pydantic.create_model(f"{name}Pages", __base__=BaseModel, pages=pages)

    instruction_page_type = make_page_type("Instruction", typing.Union[tuple(instruction_components.gather())])
    statement_pages_type = make_pages_type("Statement", typing.Union[tuple(statement_components.gather())])
    reference_line_type = make_line_type("Reference", typing.Union[tuple(reference_components.gather())])

    return typing.cast(
        type[Exercise],
        pydantic.create_model(
            "Exercise",
            __base__=BaseModel,
            format=(Literal["v1"], pydantic.Field()),
            instruction=(instruction_page_type, pydantic.Field()),
            statement=(statement_pages_type, pydantic.Field()),
            reference=(reference_line_type | None, pydantic.Field()),
        ),
    )
