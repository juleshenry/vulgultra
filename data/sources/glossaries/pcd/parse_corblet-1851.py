#!/usr/bin/env python3
"""Corblet, Glossaire étymologique et comparatif du patois picard, ancien et moderne (1851)
-> headword/gloss tables.

Picard of Picardy proper (Somme, with words from Boulogne, Béthune, Saint-Quentin,
Soissons ... named in parentheses; those locality notes are not carried over).

Source text: raw/glossairetymol00corbuoft_tesseract.txt, our own Tesseract 5
re-OCR (see reocr.py) of the archive.org scan `glossairetymol00corbuoft`
(University of Toronto copy); only the glossary proper is read.

An entry is `HEADWORD [et VARIANT] [(particle or Locality)]. Gloss. — comparisons, etymology.`
The book marks with an asterisk the words "no longer in use", taken from
medieval and 15th-16th century Picard documents. Those go to
corblet-1851-old-picard.doubtful.tsv; everything else to corblet-1851.doubtful.tsv.

What the script keeps and drops:
  * headwords are lower-cased (the book prints them in capitals); nothing
    else is changed. A lower-case particle in parentheses stays with the
    headword as printed (`bistinchint (de)`), except the reflexive `(se)`.
  * a headword is accepted only if it is made of letters, apostrophes,
    hyphens and spaces and fits the alphabetical run of its neighbours
    (first three letters, accents ignored): the guard against OCR-garbled
    headwords.
  * gloss = the first sentence after the headword; synonyms, comparisons
    with other dialects, etymologies (after a dash) and cross-references
    are cut.

    python3 parse_corblet-1851.py
"""
from __future__ import annotations

import bisect
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw" / "glossairetymol00corbuoft_tesseract.txt"
OUT = HERE / "corblet-1851.doubtful.tsv"
OUT_OLD = HERE / "corblet-1851-old-picard.doubtful.tsv"

UP = "A-ZÀ-ÖØ-ÞŒÆ"
LOW = "a-zà-öø-ÿœæ"
CAPS = rf"[{UP}][{UP}'’\-]*"
TERM = rf"{CAPS}(?: {CAPS})*"
ENTRY = re.compile(
    rf"^(?P<star>[^{UP}{LOW}\s(\[«»—\-]{{1,3}}\s*)?"         # the asterisk (however the OCR read it)
    rf"(?P<caps>{TERM}(?:,? (?:et|ou|ET|OU) {TERM}){{0,3}})"
    rf"\s*(?P<part>[\[({{][^\])}}]{{1,40}}[\])}}])?"
    rf"\s*(?P<part2>[\[({{][^\])}}]{{1,40}}[\])}}])?"
    rf"\s*\.\s*(?:—\s*)?(?P<body>\S.*)$")
ABBREVIATIONS = r"(?:\b(?:M|MM|Mme|St|Ste|etc|ex|v|V|p|art|chap|t|s|m|f|a|n|lat|fr|cf|Syn|syn)|\b[A-Z])$"


def fold(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower().replace("œ", "oe").replace("æ", "ae"))
    return re.sub(r"[^a-z]", "", "".join(c for c in text if not unicodedata.combining(c)))


def glossary_lines(path: Path) -> list[str]:
    """The lines of the glossary proper: from its heading to 'FIN DU GLOSSAIRE'."""
    lines = [re.sub(r"\s+", " ", raw.replace("’", "'")).replace(" ,", ",").strip()
             for raw in path.read_text(encoding="utf-8").split("\n")]
    start = max(i for i, line in enumerate(lines) if re.search(r"ABR[ÉE]VIATIONS", line))
    ends = [i for i, line in enumerate(lines) if re.search(r"FIN\s+DU\s+GLOSSAIRE", line) and i > start]
    return [line for line in lines[start:ends[0] if ends else len(lines)] if not line.startswith("=== leaf")]


def raw_entries(path: Path):
    current, rest = None, []
    for line in glossary_lines(path):
        found = ENTRY.match(line) if line else None
        if found and len(fold(found.group("caps"))) >= 2:
            if current:
                yield current, rest
            current, rest = found, []
        elif current is not None and line:
            rest.append(line)
    if current:
        yield current, rest


def join(first: str, rest: list[str]) -> str:
    text = first
    for line in rest:
        text = text[:-1] + line if text.endswith("-") and line[:1].islower() else text + " " + line
    return text


def first_sentence(body: str) -> str:
    position = 0
    while True:
        found = re.search(r"[.!?](?=\s|$)", body[position:])
        if not found:
            return body
        end = position + found.start()
        if body[end] == "." and re.search(ABBREVIATIONS, body[:end]):
            position = end + 1
            continue
        return body[:end]


def shorten(gloss: str, limit: int = 150) -> str:
    gloss = re.split(r"\s*[«»]|\s*[—–]\s*|\s+-\s+", gloss)[0]
    if len(gloss) > limit:
        cut = max(gloss.rfind(";", 0, limit), gloss.rfind(",", 0, limit))
        gloss = gloss[:cut] if cut > 40 else gloss[:limit].rsplit(" ", 1)[0]
    return gloss.strip(" .;,:-—")


def alphabetical(keys: list[str]) -> list[bool]:
    """Longest non-decreasing run of the 3-letter keys: True where the entry belongs to it."""
    tails: list[str] = []
    tail_index: list[int] = []
    previous = [-1] * len(keys)
    for i, key in enumerate(keys):
        at = bisect.bisect_right(tails, key)
        if at == len(tails):
            tails.append(key)
            tail_index.append(i)
        else:
            tails[at] = key
            tail_index[at] = i
        previous[i] = tail_index[at - 1] if at else -1
    keep = [False] * len(keys)
    i = tail_index[-1] if tail_index else -1
    while i >= 0:
        keep[i] = True
        i = previous[i]
    return keep


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else RAW
    parsed = []
    for found, rest in raw_entries(path):
        heads = re.split(r",? (?:et|ou|ET|OU) ", found.group("caps"))
        particle = ""
        for part in (found.group("part"), found.group("part2")):
            inner = (part or "").strip("[](){} ")
            if inner and inner[0].islower() and not re.fullmatch(r"(?i)se|s'", inner):
                particle = inner
        gloss = shorten(first_sentence(join(found.group("body"), rest)))
        if not gloss or re.match(r"(?i)^(?:v|voy|voyez)\b[. ]", gloss + " ") or not re.search(rf"[{LOW}]{{3}}", gloss):
            continue
        if particle:
            heads = [f"{head} ({particle})" for head in heads]
        parsed.append((heads, gloss, bool(found.group("star")), fold(found.group("caps"))[:3]))
    keep = alphabetical([p[3] for p in parsed])
    tables: dict[bool, list[tuple[str, str]]] = {False: [], True: []}
    seen, dropped = set(), 0
    for (heads, gloss, old, _), fits in zip(parsed, keep):
        if not fits:
            dropped += 1
            continue
        for head in heads:
            head = unicodedata.normalize("NFC", head.lower().strip())
            if (head, gloss) not in seen:
                seen.add((head, gloss))
                tables[old].append((head, gloss))
    for old, target in ((False, OUT), (True, OUT_OLD)):
        with target.open("w", encoding="utf-8") as out:
            out.write("headword\tgloss\tgloss_lang\tpos\n")
            for head, gloss in tables[old]:
                out.write(f"{head}\t{gloss}\tfr\t\n")
        print(f"{target.name}: {len(tables[old])} rows, {len({r[0] for r in tables[old]})} headwords")
    print(f"{dropped} entries left out as not fitting the alphabetical run")


if __name__ == "__main__":
    main()
