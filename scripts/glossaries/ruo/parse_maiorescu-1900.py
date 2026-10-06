#!/usr/bin/env python3
"""Maiorescu, *Itinerar în Istria și vocabular istriano-român* (2nd ed. 1900), the vocabulary
raw/maiorescu_1900_tesseract-ron-deu_pp105-146_txt/pNNNN.txt  ->  maiorescu-1900.scan.tsv

The printed entry:

    apoi, apoi. Se zice și poi, (dann, nachher).
    apă-viiă, in Jeiune: apă curgătoare (fliessendes Wasser.)

the Istro-Romanian word, remarks in Romanian, and at the end the German meaning in
brackets. Rows keep the headword and that German meaning.

Two cautions, which is why the table is named .scan and its forms count as attested
with a spelling still to check. The text is a machine reading (Tesseract, Romanian and
German models; made from the PDF at 300 dpi, PDF pages 105-146) that nobody has
proofread. And Maiorescu (d. 1864; public domain) writes Istro-Romanian in a spelling
made to look like Romanian, which later collectors (Pușcariu, Popovici) do not follow.

    python3 parse_maiorescu-1900.py
"""
import csv
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = os.path.join(HERE, "raw", "maiorescu_1900_tesseract-ron-deu_pp105-146_txt", "p*.txt")
HEAD = re.compile(r"^([a-zăâîșțşţáéíóúàèìòù]+(?:-[a-zăâîșțşţ]+)?)[,.]?\s")
GERMAN = re.compile(r"\(([^()]{2,45})\)[.,; ]*$")


def main():
    rows = set()
    for path in sorted(glob.glob(PAGES)):
        with open(path, encoding="utf-8") as stream:
            blocks = re.split(r"\n\s*\n", stream.read())
        for block in blocks:
            text = re.sub(r"(\w)-\n(\w)", r"\1\2", block.strip()).replace("\n", " ")
            head, german = HEAD.match(text), GERMAN.search(text)
            if not head or not german:
                continue
            for meaning in re.split(r"\s*[,;]\s*", german.group(1).strip(" .!")):
                if re.fullmatch(r"[A-Za-zÄÖÜäöüß ]{2,30}", meaning):
                    rows.add((head.group(1).translate(str.maketrans("şţ", "șț")), meaning, "de", ""))
    with open(os.path.join(HERE, "maiorescu-1900.scan.tsv"), "w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out, delimiter="\t", quoting=csv.QUOTE_NONE, quotechar=None, escapechar=None)
        writer.writerow(("headword", "gloss", "gloss_lang", "pos"))
        writer.writerows(sorted(rows))
    print(f"maiorescu-1900.scan.tsv: {len(rows)} rows, {len({row[0] for row in rows})} headwords")


if __name__ == "__main__":
    main()
