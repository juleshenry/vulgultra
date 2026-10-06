#!/usr/bin/env python3
"""Parse the glossary of Pericle Papahagi, Basme aromâne și glosar (1905),
pp. 507-748, into a headword-gloss table.

The only scan is Google's bitonal one (archive.org basmearomneiglo00papagoog);
its bold headword type is badly reproduced, and no single OCR reads it
reliably.  So two independent readings of the same pages are compared and a
row is kept only when BOTH give the same headword, letter for letter:

  A. raw/papahagi_1905_basmearomneiglo00papagoog_djvu.txt
       the ABBYY FineReader text archive.org ships with the item;
  B. raw/papahagi_1905_tesseract-latin/pNNN.tsv.gz  (NNN = PDF page)
       Tesseract 5.5 `Latin` script model (tessdata_best) on the PDF pages
       rendered at 400 dpi and thinned by one pixel
       (pdftoppm -r 400 -gray | magick -morphology Dilate Diamond:1 |
        tesseract -l Latin --psm 3 -c tessedit_create_tsv=1).

Entry shape in the source:
    Headword[, variant] [şi: variant] POS. = gloss refs; phrase = gloss ...
e.g. "Oaspe sm. = oaspete, amic, prietin 14, 39₁₄ ...; pl. oaspiţĭ 98."
Only the first gloss (the one right after the first "=") is taken; it stops
at the first reference number, ";" or ":".  Glosses are Romanian.

Output  papahagi-1905-glosar.tsv            headword agreed by A and B
        papahagi-1905-glosar.doubtful.tsv   B's reading where A disagrees
                                            or has no such entry
The two encodings of s/t with cedilla or comma below are written comma-below
(ș ț); nothing else in a headword is changed.

Usage: python3 parse_papahagi-1905-glosar.py     (stdlib only)
"""
import csv
import glob
import gzip
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ABBYY = os.path.join(HERE, "raw", "papahagi_1905_basmearomneiglo00papagoog_djvu.txt")
TESS = os.path.join(HERE, "raw", "papahagi_1905_tesseract-latin")

POS_MAP = {"sm": "noun", "sf": "noun", "sn": "noun", "subst": "noun", "adj": "adj",
           "adv": "adv", "vb": "verb", "prep": "prep", "conj": "conj", "num": "num",
           "pron": "pron", "interj": "other", "art": "other"}
POS_RX = r"(?:loc\.\s*adv|sm|sf|sn|subst|adj|adv|vb|prep|conj|interj|num|pron|art)"
LETTER = r"A-Za-zÀ-ÖØ-öø-ſƀ-ɏḀ-ỿ"
# Headword [, variant] [[şi: x]] [(mi-)] POS. [conj. class] = gloss
ENTRY_RX = re.compile(
    r"^(?P<hw>[" + LETTER + r"][" + LETTER + r"'’\-]*)"
    r"(?:\s*,\s*(?P<hw2>[" + LETTER + r"][" + LETTER + r"'’\-]*))?"
    r"\s*(?:[\[\(][^\]\)=]{0,40}[\]\)/|Jj]\s*)?"
    r"(?:\((?:mi|me|ńi|ni)-?\)\s*)?"
    r"(?P<pos>" + POS_RX + r")\s*\.?\s*(?:pl\.\s*)?(?:I{1,3}V?|IV|1{1,3}V?)?\s*\.?\s*"
    r"(?:\[[^\]=]{0,60}\]\s*)?"
    r"[=—–\-]{1,3}\s*(?P<rest>.+)$")
NORM_ST = str.maketrans({"ş": "ș", "Ş": "Ș", "ţ": "ț", "Ţ": "Ț", "’": "'"})


def nfc(s):
    return unicodedata.normalize("NFC", s).translate(NORM_ST)


def loose(s):
    """Letters only, no diacritics: for comparing two readings of a gloss."""
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if c.isalpha() and unicodedata.category(c) != "Mn")


def first_gloss(rest):
    """Text right after '=' up to the first reference / ';' / ':'."""
    g = rest.strip()
    g = re.sub(r"^1\s*[°º\"*'’]+\s*", "", g)          # "1° prind; ..."
    g = re.split(r"\s*(?:;|:|\s\d|\d{2,}|\bpl\.|\bfem\.|\bInf\.|\bVezi\b|\betc\b|=)", g, maxsplit=1)[0]
    g = re.sub(r"\s+", " ", g).strip(" ,.-—")
    return g


def dehyphen(lines):
    """Join physical lines of an entry; a word split at a line end is glued."""
    out = ""
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        if out.endswith("-") and ln[:1].islower():
            out = out[:-1] + ln
        else:
            out = (out + " " + ln).strip()
    return out


def parse_entry(text):
    text = nfc(re.sub(r"\s+", " ", text)).strip()
    m = ENTRY_RX.match(text)
    if not m:
        return None
    hw = m.group("hw")
    if not hw[0].isupper():
        return None
    pos = re.sub(r"[.\s]", "", m.group("pos"))
    pos = "adv" if pos.startswith("loc") else pos
    g = first_gloss(m.group("rest"))
    if not g or len(g) > 80:
        return None
    return {"hw": hw, "hw2": m.group("hw2"), "pos": POS_MAP.get(pos, ""), "gloss": g}


# ---------------------------------------------------------------- reading A
def abbyy_entries():
    lines = open(ABBYY, encoding="utf-8").read().split("\n")
    start = max(i for i, l in enumerate(lines[:31000]) if l.strip() == "GLOSAR.") if True else 0
    # the first "GLOSAR." running head after the tales
    start = next(i for i, l in enumerate(lines) if i > 30000 and l.strip() == "GLOSAR.")
    ents = []
    buf = None
    for l in lines[start:]:
        s = re.sub(r"\s+", " ", l).strip()
        if not s or s in ("GLOSAR.",) or re.fullmatch(r"\d{3}", s) or "PAPAHAGI" in s:
            continue
        if re.match(r"^[A-ZÀ-ÖØ-ÞĂÂÎŞŢȘȚ][^ ]* ?[^=]{0,45}(" + POS_RX + r")\s*\.", s) and "=" in s[:70] \
                or re.match(r"^[A-ZÀ-ÖØ-ÞĂÂÎŞŢȘȚ][^ ]*\s*\.\s*Vezi", s):
            if buf:
                ents.append(buf)
            buf = [s]
        elif buf is not None:
            buf.append(s)
    if buf:
        ents.append(buf)
    return [dehyphen(b) for b in ents]


# ---------------------------------------------------------------- reading B
def tess_pages():
    for fn in sorted(glob.glob(os.path.join(TESS, "p*.tsv.gz"))):
        page = int(re.search(r"p(\d+)\.tsv", fn).group(1))
        with gzip.open(fn, "rt", encoding="utf-8") as f:
            rows = list(csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
        yield page, rows[1:]


def tess_entries():
    """Yield (page, left, top, text) for every entry found by geometry:
    the first line of an entry hangs out to the left of its other lines."""
    for page, rows in tess_pages():
        words = []
        pw = 0
        for r in rows:
            if len(r) < 12:
                continue
            if r[0] == "1":
                pw = int(r[8])
            if r[0] != "5" or not r[11].strip():
                continue
            words.append((r[2], r[3], r[4], int(r[6]), int(r[7]), int(r[8]), int(r[9]), r[11]))
        if not words or not pw:
            continue
        lines = defaultdict(list)
        for b, p, l, x, y, w, h, t in words:
            lines[(b, p, l)].append((x, y, w, h, t))
        L = []
        for k, ws in lines.items():
            ws.sort()
            x0 = ws[0][0]
            y0 = min(w[1] for w in ws)
            x1 = max(w[0] + w[2] for w in ws)
            L.append([x0, y0, x1, " ".join(w[4] for w in ws)])
        mid = pw / 2
        for col in (0, 1):
            cl = [l for l in L if (l[0] + l[2]) / 2 < mid] if col == 0 else \
                 [l for l in L if (l[0] + l[2]) / 2 >= mid]
            cl = [l for l in cl if l[2] - l[0] > 60 or len(l[3]) > 3]
            cl.sort(key=lambda l: l[1])
            if len(cl) < 3:
                continue
            xs = [l[0] for l in cl]
            cur = None
            for i, l in enumerate(cl):
                win = sorted(xs[max(0, i - 6):i + 7])
                ref = win[len(win) * 2 // 3]              # continuation-line x
                is_start = l[0] < ref - 30
                if is_start:
                    if cur:
                        yield cur
                    cur = [page, l[0], l[1], [l[3]]]
                elif cur:
                    cur[3].append(l[3])
            if cur:
                yield cur


def main():
    stats = Counter()
    a_by_hw = defaultdict(list)
    for text in abbyy_entries():
        stats["A_entries"] += 1
        d = parse_entry(text)
        if not d:
            continue
        stats["A_parsed"] += 1
        a_by_hw[d["hw"]].append(d)
    rows, doubtful, seen = [], [], set()
    for page, x, y, lines in tess_entries():
        stats["B_entries"] += 1
        d = parse_entry(dehyphen(lines))
        if not d:
            continue
        stats["B_parsed"] += 1
        row = (d["hw"], d["gloss"], "ro", d["pos"])
        cands = a_by_hw.get(d["hw"], [])
        ok = False
        for c in cands:
            ga, gb = loose(c["gloss"]), loose(d["gloss"])
            if ga == gb or (len(gb) > 3 and (ga.startswith(gb) or gb.startswith(ga))):
                ok = True
        if ok:
            if row not in seen:
                seen.add(row)
                rows.append(row + (page,))
                stats["agreed"] += 1
        else:
            doubtful.append(row + (page,))
            stats["B_only_or_gloss_differs" if cands else "B_headword_not_in_A"] += 1
    header = "headword\tgloss\tgloss_lang\tpos\n"
    with open(os.path.join(HERE, "papahagi-1905-glosar.tsv"), "w", encoding="utf-8") as f:
        f.write(header)
        for r in rows:
            f.write("\t".join(r[:4]) + "\n")
    with open(os.path.join(HERE, "papahagi-1905-glosar.doubtful.tsv"), "w", encoding="utf-8") as f:
        f.write(header)
        for r in doubtful:
            f.write("\t".join(r[:4]) + "\n")
    if "--pages" in sys.argv:          # side file for checking rows against the scan
        with open(sys.argv[sys.argv.index("--pages") + 1], "w", encoding="utf-8") as f:
            for r in rows:
                f.write("\t".join(map(str, r)) + "\n")
    for k in sorted(stats):
        print(f"{k}\t{stats[k]}", file=sys.stderr)


if __name__ == "__main__":
    main()
