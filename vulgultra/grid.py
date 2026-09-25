"""Meaning-grid loading primitives.

The complete grid is retained separately from the minimum-syllable candidate
shortlist.  Evidence is carried as data, so an optimizer result can be traced
back to a cell without treating English labels as source forms.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from vulgultra.pipeline_constants import BIBLE_GRID_SCHEMA


def form_records(raw: Any) -> list[dict[str, str]]:
    """Normalize a grid cell while retaining evidence and relation."""
    values = raw if isinstance(raw, list) else [raw]
    records: list[dict[str, str]] = []
    for value in values:
        if isinstance(value, str):
            form = value.strip()
            record = {"form": form, "evidence": "grid", "relation": "direct"}
        elif isinstance(value, dict):
            form = str(value.get("form") or value.get("word") or "").strip()
            evidence = value.get("evidence") or value.get("source") or "grid"
            record = {
                "form": form,
                "evidence": json.dumps(evidence, ensure_ascii=False, sort_keys=True)
                if isinstance(evidence, (dict, list)) else str(evidence),
                "relation": str(value.get("relation") or "direct"),
            }
        else:
            continue
        if record["form"]:
            records.append(record)
    return records


def load_bible_grid(path: str | Path) -> list[dict[str, Any]]:
    """Load and validate the optional compiled Bible grid."""
    source = Path(path)
    data = json.loads(source.read_text(encoding="utf-8"))
    if data.get("schema") != BIBLE_GRID_SCHEMA:
        raise ValueError(f"{source}: expected schema {BIBLE_GRID_SCHEMA}")
    concepts = data.get("concepts")
    if not isinstance(concepts, list):
        raise ValueError(f"{source}: concepts must be an array")
    return concepts
