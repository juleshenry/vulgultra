#!/usr/bin/env python3
"""Fetch Verbix conjugations for Aragonese lemmas already in the Kaikki harvest.

Non-commercial use under Verbix CC BY-NC 3.0: cite Verbix and link
https://www.verbix.com. Responses are cached under data/sources/verbix/an/.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vulgultra.verbix_an import harvest_lemmas  # noqa: E402

WORDS = ROOT / "data" / "words"
CACHE = ROOT / "data" / "sources" / "verbix" / "an"
OUT = ROOT / "data" / "conjugation" / "sources" / "an_verbix.json"
KAIKKI_AN = WORDS / "kaikki-an.jsonl"
AN_JSON = ROOT / "data" / "conjugation" / "sources" / "an.json"


def lemma_list() -> list[str]:
    lemmas: set[str] = set()
    if AN_JSON.is_file():
        document = json.loads(AN_JSON.read_text(encoding="utf-8"))
        for paradigm in document.get("paradigms") or []:
            lemma = str(paradigm.get("lemma") or "").strip()
            if lemma:
                lemmas.add(lemma)
    if KAIKKI_AN.is_file():
        for line in KAIKKI_AN.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("pos") != "verb":
                continue
            word = str(entry.get("word") or "").strip()
            if not word:
                continue
            # Prefer lemma senses; also collect form-of targets lightly via an.json.
            senses = entry.get("senses") or []
            if any(isinstance(sense, dict) and not sense.get("form_of") for sense in senses):
                lemmas.add(word)
    # Docs sample / auxiliaries that fill thin Kaikki holes.
    lemmas.update({"trobar", "beber", "partir", "falar", "haber", "estar", "ser", "renaixer"})
    return sorted(lemmas)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="refetch even if cached")
    parser.add_argument("--sleep", type=float, default=0.2, help="delay between requests")
    parser.add_argument("--limit", type=int, default=0, help="optional lemma cap for smoke tests")
    args = parser.parse_args()

    lemmas = lemma_list()
    if args.limit > 0:
        lemmas = lemmas[: args.limit]
    if not lemmas:
        print("no Aragonese lemmas found", file=sys.stderr)
        return 1

    print(f"harvesting {len(lemmas)} lemmas from Verbix → {CACHE}")
    document = harvest_lemmas(
        lemmas, cache_dir=CACHE, sleep_s=args.sleep, force=args.force,
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    stats = document["metadata"]["stats"]
    print(f"wrote {OUT}")
    print(
        f"  paradigms={len(document['paradigms'])} "
        f"attested={stats['attested']} generated={stats['generated']} empty={stats['empty']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
