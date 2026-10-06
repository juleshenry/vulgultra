#!/usr/bin/env python3
"""Piedmontese Wikisource, "Dissionari Italian-Piemontèis" → Piedmontese headword, Italian gloss.

The dictionary is a working Italian → Piedmontese glossary kept on
pms.wikisource.org (CC BY-SA 4.0) by its translators, one wiki page per
letter, about 5,100 Italian entries, hand-written in this shape:

    * '''Badare''' (vi): pijesse varda, guardesse da, fé atension; ('''aver cura''') cudì, acudì.
    * '''Carta''' (sf): papé, carta; '''carta bollata:''' carta da bòl, carta bolà; …
    * '''Calice''' (sm): (vaso sacro) càles: (bicchiere) copa, san-a, càles; (di fiori) boton, càles.

It is turned round: every Piedmontese equivalent becomes a headword and the
Italian word it stands under becomes its gloss. A sub-sense in brackets is
kept in the gloss ("Badare (aver cura)"); a bold Italian phrase inside the
entry ("carta bollata") is the gloss of what follows it. Left out, to keep
the table clean: usage examples in square brackets, anything after ">"
(derived words), equivalents longer than four words (paraphrases), and
equivalents with a slash or an unclosed bracket.

    python3 data/sources/glossaries/pms/parse_pmswikisource-dissionari.py
"""

from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw" / "pmswikisource_dissionari_italian_piemonteis"
OUT = HERE / "pmswikisource-dissionari.tsv"

POS_LABEL = re.compile(
    r"^(?:s|sm|sf|smp|sfp|sr|smf|sost|v|vt|vi|vr|vp|ag|agg|av|avv|pp|prep|cong|pron|art|num|escl|inter|espr|loc)"
    r"(?:[.,/ ]+(?:e |o )?(?:s|sm|sf|smp|sfp|v|vt|vi|vr|ag|agg|av|avv|pp|prep|cong|pron|inter)\.?)*\.?$")
REGISTER = re.compile(r"^\((?:fam|fig|volg|pop|lett|ant|scherz|spreg|dial|iron|est|raro|rar|fr|mdd)\.?\)\s*", re.I)


def pos_of(label: str) -> str:
    first = re.split(r"[.,/ ]", label.strip().lower())[0]
    if first in ("s", "sm", "sf", "smp", "sfp", "sr", "smf", "sost"):
        return "noun"
    if first in ("v", "vt", "vi", "vr", "vp"):
        return "verb"
    if first in ("ag", "agg", "pp"):
        return "adj"
    if first in ("av", "avv"):
        return "adv"
    return {"prep": "prep", "cong": "conj", "pron": "pron", "num": "num"}.get(first, "other")


def entry_lines():
    for path in sorted(RAW.glob("*.wiki")):
        if "Usa_e_getta" in path.name:
            continue
        text = path.read_text(encoding="utf-8").replace("﻿", "")
        # Two entries sometimes share a line: "… van.* '''Vantaggio''' (sm): …"
        text = re.sub(r"(?<!\n)\*\s*'''(?=[A-ZÀ-Ý])", "\n* '''", text)
        for line in text.split("\n"):
            line = line.strip()
            if re.match(r"^[*é]\s*'''", line):
                yield re.sub(r"^[*é]\s*", "", line)


def strip_examples(text: str) -> str:
    text = re.sub(r"\[[^\[\]]*\]", " ", text)          # [usage examples]
    text = text.split("[")[0]                            # an unclosed example runs to the end
    return text.split(">")[0]                            # > derived words


def unbold_brackets(text: str) -> str:
    """('''aver cura''') and '''(serbare)''' and '''(del vino):''' → (aver cura), (serbare), (del vino):"""
    text = re.sub(r"'''\s*\(", "(", text)
    text = re.sub(r"\(\s*'''", "(", text)
    text = re.sub(r"\)\s*:?\s*'''\s*:?", "):", text)
    text = re.sub(r"'''\s*\)", ")", text)
    return text


def equivalents(text: str):
    """(equivalent, sub-sense or "") for the comma-separated items of one stretch of an entry.

    A bracket that opens an item — "('predicozzo') rimprocc, arpròcc" — names the
    sub-sense of that item and of the ones after it.
    """
    sense = ""
    for item in text.split(","):
        item = item.strip().strip(".").strip()
        item = REGISTER.sub("", item)
        opening = re.match(r"\(([^()]{1,60})\)\s*:?\s*", item)
        if opening:
            sense = opening.group(1).strip(" :")
            item = REGISTER.sub("", item[opening.end():])
        item = re.sub(r"\s*\([^()]*\)\s*$", "", item).strip()       # trailing note: "fagnan (fr. fainéant)"
        item = item.strip(" .:;")
        if not item or "'''" in item or re.search(r"[()/\[\]=|{}<>:;°…^]|\.\.\.", item):
            continue
        if len(item.split()) > 4 or not re.search(r"[a-zà-ÿ]", item):
            continue
        yield unicodedata.normalize("NFC", re.sub(r"\s+", " ", item)), sense


def parse(line: str):
    """Yield (piedmontese, italian gloss, pos) for one entry line."""
    match = re.match(r"'''(.+?)'''\s*", line)
    if not match:
        return
    head = match.group(1).strip(" :")
    rest = line[match.end():]
    inside = re.match(r"^(.*?)\s*\(([^()]{1,12})\)$", head)      # "'''Passo (sm)'''": the label is inside the bold
    if inside and POS_LABEL.match(inside.group(2).strip().lower()):
        head, rest = inside.group(1).strip(), f"({inside.group(2)}) {rest}"
    # "'''Baccano''' ('''grande''') (sm): …" → a qualifier that belongs to the headword
    qualifier = re.match(r"\(\s*'''([^')]+)'''\s*\)\s*", rest)
    if qualifier:
        head = f"{head} ({qualifier.group(1).strip()})"
        rest = rest[qualifier.end():]
    rest = rest.lstrip(" :;")
    pos = ""
    label = re.match(r"\(([^()]{1,22})\)\s*[:;,.]?\s*", rest)
    if label and POS_LABEL.match(label.group(1).strip().lower()):
        pos = pos_of(label.group(1))
        rest = rest[label.end():]
    if not head or len(head) > 60:
        return
    rest = unbold_brackets(strip_examples(rest))
    rest = re.sub(r":\s*\(", "; (", rest)           # "(vaso sacro) càles: (bicchiere) copa"
    for segment in rest.split(";"):
        segment = segment.strip()
        if not segment:
            continue
        gloss, part = head, pos
        bold = re.match(r"'''(.+?)'''\s*(?:\(([^()]{1,22})\)\s*)?:?\s*", segment)
        if bold:
            # an Italian phrase or derived word with its own equivalents
            gloss = bold.group(1).strip(" :")
            part = pos_of(bold.group(2)) if bold.group(2) and POS_LABEL.match(bold.group(2).strip().lower()) else ""
            segment = segment[bold.end():]
        else:
            bracket = re.match(r"\(([^()]{1,60})\)\s*:?\s*", segment)
            if bracket:
                inner = bracket.group(1).strip(" :")
                if POS_LABEL.match(inner.lower()):
                    part = pos_of(inner)
                elif not REGISTER.match(f"({inner})"):
                    gloss = f"{head} ({inner})"
                segment = segment[bracket.end():]
            elif ":" in segment:
                # "quanto mi dispiace: s’am rincress!" — an Italian phrase, then its equivalents
                left, right = segment.split(":", 1)
                if 0 < len(left.split()) <= 6 and "'''" not in left:
                    gloss, part, segment = left.strip(), "", right
        if not gloss or "'''" in segment:
            # further bold phrases inside the segment: too tangled to pair safely
            segment = segment.split("'''")[0]
        for word, sense in equivalents(segment):
            yield word, (f"{head} ({sense})" if sense and gloss == head else gloss), part


def main() -> None:
    rows, seen = [], set()
    entries = 0
    for line in entry_lines():
        entries += 1
        for word, gloss, pos in parse(line.replace("\u2019\u2019", "''")):
            word, gloss = word.replace("''", "").strip(), re.sub(r"\s+", " ", gloss.replace("''", "")).strip()
            if not word or not gloss or gloss.startswith("(") or gloss.count("(") != gloss.count(")"):
                continue                       # a gloss cut in half by irregular markup
            row = (word, gloss, "it", pos)
            if row not in seen:
                seen.add(row)
                rows.append(row)
    with OUT.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_NONE, escapechar="\\")
        writer.writerow(["headword", "gloss", "gloss_lang", "pos"])
        writer.writerows(rows)
    print(entries, "Italian entries ->", len(rows), "rows,", len({row[0] for row in rows}), "Piedmontese headwords")


if __name__ == "__main__":
    main()
