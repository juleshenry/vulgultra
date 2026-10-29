#!/usr/bin/env python3
"""Vocabulaithe Jèrriais-Angliais (Société Jersiaise, Section de la langue Jèrriaise) -> table.

PENDING A LICENCE DECISION: the Section offers raw/vocab.txt as a download
("6,500 terms in text format - downloadable") but states no licence.

The file is Latin-1, one `Jèrriais<TAB>English` pair per line. Headword cells
that list variants with commas (`Âbréhan, Âbra-am, Bram`) are split into one
row per variant; nothing else is changed. Rows whose headword starts with a
capital are kept (the source capitalises names and whole sentences alike).

    python3 parse_sdllj-vocabulaithe-jerriais.py
"""
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows, seen = [], set()
for line in (HERE / "raw" / "vocab.txt").read_text(encoding="latin-1").split("\n"):
    cells = [" ".join(cell.split()) for cell in line.split("\t")]
    if len(cells) != 2 or not all(cells):
        continue
    heads, gloss = cells
    for head in heads.split(","):
        head = unicodedata.normalize("NFC", head.strip())
        if head and (head, gloss) not in seen:
            seen.add((head, gloss))
            rows.append((head, gloss))
with (HERE / "sdllj-vocabulaithe-jerriais.tsv").open("w", encoding="utf-8") as out:
    out.write("headword\tgloss\tgloss_lang\tpos\n")
    for head, gloss in rows:
        out.write(f"{head}\t{gloss}\ten\t\n")
print(f"sdllj-vocabulaithe-jerriais.tsv: {len(rows)} rows, {len({r[0] for r in rows})} headwords")
