"""Conjugation-corpus normalization and morpheme-linkage EDA.

This module deliberately stops before morphology optimization.  It provides a
stable interchange shape for sourced paradigms and records *candidate* links
between recurring phonemic material in the same person/number slot across
tense--mood cells.  A shared suffix is evidence, not an automatic morpheme
segmentation claim.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations
import json
from pathlib import Path
from typing import Any, Iterable


SCHEMA = "vulgultra.conjugation.v1"
PERSON_SLOTS = ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")
TEMPLATE_PERSON_ORDER = ("1sg", "1pl", "2sg", "2pl", "3sg", "3pl")

# These labels are deliberately descriptive.  They are not a claim that all
# lects have the same tense inventory; source labels remain in each record.
DEFAULT_FEATURES = (
    "indicative.present",
    "indicative.past",
    "indicative.future",
    "subjunctive.present",
    "theme.i",
    "theme.a",
)


def _as_phonemes(value: object) -> list[str]:
    """Normalize a JSON phoneme value without guessing IPA segmentation."""
    if isinstance(value, list):
        return [str(part) for part in value if str(part)]
    if isinstance(value, tuple):
        return [str(part) for part in value if str(part)]
    if isinstance(value, str):
        # A space-separated IPA field is unambiguous.  A compact string is
        # deliberately not segmented: affricates and multigraphs would make
        # code-point splitting false evidence.
        return value.split() if " " in value else []
    return []


def normalize_cell(
    value: object,
    *,
    lect: str,
    feature: str,
    slot: str | None = None,
) -> dict[str, Any]:
    """Normalize one cell while retaining source spelling and metadata.

    Accepted input is a string, or an object containing ``form`` and either
    ``phonemes``/``ipa``.  Missing phonemes are left empty so validation can
    report them instead of silently transcribing or inventing a segmentation.
    """
    if isinstance(value, str):
        raw: dict[str, Any] = {"form": value}
    elif isinstance(value, dict):
        raw = dict(value)
    else:
        raise ValueError(f"{lect}:{feature}:{slot}: cell must be a string/object")

    form = str(raw.get("form") or raw.get("word") or "").strip()
    if not form:
        raise ValueError(f"{lect}:{feature}:{slot}: cell has no form")
    phones = _as_phonemes(raw.get("phonemes", raw.get("ipa", [])))
    out: dict[str, Any] = {
        "form": form,
        "phonemes": phones,
        "source_label": str(raw.get("source_label") or raw.get("label") or ""),
    }
    if "ipa" in raw:
        out["ipa"] = raw["ipa"]
    for key in ("evidence", "source_url", "confidence", "notes"):
        if key in raw:
            out[key] = raw[key]
    return out


def normalize_document(document: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize a corpus document.

    Input may use either a top-level ``paradigms`` array or one paradigm
    object.  Every normalized paradigm has feature → six-slot cell maps.
    """
    if not isinstance(document, dict):
        raise ValueError("conjugation document must be an object")
    schema = document.get("schema")
    if schema not in (None, SCHEMA):
        raise ValueError(f"expected {SCHEMA}, got {schema!r}")
    paradigms = document.get("paradigms")
    if paradigms is None:
        paradigms = [document]
    if not isinstance(paradigms, list):
        raise ValueError("paradigms must be an array")

    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(paradigms):
        if not isinstance(raw, dict):
            raise ValueError(f"paradigms[{index}] must be an object")
        lect = str(raw.get("lect") or document.get("lect") or "").strip()
        if not lect:
            raise ValueError(f"paradigms[{index}] has no lect")
        lemma = str(raw.get("lemma") or raw.get("verb") or "").strip()
        if not lemma:
            raise ValueError(f"{lect}: paradigm has no lemma")
        cells_in = raw.get("cells") or raw.get("paradigms")
        if not isinstance(cells_in, dict):
            raise ValueError(f"{lect}:{lemma}: cells must be an object")

        cells: dict[str, dict[str, dict[str, Any]]] = {}
        for feature, row in cells_in.items():
            if not isinstance(row, dict):
                raise ValueError(f"{lect}:{lemma}:{feature}: row must be an object")
            feature_id = str(feature)
            out_row: dict[str, dict[str, Any]] = {}
            for slot, value in row.items():
                slot_id = str(slot)
                if slot_id not in PERSON_SLOTS and not slot_id.startswith("nonfinite."):
                    # Preserve source-specific slots, but make the anomaly
                    # visible to the EDA rather than dropping it.
                    slot_id = slot_id
                out_row[slot_id] = normalize_cell(
                    value, lect=lect, feature=feature_id, slot=slot_id,
                )
            cells[feature_id] = out_row

        normalized.append({
            "lect": lect,
            "lemma": lemma,
            "class_source": str(raw.get("class_source") or raw.get("class") or ""),
            "source": raw.get("source") or document.get("source") or {},
            "regularity": str(raw.get("regularity") or "unknown"),
            "cells": cells,
        })

    return {
        "schema": SCHEMA,
        "metadata": document.get("metadata") or {},
        "paradigms": normalized,
    }


def load_documents(path: str | Path) -> list[dict[str, Any]]:
    """Load one JSON file or every JSON file in a directory."""
    target = Path(path)
    paths = sorted(target.glob("*.json")) if target.is_dir() else [target]
    if not paths:
        raise FileNotFoundError(f"no JSON conjugation sources found at {target}")
    out: list[dict[str, Any]] = []
    for source_path in paths:
        document = json.loads(source_path.read_text(encoding="utf-8"))
        normalized = normalize_document(document)
        normalized["metadata"] = {
            **normalized.get("metadata", {}),
            "source_file": str(source_path),
        }
        for paradigm in normalized["paradigms"]:
            source = paradigm.get("source")
            if not isinstance(source, dict):
                source = {"source_value": source}
            paradigm["source"] = {**source, "source_file": str(source_path)}
        out.extend(normalized["paradigms"])
    return out


def _common_suffix(left: list[str], right: list[str]) -> tuple[str, ...]:
    result: list[str] = []
    for a, b in zip(reversed(left), reversed(right)):
        if a != b:
            break
        result.append(a)
    return tuple(reversed(result))


def _common_prefix(sequences: Iterable[list[str]]) -> tuple[str, ...]:
    rows = [row for row in sequences if row]
    if not rows:
        return ()
    result: list[str] = []
    for values in zip(*rows):
        if len(set(values)) != 1:
            break
        result.append(values[0])
    return tuple(result)


def analyze_paradigm(paradigm: dict[str, Any]) -> dict[str, Any]:
    """Find candidate cross-tense links for one normalized paradigm."""
    cells: dict[str, dict[str, dict[str, Any]]] = paradigm["cells"]
    links: list[dict[str, Any]] = []

    # Same person/number across tense-mood rows: a shared suffix is a
    # candidate person marker.  We require a proper suffix so identical whole
    # forms are reported as syncretism rather than confidently segmented.
    for slot in PERSON_SLOTS:
        occupied = [
            (feature, row[slot])
            for feature, row in cells.items()
            if slot in row and row[slot].get("phonemes")
        ]
        for (feature_a, cell_a), (feature_b, cell_b) in combinations(occupied, 2):
            suffix = _common_suffix(cell_a["phonemes"], cell_b["phonemes"])
            if not suffix:
                continue
            if len(suffix) >= min(len(cell_a["phonemes"]), len(cell_b["phonemes"])):
                continue
            links.append({
                "kind": "person_number_suffix",
                "slot": slot,
                "features": [feature_a, feature_b],
                "segments": list(suffix),
                "members": [
                    {"feature": feature_a, "slot": slot},
                    {"feature": feature_b, "slot": slot},
                ],
                "confidence": round(
                    len(suffix) / min(len(cell_a["phonemes"]), len(cell_b["phonemes"])),
                    3,
                ),
                "evidence": "shared-proper-suffix",
            })

    # Within one tense-mood row, a common prefix is only a stem/theme
    # candidate.  Label it cautiously; it may be lexical stem material rather
    # than an inflectional morpheme.
    for feature, row in cells.items():
        occupied = [
            (slot, cell) for slot, cell in row.items()
            if slot in PERSON_SLOTS and cell.get("phonemes")
        ]
        prefix = _common_prefix(cell["phonemes"] for _, cell in occupied)
        if len(prefix) < 2 or len(occupied) < 2:
            continue
        links.append({
            "kind": "within_feature_shared_prefix",
            "feature": feature,
            "segments": list(prefix),
            "members": [{"feature": feature, "slot": slot} for slot, _ in occupied],
            "confidence": round(len(prefix) / min(len(cell["phonemes"]) for _, cell in occupied), 3),
            "evidence": "shared-prefix-candidate",
        })

    return {
        "lect": paradigm["lect"],
        "lemma": paradigm["lemma"],
        "class_source": paradigm.get("class_source", ""),
        "links": links,
    }


def coverage_report(paradigms: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize six-slot coverage without fabricating missing forms."""
    by_lect: dict[str, dict[str, Any]] = {}
    for paradigm in paradigms:
        lect = paradigm["lect"]
        lect_report = by_lect.setdefault(lect, {
            "paradigms": 0,
            "lemmas": [],
            "features": {},
        })
        lect_report["paradigms"] += 1
        lect_report["lemmas"].append(paradigm["lemma"])
        for feature, row in paradigm["cells"].items():
            item = lect_report["features"].setdefault(feature, {
                "paradigms": 0,
                "occupied": 0,
                "expected": 0,
                "missing_slots": defaultdict(int),
            })
            item["paradigms"] += 1
            for slot in PERSON_SLOTS:
                item["expected"] += 1
                cell = row.get(slot)
                if cell and cell.get("form"):
                    item["occupied"] += 1
                else:
                    item["missing_slots"][slot] += 1
    for lect_report in by_lect.values():
        for item in lect_report["features"].values():
            item["missing_slots"] = dict(sorted(item["missing_slots"].items()))
        lect_report["lemmas"] = sorted(set(lect_report["lemmas"]))
    return {
        "lect_count": len(by_lect),
        "paradigm_count": len(paradigms),
        "by_lect": dict(sorted(by_lect.items())),
    }


def analyze(paradigms: list[dict[str, Any]], *, expected_lects: Iterable[str] = ()) -> dict[str, Any]:
    analyses = [analyze_paradigm(paradigm) for paradigm in paradigms]
    report = coverage_report(paradigms)
    observed = set(report["by_lect"])
    expected = set(expected_lects)
    report["missing_expected_lects"] = sorted(expected - observed)
    link_counts: dict[tuple[str, str, str], int] = defaultdict(int)
    for paradigm in analyses:
        for link in paradigm["links"]:
            link_counts[(
                str(link["kind"]),
                str(link.get("slot") or link.get("feature") or ""),
                "·".join(link["segments"]),
            )] += 1
    link_summary = [
        {"kind": kind, "axis": axis, "segments": segments.split("·"), "support": support}
        for (kind, axis, segments), support in sorted(
            link_counts.items(), key=lambda item: (-item[1], item[0]),
        )
    ]
    return {
        "schema": SCHEMA,
        "metadata": {
            "purpose": "conjugation coverage and candidate morpheme linkage EDA",
            "optimizer_involved": False,
            "segmentation_status": "candidate links; not asserted morphemes",
        },
        "coverage": report,
        "paradigms": analyses,
        "link_summary": link_summary,
    }


def render_markdown(result: dict[str, Any]) -> str:
    """Render a compact, source-agnostic EDA report."""
    coverage = result["coverage"]
    lines = [
        "# Conjugation EDA",
        "",
        "This report describes normalized paradigms and candidate phonemic links.",
        "It does not choose an optimizer paradigm or assert morpheme boundaries.",
        "",
        f"- Lects observed: **{coverage['lect_count']}**",
        f"- Paradigms: **{coverage['paradigm_count']}**",
        f"- Expected lects missing: **{len(coverage['missing_expected_lects'])}**",
        "",
        "## Coverage by lect",
        "",
        "| Lect | Paradigms | Features | Occupied / expected |",
        "|---|---:|---:|---:|",
    ]
    for lect, lect_report in sorted(coverage["by_lect"].items()):
        expected = sum(item["expected"] for item in lect_report["features"].values())
        occupied = sum(item["occupied"] for item in lect_report["features"].values())
        lines.append(
            f"| `{lect}` | {lect_report['paradigms']} | "
            f"{len(lect_report['features'])} | {occupied} / {expected} |"
        )
    lines.extend([
        "",
        "## Most-supported candidate links",
        "",
        "| Kind | Axis | Segments | Paradigm support |",
        "|---|---|---|---:|",
    ])
    for link in result.get("link_summary", [])[:40]:
        segments = " ".join(f"`{segment}`" for segment in link["segments"])
        lines.append(
            f"| `{link['kind']}` | `{link['axis']}` | {segments} | {link['support']} |"
        )
    if not result.get("link_summary"):
        lines.append("| — | — | — | 0 |")
    lines.extend([
        "",
        "## Interpretation",
        "",
        "Links are candidate evidence for later stem/theme/person analysis. "
        "A shared suffix is not yet a declared morpheme; segmentation and "
        "concordance constraints belong to the later optimizer phase.",
        "",
    ])
    return "\n".join(lines)


def template_seed_paradigms() -> list[dict[str, Any]]:
    """Export current internal ending templates as an explicitly non-source seed.

    This is useful for schema smoke tests and exposes all current lect keys,
    but it must not be mistaken for collected full conjugation evidence.
    """
    from vulgultra.paradigms import VERB_TEMPLATES
    from vulgultra.phonology import to_orthography
    from vulgultra.romance_swadesh import SOURCE_LANGS

    rows: list[dict[str, Any]] = []
    for lect in SOURCE_LANGS:
        template = VERB_TEMPLATES.get(lect, [])
        if not template:
            continue
        cells: dict[str, dict[str, Any]] = {}
        for index, feature in enumerate(DEFAULT_FEATURES):
            start = index * 6
            row: dict[str, Any] = {}
            for local, slot in zip(TEMPLATE_PERSON_ORDER, template[start:start + 6]):
                row[local] = {
                    "form": "-" + to_orthography(slot),
                    "phonemes": list(slot),
                    "source_label": "internal-ending-template",
                    "notes": "bootstrap ending; not a sourced full conjugation",
                }
            cells[feature] = row
        rows.append({
            "lect": lect,
            "lemma": "__template__",
            "class_source": "internal-template",
            "regularity": "template",
            "source": {"kind": "repository-template", "attested": False},
            "cells": cells,
        })
    return rows
