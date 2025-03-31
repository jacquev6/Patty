from typing import Iterable
import textwrap

import compact_json  # type: ignore

from . import database_utils
from . import llm
from . import orm_models
from . import adaptation


def make_default_system_prompt() -> str:
    # Be very careful to KEEP THESE TWO VERSIONS of the exercise IN SYNC.

    text_exercise = textwrap.dedent(
        """\
        2 Complète avec "l'herbe" ou "les chats"
        a. Les vaches mangent ...
        b. Les chiens courent après ..."""
    )

    exercise = adaptation.AdaptedExercise(
        format="v1",
        instructions=adaptation.Page[adaptation.PassiveComponent](
            lines=[
                adaptation.Line[adaptation.PassiveComponent](
                    contents=[
                        adaptation.Text(kind="text", text="Complète"),
                        adaptation.Whitespace(kind="whitespace"),
                        adaptation.Text(kind="text", text="avec"),
                        adaptation.Whitespace(kind="whitespace"),
                        adaptation.PassiveSequence(
                            kind="sequence",
                            contents=[
                                adaptation.Text(kind="text", text="l'"),
                                adaptation.Text(kind="text", text="herbe"),
                            ],
                            bold=False,
                            italic=False,
                            highlighted=None,
                            boxed=True,
                            vertical=False,
                        ),
                        adaptation.Whitespace(kind="whitespace"),
                        adaptation.Text(kind="text", text="ou"),
                        adaptation.Whitespace(kind="whitespace"),
                        adaptation.PassiveSequence(
                            kind="sequence",
                            contents=[
                                adaptation.Text(kind="text", text="les"),
                                adaptation.Whitespace(kind="whitespace"),
                                adaptation.Text(kind="text", text="chats"),
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
        wording=adaptation.Pages[adaptation.AnyComponent](
            pages=[
                adaptation.Page[adaptation.AnyComponent](
                    lines=[
                        adaptation.Line[adaptation.AnyComponent](
                            contents=[
                                adaptation.Text(kind="text", text="a"),
                                adaptation.Text(kind="text", text="."),
                                adaptation.Whitespace(kind="whitespace"),
                                adaptation.Text(kind="text", text="Les"),
                                adaptation.Whitespace(kind="whitespace"),
                                adaptation.Text(kind="text", text="vaches"),
                                adaptation.Whitespace(kind="whitespace"),
                                adaptation.Text(kind="text", text="mangent"),
                                adaptation.Whitespace(kind="whitespace"),
                                adaptation.MultipleChoicesInput(
                                    kind="multipleChoicesInput",
                                    choices=[
                                        adaptation.Line[adaptation.PassiveComponent](
                                            contents=[
                                                adaptation.Text(kind="text", text="l'"),
                                                adaptation.Text(kind="text", text="herbe"),
                                            ]
                                        ),
                                        adaptation.Line[adaptation.PassiveComponent](
                                            contents=[
                                                adaptation.Text(kind="text", text="les"),
                                                adaptation.Whitespace(kind="whitespace"),
                                                adaptation.Text(kind="text", text="chats"),
                                            ]
                                        ),
                                    ],
                                    showChoicesByDefault=False,
                                ),
                            ]
                        ),
                        adaptation.Line[adaptation.AnyComponent](
                            contents=[
                                adaptation.Text(kind="text", text="b"),
                                adaptation.Text(kind="text", text="."),
                                adaptation.Whitespace(kind="whitespace"),
                                adaptation.Text(kind="text", text="Les"),
                                adaptation.Whitespace(kind="whitespace"),
                                adaptation.Text(kind="text", text="chiens"),
                                adaptation.Whitespace(kind="whitespace"),
                                adaptation.Text(kind="text", text="courent"),
                                adaptation.Whitespace(kind="whitespace"),
                                adaptation.Text(kind="text", text="après"),
                                adaptation.Whitespace(kind="whitespace"),
                                adaptation.MultipleChoicesInput(
                                    kind="multipleChoicesInput",
                                    choices=[
                                        adaptation.Line[adaptation.PassiveComponent](
                                            contents=[
                                                adaptation.Text(kind="text", text="l'"),
                                                adaptation.Text(kind="text", text="herbe"),
                                            ]
                                        ),
                                        adaptation.Line[adaptation.PassiveComponent](
                                            contents=[
                                                adaptation.Text(kind="text", text="les"),
                                                adaptation.Whitespace(kind="whitespace"),
                                                adaptation.Text(kind="text", text="chats"),
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
            {textwrap.indent(text_exercise, "            ").lstrip()}
            ```

            Alors une adaptation possible est :

            ```
            {textwrap.indent(json_exercise, "            ").lstrip()}
            ```
            """
    )


def create_default_adaptation_strategy(session: database_utils.Session) -> None:
    session.add(
        orm_models.AdaptationStrategy(
            model=llm.OpenAiModel(name="gpt-4o-2024-08-06"), system_prompt=make_default_system_prompt()
        )
    )


available_fixtures = {"default-adaptation-strategy": create_default_adaptation_strategy}


def load(session: database_utils.Session, fixtures: Iterable[str]) -> None:
    database_utils.truncate_all_tables(session)
    for fixture in fixtures:
        available_fixtures[fixture](session)
