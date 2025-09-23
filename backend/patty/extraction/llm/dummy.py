from typing import Literal
import json
import textwrap

import PIL.Image

from ..extracted import Exercise
from .base import Model


class DummyModel(Model):
    provider: Literal["dummy"]
    name: Literal["dummy-1", "dummy-2", "dummy-for-images"]

    def do_extract(self, prompt: str, image: PIL.Image.Image) -> str:
        if self.name == "dummy-for-images":
            return self.do_extract_for_images(prompt, image)
        else:
            return self.do_extract_standard(prompt, image)

    def do_extract_for_images(self, prompt: str, image: PIL.Image.Image) -> str:
        return json.dumps(
            [
                Exercise(
                    id=None,
                    type="exercice",
                    images=False,
                    type_images="none",
                    properties=Exercise.Properties(
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
        else:
            return json.dumps(
                [
                    Exercise(
                        id=None,
                        type="exercice",
                        images=False,
                        type_images="none",
                        properties=Exercise.Properties(
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
                    Exercise(
                        id=None,
                        type="exercice",
                        images=False,
                        type_images="none",
                        properties=Exercise.Properties(
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
