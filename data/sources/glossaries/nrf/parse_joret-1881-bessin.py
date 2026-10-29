#!/usr/bin/env python3
"""Joret, Essai sur le patois normand du Bessin, suivi d'un dictionnaire
etymologique (1881) -> headword/gloss table.

Source: raw/essaisurlepatois00joreuoft_djvu.txt (archive.org OCR). Mainland
Norman of the Bessin (Calvados), in Joret's own phonetic spelling, which is
kept exactly (including optional letters in parentheses: `anbroqu(i)é`).

An entry reads `Headword[, variant], s. f. : gloss. Example. R. etymon.`;
`D. Derived, s. m. : gloss` lists a derivative under its base word.

Left out, to keep OCR damage away from the headwords:
  * headwords the book prints in small capitals (the OCR returns them in
    mixed case with frequent letter errors);
  * headwords carrying the book's dagger (words Joret calls doubtful,
    obsolete or not collected by himself), whatever the OCR made of the sign;
  * headwords that break the alphabetical run of their neighbours (first two
    letters, accents ignored), and derivatives that do not share the first
    letter of their base word;
  * headwords with a digit or stray punctuation.
A leading `*` (word shared with or borrowed from French) is dropped, the word
kept. The reflexive marker `(s')` is dropped. The gloss is the definition
before the first example, `R.` (root) or cross-reference; `1° ... 2° ...`
senses become one row each.

    python3 parse_joret-1881-bessin.py
"""
from __future__ import annotations

import bisect
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw" / "essaisurlepatois00joreuoft_djvu.txt"
OUT = HERE / "joret-1881-bessin.doubtful.tsv"

LETTERS = "A-Za-zÀ-ÖØ-öø-ÿŒœ"
WORD = rf"[{LETTERS}][{LETTERS}'’()\-]*"
POS_PART = r"(?:s\. ?[mfv]\.?(?: ?pl\.?)?|s\.|[vVyY]\. ?[anrip]\.?|ad\.|a\.|p\. ?p\.|pr[ée]p\.|pr\.|cj\.|int\.|loc\.[^:]{0,12}|n\. ?de n[^:]{0,8}|art\.)"
HEAD = re.compile(
    rf"^(D\. ?)?([^{LETTERS}]{{0,5}}[fij]?(?=[A-ZÀ-ÖØ-ÞŒ]))?({WORD}(?: ?\([^)]{{1,12}}\))?(?:, ?{WORD}(?: ?\([^)]{{1,12}}\))?)*) ?, ?"
    rf"((?:\d° ?)?{POS_PART}(?:(?: et |, ?| ou ){POS_PART})*) ?:(.*)$")
POS = [(r"^(?:\d° ?)?s", "noun"), (r"^(?:\d° ?)?[vVyY]", "verb"), (r"^(?:\d° ?)?ad", "adv"), (r"^(?:\d° ?)?a\.", "adj"),
       (r"^(?:\d° ?)?p\. ?p", "adj"), (r"^pr[ée]p", "prep"), (r"^pr", "pron"), (r"^cj", "conj"), (r"^n\.", "num")]


def key(word: str) -> str:
    plain = unicodedata.normalize("NFD", word.lower())
    return "".join(ch for ch in plain if "a" <= ch <= "z")


def lines() -> list[str]:
    text = RAW.read_text(encoding="utf-8").split("\n")
    start = next(i for i, line in enumerate(text) if "DICTIONNAIRE" in line and "TYMOLOGIQUE^" in line)
    return [re.sub(r"\s+", " ", line).strip() for line in text[start:]]


def raw_entries():
    """(is derivative, mark, head text, pos text, body) with continuation lines joined."""
    current = None
    for line in lines():
        if not line or re.search(r"JORET\.? ?[—-]|PATOIS NORMAND", line) or re.fullmatch(r"[\d ]+", line):
            continue
        found = HEAD.match(line)
        if found:
            if current:
                yield current
            current = [bool(found.group(1)), (found.group(2) or "").strip(), found.group(3), found.group(4), found.group(5)]
        elif current:
            if re.match(r"^\d+\. ", line):          # a footnote closes the entry
                yield current
                current = None
            elif current[4].endswith("-"):
                current[4] = current[4][:-1] + line
            else:
                current[4] += " " + line
    if current:
        yield current


def gloss_of(body: str) -> list[str]:
    body = re.split(r"\s(?:R\.|V\.|Cf\.|D\.|—)\s", " " + body + " ")[0]
    body = re.sub(r"[*^]", "", body).strip()
    senses = [s for s in re.split(r"\s*\d ?°\s*", body) if s.strip()] if re.search(r"\d ?°", body) else [body]
    out = []
    for sense in senses:
        sense = re.split(r"\.(?=\s|$)", sense)[0]          # first sentence: the definition
        sense = re.sub(r"\s+", " ", sense).strip(" .;,:…")
        if sense and len(sense) <= 160 and not re.search(r"\b[a-z]$", sense[-2:]) or sense:
            if sense and len(sense) <= 160:
                out.append(sense)
    return out


def main() -> None:
    candidates = []                    # (is derivative, [heads], pos, [glosses])
    for derived, mark, head, pos_text, body in raw_entries():
        if mark.replace("*", "").strip():
            continue                   # dagger (any OCR shape): doubtful or obsolete word
        heads = []
        for term in re.split(r"\s*,\s*", head):
            term = re.sub(r"\s*\((?:s['’]|se)\)", "", term).strip()
            if not term or re.search(r"\d", term) or sum(ch.isupper() for ch in term[1:]) > 0:
                heads = []
                break                  # small capitals or a damaged head: skip the entry
            heads.append(term)
        if not heads:
            continue
        pos = next((name for pattern, name in POS if re.search(pattern, pos_text)), "other")
        glosses = gloss_of(body)
        if glosses:
            candidates.append((derived, heads, pos, glosses))

    # Alphabetical run of the main entries (longest non-decreasing run of 2-letter keys);
    # the addenda at the end restart the alphabet, so the run is taken per pass.
    keep = [False] * len(candidates)
    mains = [i for i, c in enumerate(candidates) if not c[0]]
    keys = [key(candidates[i][1][0])[:2] for i in mains]
    restart = next((n for n in range(len(keys) - 1, 0, -1)
                    if keys[n] < keys[n - 1] and keys[n] <= "ap" and keys[n - 1] >= "v"), len(keys))
    for lo, hi in ((0, restart), (restart, len(keys))):
        tails, tail_index, previous = [], [], {}
        for n in range(lo, hi):
            at = bisect.bisect_right(tails, keys[n])
            if at == len(tails):
                tails.append(keys[n]); tail_index.append(n)
            else:
                tails[at] = keys[n]; tail_index[at] = n
            previous[n] = tail_index[at - 1] if at else None
        n = tail_index[-1] if tail_index else None
        while n is not None:
            keep[mains[n]] = True
            n = previous[n]
    base = ""
    for i, (derived, heads, _, _) in enumerate(candidates):
        if not derived:
            base = key(heads[0])[:1] if keep[i] else ""
        else:
            keep[i] = bool(base) and key(heads[0])[:1] == base

    rows, seen = [], set()
    for i, (derived, heads, pos, glosses) in enumerate(candidates):
        if not keep[i]:
            continue
        for head in heads:
            head = unicodedata.normalize("NFC", head[0].lower() + head[1:])
            for gloss in glosses:
                row = (head, gloss, pos)
                if row not in seen:
                    seen.add(row)
                    rows.append(row)
    with OUT.open("w", encoding="utf-8") as out:
        out.write("headword\tgloss\tgloss_lang\tpos\n")
        for head, gloss, pos in rows:
            out.write(f"{head}\t{gloss}\tfr\t{pos}\n")
    print(f"{OUT.name}: {len(rows)} rows, {len({r[0] for r in rows})} headwords "
          f"({len(candidates)} entries read, {sum(keep)} kept)")


if __name__ == "__main__":
    main()
