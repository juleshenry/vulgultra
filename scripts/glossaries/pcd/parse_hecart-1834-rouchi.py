#!/usr/bin/env python3
"""Hécart, Dictionnaire rouchi-français, 3rd ed. (Valenciennes, 1834) -> headword/gloss table.

Rouchi is the Picard of Valenciennes and the French Hainaut.

Source text: raw/dictionnairerouc00hcuoft_tesseract.txt, our own Tesseract 5
re-OCR (see reocr.py) of the archive.org scan `dictionnairerouc00hcuoft`
(University of Toronto copy). The OCR text archive.org itself serves
(raw/dictionnairerouc00hcuoft_djvu.txt) is too noisy in the headwords.

An entry starts on a line `HEADWORD, gloss.` (headword in capitals; a phrase
may follow in lower case: `ADON come adon, alors comme alors`; an inverted
particle may follow in brackets: `ACRAPER [s'], ...`).

What the script keeps and drops:
  * headwords are lower-cased (the book prints them in capitals); nothing
    else is changed. The reflexive `[s']`/`[se]` is dropped, other bracketed
    particles stay as printed after the headword.
  * guards against OCR-garbled headwords: a headword must be made of
    letters, apostrophes, hyphens and spaces; it must fit the alphabetical
    run of its neighbours (first three letters, accents ignored); and it
    must be confirmed by a second, independent OCR reading: every word of
    it has to occur in archive.org's own OCR text of the same scan
    (accents ignored). A single-word headword that fails only this last
    test is still kept when all its letter trigrams are common among the
    confirmed headwords; everything else is dropped.
  * gloss = the first sentence after the headword (and after the part of
    speech, if given); examples, quotations, etymologies are cut; entries
    that are only a cross-reference ("V. Fachon.") are dropped.

    python3 parse_hecart-1834-rouchi.py
"""
from __future__ import annotations

import bisect
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw" / "dictionnairerouc00hcuoft_tesseract.txt"
WITNESS = HERE / "raw" / "dictionnairerouc00hcuoft_djvu.txt"     # archive.org's own OCR, a second reading
OUT = HERE / "hecart-1834-rouchi.doubtful.tsv"

UP = "A-ZÀ-ÖØ-ÞŒÆ"
LOW = "a-zà-öø-ÿœæ"
CAPS = rf"[{UP}][{UP}'’\-]*"
ENTRY = re.compile(
    rf"^(?P<caps>{CAPS}(?: {CAPS})*)"                      # HEADWORD (may be several capitalised words)
    rf"(?P<tail>(?: (?:[{LOW}'’\-]+|{CAPS})){{0,5}})"       # ... rest of a phrase
    rf"\s*(?P<part>[\[(][^\])]{{1,40}}[\])])?"             # [s'] (envoyer)
    rf"\s*(?P<sep>[,;]|\.(?= ))\s*(?P<body>\S.*)$")
D = r"[.,]"                       # the OCR often reads the full stop of an abbreviation as a comma
POS = [
    (rf"s{D} ?m{D} ?(?:et|ou) ?f{D}|s{D} ?[mf]{D}(?: ?pl{D})?|subst{D} ?(?:[mf]{D})?", "noun"),
    (rf"v{D} ?(?:a|n|r[ée]fl|pron|imp){D}(?: et ?[an]{D})?|verbe", "verb"),
    (rf"adj{D}(?: ?(?:des 2 g|[mf]){D})?", "adj"), (rf"adv{D}|loc{D} ?adv{D}|adverbe", "adv"),
    (rf"pr[ée]p{D}", "prep"), (rf"conj{D}", "conj"), (rf"pron{D}(?: ?(?:pers|poss|d[ée]m|rel|ind){D})?", "pron"),
    (rf"interj{D}|interjection|art{D}|part{D}", "other"),
]
POS_RE = re.compile(r"^(?:" + "|".join(f"(?P<p{i}>{p})" for i, (p, _) in enumerate(POS)) + r")[\s,]*", re.I)
ABBREVIATIONS = r"(?:\b(?:M|MM|Mme|St|Ste|etc|ex|v|V|p|pag|art|chap|tom|t|s|m|f|a|n|lat|fr|esp|ital|angl|all|cf|c\.-à-d)|\b[A-Z])$"


def fold(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower().replace("œ", "oe").replace("æ", "ae"))
    return re.sub(r"[^a-z]", "", "".join(c for c in text if not unicodedata.combining(c)))


def lines_of(path: Path):
    """The lines of the dictionary proper: from the first page headed ABA onwards."""
    lines = path.read_text(encoding="utf-8").split("\n")
    start = next((i for i, line in enumerate(lines) if line.strip() == "ABA"), 0)
    while start and not lines[start].startswith("=== leaf"):
        start -= 1
    for raw in lines[start:]:
        if not raw.startswith("=== leaf"):
            yield re.sub(r"\s+", " ", raw.replace("’", "'")).replace(" ,", ",").strip()


def raw_entries(path: Path):
    """(match of the entry's first line, the rest of its text) in page order."""
    current, rest = None, []
    for line in lines_of(path):
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
        broken = re.search(r"[^\W\d_][-—–]$", text) and line[:1].islower()     # a word split at the line end
        text = text[:-1] + line if broken else text + " " + line
    return text


def words_of(head: str) -> list[str]:
    return re.sub(r"\(.*?\)", " ", head).split()


def trusted(heads: list[str]) -> set[str]:
    """The headwords a second OCR reading confirms, or whose letter sequences are all ordinary."""
    witness = WITNESS.read_text(encoding="utf-8")
    attested = {fold(token) for token in re.findall(r"[^\W\d_]+(?:['’\-][^\W\d_]+)*", witness)}
    confirmed = {h for h in heads if words_of(h) and all(fold(w) in attested for w in words_of(h))}
    trigrams: dict[str, int] = {}
    for head in confirmed:
        for word in words_of(head):
            padded = f"^{word}$"
            for i in range(len(padded) - 2):
                trigrams[padded[i:i + 3]] = trigrams.get(padded[i:i + 3], 0) + 1
    ordinary = set()
    for head in set(heads) - confirmed:
        parts = words_of(head)
        if len(parts) == 1 and len(parts[0]) >= 3:
            padded = f"^{parts[0]}$"
            if all(trigrams.get(padded[i:i + 3], 0) >= 2 for i in range(len(padded) - 2)):
                ordinary.add(head)
    return confirmed | ordinary


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
    gloss = re.split(r"\s*[«»]|\s+—\s*|\s*-—\s*", gloss)[0]
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
        caps, tail, part = found.group("caps"), found.group("tail") or "", found.group("part")
        body = join(found.group("body"), rest)
        heads = [caps + tail]
        variant = re.match(rf"^({CAPS}) (?:ou|et) ({CAPS})$", (caps + tail).strip())
        if variant:
            heads = [variant.group(1), variant.group(2)]
        pos = ""
        marked = POS_RE.match(body)
        if marked:
            pos = next(name for i, (_, name) in enumerate(POS) if marked.group(f"p{i}"))
            body = body[marked.end():]
        gloss = shorten(first_sentence(body))
        if not gloss or re.match(r"(?i)^(?:v|voy|voyez)\b[. ]", gloss + " ") or not re.search(rf"[{LOW}]{{3}}", gloss):
            continue
        if part and not re.fullmatch(r"[\[(]\s*(?:se|s')\s*[\])]", part, re.I):
            heads = [f"{h} ({part.strip('[]() ')})" for h in heads]
        parsed.append((heads, gloss, pos, fold(caps)[:3]))
    keep = alphabetical([p[3] for p in parsed])
    rows, seen, dropped, unconfirmed = [], set(), 0, 0
    lowered = [[unicodedata.normalize("NFC", h.lower().strip()) for h in p[0]] for p in parsed]
    good = trusted([h for heads, fits in zip(lowered, keep) if fits for h in heads])
    for heads, (_, gloss, pos, _), fits in zip(lowered, parsed, keep):
        if not fits:
            dropped += 1
            continue
        for head in heads:
            if head not in good:
                unconfirmed += 1
                continue
            if (head, gloss) not in seen:
                seen.add((head, gloss))
                rows.append((head, gloss, pos))
    with OUT.open("w", encoding="utf-8") as out:
        out.write("headword\tgloss\tgloss_lang\tpos\n")
        for head, gloss, pos in rows:
            out.write(f"{head}\t{gloss}\tfr\t{pos}\n")
    print(f"{OUT.name}: {len(rows)} rows, {len({r[0] for r in rows})} headwords; "
          f"{dropped} entries left out as not fitting the alphabetical run, "
          f"{unconfirmed} headwords as not confirmed by the second OCR reading")


if __name__ == "__main__":
    main()
