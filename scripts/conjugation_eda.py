#!/usr/bin/env python3
"""Normalize sourced Romance paradigms and emit linkage/coverage EDA."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vulgultra.conjugation_eda import (  # noqa: E402
    SCHEMA,
    analyze,
    load_documents,
    normalize_document,
    template_seed_paradigms,
)
from vulgultra.romance_swadesh import SOURCE_LANGS  # noqa: E402


def write_json(value: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        help="JSON file or directory of normalized source paradigms",
    )
    parser.add_argument(
        "--from-templates",
        action="store_true",
        help="use internal ending templates as a clearly labeled bootstrap fixture",
    )
    parser.add_argument(
        "-o", "--output", type=Path,
        default=ROOT / "data/eda/conjugation_eda.json",
        help="EDA JSON output path",
    )
    parser.add_argument(
        "--normalized-output", type=Path,
        help="also write the normalized paradigm corpus",
    )
    parser.add_argument(
        "--markdown-output", type=Path,
        help="also write a human-readable EDA report",
    )
    args = parser.parse_args()
    if bool(args.input) == bool(args.from_templates):
        parser.error("choose exactly one of --input or --from-templates")

    if args.from_templates:
        paradigms = template_seed_paradigms()
        source_note = "internal ending templates; not collected full conjugations"
    else:
        paradigms = load_documents(args.input)
        source_note = "normalized external paradigm sources"

    result = analyze(paradigms, expected_lects=SOURCE_LANGS)
    result["metadata"]["source_note"] = source_note
    result["metadata"]["schema"] = SCHEMA
    write_json(result, args.output)
    if args.normalized_output:
        write_json({"schema": SCHEMA, "paradigms": paradigms}, args.normalized_output)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        from vulgultra.conjugation_eda import render_markdown
        args.markdown_output.write_text(render_markdown(result), encoding="utf-8")

    coverage = result["coverage"]
    print(f"wrote {args.output}")
    print(f"  lects: {coverage['lect_count']}/{len(SOURCE_LANGS)}")
    print(f"  paradigms: {coverage['paradigm_count']}")
    missing = coverage["missing_expected_lects"]
    if missing:
        print(f"  missing lects: {', '.join(missing)}")
    print(f"  candidate links: {sum(len(p['links']) for p in result['paradigms'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
