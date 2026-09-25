"""Serialization boundary for Python↔Rust interchange and audit output."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from vulgultra.pipeline_constants import CANDIDATE_SCHEMA, CONCEPT_GRID_SCHEMA
from vulgultra.optimizer import SAResult
from vulgultra.phonology import extract_phonemes, to_orthography


def write_json(value: Any, path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def format_genome(result: SAResult) -> dict[str, Any]:
    """Serialize the Python reference optimizer's result for audit output."""
    genome = result.genome
    all_phonemes: set[str] = set()
    roots: dict[str, dict[str, Any]] = {}
    for concept in genome.selections:
        root = genome.get_root(concept)
        all_phonemes.update(extract_phonemes(root.vulgultra_phonemes))
        roots[concept] = {
            "ipa": root.vulgultra_phonemes,
            "orthography": root.orthography,
            "source_lang": root.source_lang,
            "source_word": root.source_word,
            "syllables": root.syllables,
            "violations": root.violations,
            "evidence": root.evidence,
            "relation": root.relation,
        }

    def table(values: dict[str, dict[str, list[str]]]) -> dict[str, dict[str, str]]:
        output: dict[str, dict[str, str]] = {}
        for class_id, cells in values.items():
            output[class_id] = {slot: to_orthography(seq) for slot, seq in cells.items()}
            for seq in cells.values():
                all_phonemes.update(extract_phonemes(seq))
        return output

    noun = table(genome.noun_endings)
    verb = table(genome.verb_endings)
    adj = {slot: to_orthography(seq) for slot, seq in genome.adj_endings.items()}
    for seq in genome.adj_endings.values():
        all_phonemes.update(extract_phonemes(seq))
    return {
        "version": "2.0",
        "metadata": {
            "total_concepts": len(roots),
            "total_energy": result.energy,
            "iterations": result.iterations,
            "acceptance_rate": round(result.acceptance_rate, 4),
        },
        "energy_breakdown": {key: round(value, 2) for key, value in result.breakdown.items()},
        "phoneme_inventory": sorted(all_phonemes),
        "phoneme_count": len(all_phonemes),
        "roots": roots,
        "noun_endings": noun,
        "verb_endings": verb,
        "adj_endings": adj,
    }


def write_concept_grid_document(rows: list[dict[str, Any]], path: str | Path, metadata: dict[str, Any]) -> None:
    """Write a full evidence-bearing grid before σ filtering."""
    write_json({"schema": CONCEPT_GRID_SCHEMA, "metadata": metadata, "concepts": rows}, path)


def candidate_document(concepts: dict[str, list[dict[str, Any]]], ending_catalog: dict[str, Any]) -> dict[str, Any]:
    """Create the stable Python-to-Rust envelope."""
    return {
        "schema": CANDIDATE_SCHEMA,
        "algorithm": {
            "stage_1": "legal minimum-syllable shortlist per concept",
            "stage_2": "maximize observed IPA segments in root ties",
            "source_spread": "audit-only",
            "morpheme_uniformity": "not scored",
        },
        "concepts": concepts,
        "ending_catalog": ending_catalog,
    }
