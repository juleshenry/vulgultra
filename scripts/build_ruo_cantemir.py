#!/usr/bin/env python3
"""Ingest Southern Istro-Romanian from Cantemir 2020 thesis appendix + examples.

Source: Cantemir_Thesis_Final_Draft-converted.pdf
Phonological Analysis of the Southern Dialect of Istro-Romanian/Vlashki
as Compared to Daco-Romanian.

Appendix columns: Daco-Romanian orthography, DR IPA, IR IPA, English.
IR lemmas are IPA converted to a practical spelling (not DR forms).
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "Cantemir_Thesis_Final_Draft-converted.pdf"
WORDS = ROOT / "data" / "words"
DEST = WORDS / "ruo_words.json"

# IPA → practical IR spelling (Vrzić-ish / existing ruo: č ț ž š å ä ă â)
IPA_MAP = [
    ("t͡ʃ", "č"),
    ("͡tʃ", "č"),
    ("tʃ", "č"),
    ("t͡s", "ț"),
    ("͡ts", "ț"),
    ("d͡ʒ", "ǧ"),
    ("͡dʒ", "ǧ"),
    ("dʒ", "ǧ"),
    ("o̯a", "oa"),
    ("e̯a", "ea"),
    ("e̯", "e"),
    ("o̯", "o"),
    ("a̯", "a"),
    ("ʒ", "ž"),
    ("ʃ", "š"),
    ("ɾ", "r"),
    ("ɒ", "å"),
    ("æ", "ä"),
    ("ə", "ă"),
    ("ɨ", "â"),
    ("χ", "h"),
    ("ʎ", "ľ"),
    ("ŋ", "n"),
    ("ɟ", "g"),
    ("c", "k"),
]


def ipa_to_ortho(ipa: str) -> str:
    s = (ipa or "").strip()
    s = s.strip("/[]")
    for a, b in IPA_MAP:
        s = s.replace(a, b)
    s = re.sub(r"[ˈˌ.\-ː̯̚͡''`ʹ′]", "", s)
    s = s.replace(" ", "")
    return s


GLOSS_FIX = {
    # appendix English vs obvious DR lemma
    "february": "six",  # DR şase
    "the throat": "the neck",
}


def parse_pairs(text: str) -> list[dict]:
    """Find [DR IPA] [IR IPA] 'gloss' triples; optional DR orthography before."""
    rows = []
    # allow combining marks inside IPA
    pat = re.compile(
        r"(?:(?P<dr>[A-Za-zăâîșşțţĂÂÎȘŞȚŢ \-']{1,40}?)\s+)?"
        r"\[(?P<drip>[^\[\]]+)\]\s+"
        r"\[(?P<irip>[^\[\]]+)\]\s+"
        r"[‘'‛′](?P<gloss>[^’'\"]+)[’']",
        re.UNICODE,
    )
    for m in pat.finditer(text):
        dr = (m.group("dr") or "").strip().strip("-")
        drip = m.group("drip").strip()
        irip = m.group("irip").strip()
        gloss = m.group("gloss").strip().lower()
        gloss = GLOSS_FIX.get(gloss, gloss)
        form = ipa_to_ortho(irip)
        if not form or len(form) < 2:
            continue
        if not re.search(r"[A-Za-zĂÂÎȘȚăâîșțåäčžšǧľț]", form):
            continue
        rows.append(
            {
                "ruo": form,
                "ipa": irip,
                "gloss_en": gloss,
                "dr": dr,
                "dr_ipa": drip,
            }
        )
    return rows


def load_pdf_text() -> str:
    out = subprocess.check_output(
        ["pdftotext", "-layout", str(PDF), "-"],
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return out


def merge(rows: list[dict]) -> dict:
    if DEST.exists():
        data = json.loads(DEST.read_text(encoding="utf-8"))
    else:
        data = {"meta": {"lang": "ruo", "n_entries": 0}, "entries": {}}
    entries = data.setdefault("entries", {})
    # drop previous Cantemir keys that still had stress apostrophes
    for k in list(entries):
        rec = entries[k]
        if "cantemir2020" in (rec.get("sources") or []) and ("'" in k or "`" in k):
            del entries[k]
    added = 0
    for r in rows:
        w = r["ruo"]
        rec = entries.get(w)
        if rec is None:
            rec = {
                "ruo": w,
                "pos": [],
                "glosses_en": [],
                "ipa": r["ipa"],
                "dr": r["dr"] or None,
                "sources": ["cantemir2020"],
            }
            entries[w] = rec
            added += 1
        else:
            srcs = rec.setdefault("sources", [])
            if "cantemir2020" not in srcs:
                srcs.append("cantemir2020")
            if r["ipa"] and not rec.get("ipa"):
                rec["ipa"] = r["ipa"]
            if r["dr"] and not rec.get("dr"):
                rec["dr"] = r["dr"]
        g = r["gloss_en"]
        glosses = rec.setdefault("glosses_en", [])
        if g and g not in glosses:
            glosses.append(g)
    data["meta"]["lang"] = "ruo"
    data["meta"]["n_entries"] = len(entries)
    data["meta"]["n_cantemir"] = sum(
        1 for e in entries.values() if "cantemir2020" in (e.get("sources") or [])
    )
    data["meta"]["cantemir_source"] = (
        "Cantemir, Phonological Analysis of the Southern Dialect of "
        "Istro-Romanian/Vlashki as Compared to Daco-Romanian (2020)"
    )
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"added": added, "n": len(entries), "parsed": len(rows)}


# High-confidence Swadesh overlays from Cantemir's own Southern IR recordings.
# Citation forms = IR IPA spelling; definite 'the X' used when that is what she lists.
CANTEMIR_SWADESH = {
    "there": "kalo",
    "other": "wata",
    "four": "pwatru",
    "five": "činz",
    "big": "måre",
    "head": "kåp",
    "nose": "nwasu",
    "mouth": "gura",
    "foot": "pițor",
    "leg": "pițor",
    "knee": "zerukij",
    "hand": "mărle",
    "neck": "gutu",
    "breast": "siru",
    "come": "verija",
    "fall": "kazuta",
    "put": "pure",
    "tie": "läga",
    "say": "zeja",
    "sun": "sore",
    "water": "wapa",
    "salt": "sware",
    "fire": "foku",
    "night": "sära",
    "year": "wan",
    "good": "bur",
    "mother": "mwaja",
    "chest": "kjeptu",
}


def main() -> None:
    if not PDF.exists():
        raise SystemExit(f"missing {PDF}")
    text = load_pdf_text()
    # appendix is the bulk wordlist; body examples duplicate it
    i = text.find("This appendix contains")
    appendix = text[i:] if i >= 0 else text
    rows = parse_pairs(appendix)
    # also body example tables (same format)
    body = text[:i] if i >= 0 else ""
    extra = parse_pairs(body)
    seen = {(r["ruo"], r["gloss_en"]) for r in rows}
    for r in extra:
        key = (r["ruo"], r["gloss_en"])
        if key not in seen:
            rows.append(r)
            seen.add(key)
    stats = merge(rows)
    print(
        f"ruo  parsed={stats['parsed']}  +{stats['added']}  total={stats['n']}  ← Cantemir 2020"
    )
    print("sample:")
    for r in rows[:12]:
        print(f"  {r['ruo']:12}  {r['ipa']:20}  {r['gloss_en']}  (DR {r['dr']})")


if __name__ == "__main__":
    main()
