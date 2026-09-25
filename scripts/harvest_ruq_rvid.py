#!/usr/bin/env python3
"""Compile Megleno-Romanian (`ruq`) conjugations from RVID 2.0 + Capidan tables.

Primary descriptive source: Capidan 1925 (*Meglenoromânii* I). The machine-
readable layer is the Romance Verbal Inflection Dataset 2.0 (GPLv3), derived
from the Oxford Online Database of Romance Verb Morphology, which generalizes
Capidan’s survey across Greek–Macedonian border varieties (see Atanasov 2002).

Orthographic class exemplars follow Capidan-tradition tables as summarized on
French Wikipedia (Mégléno-roumain); IPA paradigms come from RVID.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RVID = ROOT / "data" / "sources" / "rvid_megleno"
OUT = ROOT / "data" / "conjugation" / "sources" / "ruq_diseux.json"

SLOTS = ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")
PERSON = {
    "1SG": "1sg", "2SG": "2sg", "3SG": "3sg",
    "1PL": "1pl", "2PL": "2pl", "3PL": "3pl",
}
FEATURE = {
    "PRS-IND": "indicative.present",
    "IMPERF-IND": "indicative.imperfect",
    "PRET": "indicative.preterite",
    "PRS-SBJV": "subjunctive.present",
    "IMP": "imperative",
}

# Capidan-tradition orthographic models (fr.wiki / Capidan conjugations).
# Short infinitives are citation labels; Capidan/Oxford note verbal infinitive
# use is highly restricted / virtually extinct.
ORTHO_MODELS = {
    "cantare": {
        "lemma": "căntári",
        "class_source": "I",
        "gloss": "to sing",
        "indicative.present": ("cǫ́nt", "cǫ́nț", "cǫ́ntă", "căntǫ́m", "căntáț", "cǫ́ntă"),
        "indicative.imperfect": ("căntám", "căntái̯", "căntá", "căntám", "căntáț", "căntáu̯"),
        "indicative.preterite": ("căntái̯", "căntáș", "căntǫ́", "căntǫ́m", "căntáț", "căntáră"),
        "subjunctive.present": ("să cǫ́nt", "să cǫ́nț", "să cǫ́ntă", "să căntǫ́m", "să căntáț", "să cǫ́ntă"),
    },
    "lucrari": {
        "lemma": "lucrári",
        "class_source": "I-ez",
        "gloss": "to work",
        "indicative.present": ("lucréz", "lucréz", "lucre̯áză", "lucrǫ́m", "lucráț", "lucre̯áză"),
        "subjunctive.present": ("să lucréz", "să lucréz", "să lucre̯áză", "să lucrǫ́m", "să lucráț", "să lucre̯áză"),
    },
    "cadere": {
        "lemma": "cădeári",
        "class_source": "II",
        "gloss": "to fall",
        "indicative.present": ("cad", "caz", "cádi", "cădém", "cădéț", "cad"),
        "indicative.imperfect": ("căde̯ám", "căde̯ái̯", "căde̯á", "căde̯ám", "căde̯áț", "căde̯áu̯"),
        "indicative.preterite": ("căzúi̯", "căzúș", "căzú", "căzúm", "căzúț", "căzúră"),
        "subjunctive.present": ("să cád", "să cáz", "să cádă", "să cădém", "să cădéț", "să cádă"),
    },
    "battuere": {
        "lemma": "bátiri",
        "class_source": "III",
        "gloss": "to beat",
        "indicative.present": ("bat", "baț", "báti", "bátim", "bátiț", "bat"),
        "indicative.imperfect": ("băte̯ám", "băte̯ái̯", "băte̯á", "băte̯ám", "băte̯áț", "băte̯áu̯"),
        "indicative.preterite": ("bătúi̯", "bătúș", "bătú", "bătúm", "bătúț", "bătúră"),
        "subjunctive.present": ("să bát", "să báț", "să bátă", "să bátim", "să bátiț", "să bátă"),
    },
    "dormire": {
        "lemma": "durmíri",
        "class_source": "IV",
        "gloss": "to sleep",
        "indicative.present": ("dorm", "dorm", "do̯ármi", "durmím", "durmíț", "dorm"),
        "indicative.imperfect": ("durme̯ám", "durme̯ái̯", "durme̯á", "durme̯ám", "durme̯áț", "durme̯áu̯"),
        "indicative.preterite": ("durmíi̯", "durmíș", "durmí", "durmím", "durmíț", "durmíră"),
        "subjunctive.present": ("să dórm", "să dárm", "să do̯ármă", "să durmím", "să durmíț", "să do̯ármă"),
    },
    "seruire": {
        "lemma": "sirbíri",
        "class_source": "IV-esc",
        "gloss": "to serve / work",
        "indicative.present": ("sirbés", "sirbéș", "sirbe̯áști", "sirbím", "sirbíț", "sirbés"),
        "subjunctive.present": ("să sirbés", "să sirbéș", "să sirbe̯áscă", "să sirbím", "să sirbíț", "să sirbe̯áscă"),
    },
}

ETYMON_CLASS = {
    "cantare": "I", "lucrari": "I-ez", "stare": "I", "adunare": "I", "intrare": "I",
    "ambulare": "I", "leuare": "I", "afflare": "I",
    "cadere": "II", "sedere": "II", "habere": "II", "posse": "II",
    "battuere": "III", "bibere": "III", "ardere": "III", "dicere": "III",
    "facere": "III", "ducere": "III", "mergere": "III", "plangere": "III",
    "rumpere": "III", "sugere": "III", "tondere": "III", "trahere": "III",
    "coquere": "III", "intelligere": "III",
    "dormire": "IV", "seruire": "IV-esc", "subire": "IV", "fugere": "IV",
    "dare": "I", "esse~fieri": "fi",
}

# Capidan 1925 pp. 172–74 are the locus often cited for a fi; forms below follow
# Capidan-tradition summaries (Wikisource dialect chapter + RVID IPA cross-check).
FI_ORTHO = {
    "lemma": "iri / sam",
    "class_source": "fi",
    "gloss": "to be",
    "indicative.present": ("jes", "jești", "jasti", "im", "iț", "sa"),
    "indicative.imperfect": ("ăi̯ram", "ăi̯rai̯", "ăi̯ra", "ăi̯ram", "ăi̯raț", "ăi̯rau̯"),
    "indicative.preterite": ("fui̯", "fuș", "fu", "fum", "fuț", "fură"),
    "subjunctive.present": ("esku", "jeș", "jască", "im", "iț", "ijă"),
}


def cell(form: str, *, ipa: str = "", url: str = "", label: str = "") -> dict:
    out = {
        "form": form,
        "phonemes": [],
        "source_label": label or "rvid/capidan",
        "source_url": url or "https://gitlab.com/sbeniamine/Romance_Verbal_Inflection_Dataset",
    }
    if ipa:
        out["ipa"] = ipa
    return out


def row_forms(forms: tuple[str, ...], *, ipas: dict[str, str] | None = None) -> dict[str, dict]:
    out = {}
    for slot, form in zip(SLOTS, forms):
        if not form:
            continue
        out[slot] = cell(form, ipa=(ipas or {}).get(slot, ""), label="capidan-tradition orthography")
    return out


def parse_rvid() -> dict[str, dict[str, dict[str, str]]]:
    """cognateset → feature → slot → IPA form."""
    by: dict[str, dict[str, dict[str, str]]] = defaultdict(lambda: defaultdict(dict))
    with open(RVID / "forms.csv", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            form = (row.get("Form") or "").strip()
            if not form or form in {"Ø", "?", "-", "–"}:
                continue
            cell_id = row.get("Cell") or ""
            if "~" in cell_id:
                feat, person = cell_id.split("~", 1)
            else:
                feat, person = cell_id, ""
            feature = FEATURE.get(feat)
            if not feature:
                # Keep infinitive / participle as tagged extras
                if feat == "INF":
                    feature = "nonfinite.infinitive"
                    person = "CIT"
                elif feat == "PST-PTCP":
                    feature = "nonfinite.participle"
                    person = "MSG"
                elif feat == "GER":
                    feature = "nonfinite.gerund"
                    person = "INV"
                else:
                    continue
            slot = PERSON.get(person, person.lower() if person else "inv")
            by[row["Cognateset_ID"]][feature][slot] = form
    return by


def lexeme_index() -> dict[str, dict]:
    out = {}
    with open(RVID / "lexemes.csv", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            out[row["Cognateset_ID"]] = row
    return out


def build() -> dict:
    rvid = parse_rvid()
    lexemes = lexeme_index()
    paradigms: list[dict] = []

    # 0) a fi (Capidan 1925 ~pp. 172–74 locus in secondary literature).
    fi_ipas = rvid.get("esse~fieri", {})
    fi_cells: dict[str, dict] = {}
    for feature, forms in FI_ORTHO.items():
        if feature in {"lemma", "class_source", "gloss"}:
            continue
        ipas = {slot: fi_ipas.get(feature, {}).get(slot, "") for slot in SLOTS}
        fi_cells[feature] = row_forms(forms, ipas=ipas)
    for feature, slot_map in fi_ipas.items():
        if feature in fi_cells:
            continue
        row = {}
        for slot, ipa in slot_map.items():
            if slot in SLOTS:
                row[slot] = cell(ipa, ipa=ipa, label="rvid IPA")
        if row:
            fi_cells[feature] = row
    paradigms.append({
        "lect": "ruq",
        "lemma": FI_ORTHO["lemma"],
        "class_source": "fi",
        "regularity": "irregular",
        "source": {
            "attested": True,
            "title": "Capidan 1925 a fi (Megleno-Romanian)",
            "url": "https://ro.wikisource.org/wiki/Meglenorom%C3%A2nii/Volumul_I",
            "provider": "Capidan 1925 (+ RVID IPA)",
            "gloss_en": FI_ORTHO["gloss"],
            "etymon": "esse~fieri",
            "page_hint": "often cited via Capidan 1925, pp. 172–74 for FIERI/a fi material",
            "rvid_license": "GPLv3",
        },
        "cells": fi_cells,
    })

    # 1) Orthographic Capidan-tradition exemplars (readable pages).
    for etymon, model in ORTHO_MODELS.items():
        ipa_map = rvid.get(etymon, {})
        cells: dict[str, dict] = {}
        for feature, forms in model.items():
            if feature in {"lemma", "class_source", "gloss"}:
                continue
            ipas = {
                slot: ipa_map.get(feature, {}).get(slot, "")
                for slot in SLOTS
            }
            cells[feature] = row_forms(forms, ipas=ipas)
        # attach IPA-only features from RVID not in ortho model
        for feature, slot_map in ipa_map.items():
            if feature in cells:
                continue
            if feature.startswith("nonfinite."):
                # citation infinitive note
                for slot, ipa in slot_map.items():
                    cells.setdefault(feature, {})[slot] = cell(
                        f"[{ipa}]",
                        ipa=ipa,
                        label="rvid IPA citation form (infinitive restricted)",
                    )
                continue
            row = {}
            for slot, ipa in slot_map.items():
                if slot not in SLOTS:
                    continue
                row[slot] = cell(ipa, ipa=ipa, label="rvid IPA")
            if row:
                cells[feature] = row
        paradigms.append({
            "lect": "ruq",
            "lemma": model["lemma"],
            "class_source": model["class_source"],
            "regularity": "model",
            "source": {
                "attested": True,
                "title": f"Capidan/RVID Megleno:{model['lemma']}",
                "url": "https://ro.wikisource.org/wiki/Meglenorom%C3%A2nii/Volumul_I",
                "provider": "Capidan 1925 via RVID/ODRVM + Capidan-tradition tables",
                "gloss_en": model["gloss"],
                "etymon": etymon,
                "rvid_license": "GPLv3",
                "caveat": (
                    "ODRVM/RVID generalizes Capidan across border varieties; "
                    "short infinitive virtually extinct as a verbal form."
                ),
            },
            "cells": cells,
        })

    # 2) Remaining RVID lemmas (IPA as form).
    covered = set(ORTHO_MODELS) | {"esse~fieri"}
    for etymon, featmap in sorted(rvid.items()):
        if etymon in covered:
            continue
        meta = lexemes.get(etymon, {})
        lemma = etymon.replace("~", "/")
        class_source = ETYMON_CLASS.get(etymon, "other")
        cells = {}
        for feature, slot_map in featmap.items():
            row = {}
            for slot, ipa in slot_map.items():
                key = slot if slot in SLOTS or slot in {"cit", "msg", "inv"} else slot
                if feature.startswith("nonfinite."):
                    row[key] = cell(f"[{ipa}]", ipa=ipa, label="rvid IPA")
                elif slot in SLOTS:
                    row[slot] = cell(ipa, ipa=ipa, label="rvid IPA")
            if row:
                cells[feature] = row
        if not any(slot in SLOTS for row in cells.values() for slot in row):
            continue
        paradigms.append({
            "lect": "ruq",
            "lemma": lemma,
            "class_source": class_source,
            "regularity": "unknown",
            "source": {
                "attested": True,
                "title": f"RVID Megleno:{etymon}",
                "url": "https://gitlab.com/sbeniamine/Romance_Verbal_Inflection_Dataset",
                "provider": "Romance Verbal Inflection Dataset 2.0 (from ODRVM/Capidan)",
                "gloss_en": meta.get("Meaning") or "",
                "etymon": etymon,
                "comment": meta.get("Comment") or "",
                "rvid_license": "GPLv3",
                "caveat": (
                    "IPA phonemic forms. Capidan 1925 is the descriptive base; "
                    "Atanasov 2002 for modern qualification."
                ),
            },
            "cells": cells,
        })

    return {
        "schema": "vulgultra.conjugation.v1",
        "metadata": {
            "lect": "ruq",
            "purpose": "Megleno-Romanian conjugations from Capidan/RVID",
            "provider": "Capidan 1925 + Romance Verbal Inflection Dataset 2.0",
            "attribution": (
                "Capidan, Theodor. 1925. Meglenoromânii I. "
                "Digitized morphology: Beniamine, Maiden & Round 2020 (RVID 2.0 / ODRVM)."
            ),
            "license_notes": "RVID GPLv3; Capidan text via Wikisource where available",
            "scholarly_prefer": [
                "Capidan 1925 (exact page for published claims)",
                "Atanasov 2002 Meglenoromâna astăzi",
                "Oxford Handbook Eastern Romance chapter",
            ],
            "ending_inventories": {},
            "optimizer_involved": False,
            "n_paradigms": len(paradigms),
            "gaps": (
                "Analytic future/conditional largely absent in RVID (Ø). "
                "Infinitive rows are citation/lexical labels, not productive verbal infinitives."
            ),
        },
        "paradigms": paradigms,
    }


def main() -> int:
    if not (RVID / "forms.csv").is_file():
        raise SystemExit(
            f"missing {RVID}/forms.csv — vendor Megleno rows from "
            "https://gitlab.com/sbeniamine/Romance_Verbal_Inflection_Dataset"
        )
    document = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT} paradigms={len(document['paradigms'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
