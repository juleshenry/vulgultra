#!/usr/bin/env python3
"""Stream the Kaikki extract of Latin and keep each word's Romance descendants.

Latin is never a source of forms (daughters only), but a Latin word is the
shortest way to name a family of daughter words: Wiktionary's Latin entries
list the reflexes of each word, lect by lect. Two files under
`data/sources/kaikki_full/`:

    la.jsonl      one row per dictionary entry: the word, its part of speech,
                  its first glosses, and (code, form) pairs for its reflexes
    la_forms.tsv  inflected form, dictionary word, part of speech: what turns
                  the words of a Latin text into dictionary words

    python3 scripts/fetch_latin_descendants.py
"""

from __future__ import annotations

import json
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "sources" / "kaikki_full" / "la.jsonl"
FORMS = OUT.with_name("la_forms.tsv")
URL = "https://kaikki.org/dictionary/Latin/kaikki.org-dictionary-Latin.jsonl"
USER_AGENT = "vulgultra-research/0.1 (+noncommercial morphology corpus)"
# Wiktionary's codes for the 36 lects and the older stages a reflex passes through.
ROMANCE = {
    "es", "pt", "gl", "an", "ast", "ext", "lad", "mwl", "oc", "ca", "fr", "wa", "pcd", "nrf", "roa-gal", "frp",
    "lmo", "pms", "lij", "egl", "rgn", "it", "scn", "vec", "co", "ist", "dlm", "rm", "fur", "lld", "sc", "ro",
    "rup", "ruo", "ruq", "nap", "fro", "frm", "osp", "roa-opt", "pro", "roa-oit", "VL.", "la-vul", "la-med", "LL.",
}


def reflexes(nodes: list, found: list[list[str]]) -> None:
    """Every (code, form) under a descendants tree, whichever layout the extract uses."""
    for node in nodes or []:
        code, word = node.get("lang_code"), node.get("word")
        if code in ROMANCE and word:
            found.append([code, word])
        for template in node.get("templates") or []:
            args = template.get("args") or {}
            if template.get("name") in ("desc", "l", "desctree", "descendant") and args.get("1") in ROMANCE:
                found.extend([args["1"], args[key]] for key in ("2", "3", "4") if args.get(key))
        reflexes(node.get("descendants") or [], found)


def plain(word: str) -> str:
    """Lowercase, without the macrons and breves a dictionary adds."""
    return "".join(ch for ch in unicodedata.normalize("NFD", word.lower()) if not unicodedata.combining(ch))


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    partial, forms_partial = OUT.with_suffix(".jsonl.part"), FORMS.with_suffix(".tsv.part")
    read = kept = inflected = 0
    request = urllib.request.Request(URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response, partial.open("w", encoding="utf-8") as out, \
            forms_partial.open("w", encoding="utf-8") as forms:
        for line in response:
            read += 1
            entry = json.loads(line)
            word, pos = entry.get("word", ""), entry.get("pos", "")
            if not word or " " in word or pos in ("name", "character", "symbol", "suffix", "prefix"):
                continue
            lemmas = {plain(target["word"]) for sense in entry.get("senses") or []
                      for target in sense.get("form_of") or [] if target.get("word")}
            for lemma in sorted(lemmas):
                forms.write(f"{plain(word)}\t{lemma}\t{pos}\n")
                inflected += 1
            glosses = [gloss for sense in entry.get("senses") or [] if not sense.get("form_of")
                       for gloss in sense.get("glosses") or []][:4]
            if not glosses:
                continue
            found: list[list[str]] = []
            reflexes(entry.get("descendants") or [], found)
            pairs = [list(pair) for pair in dict.fromkeys(map(tuple, found))]
            out.write(json.dumps({"word": plain(word), "pos": pos, "glosses": glosses, "descendants": pairs},
                                 ensure_ascii=False) + "\n")
            kept += 1
    partial.rename(OUT)
    forms_partial.rename(FORMS)
    print(f"la: {kept} dictionary entries and {inflected} inflected forms of {read} rows → {OUT.parent}")


if __name__ == "__main__":
    main()
