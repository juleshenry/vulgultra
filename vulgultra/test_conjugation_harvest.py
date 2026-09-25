"""Tests for Kaikki conjugation harvest and 6-slot ending extraction."""

import unittest

from vulgultra.conjugation_harvest import (
    aggregate_ending_inventory,
    decode_tags,
    primary_conj_template,
    select_representatives,
    strip_endings,
)


class ConjugationHarvestTests(unittest.TestCase):
    def test_conditional_is_not_folded_into_bare_indicative(self) -> None:
        slot, feature, ambiguous = decode_tags([
            "conditional", "first-person", "indicative", "singular",
        ])
        self.assertEqual(slot, "1sg")
        self.assertEqual(feature, "conditional")
        self.assertFalse(ambiguous)

    def test_present_indicative_feature(self) -> None:
        slot, feature, _ambiguous = decode_tags([
            "first-person", "indicative", "present", "singular",
        ])
        self.assertEqual(slot, "1sg")
        self.assertEqual(feature, "indicative.present")

    def test_primary_conj_template_prefers_specific_name(self) -> None:
        class_source, stem = primary_conj_template([
            {"name": "ast-conj-table", "args": {"infinitive": "abater"}},
            {"name": "ast-conj-er", "args": {"1": "abat"}},
        ])
        self.assertEqual(class_source, "ast-conj-er")
        self.assertEqual(stem, "abat")

    def test_strip_endings_with_template_stem(self) -> None:
        forms = {
            "1sg": "abato", "2sg": "abates", "3sg": "abate",
            "1pl": "abatemos", "2pl": "abatéis", "3pl": "abaten",
        }
        result = strip_endings(forms, stem="abat")
        self.assertIsNotNone(result)
        endings, used, mode = result  # type: ignore[misc]
        self.assertEqual(used, "abat")
        self.assertEqual(mode, "template")
        self.assertEqual(endings["1sg"], "o")
        self.assertEqual(endings["2sg"], "es")
        self.assertEqual(endings["1pl"], "emos")

    def test_strip_endings_lcp_fallback(self) -> None:
        forms = {
            "1sg": "bebo", "2sg": "bebes", "3sg": "bebe",
            "1pl": "bebemos", "2pl": "bebéis", "3pl": "beben",
        }
        result = strip_endings(forms, stem=None)
        self.assertIsNotNone(result)
        endings, used, mode = result  # type: ignore[misc]
        self.assertEqual(used, "beb")
        self.assertEqual(mode, "lcp")
        self.assertEqual(endings["3sg"], "e")

    def test_select_representatives_keeps_named_irregular(self) -> None:
        lemmas = {
            "comer": {"features": {"indicative.present": {
                "1sg": [{"form": "como"}], "2sg": [{"form": "comes"}],
                "3sg": [{"form": "come"}], "1pl": [{"form": "comemos"}],
                "2pl": [{"form": "comeis"}], "3pl": [{"form": "comen"}],
            }}},
            "ser": {"features": {"indicative.present": {
                "1sg": [{"form": "so"}], "2sg": [{"form": "yes"}],
                "3sg": [{"form": "ye"}], "1pl": [{"form": "somos"}],
                "2pl": [{"form": "sois"}], "3pl": [{"form": "son"}],
            }}},
        }
        chosen = select_representatives(
            lemmas, class_source="ast-conj-ser", limit=2,
        )
        self.assertEqual(chosen[0], "ser")

    def test_aggregate_ending_inventory_majority(self) -> None:
        def lemma(stem: str, endings: tuple[str, ...]) -> dict:
            slots = ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")
            cells = {
                slot: [{"form": stem + ending}]
                for slot, ending in zip(slots, endings)
            }
            return {"stem": stem, "features": {"indicative.present": cells}}

        lemmas = {
            f"v{i}": lemma("stem", ("o", "es", "e", "emos", "éis", "en"))
            for i in range(5)
        }
        inventory = aggregate_ending_inventory(lemmas)
        present = inventory["indicative.present"]
        self.assertEqual(present["support"], 5)
        self.assertEqual(present["endings"]["1sg"], "o")
        self.assertEqual(present["endings"]["2pl"], "éis")


if __name__ == "__main__":
    unittest.main()
