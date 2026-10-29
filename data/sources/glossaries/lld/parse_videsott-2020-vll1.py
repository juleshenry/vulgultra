#!/usr/bin/env python3
"""Videsott (ed.) 2020, Vocabolar dl ladin leterar 1 → one headword–gloss table per Ladin idiom.

The PDF is born digital (no OCR), so the entry structure is read from the
fonts:

    amalé Ⓔ nordit. amalà ‹ AD + MALE HABITUS (GsellMM) 6 1763 amarè …      Arial-Bold 10.5: lemma
    gad. amaré mar. amaré Badia amarè grd. amalà fas. malà fod. malé, amalé †   Helvetica-Narrow: idiom, Arial: its forms
    agg. Ⓜ amalés, amaleda, amaledes                                          Times-Bold: part of speech
    che è colpito da una malattia (gad. B 1763; …, grd. A 1879; …)            Times-BoldItalic: definition; idioms of the sense
    Ⓘ ammalato Ⓓ krank ◇ a) …                                                 the Italian and the German equivalent

A row is written for an idiom's form only under the senses the dictionary
records for that idiom (the list in brackets after the definition); the
valley sub-varieties (mar., Badia under gad.; caz., bra., moe. under fas.;
col. under fod.) count as covered by their valley. Forms marked † (obsolete)
are kept without the dagger. Left out: phrases (◆ …), which the dictionary
gives only in the lemma's spelling, not per idiom; senses of a past
participle used as adjective or noun ("p.p. come agg."), because the idiom
line holds the infinitive; and entries with no line of idiom forms.
Place and personal names (topon., antrop.) get pos "other".

    python3 data/sources/glossaries/lld/parse_videsott-2020-vll1.py
"""

from __future__ import annotations

import collections
import csv
import re
import unicodedata
from pathlib import Path

import fitz

HERE = Path(__file__).resolve().parent
PDF = HERE / "raw" / "videsott_2020_vll1_978-88-6046-168-1.pdf"
FIRST, LAST = 37, 1127            # PDF page indexes of the dictionary proper (A–Z); the reverse indexes follow
SLUG = "videsott-2020-vll1"

# Idiom label in the book → file-name part.
IDIOMS = {
    "gad.": "badiot", "mar.": "mareo", "Badia": "badia", "grd.": "gherdeina",
    "fas.": "fascian", "caz.": "cazet", "bra.": "brach", "moe.": "moenat",
    "fod.": "fodom", "col.": "col", "amp.": "anpezan", "LD": "ladin-dolomitan", "MdR": "micura-de-ru",
}
PARENT = {"mar.": "gad.", "Badia": "gad.", "caz.": "fas.", "bra.": "fas.", "moe.": "fas.", "col.": "fod."}
LABEL = re.compile(r"(?<![\w.])(gad\.|mar\.|Badia|grd\.|fas\.|caz\.|bra\.|moe\.|fod\.|col\.|amp\.|LD|MdR)(?![\w])")
POS = (
    (re.compile(r"come agg"), "adj"), (re.compile(r"come s\."), "noun"),
    (re.compile(r"^(s\.|sost)"), "noun"), (re.compile(r"^(v\.|verbo)"), "verb"), (re.compile(r"^agg"), "adj"),
    (re.compile(r"^avv"), "adv"), (re.compile(r"^pron"), "pron"), (re.compile(r"^num"), "num"),
    (re.compile(r"^prep"), "prep"), (re.compile(r"^cong"), "conj"),
)


def kind(font: str, size: float) -> str:
    if font.endswith("Arial-BoldMT"):
        return "HEAD" if abs(size - 10.5) < 0.4 else "X"
    if font.endswith("Helvetica-Narrow"):
        return "IDIOM"
    if font.endswith("ArialUnicodeMS"):
        return "MARK"
    if font.endswith("ArialMT"):
        return "ARIAL"
    if font.endswith("TimesNewRomanPS-BoldMT"):
        return "POS"
    if "TimesNewRomanPS-BoldItal" in font:
        return "DEF"
    if font.endswith("TimesNewRomanPSMT"):
        return "ROMAN"
    return "X"


def tokens():
    """(kind, text, starts_line) for every span of the dictionary, in reading order."""
    document = fitz.open(PDF)
    for number in range(FIRST, LAST + 1):
        page = document[number]
        middle = page.rect.width / 2 - 45
        lines = []
        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                x, y = line["bbox"][0], line["bbox"][1]
                if y < 45 or not line["spans"]:
                    continue                      # running head and page number
                lines.append((x >= middle, round(y), x, line["spans"]))
        lines.sort(key=lambda row: (row[0], row[1], row[2]))
        for _, _, _, spans in lines:
            first = True
            for span in spans:
                text = span["text"].replace("­", "").replace("\t", " ")
                if not text.strip():
                    continue
                yield kind(span["font"], span["size"]), text, first
                first = False
            yield "EOL", "", False


def joined(parts: list[tuple[str, bool]]) -> str:
    """Join text pieces; a piece that ends a line with a hyphen is glued to the next one."""
    out = ""
    for text, line_end in parts:
        out += text
        if line_end:
            if out.endswith("-") and len(out) > 1 and out[-2].isalpha():
                out = out[:-1]
            elif not out.endswith(" "):
                out += " "
    return re.sub(r"\s+", " ", out).strip()


def pos_of(label: str) -> str:
    label = label.strip().lower()
    if not label:
        return ""
    for pattern, name in POS:
        if pattern.search(label):
            return name
    return "other"


def clean_gloss(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip(" ;,.")
    return text


def clean_form(text: str) -> str:
    text = unicodedata.normalize("NFC", text.replace("†", "")).strip(" ;.")
    return re.sub(r"\s+", " ", text)


def entries() -> list[dict]:
    """Every lemma: {lemma, forms: {idiom: [text pieces]}, senses: [{pos, idioms, it, de, phrase}]}."""
    stream = list(tokens())
    total = len(stream)
    found: list[dict] = []
    entry: dict | None = None
    mode = "none"          # head | forms | pos | body | it | de
    buffer: list[tuple[str, bool]] = []
    sense: dict | None = None
    idiom = ""
    pos = ""
    phrase = False
    since_def: list[str] = []     # Arial text since the last definition: holds the idioms of the sense

    def close_sense() -> None:
        nonlocal sense, mode, buffer
        if sense is not None and entry is not None:
            if mode == "it":
                sense["it"] = joined(buffer)
            elif mode == "de":
                sense["de"] = joined(buffer)
            if sense["it"] or sense["de"]:
                entry["senses"].append(sense)
        sense = None
        buffer = []
        if mode in ("it", "de"):
            mode = "body"

    def open_sense() -> dict:
        return {"pos": pos, "idioms": set(LABEL.findall(" ".join(since_def))), "it": "", "de": "", "phrase": phrase}

    index = 0
    while index < total:
        token, text, starts = stream[index]
        if token == "EOL":
            index += 1
            continue
        line_end = index + 1 < total and stream[index + 1][0] == "EOL"
        if token == "HEAD" and starts:
            close_sense()
            ahead, line_text = index, ""
            while ahead < total and stream[ahead][0] != "EOL":
                line_text += stream[ahead][1]
                ahead += 1
            if "↦" in line_text:
                # Cross-reference "form (idiom) ↦ lemma."; it can wrap onto a second line.
                while ahead + 1 < total and not line_text.rstrip().endswith(".") and len(line_text) < 400:
                    ahead += 1
                    while ahead < total and stream[ahead][0] != "EOL":
                        line_text += stream[ahead][1]
                        ahead += 1
                index = ahead + 1
                continue
            if entry is not None:
                found.append(entry)
            entry = {"lemma": clean_form(text), "forms": collections.OrderedDict(), "senses": []}
            mode, pos, phrase, idiom, since_def = "head", "", False, "", []
            index += 1
            continue
        if entry is None:
            index += 1
            continue
        if token == "HEAD" and mode == "head":
            entry["lemma"] = clean_form(entry["lemma"] + text)       # lemma continued in a second span
            index += 1
            continue
        if mode == "head" and token != "HEAD":
            mode = "body"
        if token == "IDIOM":
            close_sense()
            label = text.strip()
            if label in IDIOMS and not entry["senses"] and not pos:
                mode, idiom = "forms", label
                entry["forms"].setdefault(idiom, [])
            index += 1
            continue
        if mode == "forms":
            if token == "ARIAL":
                pieces = entry["forms"][idiom]
                if pieces and pieces[-1].endswith("\x00"):      # the form was hyphenated at the line end
                    pieces[-1] = pieces[-1][:-2] + text.lstrip()
                else:
                    pieces.append(text)
                if line_end and re.search(r"\w-\s*$", text):
                    pieces[-1] = pieces[-1].rstrip() + "\x00"
                index += 1
                continue
            if token == "ROMAN":
                if "," in text:
                    entry["forms"][idiom].append(",")
                index += 1
                continue
            mode = "body"
        if token == "POS":
            close_sense()
            label = text.strip()
            if re.match(r"^[a-zA-Z]", label):
                pos = (pos + " " + label).strip() if mode == "pos" else label
                mode = "pos"
                phrase = False
            index += 1
            continue
        if mode == "pos":
            mode = "body"
        if token == "DEF":
            close_sense()
            since_def = []
            index += 1
            continue
        if token == "MARK":
            if "◆" in text:
                close_sense()
                phrase = True
                since_def = []
            elif "Ⓘ" in text:
                close_sense()
                sense = open_sense()
                mode, buffer = "it", []
            elif "Ⓓ" in text:
                if mode == "it" and sense is not None:
                    sense["it"] = joined(buffer)
                else:
                    close_sense()
                    sense = open_sense()
                mode, buffer = "de", []
            else:
                close_sense()                  # ◇ examples, ☝ references, Ⓜ morphology, sigla
            index += 1
            continue
        if token == "ARIAL":
            if mode in ("it", "de"):
                buffer.append((text, line_end))
            else:
                since_def.append(text)
            index += 1
            continue
        if mode in ("it", "de") and not (token == "ROMAN" and not text.strip(" ,;")):
            close_sense()
        index += 1
    close_sense()
    if entry is not None:
        found.append(entry)
    return found


def forms_of(pieces: list[str]) -> list[str]:
    forms, current = [], ""
    for piece in pieces:
        if piece == ",":
            forms.append(current)
            current = ""
        else:
            for index, part in enumerate(piece.split(",")):
                if index:
                    forms.append(current)
                    current = ""
                current = f"{current} {part}" if current.strip() and not current.endswith("\x00") else current + part
    forms.append(current)
    out = []
    for form in forms:
        form = clean_form(form.replace("\x00", ""))
        halves = form.split()
        if len(halves) == 2 and halves[0] == halves[1]:
            form = halves[0]                         # the same form printed twice
        if form and form not in out and not re.search(r"[()\d]", form):
            out.append(form)
    return out


def main() -> None:
    rows: dict[str, list[tuple[str, str, str, str]]] = collections.defaultdict(list)
    seen: dict[str, set] = collections.defaultdict(set)
    stats = collections.Counter()
    for entry in entries():
        stats["lemmas"] += 1
        if not entry["forms"]:
            stats["lemmas without idiom forms"] += 1
            continue
        if not entry["senses"]:
            stats["lemmas without glossed senses"] += 1
        for sense in entry["senses"]:
            if sense["phrase"]:
                stats["phrases skipped"] += 1
                continue
            if "p.p." in sense["pos"]:
                # a past participle used as adjective or noun: the idiom line gives the infinitive, not its form
                stats["participle senses skipped"] += 1
                continue
            part = pos_of(sense["pos"])
            for idiom, pieces in entry["forms"].items():
                if idiom not in sense["idioms"] and PARENT.get(idiom) not in sense["idioms"]:
                    continue
                for form in forms_of(pieces):
                    for language in ("it", "de"):
                        gloss = clean_gloss(sense[language])
                        if not gloss:
                            continue
                        row = (form, gloss, language, part)
                        if row not in seen[idiom]:
                            seen[idiom].add(row)
                            rows[idiom].append(row)
    for idiom, name in IDIOMS.items():
        path = HERE / f"{SLUG}.{name}.tsv"
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_NONE, escapechar="\\")
            writer.writerow(["headword", "gloss", "gloss_lang", "pos"])
            writer.writerows(rows.get(idiom, []))
        heads = len({row[0] for row in rows.get(idiom, [])})
        print(f"{name:16s} {len(rows.get(idiom, [])):6d} rows  {heads:5d} headwords")
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
