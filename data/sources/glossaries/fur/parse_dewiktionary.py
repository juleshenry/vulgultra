#!/usr/bin/env python3
"""German Wiktionary (Kaikki extract, CC BY-SA 4.0) → headword–gloss tables, German glosses.

`raw/dewiktionary_north_italy.jsonl` holds the entries of the nine northern
lects filtered from the Kaikki extract of de.wiktionary.org (see
`rm/fetch_dewiktionary.py`). This script writes the entries of the lect whose
folder it sits in. Inflected forms ("Plural des Substantivs …") are left out.
The gloss is the German translation the entry gives for the sense when there
is one, otherwise the German definition as written ("der Esel").

For Romansh the German Wiktionary labels every sense with its idioms; one
table is written per idiom (`dewiktionary.vallader.tsv`, …), a sense valid
for several idioms going into each. Proper names get pos "other".

    python3 data/sources/glossaries/{lect}/parse_dewiktionary.py
"""

from __future__ import annotations

import collections
import csv
import json
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
LECT = HERE.name
RAW = HERE / "raw" / "dewiktionary_north_italy.jsonl"
POS = {"noun": "noun", "verb": "verb", "adj": "adj", "adv": "adv", "pron": "pron", "num": "num",
       "prep": "prep", "conj": "conj", "name": "other", "phrase": "other", "intj": "other",
       "article": "other", "particle": "other", "abbrev": "other", "suffix": "other", "prefix": "other"}
IDIOMS = {
    "rumantsch grischun": "rumantsch-grischun", "grischun": "rumantsch-grischun", "rumantsch grischu": "rumantsch-grischun",
    "vallader": "vallader", "vallender": "vallader", "putèr": "puter", "engadinisch": "engadin",
    "sursilvan": "sursilvan", "surselvisch": "sursilvan", "sutsilvan": "sutsilvan", "sutselvisch": "sutsilvan",
    "surmiran": "surmiran", "surmeirisch": "surmiran",
}


def main() -> None:
    tables: dict[str, list[tuple[str, str, str, str]]] = collections.defaultdict(list)
    seen: set[tuple[str, tuple]] = set()
    with RAW.open(encoding="utf-8") as stream:
        for line in stream:
            entry = json.loads(line)
            if entry.get("lang_code") != LECT or "form-of" in (entry.get("tags") or []):
                continue
            head = unicodedata.normalize("NFC", entry.get("word") or "").strip()
            if not head:
                continue
            pos = POS.get(entry.get("pos") or "", "")
            german: dict[str, list[str]] = collections.defaultdict(list)
            for translation in entry.get("translations") or []:
                if translation.get("lang_code") == "de" and translation.get("word"):
                    german[translation.get("sense_index") or ""].append(translation["word"].strip())
            for sense in entry.get("senses") or []:
                if "form-of" in (sense.get("tags") or []) or "no-gloss" in (sense.get("tags") or []):
                    continue
                words = german.get(sense.get("sense_index") or "")
                gloss = ", ".join(dict.fromkeys(words)) if words else "; ".join(sense.get("glosses") or [])
                gloss = " ".join(gloss.split())
                if not gloss:
                    continue
                idioms = sorted({IDIOMS[tag.lower()] for tag in sense.get("raw_tags") or [] if tag.lower() in IDIOMS})
                if LECT != "rm":
                    idioms = [""]
                elif not idioms:
                    idioms = ["unspecified"]
                for idiom in idioms:
                    row = (head, gloss, "de", pos)
                    if (idiom, row) not in seen:
                        seen.add((idiom, row))
                        tables[idiom].append(row)
    for idiom, rows in sorted(tables.items()):
        name = f"dewiktionary.{idiom}.tsv" if idiom else "dewiktionary.tsv"
        with (HERE / name).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_NONE, escapechar="\\")
            writer.writerow(["headword", "gloss", "gloss_lang", "pos"])
            writer.writerows(rows)
        print(name, len(rows), "rows,", len({row[0] for row in rows}), "headwords")


if __name__ == "__main__":
    main()
