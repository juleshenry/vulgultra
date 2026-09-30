"""Tests for Gallo Wiktionnaire cell parsing."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "harvest_gallo_frwikt",
    ROOT / "scripts" / "harvest_gallo_frwikt.py",
)
assert SPEC and SPEC.loader
hg = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(hg)


def row(*forms: str) -> dict:
    return {slot: {"form": form} for slot, form in zip(hg.SLOTS, forms)}


class GalloHarvestTests(unittest.TestCase):
    def test_elg_second_plural_pronoun(self) -> None:
        self.assertEqual(hg.cell_forms("vóz chauntétz"), ["chauntétz"])

    def test_pronoun_alternation_is_not_a_form_split(self) -> None:
        self.assertEqual(hg.cell_forms("vous / v'etes"), ["etes"])

    def test_line_variants_are_kept_in_order(self) -> None:
        self.assertEqual(hg.cell_forms("il chauntt\nil chauntan"), ["chauntt", "chauntan"])

    def test_reflexive_clitics(self) -> None:
        self.assertEqual(hg.cell_forms("il/ol se nall", reflexive=True), ["nall"])
        self.assertEqual(hg.cell_forms("vóz vóz nalétz", reflexive=True), ["nalétz"])
        self.assertEqual(hg.cell_forms("nall tei", reflexive=True), ["nall"])

    def test_clipped_et_imperfect_restored(self) -> None:
        self.assertEqual(hg.cell_forms("je ’taes"), ["etaes"])

    def test_foreign_row_and_cell_dropped(self) -> None:
        cells = {
            "indicative.present": row("chauntt", "chauntt", "chauntt", "chaunton", "chauntétz", "chauntt"),
            "subjunctive.present": row("bauj", "bauj", "bauj", "baujion", "baujiétz", "bauj"),
            "indicative.preterite": row("chauntis", "chauntis", "póvit", "chauntim", "chauntitt", "chauntirr"),
        }
        hg.drop_foreign_forms("chauntae", cells)
        self.assertNotIn("subjunctive.present", cells)
        self.assertNotIn("3sg", cells["indicative.preterite"])

    def test_stem_alternation_survives(self) -> None:
        cells = {
            "indicative.present": row("tiens", "tiens", "tient", "tenon", "tenétz", "tienn"),
            "indicative.future": row("tienrae", "tienras", "tienra", "tienron", "tienrétz", "tienron"),
        }
        self.assertEqual(hg.drop_foreign_forms("teni", cells), [])


if __name__ == "__main__":
    unittest.main()
