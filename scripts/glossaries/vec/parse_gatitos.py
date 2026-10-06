#!/usr/bin/env python3
"""GATITOS (Google, CC BY 4.0) → headword–gloss table for the lect of this folder.

GATITOS is a lexicon of about 4,000 frequent English words and short phrases
translated by hand into low-resource languages. `raw/gatitos_en_{lect}.jsonl`
lists, per English entry, its translations; `raw/gatitos_{lect}_en.jsonl` is
the same pairs indexed from the lect. Both are read and the pairs united.
The source gives no part of speech and names no variety. Spelling and
capitalisation are the source's (it mirrors the English: "Yes" → "Scì").

    python3 data/sources/glossaries/{lect}/parse_gatitos.py
"""

from __future__ import annotations

import csv
import json
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
LECT = HERE.name
RAW = HERE / "raw"


def pairs():
    with (RAW / f"gatitos_en_{LECT}.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            entry = json.loads(line)
            for target in entry["trgs"]:
                yield target, entry["src"]
    with (RAW / f"gatitos_{LECT}_en.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            entry = json.loads(line)
            for target in entry["trgs"]:
                yield entry["src"], target


def main() -> None:
    seen, rows = set(), []
    for head, gloss in pairs():
        head = unicodedata.normalize("NFC", head).strip()
        gloss = gloss.strip()
        if not head or not gloss or "\t" in head or "\t" in gloss or (head, gloss) in seen:
            continue
        seen.add((head, gloss))
        rows.append((head, gloss, "en", ""))
    with (HERE / "gatitos.tsv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_NONE, escapechar="\\")
        writer.writerow(["headword", "gloss", "gloss_lang", "pos"])
        writer.writerows(rows)
    print(LECT, len(rows), "rows,", len({row[0] for row in rows}), "headwords")


if __name__ == "__main__":
    main()
