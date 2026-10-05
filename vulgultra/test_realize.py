"""Pins noun, adjective and sentence realization as it stands.

These record current behaviour, quirks included, so that a later rewrite of
the junction, number, case or gender logic shows up as a deliberate diff.
Verb forms are left unasserted: the verb table is being rebuilt by hand.
"""

from __future__ import annotations

import unittest

from vulgultra.morphology_constants import NOUN_SLOT_NAMES
from vulgultra.realize import (
    add_ending, article, copula, gender_of, inflect_adj, inflect_noun,
    realize_sentence,
)

# grammar.tex §3.1 table, in NOUN_SLOT_NAMES order.
ENDINGS = dict(zip(NOUN_SLOT_NAMES, [
    "o", "on", "is", "i", "os", "or",
    "a", "an", "es", "e", "as", "ar",
]))
CELLS = [(g, n, c) for g in "mf" for n in ("sg", "pl") for c in ("nom", "acc", "gen")]

ROOTS = {
    "cat": {"orthography": "gat", "source_lang": "ca"},
    "dog": {"orthography": "kan", "source_lang": "it"},
    "woman": {"orthography": "don", "source_lang": "it"},
    "water": {"orthography": "akw", "source_lang": "it"},
    "red": {"orthography": "roy", "source_lang": "an"},
    "cold": {"orthography": "fred", "source_lang": "ca"},
    "see": {"orthography": "ve", "source_lang": "ast"},
    "smile": {"orthography": "ri", "source_lang": "fr"},
    "i": {"orthography": "yo", "source_lang": "an"},
}
VERB_ENDINGS = {"prs_1sg": "o", "prs_3sg": "a"}


def realize(tokens: list[str], roots: dict[str, dict] = ROOTS) -> list[tuple[str, str]]:
    words = realize_sentence(tokens, roots, VERB_ENDINGS, ENDINGS, noun_endings=ENDINGS)
    return [(word["form"], word["role"]) for word in words]


class JunctionFixtures(unittest.TestCase):
    def test_consonant_final_stem_takes_the_ending_whole(self) -> None:
        self.assertEqual(add_ending("gat", "o"), "gato")
        self.assertEqual(add_ending("sol", "o"), "solo")
        self.assertEqual(add_ending("gat", ""), "gat")

    def test_vowel_final_stem_loses_its_vowel_when_a_nucleus_remains(self) -> None:
        self.assertEqual(add_ending("da", "am"), "dam")
        self.assertEqual(add_ending("kome", "a"), "koma")
        self.assertEqual(add_ending("dia", "o"), "dio")

    def test_vowel_final_stem_without_another_nucleus_keeps_its_vowel(self) -> None:
        self.assertEqual(add_ending("ve", "o"), "veo")
        self.assertEqual(add_ending("pe", "o"), "peo")
        self.assertEqual(add_ending("o", "a"), "oa")

    def test_glide_spelled_y_counts_as_a_consonant(self) -> None:
        self.assertEqual(add_ending("fryo", "a"), "fryoa")


class NominalFixtures(unittest.TestCase):
    def test_noun_reaches_all_twelve_cells(self) -> None:
        forms = [inflect_noun("gat", g, n, ENDINGS, case=c) for g, n, c in CELLS]
        self.assertEqual(forms, [
            "gato", "gaton", "gatis", "gati", "gatos", "gator",
            "gata", "gatan", "gates", "gate", "gatas", "gatar",
        ])

    def test_noun_without_a_table_falls_back_to_singular_endings(self) -> None:
        forms = [inflect_noun("gat", g, n, {}, case=c) for g, n, c in CELLS]
        self.assertEqual(forms, [
            "gato", "gaton", "gatis", "gato", "gaton", "gatis",
            "gata", "gatan", "gates", "gata", "gatan", "gates",
        ])

    def test_adjective_copies_the_noun_table(self) -> None:
        forms = [inflect_adj("bon", g, n, ENDINGS, case=c) for g, n, c in CELLS]
        self.assertEqual(forms, [
            "bono", "bonon", "bonis", "boni", "bonos", "bonor",
            "bona", "bonan", "bones", "bone", "bonas", "bonar",
        ])

    def test_adjective_without_a_table_ignores_case_and_number(self) -> None:
        self.assertEqual(inflect_adj("bon", "m", "pl", {}, case="acc"), "bono")
        self.assertEqual(inflect_adj("bon", "f", "sg", {}, case="gen"), "bona")

    def test_gender_is_a_hand_list_with_masculine_default(self) -> None:
        self.assertEqual(gender_of("cat_f"), "f")
        self.assertEqual(gender_of("water"), "f")
        self.assertEqual(gender_of("sun"), "m")
        self.assertEqual(gender_of("hand"), "m")
        self.assertEqual(gender_of("flower"), "m")

    def test_closed_forms(self) -> None:
        self.assertEqual([article(g, n) for g in "mf" for n in ("sg", "pl")], ["o", "os", "a", "as"])
        self.assertEqual(
            [copula(p) for p in ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")],
            ["so", "es", "e", "som", "sos", "son"],
        )
        self.assertEqual(copula("unknown"), "e")


class SentenceFixtures(unittest.TestCase):
    def test_article_and_adjective_agree_with_the_noun(self) -> None:
        self.assertEqual(
            realize(["def_art", "cat", "red", "smile"])[:3],
            [("o", "art"), ("gato", "noun"), ("royo", "adj")],
        )
        self.assertEqual(
            realize(["def_art", "water", "copula", "cold"]),
            [("a", "art"), ("akwa", "noun"), ("e", "cop"), ("freda", "adj")],
        )

    def test_noun_after_a_content_verb_is_accusative(self) -> None:
        words = realize(["def_art", "woman", "see", "def_art", "dog"])
        self.assertEqual(words[:2], [("a", "art"), ("dona", "noun")])
        self.assertEqual(words[2][1], "verb")
        self.assertEqual(words[3:], [("o", "art"), ("kanon", "noun")])

    def test_copula_follows_the_subject_pronoun(self) -> None:
        self.assertEqual(realize(["i", "copula", "cold"])[:2], [("yo", "pron"), ("so", "cop")])

    def test_missing_root_is_inflected_from_its_concept_id(self) -> None:
        self.assertEqual(realize(["def_art", "cat_f"]), [("a", "art"), ("cat_fa", "noun")])

    def test_root_part_of_speech_overrides_the_grid(self) -> None:
        roots = {**ROOTS, "cat": {**ROOTS["cat"], "pos": "verb"}}
        self.assertEqual(realize(["def_art", "cat"], roots)[0][1], "verb")


if __name__ == "__main__":
    unittest.main()
