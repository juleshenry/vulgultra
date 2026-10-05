"""The post-optimizer join that puts grid fields on selected roots."""

from __future__ import annotations

import unittest

from vulgultra.lexicon_fields import annotate_lexicon

GRID = {"concepts": [
    {"id": "water", "gloss_en": "water", "pos": "noun", "forms": {}},
    {"id": "you_sg", "gloss_en": "you sg", "pos": "pron", "forms": {}},
]}


class LexiconFieldFixtures(unittest.TestCase):
    def test_grid_fields_replace_whatever_the_optimizer_wrote(self) -> None:
        lexicon = {
            "version": "2.0.0",
            "roots": {
                "water": {"orthography": "o", "source_lang": "fr", "pos": "verb"},
                "you_sg": {"orthography": "tu", "source_lang": "an"},
            },
        }
        joined = annotate_lexicon(lexicon, GRID)
        self.assertEqual(joined["roots"]["water"], {
            "orthography": "o", "source_lang": "fr", "pos": "noun", "gloss_en": "water",
        })
        self.assertEqual(joined["roots"]["you_sg"]["gloss_en"], "you sg")
        self.assertEqual(joined["version"], "2.0.0")
        self.assertEqual(lexicon["roots"]["water"]["pos"], "verb")

    def test_root_missing_from_the_grid_is_an_error(self) -> None:
        with self.assertRaises(KeyError):
            annotate_lexicon({"roots": {"moon": {"orthography": "lun"}}}, GRID)


if __name__ == "__main__":
    unittest.main()
