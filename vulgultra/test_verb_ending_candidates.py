"""Tests for theme assignment, TAM mapping and σ in the verb shortlist."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "verb_ending_candidates",
    ROOT / "scripts" / "verb_ending_candidates.py",
)
assert SPEC and SPEC.loader
vec = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(vec)


class VerbEndingCandidateTests(unittest.TestCase):
    def test_latin_are_classes_are_a_theme(self) -> None:
        self.assertEqual(vec.theme_of("es", "-ar"), "a")
        self.assertEqual(vec.theme_of("fr", "-er"), "a")
        self.assertEqual(vec.theme_of("pms", "-é"), "a")
        self.assertEqual(vec.theme_of("lld", "-er"), "a")
        self.assertEqual(vec.theme_of("eml", "-ēr"), "a")

    def test_other_themes(self) -> None:
        self.assertEqual(vec.theme_of("es", "-er"), "e")
        self.assertEqual(vec.theme_of("ro", "-ea"), "e")
        self.assertEqual(vec.theme_of("ro", "-e"), "re")
        self.assertEqual(vec.theme_of("fr", "-re"), "re")
        self.assertEqual(vec.theme_of("it", "-ire"), "i")
        self.assertEqual(vec.theme_of("ruq", "IV-esc"), "i")

    def test_irregular_classes_have_no_theme(self) -> None:
        self.assertIsNone(vec.theme_of("es", "ser"))
        self.assertIsNone(vec.theme_of("fr", "other"))
        self.assertIsNone(vec.theme_of("rup", "unknown"))

    def test_tam_aliases(self) -> None:
        self.assertEqual(vec.canonical_tam("conditional.present"), "conditional")
        self.assertEqual(vec.canonical_tam("subjunctive.preterite"), "subjunctive.imperfect")
        self.assertEqual(vec.canonical_tam("indicative.present"), "indicative.present")
        self.assertIsNone(vec.canonical_tam("indicative"))

    def test_sigma_keeps_two_syllables_and_forms_glides(self) -> None:
        self.assertEqual(vec.ending_sigma("∅"), 0)
        self.assertEqual(vec.ending_sigma("o"), 1)
        self.assertEqual(vec.ending_sigma("amos"), 2)
        self.assertEqual(vec.ending_sigma("iamo"), 2)
        # Read as Vulgultra spelling, not Romanian: final i is a vowel.
        self.assertEqual(vec.ending_sigma("ați"), 2)


if __name__ == "__main__":
    unittest.main()
