#!/usr/bin/env python3
"""Parse Extremaduran conjugation tables from vendor/recursos_es-ext.

Spanish and Extremaduran files share section order. Variant cells are aligned
by grouping consecutive identical Spanish forms (e.g. soy/soy → soi/so).
"""

from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FOLDER = ROOT / "vendor" / "recursos_es-ext" / "Conjugacion verbos"
OUT = ROOT / "data" / "conjugation" / "sources" / "ext_diseux.json"
SOURCE_URL = "https://github.com/juanro49/recursos_es-ext"

SLOTS = ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")

FEATURE_HEADERS = {
    "presenti simpli": "indicative.present",
    "presente simple": "indicative.present",
    "passau simpli": "indicative.preterite",
    "preterito perfecto simple": "indicative.preterite",
    "passau emperfetu": "indicative.imperfect",
    "preterito imperfecto": "indicative.imperfect",
    "hoturu simpli": "indicative.future",
    "futuro simple": "indicative.future",
    "podencial simpli": "conditional",
    "condicional simple": "conditional",
    "presenti simpli de sojuntivu": "subjunctive.present",
    "presente simple de subjuntivo": "subjunctive.present",
    "passau imperfetu de sojuntivu": "subjunctive.imperfect",
    "preterito imperfecto de subjuntivo": "subjunctive.imperfect",
    "hoturu de sojuntivu": "subjunctive.future",
    "futuro de subjuntivo": "subjunctive.future",
    "imperativu afirmau": "imperative",
    "imperativo afirmado": "imperative",
}

# Every section title in the paired files, including compounds we skip.
ALL_HEADERS = {
    "enfinitivu simpli", "infinitivo simple",
    "enfinitivu compuestu", "infinitivo compuesto",
    "gerundiu simpli", "gerundio simple",
    "gerundiu compuestu", "gerundio compuesto",
    "participiu", "participio",
    "presenti simpli", "presente simple",
    "passau simpli", "preterito perfecto simple",
    "passau emperfetu", "preterito imperfecto",
    "passau continu", "pasado continuo",
    "passau perfetu", "preterito perfecto compuesto",
    "passau mas-que-perfetu", "preterito pluscuamperfecto",
    "hoturu simpli", "futuro simple",
    "hoturu perfetu", "futuro perfecto",
    "podencial simpli", "condicional simple",
    "podencial compuestu", "condicional compuesto",
    "presenti simpli de sojuntivu", "presente simple de subjuntivo",
    "passau perfetu de sojuntivu", "preterito perfecto de subjuntivo",
    "passau imperfetu de sojuntivu", "preterito imperfecto de subjuntivo",
    "hoturu de sojuntivu", "futuro de subjuntivo",
    "passau mas-que-perfetu de sojuntivu", "preterito pluscuamperfecto de subjuntivo",
    "imperativu afirmau", "imperativo afirmado",
    "imperativu negau", "imperativo negado",
}

IRREGULAR = {
    "sel": "ser", "ser": "ser",
    "estal": "estar", "estar": "estar",
    "avel": "haber", "haber": "haber",
    "dil": "ir", "ir": "ir",
    "venir": "venir",
}


def fold(text: str) -> str:
    stripped = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode()
    return stripped.lower().strip()


def class_from_lemma(lemma: str) -> str:
    low = lemma.lower().strip()
    if low in IRREGULAR:
        return IRREGULAR[low]
    for ending in ("al", "el", "il", "ar", "er", "ir"):
        if low.endswith(ending):
            return f"-{ending}"
    return "other"


def parse_sections(text: str) -> dict[str, list[str]]:
    """Map folded header → form lines (last wins if a header repeats)."""
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        key = fold(line)
        if key in ALL_HEADERS:
            current = key
            sections[current] = []
            continue
        if current is None:
            continue
        sections[current].append(line)
    return sections


def assign_slots(
    ext_forms: list[str],
    es_forms: list[str] | None,
) -> dict[str, list[str]]:
    """Map EXT forms onto 6 person slots. Values are [primary, *alts]."""
    cleaned = [form for form in ext_forms if form and form != "-"]
    if not cleaned:
        return {}
    if es_forms and len(es_forms) == len(ext_forms):
        groups: list[list[str]] = []
        current_es = None
        current: list[str] = []
        for es_form, ext_form in zip(es_forms, ext_forms):
            if current_es is None or es_form != current_es:
                if current:
                    groups.append(current)
                current_es = es_form
                current = [ext_form]
            else:
                current.append(ext_form)
        if current:
            groups.append(current)
        usable = [[form for form in group if form and form != "-"] for group in groups]
        usable = [group for group in usable if group]
        if len(usable) == 6:
            return {slot: group for slot, group in zip(SLOTS, usable)}
    n = len(cleaned)
    if n == 6:
        return {slot: [form] for slot, form in zip(SLOTS, cleaned)}
    if n == 7:
        return {
            "1sg": cleaned[:2],
            "2sg": [cleaned[2]],
            "3sg": [cleaned[3]],
            "1pl": [cleaned[4]],
            "2pl": [cleaned[5]],
            "3pl": [cleaned[6]],
        }
    if n == 8:
        return {
            "1sg": cleaned[:2],
            "2sg": [cleaned[2]],
            "3sg": [cleaned[3]],
            "1pl": [cleaned[4]],
            "2pl": [cleaned[5]],
            "3pl": cleaned[6:],
        }
    if n >= 9:
        return {
            "1sg": cleaned[:2],
            "2sg": [cleaned[2]],
            "3sg": cleaned[3:5],
            "1pl": [cleaned[5]],
            "2pl": [cleaned[6]],
            "3pl": cleaned[7:9],
        }
    return {slot: [form] for slot, form in zip(SLOTS, cleaned)}


def cell(form: str, alts: list[str], *, url: str, label: str) -> dict:
    packed = {
        "form": form,
        "phonemes": [],
        "source_label": label,
        "source_url": url,
    }
    extras = [item for item in alts if item and item != form]
    if extras:
        packed["notes"] = extras
    return packed


def parse_lemma(lemma: str, ext_text: str, es_text: str, rel: str) -> dict | None:
    ext_sections = parse_sections(ext_text)
    es_sections = parse_sections(es_text)
    url = SOURCE_URL + "/tree/master/Conjugacion%20verbos"
    cells: dict[str, dict] = {}
    for header, feature in FEATURE_HEADERS.items():
        if header not in ext_sections:
            continue
        ext_forms = ext_sections[header]
        es_forms = None
        for es_header, es_feature in FEATURE_HEADERS.items():
            if es_feature == feature and es_header in es_sections:
                es_forms = es_sections[es_header]
                break
        slotted = assign_slots(ext_forms, es_forms)
        row: dict[str, dict] = {}
        for slot, forms in slotted.items():
            primary, *alts = forms
            if " " in primary:
                continue
            row[slot] = cell(primary, alts, url=url, label=feature)
        if row:
            cells[feature] = row
    if not cells:
        return None
    infinitive = (ext_sections.get("enfinitivu simpli") or [lemma])[0]
    return {
        "lect": "ext",
        "lemma": infinitive,
        "class_source": class_from_lemma(infinitive),
        "regularity": "irregular" if class_from_lemma(infinitive) in IRREGULAR.values() else "regular",
        "source": {
            "attested": True,
            "title": f"recursos_es-ext:{infinitive}",
            "url": url,
            "provider": "recursos_es-ext",
            "source_file": rel,
        },
        "cells": cells,
    }


def main() -> int:
    paradigms: list[dict] = []
    for ext_path in sorted(FOLDER.glob("*.ext.txt")):
        lemma = ext_path.name[:-8]
        es_path = ext_path.with_name(f"{lemma}.es.txt")
        ext_text = ext_path.read_text(encoding="utf-8", errors="replace")
        es_text = es_path.read_text(encoding="utf-8", errors="replace") if es_path.is_file() else ""
        rel = str(ext_path.relative_to(ROOT))
        packed = parse_lemma(lemma, ext_text, es_text, rel)
        if packed:
            paradigms.append(packed)
            print(f"{lemma}: {packed['lemma']} class={packed['class_source']} tams={len(packed['cells'])}")
        else:
            print(f"{lemma}: skipped (no finite grid)")
    document = {
        "schema": "vulgultra.conjugation.v1",
        "metadata": {
            "lect": "ext",
            "purpose": "Extremaduran conjugations from recursos_es-ext paired ES/EXT tables",
            "provider": "recursos_es-ext",
            "attribution": (
                "juanro49/recursos_es-ext (CC0); "
                "https://github.com/juanro49/recursos_es-ext"
            ),
            "ending_inventories": {},
            "optimizer_involved": False,
        },
        "paradigms": paradigms,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT} paradigms={len(paradigms)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
