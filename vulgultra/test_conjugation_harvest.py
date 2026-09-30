"""Tests for Kaikki conjugation harvest and 6-slot ending extraction."""

import unittest

from vulgultra.conjugation_harvest import (
    aggregate_ending_inventory,
    decode_tags,
    primary_conj_template,
    recover_conjugation_persons,
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

    def test_recover_conjugation_persons_fills_1sg_3sg_3pl(self) -> None:
        forms = recover_conjugation_persons([
            {"form": "sai", "source": "conjugation",
             "tags": ["error-unrecognized-form", "indicative", "present", "singular"]},
            {"form": "sante", "source": "conjugation",
             "tags": ["indicative", "present", "second-person", "singular"]},
            {"form": "sant", "source": "conjugation",
             "tags": ["error-unrecognized-form", "indicative", "present", "singular"]},
            {"form": "saime", "source": "conjugation",
             "tags": ["first-person", "indicative", "plural", "present"]},
            {"form": "saite", "source": "conjugation",
             "tags": ["indicative", "plural", "present", "second-person"]},
            {"form": "sant", "source": "conjugation",
             "tags": ["error-unrecognized-form", "indicative", "present", "plural"]},
        ])
        slots = []
        for rec in forms:
            slot, feature, amb = decode_tags(rec["tags"])
            slots.append((rec["form"], slot, feature, amb))
        self.assertEqual(
            slots,
            [
                ("sai", "1sg", "indicative.present", False),
                ("sante", "2sg", "indicative.present", False),
                ("sant", "3sg", "indicative.present", False),
                ("saime", "1pl", "indicative.present", False),
                ("saite", "2pl", "indicative.present", False),
                ("sant", "3pl", "indicative.present", False),
            ],
        )


if __name__ == "__main__":
    unittest.main()


class HarvestFixTests(unittest.TestCase):
    SLOTS = ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")

    def endings(self, lect: str, forms: str) -> dict:
        from vulgultra.conjugation_harvest import strip_endings
        result = strip_endings(dict(zip(self.SLOTS, forms.split())), None, lect)
        assert result
        return result[0]

    def test_inchoative_infix_is_stem(self) -> None:
        dormo = self.endings("it", "dormo dormi dorme dormiamo dormite dormono")
        self.assertEqual(self.endings("it", "finisco finisci finisce finiamo finite finiscono"), dormo)
        self.assertEqual(self.endings("ro", "lucrez lucrezi lucrează lucrăm lucrați lucrează")["1sg"], "∅")
        self.assertEqual(self.endings("ca", "serveixo serveixes serveix servim serviu serveixen")["1sg"], "o")
        self.assertEqual(self.endings("es", "conozco conoces conoce conocemos conocéis conocen")["1sg"], "o")

    def test_template_stem_falls_back_to_lcp(self) -> None:
        from vulgultra.conjugation_harvest import strip_endings
        forms = dict(zip(self.SLOTS, "canto cantas canta cantamos cantais cantan".split()))
        endings, used, mode = strip_endings(forms, stem="aveir")
        self.assertEqual((used, mode, endings["1sg"]), ("cant", "lcp", "o"))

    def test_subject_clitics(self) -> None:
        from vulgultra.conjugation_harvest import strip_subject_clitics
        self.assertEqual(strip_subject_clitics("fur", "o fevelavi"), "fevelavi")
        self.assertEqual(strip_subject_clitics("fur", "al"), "")
        self.assertEqual(strip_subject_clitics("vec", "el łustra"), "łustra")
        self.assertEqual(strip_subject_clitics("es", "me fié"), "me fié")

    def test_tense_tags(self) -> None:
        self.assertEqual(decode_tags(["historic", "indicative", "past", "first-person", "singular"])[1],
                         "indicative.preterite")
        self.assertEqual(decode_tags(["indicative", "perfect", "first-person", "singular"], "ro")[1],
                         "indicative.preterite")
        self.assertEqual(decode_tags(["indicative", "past", "first-person", "singular"], "pms")[1],
                         "indicative.imperfect")
        self.assertTrue(decode_tags(["imperative", "negative", "second-person", "singular"])[1].startswith("skip"))

    def test_row_forms_prefers_single_word(self) -> None:
        from vulgultra.conjugation_harvest import row_forms
        cells = {"1sg": [{"form": "me fiai"}, {"form": "fiai"}]}
        self.assertEqual(row_forms(cells)["1sg"], "fiai")


class VerbixParseTests(unittest.TestCase):
    def record(self, tenses: list, exists: bool = True) -> dict:
        return {"lemma": "falar", "raw": {"exists": exists, "tenses": {
            str(i): {"name": name, "forms": [{"id": pid, "form": form} for pid, form in forms]}
            for i, (name, forms) in enumerate(tenses)
        }}}

    def test_first_tense_wins_and_compound_is_skipped(self) -> None:
        from vulgultra.verbix import parse_paradigm
        paradigm = parse_paradigm("pt", self.record([
            ("Indicative Pluperfect", [(1, "falara")]),
            ("Indicative Pluperfect", [(1, "tinha falado")]),
        ]))
        cell = paradigm["cells"]["indicative.pluperfect"]["1sg"]
        self.assertEqual((cell["form"], cell["variants"]), ("falara", []))

    def test_extra_forms_are_variants(self) -> None:
        from vulgultra.verbix import parse_paradigm
        paradigm = parse_paradigm("es", self.record([
            ("Subjunctive Past", [(1, "hablara"), (1, "hablase")]),
        ]))
        cell = paradigm["cells"]["subjunctive.imperfect"]["1sg"]
        self.assertEqual((cell["form"], cell["variants"]), ("hablara", ["hablase"]))

    def test_friulian_past_is_preterite_and_generated_pages_skipped(self) -> None:
        from vulgultra.verbix import map_feature, parse_paradigm
        self.assertEqual(map_feature("Indicative Past", "fur"), "indicative.preterite")
        self.assertEqual(map_feature("Indicative Past", "pt"), "indicative.imperfect")
        self.assertIsNone(parse_paradigm("es", self.record([("Indicative Present", [(1, "x")])], exists=False)))
