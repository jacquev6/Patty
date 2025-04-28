from typing import Iterable
import datetime
import textwrap

import compact_json  # type: ignore
import fastapi

from . import adaptation
from . import adapted
from . import database_utils
from . import llm
from . import settings


def make_default_system_prompt() -> str:
    # Be very careful to KEEP THESE TWO VERSIONS of the exercise IN SYNC.

    text_exercise = textwrap.dedent(
        """\
        Complète avec "l'herbe" ou "les chats"
        a. Les vaches mangent ...
        b. Les chiens courent après ..."""
    )

    exercise = adapted.Exercise(
        format="v1",
        instruction=adapted.InstructionPage(
            lines=[
                adapted.InstructionLine(
                    contents=[
                        adapted.Text(kind="text", text="Complète"),
                        adapted.Whitespace(kind="whitespace"),
                        adapted.Text(kind="text", text="avec"),
                        adapted.Whitespace(kind="whitespace"),
                        adapted.Choice(
                            kind="choice",
                            contents=[adapted.Text(kind="text", text="l'"), adapted.Text(kind="text", text="herbe")],
                        ),
                        adapted.Whitespace(kind="whitespace"),
                        adapted.Text(kind="text", text="ou"),
                        adapted.Whitespace(kind="whitespace"),
                        adapted.Choice(
                            kind="choice",
                            contents=[
                                adapted.Text(kind="text", text="les"),
                                adapted.Whitespace(kind="whitespace"),
                                adapted.Text(kind="text", text="chats"),
                            ],
                        ),
                    ]
                )
            ]
        ),
        example=None,
        hint=None,
        statement=adapted.StatementPages(
            pages=[
                adapted.StatementPage(
                    lines=[
                        adapted.StatementLine(
                            contents=[
                                adapted.Text(kind="text", text="a"),
                                adapted.Text(kind="text", text="."),
                                adapted.Whitespace(kind="whitespace"),
                                adapted.Text(kind="text", text="Les"),
                                adapted.Whitespace(kind="whitespace"),
                                adapted.Text(kind="text", text="vaches"),
                                adapted.Whitespace(kind="whitespace"),
                                adapted.Text(kind="text", text="mangent"),
                                adapted.Whitespace(kind="whitespace"),
                                adapted.MultipleChoicesInput(
                                    kind="multipleChoicesInput",
                                    choices=[
                                        adapted.PureTextContainer(
                                            contents=[
                                                adapted.Text(kind="text", text="l'"),
                                                adapted.Text(kind="text", text="herbe"),
                                            ]
                                        ),
                                        adapted.PureTextContainer(
                                            contents=[
                                                adapted.Text(kind="text", text="les"),
                                                adapted.Whitespace(kind="whitespace"),
                                                adapted.Text(kind="text", text="chats"),
                                            ]
                                        ),
                                    ],
                                    showChoicesByDefault=False,
                                ),
                            ]
                        ),
                        adapted.StatementLine(
                            contents=[
                                adapted.Text(kind="text", text="b"),
                                adapted.Text(kind="text", text="."),
                                adapted.Whitespace(kind="whitespace"),
                                adapted.Text(kind="text", text="Les"),
                                adapted.Whitespace(kind="whitespace"),
                                adapted.Text(kind="text", text="chiens"),
                                adapted.Whitespace(kind="whitespace"),
                                adapted.Text(kind="text", text="courent"),
                                adapted.Whitespace(kind="whitespace"),
                                adapted.Text(kind="text", text="après"),
                                adapted.Whitespace(kind="whitespace"),
                                adapted.MultipleChoicesInput(
                                    kind="multipleChoicesInput",
                                    choices=[
                                        adapted.PureTextContainer(
                                            contents=[
                                                adapted.Text(kind="text", text="l'"),
                                                adapted.Text(kind="text", text="herbe"),
                                            ]
                                        ),
                                        adapted.PureTextContainer(
                                            contents=[
                                                adapted.Text(kind="text", text="les"),
                                                adapted.Whitespace(kind="whitespace"),
                                                adapted.Text(kind="text", text="chats"),
                                            ]
                                        ),
                                    ],
                                    showChoicesByDefault=False,
                                ),
                            ]
                        ),
                    ]
                )
            ]
        ),
        reference=None,
    )

    formatter = compact_json.Formatter()
    formatter.ensure_ascii = False
    formatter.indent_spaces = 2
    formatter.max_inline_complexity = 1
    formatter.table_dict_minimum_similarity = 101
    json_exercise = "\n".join(line.rstrip() for line in formatter.serialize(exercise.model_dump()).splitlines())

    return textwrap.dedent(
        f"""\
        Le premier message de l'utilisateur sera un exercice scolaire.
        Ta mission est de fournir une "adaptation" de cet exercice.
        Tu ne dois jamais résoudre les exercices, seulement les adapter.

        Dans ses messages suivants, l'utilisateur te demandera de faire des ajustements à ta réponse.
        A chaque ajustement, tu dois répondre avec la nouvelle adaptation de l'exercice initial,
        en respectant les consignes de ce messages système et les ajustements demandés par l'utilisateur.

        Dans le format JSON pour tes réponses, il y a un champs `instruction` pour la consigne de l'exercice, et un champs `statement` pour l'énoncé de l'exercice.
        Il y a aussi un champs `reference` pour les références de l'exercice, qui peut être null si l'exercice n'a pas de références.

        Voici un exemple. Si l'exercice initial est :

        ```
        {textwrap.indent(text_exercise, "        ").lstrip()}
        ```

        Alors une adaptation possible est :

        ```
        {textwrap.indent(json_exercise, "        ").lstrip()}
        ```
        """
    )


def create_default_adaptation_strategy() -> Iterable[object]:
    yield adaptation.Strategy(
        created_by="Patty",
        model=llm.OpenAiModel(name="gpt-4o-2024-08-06"),
        system_prompt=make_default_system_prompt(),
        response_specification=adaptation.strategy.JsonSchemaLlmResponseSpecification(
            format="json",
            formalism="json-schema",
            instruction_components=adapted.InstructionComponents(
                text=True, whitespace=True, arrow=True, formatted=True, choice=True
            ),
            example_components=adapted.ExampleComponents(text=True, whitespace=True, arrow=True, formatted=True),
            hint_components=adapted.HintComponents(text=True, whitespace=True, arrow=True, formatted=True),
            statement_components=adapted.StatementComponents(
                text=True,
                whitespace=True,
                arrow=True,
                formatted=True,
                free_text_input=False,
                multiple_choices_input=True,
                selectable_input=False,
                swappable_input=False,
            ),
            reference_components=adapted.ReferenceComponents(text=True, whitespace=True, arrow=True, formatted=True),
        ),
    )


def create_dummy_adaptation_strategy() -> Iterable[object]:
    yield adaptation.Strategy(
        created_by="Patty",
        model=llm.DummyModel(name="dummy-1"),
        system_prompt="Blah blah blah.",
        response_specification=adaptation.strategy.JsonSchemaLlmResponseSpecification(
            format="json",
            formalism="json-schema",
            instruction_components=adapted.InstructionComponents(
                text=True, whitespace=True, arrow=True, formatted=True, choice=True
            ),
            example_components=adapted.ExampleComponents(text=True, whitespace=True, arrow=True, formatted=True),
            hint_components=adapted.HintComponents(text=True, whitespace=True, arrow=True, formatted=True),
            statement_components=adapted.StatementComponents(
                text=True,
                whitespace=True,
                arrow=True,
                formatted=True,
                free_text_input=True,
                multiple_choices_input=True,
                selectable_input=True,
                swappable_input=True,
            ),
            reference_components=adapted.ReferenceComponents(text=True, whitespace=True, arrow=True, formatted=True),
        ),
    )


def create_default_adaptation_input() -> Iterable[object]:
    yield adaptation.Input(
        created_by="Patty",
        page_number=42,
        exercise_number="5",
        text=textwrap.dedent(
            """\
            Complète avec "le vent" ou "la pluie"
            a. Les feuilles sont chahutées par ...
            b. Les vitres sont mouillées par ...
            """
        ),
    )


def make_successful_adaptation(*, batch: object, strategy: object, input: object) -> object:
    return adaptation.Adaptation(
        created_by="Patty",
        batch=batch,
        strategy=strategy,
        input=input,
        raw_llm_conversations=[{"initial": "conversation"}],
        _initial_assistant_response=adaptation.AssistantSuccess(
            kind="success",
            exercise=adapted.Exercise(
                **{  # type: ignore[arg-type]
                    "format": "v1",
                    "instruction": {
                        "lines": [
                            {
                                "contents": [
                                    {"kind": "text", "text": "Complète"},
                                    {"kind": "whitespace"},
                                    {"kind": "text", "text": "avec"},
                                    {"kind": "whitespace"},
                                    {
                                        "kind": "choice",
                                        "contents": [
                                            {"kind": "text", "text": "le"},
                                            {"kind": "whitespace"},
                                            {"kind": "text", "text": "vent"},
                                        ],
                                    },
                                    {"kind": "whitespace"},
                                    {"kind": "text", "text": "ou"},
                                    {"kind": "whitespace"},
                                    {
                                        "kind": "choice",
                                        "contents": [
                                            {"kind": "text", "text": "la"},
                                            {"kind": "whitespace"},
                                            {"kind": "text", "text": "pluie"},
                                        ],
                                    },
                                ]
                            }
                        ]
                    },
                    "example": None,
                    "hint": None,
                    "statement": {
                        "pages": [
                            {
                                "lines": [
                                    {
                                        "contents": [
                                            {"kind": "text", "text": "a"},
                                            {"kind": "text", "text": "."},
                                            {"kind": "whitespace"},
                                            {"kind": "text", "text": "Les"},
                                            {"kind": "whitespace"},
                                            {"kind": "text", "text": "feuilles"},
                                            {"kind": "whitespace"},
                                            {"kind": "text", "text": "sont"},
                                            {"kind": "whitespace"},
                                            {"kind": "text", "text": "chahutées"},
                                            {"kind": "whitespace"},
                                            {"kind": "text", "text": "par"},
                                            {"kind": "whitespace"},
                                            {
                                                "kind": "multipleChoicesInput",
                                                "choices": [
                                                    {
                                                        "contents": [
                                                            {"kind": "text", "text": "le"},
                                                            {"kind": "whitespace"},
                                                            {"kind": "text", "text": "vent"},
                                                        ]
                                                    },
                                                    {
                                                        "contents": [
                                                            {"kind": "text", "text": "la"},
                                                            {"kind": "whitespace"},
                                                            {"kind": "text", "text": "pluie"},
                                                        ]
                                                    },
                                                ],
                                                "showChoicesByDefault": False,
                                            },
                                        ]
                                    },
                                    {
                                        "contents": [
                                            {"kind": "text", "text": "b"},
                                            {"kind": "text", "text": "."},
                                            {"kind": "whitespace"},
                                            {"kind": "text", "text": "Les"},
                                            {"kind": "whitespace"},
                                            {"kind": "text", "text": "vitres"},
                                            {"kind": "whitespace"},
                                            {"kind": "text", "text": "sont"},
                                            {"kind": "whitespace"},
                                            {"kind": "text", "text": "mouillées"},
                                            {"kind": "whitespace"},
                                            {"kind": "text", "text": "par"},
                                            {"kind": "whitespace"},
                                            {
                                                "kind": "multipleChoicesInput",
                                                "choices": [
                                                    {
                                                        "contents": [
                                                            {"kind": "text", "text": "le"},
                                                            {"kind": "whitespace"},
                                                            {"kind": "text", "text": "vent"},
                                                        ]
                                                    },
                                                    {
                                                        "contents": [
                                                            {"kind": "text", "text": "la"},
                                                            {"kind": "whitespace"},
                                                            {"kind": "text", "text": "pluie"},
                                                        ]
                                                    },
                                                ],
                                                "showChoicesByDefault": False,
                                            },
                                        ]
                                    },
                                ]
                            }
                        ]
                    },
                    "reference": None,
                }
            ),
        ).model_dump(),
        _adjustments=[],
        manual_edit=None,
    )


def make_in_progress_adaptation(*, batch: object, strategy: object, input: object) -> object:
    return adaptation.Adaptation(
        created_by="Patty",
        batch=batch,
        strategy=strategy,
        input=input,
        raw_llm_conversations=[{"initial": "conversation"}],
        _initial_assistant_response=None,
        _adjustments=[],
        manual_edit=None,
    )


def make_invalid_json_adaptation(*, batch: object, strategy: object, input: object) -> object:
    return adaptation.Adaptation(
        created_by="Patty",
        batch=batch,
        strategy=strategy,
        input=input,
        raw_llm_conversations=[{"initial": "conversation"}],
        _initial_assistant_response=adaptation.AssistantInvalidJsonError(
            kind="error", error="invalid-json", parsed={}
        ).model_dump(),
        _adjustments=[],
        manual_edit=None,
    )


def make_not_json_adaptation(*, batch: object, strategy: object, input: object) -> object:
    return adaptation.Adaptation(
        created_by="Patty",
        batch=batch,
        strategy=strategy,
        input=input,
        raw_llm_conversations=[{"initial": "conversation"}],
        _initial_assistant_response=adaptation.AssistantNotJsonError(
            kind="error", error="not-json", text="This is not JSON."
        ).model_dump(),
        _adjustments=[],
        manual_edit=None,
    )


def create_seed_data() -> Iterable[object]:
    [strategy] = create_default_adaptation_strategy()
    yield strategy
    [input] = create_default_adaptation_input()
    yield input
    batch = adaptation.Batch(
        created_by="Patty",
        created_at=datetime.datetime(2000, 1, 1, 0, 0, 0, 0, datetime.timezone.utc),
        strategy=strategy,
    )
    yield batch
    yield make_successful_adaptation(batch=batch, strategy=strategy, input=input)


def create_dummy_adaptation() -> Iterable[object]:
    [strategy] = create_dummy_adaptation_strategy()
    yield strategy
    [input] = create_default_adaptation_input()
    yield input
    batch = adaptation.Batch(
        created_by="Patty",
        created_at=datetime.datetime(2000, 1, 1, 0, 0, 0, 0, datetime.timezone.utc),
        strategy=strategy,
    )
    yield batch
    yield make_successful_adaptation(batch=batch, strategy=strategy, input=input)


def create_mixed_dummy_batch() -> Iterable[object]:
    [strategy] = create_dummy_adaptation_strategy()
    yield strategy
    [input] = create_default_adaptation_input()
    yield input
    batch = adaptation.Batch(
        created_by="Patty",
        created_at=datetime.datetime(2000, 1, 1, 0, 0, 0, 0, datetime.timezone.utc),
        strategy=strategy,
    )
    yield batch
    yield make_successful_adaptation(batch=batch, strategy=strategy, input=input)
    yield make_in_progress_adaptation(batch=batch, strategy=strategy, input=input)
    yield make_invalid_json_adaptation(batch=batch, strategy=strategy, input=input)
    yield make_not_json_adaptation(batch=batch, strategy=strategy, input=input)


available_fixtures = {
    "-".join(f.__name__.split("_")[1:]): f
    for f in (
        create_default_adaptation_input,
        create_default_adaptation_strategy,
        create_dummy_adaptation_strategy,
        create_dummy_adaptation,
        create_mixed_dummy_batch,
        create_seed_data,
    )
}


def load(session: database_utils.Session, fixtures: Iterable[str]) -> None:
    database_utils.truncate_all_tables(session)
    for fixture in fixtures:
        for instance in available_fixtures[fixture]():
            session.add(instance)


app = fastapi.FastAPI(database_engine=database_utils.create_engine(settings.DATABASE_URL))


@app.post("/load")
def post_load(fixtures: str, session: database_utils.SessionDependable) -> None:
    print(available_fixtures)
    load(session, fixtures.split(","))
