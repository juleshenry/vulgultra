#!/usr/bin/env python3
"""Fleury, Essai sur le patois normand de la Hague (1886), Glossaire
etymologique -> headword/gloss table.

Source: raw/essisurlepatoisn00fleuuoft_djvu.txt (archive.org OCR). Mainland
Norman of La Hague (north-west Cotentin, Manche), in Fleury's own spelling
(`abillotâë`, `môuëji'ei`), which is kept exactly as the OCR returns it.

An entry reads `Headword[, variant], s. m., gloss. — R. etymon.` followed by
indented examples in patois.

Left out, to keep OCR damage away from the headwords: headwords that break
the alphabetical run of their neighbours (first two letters, accents
ignored), headwords with a digit, a capital inside the word or stray
punctuation, and entries whose definition is only a usage note. The
reflexive marker `(s')` / `(se)` is dropped; another particle in parentheses
stays as printed (`abanoun (à l')`). The gloss is the definition up to the
first full stop or the `— R.` etymology; examples are cut.

    python3 parse_fleury-1886-hague.py
"""
from __future__ import annotations

import bisect
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw" / "essisurlepatoisn00fleuuoft_djvu.txt"
OUT = HERE / "fleury-1886-hague.doubtful.tsv"

LETTERS = "A-Za-zÀ-ÖØ-öø-ÿŒœ"
WORD = rf"[{LETTERS}][{LETTERS}'’\-]*"
TERM = rf"{WORD}(?: {WORD}){{0,3}}(?: ?\([^)]{{1,14}}\))?"
POS_PART = (r"(?:s\. ?[mf]\.?(?: ?pl\.?)?|[vV]\. ?(?:a|n|pr|r|imp|impers|unip)\.?|adj\.?|adv\.?|loc\. ?(?:adv|pr[ée]p|conj)?\.?|"
            r"pr[ée]p\.?|pron\.?|conj\.?|interj\.?|part\.?(?: ?pass[ée]?)?\.?|n\. ?de nombre|art\.?)")
HEAD = re.compile(rf"^({TERM}(?:, ?{TERM}){{0,3}}) ?, ?({POS_PART}(?:(?: et | ou |, ?){POS_PART})*) ?[,.:]? ?(.*)$")
POS = [(r"^s", "noun"), (r"^[vV]", "verb"), (r"^adj", "adj"), (r"^adv|^loc\. ?adv", "adv"), (r"^pr[ée]p|^loc\. ?pr", "prep"),
       (r"^pron", "pron"), (r"^conj|^loc\. ?conj", "conj"), (r"^n\.", "num"), (r"^part", "adj")]


def key(word: str) -> str:
    plain = unicodedata.normalize("NFD", word.lower())
    return "".join(ch for ch in plain if "a" <= ch <= "z")


def lines() -> list[str]:
    text = RAW.read_text(encoding="utf-8").split("\n")
    start = next(i for i, line in enumerate(text) if re.match(r"GLOSSAIRE\s+ÉTYMOLOGIQUE", line.strip()))
    end = next(i for i, line in enumerate(text) if i > start and "PREMIÈRE" in line and "PHONÉTIQUE ET FLEXION" in re.sub(r"\s+", " ", line))
    return [re.sub(r"\s+", " ", line).strip() for line in text[start + 1:end]]


def raw_entries():
    current = None
    for line in lines():
        if not line or re.fullmatch(r"[—\-–\s\d]+", line):
            continue
        found = HEAD.match(line)
        if found and found.group(1)[0].isupper():
            if current:
                yield current
            current = [found.group(1), found.group(2), found.group(3)]
        elif current:
            current[2] = current[2][:-1] + line if current[2].endswith("-") else current[2] + " " + line
    if current:
        yield current


def gloss_of(body: str) -> str:
    body = re.split(r"\s*[—–]\s*R\b|\sR\. ", body)[0]
    body = re.split(r"\.(?=\s|$)", body)[0]
    body = re.sub(r"\s+", " ", body).strip(" .;,:—–-")
    return body


def main() -> None:
    candidates = []
    for head, pos_text, body in raw_entries():
        heads = []
        for term in re.split(r"\s*,\s*", head):
            term = re.sub(r"\s*\((?:s['’]|se)\)", "", term).strip()
            bare = re.sub(r"\([^)]*\)", "", term)
            if not term or re.search(r"\d", term) or sum(ch.isupper() for ch in bare[1:]) > 0:
                heads = []
                break
            heads.append(term)
        gloss = gloss_of(body)
        if not heads or not gloss or len(gloss) > 160:
            continue
        if re.match(r"(?i)^(s[’']emploie|se dit|voy|v\.|ce mot|même sens|mot qui|usité)\b", gloss):
            continue
        pos = next((name for pattern, name in POS if re.search(pattern, pos_text)), "other")
        candidates.append((heads, pos, gloss))

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

    rows, seen = [], set()
    for i, (heads, pos, gloss) in enumerate(candidates):
        if i not in keep:
            continue
        for head in heads:
            head = unicodedata.normalize("NFC", head[0].lower() + head[1:])
            row = (head, gloss, pos)
            if row not in seen:
                seen.add(row)
                rows.append(row)
    with OUT.open("w", encoding="utf-8") as out:
        out.write("headword\tgloss\tgloss_lang\tpos\n")
        for head, gloss, pos in rows:
            out.write(f"{head}\t{gloss}\tfr\t{pos}\n")
    print(f"{OUT.name}: {len(rows)} rows, {len({r[0] for r in rows})} headwords "
          f"({len(candidates)} entries read, {len(keep)} kept)")


if __name__ == "__main__":
    main()
