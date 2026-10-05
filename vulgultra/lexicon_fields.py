"""Join grid fields onto the selected roots after the optimizer has run.

The optimizer needs none of these fields to choose a root, so they do not
cross the Rust boundary: the lexicon it writes is joined back to the concept
grid by concept id. Output is key-sorted, so the same selection always
produces the same file.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

# Per-concept fields; the grid is authoritative for them.
CONCEPT_FIELDS = ("gloss_en", "pos")


def annotate_lexicon(lexicon: dict[str, Any], grid: dict[str, Any]) -> dict[str, Any]:
    """Return the lexicon with every root carrying its concept's grid fields."""
    rows = {row["id"]: row for row in grid.get("concepts", [])}
    roots: dict[str, dict[str, Any]] = {}
    for concept_id, root in lexicon.get("roots", {}).items():
        if concept_id not in rows:
            raise KeyError(f"root {concept_id!r} has no row in the concept grid")
        roots[concept_id] = {
            **root,
            **{field: rows[concept_id].get(field, "") for field in CONCEPT_FIELDS},
        }
    return {**lexicon, "roots": roots}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-l", "--lexicon", type=Path, default=Path("data/vulgultra_lexicon.json"))
    parser.add_argument("-g", "--grid", type=Path, default=Path("data/concept_grid.json"))
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="Defaults to rewriting the lexicon in place")
    args = parser.parse_args()

    lexicon = json.loads(args.lexicon.read_text(encoding="utf-8"))
    grid = json.loads(args.grid.read_text(encoding="utf-8"))
    output = args.output or args.lexicon
    output.write_text(
        json.dumps(annotate_lexicon(lexicon, grid), indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    print(f"Joined {', '.join(CONCEPT_FIELDS)} onto {len(lexicon.get('roots', {}))} roots: {output}")


if __name__ == "__main__":
    main()
