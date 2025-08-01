import itertools
from typing import Any, Iterable, TypeVar
import datetime
import textwrap

import boto3
import botocore
import compact_json  # type: ignore[import-untyped]
import fastapi
import sqlalchemy.orm

from . import adapted
from . import database_utils
from . import extracted
from . import orm_models as db
from . import settings
from .adaptation import adaptation
from .adaptation import llm as adaptation_llm
from .adaptation import strategy as adaptation_strategy
from .extraction import llm as extraction_llm


created_at = datetime.datetime(2000, 1, 1, 0, 0, 0, 0, datetime.timezone.utc)


def make_default_adaptation_prompt() -> str:
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


def make_default_extraction_prompt() -> str:
    exercise = extracted.Exercise(
        **{  # type: ignore[arg-type]
            "id": "p47_ex4",
            "numero": "1",
            "consignes": [
                "Additionne les nombres suivants et donne le résultat.",
                "Soustrais les nombres suivants et donne le résultat.",
            ],
            "enonce": "7 + 3, 5 + 2, 8 + 6, 4 + 9",
            "conseil": "Commence par ajouter les unités et vérifie ton résultat.",
            "exemple": "4 + 5 = 9.",
            "references": "© Source: Manuel de mathématiques, page 34.",
            "autre": "Informations additionnelles si présentes.",
        }
    )

    return textwrap.dedent(
        f"""\
        You are an expert in the extraction and structuring of educational exercises from texts. Your task is to :
        1. Carefully read the input and extract exercises without modifying the text in any way. Keep the exact format, language, letters, words, punctuation, and sentence structure as in the original.
        2. Extract only the exercise-related elements, structured as follows:

           JSON Schema:
        { textwrap.indent(exercise.model_dump_json(indent=2), "        ").lstrip() }

        3. Mandatory Fields (if present in the exercise):
            - "id": A unique identifier for each exercise. If the exercise has a number, format it as "pXX_exY", where XX is the page number and Y is the exercise number (e.g., "p47_ex4"). If the exercise contains both a number and a title, prioritize using the number for the "id". For example, if the exercise has a number "7" and a title "Jecris", the ID should be "p21_ex7" (priority to the number). If no number is given, use a descriptive title for the exercise (e.g., "p45_exDefiLangue", "p49_exJecris").
            - "numero": Exercise number (e.g., "1"). If no number is given, skip it.
            - "consignes": A **list** of all instructions that belong to the same exercise. These are often bolded or clearly marked.
            - **"exemple": Example or model solution (optional). Identify text that demonstrates how to do the exercise. Look for visual/textual cues:
                - **Position:** Often appears *between* the `consignes` and the main `enonce` (especially before lists like a., b., c...).
                - **Keywords:** May start with indicators like "Exemple:", "Ex:", etc.
                - **Formatting:** May use distinct formatting such as *italics*, indentation, parentheses, or be visually set apart (reflecting original distinctions like color or boxing).**
            - "enonce": The main content of the exercise **itself** (e.g., questions, sentences to complete, list items). This follows `consignes` and any `exemple` or `conseil`. **Crucially, ensure that text identified as `exemple` or `conseil` is *excluded* from the `enonce`.**
            - **"conseil": Helpful hints, tips, or guidance (optional). Identify text offering advice. Look for visual/textual cues:
                - **Position:** Can appear anywhere relative to the `consignes`, `exemple`, or `enonce`, but is distinct from them.
                - **Keywords:** May start with indicators like "Conseil:", "Astuce:", "Attention:", "N.B.:", "Rappel:", etc.
                - **Formatting:** May use distinct formatting such as *italics*, indentation, parentheses, or be visually set apart.**
            - "references": Source or citation (optional).
            - "autre": Other relevant information (optional).

        4. Preserve the original format and layout as in the input document.
        5. Group multiple instructions ("consignes") under the same `"numero"` if they belong to the same exercise.
        6. Return only the JSON content without any formatting markers.
        7. Do not wrap the response in <think> tags—provide the JSON directly.
        8. Do not solve the exercises please, you should only extract them as-is.
        9. Maintain list structures exactly as they appear.
        10. Do not separate words or phrases unnecessarily.
        11. Respect list ordering.
        12. Return a list of exercises in strict JSON format. Use only double quotes for keys and values.
        13. An image of the page is attached that contains exercise boxes—structure the content based on the visual layout.
        14. In the image, the 'consigne' is typically bold. Use **all available visual and textual cues** to distinguish between `consignes`, `exemple`, `conseil`, and `enonce`. Pay close attention to:
            - **Formatting:** Bolding (often `consignes`), *italics* (often `exemple` or `conseil`), indentation, parentheses.
            - **Positioning:** Especially text located between `consignes` and list-based `enonce` (often `exemple`).
            - **Keywords:** Explicit labels like "Exemple:", "Conseil:", "Attention:", etc.
            **Assume that elements like examples and advice might have had distinct visual treatments (like color or boxing) in the source, and look for corresponding textual cues (italics, indentation, keywords) to identify them.**
        15. Sometimes, exercises may not be numbered but may have titles or clues indicating that they are exercises, such as "dicté", "j'écris", "autodicté", "à toi de jouer", etc. These should be included as exercises as well.
        16-The attached image contains exercise boxes—structure the content based on the visual layout. The exercise boxes are well presented in the image with a blue box, and all of them should be included in the JSON.
        """
    )


class FixturesCreator:
    def __init__(self, session: database_utils.Session) -> None:
        self.__session = session

    Model = TypeVar("Model", bound=sqlalchemy.orm.DeclarativeBase)

    def make(self, __model: type[Model], **kwargs: Any) -> Model:
        instance = __model(**kwargs)
        self.__session.add(instance)
        self.__session.flush()
        return instance

    def create_default_adaptation_strategy(self) -> db.AdaptationStrategy:
        strategy_settings = self.make(
            db.AdaptationStrategySettings,
            created_by_username="Patty",
            created_at=created_at,
            system_prompt=make_default_adaptation_prompt(),
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
        return self.make(
            db.AdaptationStrategy,
            created_by_username="Patty",
            created_by_classification_batch=None,
            created_at=created_at,
            model=adaptation_llm.OpenAiModel(provider="openai", name="gpt-4o-2024-08-06"),
            settings=strategy_settings,
        )

    def make_dummy_adaptation_strategy_settings(
        self, system_prompt: str = "Blah blah blah."
    ) -> db.AdaptationStrategySettings:
        return self.make(
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

    def create_dummy_adaptation_strategy(self, system_prompt: str = "Blah blah blah.") -> db.AdaptationStrategy:
        settings = self.make_dummy_adaptation_strategy_settings(system_prompt)
        return self.make(
            db.AdaptationStrategy,
            created_by_username="Patty",
            created_by_classification_batch=None,
            created_at=created_at,
            model=adaptation_llm.DummyModel(provider="dummy", name="dummy-1"),
            settings=settings,
        )

    def create_default_adaptation_input(self) -> db.AdaptableExercise:
        return self.make(
            db.AdaptableExercise,
            created_by_username="Patty",
            created_by_page_extraction=None,
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

    def make_successful_adaptation(
        self,
        *,
        adaptation_batch: db.AdaptationBatch | None,
        strategy: db.AdaptationStrategy,
        exercise: db.AdaptableExercise,
    ) -> db.Adaptation:
        return self.make(
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

    def make_in_progress_adaptation(
        self,
        *,
        adaptation_batch: db.AdaptationBatch | None,
        strategy: db.AdaptationStrategy,
        exercise: db.AdaptableExercise,
    ) -> db.Adaptation:
        return self.make(
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

    def make_invalid_json_adaptation(
        self,
        *,
        adaptation_batch: db.AdaptationBatch | None,
        strategy: db.AdaptationStrategy,
        exercise: db.AdaptableExercise,
    ) -> db.Adaptation:
        return self.make(
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

    def make_not_json_adaptation(
        self,
        *,
        adaptation_batch: db.AdaptationBatch | None,
        strategy: db.AdaptationStrategy,
        exercise: db.AdaptableExercise,
    ) -> db.Adaptation:
        return self.make(
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
        batch = self.make(
            db.AdaptationBatch,
            created_by_username="Patty",
            created_at=created_at,
            textbook=None,
            removed_from_textbook=False,
            strategy=strategy,
        )
        self.make_successful_adaptation(
            adaptation_batch=batch, strategy=strategy, exercise=self.create_default_adaptation_input()
        )
        self.create_default_extraction_strategy()

    def create_dummy_adaptation(self) -> None:
        strategy = self.create_dummy_adaptation_strategy()
        batch = self.make(
            db.AdaptationBatch,
            created_by_username="Patty",
            created_at=created_at,
            textbook=None,
            removed_from_textbook=False,
            strategy=strategy,
        )
        self.make_successful_adaptation(
            adaptation_batch=batch, strategy=strategy, exercise=self.create_default_adaptation_input()
        )

    def create_mixed_dummy_adaptation_batch(self) -> None:
        strategy = self.create_dummy_adaptation_strategy()
        batch = self.make(
            db.AdaptationBatch,
            created_by_username="Patty",
            created_at=created_at,
            textbook=None,
            removed_from_textbook=False,
            strategy=strategy,
        )
        self.make_successful_adaptation(
            adaptation_batch=batch, strategy=strategy, exercise=self.create_default_adaptation_input()
        )
        self.make_in_progress_adaptation(
            adaptation_batch=batch, strategy=strategy, exercise=self.create_default_adaptation_input()
        )
        self.make_invalid_json_adaptation(
            adaptation_batch=batch, strategy=strategy, exercise=self.create_default_adaptation_input()
        )
        self.make_not_json_adaptation(
            adaptation_batch=batch, strategy=strategy, exercise=self.create_default_adaptation_input()
        )

    def create_dummy_branch(
        self, *, name: str = "Branchy McBranchFace", system_prompt: str = "Blah blah blah."
    ) -> db.ExerciseClass:
        settings = self.make_dummy_adaptation_strategy_settings(system_prompt=system_prompt)
        exercise_class = self.make(
            db.ExerciseClass,
            created_by_username="Patty",
            created_by_classification_batch=None,
            created_at=created_at,
            name=name,
            latest_strategy_settings=settings,
        )
        settings.exercise_class = exercise_class
        return exercise_class

    def create_dummy_textbook(self) -> None:
        textbook = self.make(
            db.Textbook,
            created_by_username="Patty",
            created_at=created_at,
            title="Dummy Textbook Title",
            editor=None,
            year=None,
            isbn=None,
        )

        success_branch_1 = self.create_dummy_branch(name="Branch with successes 1", system_prompt="Thou shall succeed.")
        success_strategy_1 = self.make(
            db.AdaptationStrategy,
            created_by_username="Patty",
            created_by_classification_batch=None,
            created_at=created_at,
            model=adaptation_llm.DummyModel(provider="dummy", name="dummy-1"),
            settings=success_branch_1.latest_strategy_settings,
        )
        success_adaptation_batch_1 = self.make(
            db.AdaptationBatch,
            created_by_username="Patty",
            created_at=created_at,
            strategy=success_strategy_1,
            textbook=textbook,
            removed_from_textbook=False,
        )
        self.make_successful_adaptation(
            adaptation_batch=success_adaptation_batch_1,
            strategy=success_strategy_1,
            exercise=self.make(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_by_page_extraction=None,
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
        self.make_successful_adaptation(
            adaptation_batch=success_adaptation_batch_1,
            strategy=success_strategy_1,
            exercise=self.make(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_by_page_extraction=None,
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
        self.make_successful_adaptation(
            adaptation_batch=success_adaptation_batch_1,
            strategy=success_strategy_1,
            exercise=self.make(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_by_page_extraction=None,
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
        success_strategy_2 = self.make(
            db.AdaptationStrategy,
            created_by_username="Patty",
            created_by_classification_batch=None,
            created_at=created_at,
            model=adaptation_llm.DummyModel(provider="dummy", name="dummy-1"),
            settings=success_branch_2.latest_strategy_settings,
        )
        success_adaptation_batch_2 = self.make(
            db.AdaptationBatch,
            created_by_username="Patty",
            created_at=created_at,
            strategy=success_strategy_2,
            textbook=textbook,
            removed_from_textbook=False,
        )
        self.make_successful_adaptation(
            adaptation_batch=success_adaptation_batch_2,
            strategy=success_strategy_2,
            exercise=self.make(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_by_page_extraction=None,
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
        self.make_successful_adaptation(
            adaptation_batch=success_adaptation_batch_2,
            strategy=success_strategy_2,
            exercise=self.make(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_by_page_extraction=None,
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
        self.make_successful_adaptation(
            adaptation_batch=success_adaptation_batch_2,
            strategy=success_strategy_2,
            exercise=self.make(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_by_page_extraction=None,
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
        self.make_successful_adaptation(
            adaptation_batch=success_adaptation_batch_2,
            strategy=success_strategy_2,
            exercise=self.make(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_by_page_extraction=None,
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

        removed_adaptation_batch = self.make(
            db.AdaptationBatch,
            created_by_username="Patty",
            created_at=created_at,
            strategy=success_strategy_2,
            textbook=textbook,
            removed_from_textbook=True,
        )
        self.make_successful_adaptation(
            adaptation_batch=removed_adaptation_batch,
            strategy=success_strategy_2,
            exercise=self.make(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_by_page_extraction=None,
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
        errors_strategy = self.make(
            db.AdaptationStrategy,
            created_by_username="Patty",
            created_by_classification_batch=None,
            created_at=created_at,
            model=adaptation_llm.DummyModel(provider="dummy", name="dummy-1"),
            settings=errors_branch.latest_strategy_settings,
        )
        errors_adaptation_batch = self.make(
            db.AdaptationBatch,
            created_by_username="Patty",
            created_at=created_at,
            strategy=errors_strategy,
            textbook=textbook,
            removed_from_textbook=False,
        )
        self.make_not_json_adaptation(
            adaptation_batch=errors_adaptation_batch,
            strategy=errors_strategy,
            exercise=self.make(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_by_page_extraction=None,
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
        self.make_invalid_json_adaptation(
            adaptation_batch=errors_adaptation_batch,
            strategy=errors_strategy,
            exercise=self.make(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_by_page_extraction=None,
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

        self.make_successful_adaptation(
            adaptation_batch=batch,
            strategy=strategy,
            exercise=self.make(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_by_page_extraction=None,
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

        self.make_successful_adaptation(
            adaptation_batch=batch,
            strategy=strategy,
            exercise=self.make(
                db.AdaptableExercise,
                created_by_username="Patty",
                created_by_page_extraction=None,
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

    def create_default_extraction_strategy(self) -> None:
        self.make(
            db.ExtractionStrategy,
            created_by_username="Patty",
            created_at=created_at,
            model=extraction_llm.GeminiModel(provider="gemini", name="gemini-2.0-flash"),
            prompt=make_default_extraction_prompt(),
        )

    def create_dummy_extraction_strategy(self) -> None:
        self.make(
            db.ExtractionStrategy,
            created_by_username="Patty",
            created_at=created_at,
            model=extraction_llm.DummyModel(provider="dummy", name="dummy-1"),
            prompt="Blah blah blah.",
        )

    def make_adaptation_batches(self, count: int) -> None:
        for i in range(count):
            strategy = self.create_dummy_adaptation_strategy(f"Blah blah blah {i + 1}.")
            self.make(
                db.AdaptationBatch,
                created_by_username="Patty",
                created_at=created_at,
                textbook=None,
                removed_from_textbook=False,
                strategy=strategy,
            )

    def create_20_adaptation_batches(self) -> None:
        self.make_adaptation_batches(20)

    def create_21_adaptation_batches(self) -> None:
        self.make_adaptation_batches(21)

    def create_70_adaptation_batches(self) -> None:
        self.make_adaptation_batches(70)

    def create_dummy_classification_batch(self) -> None:
        self.create_dummy_coche_exercise_classes()
        class1 = self.__session.get(db.ExerciseClass, 1)
        assert class1 is not None

        class2 = self.make(
            db.ExerciseClass,
            created_by_username="Patty",
            created_by_classification_batch=None,
            created_at=created_at,
            name="NoSettings",
            latest_strategy_settings=None,
        )

        model_for_adaptation = adaptation_llm.DummyModel(provider="dummy", name="dummy-1")

        batch = self.make(
            db.ClassificationBatch,
            created_by_username="Patty",
            created_at=created_at,
            created_by_page_extraction=None,
            model_for_adaptation=model_for_adaptation,
        )
        exe1 = self.make(
            db.AdaptableExercise,
            created_by_username="Patty",
            created_by_page_extraction=None,
            created_at=created_at,
            page_number=1,
            exercise_number="1",
            textbook=None,
            removed_from_textbook=False,
            full_text="Avec adaptation",
            instruction_hint_example_text=None,
            statement_text=None,
            classified_at=created_at,
            classified_by_classification_batch=batch,
            classified_by_username=None,
            exercise_class=class1,
        )
        self.make_successful_adaptation(
            adaptation_batch=None,
            strategy=self.make(
                db.AdaptationStrategy,
                created_at=created_at,
                created_by_username=None,
                created_by_classification_batch=batch,
                model=model_for_adaptation,
                settings=class1.latest_strategy_settings,
            ),
            exercise=exe1,
        )
        self.make(
            db.AdaptableExercise,
            created_by_username="Patty",
            created_by_page_extraction=None,
            created_at=created_at,
            page_number=1,
            exercise_number="1",
            textbook=None,
            removed_from_textbook=False,
            full_text="Sans adaptation",
            instruction_hint_example_text=None,
            statement_text=None,
            classified_at=created_at,
            classified_by_classification_batch=batch,
            classified_by_username=None,
            exercise_class=class2,
        )


def load(session: database_utils.Session, truncate: bool, fixtures: Iterable[str]) -> None:
    creator = FixturesCreator(session)

    available_fixtures = {
        "-".join(name.split("_")[1:]): getattr(creator, name) for name in dir(creator) if name.startswith("create_")
    }

    if truncate:
        database_utils.truncate_all_tables(session)

        s3 = boto3.client("s3", config=botocore.client.Config(region_name="eu-west-3"))
        for batch in itertools.batched(
            (
                {"Key": obj["Key"]}
                for page in s3.get_paginator("list_objects_v2").paginate(Bucket="jacquev6", Prefix="patty/dev")
                if "Contents" in page
                for obj in page["Contents"]
            ),
            1000,
        ):
            s3.delete_objects(Bucket="jacquev6", Delete={"Objects": batch})

    for fixture in fixtures:
        available_fixtures[fixture]()


app = fastapi.FastAPI(database_engine=database_utils.create_engine(settings.DATABASE_URL))


@app.post("/load")
def post_load(fixtures: str, session: database_utils.SessionDependable) -> None:
    load(session, True, [] if fixtures == "" else fixtures.split(","))
