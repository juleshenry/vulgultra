#!/usr/bin/env python3
"""Orain, Glossaire patois du département d'Ille-et-Vilaine (1886) -> headword/gloss table.

Sources: ocr/orain-1886_tesseract-fra.txt, a Tesseract OCR of the archive.org
page scans (made by ocr_orain-1886-ille-et-vilaine.py), and
raw/glossaire_patois_ille_vilaine_djvu.txt, archive.org's own OCR text (ABBYY
FineReader 8) of the same scans.

An entry is `HEADWORD[, FEM. ENDING][ (s')], s. f. Gloss. « example »
(Locality.)`. The gloss is the first sentence after the part of speech, as
printed; examples in « », remarks and the closing locality (Rennes, Redon,
Bain, ...: all within Ille-et-Vilaine, not carried over) are cut. Entries
whose text is only a cross-reference or a remark are skipped.

Headwords are printed in capitals and small capitals and are written here in
lower case; nothing else is changed and no spelling is repaired. Because the
text is OCR, a headword is taken only if
  * Tesseract returned it wholly in capitals (a small capital it was unsure
    of comes out in lower case), letters, hyphens and apostrophes only;
  * the ABBYY text has the same word, letter for letter, at the start of a
    line (two independent OCR engines agree on the spelling).

    python3 parse_orain-1886-ille-et-vilaine.py
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
TESSERACT = HERE / "ocr" / "orain-1886_tesseract-fra.txt"
ABBYY = HERE / "raw" / "glossaire_patois_ille_vilaine_djvu.txt"
OUT = HERE / "orain-1886-ille-et-vilaine.tsv"

UP = "A-ZÀ-ÖØ-ÞŒ"
LOW = "a-zà-öø-ÿœ"
CAPS = rf"[{UP}][{UP}'’\-]*"
POS = (r"(?:[sS]\. ?[mMfF]\. ?(?:et ?[mf]\. ?)?(?:p[li]\.)?|[sS]\. ?(?:p[li]\.)?|"
       r"[vV]\. ?(?:[aàn]|pr|imp|r[ée]fl|pron)\.(?: ?et ?(?:a|n|pr)\.)?|"
       r"[aA]dj\.(?: ?des deux g\.| ?[mf]\.| ?num\.| ?et ?subst?\.)?|[aA]dv\.|[lL]oc\.(?: ?ad[vj]\.| ?aff\.)?|"
       r"[pP]r[ée]p\.|[cC]onj\.|[pP]ron\.(?: ?pers\.)?|[iI]nt(?:erj)?\.|[eE]xcl\.|[pP]art\.)")
ENTRY = re.compile(
    rf"^({CAPS}(?: (?:(?:et|ou|ET|OU) )?{CAPS}){{0,5}})"            # headword(s) in capitals
    rf"(?:, ?[{UP}]{{1,5}})?"                                       # feminine ending: PANSU, E
    rf"(?: ?\((?:[sS]['’]|[sS]e)\))?"                               # reflexive (s')
    rf" ?[,.] ?({POS})\s*(.*)$")
POS_MAP = [(r"(?i)^s", "noun"), (r"(?i)^v", "verb"), (r"(?i)^adj\. ?num", "num"), (r"(?i)^adj", "adj"),
           (r"(?i)^adv|^loc\. ?adv", "adv"), (r"(?i)^pr[ée]p", "prep"), (r"(?i)^conj", "conj"),
           (r"(?i)^pron", "pron"), (r"(?i)^int|^excl|^loc|^part", "other")]
SKIP_GLOSS = re.compile(r"(?i)^(?:v\. |voy|voir |syn|même|se dit|ne se dit|s['’]emploie|employé|pour |c['’]est|"
                        r"n['’]est|est |ce mot|mot |terme|expression|locution|on dit|usité|dans |d['’]où|du verbe|de )")
ABBREV = r"(?:\b(?:M|MM|Mme|St|Ste|etc|V|v|p|s|c\.-à-d)|\b[A-Z])$"


def nfc_lower(text: str) -> str:
    return unicodedata.normalize("NFC", text.lower())


def glossary_lines(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").split("\n")
    start = max(i for i, line in enumerate(lines) if "ILLE-ET-VILAINE" in line and i < len(lines) // 4) + 1
    end = next(i for i, line in enumerate(lines) if "FIN DU GLOSSAIRE" in line)
    return [re.sub(r"\s+", " ", line).strip() for line in lines[start:end]]


def entries():
    current = None
    for line in glossary_lines(TESSERACT):
        line = re.sub(r"^[^\w(«]+", "", line)              # specks at the left margin
        line = re.sub(r"\s*[|‘’'\"_:;.\-]{1,3}$", "", line) if re.search(r"\s[|‘_:;]$|\s[.\-]$", line) else line
        if not line or line.startswith("=== page") or re.fullmatch(r"[—–\- \dIVXLTO]{1,9}", line):
            continue
        found = ENTRY.match(line)
        if found:
            if current:
                yield current
            current = [found.group(1), found.group(2), found.group(3)]
        elif current:
            body = current[2]
            current[2] = body[:-1] + line if body.endswith("-") and not body.endswith(" -") else body + " " + line
    if current:
        yield current


def abbyy_words() -> set[str]:
    """Lower-cased first words (up to four) of every line of the ABBYY text."""
    found = set()
    for line in glossary_lines(ABBYY):
        words = re.split(r"[ ,.]+", line)
        for n in range(1, min(6, len(words)) + 1):
            found.add(nfc_lower(" ".join(words[:n])))
    return found


def first_sentence(body: str) -> str:
    position = 0
    while True:
        found = re.search(r"\.(?=\s|$)|[«»(]|\s[—–]\s", body[position:])
        if not found:
            return body
        end = position + found.start()
        if found.group(0) == "." and re.search(ABBREV, body[:end]):
            position = end + 1
            continue
        return body[:end]


def main() -> None:
    confirm = abbyy_words()
    rows, seen = [], set()
    stats = {"entries": 0, "not_capitals": 0, "not_confirmed": 0, "no_gloss": 0}
    for heads, pos_text, body in entries():
        stats["entries"] += 1
        gloss = re.sub(r"\s+([,;])", r"\1", first_sentence(body)).strip(" .,;:")
        if (len(gloss) < 2 or SKIP_GLOSS.match(gloss) or len(gloss) > 150
                or re.search(rf"[^{LOW}{UP} ,;'’\-]|[{LOW}][{UP}]", gloss)):
            stats["no_gloss"] += 1
            continue
        pos = next((name for pattern, name in POS_MAP if re.search(pattern, pos_text)), "")
        for head in re.split(r" (?:et|ou|ET|OU) ", heads):
            if not re.fullmatch(rf"[{UP}]+(?:['’\- ][{UP}]+)*", head) or len(head) < 2:
                stats["not_capitals"] += 1
                continue
            head = nfc_lower(head)
            if head not in confirm:
                stats["not_confirmed"] += 1
                continue
            key = (head, gloss, pos)
            if key not in seen:
                seen.add(key)
                rows.append(key)
    with OUT.open("w", encoding="utf-8") as out:
        out.write("headword\tgloss\tgloss_lang\tpos\n")
        for head, gloss, pos in rows:
            out.write(f"{head}\t{gloss}\tfr\t{pos}\n")
    print(f"{OUT.name}: {len(rows)} rows, {len({r[0] for r in rows})} headwords")
    print(stats)


if __name__ == "__main__":
    main()
