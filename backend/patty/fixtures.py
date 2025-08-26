import itertools
from typing import Iterable, TypeVar
import datetime
import textwrap

import boto3
import botocore
import compact_json  # type: ignore[import-untyped]
import fastapi
import sqlalchemy.orm

from . import adaptation
from . import classification
from . import database_utils
from . import exercises
from . import external_exercises  # noqa: F401 to populate the metadata
from . import extraction
from . import sandbox
from . import settings
from . import textbooks


created_at = datetime.datetime(2000, 1, 1, 0, 0, 0, 0, datetime.timezone.utc)


def make_default_adaptation_prompt() -> str:
    # Be very careful to KEEP THESE TWO VERSIONS of the exercise IN SYNC.

    text_exercise = textwrap.dedent(
        """\
        Complète avec "l'herbe" ou "les chats"
        a. Les vaches mangent ...
        b. Les chiens courent après ..."""
    )

    exercise = adaptation.adapted.ExerciseV1(
        format="v1",
        instruction=adaptation.adapted.InstructionPage(
            lines=[
                adaptation.adapted.InstructionLine(
                    contents=[
                        adaptation.adapted.Text(kind="text", text="Complète"),
                        adaptation.adapted.Whitespace(kind="whitespace"),
                        adaptation.adapted.Text(kind="text", text="avec"),
                        adaptation.adapted.Whitespace(kind="whitespace"),
                        adaptation.adapted.Choice(
                            kind="choice",
                            contents=[
                                adaptation.adapted.Text(kind="text", text="l'"),
                                adaptation.adapted.Text(kind="text", text="herbe"),
                            ],
                        ),
                        adaptation.adapted.Whitespace(kind="whitespace"),
                        adaptation.adapted.Text(kind="text", text="ou"),
                        adaptation.adapted.Whitespace(kind="whitespace"),
                        adaptation.adapted.Choice(
                            kind="choice",
                            contents=[
                                adaptation.adapted.Text(kind="text", text="les"),
                                adaptation.adapted.Whitespace(kind="whitespace"),
                                adaptation.adapted.Text(kind="text", text="chats"),
                            ],
                        ),
                    ]
                )
            ]
        ),
        example=None,
        hint=None,
        statement=adaptation.adapted.StatementPagesV1(
            pages=[
                adaptation.adapted.StatementPage(
                    lines=[
                        adaptation.adapted.StatementLine(
                            contents=[
                                adaptation.adapted.Text(kind="text", text="a"),
                                adaptation.adapted.Text(kind="text", text="."),
                                adaptation.adapted.Whitespace(kind="whitespace"),
                                adaptation.adapted.Text(kind="text", text="Les"),
                                adaptation.adapted.Whitespace(kind="whitespace"),
                                adaptation.adapted.Text(kind="text", text="vaches"),
                                adaptation.adapted.Whitespace(kind="whitespace"),
                                adaptation.adapted.Text(kind="text", text="mangent"),
                                adaptation.adapted.Whitespace(kind="whitespace"),
                                adaptation.adapted.MultipleChoicesInput(
                                    kind="multipleChoicesInput",
                                    choices=[
                                        adaptation.adapted.FormattedTextContainer(
                                            contents=[
                                                adaptation.adapted.Text(kind="text", text="l'"),
                                                adaptation.adapted.Text(kind="text", text="herbe"),
                                            ]
                                        ),
                                        adaptation.adapted.FormattedTextContainer(
                                            contents=[
                                                adaptation.adapted.Text(kind="text", text="les"),
                                                adaptation.adapted.Whitespace(kind="whitespace"),
                                                adaptation.adapted.Text(kind="text", text="chats"),
                                            ]
                                        ),
                                    ],
                                    showChoicesByDefault=False,
                                ),
                            ]
                        ),
                        adaptation.adapted.StatementLine(
                            contents=[
                                adaptation.adapted.Text(kind="text", text="b"),
                                adaptation.adapted.Text(kind="text", text="."),
                                adaptation.adapted.Whitespace(kind="whitespace"),
                                adaptation.adapted.Text(kind="text", text="Les"),
                                adaptation.adapted.Whitespace(kind="whitespace"),
                                adaptation.adapted.Text(kind="text", text="chiens"),
                                adaptation.adapted.Whitespace(kind="whitespace"),
                                adaptation.adapted.Text(kind="text", text="courent"),
                                adaptation.adapted.Whitespace(kind="whitespace"),
                                adaptation.adapted.Text(kind="text", text="après"),
                                adaptation.adapted.Whitespace(kind="whitespace"),
                                adaptation.adapted.MultipleChoicesInput(
                                    kind="multipleChoicesInput",
                                    choices=[
                                        adaptation.adapted.FormattedTextContainer(
                                            contents=[
                                                adaptation.adapted.Text(kind="text", text="l'"),
                                                adaptation.adapted.Text(kind="text", text="herbe"),
                                            ]
                                        ),
                                        adaptation.adapted.FormattedTextContainer(
                                            contents=[
                                                adaptation.adapted.Text(kind="text", text="les"),
                                                adaptation.adapted.Whitespace(kind="whitespace"),
                                                adaptation.adapted.Text(kind="text", text="chats"),
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
    exercise = extraction.extracted.Exercise.model_validate(
        {
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

    def add(self, instance: Model) -> Model:
        self.__session.add(instance)
        return instance

    def create_seed_data(self) -> None:
        # Adaptation
        settings = self.add(
            adaptation.AdaptationSettings(
                created_by="Patty",
                created_at=created_at,
                system_prompt=make_default_adaptation_prompt(),
                response_specification=adaptation.strategy.JsonSchemaLlmResponseSpecification(
                    format="json",
                    formalism="json-schema",
                    instruction_components=adaptation.adapted.InstructionComponents(
                        text=True, whitespace=True, arrow=True, formatted=True, choice=True
                    ),
                    example_components=adaptation.adapted.ExampleComponents(
                        text=True, whitespace=True, arrow=True, formatted=True
                    ),
                    hint_components=adaptation.adapted.HintComponents(
                        text=True, whitespace=True, arrow=True, formatted=True
                    ),
                    statement_components=adaptation.adapted.StatementComponents(
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
                    reference_components=adaptation.adapted.ReferenceComponents(
                        text=True, whitespace=True, arrow=True, formatted=True
                    ),
                ),
                exercise_class=None,
                parent=None,
            )
        )
        model = adaptation.llm.OpenAiModel(provider="openai", name="gpt-4o-2024-08-06")
        batch = self.add(
            sandbox.adaptation.SandboxAdaptationBatch(
                created_by="Patty", created_at=created_at, settings=settings, model=model
            )
        )
        self.make_successful_adaptation(
            created=self.add(
                sandbox.adaptation.AdaptationCreationBySandboxBatch(at=created_at, sandbox_adaptation_batch=batch)
            ),
            settings=settings,
            model=model,
            exercise=self.create_default_adaptation_input(),
        )

        # Extraction
        self.add(
            extraction.ExtractionSettings(
                created_by="Patty", created_at=created_at, prompt=make_default_extraction_prompt()
            )
        )

    def make_dummy_adaptation_strategy_settings(
        self, system_prompt: str = "Blah blah blah."
    ) -> adaptation.AdaptationSettings:
        return self.add(
            adaptation.AdaptationSettings(
                created_by="Patty",
                created_at=created_at,
                system_prompt=system_prompt,
                response_specification=adaptation.strategy.JsonSchemaLlmResponseSpecification(
                    format="json",
                    formalism="json-schema",
                    instruction_components=adaptation.adapted.InstructionComponents(
                        text=True, whitespace=True, arrow=True, formatted=True, choice=True
                    ),
                    example_components=adaptation.adapted.ExampleComponents(
                        text=True, whitespace=True, arrow=True, formatted=True
                    ),
                    hint_components=adaptation.adapted.HintComponents(
                        text=True, whitespace=True, arrow=True, formatted=True
                    ),
                    statement_components=adaptation.adapted.StatementComponents(
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
                    reference_components=adaptation.adapted.ReferenceComponents(
                        text=True, whitespace=True, arrow=True, formatted=True
                    ),
                ),
                exercise_class=None,
                parent=None,
            )
        )

    def create_default_adaptation_input(self) -> adaptation.AdaptableExercise:
        return self.add(
            adaptation.AdaptableExercise(
                created=exercises.ExerciseCreationByUser(at=created_at, username="Patty"),
                location=exercises.ExerciseLocationMaybePageAndNumber(page_number=42, exercise_number="5"),
                full_text=textwrap.dedent(
                    """\
                    Complète avec "le vent" ou "la pluie"
                    a. Les feuilles sont chahutées par ...
                    b. Les vitres sont mouillées par ...
                    """
                ),
                instruction_hint_example_text=None,
                statement_text=None,
            )
        )

    def make_successful_adaptation(
        self,
        *,
        created: adaptation.AdaptationCreation,
        settings: adaptation.AdaptationSettings,
        model: adaptation.llm.ConcreteModel,
        exercise: adaptation.AdaptableExercise,
    ) -> adaptation.Adaptation:
        return self.add(
            adaptation.Adaptation(
                created=created,
                settings=settings,
                model=model,
                exercise=exercise,
                raw_llm_conversations=[{"initial": "conversation"}],
                initial_assistant_response=adaptation.assistant_responses.Success(
                    kind="success",
                    exercise=adaptation.adapted.Exercise.model_validate(
                        {
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
        )

    def make_in_progress_adaptation(
        self,
        *,
        created: adaptation.AdaptationCreation,
        settings: adaptation.AdaptationSettings,
        model: adaptation.llm.ConcreteModel,
        exercise: adaptation.AdaptableExercise,
    ) -> adaptation.Adaptation:
        exercise_adaptation = self.add(
            adaptation.Adaptation(
                created=created,
                settings=settings,
                model=model,
                exercise=exercise,
                raw_llm_conversations=[{"initial": "conversation"}],
                initial_assistant_response=None,
                adjustments=[],
                manual_edit=None,
            )
        )
        # Hack: store a JSON null in _initial_assistant_response instead of a SQL NULL to avoid
        # being picked up by the submission daemon, but still pass as in-progress in the tests.
        exercise_adaptation._initial_assistant_response = None
        return exercise_adaptation

    def make_invalid_json_adaptation(
        self,
        *,
        created: adaptation.AdaptationCreation,
        settings: adaptation.AdaptationSettings,
        model: adaptation.llm.ConcreteModel,
        exercise: adaptation.AdaptableExercise,
    ) -> adaptation.Adaptation:
        return self.add(
            adaptation.Adaptation(
                created=created,
                settings=settings,
                model=model,
                exercise=exercise,
                raw_llm_conversations=[{"initial": "conversation"}],
                initial_assistant_response=adaptation.assistant_responses.InvalidJsonError(
                    kind="error", error="invalid-json", parsed={}
                ),
                adjustments=[],
                manual_edit=None,
            )
        )

    def make_not_json_adaptation(
        self,
        *,
        created: adaptation.AdaptationCreation,
        settings: adaptation.AdaptationSettings,
        model: adaptation.llm.ConcreteModel,
        exercise: adaptation.AdaptableExercise,
    ) -> adaptation.Adaptation:
        return self.add(
            adaptation.Adaptation(
                created=created,
                settings=settings,
                model=model,
                exercise=exercise,
                raw_llm_conversations=[{"initial": "conversation"}],
                initial_assistant_response=adaptation.assistant_responses.NotJsonError(
                    kind="error", error="not-json", text="This is not JSON."
                ),
                adjustments=[],
                manual_edit=None,
            )
        )

    def create_dummy_adaptation(self) -> None:
        settings = self.make_dummy_adaptation_strategy_settings()
        model = adaptation.llm.DummyModel(provider="dummy", name="dummy-1")
        self.make_successful_adaptation(
            created=self.add(
                sandbox.adaptation.AdaptationCreationBySandboxBatch(
                    at=created_at,
                    sandbox_adaptation_batch=self.add(
                        sandbox.adaptation.SandboxAdaptationBatch(
                            created_by="Patty", created_at=created_at, settings=settings, model=model
                        )
                    ),
                )
            ),
            settings=settings,
            model=model,
            exercise=self.create_default_adaptation_input(),
        )

    def create_mixed_dummy_adaptation_batch(self) -> None:
        settings = self.make_dummy_adaptation_strategy_settings()
        model = adaptation.llm.DummyModel(provider="dummy", name="dummy-1")
        batch = self.add(
            sandbox.adaptation.SandboxAdaptationBatch(
                created_by="Patty", created_at=created_at, settings=settings, model=model
            )
        )
        self.make_successful_adaptation(
            created=self.add(
                sandbox.adaptation.AdaptationCreationBySandboxBatch(at=created_at, sandbox_adaptation_batch=batch)
            ),
            settings=settings,
            model=model,
            exercise=self.create_default_adaptation_input(),
        )
        self.make_in_progress_adaptation(
            created=self.add(
                sandbox.adaptation.AdaptationCreationBySandboxBatch(at=created_at, sandbox_adaptation_batch=batch)
            ),
            settings=settings,
            model=model,
            exercise=self.create_default_adaptation_input(),
        )
        self.make_invalid_json_adaptation(
            created=self.add(
                sandbox.adaptation.AdaptationCreationBySandboxBatch(at=created_at, sandbox_adaptation_batch=batch)
            ),
            settings=settings,
            model=model,
            exercise=self.create_default_adaptation_input(),
        )
        self.make_not_json_adaptation(
            created=self.add(
                sandbox.adaptation.AdaptationCreationBySandboxBatch(at=created_at, sandbox_adaptation_batch=batch)
            ),
            settings=settings,
            model=model,
            exercise=self.create_default_adaptation_input(),
        )

    def create_dummy_branch(
        self, *, name: str = "Branchy McBranchFace", system_prompt: str = "Blah blah blah."
    ) -> adaptation.ExerciseClass:
        settings = self.make_dummy_adaptation_strategy_settings(system_prompt=system_prompt)
        exercise_class = self.add(
            adaptation.ExerciseClass(
                created=classification.ExerciseClassCreationByUser(at=created_at, username="Patty"),
                name=name,
                latest_strategy_settings=settings,
            )
        )
        self.__session.flush()
        settings.exercise_class = exercise_class
        return exercise_class

    def create_dummy_textbook(self) -> textbooks.Textbook:
        return self.add(
            textbooks.Textbook(
                created_by="Patty",
                created_at=created_at,
                title="Dummy Textbook Title",
                publisher=None,
                year=None,
                isbn=None,
            )
        )

    def create_dummy_textbook_with_text_exercise_numbers(self) -> None:
        model_for_extraction = extraction.llm.DummyModel(provider="dummy", name="dummy-1")
        model_for_adaptation = adaptation.llm.DummyModel(provider="dummy", name="dummy-1")

        textbook = self.create_dummy_textbook()

        pdf_file = self.add(
            extraction.PdfFile(
                created_by="Patty",
                created_at=created_at,
                sha256="dummy_sha256",
                bytes_count=123456,
                pages_count=30,
                known_file_names=["dummy_textbook.pdf"],
            )
        )
        pdf_file_range = self.add(
            extraction.PdfFileRange(
                created_by="Patty", created_at=created_at, pdf_file=pdf_file, first_page_number=10, pages_count=3
            )
        )
        extraction_batch = self.add(
            textbooks.TextbookExtractionBatch(
                created_by="Patty",
                created_at=created_at,
                pdf_file_range=pdf_file_range,
                textbook=textbook,
                first_textbook_page_number=40,
                model_for_extraction=model_for_extraction,
                model_for_adaptation=model_for_adaptation,
                removed_from_textbook=False,
            )
        )

        extraction_settings = self.add(
            extraction.ExtractionSettings(created_by="Patty", created_at=created_at, prompt="Blah blah blah.")
        )
        page_40_extraction = self.add(
            extraction.PageExtraction(
                created=textbooks.PageExtractionCreationByTextbook(
                    at=created_at, textbook_extraction_batch=extraction_batch
                ),
                pdf_file_range=pdf_file_range,
                pdf_page_number=10,  # Page 40 in the textbook
                settings=extraction_settings,
                model=model_for_extraction,
                run_classification=True,
                model_for_adaptation=model_for_adaptation,
                assistant_response=extraction.assistant_responses.Success(
                    kind="success",
                    exercises=[
                        extraction.extracted.Exercise(
                            id="p40_ex4",
                            numero="4",
                            consignes=['Complète avec "le vent" ou "la pluie"'],
                            conseil=None,
                            exemple=None,
                            enonce="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
                            references=None,
                            autre=None,
                        ),
                        extraction.extracted.Exercise(
                            id="p40_ex6",
                            numero="6",
                            consignes=['Complète avec "le vent" ou "la pluie"'],
                            conseil=None,
                            exemple=None,
                            enonce="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
                            references=None,
                            autre=None,
                        ),
                        extraction.extracted.Exercise(
                            id="p40_ex8",
                            numero="8",
                            consignes=['Complète avec "le vent" ou "la pluie"'],
                            conseil=None,
                            exemple=None,
                            enonce="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
                            references=None,
                            autre=None,
                        ),
                        extraction.extracted.Exercise(
                            id="p40_ex10",
                            numero="10",
                            consignes=['Complète avec "le vent" ou "la pluie"'],
                            conseil=None,
                            exemple=None,
                            enonce="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
                            references=None,
                            autre=None,
                        ),
                    ],
                ),
            )
        )
        exercise_4_page_40 = self.add(
            adaptation.AdaptableExercise(
                created=extraction.ExerciseCreationByPageExtraction(at=created_at, page_extraction=page_40_extraction),
                location=textbooks.ExerciseLocationTextbook(
                    textbook=textbook, page_number=40, exercise_number="4", removed_from_textbook=False
                ),
                full_text=textwrap.dedent(
                    """\
                Complète avec "le vent" ou "la pluie"
                a. Les feuilles sont chahutées par ...
                b. Les vitres sont mouillées par ...
                """
                ),
                instruction_hint_example_text='Complète avec "le vent" ou "la pluie"',
                statement_text="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
            )
        )
        exercise_6_page_40 = self.add(
            adaptation.AdaptableExercise(
                created=extraction.ExerciseCreationByPageExtraction(at=created_at, page_extraction=page_40_extraction),
                location=textbooks.ExerciseLocationTextbook(
                    textbook=textbook, page_number=40, exercise_number="6", removed_from_textbook=False
                ),
                full_text=textwrap.dedent(
                    """\
                Complète avec "le vent" ou "la pluie"
                a. Les feuilles sont chahutées par ...
                b. Les vitres sont mouillées par ...
                """
                ),
                instruction_hint_example_text='Complète avec "le vent" ou "la pluie"',
                statement_text="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
            )
        )
        exercise_10_page_40 = self.add(
            adaptation.AdaptableExercise(
                created=extraction.ExerciseCreationByPageExtraction(at=created_at, page_extraction=page_40_extraction),
                location=textbooks.ExerciseLocationTextbook(
                    textbook=textbook, page_number=40, exercise_number="10", removed_from_textbook=False
                ),
                full_text=textwrap.dedent(
                    """\
                Complète avec "le vent" ou "la pluie"
                a. Les feuilles sont chahutées par ...
                b. Les vitres sont mouillées par ...
                """
                ),
                instruction_hint_example_text='Complète avec "le vent" ou "la pluie"',
                statement_text="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
            )
        )
        exercise_8_page_40 = self.add(
            adaptation.AdaptableExercise(
                created=extraction.ExerciseCreationByPageExtraction(at=created_at, page_extraction=page_40_extraction),
                location=textbooks.ExerciseLocationTextbook(
                    textbook=textbook, page_number=40, exercise_number="8", removed_from_textbook=False
                ),
                full_text=textwrap.dedent(
                    """\
                Complète avec "le vent" ou "la pluie"
                a. Les feuilles sont chahutées par ...
                b. Les vitres sont mouillées par ...
                """
                ),
                instruction_hint_example_text='Complète avec "le vent" ou "la pluie"',
                statement_text="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
            )
        )
        page_42_extraction = self.add(
            extraction.PageExtraction(
                created=textbooks.PageExtractionCreationByTextbook(
                    at=created_at, textbook_extraction_batch=extraction_batch
                ),
                pdf_file_range=pdf_file_range,
                pdf_page_number=12,  # Page 42 in the textbook
                settings=extraction_settings,
                model=model_for_extraction,
                run_classification=True,
                model_for_adaptation=model_for_adaptation,
                assistant_response=extraction.assistant_responses.Success(
                    kind="success",
                    exercises=[
                        extraction.extracted.Exercise(
                            id="p42_ex5",
                            numero="5",
                            consignes=['Complète avec "le vent" ou "la pluie"'],
                            conseil=None,
                            exemple=None,
                            enonce="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
                            references=None,
                            autre=None,
                        ),
                        extraction.extracted.Exercise(
                            id="p42_ex6",
                            numero="6",
                            consignes=['Complète avec "le vent" ou "la pluie"'],
                            conseil=None,
                            exemple=None,
                            enonce="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
                            references=None,
                            autre=None,
                        ),
                        extraction.extracted.Exercise(
                            id="p42_exAutoDictée",
                            numero="Auto-dictée",
                            consignes=['Complète avec "le vent" ou "la pluie"'],
                            conseil=None,
                            exemple=None,
                            enonce="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
                            references=None,
                            autre=None,
                        ),
                        extraction.extracted.Exercise(
                            id="p42_ex6Texte",
                            numero="Exo identifié par texte / 5",
                            consignes=['Complète avec "le vent" ou "la pluie"'],
                            conseil=None,
                            exemple=None,
                            enonce="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
                            references=None,
                            autre=None,
                        ),
                    ],
                ),
            )
        )
        exercise_5_page_42 = self.add(
            adaptation.AdaptableExercise(
                created=extraction.ExerciseCreationByPageExtraction(at=created_at, page_extraction=page_42_extraction),
                location=textbooks.ExerciseLocationTextbook(
                    textbook=textbook, page_number=42, exercise_number="5", removed_from_textbook=False
                ),
                full_text=textwrap.dedent(
                    """\
                Complète avec "le vent" ou "la pluie"
                a. Les feuilles sont chahutées par ...
                b. Les vitres sont mouillées par ...
                """
                ),
                instruction_hint_example_text='Complète avec "le vent" ou "la pluie"',
                statement_text="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
            )
        )
        exercise_6_page_42 = self.add(
            adaptation.AdaptableExercise(
                created=extraction.ExerciseCreationByPageExtraction(at=created_at, page_extraction=page_42_extraction),
                location=textbooks.ExerciseLocationTextbook(
                    textbook=textbook, page_number=42, exercise_number="6", removed_from_textbook=False
                ),
                full_text=textwrap.dedent(
                    """\
                Complète avec "le vent" ou "la pluie"
                a. Les feuilles sont chahutées par ...
                b. Les vitres sont mouillées par ...
                """
                ),
                instruction_hint_example_text='Complète avec "le vent" ou "la pluie"',
                statement_text="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
            )
        )
        exercise_auto_dictée_page_42 = self.add(
            adaptation.AdaptableExercise(
                created=extraction.ExerciseCreationByPageExtraction(at=created_at, page_extraction=page_42_extraction),
                location=textbooks.ExerciseLocationTextbook(
                    textbook=textbook, page_number=42, exercise_number="Auto-dictée", removed_from_textbook=False
                ),
                full_text=textwrap.dedent(
                    """\
                Complète avec "le vent" ou "la pluie"
                a. Les feuilles sont chahutées par ...
                b. Les vitres sont mouillées par ...
                """
                ),
                instruction_hint_example_text='Complète avec "le vent" ou "la pluie"',
                statement_text="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
            )
        )
        exercise_text_page_42 = self.add(
            adaptation.AdaptableExercise(
                created=extraction.ExerciseCreationByPageExtraction(at=created_at, page_extraction=page_42_extraction),
                location=textbooks.ExerciseLocationTextbook(
                    textbook=textbook,
                    page_number=42,
                    exercise_number="Exo identifié par texte / 5",
                    removed_from_textbook=False,
                ),
                full_text=textwrap.dedent(
                    """\
                Complète avec "le vent" ou "la pluie"
                a. Les feuilles sont chahutées par ...
                b. Les vitres sont mouillées par ...
                """
                ),
                instruction_hint_example_text='Complète avec "le vent" ou "la pluie"',
                statement_text="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
            )
        )

        mcq_exercise_class = self.create_dummy_branch(name="QCM", system_prompt="Blah blah QCM.")
        page_40_classification_chunk = self.add(
            classification.ClassificationChunk(
                created=extraction.ClassificationChunkCreationByPageExtraction(
                    at=created_at, page_extraction=page_40_extraction
                ),
                model_for_adaptation=model_for_adaptation,
            )
        )
        self.add(
            classification.ClassificationByChunk(
                exercise=exercise_4_page_40,
                at=created_at,
                classification_chunk=page_40_classification_chunk,
                exercise_class=mcq_exercise_class,
            )
        )
        self.add(
            classification.ClassificationByChunk(
                exercise=exercise_6_page_40,
                at=created_at,
                classification_chunk=page_40_classification_chunk,
                exercise_class=mcq_exercise_class,
            )
        )
        self.add(
            classification.ClassificationByChunk(
                exercise=exercise_8_page_40,
                at=created_at,
                classification_chunk=page_40_classification_chunk,
                exercise_class=mcq_exercise_class,
            )
        )
        self.add(
            classification.ClassificationByChunk(
                exercise=exercise_10_page_40,
                at=created_at,
                classification_chunk=page_40_classification_chunk,
                exercise_class=mcq_exercise_class,
            )
        )
        page_42_classification_chunk = self.add(
            classification.ClassificationChunk(
                created=extraction.ClassificationChunkCreationByPageExtraction(
                    at=created_at, page_extraction=page_42_extraction
                ),
                model_for_adaptation=model_for_adaptation,
            )
        )
        self.add(
            classification.ClassificationByChunk(
                exercise=exercise_5_page_42,
                at=created_at,
                classification_chunk=page_42_classification_chunk,
                exercise_class=mcq_exercise_class,
            )
        )
        self.add(
            classification.ClassificationByChunk(
                exercise=exercise_6_page_42,
                at=created_at,
                classification_chunk=page_42_classification_chunk,
                exercise_class=mcq_exercise_class,
            )
        )
        self.add(
            classification.ClassificationByChunk(
                exercise=exercise_auto_dictée_page_42,
                at=created_at,
                classification_chunk=page_42_classification_chunk,
                exercise_class=mcq_exercise_class,
            )
        )
        self.add(
            classification.ClassificationByChunk(
                exercise=exercise_text_page_42,
                at=created_at,
                classification_chunk=page_42_classification_chunk,
                exercise_class=mcq_exercise_class,
            )
        )

        assert mcq_exercise_class.latest_strategy_settings is not None
        self.make_successful_adaptation(
            created=self.add(
                classification.AdaptationCreationByChunk(
                    at=created_at, classification_chunk=page_40_classification_chunk
                )
            ),
            settings=mcq_exercise_class.latest_strategy_settings,
            model=model_for_adaptation,
            exercise=exercise_4_page_40,
        )
        self.make_successful_adaptation(
            created=self.add(
                classification.AdaptationCreationByChunk(
                    at=created_at, classification_chunk=page_40_classification_chunk
                )
            ),
            settings=mcq_exercise_class.latest_strategy_settings,
            model=model_for_adaptation,
            exercise=exercise_6_page_40,
        )
        self.make_successful_adaptation(
            created=self.add(
                classification.AdaptationCreationByChunk(
                    at=created_at, classification_chunk=page_40_classification_chunk
                )
            ),
            settings=mcq_exercise_class.latest_strategy_settings,
            model=model_for_adaptation,
            exercise=exercise_8_page_40,
        )
        # No adaptation for exercise_10_page_40: check that it does not appear in the exported HTML
        self.make_successful_adaptation(
            created=self.add(
                classification.AdaptationCreationByChunk(
                    at=created_at, classification_chunk=page_42_classification_chunk
                )
            ),
            settings=mcq_exercise_class.latest_strategy_settings,
            model=model_for_adaptation,
            exercise=exercise_5_page_42,
        )
        self.make_successful_adaptation(
            created=self.add(
                classification.AdaptationCreationByChunk(
                    at=created_at, classification_chunk=page_42_classification_chunk
                )
            ),
            settings=mcq_exercise_class.latest_strategy_settings,
            model=model_for_adaptation,
            exercise=exercise_6_page_42,
        )
        self.make_successful_adaptation(
            created=self.add(
                classification.AdaptationCreationByChunk(
                    at=created_at, classification_chunk=page_42_classification_chunk
                )
            ),
            settings=mcq_exercise_class.latest_strategy_settings,
            model=model_for_adaptation,
            exercise=exercise_auto_dictée_page_42,
        )
        self.make_successful_adaptation(
            created=self.add(
                classification.AdaptationCreationByChunk(
                    at=created_at, classification_chunk=page_42_classification_chunk
                )
            ),
            settings=mcq_exercise_class.latest_strategy_settings,
            model=model_for_adaptation,
            exercise=exercise_text_page_42,
        )

    def create_dummy_coche_exercise_classes(self) -> None:
        self.create_dummy_branch(name="CocheMot", system_prompt="Blah blah coche mot.")
        self.create_dummy_branch(name="CochePhrase", system_prompt="Blah blah coche phrase.")

    def create_dummy_extraction_strategy(self) -> None:
        self.add(extraction.ExtractionSettings(created_by="Patty", created_at=created_at, prompt="Blah blah blah."))

    def make_adaptation_batches(self, count: int) -> None:
        model = adaptation.llm.DummyModel(provider="dummy", name="dummy-1")
        for i in range(count):
            settings = self.make_dummy_adaptation_strategy_settings(f"Blah blah blah {i + 1}.")
            self.add(
                sandbox.adaptation.SandboxAdaptationBatch(
                    created_by="Patty", created_at=created_at, settings=settings, model=model
                )
            )

    def create_20_adaptation_batches(self) -> None:
        self.make_adaptation_batches(20)

    def create_21_adaptation_batches(self) -> None:
        self.make_adaptation_batches(21)

    def create_70_adaptation_batches(self) -> None:
        self.make_adaptation_batches(70)

    def create_dummy_classification_batch(self) -> None:
        self.create_dummy_coche_exercise_classes()
        class1 = self.__session.get(adaptation.ExerciseClass, 1)
        assert class1 is not None
        assert class1.latest_strategy_settings is not None

        class2 = self.add(
            adaptation.ExerciseClass(
                created=classification.ExerciseClassCreationByUser(at=created_at, username="Patty"),
                name="NoSettings",
                latest_strategy_settings=None,
            )
        )

        model_for_adaptation = adaptation.llm.DummyModel(provider="dummy", name="dummy-1")

        batch = self.add(
            sandbox.classification.SandboxClassificationBatch(
                created_by="Patty", created_at=created_at, model_for_adaptation=model_for_adaptation
            )
        )
        chunk = self.add(
            classification.ClassificationChunk(
                created=sandbox.classification.ClassificationChunkCreationBySandboxBatch(
                    at=created_at, sandbox_classification_batch=batch
                ),
                model_for_adaptation=model_for_adaptation,
            )
        )
        exe1 = self.add(
            adaptation.AdaptableExercise(
                created=exercises.ExerciseCreationByUser(at=created_at, username="Patty"),
                location=exercises.ExerciseLocationMaybePageAndNumber(page_number=1, exercise_number="1"),
                full_text="Avec adaptation",
                instruction_hint_example_text=None,
                statement_text=None,
            )
        )
        self.add(
            classification.ClassificationByChunk(
                at=created_at, exercise=exe1, classification_chunk=chunk, exercise_class=class1
            )
        )
        self.make_successful_adaptation(
            created=self.add(classification.AdaptationCreationByChunk(at=created_at, classification_chunk=chunk)),
            model=model_for_adaptation,
            settings=class1.latest_strategy_settings,
            exercise=exe1,
        )
        exe2 = self.add(
            adaptation.AdaptableExercise(
                created=exercises.ExerciseCreationByUser(at=created_at, username="Patty"),
                location=exercises.ExerciseLocationMaybePageAndNumber(page_number=1, exercise_number="1"),
                full_text="Sans adaptation",
                instruction_hint_example_text=None,
                statement_text=None,
            )
        )
        self.add(
            classification.ClassificationByChunk(
                at=created_at, exercise=exe2, classification_chunk=chunk, exercise_class=class2
            )
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
        session.flush()


app = fastapi.FastAPI(database_engine=database_utils.create_engine(settings.DATABASE_URL))


@app.post("/load")
def post_load(fixtures: str, session: database_utils.SessionDependable) -> None:
    load(session, True, [] if fixtures == "" else fixtures.split(","))
