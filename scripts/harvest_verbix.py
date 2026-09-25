#!/usr/bin/env python3
"""Harvest Verbix conjugations for one or more Vulgultra lects.

Lemma seeds come from existing conjugation JSON, Kaikki verb dumps, and
infinitive-looking entries in {code}_words.json. CC BY-NC 3.0 — cite Verbix.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vulgultra.verbix import LECT_CONFIG, harvest_lemmas  # noqa: E402

WORDS = ROOT / "data" / "words"
CACHE_ROOT = ROOT / "data" / "sources" / "verbix"
OUT_ROOT = ROOT / "data" / "conjugation" / "sources"

SEED_IRREGULARS = {
    "es": ["hablar", "comer", "vivir", "ser", "estar", "haber", "ir", "tener", "hacer", "decir"],
    "pt": ["falar", "comer", "viver", "ser", "estar", "haver", "ir", "ter", "fazer", "dizer"],
    "gl": ["falar", "comer", "vivir", "ser", "estar", "haber", "ir", "ter", "facer", "dicir"],
    "ca": ["parlar", "menjar", "viure", "ser", "estar", "haver", "anar", "tenir", "fer", "dir"],
    "fr": ["parler", "finir", "vendre", "être", "avoir", "aller", "faire", "dire", "venir"],
    "it": ["parlare", "credere", "dormire", "essere", "avere", "andare", "fare", "dire", "stare"],
    "ro": ["a", "vorbi", "lucra", "fi", "avea", "merge", "face", "zice"],
    "an": ["trobar", "beber", "partir", "estar", "ser", "haber", "renaixer"],
    "frp": [
        "parlar", "ésser", "etre", "avêr", "aver", "avé", "fâre", "fare",
        "alar", "allar", "venir", "tenir", "vêre", "dire", "prendre",
    ],
    "fur": ["fevelâ", "jessi", "vê", "lâ"],
    "mwl": ["falar", "comer", "bibir", "ser", "star", "haber", "ir"],
    "oc": ["parlar", "béure", "partir", "èsser", "aver", "anar"],
    "rm": ["clamar", "esser", "haver", "ir"],
    "pms": ["parlé", "esse", "avé", "andé"],
    "co": ["parlà", "esse", "avè", "andà"],
    "lld": ["jì", "ester", "avé", "fé"],
    "gsc": ["parlar", "estar", "aver", "anar", "préner", "véder", "díser", "finar"],
}


def lemmas_from_kaikki(lect: str) -> set[str]:
    path = WORDS / f"kaikki-{lect}.jsonl"
    out: set[str] = set()
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("pos") != "verb":
            continue
        word = str(entry.get("word") or "").strip()
        senses = entry.get("senses") or []
        if any(isinstance(s, dict) and not s.get("form_of") for s in senses):
            if word:
                out.add(word)
    return out


def lemmas_from_words_json(lect: str) -> set[str]:
    path = WORDS / f"{lect}_words.json"
    out: set[str] = set()
    if not path.is_file():
        return out
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("entries") if isinstance(data, dict) else data
    if not isinstance(entries, dict):
        return out
    endings = LECT_CONFIG.get(lect, {}).get("endings") or ("ar", "er", "ir")
    endings = tuple(sorted(endings, key=len, reverse=True))
    for key, value in entries.items():
        word = str(key).strip()
        if not word:
            continue
        pos = []
        if isinstance(value, dict):
            raw_pos = value.get("pos") or []
            pos = raw_pos if isinstance(raw_pos, list) else [raw_pos]
        if "verb" in pos or any(word.lower().endswith(end) for end in endings):
            # Avoid obvious non-verbs when POS missing: require ending match.
            if "verb" in pos or any(word.lower().endswith(end) for end in endings):
                out.add(word)
    return out


def lemmas_from_existing(lect: str) -> set[str]:
    path = OUT_ROOT / f"{lect}.json"
    out: set[str] = set()
    if not path.is_file():
        return out
    data = json.loads(path.read_text(encoding="utf-8"))
    for paradigm in data.get("paradigms") or []:
        lemma = str(paradigm.get("lemma") or "").strip()
        if lemma:
            out.add(lemma)
    return out


def lemma_list(lect: str, *, limit: int = 0) -> list[str]:
    lemmas = set(SEED_IRREGULARS.get(lect, []))
    lemmas |= lemmas_from_existing(lect)
    lemmas |= lemmas_from_kaikki(lect)
    # words.json can be huge; only use when Kaikki is thin.
    if len(lemmas) < 200:
        lemmas |= lemmas_from_words_json(lect)
    ordered = sorted(lemmas)
    if limit > 0:
        # Keep seeds first.
        seeds = [w for w in SEED_IRREGULARS.get(lect, []) if w in lemmas]
        rest = [w for w in ordered if w not in seeds]
        ordered = seeds + rest
        ordered = ordered[:limit]
    return ordered


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "lects",
        nargs="*",
        help=f"lect codes (default: all configured: {', '.join(sorted(LECT_CONFIG))})",
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--sleep", type=float, default=0.12)
    parser.add_argument("--limit", type=int, default=0, help="cap lemmas per lect")
    args = parser.parse_args()
    lects = args.lects or sorted(LECT_CONFIG)
    for lect in lects:
        if lect not in LECT_CONFIG:
            print(f"skip unknown lect {lect}", file=sys.stderr)
            continue
        lemmas = lemma_list(lect, limit=args.limit)
        if not lemmas:
            print(f"{lect}: no lemmas")
            continue
        print(f"{lect}: harvesting {len(lemmas)} lemmas")
        document = harvest_lemmas(
            lect,
            lemmas,
            cache_dir=CACHE_ROOT / lect,
            sleep_s=args.sleep,
            force=args.force,
        )
        OUT_ROOT.mkdir(parents=True, exist_ok=True)
        out = OUT_ROOT / f"{lect}_verbix.json"
        out.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        stats = document["metadata"]["stats"]
        print(
            f"  wrote {out} paradigms={len(document['paradigms'])} "
            f"attested={stats['attested']} generated={stats['generated']} empty={stats['empty']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
