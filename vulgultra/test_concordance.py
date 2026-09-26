"""Concordance tie-break: shared person coda across tenses among equal σ."""

from __future__ import annotations

import unittest

from vulgultra.optimizer import (
    PERSON_CELL_NAMES,
    _cell_score,
    _common_suffix_len,
    assemble_verb_rows,
)
from vulgultra.phonology import from_orthography


def _phones(ortho: str) -> list[str]:
    return from_orthography(ortho)


class ConcordanceTests(unittest.TestCase):
    def test_common_suffix_ons_erons(self) -> None:
        self.assertEqual(
            _common_suffix_len(_phones("ons"), _phones("erons")),
            3,
        )
        # Trailing /s/ alone is a weaker match than full /ons/.
        self.assertEqual(
            _common_suffix_len(_phones("ons"), _phones("amos")),
            1,
        )
        self.assertGreater(
            _common_suffix_len(_phones("ons"), _phones("erons")),
            _common_suffix_len(_phones("ons"), _phones("amos")),
        )

    def test_cell_score_prefers_concordant_tie(self) -> None:
        anchors = [_phones("ons")]
        empty_row: list[list[str]] = []
        phonemes: set[str] = set()
        erons = _cell_score(
            _phones("erons"),
            row_so_far=empty_row,
            anchors=anchors,
            phonemes=phonemes,
            lang="fr",
        )
        amos = _cell_score(
            _phones("amos"),
            row_so_far=empty_row,
            anchors=anchors,
            phonemes=phonemes,
            lang="es",
        )
        # Same syllable count; concordance tips toward erons.
        self.assertEqual(erons[0], amos[0])
        self.assertLess(erons, amos)

    def test_shorter_beats_concordance(self) -> None:
        anchors = [_phones("ons")]
        short = _cell_score(
            _phones("a"),
            row_so_far=[],
            anchors=anchors,
            phonemes=set(),
            lang="es",
        )
        long_concordant = _cell_score(
            _phones("erons"),
            row_so_far=[],
            anchors=anchors,
            phonemes=set(),
            lang="fr",
        )
        self.assertLess(short[0], long_concordant[0])
        self.assertLess(short, long_concordant)

    def test_assemble_picks_concordant_future_1pl(self) -> None:
        """Present 1pl /ons/ tips a tied 2σ future toward /erons/."""
        # Minimal 41-cell blocks: only 1pl (index 1) and future 1pl (index 7)
        # matter. Other cells are distinct filler so row collisions stay zero.
        fillers_a = ["o", "ons", "as", "ez", "e", "ent"]
        fillers_b = ["o", "mos", "as", "ais", "a", "an"]
        # past / subj / themes: keep 1σ distinct junk per lect
        past_a = ["i", "es", "is", "iez", "it", "irent"]
        past_b = ["i", "imos", "iste", "isteis", "io", "ieron"]
        fut_a = ["re", "erons", "ras", "rez", "ra", "ront"]
        fut_b = ["re", "amos", "ras", "reis", "ra", "ran"]
        sub_a = ["e", "ions", "es", "iez", "e", "ent"]
        sub_b = ["e", "emos", "es", "eis", "e", "en"]
        ti_a = ["i", "imos", "is", "itis", "i", "in"]
        ti_b = ["i", "imus", "is", "itis", "i", "in"]
        ta_a = ["a", "amos", "as", "atis", "a", "an"]
        ta_b = ["a", "amus", "as", "atis", "a", "an"]
        nf = ["r", "nt", "t", "a", "e"]

        def block(rows: list[list[str]]) -> list[list[str]]:
            cells: list[list[str]] = []
            for row in rows:
                cells.extend(_phones(c) for c in row)
            cells.extend(_phones(c) for c in nf)
            assert len(cells) == 41
            return cells

        templates = {
            "aa": block([fillers_a, past_a, fut_a, sub_a, ti_a, ta_a]),
            "bb": block([fillers_b, past_b, fut_b, sub_b, ti_b, ta_b]),
        }
        cells, label = assemble_verb_rows(set(), templates)
        # Present 1pl should be ons (aa); future 1pl should follow with erons.
        self.assertEqual(cells[1], _phones("ons"))
        self.assertEqual(cells[13], _phones("erons"))  # fut row starts at 12
        self.assertIn("prs=", label)
        self.assertEqual(len(PERSON_CELL_NAMES), 6)


if __name__ == "__main__":
    unittest.main()
