from typing import Iterable
import textwrap

import compact_json  # type: ignore

from . import adaptation
from . import adapted
from . import database_utils
from . import llm


def make_default_system_prompt() -> str:
    # Be very careful to KEEP THESE TWO VERSIONS of the exercise IN SYNC.

    text_exercise = textwrap.dedent(
        """\
        2 Complète avec "l'herbe" ou "les chats"
        a. Les vaches mangent ...
        b. Les chiens courent après ..."""
    )

    exercise = adapted.Exercise(
        format="v1",
        instructions=adapted.Page[adapted.PassiveComponent](
            lines=[
                adapted.Line[adapted.PassiveComponent](
                    contents=[
                        adapted.Text(kind="text", text="Complète"),
                        adapted.Whitespace(kind="whitespace"),
                        adapted.Text(kind="text", text="avec"),
                        adapted.Whitespace(kind="whitespace"),
                        adapted.PassiveSequence(
                            kind="sequence",
                            contents=[adapted.Text(kind="text", text="l'"), adapted.Text(kind="text", text="herbe")],
                            bold=False,
                            italic=False,
                            highlighted=None,
                            boxed=True,
                            vertical=False,
                        ),
                        adapted.Whitespace(kind="whitespace"),
                        adapted.Text(kind="text", text="ou"),
                        adapted.Whitespace(kind="whitespace"),
                        adapted.PassiveSequence(
                            kind="sequence",
                            contents=[
                                adapted.Text(kind="text", text="les"),
                                adapted.Whitespace(kind="whitespace"),
                                adapted.Text(kind="text", text="chats"),
                            ],
                            bold=False,
                            italic=False,
                            highlighted=None,
                            boxed=True,
                            vertical=False,
                        ),
                    ]
                )
            ]
        ),
        wording=adapted.Pages[adapted.AnyComponent](
            pages=[
                adapted.Page[adapted.AnyComponent](
                    lines=[
                        adapted.Line[adapted.AnyComponent](
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
                                        adapted.Line[adapted.PassiveComponent](
                                            contents=[
                                                adapted.Text(kind="text", text="l'"),
                                                adapted.Text(kind="text", text="herbe"),
                                            ]
                                        ),
                                        adapted.Line[adapted.PassiveComponent](
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
                        adapted.Line[adapted.AnyComponent](
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
                                        adapted.Line[adapted.PassiveComponent](
                                            contents=[
                                                adapted.Text(kind="text", text="l'"),
                                                adapted.Text(kind="text", text="herbe"),
                                            ]
                                        ),
                                        adapted.Line[adapted.PassiveComponent](
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
        references=None,
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

        Le format pour tes réponses comporte deux champs: `prose` et `structured`.
        Tu dois utiliser `prose` pour interagir avec l'utilisateur.
        Tu dois utiliser `structured` pour renvoyer l'adaptation de l'exercice initial, après les ajustements demandés par l'utilisateur.
        Tu peux laisser le champ `structured` null si le message de l'utilisateur ne demande pas de changement à l'adaptation.

        Dans le champs `structured`, il y a un champs `instructions` pour la consigne de l'exercice, et un champs `wording` pour l'énoncé de l'exercice.
        Il y a aussi un champs `references` pour les références de l'exercice, qui peut être null si l'exercice n'a pas de références.

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
        model=llm.OpenAiModel(name="gpt-4o-2024-08-06"), system_prompt=make_default_system_prompt()
    )


def create_dummy_adaptation_strategy() -> Iterable[object]:
    yield adaptation.Strategy(model=llm.DummyModel(name="dummy-1"), system_prompt="Blah blah blah.")


def create_default_adaptation_input() -> Iterable[object]:
    yield adaptation.Input(
        text=textwrap.dedent(
            """\
            5 Complète avec "le vent" ou "la pluie"
            a. Les feuilles sont chahutées par ...
            b. Les vitres sont mouillées par ...
            """
        )
    )


def create_actual_openai_adaptation() -> Iterable[object]:
    [strategy] = create_default_adaptation_strategy()
    yield strategy
    [input] = create_default_adaptation_input()
    yield input
    yield adaptation.Adaptation(
        strategy=strategy,
        input=input,
        _initial_response={
            "prose": "Je vais te proposer une version adapt\u00e9e de ton exercice initial.",
            "structured": {
                "format": "v1",
                "instructions": {
                    "lines": [
                        {
                            "contents": [
                                {"kind": "text", "text": "Compl\u00e8te"},
                                {"kind": "whitespace"},
                                {"kind": "text", "text": "avec"},
                                {"kind": "whitespace"},
                                {
                                    "kind": "sequence",
                                    "contents": [
                                        {"kind": "text", "text": "le"},
                                        {"kind": "whitespace"},
                                        {"kind": "text", "text": "vent"},
                                    ],
                                    "bold": False,
                                    "italic": False,
                                    "highlighted": None,
                                    "boxed": True,
                                    "vertical": False,
                                },
                                {"kind": "whitespace"},
                                {"kind": "text", "text": "ou"},
                                {"kind": "whitespace"},
                                {
                                    "kind": "sequence",
                                    "contents": [
                                        {"kind": "text", "text": "la"},
                                        {"kind": "whitespace"},
                                        {"kind": "text", "text": "pluie"},
                                    ],
                                    "bold": False,
                                    "italic": False,
                                    "highlighted": None,
                                    "boxed": True,
                                    "vertical": False,
                                },
                            ]
                        }
                    ]
                },
                "wording": {
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
                                        {"kind": "text", "text": "chahut\u00e9es"},
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
                                        {"kind": "text", "text": "mouill\u00e9es"},
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
                "references": None,
            },
        },
        _adjustments=[
            {
                "user_prompt": "Merci!",
                "assistant_response": {
                    "prose": "Avec plaisir! N'h\u00e9site pas si tu as besoin d'autres adaptations ou ajustements.",
                    "structured": None,
                },
            }
        ],
        manual_edit=None,
    )


available_fixtures = {
    "default-adaptation-strategy": create_default_adaptation_strategy,
    "dummy-adaptation-strategy": create_dummy_adaptation_strategy,
    "default-adaptation-input": create_default_adaptation_input,
    "actual-openai-adaptation": create_actual_openai_adaptation,
}


def load(session: database_utils.Session, fixtures: Iterable[str]) -> None:
    database_utils.truncate_all_tables(session)
    for fixture in fixtures:
        for instance in available_fixtures[fixture]():
            session.add(instance)
