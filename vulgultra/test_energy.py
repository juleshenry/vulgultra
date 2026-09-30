"""Energy parity fixture and the σ-slice mutation invariant.

The hand total is the same vector the Rust test asserts. Root SA scores only
the selected-root segment union; endings are optimized separately.
"""

from __future__ import annotations

import random
import unittest

from vulgultra.optimizer import (
    NOUN_SLOTS,
    VERB_SLOTS,
    Candidate,
    Genome,
    compute_energy,
    mutate_root,
)
from vulgultra.optimizer_constants import W_COLL
from vulgultra.phonology import count_syllables


def _cand(concept: str, lang: str, word: str, phones: list[str], syl: int = 1) -> Candidate:
    return Candidate(
        concept=concept,
        source_lang=lang,
        source_word=word,
        ipa="".join(phones),
        vulgultra_phonemes=list(phones),
        orthography="".join(phones),
        syllables=syl,
        violations=0,
    )


def _fixture() -> Genome:
    row = [["p", "a"], ["b", "e"], ["t", "i"], ["d", "o"], ["k", "u"], ["m", "a", "n"]]
    finite = row * 6
    nf = [["r", "a"], ["n", "e"], ["t", "o"], ["a"], ["e"]]
    verb_cells = finite + nf
    noun_cells = [
        ["o"], ["o", "n"], ["i", "s"], ["i"], ["o", "s"], ["o", "r"],
        ["a"], ["a", "n"], ["e", "s"], ["e"], ["a", "s"], ["a", "r"],
    ]
    assert len(verb_cells) == len(VERB_SLOTS)
    assert len(noun_cells) == len(NOUN_SLOTS)
    noun = {slot: cell[:] for slot, cell in zip(NOUN_SLOTS, noun_cells)}
    verb = {slot: cell[:] for slot, cell in zip(VERB_SLOTS, verb_cells)}
    cands = {
        "c1": [_cand("c1", "es", "gat", ["ɡ", "a", "t"])],
        "c2": [_cand("c2", "it", "kan", ["k", "a", "n"])],
        "c3": [_cand("c3", "pt", "a", ["a"])],
    }
    return Genome(
        selections={"c1": 0, "c2": 0, "c3": 0},
        candidates=cands,
        noun_endings={"class_1": noun},
        verb_endings={"class_1": verb},
        adj_endings={slot: cell[:] for slot, cell in noun.items()},
    )


class EnergyTests(unittest.TestCase):
    def test_fixture_matches_hand_total(self) -> None:
        total, bd = compute_energy(_fixture())
        self.assertEqual(bd["E_phon"], -5)
        self.assertEqual(bd["E_end"], 10600)
        self.assertEqual(bd["E_coll"], 0)
        self.assertEqual(bd["E_tact"], 0)
        self.assertEqual(bd["E_dist"], 0)
        self.assertAlmostEqual(total, 10595, places=6)

    def test_finite_verb_syncretism_costs_nothing(self) -> None:
        genome = _fixture()
        verb = genome.verb_endings["class_1"]
        verb["prs_3pl"] = verb["prs_3sg"][:]
        verb["prs_2sg"] = verb["prs_1sg"][:]
        _total, bd = compute_energy(genome)
        self.assertEqual(bd["E_coll"], 0)
        self.assertEqual(bd["E_dist"], 0)

    def test_noun_and_nonfinite_collisions_still_counted(self) -> None:
        genome = _fixture()
        noun = genome.noun_endings["class_1"]
        noun[NOUN_SLOTS[1]] = noun[NOUN_SLOTS[0]][:]
        self.assertEqual(compute_energy(genome)[1]["E_coll"], W_COLL)
        genome = _fixture()
        verb = genome.verb_endings["class_1"]
        verb[VERB_SLOTS[-1]] = verb[VERB_SLOTS[-2]][:]
        self.assertEqual(compute_energy(genome)[1]["E_coll"], W_COLL)

    def test_verb_cells_keep_attested_ending_nouns_clip(self) -> None:
        from vulgultra.paradigms import VERB_TEMPLATES, _case_block, _row
        from vulgultra.phonology import from_orthography
        # Aragonese present 1pl is attested `amos` and must not clip to `mos`.
        self.assertEqual(VERB_TEMPLATES["an"][1], from_orthography("amos"))
        # Noun gen.pl is still 1σ (Latin -ōrum/-ārum reduced to `or`/`ar`).
        block = _case_block("o", "a", "os", "as")
        gen_pl = block[NOUN_SLOTS.index("m_gen_pl")]
        self.assertEqual(count_syllables(gen_pl), 1)
        self.assertTrue(all(count_syllables(cell) == 1 for cell in block))
        # The nominal row builder still clips a 2σ cell to its last σ.
        self.assertEqual(_row("orum")[0], from_orthography("rum"))

    def test_mutation_stays_on_sigma_slice(self) -> None:
        genome = _fixture()
        genome.candidates["c1"] = [
            _cand("c1", "es", "a", ["a"], 1),
            _cand("c1", "fr", "ba", ["b", "a"], 2),
            _cand("c1", "it", "ka", ["k", "a"], 1),
        ]
        genome.selections["c1"] = 0
        random.seed(7)
        for _ in range(40):
            moved = mutate_root(genome)
            self.assertEqual(moved.get_root("c1").syllables, 1)

if __name__ == "__main__":
    unittest.main()


class DiphthongRepairTests(unittest.TestCase):
    def test_falling_and_rising_diphthongs_are_one_syllable(self) -> None:
        from vulgultra.phonology import count_syllables, from_orthography, repair
        for ortho, sigma in [("ais", 1), ("ai", 1), ("eu", 1), ("au", 1), ("akua", 2), ("amos", 2), ("ea", 2)]:
            self.assertEqual(count_syllables(repair(from_orthography(ortho))), sigma, ortho)

    def test_intervocalic_high_vowel_is_one_glide(self) -> None:
        from vulgultra.phonology import repair
        self.assertEqual(repair(list("aio")), list("ajo"))
