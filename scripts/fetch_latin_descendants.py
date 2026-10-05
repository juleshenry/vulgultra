#!/usr/bin/env python3
"""Stream the Kaikki extract of Latin and keep each word's Romance descendants.

Latin is never a source of forms (daughters only), but a Latin word is the
shortest way to name a family of daughter words: Wiktionary's Latin entries
list the reflexes of each word, lect by lect. One row per Latin dictionary
entry that has a Romance descendant, in `data/sources/kaikki_full/la.jsonl`:
the word, its part of speech, its first glosses, and (code, form) pairs.

    python3 scripts/fetch_latin_descendants.py
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "sources" / "kaikki_full" / "la.jsonl"
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


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    partial = OUT.with_suffix(".jsonl.part")
    read = kept = 0
    request = urllib.request.Request(URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response, partial.open("w", encoding="utf-8") as out:
        for line in response:
            read += 1
            if b'"descendants"' not in line:
                continue
            entry = json.loads(line)
            found: list[list[str]] = []
            reflexes(entry.get("descendants") or [], found)
            pairs = [list(pair) for pair in dict.fromkeys(map(tuple, found))]
            if not pairs:
                continue
            glosses = [gloss for sense in entry.get("senses") or [] for gloss in sense.get("glosses") or []][:4]
            out.write(json.dumps({"word": entry["word"], "pos": entry.get("pos"), "glosses": glosses,
                                  "descendants": pairs}, ensure_ascii=False) + "\n")
            kept += 1
    partial.rename(OUT)
    print(f"la: kept {kept} of {read} rows → {OUT}")


if __name__ == "__main__":
    main()
