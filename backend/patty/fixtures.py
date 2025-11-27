import os
from typing import Iterable, TypeVar
import datetime
import textwrap

import compact_json  # type: ignore[import-untyped]
import fastapi
import sqlalchemy.orm

from . import adaptation
from . import classification
from . import database_utils
from . import errors  # noqa: F401 to populate the metadata
from . import exercises
from . import external_exercises  # noqa: F401 to populate the metadata
from . import extraction
from . import file_storage
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
    exercise = extraction.extracted.ExerciseV2.model_validate(
        {
            "id": "p47_ex4",
            "type": "exercice",
            "images": True,
            "type_images": "ordered",
            "properties": {
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
            },
        }
    )

    # Unusual whitespace (U+00a0) comes from Mohamed-Amine's prompt. Cowardly keeping it for now. Same for missing last line ending.
    return textwrap.dedent(
        f"""\
        You are an expert in the extraction and structuring of educational exercises from texts. 
        Your task is to :  

        1. Carefully read the input and extract exercises without modifying the text in any way. Keep the exact format, language, letters, words, punctuation, and sentence structure as in the original.  

        2. Extract only the exercise-related elements, structured as follows:  
        { textwrap.indent(exercise.model_dump_json(indent=2).replace("  ", "  "), "        ").lstrip() }

        3. **Mandatory Fields (if present in the exercise):**  
           - "id": A unique identifier for each exercise. If the exercise has a number, format it as "pXX_exY", where XX is the page number and Y is the exercise number.  
           - "numero": Exercise number.  
           - "consignes": List of all instructions.  
           - "exemple": Example solution (optional).  
           - "enonce": The main content of the exercise.  
           - "conseil": Helpful hints (optional).  
           - "references": Source (optional).  
           - "autre": Other info (optional).  

        4. **Images rule:**  
           - If no image → "images": false, "type_images": "none".  
           - If one image → "images": true, "type_images": "unique".  
           - If multiple images → "images": true, "type_images": "ordered", "unordered" or "composite".  
           - Images are **always contained in a red box**, and their **name is written in the middle of the image in white text with a black background**.  
           - When an image is present, insert its filename (without extension) in the `enonce` between `{{ }}`.  
             - Example: `a. {{p130c2}} {{p130c3}}, b. {{p130c0}} {{p130c1}}`  

        5. Preserve the original format and layout as in the input document.  

        6. Group multiple consignes under the same "numero" if they belong to the same exercise.  

        7. Return only the JSON content, strict JSON format, with double quotes.  

        8. Do not solve the exercises.  

        9. Maintain list structures and ordering.  

        10. For images, filenames like `p078c10.png` should appear in the `enonce` as `{{p078c10}}`.  

        11. Use all visual and textual cues (bold, italics, indentation) to separate consigne, exemple, conseil, and enonce.  

        12. Always output a JSON list of exercises.  """
    )


class FixturesCreator:
    def __init__(self, session: database_utils.Session) -> None:
        self.__session = session

    Model = TypeVar("Model", bound=sqlalchemy.orm.DeclarativeBase)

    def add(self, instance: Model) -> Model:
        self.__session.add(instance)
        return instance

    def create_seed_data(self) -> None:
        self.create_adaptation_seed_data()
        self.create_extraction_seed_data()

    def create_adaptation_seed_data(self) -> None:
        settings = self.add(
            adaptation.AdaptationSettings(
                created_by="Patty",
                created_at=created_at,
                system_prompt=make_default_adaptation_prompt(),
                response_specification=adaptation.strategy.JsonSchemaLlmResponseSpecification(
                    format="json",
                    formalism="json-schema",
                    instruction_components=adaptation.adapted.InstructionComponents(
                        text=True, whitespace=True, arrow=True, formatted=True, image=True, choice=True
                    ),
                    example_components=adaptation.adapted.ExampleComponents(
                        text=True, whitespace=True, arrow=True, formatted=True, image=True
                    ),
                    hint_components=adaptation.adapted.HintComponents(
                        text=True, whitespace=True, arrow=True, formatted=True, image=True
                    ),
                    statement_components=adaptation.adapted.StatementComponents(
                        text=True,
                        whitespace=True,
                        arrow=True,
                        formatted=True,
                        image=True,
                        free_text_input=False,
                        multiple_choices_input=True,
                        selectable_input=False,
                        swappable_input=False,
                        editable_text_input=False,
                        split_word_input=False,
                    ),
                    reference_components=adaptation.adapted.ReferenceComponents(
                        text=True, whitespace=True, arrow=True, formatted=True, image=True
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

    def create_extraction_seed_data(self) -> None:
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
                        text=True, whitespace=True, arrow=True, formatted=True, image=True, choice=True
                    ),
                    example_components=adaptation.adapted.ExampleComponents(
                        text=True, whitespace=True, arrow=True, formatted=True, image=True
                    ),
                    hint_components=adaptation.adapted.HintComponents(
                        text=True, whitespace=True, arrow=True, formatted=True, image=True
                    ),
                    statement_components=adaptation.adapted.StatementComponents(
                        text=True,
                        whitespace=True,
                        arrow=True,
                        formatted=True,
                        image=True,
                        free_text_input=True,
                        multiple_choices_input=True,
                        selectable_input=True,
                        swappable_input=True,
                        editable_text_input=True,
                        split_word_input=True,
                    ),
                    reference_components=adaptation.adapted.ReferenceComponents(
                        text=True, whitespace=True, arrow=True, formatted=True, image=True
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
                initial_timing=None,
                adjustments=[],
                manual_edit=None,
                approved_by=None,
                approved_at=None,
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
                initial_timing=None,
                adjustments=[],
                manual_edit=None,
                approved_by=None,
                approved_at=None,
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
                initial_timing=None,
                adjustments=[],
                manual_edit=None,
                approved_by=None,
                approved_at=None,
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
                initial_timing=None,
                adjustments=[],
                manual_edit=None,
                approved_by=None,
                approved_at=None,
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
                pages_count=None,
                single_pdf_file=None,
            )
        )

    def create_dummy_textbook_with_pdf_range(
        self,
    ) -> tuple[
        extraction.llm.ConcreteModel,
        adaptation.llm.ConcreteModel,
        textbooks.Textbook,
        extraction.PdfFileRange,
        textbooks.TextbookExtractionBatch,
        extraction.ExtractionSettings,
        adaptation.ExerciseClass,
    ]:
        model_for_extraction = extraction.llm.DummyModel(provider="dummy", name="dummy-1")
        model_for_adaptation = adaptation.llm.DummyModel(provider="dummy", name="dummy-1")

        textbook = self.create_dummy_textbook()

        pdf_file = self.add(
            extraction.PdfFile(
                created_by="Patty",
                created_at=created_at,
                sha256="044c5caf34cba74e1e4cb6a498485923a8dbf28b74d414155586f18236da78b4",
                bytes_count=37223,
                pages_count=35,
                known_file_names=["long.pdf"],
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
                marked_as_removed=False,
            )
        )

        extraction_settings = self.add(
            extraction.ExtractionSettings(created_by="Patty", created_at=created_at, prompt="Blah blah blah.")
        )
        page_40_extraction = self.add(
            extraction.PageExtraction(
                created=textbooks.PageExtractionCreationByTextbook(
                    at=created_at, textbook_extraction_batch=extraction_batch, marked_as_removed=False
                ),
                pdf_file_range=pdf_file_range,
                pdf_page_number=10,  # Page 40 in the textbook
                settings=extraction_settings,
                model=model_for_extraction,
                run_classification=True,
                model_for_adaptation=model_for_adaptation,
                assistant_response=extraction.assistant_responses.SuccessV2(
                    kind="success",
                    version="v2",
                    exercises=[
                        extraction.extracted.ExerciseV2(
                            id="p40_ex4",
                            type="exercice",
                            images=False,
                            type_images="none",
                            properties=extraction.extracted.ExerciseV2.Properties(
                                numero="4",
                                consignes=['Complète avec "le vent" ou "la pluie"'],
                                conseil=None,
                                exemple=None,
                                enonce="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
                                references=None,
                                autre=None,
                            ),
                        ),
                        extraction.extracted.ExerciseV2(
                            id="p40_ex6",
                            type="exercice",
                            images=False,
                            type_images="none",
                            properties=extraction.extracted.ExerciseV2.Properties(
                                numero="6",
                                consignes=['Complète avec "le vent" ou "la pluie"'],
                                conseil=None,
                                exemple=None,
                                enonce="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
                                references=None,
                                autre=None,
                            ),
                        ),
                        extraction.extracted.ExerciseV2(
                            id="p40_ex10",
                            type="exercice",
                            images=False,
                            type_images="none",
                            properties=extraction.extracted.ExerciseV2.Properties(
                                numero="10",
                                consignes=['Complète avec "le vent" ou "la pluie"'],
                                conseil=None,
                                exemple=None,
                                enonce="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
                                references=None,
                                autre=None,
                            ),
                        ),
                        extraction.extracted.ExerciseV2(
                            id="p40_ex8",
                            type="exercice",
                            images=False,
                            type_images="none",
                            properties=extraction.extracted.ExerciseV2.Properties(
                                numero="8",
                                consignes=['Complète avec "le vent" ou "la pluie"'],
                                conseil=None,
                                exemple=None,
                                enonce="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
                                references=None,
                                autre=None,
                            ),
                        ),
                    ],
                ),
                timing=None,
            )
        )
        exercise_4_page_40 = self.add(
            adaptation.AdaptableExercise(
                created=extraction.ExerciseCreationByPageExtraction(at=created_at, page_extraction=page_40_extraction),
                location=textbooks.ExerciseLocationTextbook(
                    textbook=textbook, page_number=40, exercise_number="4", marked_as_removed=False
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
                    textbook=textbook, page_number=40, exercise_number="6", marked_as_removed=False
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
                    textbook=textbook, page_number=40, exercise_number="10", marked_as_removed=False
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
                    textbook=textbook, page_number=40, exercise_number="8", marked_as_removed=False
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
                timing=None,
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

        return (
            model_for_extraction,
            model_for_adaptation,
            textbook,
            pdf_file_range,
            extraction_batch,
            extraction_settings,
            mcq_exercise_class,
        )

    def create_dummy_textbook_with_text_exercise_numbers(self) -> None:
        (
            model_for_extraction,
            model_for_adaptation,
            textbook,
            pdf_file_range,
            extraction_batch,
            extraction_settings,
            mcq_exercise_class,
        ) = self.create_dummy_textbook_with_pdf_range()

        page_42_extraction = self.add(
            extraction.PageExtraction(
                created=textbooks.PageExtractionCreationByTextbook(
                    at=created_at, textbook_extraction_batch=extraction_batch, marked_as_removed=False
                ),
                pdf_file_range=pdf_file_range,
                pdf_page_number=12,  # Page 42 in the textbook
                settings=extraction_settings,
                model=model_for_extraction,
                run_classification=True,
                model_for_adaptation=model_for_adaptation,
                assistant_response=extraction.assistant_responses.SuccessV2(
                    kind="success",
                    version="v2",
                    exercises=[
                        extraction.extracted.ExerciseV2(
                            id="p42_ex5",
                            type="exercice",
                            images=False,
                            type_images="none",
                            properties=extraction.extracted.ExerciseV2.Properties(
                                numero="5",
                                consignes=['Complète avec "le vent" ou "la pluie"'],
                                conseil=None,
                                exemple=None,
                                enonce="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
                                references=None,
                                autre=None,
                            ),
                        ),
                        extraction.extracted.ExerciseV2(
                            id="p42_ex6",
                            type="exercice",
                            images=False,
                            type_images="none",
                            properties=extraction.extracted.ExerciseV2.Properties(
                                numero="6",
                                consignes=['Complète avec "le vent" ou "la pluie"'],
                                conseil=None,
                                exemple=None,
                                enonce="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
                                references=None,
                                autre=None,
                            ),
                        ),
                        extraction.extracted.ExerciseV2(
                            id="p42_exAutoDictée",
                            type="exercice",
                            images=False,
                            type_images="none",
                            properties=extraction.extracted.ExerciseV2.Properties(
                                numero="Auto-dictée",
                                consignes=['Complète avec "le vent" ou "la pluie"'],
                                conseil=None,
                                exemple=None,
                                enonce="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
                                references=None,
                                autre=None,
                            ),
                        ),
                        extraction.extracted.ExerciseV2(
                            id="p42_ex6Texte",
                            type="exercice",
                            images=False,
                            type_images="none",
                            properties=extraction.extracted.ExerciseV2.Properties(
                                numero="Exo identifié par texte / 5",
                                consignes=['Complète avec "le vent" ou "la pluie"'],
                                conseil=None,
                                exemple=None,
                                enonce="a. Les feuilles sont chahutées par ...\nb. Les vitres sont mouillées par ...",
                                references=None,
                                autre=None,
                            ),
                        ),
                    ],
                ),
                timing=None,
            )
        )
        exercise_5_page_42 = self.add(
            adaptation.AdaptableExercise(
                created=extraction.ExerciseCreationByPageExtraction(at=created_at, page_extraction=page_42_extraction),
                location=textbooks.ExerciseLocationTextbook(
                    textbook=textbook, page_number=42, exercise_number="5", marked_as_removed=False
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
                    textbook=textbook, page_number=42, exercise_number="6", marked_as_removed=False
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
                    textbook=textbook, page_number=42, exercise_number="Auto-dictée", marked_as_removed=False
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
                    marked_as_removed=False,
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

        page_42_classification_chunk = self.add(
            classification.ClassificationChunk(
                created=extraction.ClassificationChunkCreationByPageExtraction(
                    at=created_at, page_extraction=page_42_extraction
                ),
                model_for_adaptation=model_for_adaptation,
                timing=None,
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

    def create_dummy_single_pdf_textbook(self) -> None:
        pdf_file = self.add(
            extraction.PdfFile(
                created_by="Patty",
                created_at=created_at,
                sha256="044c5caf34cba74e1e4cb6a498485923a8dbf28b74d414155586f18236da78b4",
                bytes_count=37223,
                pages_count=35,
                known_file_names=["long.pdf"],
            )
        )
        assert isinstance(file_storage.pdf_files, file_storage.file_system_engine.FileSystemStorageEngine)
        os.link(
            os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "e2e-tests", "inputs", "long.pdf"),
            file_storage.pdf_files._make_path("044c5caf34cba74e1e4cb6a498485923a8dbf28b74d414155586f18236da78b4"),
        )

        textbook = self.add(
            textbooks.Textbook(
                created_by="Patty",
                created_at=created_at,
                title="Single-PDF",
                publisher=None,
                year=None,
                isbn=None,
                pages_count=None,
                single_pdf_file=pdf_file,
            )
        )

        model_for_extraction = extraction.llm.DummyModel(provider="dummy", name="dummy-1")
        model_for_adaptation = adaptation.llm.DummyModel(provider="dummy", name="dummy-1")
        pdf_file_range = self.add(
            extraction.PdfFileRange(
                created_by="Patty", created_at=created_at, pdf_file=pdf_file, first_page_number=4, pages_count=2
            )
        )
        extraction_batch = self.add(
            textbooks.TextbookExtractionBatch(
                created_by="Patty",
                created_at=created_at,
                pdf_file_range=pdf_file_range,
                textbook=textbook,
                first_textbook_page_number=7,
                model_for_extraction=model_for_extraction,
                model_for_adaptation=model_for_adaptation,
                marked_as_removed=False,
            )
        )
        extraction_settings = self.add(
            extraction.ExtractionSettings(created_by="Patty", created_at=created_at, prompt="Blah blah blah.")
        )
        self.add(
            extraction.PageExtraction(
                created=textbooks.PageExtractionCreationByTextbook(
                    at=created_at, textbook_extraction_batch=extraction_batch, marked_as_removed=False
                ),
                pdf_file_range=pdf_file_range,
                pdf_page_number=4,
                settings=extraction_settings,
                model=model_for_extraction,
                run_classification=True,
                model_for_adaptation=model_for_adaptation,
                assistant_response=None,
                timing=None,
            )
        )
        self.add(
            extraction.PageExtraction(
                created=textbooks.PageExtractionCreationByTextbook(
                    at=created_at, textbook_extraction_batch=extraction_batch, marked_as_removed=False
                ),
                pdf_file_range=pdf_file_range,
                pdf_page_number=5,
                settings=extraction_settings,
                model=model_for_extraction,
                run_classification=True,
                model_for_adaptation=model_for_adaptation,
                assistant_response=None,
                timing=None,
            )
        )

    def create_dummy_coche_exercise_classes(self) -> None:
        self.create_dummy_branch(name="CocheMot", system_prompt="Blah blah coche mot.")
        self.create_dummy_branch(name="CochePhrase", system_prompt="Blah blah coche phrase.")

    def create_dummy_expression_ecrite_exercise_class(self) -> None:
        self.create_dummy_branch(name="ExpressionEcrite", system_prompt="Blah blah expression écrite.")

    def create_dummy_transforme_mot_exercise_class(self) -> None:
        self.create_dummy_branch(name="TransformeMot", system_prompt="Blah blah transforme mot.")

    def create_dummy_rcimage_exercise_class(self) -> None:
        self.create_dummy_branch(name="RCImage", system_prompt="Blah blah RC image.")

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
                timing=None,
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

    def create_empty_extraction_batch(self) -> None:
        model_for_extraction = extraction.llm.DummyModel(provider="dummy", name="dummy-1")
        model_for_adaptation = adaptation.llm.DummyModel(provider="dummy", name="dummy-1")

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
        settings = self.add(
            extraction.ExtractionSettings(created_by="Patty", created_at=created_at, prompt="Blah blah blah.")
        )
        self.add(
            sandbox.extraction.SandboxExtractionBatch(
                created_by="Patty",
                created_at=created_at,
                pdf_file_range=pdf_file_range,
                settings=settings,
                model=model_for_extraction,
                run_classification=True,
                model_for_adaptation=model_for_adaptation,
            )
        )


def load(session: database_utils.Session, truncate: bool, fixtures: Iterable[str]) -> None:
    creator = FixturesCreator(session)

    available_fixtures = {
        "-".join(name.split("_")[1:]): getattr(creator, name) for name in dir(creator) if name.startswith("create_")
    }

    if truncate:
        database_utils.truncate_all_tables(session)
        file_storage.exercise_images.delete_all()
        file_storage.external_exercises.delete_all()
        file_storage.pdf_files.delete_all()

    for fixture in fixtures:
        available_fixtures[fixture]()
        session.flush()


app = fastapi.FastAPI(database_engine=database_utils.create_engine(settings.DATABASE_URL))


@app.post("/load")
def post_load(fixtures: str, session: database_utils.SessionDependable) -> None:
    load(session, True, [] if fixtures == "" else fixtures.split(","))
