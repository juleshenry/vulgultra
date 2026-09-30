"""Verbix conjugation client for Romance lects (CC BY-NC 3.0).

Cite Verbix and link https://www.verbix.com. Responses are cached under
data/sources/verbix/{lect}/.
"""

from __future__ import annotations

import json
import re
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

# Simple (synthetic) tenses only. Compound tenses (perfects, periphrastic
# past, compound pluperfects) carry an auxiliary and are not person endings;
# pluperfect stays because pt/gl/ro have a synthetic one (falara, lucrasem).
TENSE_BY_NAME = {
    "indicative present": "indicative.present",
    "subjunctive present": "subjunctive.present",
    "indicative past": "indicative.imperfect",
    "subjunctive past": "subjunctive.imperfect",
    "indicative imperfect": "indicative.imperfect",
    "subjunctive imperfect": "subjunctive.imperfect",
    "indicative preterite": "indicative.preterite",
    "indicative future": "indicative.future",
    "indicative future i": "indicative.future",
    "subjunctive future": "subjunctive.future",
    "conditional": "conditional",
    "conditional present": "conditional",
    "conditional present, direct": "conditional",
    "imperative": "imperative",
    "indicative pluperfect": "indicative.pluperfect",
    # lld / frp tables omit the mood; pms says "conjunctive".
    "present": "indicative.present",
    "imperfect": "indicative.imperfect",
    "preterite": "indicative.preterite",
    "future": "indicative.future",
    "subj.present": "subjunctive.present",
    "subj.imperfect": "subjunctive.imperfect",
    "conjunctive present": "subjunctive.present",
    "conjunctive past": "subjunctive.imperfect",
    # Second series of a tense: parsed as variants of the first.
    "subjunctive present ii": "subjunctive.present",
    "indicative future ii": "indicative.future",
    "conditional present ii": "conditional",
    "conditional present, indirect": "conditional",
}

# Per-lect corrections to the generic map (None drops the tense).
LECT_TENSE_BY_NAME: dict[str, dict[str, str | None]] = {
    # Friulian lists Indicative Imperfect separately; its "Past" is the preterite.
    "fur": {"indicative past": "indicative.preterite"},
    # Romanian has no synthetic past subjunctive; Verbix fills it with junk.
    "ro": {"subjunctive past": None, "indicative future ii": None},
}

# Verbix shelves Gascon under Occitan, so its "gsc" pages are Languedocien.
NOT_HARVESTED = {"gsc"}

# Lect → Verbix ISO + numeric langid + infinitive ending classes.
LECT_CONFIG: dict[str, dict[str, Any]] = {
    "es": {"iso": "spa", "langid": 1, "endings": ("ar", "er", "ir")},
    "pt": {"iso": "por", "langid": 2, "endings": ("ar", "er", "ir")},
    "gl": {"iso": "glg", "langid": 6, "endings": ("ar", "er", "ir")},
    "ca": {"iso": "cat", "langid": 7, "endings": ("ar", "er", "ir", "re")},
    "fr": {"iso": "fra", "langid": 3, "endings": ("er", "ir", "re")},
    "it": {"iso": "ita", "langid": 4, "endings": ("are", "ere", "ire")},
    "ro": {"iso": "ron", "langid": 5, "endings": ("ea", "a", "e", "i", "î")},
    "an": {"iso": "arg", "langid": 52, "endings": ("ar", "er", "ir", "re")},
    "ast": {"iso": "ast", "langid": 16, "endings": ("ar", "er", "ir")},
    "mwl": {"iso": "mwl", "langid": 54, "endings": ("ar", "er", "ir")},
    "oc": {"iso": "oci", "langid": 8, "endings": ("ar", "er", "ir", "re")},
    "co": {"iso": "cos", "langid": 129, "endings": ("à", "é", "ì", "are", "ere", "ire", "a", "e", "i")},
    "fur": {"iso": "fur", "langid": 132, "endings": ("â", "ê", "î", "à", "è", "ì", "ar", "er", "ir", "i")},
    "frp": {"iso": "frp", "langid": 261, "endings": ("ar", "er", "ir", "re")},
    "rm": {"iso": "roh", "langid": 56, "endings": ("ar", "er", "ir", "air", "eir", "ir")},
    "pms": {"iso": "pms", "langid": 12034, "endings": ("é", "è", "ì", "ar", "er", "ir", "e")},
    "sc": {"iso": "srd", "langid": 12, "endings": ("are", "ere", "ire", "ai", "ei", "i")},
    "scn": {"iso": "scn", "langid": 13946, "endings": ("ari", "iri", "iri", "ari")},
    "lld": {"iso": "lld", "langid": 295, "endings": ("é", "èr", "er", "ir", "ì", "ëi", "ei", "e")},
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


# Enclitic pronouns on pronominal infinitives: es zumbársela, it andarsene,
# pt/ca queixar-se. Stripped so the verb joins its conjugation class.
_IBERO_ENCLITIC = re.compile(r"(?<=r)(?:se|me|te|nos|os)?(?:l[aoe]s?)?$")
_ITALO_ENCLITIC = re.compile(r"(?<=r)(?:si|mi|ti|ci|vi)?(?:ne|l[aoie]|cel[aoie]|sel[aoie]|sene|cene)?$")
_HYPHEN_ENCLITIC = re.compile(
    r"(?:-(?:se|s'hi|me|te|nos|vos|li|hi|ne|en|lo|la|lhe|o|a)(?:-\w+)?|'(?:s|n|l|m|t|hi))$"
)
_UNACCENT = str.maketrans("áéíóú", "aeiou")
_IBERO = {"es", "ast", "an", "ext", "gl", "mwl", "lad"}
_ITALO = {"it", "co", "scn", "sc"}


def bare_infinitive(lect: str, lemma: str) -> str:
    """Infinitive without enclitic pronouns (zumbársela → zumbar, andarsene → andare)."""
    low = lemma.lower().strip()
    stripped = _HYPHEN_ENCLITIC.sub("", low)
    if stripped == low and lect in _IBERO:
        stripped = _IBERO_ENCLITIC.sub("", low)
        if stripped != low:
            stripped = stripped[:-2] + stripped[-2:].translate(_UNACCENT)
        # Hiatus -ír is the -ir class (reír, oír, saír).
        if stripped.endswith("ír"):
            stripped = stripped[:-2] + "ir"
    elif stripped == low and lect in _ITALO:
        stripped = _ITALO_ENCLITIC.sub("", low)
        if stripped != low:
            # Italian drops -e before the clitic; -rre verbs (condursi, porsi, trarsi).
            stripped += "re" if stripped.endswith(("dur", "por", "trar")) else "e"
    return stripped


def class_from_infinitive(lect: str, lemma: str) -> str:
    if " " in lemma.strip():
        # Idioms (tirar a sorte grande, fer olor) are phrases, not verb classes.
        return "phrase"
    low = bare_infinitive(lect, lemma)
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


def map_feature(tense_name: str, lect: str = "") -> str | None:
    name = tense_name.strip().lower()
    overrides = LECT_TENSE_BY_NAME.get(lect, {})
    if name in overrides:
        return overrides[name]
    return TENSE_BY_NAME.get(name)


_DIALECT_TAG = re.compile(r"\s*\((?:N|S)\)\s*$")


def clean_form(form: str) -> list[str]:
    """One Verbix form → bare words; [] for compound / annotated forms.

    Some pages glue two variants with no separator (frp prendríontprendríant):
    two halves of near-equal length that share a 5+ letter prefix.
    """
    text = _DIALECT_TAG.sub("", str(form or "").strip())
    if not text or text == "-" or " " in text or "(" in text:
        return []
    for cut in range(5, len(text) - 4):
        head, tail = text[:cut], text[cut:]
        if head[:5] == tail[:5] and abs(len(head) - len(tail)) <= 2:
            return [head, tail]
    return [text]


def _imperative_slots(ids: list[int]) -> dict[int, str]:
    """Some lects number imperative persons 1..3 (2sg, 1pl, 2pl)."""
    if ids and max(ids) <= 3:
        return {1: "2sg", 2: "1pl", 3: "2pl"}
    return PERSON_BY_ID


def parse_paradigm(lect: str, record: dict[str, Any]) -> dict[str, Any] | None:
    """First tense mapped to a feature is primary; later ones add variants.

    Every form listed for a person is kept in page order: the first as
    `form`, the rest as `variants` (es -ra/-se subjunctive, co N/S pairs).
    Rule-generated pages (`exists: false`) are not attested and are skipped.
    """
    lemma = str(record.get("lemma") or "").strip()
    raw = record.get("raw") if isinstance(record.get("raw"), dict) else {}
    tenses = raw.get("tenses") if isinstance(raw.get("tenses"), dict) else {}
    if not lemma or not tenses or not raw.get("exists"):
        return None
    cells: dict[str, dict[str, dict[str, Any]]] = {}
    for tense in tenses.values():
        if not isinstance(tense, dict):
            continue
        name = str(tense.get("name") or "")
        feature = map_feature(name, lect)
        if not feature:
            continue
        forms = [rec for rec in tense.get("forms") or [] if isinstance(rec, dict)]
        ids: list[int] = []
        for rec in forms:
            try:
                ids.append(int(rec.get("id")))
            except (TypeError, ValueError):
                ids.append(0)
        slots = _imperative_slots(ids) if feature == "imperative" else PERSON_BY_ID
        row = cells.setdefault(feature, {})
        for person_id, rec in zip(ids, forms):
            slot = slots.get(person_id)
            if not slot:
                continue
            for form in clean_form(rec.get("form")):
                cell = row.get(slot)
                if cell is None:
                    row[slot] = {
                        "form": form,
                        "variants": [],
                        "phonemes": [],
                        "source_label": name,
                        "source_url": record.get("page_url") or "",
                    }
                elif form != cell["form"] and form not in cell["variants"]:
                    cell["variants"].append(form)
        if not row:
            cells.pop(feature)
    if not cells:
        return None
    return {
        "lect": lect,
        "lemma": lemma,
        "class_source": class_from_infinitive(lect, lemma),
        "regularity": "attested",
        "source": {
            "attested": True,
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
            raw = record.get("raw") if isinstance(record.get("raw"), dict) else {}
            stats["generated" if raw.get("tenses") and not raw.get("exists") else "empty"] += 1
            continue
        stats["attested"] += 1
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
