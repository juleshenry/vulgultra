"""Tests for stem bucketing in the ending-candidate report."""

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
    def test_surface_stem_keeps_rgn_first_class(self) -> None:
        self.assertEqual(vec.surface_stem("rgn-conj-first"), "rgn-conj-first")
        self.assertEqual(vec.surface_stem("rgn-conj-avér"), "avér")
        self.assertEqual(vec.surface_stem("lad-conj-ar"), "-ar")

    def test_new_harvest_stems_are_analyzed(self) -> None:
        self.assertEqual(vec.bucket_of("-al"), "a-theme")
        self.assertEqual(vec.bucket_of("-el"), "e-theme")
        self.assertEqual(vec.bucket_of("-ur"), "a-theme")
        self.assertEqual(vec.bucket_of("-ro"), "re")
        self.assertEqual(vec.bucket_of("-tcher"), "e-theme")
        self.assertEqual(vec.bucket_of("rgn-conj-first"), "a-theme")
        self.assertEqual(vec.bucket_of("ête"), "esse")
        self.assertEqual(vec.bucket_of("avì"), "habere")
        self.assertEqual(vec.bucket_of("saite"), "esse")
        self.assertEqual(vec.bucket_of("étr"), "esse")
        self.assertEqual(vec.bucket_of("avair"), "habere")


if __name__ == "__main__":
    unittest.main()
