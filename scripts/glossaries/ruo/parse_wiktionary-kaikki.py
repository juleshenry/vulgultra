#!/usr/bin/env python3
"""Non-English Wiktionary editions (Kaikki/wiktextract raw extracts) -> wiktionary-kaikki.tsv

Input (in raw/, one pair per edition, already filtered to this lect):
  kaikki-{edition}.entries.jsonl       entries whose lang_code is this lect (untouched Kaikki lines)
  kaikki-{edition}.translations.jsonl  one line per translation into this lect found in other entries
                                       ({edition, entry_word, entry_lang_code, entry_pos, sense_gloss, translation})
Output: wiktionary-kaikki.tsv  (headword, gloss, gloss_lang, pos); gloss_lang = language of the edition.
The lect is taken from the name of the folder this script sits in.
"""
import json, glob, os, re, csv
HERE = os.path.dirname(os.path.abspath(__file__))
LECT = os.path.basename(HERE)
ED_LANG = {"plwiktionary": "pl", "ruwiktionary": "ru", "nlwiktionary": "nl", "cswiktionary": "cs",
           "dewiktionary": "de", "trwiktionary": "tr", "elwiktionary": "el"}
POS = {"noun": "noun", "name": "noun", "verb": "verb", "adj": "adj", "adv": "adv", "pron": "pron", "num": "num",
       "prep": "prep", "conj": "conj"}
def pos_of(p):
    if not p: return ""
    return POS.get(p, "other")
def clean(s):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s.strip(" ;,")
rows = []
for f in sorted(glob.glob(os.path.join(HERE, "raw", "kaikki-*.entries.jsonl"))):
    ed = os.path.basename(f).split("-")[1].split(".")[0]
    for line in open(f, encoding="utf-8"):
        d = json.loads(line)
        if d.get("lang_code") != LECT: continue
        w = clean(d.get("word"))
        if not w: continue
        for s in d.get("senses") or []:
            if s.get("form_of") or "form-of" in (s.get("tags") or []): continue
            gl = s.get("glosses") or []
            if not gl: continue
            g = clean(gl[-1])
            if g: rows.append((w, g, ED_LANG[ed], pos_of(d.get("pos"))))
for f in sorted(glob.glob(os.path.join(HERE, "raw", "kaikki-*.translations.jsonl"))):
    ed = os.path.basename(f).split("-")[1].split(".")[0]
    for line in open(f, encoding="utf-8"):
        d = json.loads(line)
        tr = d["translation"]
        if tr.get("lang_code") != LECT: continue
        # only translations given under an entry in the edition's own language: the gloss is then that word
        if d.get("entry_lang_code") != ED_LANG[ed]: continue
        w = clean(tr.get("word"))
        if not w or w in "-–—?": continue
        g = clean(d.get("entry_word"))
        sense = clean(tr.get("sense") or d.get("sense_gloss") or "")
        if sense and len(sense) <= 80: g = f"{g} ({sense})"
        rows.append((w, g, ED_LANG[ed], pos_of(d.get("entry_pos"))))
seen = set(); out = []
for r in rows:
    if r not in seen:
        seen.add(r); out.append(r)
out.sort(key=lambda r: (r[0].lower(), r[2], r[1]))
with open(os.path.join(HERE, "wiktionary-kaikki.tsv"), "w", encoding="utf-8", newline="") as fo:
    wr = csv.writer(fo, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar=None, quotechar=None, lineterminator="\n")
    wr.writerow(["headword", "gloss", "gloss_lang", "pos"])
    for r in out: wr.writerow([c.replace("\t", " ") for c in r])
print(LECT, "rows", len(out))
