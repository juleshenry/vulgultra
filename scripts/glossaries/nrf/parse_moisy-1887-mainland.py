#!/usr/bin/env python3
"""Moisy, Dictionnaire de patois normand ... en usage dans la region centrale
de la Normandie (1887) -> headword/gloss table. Mainland Norman (Calvados,
Orne, Eure: Moisy's "region centrale").

Two OCR readings of the archive.org scan `normand_moisy` are compared:
  raw/moisy-1887_tesseract-fra.txt   Tesseract (French model, automatic
                                     two-column layout), made by ocr_tesseract.py
  raw/normand_centre_djvu.txt        the ABBYY text archive.org offers

An entry reads `[2. ]Headword[, variant], s. m., definition. Notes.` and is
followed by quotations from old texts, which are not glosses and are cut: the
gloss is the definition up to the first full stop, colon or cross-reference.
Headword, word class and gloss are taken from the Tesseract reading.

Kept only when all of this holds, so that OCR damage stays out:
  * the ABBYY reading has a headword that is letter for letter the same from
    the second letter on (the bold capital C of this book is read as G by
    both programs, in different places, so the first letter is not compared
    but checked by the next rule);
  * the headword fits the alphabetical run of its neighbours (first two
    letters, accents ignored): a C-word read as "G..." falls out here and is
    dropped, not repaired;
  * the headword has no digit, no capital inside the word, no stray sign;
  * every word of the gloss is a known French form (checked against the
    repository's data/sources/kaikki_full/fr_forms.tsv and fr.jsonl when
    present), which removes glosses the OCR damaged.
Headwords keep the book's spelling; only the capital initial is lower-cased.
The reflexive marker `(se)` / `(s')` is dropped; other particles in
parentheses stay as printed (`cache (en)`).

    python3 parse_moisy-1887-mainland.py
"""
from __future__ import annotations

import bisect
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
TESSERACT = HERE / "raw" / "moisy-1887_tesseract-fra.txt"
ABBYY = HERE / "raw" / "normand_centre_djvu.txt"
OUT = HERE / "moisy-1887-mainland.tsv"
FRENCH = HERE.parents[1] / "kaikki_full"

LETTERS = "A-Za-zÀ-ÖØ-öø-ÿŒœ"
WORD = rf"[{LETTERS}][{LETTERS}'’\-]*"
TERM = rf"{WORD}(?: {WORD}){{0,2}}(?: ?\([^)]{{1,25}}\))?"
# Word-class abbreviations as either OCR returns them (s. m. -> "s, m.", "5. m.", "s. /.", "v. @." ...).
POS_OCR = (r"(?:[sS58«*^][.,] ?(?:[mf/@]|et)[^,]{0,12}|[vVrt▼][?]?[.,] ?(?:a|n|@|r[ée]fl|pron|imp|unip)[^,]{0,12}|"
           r"adj[.,]?[^,]{0,10}|adv[.,]?[^,]{0,10}|loc[.,] ?[a-z]{2,5}[.,]?|pr[ée]p[.,]?|pron[.,]?[^,]{0,25}|conj[.,]?|"
           r"interj[.,]?|part[.,]?[^,]{0,10}|art[.,]?[^,]{0,10}|nom propre)")
HEAD = re.compile(rf"^(?:\d ?[.,] ?)?({TERM}(?: ?, ?{TERM}){{0,3}}) ?, ?({POS_OCR}) ?[,.]? ?(.*)$")
POS = [(r"^loc[.,] ?adv|^adv", "adv"), (r"^loc[.,] ?adj|^adj|^part", "adj"), (r"^loc[.,] ?pr|^pr[ée]p", "prep"),
       (r"^loc[.,] ?conj|^conj", "conj"), (r"^pron", "pron"), (r"^[sS58«*^]", "noun"), (r"^[vVrt▼]", "verb")]
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
    for token in re.findall(rf"[{LETTERS}]+", gloss):
        low = token.lower()
        if len(low) > 1 and low not in ELIDED and low not in forms and low.replace("oe", "œ") not in forms:
            return False
    return True


def dictionary_lines(path: Path) -> list[str]:
    text = unicodedata.normalize("NFC", path.read_text(encoding="utf-8")).replace("ﬁ", "fi").replace("ﬂ", "fl")
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.split("\n")]
    start = next(i for i, line in enumerate(lines) if re.match(r"^A est usit", line))
    end = next((i for i, line in enumerate(lines) if i > start and re.fullmatch(r"SUPPL[ÉE]MENT\.?", line)), len(lines))
    return lines[start:end]


def split_heads(text: str) -> list[str] | None:
    heads = []
    for term in re.split(r"\s*,\s*", text):
        term = re.sub(r"\s*\((?:se|s['’])\)", "", term).strip()
        bare = re.sub(r"\([^)]*\)", "", term)
        if not term or re.search(r"\d", term) or sum(ch.isupper() for ch in bare[1:]) > 0 or len(key(bare)) < 2:
            return None
        heads.append(term)
    if not heads or not heads[0][0].isupper():
        return None
    return heads


def entries(path: Path):
    """([headwords], word class, text after the word class) per entry line of one reading."""
    lines = dictionary_lines(path)
    for index, line in enumerate(lines):
        found = HEAD.match(line)
        if not found:
            continue
        heads = split_heads(found.group(1))
        if not heads:
            continue
        body = found.group(3)
        extra = 1
        while not re.search(r"[.:](?:\s|$)", body) and extra <= 3 and index + extra < len(lines):
            nxt = lines[index + extra]
            if not nxt or HEAD.match(nxt):
                break
            body = body[:-1] + nxt if body.endswith("-") else body + " " + nxt
            extra += 1
        yield heads, found.group(2), body


def gloss_of(body: str) -> str:
    body = re.split(r"[.:](?=\s|$)|,? [vV▼]\. [A-ZÀ-Þ]|\s[—–]\s", body)[0]
    return re.sub(r"\s+", " ", body).strip(" .;,:«»")


def main() -> None:
    if not TESSERACT.is_file():
        raise SystemExit(f"missing {TESSERACT.name}: run ocr_tesseract.py (see its docstring) first")
    tails = {head[1:] for heads, _, _ in entries(ABBYY) for head in heads}
    forms = french_forms()
    stats = {"read": 0, "disagree": 0, "gloss": 0}
    candidates = []
    for heads, pos_text, body in entries(TESSERACT):
        stats["read"] += 1
        if any(head[1:] not in tails for head in heads):
            stats["disagree"] += 1
            continue
        gloss = gloss_of(body)
        if (not gloss or len(gloss) > 160 or not known(gloss, forms)
                or re.match(r"(?i)^(se dit|s[’']emploie|voy|v\.|même sens|mot qui|l[’']on (?:dit|prononce))\b", gloss)):
            stats["gloss"] += 1
            continue
        pos = next((name for pattern, name in POS if re.search(pattern, pos_text)), "other")
        candidates.append((heads, pos, gloss))

    keys = [key(c[0][0])[:2] for c in candidates]
    run, run_index, previous = [], [], {}
    for n, value in enumerate(keys):
        at = bisect.bisect_right(run, value)
        if at == len(run):
            run.append(value); run_index.append(n)
        else:
            run[at] = value; run_index[at] = n
        previous[n] = run_index[at - 1] if at else None
    keep, n = set(), run_index[-1] if run_index else None
    while n is not None:
        keep.add(n)
        n = previous[n]

    rows, seen = [], set()
    for i, (heads, pos, gloss) in enumerate(candidates):
        if i not in keep:
            continue
        for head in heads:
            row = (head[0].lower() + head[1:], gloss, pos)
            if row not in seen:
                seen.add(row)
                rows.append(row)
    with OUT.open("w", encoding="utf-8") as out:
        out.write("headword\tgloss\tgloss_lang\tpos\n")
        for head, gloss, pos in rows:
            out.write(f"{head}\t{gloss}\tfr\t{pos}\n")
    print(f"{OUT.name}: {len(rows)} rows, {len({r[0] for r in rows})} headwords")
    print("  entries read", stats["read"], "| dropped: readings disagree", stats["disagree"], "| gloss", stats["gloss"],
          "| out of alphabetical run", len(candidates) - len(keep),
          "" if forms is not None else "| French form list not found: glosses unchecked")


if __name__ == "__main__":
    main()
