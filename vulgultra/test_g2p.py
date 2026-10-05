"""The transcription boundary: leftover readings and named rejections."""

from __future__ import annotations

import unicodedata
import unittest
from unittest.mock import patch

from vulgultra.g2p import UntranscribedError, transcribe_and_repair
from vulgultra.phonology import read_leftovers, unknown_segments


def nfd(text: str) -> str:
    return unicodedata.normalize("NFD", text)


class LeftoverFixtures(unittest.TestCase):
    def test_base_letter_and_its_leftover_diacritic_are_read_together(self) -> None:
        self.assertEqual(read_leftovers("pə̀ʀ", "fr"), "pɛʀ")
        self.assertEqual(read_leftovers("fɔʀə̂", "fr"), "fɔʀɛ")
        self.assertEqual(read_leftovers("feǩor", "ruo"), nfd("fet͡ʃor"))

    def test_a_reading_belongs_to_one_lect(self) -> None:
        self.assertEqual(read_leftovers("ɡlaķ", "fur"), nfd("ɡlat͡ʃ"))
        self.assertEqual(read_leftovers("ʎaŋķaɾ", "ca"), "ʎaŋsaɾ")
        self.assertEqual(read_leftovers("ɡlaķ", "it"), nfd("ɡlaķ"))

    def test_digraph_read_letter_by_letter_becomes_one_segment(self) -> None:
        self.assertEqual(read_leftovers("tsintsi", "rup"), nfd("t͡sint͡si"))
        self.assertEqual(read_leftovers("mulʒari", "ruq"), "muʎari")
        self.assertEqual(read_leftovers("žerunklʒu", "ruo"), "ʒerunkʎu")

    def test_backend_typos_are_fixed_for_every_lect(self) -> None:
        self.assertEqual(read_leftovers("ajga", "oc"), "ajɡa")
        self.assertEqual(read_leftovers("antʃ͡ʊ", "gl"), nfd("ant͡ʃʊ"))

    def test_stray_diacritic_is_reported_with_its_letter(self) -> None:
        self.assertEqual(unknown_segments(["p", "a", "s"]), [])
        self.assertEqual(unknown_segments(["k", "u", "s", "\u0323", "i", "r"]), [nfd("ṣ")])
        self.assertEqual(unknown_segments(["p", "'", "t", "i"]), ["'"])


class BoundaryFixtures(unittest.TestCase):
    def test_form_with_an_unread_letter_is_rejected_by_name(self) -> None:
        with patch("vulgultra.g2p.word_to_ipa", return_value="kuṣir"):
            with self.assertRaises(UntranscribedError) as raised:
                transcribe_and_repair("cuṣìr", "eml")
        self.assertEqual((raised.exception.lang, raised.exception.word), ("eml", "cuṣìr"))
        self.assertEqual(raised.exception.leftovers, [nfd("ṣ")])

    def test_clean_form_passes(self) -> None:
        with patch("vulgultra.g2p.word_to_ipa", return_value="pɛʀ"):
            self.assertEqual(transcribe_and_repair("père", "fr"), ("pɛʀ", ["p", "ɛ", "ʀ"]))


if __name__ == "__main__":
    unittest.main()
