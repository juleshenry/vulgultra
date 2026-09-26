#!/usr/bin/env python3
"""Harvest Istriot avì tables from the vendored Verbix docs capture.

One-page capture only (docs.verbix.com/Languages/Istriot). Feminine 3sg/3pl
are stored as alternates on the masculine 3rd-person cells.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

TABLES = ROOT / "vendor" / "istriot" / "verbix_avi_tables.txt"
OUT = ROOT / "data" / "conjugation" / "sources" / "ist_diseux.json"
DOCS_URL = "https://docs.verbix.com/Languages/Istriot"

SLOTS = ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")

# 8-row Istriot grid → 6 slots. Indices 2/3 are 3sg m/f; 6/7 are 3pl m/f.
ROW_SLOT = {0: "1sg", 1: "2sg", 2: "3sg", 3: "3sg", 4: "1pl", 5: "2pl", 6: "3pl", 7: "3pl"}

PRONOUN = re.compile(
    r"^(?:meî|teî|loû|gìla|nùi|vùi|lùri|lùre)\s+"
    r"(?:ch['’]i|ca\s+ti|ch['’]el|ca\s+la|ch['’]i|ca\s+li|i|ti|el|la|li)\s+",
    re.I,
)


def strip_pronoun(form: str) -> str:
    text = form.strip()
    text = PRONOUN.sub("", text)
    text = text.split(" - ")[0].strip()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def cell(form: str, alts: list[str], *, label: str) -> dict:
    packed = {
        "form": form,
        "phonemes": [],
        "source_label": label,
        "source_url": DOCS_URL,
    }
    extras = [item for item in alts if item and item != form]
    if extras:
        packed["notes"] = extras
    return packed


def parse_blocks(text: str) -> dict[str, list[str]]:
    """Pull left/right columns from the two-column Verbix dumps."""
    # Each TAM pair is introduced by a header line with two names.
    headers = [
        ("indicative.present", "indicative.imperfect"),
        ("subjunctive.present", "subjunctive.imperfect"),
        ("conditional", "indicative.future"),
    ]
    lines = [line.rstrip() for line in text.splitlines()]
    blocks: dict[str, list[str]] = {name: [] for pair in headers for name in pair}
    pair_index = -1
    for line in lines:
        folded = line.lower()
        if "indicativo presente" in folded or "congiuntivo presente" in folded or (
            "condizionale" in folded and "futuro" in folded
        ):
            pair_index += 1
            continue
        if pair_index < 0 or pair_index >= len(headers):
            continue
        parts = re.split(r"\s{2,}", line.strip())
        if len(parts) < 2:
            continue
        left, right = parts[0], parts[1]
        if not left or left.startswith("("):
            continue
        left_name, right_name = headers[pair_index]
        blocks[left_name].append(strip_pronoun(left))
        blocks[right_name].append(strip_pronoun(right))
    return blocks


def pack_feature(forms: list[str], feature: str) -> dict:
    by_slot: dict[str, list[str]] = {slot: [] for slot in SLOTS}
    for index, form in enumerate(forms):
        slot = ROW_SLOT.get(index)
        if not slot or not form:
            continue
        if form not in by_slot[slot]:
            by_slot[slot].append(form)
    row = {}
    for slot, values in by_slot.items():
        if not values:
            continue
        row[slot] = cell(values[0], values[1:], label=feature)
    return row


def main() -> int:
    text = TABLES.read_text(encoding="utf-8", errors="replace")
    blocks = parse_blocks(text)
    cells = {}
    for feature, forms in blocks.items():
        row = pack_feature(forms, feature)
        if row:
            cells[feature] = row
            print(feature, {slot: cell["form"] for slot, cell in row.items()})
    paradigm = {
        "lect": "ist",
        "lemma": "avì",
        "class_source": "avì",
        "regularity": "irregular",
        "source": {
            "attested": True,
            "title": "Verbix Istriot:avì",
            "url": DOCS_URL,
            "provider": "docs.verbix.com",
            "citation_note": "One-page Verbix docs capture; feminine 3rd-person as alternates.",
        },
        "cells": cells,
    }
    document = {
        "schema": "vulgultra.conjugation.v1",
        "metadata": {
            "lect": "ist",
            "purpose": "Istriot avì from Verbix docs (one-page capture)",
            "provider": "docs.verbix.com",
            "attribution": "Verbix Istriot docs (https://docs.verbix.com/Languages/Istriot)",
            "ending_inventories": {},
            "optimizer_involved": False,
        },
        "paradigms": [paradigm],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT} features={list(cells)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
