#!/usr/bin/env python3
"""Stream Kaikki JSONL dumps and keep only verb entries.

Full language dumps are hundreds of MB to >1GB. This writes a much smaller
`data/words/kaikki-{code}.jsonl` containing verb rows only.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORDS = ROOT / "data" / "words"

# Kaikki.org dictionary folder / file stem → Vulgultra lect code.
KAIKKI_LECTS = {
    "es": "Spanish",
    "pt": "Portuguese",
    "gl": "Galician",
    "ca": "Catalan",
    "fr": "French",
    "it": "Italian",
    "ro": "Romanian",
    "lmo": "Lombard",
    "eml": "Emilian",
    "nap": "Neapolitan",
}

USER_AGENT = "vulgultra-research/0.1 (+noncommercial morphology corpus)"


def dump_url(name: str) -> str:
    return (
        f"https://kaikki.org/dictionary/{name}/"
        f"kaikki.org-dictionary-{name}.jsonl"
    )


def is_verb_line(line: bytes) -> bool:
    # Fast path before JSON parse. Kaikki uses "pos": "verb".
    return b'"pos": "verb"' in line or b'"pos":"verb"' in line


def is_lemma_with_forms(entry: dict) -> bool:
    """Keep conjugated lemma rows; drop standalone form-of noise."""
    if entry.get("pos") != "verb":
        return False
    senses = entry.get("senses") or []
    is_lemma = any(isinstance(sense, dict) and not sense.get("form_of") for sense in senses)
    forms = entry.get("forms") or []
    return bool(is_lemma and forms)


def fetch_lect(code: str, name: str, *, force: bool = False) -> Path:
    out = WORDS / f"kaikki-{code}.jsonl"
    if out.is_file() and out.stat().st_size > 0 and not force:
        print(f"skip {code}: {out} exists ({out.stat().st_size} bytes)")
        return out
    url = dump_url(name)
    print(f"fetch {code} ← {url}")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    kept = 0
    seen = 0
    tmp = out.with_suffix(".jsonl.partial")
    with urllib.request.urlopen(req, timeout=120) as response, tmp.open("wb") as handle:
        for raw in response:
            seen += 1
            if seen % 200000 == 0:
                print(f"  {code}: scanned {seen:,} kept {kept:,}")
            if not is_verb_line(raw):
                continue
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if not is_lemma_with_forms(entry):
                continue
            handle.write(raw if raw.endswith(b"\n") else raw + b"\n")
            kept += 1
    tmp.replace(out)
    print(f"wrote {out} ({kept:,} lemma+forms verbs from {seen:,} lines)")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "lects",
        nargs="*",
        help=f"lect codes (default: all of {', '.join(KAIKKI_LECTS)})",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    codes = args.lects or list(KAIKKI_LECTS)
    WORDS.mkdir(parents=True, exist_ok=True)
    for code in codes:
        name = KAIKKI_LECTS.get(code)
        if not name:
            print(f"unknown lect {code}", file=sys.stderr)
            return 1
        fetch_lect(code, name, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
