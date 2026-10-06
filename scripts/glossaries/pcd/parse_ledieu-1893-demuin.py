#!/usr/bin/env python3
"""Ledieu, Petit glossaire du patois de Démuin (Paris, 1893) -> headword/gloss table.

Picard of Démuin (Somme, Santerre).

Source text: raw/petitglossairedu00lediuoft_tesseract.txt, our own Tesseract 5
re-OCR (see reocr.py) of the archive.org scan `petitglossairedu00lediuoft`
(University of Toronto copy).

An entry is `Headword[, fem. ending][ (particle)], s. m., gloss; examples.`
The part of speech right after the headword is what marks a line as the
start of an entry, so entries without one (mostly bare cross-references)
are not read.

What the script keeps and drops:
  * headwords are lower-cased (the book prints them in small capitals);
    nothing else is changed. Feminine endings after the comma are dropped;
    a particle in parentheses stays as printed, except the reflexive (se)
    and pronunciation respellings such as (ain-gneler), which are dropped.
  * a headword is accepted only if it is made of letters, apostrophes,
    hyphens and spaces and fits the alphabetical run of its neighbours
    (first three letters, accents ignored): the guard against OCR-garbled
    headwords.
  * gloss = the first clause after the part of speech, up to the first
    semicolon or full stop; examples, sub-phrases after a dash and
    cross-references are cut (so a second sense after a semicolon is lost).

    python3 parse_ledieu-1893-demuin.py
"""
from __future__ import annotations

import bisect
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw" / "petitglossairedu00lediuoft_tesseract.txt"
OUT = HERE / "ledieu-1893-demuin.doubtful.tsv"
HEAD_STYLE = "capitalised"        # how the book prints headwords: "caps", "capitalised" or "any"
CUT_AT_SEMICOLON = True           # the book puts its examples after a semicolon

UP = "A-ZÀ-ÖØ-ÞŒÆ"
LOW = "a-zà-öø-ÿœæ"
WORD = rf"[{UP}{LOW}][{UP}{LOW}'’\-]*"
HEAD = {"caps": rf"[{UP}][{UP}'’\-]*(?: [{UP}][{UP}'’\-]*){{0,3}}",
        "capitalised": rf"[{UP}][{UP}{LOW}'’\-]*(?: {WORD}){{0,4}}",
        "any": rf"{WORD}(?: {WORD}){{0,4}}"}[HEAD_STYLE]
D = r"[.,]"                       # the OCR often reads the full stop of an abbreviation as a comma
POS = [
    (rf"s{D} ?m{D}(?: ?(?:et|ou) ?f{D})?(?: ?p[li]{D})?(?: ?et ?adj{D})?|s{D} ?[fÎî]{D}(?: ?p[li]{D})?(?: ?et ?adj{D})?"
     rf"|s{D} ?(?:des )?(?:2|deux) ?g{D}|subst{D}(?: ?[mf]{D})?", "noun"),
    (rf"v{D} ?(?:a|n|r[ée]fl|pron|imp|impers|aux|act|neut|unip|r)\b{D}?(?: ?(?:et|ou) ?(?:v{D} ?)?[anr]{D})?", "verb"),
    (rf"adj{D} ?num{D}|num{D}|n{D} ?de ?nombre", "num"),
    (rf"adj{D}(?: ?(?:poss|d[ée]m|ind[ée]f|qual|verb|des 2 g|2 g|m|f){D})?(?: ?(?:et|ou) ?s{D}(?: ?[mf]{D})?)?", "adj"),
    (rf"adv{D}|loc{D} ?adv{D}", "adv"), (rf"pr[ée]p{D}|loc{D} ?pr[ée]p{D}", "prep"),
    (rf"conj{D}|loc{D} ?conj{D}", "conj"), (rf"pron{D}(?: ?(?:pers|poss|d[ée]m|rel|ind[ée]f|ind){D})?", "pron"),
    (rf"interj{D}|art{D}(?: ?(?:d[ée]f|ind[ée]f|contr){D})?|part{D}(?: ?pass[ée]?{D}?)?|loc{D}|exclam{D}|onomat{D}", "other"),
]
POS_ANY = "|".join(f"(?P<p{i}>{pattern})" for i, (pattern, _) in enumerate(POS))
ENTRY = re.compile(
    rf"^(?P<heads>{HEAD}(?:,? (?:ou|et) {HEAD}|, {HEAD}){{0,3}})"
    rf"(?P<part>\s*[\[(][^\])]{{1,40}}[\])])?"
    rf"(?:,\s*(?P<fem>[{LOW}{UP}]{{1,7}}))?"
    rf"\s*[,.]\s*(?:{POS_ANY})\s*,?\s*(?:[—–-]+\s*)?(?P<body>.*)$")
ABBREVIATIONS = r"(?:\b(?:M|MM|Mme|St|Ste|etc|ex|v|V|p|art|chap|t|s|m|f|a|n|lat|fr|cf|fig|Gr|syn|Syn|pl|sing)|\b[A-Z])$"


def fold(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower().replace("œ", "oe").replace("æ", "ae"))
    return re.sub(r"[^a-z]", "", "".join(c for c in text if not unicodedata.combining(c)))


def lines_of(path: Path):
    for raw in path.read_text(encoding="utf-8").split("\n"):
        if raw.startswith("=== leaf"):
            continue
        yield re.sub(r"\s+", " ", raw.replace("’", "'")).replace(" ,", ",").strip()


def raw_entries(path: Path):
    current, rest = None, []
    for line in lines_of(path):
        found = ENTRY.match(line) if line else None
        if found and len(fold(found.group("heads"))) >= 2:
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
    gloss = re.split(r"\s*[«»]|\s*;?\s*[—–]\s*|\s+-\s+|\s*\(Gr\b|\s*\[Gr\b", gloss)[0]
    if CUT_AT_SEMICOLON:
        gloss = gloss.split(";")[0]
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
        heads = [h for h in re.split(r",? (?:ou|et) |, ", found.group("heads")) if h]
        pos = next(name for i, (_, name) in enumerate(POS) if found.group(f"p{i}"))
        particle = (found.group("part") or "").strip("[]() ")
        gloss = shorten(first_sentence(join(found.group("body"), rest)))
        if (not gloss or re.match(r"(?i)^(?:v|voy|voyez|ce mot|même sens|mêmes? acceptions?)\b[. ]", gloss + " ")
                or not re.search(rf"[{LOW}]{{3}}", gloss)):
            continue
        respelling = fold(particle)[:2] == fold(heads[0])[:2] or "-" in particle   # (ain-gneler): pronunciation
        if particle and not respelling and not re.fullmatch(r"(?i)se|s'", particle):
            heads = [f"{head} ({particle})" for head in heads]
        parsed.append((heads, gloss, pos, fold(heads[0])[:3]))
    keep = alphabetical([p[3] for p in parsed])
    rows, seen, dropped = [], set(), 0
    for (heads, gloss, pos, _), fits in zip(parsed, keep):
        if not fits:
            dropped += 1
            continue
        for head in heads:
            head = unicodedata.normalize("NFC", head.lower().strip())
            if (head, gloss) not in seen:
                seen.add((head, gloss))
                rows.append((head, gloss, pos))
    with OUT.open("w", encoding="utf-8") as out:
        out.write("headword\tgloss\tgloss_lang\tpos\n")
        for head, gloss, pos in rows:
            out.write(f"{head}\t{gloss}\tfr\t{pos}\n")
    print(f"{OUT.name}: {len(rows)} rows, {len({r[0] for r in rows})} headwords; "
          f"{dropped} entries left out as not fitting the alphabetical run")


if __name__ == "__main__":
    main()
