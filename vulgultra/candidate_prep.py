"""Candidate preparation: G2P, repair, legality, and σ-shortlisting."""

from __future__ import annotations

from typing import Any

from vulgultra.g2p import transcribe_and_repair
from vulgultra.optimizer import Candidate
from vulgultra.phonology import (
    configure_inventory, count_syllables, count_violations, to_orthography,
)
from vulgultra.grid import form_records


def build_candidates(concepts: dict[str, dict[str, Any]]) -> dict[str, list[Candidate]]:
    """Build auditable candidates, then keep only each concept's shortest legal forms.

    The observed inventory is configured from the complete input grid before
    the shortlist is made. Selection itself never sees source spread or
    morpheme-uniformity scores.
    """
    prepared: list[tuple[str, str, dict[str, str], str, list[str]]] = []
    observed: set[str] = set()
    errors = 0
    for concept_id, lang_forms in concepts.items():
        meta = lang_forms.get("__meta__", {})
        pos = str(meta.get("pos") or "") if isinstance(meta, dict) else ""
        for lang, raw_forms in lang_forms.items():
            if lang == "__meta__":
                continue
            for record in form_records(raw_forms):
                try:
                    ipa, seq = transcribe_and_repair(record["form"], lang)
                    if seq:
                        prepared.append((concept_id, lang, record, ipa, seq))
                        observed.update(seq)
                except Exception:
                    errors += 1

    configure_inventory(observed)
    candidates: dict[str, list[Candidate]] = {}
    for concept_id, lang, record, ipa, seq in prepared:
        try:
            if not seq or count_violations(seq):
                continue
            candidate = Candidate(
                concept=concept_id,
                source_lang=lang,
                source_word=record["form"],
                ipa=ipa,
                vulgultra_phonemes=seq,
                orthography=to_orthography(seq),
                syllables=count_syllables(seq),
                violations=0,
                evidence=record.get("evidence", "grid"),
                relation=record.get("relation", "direct"),
                pos=pos,
            )
            candidates.setdefault(concept_id, []).append(candidate)
        except Exception:
            errors += 1

    for concept_id, values in list(candidates.items()):
        minimum = min(candidate.syllables for candidate in values)
        candidates[concept_id] = [candidate for candidate in values if candidate.syllables == minimum]
    if errors:
        print(f"  Warning: {errors} G2P errors skipped")
    return candidates
