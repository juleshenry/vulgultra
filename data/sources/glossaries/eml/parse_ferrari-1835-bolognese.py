#!/usr/bin/env python3
"""Ferrari 1835, *Vocabolario bolognese-italiano, colle voci francesi corrispondenti*
raw/b33521621_djvu.txt  ->  ferrari-1835-bolognese.scan.tsv

archive.org item b33521621 (Wellcome Library scan, Public Domain Mark; the text
is archive.org's Tesseract reading). The printed entry:

    DURMIACCIAR, v. Dormicchiare, Dormigliare, Sonnecchiare, v. Leggiermente dormire (Sommeiller).
    DUPPIÈZZA, n. f. Addoppiamento. Doppiamento. Raddoppiamento, n. m. Il raddoppiare ...
    PDA. V. Pinca.

a Bolognese headword in capitals, sometimes its part of speech, then the Italian
equivalents (each a capitalised word, set off by commas or full stops), then
prose. Rows keep the equivalents only; "V. x" sends the reader elsewhere and is
left out.

The file is named .scan because of one known fault: the reading drops the grave
accent on a capital (the page has DUPPIÈZZA, the reading DUPPIEZZA; checked on
leaf 300, where every headword was otherwise right, and a second reading with
the Italian model drops it too). So a headword here is the right word, in lower
case, but may lack an accent the book prints.

    python3 parse_ferrari-1835-bolognese.py
"""
import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "raw", "b33521621_djvu.txt")
TARGET = os.path.join(HERE, "ferrari-1835-bolognese.scan.tsv")
CAPITALS = "A-ZÀÈÉÌÒÙÂÊÎÔÛÄËÏÖÜ"
START = re.compile(rf"^([{CAPITALS}]{{2,}})\s*([,.])\s+(.*)$")
RUNNING_HEAD = re.compile(rf"^[{CAPITALS}]{{2,4}}(?:\s+\d+)?\s*$|^\d+\s+[{CAPITALS}]{{2,4}}\s*$")
TAG = re.compile(r"^(v|n\.\s*[mf{]|s\.\s*[mf]|add|agg|avv|prep|cong|inter|pron|m|f)\.\s*", re.I)
POS = (("v", "verb"), ("n", "noun"), ("s", "noun"), ("m", "noun"), ("f", "noun"), ("ad", "adj"), ("ag", "adj"),
       ("av", "adv"), ("prep", "prep"), ("cong", "conj"), ("pron", "pron"))
WORD = re.compile(r"[A-ZÀ-Ü][a-zà-ü']+(?:\s[a-zà-ü']+)?")


def entries():
    """(headword, the text after it up to the next headword)."""
    head, body = None, []
    with open(SOURCE, encoding="utf-8", errors="replace") as stream:
        for line in stream:
            line = line.rstrip()
            if RUNNING_HEAD.match(line.strip()):
                continue
            match = START.match(line)
            if match:
                if head:
                    yield head, " ".join(body)
                head, body = match.group(1), [match.group(3)]
            elif head and line.strip():
                body.append(line.strip())
            elif head and not line.strip() and len(body) > 12:   # a long gap: the entry is over
                yield head, " ".join(body)
                head, body = None, []
    if head:
        yield head, " ".join(body)


def equivalents(text):
    """The Italian words an entry opens with, and the part of speech if one is printed first."""
    text = re.sub(r"(\w)- (\w)", r"\1\2", text)
    pos = ""
    tag = TAG.match(text)
    if tag:
        pos = next((name for mark, name in POS if tag.group(1).lower().startswith(mark)), "")
        text = text[tag.end():]
    if re.match(r"V\.\s", text):     # vedi: a cross-reference
        return [], pos
    found = []
    for sentence in re.split(r"\s*\.\s+", text)[:4]:
        sentence = re.sub(r"\s*\([^)]*\)?", "", sentence)                  # the French word in brackets
        sentence = re.sub(r",\s*(?:v|n\.\s*[mf{]|s\.\s*[mf]|add|agg|avv)\.?\s*$", "", sentence)
        pieces = [piece.strip() for piece in re.split(r"\s*,\s*|\s+[oe]\s+", sentence) if piece.strip()]
        if not pieces or not all(WORD.fullmatch(piece) for piece in pieces) or len(pieces) > 4:
            break    # prose begins here
        found += pieces
    return found, pos


def main():
    rows = set()
    for head, text in entries():
        words, pos = equivalents(text)
        for word in words:
            rows.add((head.lower(), word, "it", pos))
    with open(TARGET, "w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out, delimiter="\t", quoting=csv.QUOTE_NONE, quotechar=None, escapechar=None)
        writer.writerow(("headword", "gloss", "gloss_lang", "pos"))
        writer.writerows(sorted(rows))
    print(f"{os.path.basename(TARGET)}: {len(rows)} rows, {len({row[0] for row in rows})} headwords")


if __name__ == "__main__":
    main()
