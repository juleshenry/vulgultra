#!/usr/bin/env python3
"""Decorde, Dictionnaire du patois du pays de Bray (1852) -> headword/gloss table.

Source: raw/pg51005.txt, the Project Gutenberg / Distributed Proofreaders
Canada transcription (eBook #51005). Norman of the Pays de Bray
(Seine-Maritime); the trailing P. / H.-N. / B.-N. marks only say the word
also occurs in Picardy, Upper or Lower Normandy and are not carried over.

An entry is a paragraph `HEADWORD[ (particle)], gloss. Ex.: example. P.`
Headwords are printed in capitals and are lower-cased here; no letter is
otherwise changed. A particle in parentheses stays with the headword as
printed (`fion (avoir le)`), except the reflexive `(se)` / `(s')`, which is
dropped. The gloss is the text between the first comma and the first full
stop; examples, etymologies and cross-references are cut. Entries that only
describe usage in a sentence ("FIN. Mot expletif qui...") are left out.

    python3 parse_decorde-1852-bray.py
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw" / "pg51005.txt"
OUT = HERE / "decorde-1852-bray.tsv"

UP = "A-ZÀ-ÖØ-ÞŒÆ"
HEAD = re.compile(rf"^([{UP}][{UP}'’\- ]*?)\s*(\([^)]*\))?\s*,\s+(.+)$")
ABBREVIATIONS = r"(?:\b(?:M|MM|Mme|St|Ste|etc|Ex|Voy|V|p)|[A-Z])$"
LOCALITY = r"(?:[\s,]+(?:P|H\.-N|B\.-N)\.?)+$"


def paragraphs() -> list[str]:
    lines = RAW.read_text(encoding="utf-8").split("\n")
    start = next(i for i, line in enumerate(lines) if line.strip() == "A" and i > 1400)
    end = next(i for i, line in enumerate(lines) if line.strip() == "TABLE" and i > start)
    body = "\n".join(lines[start:end])
    return [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def first_sentence(body: str) -> str:
    position = 0
    while True:
        found = re.search(r"\.(?=\s|$)", body[position:])
        if not found:
            return body
        end = position + found.start()
        if re.search(ABBREVIATIONS, body[:end]):
            position = end + 1
            continue
        return body[:end]


def main() -> None:
    rows, seen = [], set()
    for paragraph in paragraphs():
        found = HEAD.match(paragraph)
        if not found:
            continue
        term, particle, body = found.group(1).strip(), found.group(2), found.group(3)
        if re.match(r"(?i)^(voy|v)\b\.?", body):
            continue
        terms = [term]
        while True:                # further headwords: SÈT, SÉS, sel
            more = re.match(rf"^([{UP}][{UP}'’\-]+),\s+(.+)$", body)
            if not more:
                break
            terms.append(more.group(1))
            body = more.group(2)
        body = re.split(r"[,.;]?\s+(?:P|H\.-N|B\.-N)\.(?=[\s,]|$)", body)[0]
        gloss = first_sentence(body)
        gloss = re.split(r"\s*(?:,|;)?\s*(?:Ex\b|Voy\b|V\. _)", gloss)[0]
        gloss = re.split(r"\s*[;,]\s*(?:du (?:vieux )?(?:latin|grec|celtique|français|mot)|vient d|de _|en anglais|en (?:vieux )?français)", gloss)[0]
        gloss = re.sub(LOCALITY, "", gloss.replace("_", "").strip()).strip(" .;,")
        if not gloss:
            continue
        if len(gloss) > 160:
            gloss = gloss[:160].rsplit(" ", 1)[0]
        for term in terms:
            head = term.lower()
            if particle and not re.fullmatch(r"\((?:se|s['’])\)", particle):
                head += " " + particle
            head = unicodedata.normalize("NFC", head.replace("_", ""))
            key = (head, gloss)
            if key not in seen:
                seen.add(key)
                rows.append(key)
    with OUT.open("w", encoding="utf-8") as out:
        out.write("headword\tgloss\tgloss_lang\tpos\n")
        for head, gloss in rows:
            out.write(f"{head}\t{gloss}\tfr\t\n")
    print(f"{OUT.name}: {len(rows)} rows, {len({r[0] for r in rows})} headwords")


if __name__ == "__main__":
    main()
