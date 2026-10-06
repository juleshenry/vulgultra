#!/usr/bin/env python3
"""Du Bois & Travers, Glossaire du patois normand (1856) -> headword/gloss table.

Source: raw/pg30904.txt, the Project Gutenberg / Distributed Proofreaders
transcription (eBook #30904). Mainland Norman; the book tags many entries
with a locality (A. Alencon, B. Bayeux, C. Cherbourg/Coutances, H.-N.
Haute-Normandie, L. Lisieux, M. Manche, R. Rouen, S.-I. Seine-Inferieure,
V. Valognes), which is not carried over.

An entry is a paragraph `HEADWORD[; VARIANT] [(s. f.)]: gloss. Notes.`;
`--HEADWORD: gloss` inside a paragraph opens a sub-entry.

Headwords are printed in capitals in the book and are lower-cased here; no
letter is otherwise changed. Feminine endings after a comma (`PRINS, E`) and
the reflexive marker `(SE)` are dropped; other inverted particles stay as
printed (`quia (a)`). The gloss is the first sentence after the colon;
etymologies, quotations and cross-references ("Voyez X") are cut. When an
entry lists as many glosses as headwords (`PREUNE; PREUNIER: prune;
prunier`) they are paired in order.

    python3 parse_dubois-travers-1856-mainland.py
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw" / "pg30904.txt"
OUT = HERE / "dubois-travers-1856-mainland.tsv"

UP = "A-ZÀ-ÖØ-ÞŒÆ"
CAPS_WORD = rf"[{UP}][{UP}'’\-]*"
CAPS_TERM = rf"{CAPS_WORD}(?: {CAPS_WORD})*"
POS_MARKS = [
    (r"\bs\. ?[mf]\b|\bs\. ?[mf]\. ?pl\b|\bsubst\b", "noun"), (r"\bv\. ?(?:a|n|r[ée]fl|pron)\b|\bverbe\b", "verb"),
    (r"\badj\b", "adj"), (r"\badv\b|\badverbe\b", "adv"), (r"\bpr[ée]p\b", "prep"), (r"\bconj\b", "conj"),
    (r"\bpron\b(?!\. ?_)", "pron"), (r"\binterj", "other"),
]
ABBREVIATIONS = r"(?:\b(?:M|MM|Mme|St|Ste|s|v|p|etc|adj|adv|pl|f|m|n|a|vol|chap|art|ms|cf|c\.-à-d)|[A-Z])$"
LOCALITY = r"(?:\s+(?:A|B|C|L|M|R|V|H\.-N|S\.-I)\.)+$"


def paragraphs() -> list[str]:
    text = RAW.read_text(encoding="utf-8")
    text = text[text.index("*** START"):text.index("*** END")]
    lines = text.split("\n")
    start = next(i for i, line in enumerate(lines) if line.strip() == "A.")
    body = "\n".join(lines[start:])
    return [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def first_sentence(body: str) -> str:
    """The text up to the first sentence end that is not an abbreviation."""
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


def head_terms(head: str) -> tuple[list[str], str] | None:
    """Headwords of the part before the colon, and the part of speech if stated."""
    pos = ""
    for pattern, name in POS_MARKS:
        if re.search(pattern, head):
            pos = name
            break
    head = re.sub(r"\((?:SE|S['’])\)", "", head)
    particles = {}

    def keep(match: re.Match) -> str:
        particles[len(particles)] = match.group(0)
        return f"\x00{len(particles) - 1}\x00"

    head = re.sub(rf"\((?:{CAPS_TERM})['’]?\)", keep, head)        # (A), (DE), (FAIRE)
    head = re.sub(r"\([^)]*\)", " ", head)                          # (s. f.), (Orne), ...
    head = re.sub(r",\s*(?:s|v)\. ?(?:[mfna]|r[ée]fl)\.?(?: ?pl\.?)?\s*$", "", head)
    terms: list[str] = []
    for index, chunk in enumerate(re.split(r"\s*;\s*|\s*,\s*|\s+(?:ou plutôt|et non pas|ou|et)\s+", head)):
        chunk = chunk.strip()
        if not chunk:
            continue
        found = re.match(rf"^({CAPS_TERM})(\s*\x00\d+\x00)?\s*(.*)$", chunk)
        if not found:
            if index == 0:
                return None        # the head does not open with a capitalised headword
            continue               # a lower-case qualifier ("en parlant du lait")
        term, particle, rest = found.group(1), found.group(2), found.group(3)
        if rest and (index == 0 and len(rest) > 45 or "." in rest):
            return None            # prose, not a headword line
        if index and len(term) <= 4 and terms and not rest:
            continue               # feminine ending: PRINS, E / COURANDIER, ÈRE
        if len(term) == 1 and term not in ("A", "Y", "O"):
            continue
        if particle:
            term += " " + particles[int(particle.strip("\x00 "))]
        terms.append(term)
    return (terms, pos) if terms else None


def clean_gloss(text: str) -> str:
    text = text.replace("_", "")
    text = re.sub(LOCALITY, "", text.strip())
    return text.strip(" .;,")


def entries():
    for paragraph in paragraphs():
        for piece in re.split(rf"\.?--(?={CAPS_TERM}[^:]{{0,40}}:)", paragraph):
            if ":" not in piece:
                continue
            head, body = piece.split(":", 1)
            if len(head) > 120:
                continue
            parsed = head_terms(head)
            if not parsed:
                continue
            terms, pos = parsed
            gloss = clean_gloss(first_sentence(body.strip()))
            if not gloss or re.match(r"(?i)^(voyez|v\.|même sens|même signification)\b", gloss):
                continue
            if len(gloss) > 160:
                gloss = gloss[:160].rsplit(" ", 1)[0]
            if re.fullmatch(r"(?i)(adverbe|adjectif|interjection|juron|verbe|substantif|pr[ée]position)", gloss):
                continue           # the book gives a word class, not a meaning
            if ";--" in gloss:     # numbered senses: SAI: soir;--(s. f.): soif;--pron.: soi
                for sense in gloss.split(";--"):
                    sense = clean_gloss(re.sub(r"^\s*(?:\([^)]*\)|[a-zé]+\.)\s*:\s*", "", sense))
                    for term in terms:
                        if sense:
                            yield term, sense, ""
                continue
            parts = [clean_gloss(part) for part in gloss.split(";")]
            if len(terms) > 1 and len(parts) == len(terms) and all(parts):
                for term, part in zip(terms, parts):
                    yield term, part, pos
            else:
                for term in terms:
                    yield term, gloss, pos


def main() -> None:
    seen: set[tuple] = set()
    rows = []
    for term, gloss, pos in entries():
        head = unicodedata.normalize("NFC", term.lower())
        key = (head, gloss, pos)
        if key not in seen:
            seen.add(key)
            rows.append(key)
    with OUT.open("w", encoding="utf-8") as out:
        out.write("headword\tgloss\tgloss_lang\tpos\n")
        for head, gloss, pos in rows:
            out.write(f"{head}\t{gloss}\tfr\t{pos}\n")
    print(f"{OUT.name}: {len(rows)} rows, {len({r[0] for r in rows})} headwords")


if __name__ == "__main__":
    main()
