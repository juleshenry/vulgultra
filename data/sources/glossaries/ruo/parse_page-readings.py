#!/usr/bin/env python3
"""Istro-Romanian: the page readings of two glossaries in Pușcariu, *Studii istroromâne* III (1929)
-> puscariu-1929-glosar.tsv, glavina-1904.tsv  (+ a .doubtful.tsv beside each)

The glossaries were read from the page images, one file per page, by the rules in
raw/*/READING-RULES.md (OCR gets two headwords in three). This script only reshapes
those readings into `headword  gloss  gloss_lang  pos`; it corrects nothing.

  Pușcariu, "Glosar la vol. I"    headword, endings, part of speech, Romanian meaning, unsure
  Glavina 1904, list III          Romanian word = Istro-Romanian word(s)
  Glavina 1904, list IV           Istro-Romanian word[, forms] = Romanian meaning

Set aside as doubtful: a row the reader marked unsure, and a Glavina entry that
carries a footnote on either side of the "=" (Pușcariu's notes there mostly say
"misprint" or "Daco-Romanian, not Istro-Romanian"). Left out: cross-references,
names, and headwords shown only inside a phrase.

    python3 parse_page-readings.py
"""
import csv
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PUSCARIU = os.path.join(HERE, "raw", "puscariu_1929_glosar-vol1_page-readings")
GLAVINA = os.path.join(HERE, "raw", "glavina_1904_page-readings")
POS = (("vb", "verb"), ("sb", "noun"), ("sf", "noun"), ("sm", "noun"), ("n.", "noun"), ("adj", "adj"),
       ("adv", "adv"), ("prep", "prep"), ("conj", "conj"), ("num", "num"), ("pron", "pron"))
LABEL = re.compile(r"^(?:\([^)]*\)\s*)+")


def spellings(headword):
    """The forms a printed headword stands for: "x, y" and "x si y" are two, "(a)cåsę" is two."""
    found = []
    for form in re.split(r",\s*|\s+[sș]i\s+", headword.strip()):
        form = form.strip(" .")
        if not form or " " in form:
            continue
        optional = re.fullmatch(r"(.*)\(([^)]+)\)(.*)", form)
        found += [optional.group(1) + optional.group(3), "".join(optional.groups())] if optional else [form]
    return [form for form in found if form and "(" not in form]


def senses(gloss):
    for sense in gloss.split(";"):
        sense = LABEL.sub("", sense.strip()).strip(" .")
        if sense:
            yield sense


def write(name, rows):
    with open(os.path.join(HERE, name), "w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out, delimiter="\t", quoting=csv.QUOTE_NONE, quotechar=None, escapechar=None)
        writer.writerow(("headword", "gloss", "gloss_lang", "pos"))
        writer.writerows(sorted(set(rows)))
    print(f"{name}: {len(set(rows))} rows, {len({row[0] for row in rows})} headwords")


def puscariu():
    good, doubtful = [], []
    for path in sorted(glob.glob(os.path.join(PUSCARIU, "p*.tsv"))):
        with open(path, encoding="utf-8") as stream:
            for line in stream:
                fields = line.rstrip("\n").split("\t")
                if len(fields) < 4:
                    continue
                headword, _, printed_pos, gloss = fields[:4]
                unsure = len(fields) > 4 and fields[4].strip() == "1"
                if printed_pos.strip() in ("v.", "n. pr.") or gloss.startswith("în:") or not gloss.strip():
                    continue
                pos = next((name for mark, name in POS if printed_pos.startswith(mark)), "other" if printed_pos else "")
                for form in spellings(headword):
                    for sense in senses(gloss):
                        (doubtful if unsure else good).append((form, sense.replace("\t", " "), "ro", pos))
    write("puscariu-1929-glosar.tsv", good)
    write("puscariu-1929-glosar.doubtful.tsv", doubtful)


def glavina():
    good, doubtful = [], []
    for path in sorted(glob.glob(os.path.join(GLAVINA, "p*.tsv"))):
        with open(path, encoding="utf-8") as stream:
            for line in stream:
                fields = line.rstrip("\n").split("\t")
                if len(fields) < 3:
                    continue
                which, left, right = fields[:3]
                note = fields[3] if len(fields) > 3 else ""
                flagged = bool(re.search(r"[LR]\d|\?", note)) or "(!)" in left + right
                if which == "III":      # Romanian = Istro-Romanian
                    forms, meaning = spellings(right), left
                else:                   # Istro-Romanian[, forms] = Romanian; the forms after the first are endings
                    forms, meaning = spellings(re.split(r",\s*", left)[0]), right
                for form in forms:
                    if form.startswith("-"):
                        continue
                    for sense in senses(meaning):
                        (doubtful if flagged else good).append((form, sense.replace("\t", " "), "ro", ""))
    write("glavina-1904.tsv", good)
    write("glavina-1904.doubtful.tsv", doubtful)


if __name__ == "__main__":
    puscariu()
    glavina()
