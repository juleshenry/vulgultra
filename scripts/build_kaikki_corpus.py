#!/usr/bin/env python3
"""Turn Kaikki/Wiktextract JSONL into data/words/{code}_words.json."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORDS = ROOT / "data" / "words"


def ingest(src: Path, code: str) -> dict:
    entries: dict[str, dict] = {}
    by_gloss: dict[str, list[str]] = defaultdict(list)
    with src.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            o = json.loads(line)
            word = o.get("word")
            if not word:
                continue
            rec = entries.setdefault(
                word,
                {
                    code: word,
                    "pos": [],
                    "glosses_en": [],
                    "etymology": None,
                    "sources": ["kaikki"],
                },
            )
            pos = o.get("pos")
            if pos and pos not in rec["pos"]:
                rec["pos"].append(pos)
            for s in o.get("senses") or []:
                for g in s.get("glosses") or []:
                    if g not in rec["glosses_en"]:
                        rec["glosses_en"].append(g)
                    by_gloss[g.strip().lower()].append(word)
            if o.get("etymology_text") and not rec["etymology"]:
                rec["etymology"] = o["etymology_text"][:240]
    out = {
        "meta": {
            "lang": code,
            "source": f"https://kaikki.org/dictionary/",
            "file": src.name,
            "n_entries": len(entries),
            "n_glosses": len(by_gloss),
        },
        "entries": entries,
    }
    dest = WORDS / f"{code}_words.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out["meta"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="ingest every data/words/kaikki-*.jsonl")
    ap.add_argument("files", nargs="*", help="kaikki-CODE.jsonl paths")
    args = ap.parse_args()
    files = [Path(p) for p in args.files]
    if args.all or not files:
        files = sorted(WORDS.glob("kaikki-*.jsonl"))
        # plus root-level dlm/rm if present
        for extra in (
            ROOT / "kaikki.org-dictionary-Dalmatian.jsonl",
            ROOT / "kaikki.org-dictionary-Romansh.jsonl",
        ):
            if extra.exists():
                files.append(extra)
    if not files:
        raise SystemExit("no kaikki jsonl files found")
    WORDS.mkdir(parents=True, exist_ok=True)
    for src in files:
        name = src.name
        if name.startswith("kaikki-") and name.endswith(".jsonl"):
            code = name[len("kaikki-") : -len(".jsonl")]
        elif "Dalmatian" in name:
            code = "dlm"
        elif "Romansh" in name:
            code = "rm"
        else:
            print("skip", src)
            continue
        meta = ingest(src, code)
        print(f"{code:4}  lemmas={meta['n_entries']:5}  glosses={meta['n_glosses']:5}  ← {src.name}")


if __name__ == "__main__":
    main()
