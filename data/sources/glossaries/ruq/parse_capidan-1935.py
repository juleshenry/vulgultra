#!/usr/bin/env python3
"""Capidan 1935, *Meglenoromânii III: Dicționar meglenoromân*
raw/capidan_1935_tesseract-latin_hocr/pNNN.txt  ->  capidan-1935.tsv  (+ capidan-1935.doubtful.tsv)

The printed entry:

    Cárpini m. Carpen. ALR. 1920. Carpingros = n. loc. (Lugunța). [Derivat: ...]. — Din lat. carpĭnus,
    Cărpés vb. IV. v. corpă.

a capitalised headword with its stress marked, the gender or part of speech, the
Romanian meaning up to the first full stop, examples with their text references,
derivatives in square brackets, and after a dash the source word ("Din lat.",
"Din bg.", "Din tc."). An entry that only says "v. x" sends the reader elsewhere
and is left out.

Rows: `headword  gloss  gloss_lang  pos  latin_etymon`, the headword in lower case
with Capidan's accents kept. The text is a machine reading (Tesseract), which
gets plain letters right and Capidan's special ones (ǫ, ę, ạ) wrong. So a headword
goes to the main table only if it is spelt with letters the reader handles AND
the other machine reading of the same scan (archive.org's) has the same word;
everything else goes to the doubtful table, to be read off the page.

    python3 parse_capidan-1935.py
"""
import csv
import glob
import os
import re
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = os.path.join(HERE, "raw", "capidan_1935_tesseract-latin_hocr", "p*.txt")
SECOND = os.path.join(HERE, "raw", "capidan_1935_archiveorg_djvu.txt")
CEDILLA = str.maketrans("şţŞŢ", "șțȘȚ")
SAFE = re.compile(r"[a-zăâîșțáéíóúšžčń'’-]+")
TAG = (r"(?:m\.|f\.|n\.|a\.|vb\.\s*(?:IV|I{1,3})?\.?|adj\.|adv\.|prep\.|conj\.|interj\.|num\.|pron\.|art\.|"
       r"s\.|pl\.)")
ENTRY = re.compile(rf"^(?P<head>[^\s,.;:()\[\]=]+)(?:,\s*-\S+)*\s+(?P<tags>{TAG}(?:\s*{TAG})*)\s*(?P<rest>.*)$", re.S)
POS = (("vb", "verb"), ("adj", "adj"), ("adv", "adv"), ("prep", "prep"), ("conj", "conj"), ("num", "num"),
       ("pron", "pron"), ("interj", "other"), ("art", "other"), ("m.", "noun"), ("f.", "noun"), ("n.", "noun"),
       ("a.", "noun"), ("s.", "noun"))
LATIN = re.compile(r"[Dd]in\s+lat\.\s*(?:vulg\.\s*|pop\.\s*)?[*#]?\s*([A-Za-zāēīōūăĕĭŏŭäëïöüàèìòùáéíóú]+)")


def plain(word):
    return "".join(ch for ch in unicodedata.normalize("NFD", word.lower()) if not unicodedata.combining(ch))


def paragraphs():
    for path in sorted(glob.glob(PAGES)):
        with open(path, encoding="utf-8") as stream:
            lines = [line.rstrip() for line in stream]
        # The running head (page number, "TH. CAPIDAN" or the title) is the first two non-empty lines.
        body, dropped = [], 0
        for line in lines:
            if dropped < 2 and line.strip() and (re.fullmatch(r"[\divxlIVXL .]+", line.strip()) or "CAPIDAN" in line
                                                 or "DIC" in line.upper() and len(line) < 40):
                dropped += 1
                continue
            body.append(line)
        block = []
        for line in body + [""]:
            if line.strip():
                block.append(line.strip())
            elif block:
                text = " ".join(block)
                yield re.sub(r"(\w)- (\w)", r"\1\2", text).translate(CEDILLA)
                block = []


def main():
    with open(SECOND, encoding="utf-8", errors="replace") as stream:
        second = {plain(token.translate(CEDILLA)) for token in re.findall(r"[^\W\d_]+(?:['’-][^\W\d_]+)*", stream.read())}
    # The reader breaks an entry into several blocks; a block that does not open an entry continues the last.
    entries = []
    for text in paragraphs():
        match = ENTRY.match(text)
        if match and match.group("head")[0].isupper():
            entries.append(text)
        elif entries:
            entries[-1] += " " + text
    good, doubtful, seen = [], [], 0
    for text in entries:
        match = ENTRY.match(re.sub(r"(\w)- (\w)", r"\1\2", text))
        head = match.group("head")
        head = head[0].lower() + head[1:]
        rest = match.group("rest").strip()
        if re.match(r"v\.\s", rest) or not rest:    # a cross-reference, or a bare derivative with no meaning
            continue
        seen += 1
        # A label in brackets before the meaning ("(despre oaie)", "(Țârnareca)") is not the meaning.
        rest = re.sub(r"^(?:\([^)]*\)[.,]?\s*)+", "", rest)
        gloss = re.split(r"(?<=[a-zăâîșț)])\.(?:\s|$)", rest, maxsplit=1)[0]
        # The meaning stops where the references start: "Căptușesc, ALR. 5769", "Scrâșnesc, cf. ...", "Descânt 8/30".
        gloss = re.split(r",?\s*(?:ALR|Com|[Cc]f)\b|\s*\[|\s+\d+/\d+|:\s", gloss)[0].strip(" .,")
        if not gloss or len(gloss) > 80 or not re.match(r"[A-ZĂÂÎȘȚ]", gloss) or len(gloss.split()) > 9:
            continue
        tags = match.group("tags")
        pos = next((name for mark, name in POS if mark in tags), "")
        latin = LATIN.search(rest)
        etymon = plain(latin.group(1)) if latin else ""
        row = (head, gloss, "ro", pos, etymon if len(etymon) >= 3 else "")
        sound = SAFE.fullmatch(head) and plain(head) in second
        (good if sound else doubtful).append(row)
    for name, rows in (("capidan-1935.tsv", good), ("capidan-1935.doubtful.tsv", doubtful)):
        with open(os.path.join(HERE, name), "w", encoding="utf-8", newline="") as out:
            writer = csv.writer(out, delimiter="\t", quoting=csv.QUOTE_NONE, quotechar=None, escapechar=None)
            writer.writerow(("headword", "gloss", "gloss_lang", "pos", "latin_etymon"))
            writer.writerows(tuple(field.replace("\t", " ") for field in row) for row in sorted(set(rows)))
        print(f"{name}: {len(set(rows))} rows, {sum(1 for row in set(rows) if row[4])} with a Latin source")
    print(f"entries with a meaning seen: {seen}")


if __name__ == "__main__":
    main()
