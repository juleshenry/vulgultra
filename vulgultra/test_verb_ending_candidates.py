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

    def test_sigma_is_source_phonology(self) -> None:
        cases = [
            ("∅", "ro", 0), ("o", "es", 1), ("amos", "es", 2), ("iamo", "it", 2),
            ("áis", "es", 1), ("eu", "ca", 1), ("ía", "es", 2),
            ("ent", "fr", 0), ("es", "fr", 0), ("es", "es", 1), ("aient", "fr", 1),
            ("ați", "ro", 1), ("i", "ro", 0), ("ează", "ro", 2), ("au̯", "ruq", 1),
            ("éis", "es", 1), ("ia", "pt", 2), ("aria", "ca", 3), ("ien", "ca", 2),
            ("aia", "sc", 2), ("arão", "pt", 2), ("ões", "pt", 1), ("aróo", "lmo", 2),
            ("ē", "eml", 1), ("ii", "it", 2), ("ii", "ro", 1), ("oais", "pcd", 1),
            ("ˈeses", "oc", 2), ("iamo", "it", 2),
        ]
        for ending, lect, sigma in cases:
            self.assertEqual(vec.ending_sigma(ending, lect), sigma, (ending, lect))
    def test_whole_words_keep_their_only_vowel(self) -> None:
        self.assertEqual(vec.ending_sigma("es", "fr", word=True), 1)
        self.assertEqual(vec.ending_sigma("sommes", "fr", word=True), 1)
        self.assertEqual(vec.ending_sigma("es", "fr"), 0)

    def test_named_verbs_cover_the_copula(self) -> None:
        self.assertEqual(vec.NAMED_VERBS["esse"]["es"], ("ser",))
        self.assertIn("fr", vec.NAMED_VERBS["habere"])


if __name__ == "__main__":
    unittest.main()
