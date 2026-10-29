#!/usr/bin/env python3
"""Gamba (ed.) 1845, "Vocabolario veneto-toscano" → Venetian headword, Italian gloss.

The four-page glossary closes the "Raccolta di poesie in dialetto veneziano
d'ogni secolo" (Venezia, Cecchini, 1845) and explains the Venetian (city of
Venice) words of the poems. The text is the proofread transcription of the
Venetian Wikisource (`raw/vecwikisource/Raccolta_…p0501–p0504.wiki`, CC BY-SA
4.0; the book itself is in the public domain), where it is a two-column wiki
table:

    ||Amia||Zia
    ||Bagolo||Trastullo; ''farse bagolo'', prendersi gioco d'alcuno

The headword keeps the book's capital initial. Wiki italics are dropped
from the gloss; nothing else is changed. The source gives no part of speech.

    python3 data/sources/glossaries/vec/parse_gamba-1845-vocabolario-veneto-toscano.venexian.py
"""

from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw" / "vecwikisource"
OUT = HERE / "gamba-1845-vocabolario-veneto-toscano.venexian.tsv"
ROW = re.compile(r"^\|(?:width=\"\d+%\")?\|(?P<head>[^|]+)\|\|(?P<gloss>.+)$")


def main() -> None:
    rows = []
    for path in sorted(RAW.glob("Raccolta_di_poesie_in_dialetto_veneziano_1845.djvu.p05*.wiki")):
        for line in path.read_text(encoding="utf-8").split("\n"):
            match = ROW.match(line.strip())
            if not match:
                continue
            head = unicodedata.normalize("NFC", match.group("head").strip())
            gloss = re.sub(r"\s+", " ", match.group("gloss").replace("''", "")).strip()
            if head and gloss:
                rows.append((head, gloss, "it", ""))
    with OUT.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_NONE, escapechar="\\")
        writer.writerow(["headword", "gloss", "gloss_lang", "pos"])
        writer.writerows(rows)
    print(len(rows), "rows")


if __name__ == "__main__":
    main()
