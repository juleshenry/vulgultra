#!/usr/bin/env python3
"""Coulabin, Dictionnaire des locutions populaires du bon pays de Rennes-en-Bretagne (1891)
-> headword/gloss table.

Sources: raw/dictionnairedesl00couluoft_djvu.txt (archive.org OCR, ABBYY
FineReader) and ocr/coulabin-1891_tesseract-fra.txt (a second OCR of the same
page scans, made by ocr_coulabin-1891-rennes.py).

An entry is `Headword[, fem. ending][ (s')], v. a., definition. — Ex.: ...`.
It is often followed by a paragraph of look-alikes from other dictionaries
(`NORM.: abominer, détester. — BESCH.: ...`, `Vieux Fr.: ...`): those are
Norman, Sarthe or Old French words, not Rennes ones, and are never read as
entries (an entry must give a part of speech right after its headword).
The gloss is the definition up to the first full stop, dash or example;
entries whose text is only a remark ("vient de ...", "syn. de ...") are
skipped. The book records the popular speech of Rennes, Gallo words and
regional French alike, and says of some words that they are French.

Headwords keep the book's spelling, without the initial capital that the
book gives every headword. Because both texts are OCR, a headword is
accepted only if
  * it is made of letters, hyphens and apostrophes, with no capital or
    digit inside;
  * the two OCR engines read it identically;
  * it fits the alphabetical run of the entries around it (the longest
    non-decreasing run of the ABBYY text is kept).

    python3 parse_coulabin-1891-rennes.py
"""
from __future__ import annotations

import bisect
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ABBYY = HERE / "raw" / "dictionnairedesl00couluoft_djvu.txt"
TESSERACT = HERE / "ocr" / "coulabin-1891_tesseract-fra.txt"
OUT = HERE / "coulabin-1891-rennes.doubtful.tsv"

UP = "A-ZÀ-ÖØ-Þ"
LOW = "a-zà-öø-ÿœ"
WORD = rf"[{UP}][{LOW}]+(?:['’\-][{UP}{LOW}]?[{LOW}]+)*"
POS = (r"(?:[sS][.,] ?[mfti][.,]? ?(?:et ?[mf]\. ?)?(?:p[li]\.)?|[sS]\.(?: ?p[li]\.)?|"
       r"[vV]\. ?(?:a|n|pr|pron|prou|imp|r[ée]fl)\.|adj\.(?: ?[mf]\.)?|adv\.|loc\.(?: ?adv\.| ?pop(?:ul)?\.)?|"
       r"pr[ée]p\.|conj\.|pron\.(?: ?pers\.)?|int(?:erj)?\.|excl\.|part\.)")
ENTRY = re.compile(
    rf"^({WORD}(?: (?:ou|et) {WORD})?)"
    rf"(?:, ?[{LOW}]{{1,6}})?"                       # feminine ending: Achaisonnoux, se
    rf"(?:,? ?\([Ss](?:['’]|e)\))?"                  # reflexive (s')
    rf"[,.]? ?({POS})[,.]?\s*(.*)$")
POS_MAP = [(r"(?i)^s", "noun"), (r"(?i)^v", "verb"), (r"^adj", "adj"), (r"^adv|^loc\. ?adv", "adv"),
           (r"^pr[ée]p", "prep"), (r"^conj", "conj"), (r"^pron", "pron"), (r"^int|^excl|^loc|^part", "other")]
SKIP_GLOSS = re.compile(r"(?i)^(?:voy|v\. |vient|venant|dont |pour |syn|c['’]est|est |ce mot|ce verbe|ce terme|mot |"
                        r"terme|expression|locution|employ|usité|s['’]emploie|on dit|on appelle|se prononce|du (?:latin|verbe|vieux)|"
                        r"de l['’]|dérivé|diminutif|augmentatif|corruption|contraction|abréviation|même|"
                        r"a (?:le|la) même|signifie aussi|en français|français|vieux)")
ABBREV = r"(?:\b(?:M|MM|Mme|St|Ste|etc|V|v|p|s|c\.-à-d)|\b[A-Z])$"


def fold(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower().replace("œ", "oe"))
    return re.sub(r"[^a-z]", "", "".join(c for c in text if not unicodedata.combining(c)))


def entries(text: str):
    """(headwords, part of speech, entry text) for each entry line of an OCR text."""
    current = None
    for line in text.split("\n"):
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            continue
        found = ENTRY.match(line)
        if found:
            if current:
                yield current
            current = [found.group(1), found.group(2), found.group(3)]
        elif current is not None:
            if re.match(r"^(?:[A-ZÉ]{3,}|Vieux Fr)\b\.? ?:|^[—–-] ?\w{1,3} ?[—–-]$|^=== page", line):
                yield current           # the comparison paragraph, a page number: the entry is over
                current = None
                continue
            body = current[2]
            current[2] = body[:-1] + line if body.endswith("-") and not body.endswith(" -") else body + " " + line
    if current:
        yield current


def first_clause(body: str) -> str:
    position = 0
    while True:
        found = re.search(r"\.(?=\s|$)|[«»]|\s[—–]\s|\(Voy|\bEx\b|\s:\s|;\s*syn\b", body[position:])
        if not found:
            return body
        end = position + found.start()
        if found.group(0) == "." and re.search(ABBREV, body[:end]):
            position = end + 1
            continue
        return body[:end]


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
    abbyy_text = ABBYY.read_text(encoding="utf-8")
    abbyy_text = abbyy_text[abbyy_text.index("Abècher"):]
    first = list(entries(abbyy_text))
    second = {head for heads, _, _ in entries(TESSERACT.read_text(encoding="utf-8"))
              for head in re.split(r" (?:ou|et) ", heads)}
    keep = longest_run([fold(re.split(r" (?:ou|et) ", heads)[0]) for heads, _, _ in first])
    rows, seen = [], set()
    stats = {"entries": len(first), "out_of_order": 0, "not_confirmed": 0, "no_gloss": 0}
    for index, (heads, pos_text, body) in enumerate(first):
        if index not in keep:
            stats["out_of_order"] += 1
            continue
        gloss = re.sub(r"\s+([,;])", r"\1", first_clause(body.lstrip(" —–-"))).strip(" .,;:(—–-")
        gloss = re.sub(r"^pour (?=[\w'’ -]{3,40}$)", "", gloss)          # "Bêchée, s. f., pour becquée"
        if (not gloss or SKIP_GLOSS.match(gloss) or gloss.count("(") != gloss.count(")")
                or re.search(r"[^\w ,;'’()\-]|\d", gloss) or not re.match(rf"[{LOW}]", gloss)):
            stats["no_gloss"] += 1
            continue
        if len(gloss) > 160:
            gloss = gloss[:160].rsplit(",", 1)[0] if "," in gloss[60:160] else gloss[:160].rsplit(" ", 1)[0]
        pos = next((name for pattern, name in POS_MAP if re.search(pattern, pos_text)), "")
        for head in re.split(r" (?:ou|et) ", heads):
            if head not in second:
                stats["not_confirmed"] += 1
                continue
            key = (unicodedata.normalize("NFC", head[0].lower() + head[1:]), gloss, pos)
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
