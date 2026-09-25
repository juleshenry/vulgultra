"""Verbix conjugation client for Romance lects (CC BY-NC 3.0).

Cite Verbix and link https://www.verbix.com. Responses are cached under
data/sources/verbix/{lect}/.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

VERBIX_API_KEY = "6153a464-b4f0-11ed-9ece-ee3761609078"
USER_AGENT = "vulgultra-research/0.1 (+noncommercial; cite Verbix)"

PERSON_BY_ID = {
    1: "1sg", 2: "2sg", 3: "3sg", 4: "1pl", 5: "2pl", 6: "3pl",
}

TENSE_BY_NAME = {
    "indicative present": "indicative.present",
    "subjunctive present": "subjunctive.present",
    "indicative past": "indicative.imperfect",
    "subjunctive past": "subjunctive.imperfect",
    "indicative imperfect": "indicative.imperfect",
    "subjunctive imperfect": "subjunctive.imperfect",
    "indicative preterite": "indicative.preterite",
    "indicative future": "indicative.future",
    "conditional": "conditional",
    "imperative": "imperative",
    "indicative perifrastic past": "indicative.periphrastic-past",
    "indicative present perfect": "indicative.present-perfect",
    "indicative pluperfect": "indicative.pluperfect",
    "indicative future perfect": "indicative.future-perfect",
    "subjunctive present perfect": "subjunctive.present-perfect",
    "subjunctive pluperfect": "subjunctive.pluperfect",
    "conditional perfect": "conditional.perfect",
}

# Lect → Verbix ISO + numeric langid + infinitive ending classes.
LECT_CONFIG: dict[str, dict[str, Any]] = {
    "es": {"iso": "spa", "langid": 1, "endings": ("ar", "er", "ir")},
    "pt": {"iso": "por", "langid": 2, "endings": ("ar", "er", "ir")},
    "gl": {"iso": "glg", "langid": 6, "endings": ("ar", "er", "ir")},
    "ca": {"iso": "cat", "langid": 7, "endings": ("ar", "er", "ir", "re")},
    "fr": {"iso": "fra", "langid": 3, "endings": ("er", "ir", "re")},
    "it": {"iso": "ita", "langid": 4, "endings": ("are", "ere", "ire")},
    "ro": {"iso": "ron", "langid": 5, "endings": ("ea", "a", "e", "i")},
    "an": {"iso": "arg", "langid": 52, "endings": ("ar", "er", "ir", "re")},
    "ast": {"iso": "ast", "langid": 16, "endings": ("ar", "er", "ir")},
    "mwl": {"iso": "mwl", "langid": 54, "endings": ("ar", "er", "ir")},
    "oc": {"iso": "oci", "langid": 8, "endings": ("ar", "er", "ir", "re")},
    "co": {"iso": "cos", "langid": 129, "endings": ("à", "é", "ì", "are", "ere", "ire", "a", "e", "i")},
    "fur": {"iso": "fur", "langid": 132, "endings": ("â", "ê", "î", "à", "è", "ì", "ar", "er", "ir")},
    "frp": {"iso": "frp", "langid": 261, "endings": ("ar", "er", "ir", "re")},
    "rm": {"iso": "roh", "langid": 56, "endings": ("ar", "er", "ir", "air", "eir", "ir")},
    "pms": {"iso": "pms", "langid": 12034, "endings": ("é", "è", "ì", "é", "ar", "er", "ir")},
    "sc": {"iso": "srd", "langid": 12, "endings": ("are", "ere", "ire", "ai", "ei", "i")},
    "scn": {"iso": "scn", "langid": 13946, "endings": ("ari", "iri", "iri", "ari")},
    "lld": {"iso": "lld", "langid": 295, "endings": ("é", "er", "ir", "ì")},
    # Verbix shelves Gascon under Occitan (oci); keep lect code gsc locally.
    "gsc": {"iso": "oci", "langid": 8, "endings": ("ar", "er", "ir", "re")},
}

IRREGULAR = {
    "an": {
        "estar": "estar", "ser": "ser", "haber": "haber", "aber": "haber",
        "haber-ie": "haber-ie", "ir": "ir", "anar": "anar", "ir/anar": "ir/anar", "yir": "ir",
    },
    "es": {"estar": "estar", "ser": "ser", "haber": "haber", "ir": "ir"},
    "pt": {"estar": "estar", "ser": "ser", "haver": "haver", "ir": "ir", "ter": "ter"},
    "gl": {"estar": "estar", "ser": "ser", "haber": "haber", "ir": "ir"},
    "ca": {"estar": "estar", "ser": "ser", "haver": "haver", "anar": "anar"},
    "fr": {"être": "être", "avoir": "avoir", "aller": "aller"},
    "it": {"essere": "essere", "avere": "avere", "andare": "andare", "fare": "fare", "dare": "dare", "stare": "stare"},
    "ro": {"fi": "fi", "avea": "avea", "vrea": "vrea"},
}


def class_from_infinitive(lect: str, lemma: str) -> str:
    low = lemma.lower().strip()
    irregulars = IRREGULAR.get(lect, {})
    if low in irregulars:
        return irregulars[low]
    cfg = LECT_CONFIG.get(lect) or {}
    endings = cfg.get("endings") or ("ar", "er", "ir")
    # Longer endings first.
    for ending in sorted(endings, key=len, reverse=True):
        if low.endswith(ending):
            return f"-{ending}"
    return "other"


def normalize_class(lect: str, lemma: str, current: str | None = None) -> str:
    irregulars = IRREGULAR.get(lect, {})
    low = lemma.lower().strip()
    if low in irregulars:
        return irregulars[low]
    raw = (current or "").strip().lower()
    if raw.startswith("-") or raw in irregulars.values():
        return raw if raw.startswith("-") else raw
    # Provider tags / unknown → infinitive ending.
    return class_from_infinitive(lect, lemma)


def conj_url(lect: str, lemma: str) -> str:
    iso = LECT_CONFIG[lect]["iso"]
    return (
        f"https://api.verbix.com/conjugator/iv1/{VERBIX_API_KEY}/"
        f"{iso}/{urllib.parse.quote(lemma)}/json"
    )


def page_url(lect: str, lemma: str) -> str:
    langid = LECT_CONFIG[lect]["langid"]
    return (
        "https://www.verbix.com/webverbix/go.php?"
        f"D1={langid}&T1={urllib.parse.quote(lemma)}"
    )


def fetch_json(url: str, *, timeout: float = 30.0) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object from {url}")
    return payload


def cache_path(cache_dir: Path, lemma: str) -> Path:
    return cache_dir / f"{urllib.parse.quote(lemma, safe='')}.json"


def load_or_fetch(
    lect: str,
    lemma: str,
    *,
    cache_dir: Path,
    sleep_s: float = 0.15,
    force: bool = False,
) -> dict[str, Any]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_path(cache_dir, lemma)
    if path.is_file() and not force:
        return json.loads(path.read_text(encoding="utf-8"))
    url = conj_url(lect, lemma)
    try:
        raw = fetch_json(url)
    except urllib.error.HTTPError as exc:
        raw = {"exists": False, "error": f"HTTP {exc.code}", "tenses": {}}
    except Exception as exc:  # noqa: BLE001
        raw = {"exists": False, "error": str(exc), "tenses": {}}
    record = {
        "lect": lect,
        "lemma": lemma,
        "fetched_from": url,
        "page_url": page_url(lect, lemma),
        "license": "CC BY-NC 3.0",
        "attribution": "Verbix (https://www.verbix.com)",
        "raw": raw,
    }
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if sleep_s > 0:
        time.sleep(sleep_s)
    return record


def map_feature(tense_name: str) -> str | None:
    return TENSE_BY_NAME.get(tense_name.strip().lower())


def parse_paradigm(lect: str, record: dict[str, Any]) -> dict[str, Any] | None:
    lemma = str(record.get("lemma") or "").strip()
    raw = record.get("raw") if isinstance(record.get("raw"), dict) else {}
    tenses = raw.get("tenses") if isinstance(raw.get("tenses"), dict) else {}
    if not lemma or not tenses:
        return None
    cells: dict[str, dict[str, dict[str, Any]]] = {}
    for tense in tenses.values():
        if not isinstance(tense, dict):
            continue
        feature = map_feature(str(tense.get("name") or ""))
        if not feature:
            continue
        row: dict[str, dict[str, Any]] = {}
        for form_rec in tense.get("forms") or []:
            if not isinstance(form_rec, dict):
                continue
            try:
                person_id = int(form_rec.get("id"))
            except (TypeError, ValueError):
                continue
            slot = PERSON_BY_ID.get(person_id)
            form = str(form_rec.get("form") or "").strip()
            if not slot or not form or form == "-":
                continue
            row.setdefault(slot, {
                "form": form,
                "phonemes": [],
                "source_label": str(tense.get("name") or ""),
                "source_url": record.get("page_url") or "",
            })
        if row:
            cells[feature] = row
    if not cells:
        return None
    exists = bool(raw.get("exists"))
    return {
        "lect": lect,
        "lemma": lemma,
        "class_source": class_from_infinitive(lect, lemma),
        "regularity": "attested" if exists else "rule-generated",
        "source": {
            "attested": exists,
            "title": f"Verbix {lect}:{lemma}",
            "url": record.get("page_url") or page_url(lect, lemma),
            "provider": "Verbix",
            "license": "CC BY-NC 3.0",
        },
        "cells": cells,
    }


def harvest_lemmas(
    lect: str,
    lemmas: list[str],
    *,
    cache_dir: Path,
    sleep_s: float = 0.15,
    force: bool = False,
) -> dict[str, Any]:
    if lect not in LECT_CONFIG:
        raise KeyError(f"no Verbix config for lect {lect!r}")
    paradigms: list[dict[str, Any]] = []
    stats = {"fetched": 0, "attested": 0, "generated": 0, "empty": 0}
    for lemma in lemmas:
        record = load_or_fetch(
            lect, lemma, cache_dir=cache_dir, sleep_s=sleep_s, force=force,
        )
        stats["fetched"] += 1
        paradigm = parse_paradigm(lect, record)
        if not paradigm:
            stats["empty"] += 1
            continue
        if paradigm["source"]["attested"]:
            stats["attested"] += 1
        else:
            stats["generated"] += 1
        paradigms.append(paradigm)
    return {
        "schema": "vulgultra.conjugation.v1",
        "metadata": {
            "lect": lect,
            "purpose": "Verbix conjugation harvest",
            "provider": "Verbix",
            "license": "CC BY-NC 3.0",
            "attribution": "Verbix (https://www.verbix.com)",
            "stats": stats,
            "optimizer_involved": False,
        },
        "paradigms": paradigms,
    }
