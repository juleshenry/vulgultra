#!/usr/bin/env python3
"""Build Dalmatian lexicon from kaikki.org Wiktionary JSONL."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "kaikki.org-dictionary-Dalmatian.jsonl"
OUT = ROOT / "data" / "words" / "dlm_words.json"

# English gloss → our Swadesh concept ids (best-effort)
GLOSS_TO_IDS = {
    "i": ["i"],
    "we": ["we"],
    "you": ["you_sg", "you_pl"],
    "he": ["he"],
    "this": ["this"],
    "that": ["that"],
    "who": ["who"],
    "what": ["what"],
    "where": ["where"],
    "when": ["when"],
    "how": ["how"],
    "not": ["not"],
    "all": ["all"],
    "many": ["many"],
    "one": ["one"],
    "two": ["two"],
    "three": ["three"],
    "four": ["four"],
    "five": ["five"],
    "big": ["big"],
    "long": ["long"],
    "small": ["small"],
    "woman": ["woman"],
    "man": ["man"],
    "person": ["person"],
    "child": ["child"],
    "mother": ["mother"],
    "father": ["father"],
    "dog": ["dog"],
    "cat": ["cat"],
    "fish": ["fish"],
    "bird": ["bird"],
    "tree": ["tree"],
    "forest": ["forest"],
    "leaf": ["leaf"],
    "root": ["root"],
    "bark": ["bark"],
    "flower": ["flower"],
    "grass": ["grass"],
    "skin": ["skin"],
    "meat": ["meat"],
    "blood": ["blood"],
    "bone": ["bone"],
    "egg": ["egg"],
    "horn": ["horn"],
    "tail": ["tail"],
    "hair": ["hair"],
    "head": ["head"],
    "ear": ["ear"],
    "eye": ["eye"],
    "nose": ["nose"],
    "mouth": ["mouth"],
    "tooth": ["tooth"],
    "tongue": ["tongue"],
    "foot": ["foot"],
    "leg": ["leg"],
    "knee": ["knee"],
    "hand": ["hand"],
    "wing": ["wing"],
    "belly": ["belly"],
    "neck": ["neck"],
    "back": ["back"],
    "heart": ["heart"],
    "liver": ["liver"],
    "drink": ["drink"],
    "eat": ["eat"],
    "bite": ["bite"],
    "see": ["see"],
    "hear": ["hear"],
    "know": ["know"],
    "sleep": ["sleep"],
    "live": ["live"],
    "die": ["die"],
    "kill": ["kill"],
    "walk": ["walk"],
    "come": ["come"],
    "sit": ["sit"],
    "stand": ["stand"],
    "give": ["give"],
    "say": ["say"],
    "sun": ["sun"],
    "moon": ["moon"],
    "star": ["star"],
    "water": ["water"],
    "rain": ["rain"],
    "river": ["river"],
    "sea": ["sea"],
    "salt": ["salt"],
    "stone": ["stone"],
    "sand": ["sand"],
    "earth": ["earth"],
    "cloud": ["cloud"],
    "sky": ["sky"],
    "wind": ["wind"],
    "snow": ["snow"],
    "ice": ["ice"],
    "smoke": ["smoke"],
    "fire": ["fire"],
    "ash": ["ash"],
    "burn": ["burn"],
    "mountain": ["mountain"],
    "red": ["red"],
    "green": ["green"],
    "yellow": ["yellow"],
    "white": ["white"],
    "black": ["black"],
    "night": ["night"],
    "day": ["day"],
    "year": ["year"],
    "warm": ["warm"],
    "cold": ["cold"],
    "full": ["full"],
    "new": ["new"],
    "old": ["old"],
    "good": ["good"],
    "bad": ["bad"],
    "name": ["name"],
    "house": [],  # not a Swadesh id here but useful
}


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"missing {SRC}")
    OUT.parent.mkdir(parents=True, exist_ok=True)

    entries: dict[str, dict] = {}
    by_gloss: dict[str, list[str]] = defaultdict(list)
    swadesh_suggest: dict[str, str] = {}

    with SRC.open(encoding="utf-8") as f:
        for line in f:
            o = json.loads(line)
            word = o.get("word")
            if not word:
                continue
            pos = o.get("pos") or ""
            glosses = []
            for s in o.get("senses") or []:
                glosses.extend(s.get("glosses") or [])
            rec = entries.setdefault(
                word,
                {"dlm": word, "pos": [], "glosses_en": [], "etymology": None, "sources": ["kaikki"]},
            )
            if pos and pos not in rec["pos"]:
                rec["pos"].append(pos)
            for g in glosses:
                if g not in rec["glosses_en"]:
                    rec["glosses_en"].append(g)
                by_gloss[g.strip().lower()].append(word)
            if o.get("etymology_text") and not rec["etymology"]:
                rec["etymology"] = o["etymology_text"][:240]

    # Prefer first kaikki hit per English gloss for Swadesh overrides
    for gloss, ids in GLOSS_TO_IDS.items():
        words = by_gloss.get(gloss) or []
        if not words:
            continue
        # prefer shorter / more citation-like
        best = sorted(set(words), key=lambda w: (len(w), w))[0]
        for cid in ids:
            swadesh_suggest[cid] = best

    out = {
        "meta": {
            "lang": "dlm",
            "source": "https://kaikki.org/dictionary/Dalmatian/",
            "file": SRC.name,
            "n_entries": len(entries),
            "n_glosses": len(by_gloss),
            "n_swadesh_suggestions": len(swadesh_suggest),
        },
        "swadesh_suggestions": swadesh_suggest,
        "entries": entries,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {OUT}")
    print(json.dumps(out["meta"], indent=2))
    print("swadesh suggestions:", swadesh_suggest)


if __name__ == "__main__":
    from collections import defaultdict

    main()
