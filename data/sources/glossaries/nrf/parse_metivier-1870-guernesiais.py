#!/usr/bin/env python3
"""Métivier, Dictionnaire franco-normand ou recueil des mots particuliers au
dialecte de Guernesey (1870) -> headword/gloss table. Guernésiais.

Source text: two Tesseract (French model) readings of the archive.org scan
`DictionnaireFranco-normand`, made by ocr_tesseract.py at 300 and 400 dpi:
raw/metivier-1870_tesseract-fra.txt and raw/metivier-1870_tesseract-fra-400dpi.txt.
(The OCR text archive.org offers for this scan was made without a French
model and has no accents at all; it is not used.)

An entry reads `Headword[ ou variant], s. m. Gloss.` and is followed by
etymological notes and verse quotations, which are cut: the gloss is the
first sentence after the word class.

Kept only when all of this holds, so that OCR damage stays out:
  * both readings give the same headword, letter for letter, on the same page;
  * the headword has only the letters Métivier's spelling uses (the scan's
    `à`/`ù` nasal marks are often misread as `ä`/`ü`: such heads are dropped,
    not repaired), no digit, no capital inside the word;
  * the headword fits the alphabetical run of its neighbours (first two
    letters, accents ignored);
  * every word of the gloss is a known French form (checked against the
    repository's data/sources/kaikki_full/fr_forms.tsv and fr.jsonl when
    present), which removes glosses the OCR damaged.
Headwords keep the book's spelling; only the capital initial is lower-cased.

    python3 parse_metivier-1870-guernesiais.py
"""
from __future__ import annotations

import bisect
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
PASS_A = HERE / "raw" / "metivier-1870_tesseract-fra.txt"
PASS_B = HERE / "raw" / "metivier-1870_tesseract-fra-400dpi.txt"
OUT = HERE / "metivier-1870-guernesiais.tsv"
FRENCH = HERE.parents[1] / "kaikki_full"

ALLOWED = set("abcdefghijklmnopqrstuvwxyzàâçèéêëîïñôùûœæ'’- ")
WORD = r"[A-Za-zÀ-ÖØ-öø-ÿŒœ][A-Za-zÀ-ÖØ-öø-ÿŒœ'’\-]*"
POS_OCR = (r"(?:[s8+]\. ?(?:et adj\.|[mfw/]{1,2}[.,/]?(?: ?p[l/]\.?)?)|s[mf]\.|v\.(?: ?[an]\.)?|adj\.|ad;\.|adv\.|pr[ée]p\.|"
           r"pron\.|conj\.|interj\.|part\. ?p[au]ss[ée]\.|loc\. ?adv\.)")
HEAD = re.compile(rf"^({WORD}(?: {WORD}){{0,3}}(?:,? ou {WORD}(?: {WORD}){{0,2}})?), ?({POS_OCR}) *(.*)$")
POS = [(r"et adj", "noun"), (r"^[s8+]", "noun"), (r"^v", "verb"), (r"^ad[j;]", "adj"), (r"^part", "adj"), (r"^adv|^loc", "adv"),
       (r"^pr[ée]p", "prep"), (r"^pron", "pron"), (r"^conj", "conj")]
ELIDED = {"l", "d", "qu", "s", "n", "c", "j", "m", "t", "jusqu", "lorsqu", "puisqu", "quelqu"}


def key(word: str) -> str:
    plain = unicodedata.normalize("NFD", word.lower())
    return "".join(ch for ch in plain if "a" <= ch <= "z")


def french_forms() -> set[str] | None:
    forms: set[str] = set()
    table, lemmas = FRENCH / "fr_forms.tsv", FRENCH / "fr.jsonl"
    if not table.is_file():
        return None
    for line in table.open(encoding="utf-8"):
        forms.update(part.lower() for part in line.rstrip("\n").split("\t"))
    if lemmas.is_file():
        for line in lemmas.open(encoding="utf-8"):
            forms.add(json.loads(line).get("word", "").lower())
    return forms


def known(gloss: str, forms: set[str] | None) -> bool:
    if forms is None:
        return True
    for token in re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿŒœ]+", gloss.replace("œ", "oe").replace("Œ", "Oe")):
        low = token.lower()
        if len(low) > 1 and low not in ELIDED and low not in forms and low.replace("oe", "œ") not in forms:
            return False
    return True


def entries(path: Path):
    """(page, [headwords], pos, gloss) for every entry line of one OCR reading."""
    text = unicodedata.normalize("NFC", path.read_text(encoding="utf-8")).replace("ﬁ", "fi").replace("ﬂ", "fl")
    for chunk in text.split("\f### page ")[1:]:
        number, _, body = chunk.partition("\n")
        lines = [re.sub(r"\s+", " ", line).strip() for line in body.split("\n")]
        for index, line in enumerate(lines):
            found = HEAD.match(line)
            if not found or not found.group(1)[0].isupper():
                continue
            gloss = found.group(3)
            extra = 1
            while not re.search(r"[.:;](?:\s|$)", gloss) and extra <= 2 and index + extra < len(lines):
                nxt = lines[index + extra]
                if not nxt or HEAD.match(nxt):
                    break
                gloss = gloss[:-1] + nxt if gloss.endswith("-") else gloss + " " + nxt
                extra += 1
            gloss = re.split(r"[.:](?=\s|$)", gloss)[0]
            gloss = re.sub(r"\s[|!{}\[\]‘'’;:.,+*JjIil1ï]$", "", gloss.strip())
            gloss = gloss.strip(" .;,:|!{}[]‘’'*+")
            heads = [h.strip() for h in re.split(r",? ou ", found.group(1))]
            pos = next((name for pattern, name in POS if re.search(pattern, found.group(2))), "other")
            yield int(number), heads, pos, gloss


def clean_head(head: str) -> str | None:
    low = head[0].lower() + head[1:]
    if any(ch not in ALLOWED for ch in low) or len(key(low)) < 2 and low not in ("a", "à", "y", "o", "i", "é"):
        return None
    return low


def main() -> None:
    if not PASS_B.is_file():
        raise SystemExit(f"missing {PASS_B.name}: run ocr_tesseract.py (see its docstring) first")
    second = {(page, head) for page, heads, _, _ in entries(PASS_B) for head in heads}
    forms = french_forms()
    stats = {"read": 0, "disagree": 0, "letters": 0, "gloss": 0, "order": 0}
    candidates = []
    for page, heads, pos, gloss in entries(PASS_A):
        stats["read"] += 1
        if any((page, head) not in second for head in heads):
            stats["disagree"] += 1
            continue
        cleaned = [clean_head(head) for head in heads]
        if any(head is None for head in cleaned):
            stats["letters"] += 1
            continue
        if not gloss or len(gloss) > 160 or not known(gloss, forms):
            stats["gloss"] += 1
            continue
        candidates.append((cleaned, pos, gloss))

    keys = [key(c[0][0])[:2] for c in candidates]
    tails, tail_index, previous = [], [], {}
    for n, value in enumerate(keys):
        at = bisect.bisect_right(tails, value)
        if at == len(tails):
            tails.append(value); tail_index.append(n)
        else:
            tails[at] = value; tail_index[at] = n
        previous[n] = tail_index[at - 1] if at else None
    keep, n = set(), tail_index[-1] if tail_index else None
    while n is not None:
        keep.add(n)
        n = previous[n]
    stats["order"] = len(candidates) - len(keep)

    rows, seen = [], set()
    for i, (heads, pos, gloss) in enumerate(candidates):
        if i not in keep:
            continue
        for head in heads:
            row = (head, gloss, pos)
            if row not in seen:
                seen.add(row)
                rows.append(row)
    with OUT.open("w", encoding="utf-8") as out:
        out.write("headword\tgloss\tgloss_lang\tpos\n")
        for head, gloss, pos in rows:
            out.write(f"{head}\t{gloss}\tfr\t{pos}\n")
    print(f"{OUT.name}: {len(rows)} rows, {len({r[0] for r in rows})} headwords")
    print("  entries read", stats["read"], "| dropped: readings disagree", stats["disagree"], "| letters", stats["letters"],
          "| gloss", stats["gloss"], "| out of alphabetical run", stats["order"],
          "" if forms is not None else "| French form list not found: glosses unchecked")


if __name__ == "__main__":
    main()
