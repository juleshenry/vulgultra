#!/usr/bin/env python3
"""Dalmatian model verb kantúr from Verbix docs (one-page capture).

Kaikki person recovery in conjugation_harvest.py fills the larger lemma set.
This file adds the documented kantúr sample with class -ur.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data" / "conjugation" / "sources" / "dlm_diseux.json"
DOCS_URL = "https://docs.verbix.com/Languages/Dalmatian"
SLOTS = ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")


def row(*forms: str, feature: str) -> dict:
    out = {}
    for slot, form in zip(SLOTS, forms):
        form = form.strip()
        if not form or form == "—":
            continue
        out[slot] = {
            "form": form,
            "phonemes": [],
            "source_label": feature,
            "source_url": DOCS_URL,
        }
    return out


def main() -> int:
    paradigm = {
        "lect": "dlm",
        "lemma": "kantúr",
        "class_source": "-ur",
        "regularity": "model",
        "source": {
            "attested": True,
            "title": "Verbix Dalmatian:kantúr",
            "url": DOCS_URL,
            "provider": "docs.verbix.com",
            "citation_note": "One-page Verbix docs sample. 3sg/3pl syncretic in the source table.",
        },
        "cells": {
            "indicative.present": row(
                "kantaja", "kantaja", "kantaja", "kantuóme", "kantuóte", "kantája",
                feature="indicative.present",
            ),
            "indicative.imperfect": row(
                "kantúa", "—", "kantúa", "—", "—", "—",
                feature="indicative.imperfect",
            ),
            "indicative.future": row(
                "kantuóra", "—", "—", "—", "—", "—",
                feature="indicative.future",
            ),
            "subjunctive.imperfect": row(
                "kantás", "kantúre", "kantás", "kantesáime", "kantesáite", "—",
                feature="subjunctive.imperfect",
            ),
            "imperative": row(
                "—", "kantája", "—", "kantuóme", "kantuóte", "—",
                feature="imperative",
            ),
        },
    }
    # Drop empty-form cells created by "—" placeholders.
    for feature, cells in list(paradigm["cells"].items()):
        paradigm["cells"][feature] = {
            slot: cell for slot, cell in cells.items() if cell["form"] != "—"
        }
    document = {
        "schema": "vulgultra.conjugation.v1",
        "metadata": {
            "lect": "dlm",
            "purpose": "Dalmatian kantúr sample from Verbix docs",
            "provider": "docs.verbix.com",
            "attribution": "Verbix Dalmatian docs (https://docs.verbix.com/Languages/Dalmatian)",
            "ending_inventories": {},
            "optimizer_involved": False,
        },
        "paradigms": [paradigm],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
