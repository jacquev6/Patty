from typing import Literal
import json
import textwrap

import PIL.Image

from ..extracted import ExerciseV2, ExerciseV3
from .base import Model


class DummyModel(Model):
    provider: Literal["dummy"]
    name: Literal[
        "dummy-1", "dummy-2", "dummy-for-images", "dummy-for-textually-numbered-exercises", "dummy-for-errors"
    ]

    def do_extract(self, prompt: str, image: PIL.Image.Image) -> str:
        if self.name == "dummy-for-images":
            return self.do_extract_for_images()
        elif self.name == "dummy-for-textually-numbered-exercises":
            return self.do_extract_for_textually_numbered_exercises()
        elif self.name == "dummy-for-errors":
            return self.do_extract_for_errors(prompt, image)
        else:
            return self.do_extract_standard(prompt, image)

    def do_extract_for_images(self) -> str:
        return json.dumps(
            [
                ExerciseV2(
                    id=None,
                    type="exercice",
                    images=False,
                    type_images="none",
                    properties=ExerciseV2.Properties(
                        numero="1",
                        consignes=["Écris les noms représentés par les dessins."],
                        conseil=None,
                        exemple=None,
                        enonce=textwrap.dedent(
                            """\
                            {p1c3}
                            {p1c2}
                            {p1c1}
                            {p1c4}
                            {p1c5}
                            """
                        ),
                        references=None,
                        autre=None,
                    ),
                ).model_dump()
            ]
        )

    def do_extract_for_textually_numbered_exercises(self) -> str:
        return json.dumps(
            [
                ExerciseV2(
                    id=None,
                    type="exercice",
                    images=False,
                    type_images="none",
                    properties=ExerciseV2.Properties(
                        numero="5",
                        consignes=["Instruction 5"],
                        conseil=None,
                        exemple=None,
                        enonce="Statement 5",
                        references=None,
                        autre=None,
                    ),
                ).model_dump(),
                ExerciseV2(
                    id=None,
                    type="exercice",
                    images=False,
                    type_images="none",
                    properties=ExerciseV2.Properties(
                        numero="Not a number",
                        consignes=["Instruction Not a number"],
                        conseil=None,
                        exemple=None,
                        enonce="Statement Not a number",
                        references=None,
                        autre=None,
                    ),
                ).model_dump(),
                ExerciseV2(
                    id=None,
                    type="exercice",
                    images=False,
                    type_images="none",
                    properties=ExerciseV2.Properties(
                        numero="6",
                        consignes=["Instruction 6"],
                        conseil=None,
                        exemple=None,
                        enonce="Statement 6",
                        references=None,
                        autre=None,
                    ),
                ).model_dump(),
            ]
        )

    def do_extract_for_errors(self, prompt: str, image: PIL.Image.Image) -> str:
        color = image.getpixel((image.size[0] // 2, image.size[1] // 2))
        if color == (255, 0, 0):
            return "Not JSON"
        elif color == (0, 128, 0):
            return "{}"
        elif color == (0, 0, 255):
            raise Exception("Simulated unknown error")
        else:
            return self.do_extract_standard(prompt, image)

    def do_extract_standard(self, prompt: str, image: PIL.Image.Image) -> str:
        def raise_exception() -> str:
            raise Exception("Unknown error from DummyModel")

        special_response = {
            "Not JSON": lambda: "This is not JSON.",
            "Invalid JSON": lambda: "{}",
            "Unknown error": raise_exception,
        }.get(prompt)

        if special_response is not None:
            return special_response()
        elif '"statement"' in prompt:
            return json.dumps(
                [
                    ExerciseV3(
                        id=None,
                        type="exercise",
                        images=False,
                        image_type="none",
                        properties=ExerciseV3.Properties(
                            number="1",
                            instruction="Recopie les deux mots de chaque phrase qui se prononcent de la même façon.",
                            labels=[],
                            hint=None,
                            example=None,
                            statement=textwrap.dedent(
                                """\
                                a. Il a gagné le gros lot à la kermesse des écoles.
                                b. À la fin du film, il y a une bonne surprise.
                                c. Il a garé sa voiture dans le parking, à droite de la nôtre.
                                d. Il m'a invité à venir chez lui.
                                e. Mon oncle a un vélo à vendre.
                                """
                            ),
                            references=None,
                        ),
                    ).model_dump(),
                    ExerciseV3(
                        id=None,
                        type="exercise",
                        images=False,
                        image_type="none",
                        properties=ExerciseV3.Properties(
                            number="2",
                            instruction="Réponds par vrai ou faux.",
                            labels=[],
                            hint=None,
                            example=None,
                            statement=textwrap.dedent(
                                """\
                                a. Bleu est une couleur
                                b. Un triangle a quatre côtés
                                """
                            ),
                            references=None,
                        ),
                    ).model_dump(),
                ]
            )
        else:
            return json.dumps(
                [
                    ExerciseV2(
                        id=None,
                        type="exercice",
                        images=False,
                        type_images="none",
                        properties=ExerciseV2.Properties(
                            numero="1",
                            consignes=["Recopie les deux mots de chaque phrase qui se prononcent de la même façon."],
                            conseil=None,
                            exemple=None,
                            enonce=textwrap.dedent(
                                """\
                                a. Il a gagné le gros lot à la kermesse des écoles.
                                b. À la fin du film, il y a une bonne surprise.
                                c. Il a garé sa voiture dans le parking, à droite de la nôtre.
                                d. Il m'a invité à venir chez lui.
                                e. Mon oncle a un vélo à vendre.
                                """
                            ),
                            references=None,
                            autre=None,
                        ),
                    ).model_dump(),
                    ExerciseV2(
                        id=None,
                        type="exercice",
                        images=False,
                        type_images="none",
                        properties=ExerciseV2.Properties(
                            numero="2",
                            consignes=["Réponds par vrai ou faux."],
                            conseil=None,
                            exemple=None,
                            enonce=textwrap.dedent(
                                """\
                                a. Bleu est une couleur
                                b. Un triangle a quatre côtés
                                """
                            ),
                            references=None,
                            autre=None,
                        ),
                    ).model_dump(),
                ]
            )
