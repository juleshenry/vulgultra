"""Small, dependency-light regression fixtures for the shared objective."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from vulgultra.candidate_prep import build_candidates
from vulgultra.optimizer import Candidate, Genome, anneal, compute_energy, greedy_root_selections
from vulgultra.pipeline import candidates_to_export


def candidate(concept: str, lang: str, word: str, phones: list[str], syllables: int, evidence: str) -> Candidate:
    return Candidate(
        concept=concept,
        source_lang=lang,
        source_word=word,
        ipa=word,
        vulgultra_phonemes=phones,
        orthography=word,
        syllables=syllables,
        violations=0,
        evidence=evidence,
    )


class ObjectiveFixtures(unittest.TestCase):
    def test_preparation_keeps_only_shortest_legal_forms_and_evidence(self) -> None:
        concepts = {"water": {"es": [{"form": "corto", "evidence": "grid:p1"}, {"form": "largo", "evidence": "grid:p2"}]}}

        def fake_transcribe(word: str, _lang: str) -> tuple[str, list[str]]:
            return word, ["k", "a"] if word == "corto" else ["l", "a", "r", "ɡ", "o"]

        with patch("vulgultra.candidate_prep.transcribe_and_repair", side_effect=fake_transcribe):
            prepared = build_candidates(concepts)
        self.assertEqual([c.source_word for c in prepared["water"]], ["corto"])
        self.assertEqual(prepared["water"][0].evidence, "grid:p1")

    def test_inventory_term_rewards_distinct_root_segments(self) -> None:
        roots_a = {"one": [candidate("one", "es", "a", ["a"], 1, "a")]}
        roots_b = {"one": [candidate("one", "es", "ap", ["a", "p"], 1, "b")]}
        from vulgultra.optimizer import init_genome
        self.assertLess(compute_energy(init_genome(roots_b))[0], compute_energy(init_genome(roots_a))[0])

    def test_seeded_annealing_is_deterministic_and_export_is_auditable(self) -> None:
        roots = {
            "one": [
                candidate("one", "es", "a", ["a"], 1, "es:one"),
                candidate("one", "fr", "e", ["e"], 1, "fr:one"),
            ],
            "two": [candidate("two", "pt", "p", ["p", "a"], 1, "pt:two")],
        }
        left = anneal(roots, max_iterations=50, seed=9, progress_interval=0)
        right = anneal(roots, max_iterations=50, seed=9, progress_interval=0)
        self.assertEqual(left.genome.selections, right.genome.selections)
        export = candidates_to_export(roots)
        self.assertEqual(export["schema"], "vulgultra.candidates.v2")
        self.assertEqual(export["concepts"]["one"][0]["evidence"], "es:one")
        self.assertEqual(export["algorithm"]["morpheme_uniformity"], "not scored")


if __name__ == "__main__":
    unittest.main()
