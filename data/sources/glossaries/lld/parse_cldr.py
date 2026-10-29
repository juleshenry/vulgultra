#!/usr/bin/env python3
"""Unicode CLDR (Unicode License v3) → headword–gloss table for the lect of this folder, English glosses.

CLDR is the locale database behind operating systems. Two parts are read,
each aligned with the English file by its key, so every pair is the lect's
and the English name of the same thing:

  * `raw/cldr_annotations_{lect}.xml` (where the lect has one): the spoken
    name of each emoji and symbol ("🐑" → nursa / ewe);
  * `raw/cldr_main_{lect}.xml`: names of languages, scripts, countries and
    regions, months, weekdays, eras, date fields ("yesterday", "week") and
    units of measurement.

Entries the lect file merely copies from English or leaves as a code are
skipped (same string as the English one is kept: Africa is Africa).
The source gives no part of speech and names no variety.

    python3 data/sources/glossaries/{lect}/parse_cldr.py
"""

from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path
from xml.etree import ElementTree

HERE = Path(__file__).resolve().parent
LECT = HERE.name
RAW = HERE / "raw"
# XPath-like element chains of the main file whose text is a name; keyed by their attributes.
MAIN = (
    "localeDisplayNames/languages/language",
    "localeDisplayNames/scripts/script",
    "localeDisplayNames/territories/territory",
    "dates/calendars/calendar[@type='gregorian']/months/monthContext[@type='format']/monthWidth[@type='wide']/month",
    "dates/calendars/calendar[@type='gregorian']/days/dayContext[@type='format']/dayWidth[@type='wide']/day",
    "dates/calendars/calendar[@type='gregorian']/quarters/quarterContext[@type='format']/quarterWidth[@type='wide']/quarter",
    "dates/calendars/calendar[@type='gregorian']/eras/eraNames/era",
    "dates/calendars/calendar[@type='gregorian']/dayPeriods/dayPeriodContext[@type='format']/dayPeriodWidth[@type='wide']/dayPeriod",
    "dates/fields/field/displayName",
    "dates/fields/field/relative",
    "units/unitLength[@type='long']/unit/displayName",
)


def key(element, parents) -> tuple:
    """Element chain with its attributes, minus the ones that do not identify (draft status)."""
    return tuple((node.tag, tuple(sorted((name, value) for name, value in node.attrib.items() if name != "draft")))
                 for node in parents + [element])


def abbreviated(name: tuple) -> bool:
    """Date fields come in full, short and narrow ("wk.") variants: only the full ones are words."""
    return any(value.endswith(("-short", "-narrow")) for _, attributes in name for _, value in attributes)


def walk(root, path: str):
    """(key, text) for every element matched by the path, with the attributes of its ancestors in the key."""
    steps = path.split("/")

    def descend(node, remaining, parents):
        if not remaining:
            if node.text and node.text.strip() and "alt" not in node.attrib and "↑" not in node.text:
                yield key(node, parents), node.text.strip()
            return
        for child in node.findall(remaining[0]):
            yield from descend(child, remaining[1:], parents + [node] if node is not root else [])

    yield from descend(root, steps, [])


def clean(text: str) -> str:
    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", text)).strip()


def main() -> None:
    rows, seen = [], set()

    def add(head: str, gloss: str) -> None:
        head, gloss = clean(head), clean(gloss)
        if not head or not gloss or re.fullmatch(r"[\W\d_]+", head) or (head, gloss) in seen:
            return
        seen.add((head, gloss))
        rows.append((head, gloss, "en", ""))

    annotations = RAW / f"cldr_annotations_{LECT}.xml"
    if annotations.is_file():
        english = {node.get("cp"): node.text for node in
                   ElementTree.parse(RAW / "cldr_annotations_en.xml").getroot().iter("annotation") if node.get("type") == "tts"}
        for node in ElementTree.parse(annotations).getroot().iter("annotation"):
            if node.get("type") == "tts" and node.text and english.get(node.get("cp")) and "↑" not in node.text:
                add(node.text, english[node.get("cp")])
    lect_root = ElementTree.parse(RAW / f"cldr_main_{LECT}.xml").getroot()
    english_root = ElementTree.parse(RAW / "cldr_main_en.xml").getroot()
    for path in MAIN:
        english = dict(walk(english_root, path))
        for name, text in walk(lect_root, path):
            if name in english and not abbreviated(name):
                add(text, english[name])
    with (HERE / "cldr.tsv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_NONE, escapechar="\\")
        writer.writerow(["headword", "gloss", "gloss_lang", "pos"])
        writer.writerows(rows)
    print(LECT, len(rows), "rows,", len({row[0] for row in rows}), "headwords")


if __name__ == "__main__":
    main()
