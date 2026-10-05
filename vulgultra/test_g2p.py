"""The transcription boundary: leftover readings and named rejections."""

from __future__ import annotations

import shutil
import unicodedata
import unittest
from unittest.mock import patch

from vulgultra.g2p import UntranscribedError, transcribe_and_repair
from vulgultra.phonology import (
    configure_inventory, count_syllables, count_violations, espeak_reading, read_leftovers,
    unknown_segments, word_to_ipa,
)


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
        self.assertEqual(read_leftovers("ʒerunklʒu", "ruo"), "jerunkʎu")

    def test_a_reading_is_not_read_again_as_a_leftover(self) -> None:
        # Croatian-based Istro-Romanian: ž is ʒ, and the ʒ the backend made of j is the glide.
        self.assertEqual(read_leftovers("žut", "ruo"), "ʒut")
        self.assertEqual(read_leftovers("noʒ", "ruo"), "noj")
        self.assertEqual(read_leftovers("kurd͡ʒe", "ruo"), nfd("kurd͡ʒe"))

    def test_form_in_the_backends_own_spelling_keeps_its_reading_of_j(self) -> None:
        with patch("vulgultra.phonology._get_g2p") as backend:
            backend.return_value.transliterate.return_value = "ɨnʒunɡia"
            self.assertEqual(word_to_ipa("înjunghia", "ruo"), "ɨnʒunɡia")
            backend.return_value.transliterate.return_value = "noʒ"
            self.assertEqual(word_to_ipa("noj", "ruo"), "noj")
            backend.return_value.transliterate.return_value = nfd("unɡľə")
            self.assertEqual(word_to_ipa("ungľă", "ruo"), "unɡʎə")

    def test_a_letter_can_take_the_value_another_letter_had(self) -> None:
        # Piedmontese: o is /u/ and u is /y/, read in one pass.
        self.assertEqual(read_leftovers("tut", "pms"), "tyt")
        self.assertEqual(read_leftovers("mond", "pms"), "mund")
        self.assertEqual(read_leftovers("feu", "pms"), "fø")

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

    def test_reverse_vulgar_latin_merges_apply_in_every_lect(self) -> None:
        with patch("vulgultra.g2p.word_to_ipa", return_value="ʎuɲ"):
            self.assertEqual(transcribe_and_repair("lluny", "ca")[1], ["l", "j", "u", "n", "j"])
        with patch("vulgultra.g2p.word_to_ipa", return_value="ʝo"):
            self.assertEqual(transcribe_and_repair("yo", "es")[1], ["j", "o"])

    def test_variant_is_merged_only_in_the_lects_where_it_is_one(self) -> None:
        with patch("vulgultra.g2p.word_to_ipa", return_value="luɐ"):
            self.assertEqual(transcribe_and_repair("lua", "pt")[1], ["l", "w", "a"])
        with patch("vulgultra.g2p.word_to_ipa", return_value="krɐp"):
            self.assertEqual(transcribe_and_repair("crëp", "lld")[1], ["k", "r", "ɐ", "p"])

    def test_rhotics_are_all_kept(self) -> None:
        for lang, ipa in (("es", "kaɾo"), ("es", "karo"), ("fr", "paʀ"), ("pt", "ʁato")):
            with patch("vulgultra.g2p.word_to_ipa", return_value=ipa):
                self.assertEqual("".join(transcribe_and_repair("x", lang)[1]), ipa)

    def test_every_rhotic_is_a_liquid_in_an_onset(self) -> None:
        for lang, ipa in (("fr", "tʀɛ"), ("fr", "ɡʀɑ̃d"), ("es", "tɾes"), ("it", "tre"), ("pt", "pʁa")):
            with patch("vulgultra.g2p.word_to_ipa", return_value=ipa):
                seq = transcribe_and_repair("x", lang)[1]
            configure_inventory(set(seq))
            self.assertEqual((count_syllables(seq), count_violations(seq)), (1, 0), ipa)

    def test_one_sound_the_backend_reads_as_two(self) -> None:
        self.assertEqual(read_leftovers("dʒɑ̃b", "wa"), "d͡ʒɑ̃b")       # djambe
        self.assertEqual(read_leftovers("dao", "gallo"), "daw")
        self.assertEqual(read_leftovers("soare", "ro"), "sware")
        self.assertEqual(read_leftovers("dao", "fr"), "dao")            # only where it is one sound

    def test_a_lects_own_spellings_are_read_before_the_backend(self) -> None:
        for lang, word, pos, ipa in (
            ("rm", "tgi", "", "t͡ɕi"), ("rm", "chaun", "", "t͡ɕaun"), ("rm", "sulegl", "", "suleʎ"),
            ("rm", "glina", "", "ʎina"), ("rm", "star", "", "ʃtar"), ("rm", "culiez", "", "kuliet͡s"),
            ("lld", "scorza", "", "ʃkort͡sa"), ("fur", "cjan", "", "can"), ("fur", "zâl", "", "d͡ʒal"),
            ("eml", "żâl", "", "ðal"), ("eml", "zénc", "", "θenk"), ("scn", "panza", "", "pant͡sa"),
            ("pms", "giàun", "", "d͡ʒawn"), ("ast", "xelu", "", "ʃelu"), ("ast", "llombu", "", "ʎombu"),
            ("ast", "cabeza", "", "kabeθa"), ("ext", "humu", "", "humu"), ("lad", "mujer", "", "muʒeɾ"),
            ("lad", "kozer", "", "kozeɾ"), ("oc", "quatre", "", "katɾe"), ("nrf", "méthe", "", "með"),
            ("frp", "dent", "", "dɛ̃"), ("frp", "fuè", "", "fwɛ"), ("frp", "chantar", "verb", "ʃɑ̃ta"),
        ):
            with self.subTest(word=word):
                self.assertEqual(unicodedata.normalize("NFC", word_to_ipa(word, lang, pos)), ipa)

    def test_a_borrowed_maps_faults_are_mended(self) -> None:
        for lang, word, ipa in (
            ("fur", "bosc", "bosk"), ("sc", "girare", "d͡ʒiraɾɛ"), ("ast", "gusanu", "ɡusanu"),
            ("frp", "grant", "ɡʀɑ̃"), ("frp", "racena", "ʀasəna"), ("nrf", "mangi", "mɑ̃ʒi"),
            ("nrf", "crendre", "kʀɑ̃dʀ"), ("gallo", "faille", "faj"), ("gallo", "cinqe", "sɛ̃k"),
        ):
            with self.subTest(word=word):
                self.assertEqual(unicodedata.normalize("NFC", word_to_ipa(word, lang)), ipa)

    def test_romanian_final_i_is_a_syllable_only_in_an_infinitive(self) -> None:
        for word, pos, ipa in (("ochi", "noun", "okʲ"), ("cinci", "num", "t͡ʃint͡ʃ"), ("mulți", "det", "mult͡sʲ"),
                               ("muri", "verb", "muri"), ("zi", "noun", "zi")):
            with self.subTest(word=word):
                self.assertEqual(unicodedata.normalize("NFC", word_to_ipa(word, "ro", pos)), ipa)
        self.assertEqual(count_syllables(transcribe_and_repair("genunchi", "ro", "noun")[1]), 2)

    def test_walloon_is_read_by_its_own_rules(self) -> None:
        for word, pos, ipa in (
            ("oujhea", "", "uʒja"), ("tchén", "", "t͡ʃẽ"), ("pexhon", "", "pɛʃɔ̃"), ("lådje", "", "lɔt͡ʃ"),
            ("viker", "verb", "vike"), ("mer", "", "mɛʀ"), ("cwand", "", "kwɑ̃"), ("sonk", "", "sɔ̃k"),
            ("anêye", "", "anɛj"), ("montinne", "", "mɔ̃tɛ̃n"), ("pô", "", "põ"), ("ome", "", "ɔm"),
        ):
            with self.subTest(word=word):
                self.assertEqual(unicodedata.normalize("NFC", word_to_ipa(word, "wa", pos)), ipa)

    @unittest.skipUnless(shutil.which("espeak-ng"), "espeak-ng is not installed")
    def test_second_reader(self) -> None:
        for lang, word, ipa in (
            ("fr", "femme", "fam"), ("fr", "grand", "ɡʀɑ̃"), ("fr", "manger", "mɑ̃ʒe"), ("fr", "nuit", "nɥi"),
            ("pt", "chuva", "ʃuvɐ"), ("pt", "olho", "ɔʎu"), ("pt", "mão", "mɐ̃w̃"), ("pt", "perna", "pɛɾnɐ"),
            ("pcd", "grain.ne", "ɡʀɛ̃n"), ("pcd", "troés", "tʀwe"), ("pcd", "tchien", "t͡ʃjɛ̃"),
            ("mwl", "chuba", "t͡ʃubɐ"), ("mwl", "lhago", "ʎaɡu"), ("pt", "estrela", "ɨʃtɾelɐ"),
            ("es", "cabeza", "kabeθa"), ("es", "lluvia", "ʎubja"), ("es", "hígado", "iɡado"),
            ("ca", "peix", "peʃ"), ("ca", "beure", "bɛwɾə"), ("ca", "aigua", "ajɡwə"),
            ("it", "pesce", "peʃe"), ("it", "cuore", "kuɔre"), ("an", "xordo", "ʃoɾdo"),
        ):
            with self.subTest(word=word):
                self.assertEqual(unicodedata.normalize("NFC", word_to_ipa(word, lang)), ipa)

    def test_without_the_second_reader_the_backend_reads(self) -> None:
        with patch("vulgultra.phonology._espeak", return_value=None):
            espeak_reading.cache_clear()
            try:
                self.assertEqual(word_to_ipa("père", "fr"), "pɛʀ")
            finally:
                espeak_reading.cache_clear()

    def test_clean_form_passes(self) -> None:
        with patch("vulgultra.g2p.word_to_ipa", return_value="pɛʀ"):
            self.assertEqual(transcribe_and_repair("père", "fr"), ("pɛʀ", ["p", "ɛ", "ʀ"]))


if __name__ == "__main__":
    unittest.main()
