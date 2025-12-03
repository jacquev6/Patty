import csv
import io
import re
import textwrap
import typing
import unittest

import pymupdf


def extract_text_and_styles_from_pdf_page(pdf_page: bytes, page_number: int) -> str:
    csv_file = io.StringIO()
    csv_writer = csv.writer(csv_file, delimiter=";")
    csv_writer.writerow(["phrase", "font_family", "size", "color_hex", "style_tag", "overrides"])

    page = pymupdf.open("pdf", pdf_page)[page_number - 1]
    page_dict = page.get_text("dict")
    assert isinstance(page_dict, dict)

    for block in page_dict.get("blocks", []):
        if block.get("type", 0) != 0:
            continue

        for line in block.get("lines", []):
            spans, texts = [], []

            for span in line.get("spans", []):
                text = span.get("text", "")
                if not text.strip():
                    continue
                spans.append(
                    {
                        "bbox": tuple(span["bbox"]),
                        "font": span.get("font", ""),
                        "size": float(span.get("size", 0.0)),
                        "color": span.get("color", 0),
                        "text": text,
                    }
                )
                texts.append(text)

            if not spans:
                continue

            phrase = " ".join(" ".join(texts).split())
            fam_d, tag_d, size_d, col_d = weighted_dominant_style(spans)

            overrides = []
            words = page.get_text("words")
            assert isinstance(words, list)

            x0 = min(s["bbox"][0] for s in spans)
            y0 = min(s["bbox"][1] for s in spans)
            x1 = max(s["bbox"][2] for s in spans)
            y1 = max(s["bbox"][3] for s in spans)
            lbbox = (x0, y0, x1, y1)

            for (wx0, wy0, wx1, wy1, word, *_rest) in words:
                wbbox = (wx0, wy0, wx1, wy1)
                if rect_intersection_area(lbbox, wbbox) <= 0:
                    continue

                fam_w, tag_w, size_w, col_w = style_for_word_from_spans(wbbox, spans)

                if (
                    (fam_w != fam_d)
                    or (tag_w != tag_d)
                    or abs(size_w - size_d) > 1e-6
                    or (col_w.lower() != col_d.lower())
                ):
                    if word.strip():
                        overrides.append(f"{word}|{fam_w}|{size_w:g}|{col_w}|{tag_w}")

            csv_writer.writerow([phrase, fam_d, f"{size_d:g}", col_d, tag_d, "||".join(overrides) if overrides else ""])

    return csv_file.getvalue()


def to_hex_color(c: int | tuple[float, float, float] | list[float]) -> str:
    if isinstance(c, int):
        return f"#{c:06x}"
    if isinstance(c, (tuple, list)) and len(c) >= 3:
        vals = []
        for x in c[:3]:
            vals.append(int(round(x * 255 if x <= 1 else x)))
        return "#{:02x}{:02x}{:02x}".format(*vals)
    return "#000000"


STYLE_PATTERNS = [
    ("black", ["black", "extrablack", "condblack", "ultrablack"]),
    ("bold", ["bold", "heavy", "strong"]),
    ("semibold", ["semibold", "demibold", "demi"]),
    ("medium", ["medium"]),
    ("regular", ["regular", "book", "roman"]),
    ("light", ["light", "thin", "extralight", "ultralight"]),
]
ITALIC_PATTERNS = ["italic", "oblique"]


def normalize_style(fontname: str) -> typing.Tuple[str, str]:
    base = re.sub(r"^[A-Z]{6}\+", "", fontname or "")
    parts = base.split("-")
    family = parts[0].strip() if parts else base.strip()
    variant = "-".join(parts[1:]).lower() if len(parts) > 1 else base[len(family) :].lower()
    weight = "regular"
    if variant:
        for tag, keys in STYLE_PATTERNS:
            if any(k in variant for k in keys):
                weight = tag
                break
    italic = any(k in variant for k in ITALIC_PATTERNS)
    return family, (weight + ("/italic" if italic else ""))


def rect_intersection_area(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    x0 = max(ax0, bx0)
    y0 = max(ay0, by0)
    x1 = min(ax1, bx1)
    y1 = min(ay1, by1)
    return max(0, x1 - x0) * max(0, y1 - y0)


def style_for_word_from_spans(
    word_bbox: tuple[float, float, float, float], spans: list[typing.Any]
) -> tuple[str, str, float, str]:
    best = None
    best_area = 0.0
    for s in spans:
        area = rect_intersection_area(word_bbox, s["bbox"])
        if area > best_area:
            best_area = area
            fam, style = normalize_style(s.get("font", ""))
            size = float(s.get("size", 0.0))
            color_hex = to_hex_color(s.get("color", 0))
            best = (fam, style, size, color_hex)
    return best or ("", "regular", 0.0, "#000000")


def weighted_dominant_style(spans: list[typing.Any]) -> tuple[str, str, float, str]:
    weights: dict[tuple[str, str, float, str], int] = {}
    for s in spans:
        fam, tag = normalize_style(s.get("font", ""))
        size = float(s.get("size", 0.0))
        col = to_hex_color(s.get("color", 0))
        key = (fam, tag, size, col)
        weights[key] = weights.get(key, 0) + max(1, len(s.get("text", "")))
    return max(weights.items(), key=lambda kv: kv[1])[0]


class ExtractTextAndStylesTestCase(unittest.TestCase):
    maxDiff = None

    def test(self) -> None:
        with open("../frontend/e2e-tests/inputs/test.pdf", "rb") as f:
            pdf_data = f.read()
        text_and_styles = extract_text_and_styles_from_pdf_page(pdf_data, 1)

        self.assertEqual(
            text_and_styles[:843],
            textwrap.dedent(
                """\
                phrase;font_family;size;color_hex;style_tag;overrides\r
                Cherchons;FrankfurterSHOP;13;#ffffff;medium;\r
                6;HypatiaSansPro;11;#ec008c;bold;\r
                Je retiens;FrankfurterSHOP;13;#ffffff;medium;\r
                ●;ZapfDingbatsStd;8;#4352a3;regular;\r
                ● La classe grammaticale d’un mot désigne ce qu’il est.;HypatiaSansPro;13;#4352a3;bold;●||0|#000000|regular||classe|HypatiaSansPro|13|#4352a3|black||grammaticale|HypatiaSansPro|13|#4352a3|black\r
                chercher est un verbe . lune est un nom commun .;HypatiaSansPro;13;#4352a3;bold;chercher|HypatiaSansPro|13|#c40075|bold||verbe.|HypatiaSansPro|13|#4352a3|black||lune|HypatiaSansPro|13|#c40075|bold||nom|HypatiaSansPro|13|#4352a3|black||commun. |HypatiaSansPro|13|#4352a3|black\r
                On dit aussi que c’est la nature du mot.;HypatiaSansPro;13;#4352a3;bold;nature|HypatiaSansPro|13|#4352a3|black\r
                ●;ZapfDingbatsStd;8;#4352a3;regular;\r
                """
            ),
        )
