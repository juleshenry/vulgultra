"""Tests for Verbix Aragonese parsing."""

import unittest

from vulgultra.verbix_an import class_from_infinitive, parse_paradigm


class VerbixAnTests(unittest.TestCase):
    def test_class_from_infinitive(self) -> None:
        self.assertEqual(class_from_infinitive("trobar"), "-ar")
        self.assertEqual(class_from_infinitive("beber"), "-er")
        self.assertEqual(class_from_infinitive("partir"), "-ir")
        self.assertEqual(class_from_infinitive("estar"), "estar")

    def test_normalize_collapses_provider_labels(self) -> None:
        from vulgultra.verbix_an import normalize_an_class
        self.assertEqual(normalize_an_class("abanzar", "verbix-an-ar"), "-ar")
        self.assertEqual(normalize_an_class("abaratar", "an-conj"), "-ar")
        self.assertEqual(normalize_an_class("crompar", "an-conj-ar"), "-ar")
        self.assertEqual(normalize_an_class("haber", "an-conj-haber"), "haber")

    def test_parse_paradigm_maps_six_slots_including_2pl(self) -> None:
        record = {
            "lemma": "trobar",
            "page_url": "https://www.verbix.com/webverbix/go.php?D1=52&T1=trobar",
            "raw": {
                "exists": True,
                "tenses": {
                    "0": {
                        "name": "Indicative Present",
                        "forms": [
                            {"id": 1, "form": "trobo"},
                            {"id": 2, "form": "trobas"},
                            {"id": 3, "form": "troba"},
                            {"id": 4, "form": "trobamos"},
                            {"id": 5, "form": "trobatz"},
                            {"id": 6, "form": "troban"},
                        ],
                    }
                },
            },
        }
        paradigm = parse_paradigm(record)
        self.assertIsNotNone(paradigm)
        assert paradigm is not None
        present = paradigm["cells"]["indicative.present"]
        self.assertEqual(present["2pl"]["form"], "trobatz")
        self.assertTrue(paradigm["source"]["attested"])


if __name__ == "__main__":
    unittest.main()
