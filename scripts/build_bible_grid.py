#!/usr/bin/env python3
"""Compile concept-aligned Bible lexicons for the five major Romance lects.

The input TSVs contain lexical entries already aligned to stable concept IDs;
verse alignment by itself is not enough to claim word-level equivalence.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

LANGUAGES = ("fr", "es", "pt", "it", "ro")
REQUIRED = ("concept_id", "gloss_en", "pos", "form", "edition", "license", "verse_refs")
RELATIONS = {"direct", "nearest_equivalent", "attested_phrase"}


def build(input_dir: Path) -> dict:
    concepts: dict[str, dict] = {}
    editions: dict[str, dict[str, str]] = {}
    for lang in LANGUAGES:
        path = input_dir / f"{lang}.tsv"
        if not path.is_file():
            raise FileNotFoundError(f"Missing required Bible lexicon: {path}")
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            missing = set(REQUIRED) - set(reader.fieldnames or ())
            if missing:
                raise ValueError(f"{path}: missing columns {sorted(missing)}")
            for line_no, row in enumerate(reader, start=2):
                cid = (row.get("concept_id") or "").strip()
                gloss = (row.get("gloss_en") or "").strip()
                form = (row.get("form") or "").strip()
                edition = (row.get("edition") or "").strip()
                license_name = (row.get("license") or "").strip()
                relation = (row.get("relation") or "direct").strip()
                refs = (row.get("verse_refs") or "").strip()
                if not all((cid, gloss, form, edition, license_name, refs)):
                    raise ValueError(f"{path}:{line_no}: concept, gloss, form, edition, license, and verse_refs are required")
                if relation not in RELATIONS:
                    raise ValueError(f"{path}:{line_no}: relation must be one of {sorted(RELATIONS)}")

                concept = concepts.setdefault(cid, {
                    "id": cid,
                    "gloss_en": gloss,
                    "pos": (row.get("pos") or "").strip(),
                    "forms": {},
                })
                if concept["gloss_en"].casefold() != gloss.casefold():
                    raise ValueError(f"{path}:{line_no}: inconsistent English gloss for {cid!r}")
                if concept["pos"] and row.get("pos") and concept["pos"] != row["pos"].strip():
                    raise ValueError(f"{path}:{line_no}: inconsistent part of speech for {cid!r}")

                evidence = {
                    "type": "bible-lexicon",
                    "language": lang,
                    "edition": edition,
                    "license": license_name,
                    "verse_refs": [v.strip() for v in refs.split(";") if v.strip()],
                    "source_url": (row.get("source_url") or "").strip(),
                }
                record = {"form": form, "relation": relation, "evidence": evidence}
                cell = concept["forms"].setdefault(lang, [])
                if record not in cell:
                    cell.append(record)
                edition_record = {"edition": edition, "license": license_name}
                previous = editions.get(lang)
                if previous is not None and previous != edition_record:
                    raise ValueError(f"{path}:{line_no}: multiple editions/licenses in one language file")
                editions[lang] = edition_record

    return {
        "schema": "vulgultra.bible-grid.v1",
        "metadata": {
            "anchor_languages": list(LANGUAGES),
            "editions": editions,
            "alignment_note": "Concept-level lexical alignment is explicit; verse co-occurrence alone is not treated as equivalence.",
        },
        "concepts": [concepts[cid] for cid in sorted(concepts)],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("data/bible/lexicons"))
    parser.add_argument("--output", type=Path, default=Path("data/bible/concept_grid.json"))
    args = parser.parse_args()
    data = build(args.input_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(data['concepts'])} Bible-grid concepts to {args.output}")


if __name__ == "__main__":
    main()
