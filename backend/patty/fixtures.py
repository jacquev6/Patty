from typing import Any, Iterable, TypeVar
import datetime
import textwrap

import compact_json  # type: ignore[import-untyped]
import fastapi
import sqlalchemy.orm

from . import adapted
from . import database_utils
from . import llm
from . import orm_models as db
from . import settings
from .adaptation import adaptation
from .adaptation import strategy as adaptation_strategy


created_at = datetime.datetime(2000, 1, 1, 0, 0, 0, 0, datetime.timezone.utc)


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
                                        adapted.FormattedTextContainer(
                                            contents=[
                                                adapted.Text(kind="text", text="l'"),
                                                adapted.Text(kind="text", text="herbe"),
                                            ]
                                        ),
                                        adapted.FormattedTextContainer(
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
                                        adapted.FormattedTextContainer(
                                            contents=[
                                                adapted.Text(kind="text", text="l'"),
                                                adapted.Text(kind="text", text="herbe"),
                                            ]
                                        ),
                                        adapted.FormattedTextContainer(
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


class FixturesCreator:
    def __init__(self, session: database_utils.Session) -> None:
        self.__session = session

    Model = TypeVar("Model", bound=sqlalchemy.orm.DeclarativeBase)

    def create(self, __model: type[Model], **kwargs: Any) -> Model:
        instance = __model(**kwargs)
        self.__session.add(instance)
        self.__session.flush()
        return instance

    def create_default_adaptation_strategy(self) -> db.AdaptationStrategy:
        strategy_settings = self.create(
            db.AdaptationStrategySettings,
            created_by_username="Patty",
            created_at=created_at,
            system_prompt=make_default_system_prompt(),
            response_specification=adaptation_strategy.JsonSchemaLlmResponseSpecification(
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
                    editable_text_input=False,
                ),
                reference_components=adapted.ReferenceComponents(
                    text=True, whitespace=True, arrow=True, formatted=True
                ),
            ),
            exercise_class=None,
            parent=None,
        )
        return self.create(
            db.AdaptationStrategy,
            created_by_username="Patty",
            created_at=created_at,
            model=llm.OpenAiModel(name="gpt-4o-2024-08-06"),
            settings=strategy_settings,
        )

    def create_dummy_adaptation_strategy_settings(
        self, system_prompt: str = "Blah blah blah."
    ) -> db.AdaptationStrategySettings:
        return self.create(
            db.AdaptationStrategySettings,
            created_by_username="Patty",
            created_at=created_at,
            system_prompt=system_prompt,
            response_specification=adaptation_strategy.JsonSchemaLlmResponseSpecification(
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
                    editable_text_input=True,
                ),
                reference_components=adapted.ReferenceComponents(
                    text=True, whitespace=True, arrow=True, formatted=True
                ),
            ),
            exercise_class=None,
            parent=None,
        )

    def create_dummy_adaptation_strategy(self) -> db.AdaptationStrategy:
        settings = self.create_dummy_adaptation_strategy_settings()
        return self.create(
            db.AdaptationStrategy,
            created_by_username="Patty",
            created_at=created_at,
            model=llm.DummyModel(name="dummy-1"),
            settings=settings,
        )

    def create_default_adaptation_input(self) -> db.AdaptableExercise:
        return self.create(
            db.AdaptableExercise,
            created_by_username="Patty",
            created_at=created_at,
            page_number=42,
            exercise_number="5",
            textbook=None,
            removed_from_textbook=False,
            full_text=textwrap.dedent(
                """\
                Complète avec "le vent" ou "la pluie"
                a. Les feuilles sont chahutées par ...
                b. Les vitres sont mouillées par ...
                """
            ),
            instruction_hint_example_text=None,
            statement_text=None,
            classified_at=None,
            classified_by_classification_batch=None,
            classified_by_username=None,
            exercise_class=None,
        )

    def create_successful_adaptation(
        self,
        *,
        adaptation_batch: db.AdaptationBatch | None,
        strategy: db.AdaptationStrategy,
        exercise: db.AdaptableExercise,
    ) -> db.Adaptation:
        return self.create(
            db.Adaptation,
            created_by_username="Patty",
            created_at=created_at,
            adaptation_batch=adaptation_batch,
            classification_batch=None,
            strategy=strategy,
            exercise=exercise,
            raw_llm_conversations=[{"initial": "conversation"}],
            initial_assistant_response=adaptation.AssistantSuccess(
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
            ),
            adjustments=[],
            manual_edit=None,
        )

    def create_in_progress_adaptation(
        self,
        *,
        adaptation_batch: db.AdaptationBatch | None,
        strategy: db.AdaptationStrategy,
        exercise: db.AdaptableExercise,
    ) -> db.Adaptation:
        return self.create(
            db.Adaptation,
            created_by_username="Patty",
            created_at=created_at,
            adaptation_batch=adaptation_batch,
            classification_batch=None,
            strategy=strategy,
            exercise=exercise,
            raw_llm_conversations=[{"initial": "conversation"}],
            # Hack: store a JSON null in _initial_assistant_response instead of a SQL NULL to avoid
            # being picked up by the submission daemon, but still pass as in-progress in the tests.
            _initial_assistant_response=None,
            adjustments=[],
            manual_edit=None,
        )

    def create_invalid_json_adaptation(
        self,
        *,
        adaptation_batch: db.AdaptationBatch | None,
        strategy: db.AdaptationStrategy,
        exercise: db.AdaptableExercise,
    ) -> db.Adaptation:
        return self.create(
            db.Adaptation,
            created_by_username="Patty",
            created_at=created_at,
            adaptation_batch=adaptation_batch,
            classification_batch=None,
            strategy=strategy,
            exercise=exercise,
            raw_llm_conversations=[{"initial": "conversation"}],
            initial_assistant_response=adaptation.AssistantInvalidJsonError(
                kind="error", error="invalid-json", parsed={}
            ),
            adjustments=[],
            manual_edit=None,
        )

    def create_not_json_adaptation(
        self,
        *,
        adaptation_batch: db.AdaptationBatch | None,
        strategy: db.AdaptationStrategy,
        exercise: db.AdaptableExercise,
    ) -> db.Adaptation:
        return self.create(
            db.Adaptation,
            created_by_username="Patty",
            created_at=created_at,
            adaptation_batch=adaptation_batch,
            classification_batch=None,
            strategy=strategy,
            exercise=exercise,
            raw_llm_conversations=[{"initial": "conversation"}],
            initial_assistant_response=adaptation.AssistantNotJsonError(
                kind="error", error="not-json", text="This is not JSON."
            ),
            adjustments=[],
            manual_edit=None,
        )

    def create_seed_data(self) -> None:
        strategy = self.create_default_adaptation_strategy()
        batch = self.create(
            db.AdaptationBatch,
            created_by_username="Patty",
            created_at=created_at,
            textbook=None,
            removed_from_textbook=False,
            strategy=strategy,
        )
        self.create_successful_adaptation(
            adaptation_batch=batch, strategy=strategy, exercise=self.create_default_adaptation_input()
        )

    def create_dummy_adaptation(self) -> None:
        strategy = self.create_dummy_adaptation_strategy()
        batch = self.create(
            db.AdaptationBatch,
            created_by_username="Patty",
            created_at=created_at,
            textbook=None,
            removed_from_textbook=False,
            strategy=strategy,
        )
        self.create_successful_adaptation(
            adaptation_batch=batch, strategy=strategy, exercise=self.create_default_adaptation_input()
        )

    def create_mixed_dummy_adaptation_batch(self) -> None:
        strategy = self.create_dummy_adaptation_strategy()
        batch = self.create(
            db.AdaptationBatch,
            created_by_username="Patty",
            created_at=created_at,
            textbook=None,
            removed_from_textbook=False,
            strategy=strategy,
        )
        self.create_successful_adaptation(
            adaptation_batch=batch, strategy=strategy, exercise=self.create_default_adaptation_input()
        )
        self.create_in_progress_adaptation(
            adaptation_batch=batch, strategy=strategy, exercise=self.create_default_adaptation_input()
        )
        self.create_invalid_json_adaptation(
            adaptation_batch=batch, strategy=strategy, exercise=self.create_default_adaptation_input()
        )
        self.create_not_json_adaptation(
            adaptation_batch=batch, strategy=strategy, exercise=self.create_default_adaptation_input()
        )

    def create_dummy_branch(
        self, *, name: str = "Branchy McBranchFace", system_prompt: str = "Blah blah blah."
    ) -> db.ExerciseClass:
        settings = self.create_dummy_adaptation_strategy_settings(system_prompt=system_prompt)
        exercise_class = self.create(
            db.ExerciseClass,
            created_by_username="Patty",
            created_at=created_at,
            name=name,
            latest_strategy_settings=settings,
        )
        settings.exercise_class = exercise_class
        return exercise_class

    def create_dummy_textbook(self) -> None:
        textbook = self.create(
            db.Textbook, created_by_username="Patty", created_at=created_at, title="Dummy Textbook Title"
        )

        success_branch_1 = self.create_dummy_branch(name="Branch with successes 1", system_prompt="Thou shall succeed.")
        success_strategy_1 = self.create(
            db.AdaptationStrategy,
            created_by_username="Patty",
            created_at=created_at,
            model=llm.DummyModel(name="dummy-1"),
            settings=success_branch_1.latest_strategy_settings,
        )
        success_adaptation_batch_1 = self.create(
            db.AdaptationBatch,
            created_by_username="Patty",
            created_at=created_at,
            strategy=success_strategy_1,
            textbook=textbook,
            removed_from_textbook=False,
        )
        self.create_successful_adaptation(
            adaptation_batch=success_adaptation_batch_1,
            strategy=success_strategy_1,
            exercise=self.create(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_at=created_at,
                page_number=42,
                exercise_number="5",
                textbook=textbook,
                removed_from_textbook=False,
                full_text=textwrap.dedent(
                    """\
                    Complète avec "le vent" ou "la pluie"
                    a. Les feuilles sont chahutées par ...
                    b. Les vitres sont mouillées par ...
                    """
                ),
                instruction_hint_example_text=None,
                statement_text=None,
                classified_at=None,
                classified_by_classification_batch=None,
                classified_by_username=None,
                exercise_class=None,
            ),
        )
        self.create_successful_adaptation(
            adaptation_batch=success_adaptation_batch_1,
            strategy=success_strategy_1,
            exercise=self.create(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_at=created_at,
                page_number=40,
                exercise_number="6",
                textbook=textbook,
                removed_from_textbook=False,
                full_text=textwrap.dedent(
                    """\
                    Complète avec "le vent" ou "la pluie"
                    a. Les feuilles sont chahutées par ...
                    b. Les vitres sont mouillées par ...
                    """
                ),
                instruction_hint_example_text=None,
                statement_text=None,
                classified_at=None,
                classified_by_classification_batch=None,
                classified_by_username=None,
                exercise_class=None,
            ),
        )
        self.create_successful_adaptation(
            adaptation_batch=success_adaptation_batch_1,
            strategy=success_strategy_1,
            exercise=self.create(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_at=created_at,
                page_number=40,
                exercise_number="4",
                textbook=textbook,
                removed_from_textbook=False,
                full_text=textwrap.dedent(
                    """\
                    Complète avec "le vent" ou "la pluie"
                    a. Les feuilles sont chahutées par ...
                    b. Les vitres sont mouillées par ...
                    """
                ),
                instruction_hint_example_text=None,
                statement_text=None,
                classified_at=None,
                classified_by_classification_batch=None,
                classified_by_username=None,
                exercise_class=None,
            ),
        )

        success_branch_2 = self.create_dummy_branch(
            name="Branch with successes 2", system_prompt="Thou shall succeed as well."
        )
        success_strategy_2 = self.create(
            db.AdaptationStrategy,
            created_by_username="Patty",
            created_at=created_at,
            model=llm.DummyModel(name="dummy-1"),
            settings=success_branch_2.latest_strategy_settings,
        )
        success_adaptation_batch_2 = self.create(
            db.AdaptationBatch,
            created_by_username="Patty",
            created_at=created_at,
            strategy=success_strategy_2,
            textbook=textbook,
            removed_from_textbook=False,
        )
        self.create_successful_adaptation(
            adaptation_batch=success_adaptation_batch_2,
            strategy=success_strategy_2,
            exercise=self.create(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_at=created_at,
                page_number=42,
                exercise_number="6",
                textbook=textbook,
                removed_from_textbook=False,
                full_text=textwrap.dedent(
                    """\
                    Complète avec "le vent" ou "la pluie"
                    a. Les feuilles sont chahutées par ...
                    b. Les vitres sont mouillées par ...
                    """
                ),
                instruction_hint_example_text=None,
                statement_text=None,
                classified_at=None,
                classified_by_classification_batch=None,
                classified_by_username=None,
                exercise_class=None,
            ),
        )
        self.create_successful_adaptation(
            adaptation_batch=success_adaptation_batch_2,
            strategy=success_strategy_2,
            exercise=self.create(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_at=created_at,
                page_number=40,
                exercise_number="30",
                textbook=textbook,
                removed_from_textbook=False,
                full_text=textwrap.dedent(
                    """\
                    Complète avec "le vent" ou "la pluie"
                    a. Les feuilles sont chahutées par ...
                    b. Les vitres sont mouillées par ...
                    """
                ),
                instruction_hint_example_text=None,
                statement_text=None,
                classified_at=None,
                classified_by_classification_batch=None,
                classified_by_username=None,
                exercise_class=None,
            ),
        )
        self.create_successful_adaptation(
            adaptation_batch=success_adaptation_batch_2,
            strategy=success_strategy_2,
            exercise=self.create(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_at=created_at,
                page_number=40,
                exercise_number="8",
                textbook=textbook,
                removed_from_textbook=False,
                full_text=textwrap.dedent(
                    """\
                    Complète avec "le vent" ou "la pluie"
                    a. Les feuilles sont chahutées par ...
                    b. Les vitres sont mouillées par ...
                    """
                ),
                instruction_hint_example_text=None,
                statement_text=None,
                classified_at=None,
                classified_by_classification_batch=None,
                classified_by_username=None,
                exercise_class=None,
            ),
        )
        self.create_successful_adaptation(
            adaptation_batch=success_adaptation_batch_2,
            strategy=success_strategy_2,
            exercise=self.create(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_at=created_at,
                page_number=40,
                exercise_number="Removed",
                textbook=textbook,
                removed_from_textbook=True,
                full_text=textwrap.dedent(
                    """\
                    Complète avec "le vent" ou "la pluie"
                    a. Les feuilles sont chahutées par ...
                    b. Les vitres sont mouillées par ...
                    """
                ),
                instruction_hint_example_text=None,
                statement_text=None,
                classified_at=None,
                classified_by_classification_batch=None,
                classified_by_username=None,
                exercise_class=None,
            ),
        )

        removed_adaptation_batch = self.create(
            db.AdaptationBatch,
            created_by_username="Patty",
            created_at=created_at,
            strategy=success_strategy_2,
            textbook=textbook,
            removed_from_textbook=True,
        )
        self.create_successful_adaptation(
            adaptation_batch=removed_adaptation_batch,
            strategy=success_strategy_2,
            exercise=self.create(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_at=created_at,
                page_number=47,
                exercise_number="Removed",
                textbook=textbook,
                removed_from_textbook=False,
                full_text=textwrap.dedent(
                    """\
                    Complète avec "le vent" ou "la pluie"
                    a. Les feuilles sont chahutées par ...
                    b. Les vitres sont mouillées par ...
                    """
                ),
                instruction_hint_example_text=None,
                statement_text=None,
                classified_at=None,
                classified_by_classification_batch=None,
                classified_by_username=None,
                exercise_class=None,
            ),
        )

        errors_branch = self.create_dummy_branch(name="Branch with errors", system_prompt="Thou shall fail.")
        errors_strategy = self.create(
            db.AdaptationStrategy,
            created_by_username="Patty",
            created_at=created_at,
            model=llm.DummyModel(name="dummy-1"),
            settings=errors_branch.latest_strategy_settings,
        )
        errors_adaptation_batch = self.create(
            db.AdaptationBatch,
            created_by_username="Patty",
            created_at=created_at,
            strategy=errors_strategy,
            textbook=textbook,
            removed_from_textbook=False,
        )
        self.create_not_json_adaptation(
            adaptation_batch=errors_adaptation_batch,
            strategy=errors_strategy,
            exercise=self.create(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_at=created_at,
                page_number=142,
                exercise_number="4",
                textbook=textbook,
                removed_from_textbook=False,
                full_text="Not JSON",
                instruction_hint_example_text=None,
                statement_text=None,
                classified_at=None,
                classified_by_classification_batch=None,
                classified_by_username=None,
                exercise_class=None,
            ),
        )
        self.create_invalid_json_adaptation(
            adaptation_batch=errors_adaptation_batch,
            strategy=errors_strategy,
            exercise=self.create(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_at=created_at,
                page_number=140,
                exercise_number="4",
                textbook=textbook,
                removed_from_textbook=False,
                full_text="Invalid JSON",
                instruction_hint_example_text=None,
                statement_text=None,
                classified_at=None,
                classified_by_classification_batch=None,
                classified_by_username=None,
                exercise_class=None,
            ),
        )

    def create_dummy_textbook_with_text_exercise_numbers(self) -> None:
        self.create_dummy_textbook()

        strategy = self.__session.get(db.AdaptationStrategy, 1)
        assert strategy is not None
        batch = self.__session.get(db.AdaptationBatch, 1)
        assert batch is not None

        self.create_successful_adaptation(
            adaptation_batch=batch,
            strategy=strategy,
            exercise=self.create(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_at=created_at,
                page_number=42,
                exercise_number="Exo identifié par texte / 5",  # URL-incompatible characters
                textbook=batch.textbook,
                removed_from_textbook=False,
                full_text=textwrap.dedent(
                    """\
                    Complète avec "le vent" ou "la pluie"
                    a. Les feuilles sont chahutées par ...
                    b. Les vitres sont mouillées par ...
                    """
                ),
                instruction_hint_example_text=None,
                statement_text=None,
                classified_at=None,
                classified_by_classification_batch=None,
                classified_by_username=None,
                exercise_class=None,
            ),
        )

        self.create_successful_adaptation(
            adaptation_batch=batch,
            strategy=strategy,
            exercise=self.create(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_at=created_at,
                page_number=42,
                exercise_number="Auto-dictée",
                textbook=batch.textbook,
                removed_from_textbook=False,
                full_text=textwrap.dedent(
                    """\
                    Complète avec "le vent" ou "la pluie"
                    a. Les feuilles sont chahutées par ...
                    b. Les vitres sont mouillées par ...
                    """
                ),
                instruction_hint_example_text=None,
                statement_text=None,
                classified_at=None,
                classified_by_classification_batch=None,
                classified_by_username=None,
                exercise_class=None,
            ),
        )

    def create_dummy_coche_exercise_classes(self) -> None:
        self.create_dummy_branch(name="CocheMot", system_prompt="Blah blah coche mot.")
        self.create_dummy_branch(name="CochePhrase", system_prompt="Blah blah coche phrase.")


def load(session: database_utils.Session, fixtures: Iterable[str]) -> None:
    creator = FixturesCreator(session)

    available_fixtures = {
        "-".join(f.__name__.split("_")[1:]): f
        for f in (
            creator.create_default_adaptation_input,
            creator.create_default_adaptation_strategy,
            creator.create_dummy_adaptation_strategy,
            creator.create_dummy_adaptation,
            creator.create_dummy_branch,
            creator.create_dummy_coche_exercise_classes,
            creator.create_dummy_textbook_with_text_exercise_numbers,
            creator.create_dummy_textbook,
            creator.create_mixed_dummy_adaptation_batch,
            creator.create_seed_data,
        )
    }

    database_utils.truncate_all_tables(session)

    for fixture in fixtures:
        available_fixtures[fixture]()


app = fastapi.FastAPI(database_engine=database_utils.create_engine(settings.DATABASE_URL))


@app.post("/load")
def post_load(fixtures: str, session: database_utils.SessionDependable) -> None:
    load(session, [] if fixtures == "" else fixtures.split(","))
