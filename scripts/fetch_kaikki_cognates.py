#!/usr/bin/env python3
"""Collect the cognates Wiktionary's etymologies name beside a Latin source.

The Romanian entry *apă* says: inherited from Latin *aqua*; compare
Aromanian *apã*, Megleno-Romanian *apu*, Istro-Romanian *åpę*. For a lect
with few entries of its own that sentence is the record: the form is named,
and tied to the Latin word, in an entry of its sister. Every extract is
read, the large ones off the network and the small ones from
`data/words/`; an entry counts when its etymology gives one Latin source
first and names cognates in the lects.

Writes `data/sources/kaikki_full/cognates.tsv`: `latin`, `lect`, `form`,
`named_in` (the entry that names it).

    python3 scripts/fetch_kaikki_cognates.py
"""

from __future__ import annotations

import collections
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from extract_wikt_translations import CODES  # noqa: E402
from fetch_kaikki_full import LECTS, OUT, USER_AGENT, url  # noqa: E402

WORDS = ROOT / "data" / "words"
TARGET = OUT / "cognates.tsv"
LATIN_CODES = {"la", "la-vul", "la-lat", "la-med", "la-ecc", "la-cla", "LL.", "VL.", "ML."}
ETYMOLOGY = {"inh", "inh+", "bor", "bor+", "der", "der+", "lbor", "slbor", "uder", "inh-lite"}
COGNATE = {"cog", "cognate", "cog-lite"}
# The anchors are named as cognates too; they keep their own codes.
LECT_OF = {**CODES, "fr": "fr", "es": "es", "pt": "pt", "it": "it", "ca": "ca", "ro": "ro"}


def rows(lines, source: str):
    for line in lines:
        if b'"cog' not in line:
            continue
        entry = json.loads(line)
        templates = entry.get("etymology_templates") or []
        latin = next((template["args"].get("3", "") for template in templates
                      if template.get("name") in ETYMOLOGY and (template.get("args") or {}).get("2") in LATIN_CODES), "")
        if not latin or not entry.get("word"):
            continue
        for template in templates:
            args = template.get("args") or {}
            lect = LECT_OF.get(args.get("1", ""))
            form = (args.get("2") or "").strip()
            if template.get("name") in COGNATE and lect and lect != "la" and form and form != "-" and "*" not in form:
                yield latin, lect, form, f"{source}:{entry['word']}"


def main() -> None:
    found: set[tuple[str, str, str, str]] = set()
    for code, name in LECTS.items():
        request = urllib.request.Request(url(name), headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=180) as response:
            before = len(found)
            found.update(rows(response, code))
        print(f"{code}: {len(found) - before:,} cognates named", flush=True)
    for path in sorted(WORDS.glob("kaikki-*.jsonl")):
        code = path.stem.removeprefix("kaikki-")
        if code in LECTS or "-" in code:
            continue
        with path.open("rb") as stream:
            before = len(found)
            found.update(rows(stream, CODES.get(code, code)))
        print(f"{code}: {len(found) - before:,} cognates named", flush=True)
    with TARGET.open("w", encoding="utf-8") as out:
        out.write("latin\tlect\tform\tnamed_in\n")
        for row in sorted(found):
            out.write("\t".join(row) + "\n")
    per_lect = collections.Counter(lect for _, lect, _, _ in found)
    print(f"{len(found):,} rows → {TARGET}", dict(per_lect.most_common()))


if __name__ == "__main__":
    main()
