#!/usr/bin/env python3
"""Cénac-Moncaut, Dictionnaire gascon-français, dialecte du département du Gers (1863)
-> headword/gloss tables.

Source: ocr/cenac-moncaut-1863_tesseract-fra.txt, a Tesseract re-OCR of the
archive.org page scans (made by ocr_cenac-moncaut-1863-gers.py; archive.org's
own text layer misreads the small-capital headwords and is not used).

An entry is `HEADWORD[, FEM. ENDING], s. f., gloss[ (Dast.)][ (1290)].`
The author says (Introduction, p. vi) that his words come from three sources
and that he marks two of them: words taken from the 17th-century poet
Dastros carry "(Dast.)", words taken from medieval charters carry the date of
the charter, "tous les autres appartiennent au langage vulgaire". Hence:

    cenac-moncaut-1863-gers.tsv           unmarked: the spoken Gascon of the Gers
    cenac-moncaut-1863-gers-dastros.tsv   marked (Dast.): Dastros, 17th century
    cenac-moncaut-1863-gers-charters.tsv  marked with a year: charters, 13th-17th c.

Headwords are printed in small capitals and are lower-cased here; nothing
else is changed and no spelling is repaired. Because the text is OCR,
headwords are filtered, not fixed:
  * only headwords that Tesseract returned wholly in capitals are taken (a
    small capital it was unsure of comes out in lower case: "BrozE",
    "Bruckoc"), made of letters and hyphens only;
  * the headwords of successive entries must run alphabetically (the longest
    non-decreasing run is kept).
The gloss is the text between the part of speech and the first full stop or
parenthesis, written in lower case (the OCR scatters capitals through the
French text); a part of speech is carried over when the book gives one. A
gloss is kept only if every word of it is a known French word form (the word
list of Tesseract's French model, ocr/french-wordlist_tessdata-fra.txt, plus
data/sources/kaikki_full/fr_forms.tsv when present): this drops glosses with
OCR damage, at the price of some glosses that use rare French words.

    python3 parse_cenac-moncaut-1863-gers.py
"""
from __future__ import annotations

import bisect
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
OCR = HERE / "ocr" / "cenac-moncaut-1863_tesseract-fra.txt"
OUT = {"modern": HERE / "cenac-moncaut-1863-gers.tsv",
       "dastros": HERE / "cenac-moncaut-1863-gers-dastros.tsv",
       "charters": HERE / "cenac-moncaut-1863-gers-charters.tsv"}

UP = "A-ZÀ-ÖØ-Þ"
LOW = "a-zà-öø-ÿœ"
CAPS = rf"[{UP}][{UP}'’\-]*"
# The OCR renders "s. m." as "8 M.", "$ m.", "£ f.", "S. {." and "v. a." as "V. &,", "V. à&,", "Y. a.".
NOUN = r"[sS8$&£][.,]? ?(?:[mMfF{]|mM|IM|[fF]\. ?[mM])(?![a-zà-ÿ])[.,]*(?: ?p[l.]?\b\.?)?|subst\.?"
VERB = r"[vVY][.,] ?(?:[aàâ&%nNADd]&?(?![a-zà-ÿ])|r[ée]f\b|pr\b)?[.,]*"
POS = [("noun", NOUN), ("adj", r"adj ?[.,]|ad ?[.,]"), ("adv", r"adv ?[.,]"), ("prep", r"pr[ée]p ?[.,]"),
       ("conj", r"conj ?[.,]"), ("pron", r"pron ?[.,]|pr ?[.,]"), ("num", r"n\. ?(?:den|num)\.?|num ?[.,]"),
       ("other", r"int(?:erj)? ?[.,]|excl ?[.,]|art ?[.,]"), ("verb", VERB)]
ENTRY = re.compile(
    rf"^({CAPS}(?: OU {CAPS})?)"                                   # headword in capitals
    rf"((?:, ?(?:[{UP}]{{2}}[{UP}'’\-]*|[OAE0](?=,))){{0,2}})"       # variants / feminine endings (TO, DO, 0)
    rf"(?:\s*[,.]\s*|\s+(?=(?:{NOUN}|{VERB}|adj ?[.,]|adv ?[.,])))(.*)$")
DASTROS = re.compile(r"[({\[]\s*[DV0O][aouàâ][sa][tléif/!1]{0,2}[.,:;]*\s*[)}\]]|\bDast\b", re.I)
YEAR = re.compile(r"[({\[]\s*[1ltI!][\d/lOo ]{2,4}\d?\s*[.,]?\s*[)}\]]")


# French word forms, to tell a clean French gloss from OCR debris: the word list inside Tesseract's
# French model (saved next to the OCR text) and, when the repository has it, its French forms table.
FRENCH_LISTS = [HERE / "ocr" / "french-wordlist_tessdata-fra.txt", HERE.parents[1] / "kaikki_full" / "fr_forms.tsv"]
ELIDED = {"quelqu", "lorsqu", "jusqu", "puisqu", "presqu", "aujourd", "quoiqu"}


def french_words() -> set[str]:
    words: set[str] = set()
    for path in FRENCH_LISTS:
        if path.is_file():
            with path.open(encoding="utf-8") as lines:
                for line in lines:
                    words.update(part.lower() for part in line.rstrip("\n").split("\t"))
    if not words:
        print("warning: no French word list found; glosses are not checked against one")
    return words


def is_french(gloss: str, words: set[str]) -> bool:
    """Every word of three letters or more is a known French form (capitalised names are let through)."""
    if not words:
        return True
    for token in re.findall(r"[A-Za-zÀ-ÿœŒ]+(?:-[A-Za-zÀ-ÿœŒ]+)*", gloss):
        low = token.lower()
        if len(low) < 3 or token[0].isupper() or low in words or low in ELIDED:
            continue
        if low.endswith(("s", "x")) and low[:-1] in words:
            continue
        if low.endswith("ment") and (low[:-4] in words or low[:-4] + "e" in words or low[:-5] in words):
            continue
        if "-" in low and all(len(part) < 3 or part in words for part in low.split("-")):
            continue
        return False
    return True


def fold(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    return re.sub(r"[^a-z]", "", "".join(c for c in text if not unicodedata.combining(c)))


def entries():
    """(headwords, entry text) for each entry line of the dictionary pages."""
    text = OCR.read_text(encoding="utf-8")
    text = text[text.index("DICTIONNAIRE GASCON"):]
    stop = re.search(r"\n\s*GRAMMAIRE GASCONNE\s*\n", text)
    text = text[:stop.start()] if stop else text
    current = None
    for line in text.split("\n"):
        line = re.sub(r"\s+", " ", line).strip()
        if not line or line.startswith("=== page") or re.fullmatch(rf"[{UP}]{{1,4}}|\d{{1,3}}|[{UP}]{{2,4}} \d+|\d+ [{UP}]{{2,4}}", line):
            continue
        if " | " in line:               # two columns read as one line: unusable, and it ends the entry
            if current:
                yield current
            current = None
            continue
        found = ENTRY.match(line)
        if found:
            if current:
                yield current
            heads = found.group(1).split(" OU ") + [v for v in re.findall(rf"{CAPS}", found.group(2)) if len(v) > 3]
            current = [heads, found.group(3)]
        elif current:
            body = current[1]
            if body.rstrip().endswith((".", ")")) and re.match(rf"[{UP}\d]", line):
                yield current           # a misread headword line: it is not taken, and it ends this entry
                current = None
                continue
            current[1] = body[:-1] + line if body.endswith("-") and not body.endswith(" -") else body + " " + line
    if current:
        yield current


def split_pos(body: str) -> tuple[str, str]:
    body = re.sub(r"^[A-Za-z0]{1,3},\s*(?=adj|ad[.,])", "", body)          # feminine ending: "so, adj."
    for name, pattern in POS:
        found = re.match(rf"(?:{pattern})\s*,?\s*", body)
        if found and found.end() > 1:
            return name, body[found.end():]
    return "", body


def longest_run(keys: list[str]) -> set[int]:
    tails: list[str] = []
    tail_index: list[int] = []
    previous = [-1] * len(keys)
    for i, key in enumerate(keys):
        slot = bisect.bisect_right(tails, key)
        if slot == len(tails):
            tails.append(key)
            tail_index.append(i)
        else:
            tails[slot] = key
            tail_index[slot] = i
        previous[i] = tail_index[slot - 1] if slot else -1
    keep, i = set(), tail_index[-1] if tail_index else -1
    while i >= 0:
        keep.add(i)
        i = previous[i]
    return keep


def main() -> None:
    found = list(entries())
    keep = longest_run([fold(heads[0]) for heads, _ in found])
    rows = {name: [] for name in OUT}
    seen: set[tuple] = set()
    stats = {"entries": len(found), "out_of_order": 0, "bad_head": 0, "no_gloss": 0, "gloss_not_french": 0}
    words = french_words()
    for index, (heads, body) in enumerate(found):
        if index not in keep:
            stats["out_of_order"] += 1
            continue
        source = "dastros" if DASTROS.search(body) else "charters" if YEAR.search(body) else "modern"
        pos, rest = split_pos(body)
        gloss = re.split(r"\.(?=\s|$)|[({\[]|;\s*(?=vient|voir|voy)|;?\s+[—–-]\s", rest)[0]
        gloss = re.split(rf",\s+(?=[{UP}][{LOW}{UP}]+,)", gloss)[0]      # the next entry ran on: "..., Gaousous, so, adj"
        gloss = re.sub(r"\s+([,;])", r"\1", gloss).strip(" .,;:-—").lower()   # the OCR scatters capitals in glosses
        if (len(gloss) < 3 or len(gloss) > 140 or not re.match(rf"[{LOW}]", gloss)
                or re.search(rf"[^{LOW}{UP} ,;'’\-]|[{LOW}][{UP}]", gloss)
                or re.match(r"(?i)(?:voir|voy|idem|v\. )", gloss) or re.search(r"\b[b-df-hj-np-tv-xz]{1,2}\b ", gloss + " ")
                and re.search(r"(?:\b[a-zà-ÿ]{1,2}\b ){3}", gloss + " ")):
            stats["no_gloss"] += 1
            continue
        if not is_french(gloss, words):
            stats["gloss_not_french"] += 1
            continue
        for head in heads:
            if not re.fullmatch(rf"[{UP}]{{2,}}(?:-[{UP}]+)*", head) or re.search(r"[^A-ZÈÉÇÀÙÒÓÚÍÏË-]", head):
                stats["bad_head"] += 1
                continue
            key = (unicodedata.normalize("NFC", head.lower()), gloss, pos)
            if (source,) + key not in seen:
                seen.add((source,) + key)
                rows[source].append(key)
    for name, path in OUT.items():
        with path.open("w", encoding="utf-8") as out:
            out.write("headword\tgloss\tgloss_lang\tpos\n")
            for head, gloss, pos in rows[name]:
                out.write(f"{head}\t{gloss}\tfr\t{pos}\n")
        print(f"{path.name}: {len(rows[name])} rows, {len({r[0] for r in rows[name]})} headwords")
    print(stats)


if __name__ == "__main__":
    main()
