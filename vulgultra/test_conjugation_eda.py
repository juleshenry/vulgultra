"""Tests for the pre-optimizer conjugation EDA layer."""

import unittest

from vulgultra.conjugation_eda import analyze_paradigm, normalize_cell, normalize_document


def _cell(form: str, phones: list[str]) -> dict:
    return {"form": form, "phonemes": phones}


class ConjugationEdaTests(unittest.TestCase):
    def test_shared_person_suffix_is_linked_across_tenses(self) -> None:
        document = normalize_document({
            "schema": "vulgultra.conjugation.v1",
            "paradigms": [{
                "lect": "es",
                "lemma": "hablar",
                "class_source": "-ar",
                "cells": {
                    "indicative.present": {
                        "1pl": _cell("hablamos", list("hablamos")),
                    },
                    "indicative.future": {
                        "1pl": _cell("hablaremos", list("hablaremos")),
                    },
                },
            }],
        })
        links = analyze_paradigm(document["paradigms"][0])["links"]
        self.assertTrue(any(
            link["kind"] == "person_number_suffix"
            and link["slot"] == "1pl"
            and link["segments"] == ["m", "o", "s"]
            for link in links
        ))


    def test_identical_forms_are_not_claimed_as_a_suffix(self) -> None:
        document = normalize_document({
            "paradigms": [{
                "lect": "fr",
                "lemma": "parler",
                "cells": {
                    "indicative.present": {"1sg": _cell("e", ["e"])},
                    "indicative.past": {"1sg": _cell("e", ["e"])},
                },
            }],
        })
        links = analyze_paradigm(document["paradigms"][0])["links"]
        self.assertFalse(any(link["kind"] == "person_number_suffix" for link in links))

    def test_compact_ipa_is_not_split_as_evidence(self) -> None:
        cell = normalize_cell(
            {"form": "chat", "ipa": "ʃa"},
            lect="fr", feature="indicative.present", slot="1sg",
        )
        self.assertEqual(cell["phonemes"], [])
        self.assertEqual(cell["ipa"], "ʃa")
