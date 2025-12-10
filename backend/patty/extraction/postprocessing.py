# Copyright 2025 Mohamed-Amine Lasheb <mohamed-amine.lasheb@lecnam.net>
# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

import re
import typing
import unittest


def cleanup_slashes(t: str, /) -> str:
    """
    Nettoyage chirurgical des erreurs de backslashs générées par le LLM
    AVANT de tenter de réparer la structure JSON.
    """
    assert not t.startswith("```"), "Le texte ne doit plus contenir de balises Markdown"
    assert not t.endswith("```"), "Le texte ne doit plus contenir de balises Markdown"
    assert t == t.strip(), "Le texte ne doit plus contenir d'espaces superflus aux extrémités"

    # -----------------------------------------------------------
    # RÉPARATIONS DES BACKSLASHS (Ordre important)
    # -----------------------------------------------------------

    # A. Sauts de ligne : \\n devient \n
    # Le LLM écrit souvent 2 chars (\ + n), on veut le caractère de contrôle.
    t = t.replace("\\\\n", "\\n")

    # B. Cas critique des guillemets avec 3 backslashs : \\\" devient \"
    # C'est ton erreur actuelle : \color{\\\" -> le parser voit 3 barres.
    # On remplace par \" (1 barre + guillemet) pour que ce soit un guillemet échappé valide.
    t = t.replace('\\\\\\"', '\\"')

    # C. Cas critique des guillemets avec 2 backslashs : \\" devient \"
    # Cela arrive quand le LLM essaie d'échapper le backslash devant le guillemet.
    # Dans une string JSON, \\" signifie "Backslash littéral + Fin de string".
    # Cela CASSE le json. On remplace par \" (Guillemet échappé).
    t = t.replace('\\\\"', '\\"')

    # D. LaTeX général : \\\\bf devient \\bf (4 barres -> 2 barres)
    # Pour avoir un seul backslash littéral en JSON, il en faut 2 dans le code source.
    # Si le LLM en met 4, on réduit à 2.
    t = t.replace("\\\\\\\\", "\\\\")

    # E. Nettoyage résiduel (3 barres -> 2 barres)
    # Au cas où il reste des \\\bf
    t = t.replace("\\\\\\", "\\\\")

    return t


def remove_styles(text: str) -> str:
    # Regular expressions can't handle nested styles, so a "real" parser is needed.

    def find_annotation_end(s: str) -> int | None:
        assert s.startswith("{"), s

        depth = 0
        for index in range(0, len(s)):
            if s[index] == "{":
                depth += 1
            elif s[index] == "}":
                depth -= 1
            if depth == 0:
                return index

        return None

    def remove_styles(s: str) -> typing.Iterable[str]:
        index = 0
        while True:
            annotation_begin_index = s.find("\\", index)
            if annotation_begin_index == -1:
                yield s[index:]
                break
            else:
                yield s[index:annotation_begin_index]
                if command_match := re.match(r"^\\(bf|it|color){", s[annotation_begin_index:]):
                    index = annotation_begin_index + len(command_match.group(0))
                    annotation_end_delta = find_annotation_end(s[index - 1 :])
                    if annotation_end_delta is None:
                        yield s[annotation_begin_index:]
                        break
                    else:
                        annotation_end_index = index + annotation_end_delta
                        if command_match.group(1) == "color":
                            # Ad-hoc removal of the second argument of \color
                            if color_match := re.match(
                                r"^(.*),\s*#[0-9a-fA-F]{3,6}$", s[index : annotation_end_index - 1]
                            ):
                                yield from remove_styles(color_match.group(1).strip('"'))
                            else:
                                assert False
                        else:
                            yield from remove_styles(s[index : annotation_end_index - 1])
                        index = annotation_end_index
                else:
                    yield s[annotation_begin_index]
                    index = annotation_begin_index + 1

    return "".join(remove_styles(text))


class RemoveStylesTestCase(unittest.TestCase):
    def test_remove_simple_styles(self) -> None:
        self.assertEqual(
            remove_styles(r"alpha bravo charlie delta echo foxtrot golf hotel"),
            r"alpha bravo charlie delta echo foxtrot golf hotel",
        )
        self.assertEqual(
            remove_styles(r"alpha bravo \bf{charlie} delta echo foxtrot golf hotel"),
            r"alpha bravo charlie delta echo foxtrot golf hotel",
        )
        self.assertEqual(
            remove_styles(r"\bf{alpha bravo charlie delta echo foxtrot golf hotel}"),
            r"alpha bravo charlie delta echo foxtrot golf hotel",
        )
        self.assertEqual(
            remove_styles(r"alpha bravo charlie delta echo \it{foxtrot} golf hotel"),
            r"alpha bravo charlie delta echo foxtrot golf hotel",
        )
        self.assertEqual(
            remove_styles(r"alpha bravo \bf{charlie} delta echo foxtrot \it{golf} hotel"),
            r"alpha bravo charlie delta echo foxtrot golf hotel",
        )
        self.assertEqual(
            remove_styles(r"alpha bravo \bf{charlie} delta echo" + "\n" + r"foxtrot \it{golf} hotel"),
            r"alpha bravo charlie delta echo" + "\n" + r"foxtrot golf hotel",
        )

    def test_remove_nested_styles(self) -> None:
        self.assertEqual(
            remove_styles(r"alpha bravo \bf{\it{charlie}} delta echo foxtrot golf hotel"),
            r"alpha bravo charlie delta echo foxtrot golf hotel",
        )
        self.assertEqual(
            remove_styles(r"alpha \it{bravo \bf{charlie delta echo} foxtrot} golf hotel"),
            r"alpha bravo charlie delta echo foxtrot golf hotel",
        )

    def test_dont_touch_broken_inputs(self) -> None:
        self.assertEqual(
            remove_styles(r"alpha bravo \br{charlie delta echo foxtrot golf hotel"),
            r"alpha bravo \br{charlie delta echo foxtrot golf hotel",
        )
        self.assertEqual(
            remove_styles(r"alpha bravo charlie} delta echo \it{foxtrot} golf hotel"),
            r"alpha bravo charlie} delta echo foxtrot golf hotel",
        )
        self.assertEqual(
            remove_styles(r"alpha bravo \it{charlie} delta echo foxtrot} golf hotel"),
            r"alpha bravo charlie delta echo foxtrot} golf hotel",
        )
        self.assertEqual(
            remove_styles(r"alpha bravo \{charlie} delta echo {foxtrot} golf hotel"),
            r"alpha bravo \{charlie} delta echo {foxtrot} golf hotel",
        )
        self.assertEqual(
            remove_styles(r"alpha bravo \it{charlie {delta echo foxtrot golf hotel}"),
            r"alpha bravo \it{charlie {delta echo foxtrot golf hotel}",
        )
        self.assertEqual(
            remove_styles(r"alpha bravo \ it{charlie} delta echo foxtrot golf hotel"),
            r"alpha bravo \ it{charlie} delta echo foxtrot golf hotel",
        )
        self.assertEqual(
            remove_styles(r"alpha bravo \it {charlie} delta echo foxtrot golf hotel"),
            r"alpha bravo \it {charlie} delta echo foxtrot golf hotel",
        )

    def test_dont_touch_unknown_commands(self) -> None:
        self.assertEqual(
            remove_styles(r"alpha bravo \unknown{charlie} delta echo foxtrot golf hotel"),
            r"alpha bravo \unknown{charlie} delta echo foxtrot golf hotel",
        )

    def test_remove_styles_nested_in_unknown_commands(self) -> None:
        self.assertEqual(
            remove_styles(r"alpha bravo \cmd{charlie \bf{delta} echo} foxtrot golf hotel"),
            r"alpha bravo \cmd{charlie delta echo} foxtrot golf hotel",
        )

    def test_remove_simple_color(self) -> None:
        self.assertEqual(
            remove_styles(r"""alpha bravo charlie \color{"delta", #fF0} echo foxtrot golf hotel"""),
            r"alpha bravo charlie delta echo foxtrot golf hotel",
        )
        self.assertEqual(
            remove_styles(r"""alpha bravo charlie \color{"delta", #faFa01} echo foxtrot golf hotel"""),
            r"alpha bravo charlie delta echo foxtrot golf hotel",
        )
        self.assertEqual(
            remove_styles(r"""alpha bravo charlie \color{delta echo, #faFa01} foxtrot golf hotel"""),
            r"alpha bravo charlie delta echo foxtrot golf hotel",
        )

    def test_remove_nested_color(self) -> None:
        self.assertEqual(
            remove_styles(r"""alpha bravo \color{"charlie \bf{delta} echo", #fF0} foxtrot golf hotel"""),
            r"alpha bravo charlie delta echo foxtrot golf hotel",
        )
        self.assertEqual(
            remove_styles(r"""alpha \color{"bravo \it{charlie} delta", #faFa01} echo foxtrot golf hotel"""),
            r"alpha bravo charlie delta echo foxtrot golf hotel",
        )
        self.assertEqual(
            remove_styles(r"""alpha \color{\it{bravo}, #faFa01} charlie delta echo foxtrot golf hotel"""),
            r"alpha bravo charlie delta echo foxtrot golf hotel",
        )
        self.assertEqual(
            remove_styles(r"""alpha \it{\color{bravo, #faFa01}} charlie delta echo foxtrot golf hotel"""),
            r"alpha bravo charlie delta echo foxtrot golf hotel",
        )
