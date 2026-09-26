#!/usr/bin/env python3
"""Rebuild Romagnol 6-grids from Wiktionary rgn-conj template args.

Kaikki dumps the tables but drops 2sg (syncretic with 1sg in the module).
Template args already name every person ending. avér / vlér are hardcoded
from their Wiktionary templates (no args).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

KAIKKI = ROOT / "data" / "words" / "kaikki-rgn.jsonl"
OUT = ROOT / "data" / "conjugation" / "sources" / "rgn_diseux.json"
WIKT = "https://en.wiktionary.org/wiki/"

SLOTS = ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")


def cell(form: str, *, url: str, label: str) -> dict | None:
    form = form.strip()
    if not form or form == "—" or "{{" in form:
        return None
    return {
        "form": form,
        "phonemes": [],
        "source_label": label,
        "source_url": url,
    }


def row(forms: dict[str, str], *, url: str, label: str) -> dict:
    out = {}
    for slot in SLOTS:
        packed = cell(forms.get(slot, ""), url=url, label=label)
        if packed:
            out[slot] = packed
    return out


def join(stem: str, ending: str | None) -> str:
    if ending is None:
        return stem
    if "{{" in stem or "{{" in ending:
        return ""
    return f"{stem}{ending}"


def first_variant(value: str) -> str:
    # "{{l|rgn|ó}}, {{l|rgn|ò}}" already unwrapped by args; keep first comma piece
    piece = value.split(",")[0].strip()
    return piece


def from_table_args(lemma: str, class_source: str, args: dict, url: str) -> dict | None:
    stem = str(args.get("stem") or "").strip()
    if not stem:
        return None
    pres1 = first_variant(str(args.get("pres-1") or stem))
    pres3_stem = first_variant(str(args.get("pres-3") or stem))
    three_sg_end = str(args.get("3-s-pr") or "")
    pres3 = join(pres3_stem, three_sg_end)
    present = {
        "1sg": pres1,
        "2sg": pres1,
        "3sg": pres3,
        "1pl": join(stem, args.get("1-p-pr")),
        "2pl": join(stem, args.get("2-p-pr")),
        "3pl": pres3,
    }
    imperfect = {
        "1sg": join(stem, args.get("1-s-impf")),
        "2sg": join(stem, args.get("2-s-impf")),
        "3sg": join(stem, args.get("3-s-impf")),
        "1pl": join(stem, args.get("1-p-impf")),
        "2pl": join(stem, args.get("2-p-impf")),
        "3pl": join(stem, args.get("3-p-impf")),
    }
    past = {
        "1sg": join(stem, args.get("1-s-past")),
        "2sg": join(stem, args.get("2-s-past")),
        "3sg": join(stem, args.get("3-s-past")),
        "1pl": join(stem, args.get("1-p-past")),
        "2pl": join(stem, args.get("2-p-past")),
        "3pl": join(stem, args.get("3-p-past")),
    }
    future = {
        "1sg": join(stem, args.get("1-s-fut")),
        "2sg": join(stem, args.get("2-s-fut")),
        "3sg": join(stem, args.get("3-s-fut")),
        "1pl": join(stem, args.get("1-p-fut")),
        "2pl": join(stem, args.get("2-p-fut")),
        "3pl": join(stem, args.get("3-p-fut")),
    }
    cond = {
        "1sg": join(stem, args.get("1-s-cond")),
        "2sg": join(stem, args.get("2-s-cond")),
        "3sg": join(stem, args.get("1-s-cond")),
        "1pl": join(stem, args.get("1-p-cond")),
        "2pl": join(stem, args.get("2-p-cond")),
        "3pl": join(stem, args.get("1-s-cond")),
    }
    subj_3sg = join(stem, args.get("3-s-pr"))
    subj_3pl = join(stem, args.get("1-s-pr-s")) or subj_3sg
    subjunctive = {
        "1sg": subj_3sg,
        "2sg": subj_3sg,
        "3sg": subj_3sg,
        "1pl": join(stem, args.get("1-p-pr-s")),
        "2pl": join(stem, args.get("2-p-pr-s")),
        "3pl": subj_3pl,
    }
    cells = {}
    mapping = (
        ("indicative.present", present),
        ("indicative.imperfect", imperfect),
        ("indicative.preterite", past),
        ("indicative.future", future),
        ("conditional", cond),
        ("subjunctive.present", subjunctive),
        ("imperative", {
            "2sg": first_variant(str(args.get("pres-3") or "")),
            "1pl": join(stem, args.get("1-p-pr")),
            "2pl": join(stem, args.get("2-p-pr")),
        }),
    )
    for feature, forms in mapping:
        packed = row(forms, url=url, label=feature)
        if packed:
            cells[feature] = packed
    if not cells:
        return None
    return {
        "lect": "rgn",
        "lemma": lemma,
        "class_source": class_source,
        "regularity": "model",
        "source": {
            "attested": True,
            "title": f"Wiktionary:{lemma}",
            "url": url,
            "provider": "en.wiktionary.org",
            "stem": stem,
        },
        "cells": cells,
    }


def hardcoded_aver() -> dict:
    url = WIKT + "avér"
    def R(*forms: str, feature: str) -> dict:
        return row(dict(zip(SLOTS, forms)), url=url, label=feature)
    return {
        "lect": "rgn",
        "lemma": "avér",
        "class_source": "rgn-conj-avér",
        "regularity": "irregular",
        "source": {
            "attested": True,
            "title": "Wiktionary:avér",
            "url": url,
            "provider": "en.wiktionary.org",
        },
        "cells": {
            "indicative.present": R("ò", "é", "à", "avẽn", "avì", "à", feature="indicative.present"),
            "indicative.imperfect": R(
                "avéva", "avìvtia", "avéva", "avìmia", "avìvia", "avéva",
                feature="indicative.imperfect",
            ),
            "indicative.preterite": R(
                "avèt", "avès", "avèt", "avèsum", "avèsuv", "avèt",
                feature="indicative.preterite",
            ),
            "indicative.future": R("arò", "aré", "arà", "arẽn", "arì", "arà", feature="indicative.future"),
            "conditional": R("arèb", "arès", "arèb", "arèsum", "arèsuv", "arèb", feature="conditional"),
            "subjunctive.present": R("éva", "éva", "éva", "avègna", "avìva", "éva", feature="subjunctive.present"),
        },
    }


def hardcoded_vler() -> dict:
    url = WIKT + "vlér"
    def R(*forms: str, feature: str) -> dict:
        return row(dict(zip(SLOTS, forms)), url=url, label=feature)
    return {
        "lect": "rgn",
        "lemma": "vlér",
        "class_source": "rgn-conj-vlér",
        "regularity": "irregular",
        "source": {
            "attested": True,
            "title": "Wiktionary:vlér",
            "url": url,
            "provider": "en.wiktionary.org",
        },
        "cells": {
            "indicative.present": R("vój", "vu", "vö", "vlén", "vlè", "vö", feature="indicative.present"),
            "indicative.imperfect": R(
                "vléva", "vlìvia", "vléva", "vlìmia", "vlìvia", "vléva",
                feature="indicative.imperfect",
            ),
            "indicative.preterite": R(
                "vlét", "vlès", "vlét", "vlèsum", "vlèsuv", "vlét",
                feature="indicative.preterite",
            ),
            "indicative.future": R("vró", "vré", "vrà", "vrẽn", "vrì", "vrà", feature="indicative.future"),
            "conditional": R("vréb", "vrès", "vrèb", "vrèsum", "vrèsuv", "vrèb", feature="conditional"),
        },
    }


def harvest_kaikki() -> list[dict]:
    if not KAIKKI.is_file():
        return []
    out: list[dict] = []
    seen: set[str] = set()
    for line in KAIKKI.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("pos") != "verb":
            continue
        lemma = str(entry.get("word") or "").strip()
        templates = entry.get("inflection_templates") or []
        table = None
        class_source = "unknown"
        for item in templates:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "")
            if "conj" not in name:
                continue
            if "table" in name:
                table = item
            elif class_source == "unknown":
                class_source = name
        if table is None:
            continue
        if lemma.lower() in seen:
            continue
        packed = from_table_args(
            lemma,
            class_source,
            table.get("args") or {},
            WIKT + lemma.replace(" ", "_"),
        )
        if packed:
            seen.add(lemma.lower())
            out.append(packed)
    return out


def main() -> int:
    paradigms = harvest_kaikki()
    by_lemma = {item["lemma"].lower(): item for item in paradigms}
    for extra in (hardcoded_aver(), hardcoded_vler()):
        by_lemma[extra["lemma"].lower()] = extra
    merged = sorted(by_lemma.values(), key=lambda item: item["lemma"])
    document = {
        "schema": "vulgultra.conjugation.v1",
        "metadata": {
            "lect": "rgn",
            "purpose": "Romagnol conjugations reconstructed from Wiktionary rgn-conj templates",
            "provider": "en.wiktionary.org",
            "attribution": "Wiktionary Template:rgn-conj-* (CC BY-SA)",
            "ending_inventories": {},
            "optimizer_involved": False,
        },
        "paradigms": merged,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT} paradigms={len(merged)}")
    for item in merged:
        present = item["cells"].get("indicative.present", {})
        print(f"  {item['lemma']} {item['class_source']} present={list(present)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
