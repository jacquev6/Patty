from __future__ import annotations

from typing import Any, Iterable, Literal
import typing

import pydantic

from ..api_utils import ApiModel


# patty_json_to_html.py begin


class BaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="ignore", json_schema_extra=lambda schema: schema.pop("title"))


class Exercise(BaseModel):
    # WARNING: keep 'make_exercise_type' below consistent with this class
    format: Literal["v1"]
    instruction: InstructionPage
    example: ExamplePage | None
    hint: HintPage | None
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


class Formatted(BaseModel):
    kind: Literal["formatted"]
    contents: list[FormattedText]
    bold: bool = False
    italic: bool = False
    underlined: bool = False
    highlighted: str | None = None
    boxed: bool = False
    superscript: bool = False
    subscript: bool = False


class ActiveFormatted(BaseModel):
    kind: Literal["formatted"]
    contents: list[ActiveFormattedText]
    bold: bool = False
    italic: bool = False
    underlined: bool = False
    highlighted: str | None = None
    boxed: bool = False
    superscript: bool = False
    subscript: bool = False


class Arrow(BaseModel):
    kind: Literal["arrow"]


class Choice(BaseModel):
    kind: Literal["choice"]
    contents: list[FormattedText]


PlainText = Text | Whitespace

# WARNING: keep 'FormattedText' and 'FormattedTextComponents' consistent
FormattedText = PlainText | Arrow | Formatted


class FreeTextInput(BaseModel):
    kind: Literal["freeTextInput"]


# WARNING: keep 'ActiveFormattedText' and 'ActiveFormattedTextComponents' consistent
ActiveFormattedText = PlainText | Arrow | ActiveFormatted | FreeTextInput


class FormattedTextContainer(BaseModel):
    contents: list[FormattedText]


class MultipleChoicesInput(BaseModel):
    kind: Literal["multipleChoicesInput"]
    choices: list[FormattedTextContainer]
    showChoicesByDefault: bool


class SelectableInput(BaseModel):
    kind: Literal["selectableInput"]
    contents: list[FormattedText | SelectableInput]
    colors: list[str]
    boxed: bool


class SwappableInput(BaseModel):
    kind: Literal["swappableInput"]
    contents: list[FormattedText]


class EditableTextInput(BaseModel):
    kind: Literal["editableTextInput"]
    showOriginalText: bool
    contents: list[PlainText]
    increaseHorizontalSpace: bool = False


# WARNING: keep 'InstructionComponent' and 'InstructionComponents' consistent
InstructionComponent = FormattedText | Choice


# WARNING: keep 'ExampleComponent' and 'ExampleComponents' consistent
ExampleComponent = FormattedText


# WARNING: keep 'HintComponent' and 'HintComponents' consistent
HintComponent = FormattedText


# WARNING: keep 'StatementComponent' and 'StatementComponents' consistent
StatementComponent = ActiveFormattedText | MultipleChoicesInput | SelectableInput | SwappableInput | EditableTextInput


# WARNING: keep 'ReferenceComponent' and 'ReferenceComponents' consistent
ReferenceComponent = FormattedText


InstructionLine = Line[InstructionComponent]
ExampleLine = Line[ExampleComponent]
HintLine = Line[HintComponent]
StatementLine = Line[StatementComponent]
ReferenceLine = Line[ReferenceComponent]

InstructionPage = Page[InstructionComponent]
ExamplePage = Page[ExampleComponent]
HintPage = Page[HintComponent]
StatementPage = Page[StatementComponent]

StatementPages = Pages[StatementComponent]

# patty_json_to_html.py end


class FormattedTextComponents(ApiModel):
    text: Literal[True]
    whitespace: Literal[True]
    arrow: Literal[True]
    formatted: Literal[True]

    def gather(self) -> Iterable[type]:
        yield Text
        yield Whitespace
        yield Arrow
        yield Formatted


class ActiveFormattedTextComponents(ApiModel):
    text: Literal[True]
    whitespace: Literal[True]
    arrow: Literal[True]
    formatted: Literal[True]
    free_text_input: bool

    def gather(self) -> Iterable[type]:
        yield Text
        yield Whitespace
        yield Arrow
        if self.free_text_input:
            yield ActiveFormatted
            yield FreeTextInput
        else:
            yield Formatted


class InstructionComponents(FormattedTextComponents):
    choice: bool

    def gather(self) -> Iterable[type]:
        yield from super().gather()
        if self.choice:
            yield Choice


class ExampleComponents(FormattedTextComponents):
    pass


class HintComponents(FormattedTextComponents):
    pass


class StatementComponents(ActiveFormattedTextComponents):
    multiple_choices_input: bool
    selectable_input: bool
    swappable_input: bool
    editable_text_input: bool

    def gather(self) -> Iterable[type]:
        yield from super().gather()
        if self.multiple_choices_input:
            yield MultipleChoicesInput
        if self.selectable_input:
            yield SelectableInput
        if self.swappable_input:
            yield SwappableInput
        if self.editable_text_input:
            yield EditableTextInput


class ReferenceComponents(FormattedTextComponents):
    pass


def make_exercise_type(
    instruction_components: InstructionComponents,
    example_components: ExampleComponents,
    hint_components: HintComponents,
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
    example_page_type = make_page_type("Example", typing.Union[tuple(example_components.gather())])
    hint_page_type = make_page_type("Hint", typing.Union[tuple(hint_components.gather())])
    statement_pages_type = make_pages_type("Statement", typing.Union[tuple(statement_components.gather())])
    reference_line_type = make_line_type("Reference", typing.Union[tuple(reference_components.gather())])

    return typing.cast(
        type[Exercise],
        pydantic.create_model(
            "Exercise",
            __base__=BaseModel,
            format=(Literal["v1"], pydantic.Field()),
            instruction=(instruction_page_type, pydantic.Field()),
            example=(example_page_type | None, pydantic.Field()),
            hint=(hint_page_type | None, pydantic.Field()),
            statement=(statement_pages_type, pydantic.Field()),
            reference=(reference_line_type | None, pydantic.Field()),
        ),
    )
