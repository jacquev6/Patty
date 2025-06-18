from typing import Literal
import json
import textwrap

import PIL.Image

from ...extracted import Exercise
from .base import Model


class DummyModel(Model):
    provider: Literal["dummy"]
    name: Literal["dummy-1", "dummy-2", "dummy-3"]

    def do_extract(self, prompt: str, image: PIL.Image.Image) -> str:
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
                    ).model_dump(),
                    Exercise(
                        id=None,
                        numero="2",
                        consignes=["Recopie uniquement les phrases avec le verbe avoir."],
                        conseil=None,
                        exemple=None,
                        enonce=textwrap.dedent(
                            """\
                            a. Ce chien a mordu son maître*.
                            b. Je rentre à la maison à midi pour déjeuner en famille.
                            c. On a froid dans ce sous-bois ombragé.
                            d. Il pense toujours qu'il a raison.
                            e. Tu joues à chat avec moi ?
                            """
                        ),
                        references=None,
                        autre=None,
                    ).model_dump(),
                ]
            )
