#!/usr/bin/env python3
"""Glavina's two Istro-Romanian word lists of 1904 (in Pușcariu, *Studii istroromâne* III, 1929),
the pages nobody has read by eye yet, from the machine reading:
raw/puscariu_1929_tesseract-latin_pp183-214/pNNNN.Latin.tsv.gz  ->  glavina-1904-machine.scan.tsv

    list III   glumă = skerc                           Romanian = Istro-Romanian[: example]
    list IV    hram, -murile = odaie                   Istro-Romanian[, endings] = Romanian[: example]

List III runs from page 183 to 201 and list IV from 202 to 212. Pages 183-188 and 199-203 were
read from the page images (parse_page-readings.py) and are skipped here. On the page
compared (185) the machine reading agrees with the eye reading line for line, but it
has not been proofread, so the table is named .scan: its forms count as attested with
a spelling still to check. An entry with a footnote mark is left out (Pușcariu's notes
there mostly say "misprint" or "not Istro-Romanian").

    python3 parse_glavina-1904-machine.py
"""
import collections
import csv
import glob
import gzip
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = os.path.join(HERE, "raw", "puscariu_1929_tesseract-latin_pp183-214", "p*.Latin.tsv.gz")
READ_BY_EYE = set(range(183, 189)) | set(range(199, 204))
FOOTNOTE = re.compile(r"\s*[\d°*%!?'`]{1,3}\s?\)|\(\s*!\s*\)")
WORD = re.compile(r"[^\W\d_]+(?:[-'’][^\W\d_]+)*")


def lines(path):
    groups = collections.OrderedDict()
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for row in csv.DictReader(stream, delimiter="\t", quoting=csv.QUOTE_NONE):
            if row.get("level") == "5" and row.get("text", "").strip():
                groups.setdefault((row["block_num"], row["par_num"], row["line_num"]), []).append(row["text"])
    return [" ".join(words) for words in groups.values()]


def main():
    rows = set()
    for path in sorted(glob.glob(PAGES)):
        page = int(os.path.basename(path)[1:5])
        if page in READ_BY_EYE:
            continue
        # The running head is misread too often to go by ("GLAVINA 1I!"); the lists keep to these pages.
        which = "III" if page <= 201 else "IV" if page <= 212 else ""
        if not which:
            continue    # the editor's prose
        for line in lines(path):
            if "=" not in line or "GLAVINA" in line:
                continue
            left, _, right = line.partition("=")
            right = right.lstrip("= ").split(":")[0]
            if FOOTNOTE.search(left) or FOOTNOTE.search(right):
                continue
            left, right = left.strip(" |`'.,"), right.strip(" |`'.,")
            if which == "III":
                forms, meaning = [form.strip() for form in right.split(",")], left
            else:
                forms, meaning = [left.split(",")[0].strip()], right
            for form in forms:
                if WORD.fullmatch(form) and meaning and len(meaning) < 60 and re.match(r"[^\W\d_]", meaning):
                    rows.add((form[0].lower() + form[1:], meaning, "ro", ""))
    with open(os.path.join(HERE, "glavina-1904-machine.scan.tsv"), "w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out, delimiter="\t", quoting=csv.QUOTE_NONE, quotechar=None, escapechar=None)
        writer.writerow(("headword", "gloss", "gloss_lang", "pos"))
        writer.writerows(sorted(rows))
    print(f"glavina-1904-machine.scan.tsv: {len(rows)} rows, {len({row[0] for row in rows})} headwords")


if __name__ == "__main__":
    main()
