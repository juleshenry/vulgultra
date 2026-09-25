#!/usr/bin/env python3
"""Compile Istro-Romanian (`ruo`) conjugation tables from Verbix docs.

Primary source: https://docs.verbix.com/Languages/Istroromanian
plus Verbix scanned notes (CCF00762009_00085/86). No live Verbix conjugator
API exists for `ruo`; this is a curated table harvest.

For formal citation prefer Neiescu / Kovačec / Oxford Eastern Romance chapters;
Verbix is a compact secondary summary.
"""

from __future__ import annotations

import json
import shutil
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "conjugation" / "sources" / "ruo_diseux.json"
CACHE = ROOT / "data" / "sources" / "ruo_verbix"
DOCS_URL = "https://docs.verbix.com/Languages/Istroromanian"
NOTES = [
    "https://content.verbix.com/scanned/CCF00762009_00085.pdf",
    "https://content.verbix.com/scanned/CCF00762009_00086.pdf",
]
USER_AGENT = "vulgultra-research/0.1 (+noncommercial; cite Verbix docs)"

SLOTS = ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")


def fetch(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 1000:
        return
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as response:
        dest.write_bytes(response.read())


def row(*forms: str) -> dict[str, dict]:
    out = {}
    for slot, form in zip(SLOTS, forms):
        form = form.strip()
        if not form or form == "—":
            continue
        out[slot] = {
            "form": form,
            "phonemes": [],
            "source_label": "verbix-docs",
            "source_url": DOCS_URL,
        }
    return out


def paradigm(
    lemma: str,
    class_source: str,
    cells: dict[str, dict[str, dict]],
    *,
    gloss: str = "",
    note: str = "",
) -> dict:
    return {
        "lect": "ruo",
        "lemma": lemma,
        "class_source": class_source,
        "regularity": "model",
        "source": {
            "attested": True,
            "title": f"Verbix Istro-Romanian:{lemma}",
            "url": DOCS_URL,
            "provider": "docs.verbix.com",
            "gloss_en": gloss,
            "notes": note,
            "citation_note": (
                "Secondary online summary. For formal work cite Neiescu, "
                "Kovačec, or Oxford Eastern Romance chapters."
            ),
        },
        "cells": {feature: slots for feature, slots in cells.items() if slots},
    }


def build() -> dict:
    # Class labels: I -å, II -é, III -e, IV -í (+ -éi / -úi subtypes).
    paradigms = [
        # —— Class I (clămå / rugå) ——
        paradigm(
            "rugå",
            "I-å",
            {
                "nonfinite.infinitive": {"?": {
                    "form": "rugå", "phonemes": [], "source_url": DOCS_URL,
                    "source_label": "infinitive",
                }},
                "nonfinite.gerund": {"?": {
                    "form": "rugánda", "phonemes": [], "source_url": DOCS_URL,
                    "source_label": "gerund",
                }},
                # Present from Verbix scanned notes (complete 6-slot).
                "indicative.present": row("rog", "róži", "róga", "rugån", "rugåţ", "rógu"),
                "indicative.imperfect": row(
                    "rugåiam", "rugåiai", "rugåia", "rugåian", "rugåiat", "rugåia",
                ),
                # Conditional future table on Verbix docs (= future paradigm).
                "indicative.future": row(
                    "rugår", "rugåri", "rugåre", "rugårno", "rugåret", "rugåru",
                ),
                # Analytic conditional present: particle + infinitive.
                "conditional": row(
                    "res rugå", "rei rugå", "re rugå", "ren rugå", "ret rugå", "re rugå",
                ),
                "indicative.perfect": row(
                    "rugåt-am", "—", "—", "—", "—", "—",
                ),
            },
            gloss="to pray / call (class I model)",
            note="Infinitive class example also clămå; siblings stå, turnå, zucå",
        ),
        paradigm(
            "clămå",
            "I-å",
            {
                "nonfinite.infinitive": {"?": {
                    "form": "clămå", "phonemes": [], "source_url": DOCS_URL,
                    "source_label": "infinitive",
                }},
            },
            gloss="to call (class I citation infinitive)",
        ),
        # —— Class II (ramaré / tiré / cadé) ——
        paradigm(
            "tiré",
            "II-é",
            {
                "nonfinite.infinitive": {"?": {
                    "form": "tiré", "phonemes": [], "source_url": DOCS_URL,
                    "source_label": "infinitive",
                }},
                "nonfinite.gerund": {"?": {
                    "form": "tiránda", "phonemes": [], "source_url": DOCS_URL,
                    "source_label": "gerund",
                }},
                "indicative.present": row("tiru", "tíri", "tíre", "tirén", "tiréţ", "tíru"),
                "indicative.imperfect": row(
                    "cadéiam", "cadéiai", "cadéia", "cadéian", "cadéiat", "cadéia",
                ),
                "indicative.future": row(
                    "tirúr", "tirúri", "tirúre", "tirúrno", "tirúret", "tirúru",
                ),
                "indicative.perfect": row(
                    "—", "tirút-ai", "—", "—", "—", "—",
                ),
            },
            gloss="class II model (tiré / cadé / ramaré)",
            note="Other II: ve, be, ramaré",
        ),
        paradigm(
            "ramaré",
            "II-é",
            {
                "nonfinite.infinitive": {"?": {
                    "form": "ramaré", "phonemes": [], "source_url": DOCS_URL,
                    "source_label": "infinitive",
                }},
            },
            gloss="class II citation infinitive",
        ),
        # —— Class III (båte / trage) ——
        paradigm(
            "trage",
            "III-e",
            {
                "nonfinite.infinitive": {"?": {
                    "form": "båte", "phonemes": [], "source_url": DOCS_URL,
                    "source_label": "class III infinitive example båte",
                }},
                "nonfinite.gerund": {"?": {
                    "form": "tragánda", "phonemes": [], "source_url": DOCS_URL,
                    "source_label": "gerund",
                }},
                "indicative.present": row("meg", "méži", "mége", "mézen", "mézeţ", "mégu"),
                "indicative.imperfect": row(
                    "trazéiam", "trazéiai", "trazéia", "trazéian", "trazéiat", "trazéia",
                ),
                "indicative.future": row(
                    "trasér", "traséri", "trasére", "trasérno", "traséret", "traséru",
                ),
                "indicative.perfect": row(
                    "—", "—", "tras-a", "—", "—", "—",
                ),
            },
            gloss="class III model (båte / trage)",
            note="Other III: årde, pl'erde, zacl'ide",
        ),
        paradigm(
            "båte",
            "III-e",
            {
                "nonfinite.infinitive": {"?": {
                    "form": "båte", "phonemes": [], "source_url": DOCS_URL,
                    "source_label": "infinitive",
                }},
            },
            gloss="class III citation infinitive",
        ),
        # —— Class IV (durmi / avzí) ——
        paradigm(
            "avzí",
            "IV-í",
            {
                "nonfinite.infinitive": {"?": {
                    "form": "avzí", "phonemes": [], "source_url": DOCS_URL,
                    "source_label": "infinitive",
                }},
                "nonfinite.gerund": {"?": {
                    "form": "avzínda", "phonemes": [], "source_url": DOCS_URL,
                    "source_label": "gerund",
                }},
                "indicative.present": row("åvd", "åvzi", "åvde", "avzín", "avzíţ", "åvdu"),
                "indicative.imperfect": row(
                    "avzíiam", "avzíiai", "avzíia", "avzíian", "avzíiat", "avzíia",
                ),
                "indicative.future": row(
                    "avzír", "avzíri", "avzíre", "avzírno", "avzíret", "avzíru",
                ),
                "indicative.perfect": row(
                    "—", "—", "—", "avzít-am", "—", "—",
                ),
            },
            gloss="to hear (class IV model)",
            note="Other IV: durmí, fi, cuperí",
        ),
        paradigm(
            "durmi",
            "IV-í",
            {
                "nonfinite.infinitive": {"?": {
                    "form": "durmi", "phonemes": [], "source_url": DOCS_URL,
                    "source_label": "infinitive",
                }},
            },
            gloss="to sleep (class IV citation)",
        ),
        # —— Class IV subtype -éi (iterative/perfective notes) ——
        paradigm(
            "cupéi",
            "IV-éi",
            {
                "nonfinite.infinitive": {"?": {
                    "form": "cupéi", "phonemes": [], "source_url": DOCS_URL,
                    "source_label": "infinitive",
                }},
                "nonfinite.gerund": {"?": {
                    "form": "copéinda", "phonemes": [], "source_url": DOCS_URL,
                    "source_label": "gerund",
                }},
                "indicative.present": row(
                    "copésc", "copéšti", "copéšte", "copín", "copíţ", "copéscu",
                ),
                "indicative.future": row(
                    "copéir", "copéiri", "copéire", "copéirno", "copéiret", "copéiru",
                ),
                "indicative.perfect": row(
                    "—", "—", "—", "—", "—", "copéit-a(v)",
                ),
            },
            gloss="class IV -éi model",
            note=(
                "Verbix: verbs in -véi and -úi are iterative; -éi may be "
                "perfective or imperfective. Also bivéi, movéi, piséi, frustikéi."
            ),
        ),
        paradigm(
            "carúi",
            "IV-úi",
            {
                "nonfinite.infinitive": {"?": {
                    "form": "carúi", "phonemes": [], "source_url": DOCS_URL,
                    "source_label": "infinitive",
                }},
            },
            gloss="class IV -úi example (iterative)",
            note="Also radúi. Slavic-contact-influenced innovative class.",
        ),
    ]

    # Ending inventories from complete imperfect/future rows where stable.
    inventories = {
        "I-å": {
            "indicative.imperfect": {
                "endings": {
                    "1sg": "iam", "2sg": "iai", "3sg": "ia",
                    "1pl": "ian", "2pl": "iat", "3pl": "ia",
                },
                "support": 1,
                "stem_mode": "lemma-rugå",
            },
            "indicative.future": {
                "endings": {
                    "1sg": "r", "2sg": "ri", "3sg": "re",
                    "1pl": "rno", "2pl": "ret", "3pl": "ru",
                },
                "support": 1,
                "stem_mode": "lemma-rugå",
            },
        },
    }

    return {
        "schema": "vulgultra.conjugation.v1",
        "metadata": {
            "lect": "ruo",
            "purpose": "Istro-Romanian four-class Verbix docs harvest",
            "provider": "docs.verbix.com + Verbix scanned notes",
            "attribution": DOCS_URL,
            "license": "Verbix site terms (CC BY-NC for API/site content)",
            "scholarly_prefer": [
                "Neiescu (Istro-Romanian descriptive tradition)",
                "Kovačec 1998",
                "Oxford Eastern Romance chapters (Istro-/Megleno-/Aromanian)",
                "Oxford ORA: Istro-Romanian verbs in -[ɛi] and -[ui]",
            ],
            "ending_inventories": inventories,
            "optimizer_involved": False,
            "gaps": (
                "Present 1sg/2sg/3sg/2pl empty on Verbix HTML summary for some "
                "classes filled from scanned notes; analytic perfect/conditional "
                "shown as particle+participle/infinitive strings."
            ),
        },
        "paradigms": paradigms,
    }


def main() -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    fetch(DOCS_URL, CACHE / "Istroromanian.html")
    for url in NOTES:
        fetch(url, CACHE / Path(url).name)
        # keep a copy under data/sources/pdf if useful
        dest = ROOT / "data" / "sources" / "pdf" / Path(url).name
        if not dest.exists():
            shutil.copy2(CACHE / Path(url).name, dest)
    document = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT} paradigms={len(document['paradigms'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
