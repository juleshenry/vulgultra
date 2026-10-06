"""Tests for the readers and the aligner behind the Bible-vocabulary coverage count."""

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

tables = importlib.import_module("extract_wikt_translations")
native = importlib.import_module("extract_native_wiktionaries")
align = importlib.import_module("align_bible")
coverage = importlib.import_module("bible_coverage")


class TranslationTableTests(unittest.TestCase):
    def test_a_template_names_its_form_first(self) -> None:
        self.assertEqual(tables.forms_of("aiga|f|dif=aigo"), [("", "aiga")])

    def test_the_spanish_edition_numbers_forms_and_senses(self) -> None:
        self.assertEqual(tables.forms_of("a1=1|t1=bocje|a2=2|t2=bočhe"), [("1", "bocje"), ("2", "bočhe")])
        # One sense number for several forms serves them all.
        self.assertEqual(tables.forms_of("a1=1|a2=1|g1=f|t1=sierade|t2=autun"), [("1", "sierade"), ("1", "autun")])

    def test_markup_and_empty_forms_are_dropped(self) -> None:
        self.assertEqual(tables.clean("''aghe''."), "aghe")
        self.assertEqual(tables.clean("[[aghe]]"), "")
        self.assertEqual(tables.clean(" "), "")


class NativeWiktionaryTests(unittest.TestCase):
    def test_a_section_template_is_not_a_language(self) -> None:
        self.assertTrue(native.is_language("co", "scn"))
        self.assertTrue(native.is_language("roa-rup", "roa-rup"))
        self.assertFalse(native.is_language("noun", "scn"))
        self.assertFalse(native.is_language("trans", "scn"))

    def test_latin_is_read_without_its_marks(self) -> None:
        self.assertEqual(native.plain_latin("''càsa''."), "casa")
        self.assertEqual(native.plain_latin("*Aquā"), "aqua")


class AlignerTests(unittest.TestCase):
    def test_words_that_keep_company_are_linked(self) -> None:
        # Three "verses": source 0 always stands with target 0, source 1 with target 1, source 2 with target 2.
        pairs = [([0, 1], [0, 1]), ([0, 2], [2, 0]), ([1, 2], [1, 2]), ([0], [0]), ([1], [1])]
        links = align.Aligner(pairs, 3, 3).links()
        self.assertEqual({pair for pair, n in links.items() if n >= 2}, {(0, 0), (1, 1), (2, 2)})

    def test_resemblance_is_about_shared_letters(self) -> None:
        self.assertEqual(align.resemblance(align.shape("pan"), align.shape("pan")), 1.0)
        self.assertGreater(align.resemblance(align.shape("peccato"), align.shape("pecà")), 0.5)
        self.assertLess(align.resemblance(align.shape("aqua"), align.shape("pan")), 0.2)
        # Accents do not count.
        self.assertEqual(align.resemblance(align.shape("pão"), align.shape("pao")), 1.0)

    def test_text_is_split_at_apostrophes_and_hyphens(self) -> None:
        self.assertEqual(align.tokens("L’aghe dit-il"), ["l", "aghe", "dit", "il"])

    def test_the_romanian_cedilla_is_read_as_the_comma(self) -> None:
        self.assertEqual(align.tokens("şi ţara"), ["și", "țara"])

    def test_psalms_take_the_vulgates_numbers(self) -> None:
        # The Vulgate's Psalm 22 is the Hebrew 23rd, and counts the title as verse 1.
        latin = {("PSA", "22", str(verse)): "x" for verse in (1, 2, 3)} | {("GEN", "1", "1"): "x"}
        other = {("PSA", "23", "1"): "first", ("PSA", "23", "2"): "second", ("GEN", "1", "1"): "beginning"}
        renumbered = align.psalms_renumbered(latin, other)
        self.assertEqual(renumbered[("PSA", "22", "2")], "first")
        self.assertEqual(renumbered[("PSA", "22", "3")], "second")
        self.assertEqual(renumbered[("GEN", "1", "1")], "beginning")
        self.assertNotIn(("PSA", "23", "1"), renumbered)


class WitnessTests(unittest.TestCase):
    def test_an_edition_is_one_witness_however_it_gives_the_form(self) -> None:
        self.assertEqual(coverage.witnesses({"translation:fr.wiktionary", "gloss:fr:table"}), 1)
        self.assertEqual(coverage.witnesses({"gloss:fr:fr.wiktionary", "gloss:it:Apertium"}), 2)

    def test_a_bridge_is_no_witness(self) -> None:
        self.assertEqual(coverage.witnesses({"bridge:fr:fr.wiktionary", "bridge:it:table"}), 0)

    def test_an_imported_table_is_the_english_one(self) -> None:
        self.assertEqual(coverage.witnesses({"translation:zh.wiktionary", "translation:en.wiktionary"}), 1)
        self.assertEqual(coverage.witnesses({"gloss:ku:ku.wiktionary", "gloss:en:en.wiktionary"}), 1)

    def test_parts_of_speech_must_agree_where_both_are_known(self) -> None:
        verb, noun, numeral = (coverage.word_class(pos) for pos in ("verb", "noun", "num"))
        self.assertFalse(coverage.agree(verb, noun))
        self.assertFalse(coverage.agree(noun, numeral))
        self.assertTrue(coverage.agree(coverage.word_class("adj"), noun))
        self.assertTrue(coverage.agree(coverage.word_class("adj"), numeral))
        self.assertTrue(coverage.agree(coverage.word_class(""), verb))
        self.assertTrue(coverage.agree(coverage.word_class(["noun", "verb"]), verb))

    def test_a_gloss_loses_its_article(self) -> None:
        self.assertEqual(coverage.parts("la casa, il cane", "it"), {"casa", "cane"})
        self.assertEqual(coverage.parts("das Haus", "de"), {"haus"})

    def test_old_romanian_spelling_is_read_as_todays(self) -> None:
        self.assertEqual(coverage.parts("a apucà; şarpe", "ro"), {"apuca", "șarpe"})

    def test_a_work_is_one_source_whatever_its_tables(self) -> None:
        self.assertEqual(coverage.glossary_source("lespy-raymond-1887-bearnais-old", "fr"), "lespy-raymond-1887")
        self.assertEqual(coverage.glossary_source("videsott-2020-vll1.badia", "de"), "videsott-2020")
        self.assertEqual(coverage.glossary_source("apertium-oci-fra-gascon", "fr"), "apertium-oci-fra")
        self.assertEqual(coverage.glossary_source("wiktionary-kaikki", "pl"), "pl.wiktionary")

    def test_a_scan_is_a_witness_but_a_bridge_is_not(self) -> None:
        self.assertEqual(coverage.witnesses({"scan:text"}), 1)
        self.assertEqual(coverage.witnesses({"scan:it:ferrari-1835 (scan)", "gloss:en:en.wiktionary"}), 2)


if __name__ == "__main__":
    unittest.main()
