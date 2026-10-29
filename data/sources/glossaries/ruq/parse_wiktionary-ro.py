#!/usr/bin/env python3
"""Romanian Wiktionary (ro.wiktionary.org dump) -> wiktionary-ro.tsv

Input: raw/rowiktionary.pages.jsonl  — the pages of rowiktionary-latest-pages-articles.xml.bz2 whose wikitext
       mentions this lect ({title, ns, text}; wikitext untouched).
Two kinds of rows:
  1. the lect's own sections (=={{limba|CODE}}==): headword = page title, gloss = each '#' definition line;
  2. translation tables of Romanian entries ({{trad|CODE|word}}): headword = word, gloss = the Romanian page title.
gloss_lang is ro. The lect is taken from the name of the folder this script sits in ('roa-rup' counts as rup).
"""
import json, os, re, csv
HERE = os.path.dirname(os.path.abspath(__file__))
LECT = os.path.basename(HERE)
CODES = {"rup": ("rup", "roa-rup")}.get(LECT, (LECT,))
POS = {"substantiv": "noun", "nume propriu": "noun", "verb": "verb", "adjectiv": "adj", "adverb": "adv",
       "pronume": "pron", "numeral": "num", "prepoziție": "prep", "conjuncție": "conj", "interjecție": "other",
       "articol": "other", "expresie": "other", "locuțiune": "other", "particulă": "other"}
SKIP_HDR = {"etimologie", "pronunție", "etim-lipsă", "pron-lipsă", "var", "sin", "ant", "deriv", "trad", "trans",
            "expr", "loc", "ref", "anagrame", "vezi", "cuv", "silabe", "omofone", "paronime", "apar"}
def unwiki(s):
    s = re.sub(r"<ref[^>]*>.*?</ref>|<ref[^>]*/>|<!--.*?-->", "", s)
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = s.replace("'''", "").replace("''", "")
    s = re.sub(r"\s+", " ", s).strip(" ;,.:")
    return s
rows = []
sec_re = re.compile(r"^==\s*\{\{limba\|([^}|]+)\}\}\s*==\s*$", re.M)
hdr_re = re.compile(r"^\{\{-([^|}]+)-(?:\|([^}|]+))?\}\}")
for line in open(os.path.join(HERE, "raw", "rowiktionary.pages.jsonl"), encoding="utf-8"):
    p = json.loads(line)
    if p["ns"] != "0": continue
    text, title = p["text"], p["title"]
    parts = sec_re.split(text)          # [pre, code1, body1, code2, body2, ...]
    for i in range(1, len(parts), 2):
        code, body = parts[i].strip(), parts[i + 1]
        pos = ""
        if code in CODES:
            for ln in body.split("\n"):
                m = hdr_re.match(ln.strip())
                if m:
                    h = m.group(1).strip()
                    if h in POS: pos = POS[h]
                    elif h not in SKIP_HDR: pos = pos
                    continue
                if ln.startswith("#") and not ln.startswith(("#:", "#*", "##")):
                    g = unwiki(ln.lstrip("#").strip())
                    if g: rows.append((title, g, "ro", pos))
        elif code in ("ron", "ro"):
            for ln in body.split("\n"):
                m = hdr_re.match(ln.strip())
                if m:
                    h = m.group(1).strip()
                    if h in POS: pos = POS[h]
                    continue
                for c in CODES:
                    for w in re.findall(r"\{\{trad\|%s\|([^}|]+)" % re.escape(c), ln):
                        w = unwiki(w)
                        if w: rows.append((w, title, "ro", pos))
seen = set(); out = []
for r in rows:
    if r not in seen: seen.add(r); out.append(r)
out.sort(key=lambda r: (r[0].lower(), r[1]))
with open(os.path.join(HERE, "wiktionary-ro.tsv"), "w", encoding="utf-8", newline="") as fo:
    wr = csv.writer(fo, delimiter="\t", quoting=csv.QUOTE_NONE, quotechar=None, lineterminator="\n")
    wr.writerow(["headword", "gloss", "gloss_lang", "pos"])
    for r in out: wr.writerow([c.replace("\t", " ") for c in r])
print(LECT, "rows", len(out))
