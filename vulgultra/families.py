"""Lemma families from {code}_words.json. Classes fall out of the skeleton."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from vulgultra.romance_swadesh import SOURCE_LANGS
from vulgultra.skeleton import skeleton, split_frame

WORDS_DIR = Path(__file__).resolve().parent.parent / "data" / "words"


def lemma_of(lang: str, key: str, rec: dict) -> str:
    raw = rec.get(lang) or key
    if isinstance(raw, list):
        raw = raw[0] if raw else key
    return str(raw).strip()


def load_lemmas(langs: tuple[str, ...] = SOURCE_LANGS) -> list[tuple[str, str, list[str]]]:
    """(lang, citation, glosses_en) for every headword on disk."""
    rows: list[tuple[str, str, list[str]]] = []
    for lang in langs:
        path = WORDS_DIR / f"{lang}_words.json"
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for key, rec in (data.get("entries") or {}).items():
            if not isinstance(rec, dict):
                continue
            word = lemma_of(lang, key, rec)
            if len(word) < 2:
                continue
            glosses = [str(g).strip().lower() for g in (rec.get("glosses_en") or []) if g]
            rows.append((lang, word, glosses))
    return rows


def gloss_key(glosses: list[str]) -> str:
    if not glosses:
        return ""
    g = glosses[0].split(",")[0].split(";")[0].strip()
    return g


def build_families(
    rows: list[tuple[str, str, list[str]]] | None = None,
) -> dict[str, list[dict]]:
    """Map skeleton → member dicts. Empty skeleton is dropped (no merge)."""
    if rows is None:
        rows = load_lemmas()
    buckets: dict[str, list[dict]] = defaultdict(list)
    for lang, citation, glosses in rows:
        open_word, frame = split_frame(citation)
        sk = skeleton(citation)
        if not sk:
            continue
        buckets[sk].append({
            "lang": lang,
            "citation": citation,
            "open": open_word,
            "frame": frame,
            "gloss": gloss_key(glosses),
            "skeleton": sk,
        })
    return dict(buckets)


def split_false_friends(members: list[dict]) -> list[list[dict]]:
    """If two glossed members disagree, they are different families."""
    by_gloss: dict[str, list[dict]] = defaultdict(list)
    silent: list[dict] = []
    for m in members:
        if m["gloss"]:
            by_gloss[m["gloss"]].append(m)
        else:
            silent.append(m)
    if len(by_gloss) <= 1:
        return [members]
    groups = list(by_gloss.values())
    if silent:
        groups[0].extend(silent)
    return groups


def classify_family(members: list[dict]) -> str:
    langs = {m["lang"] for m in members}
    if len(langs) >= 2:
        return "contest"
    return "unico"


def family_stats(families: dict[str, list[dict]]) -> dict:
    contests = 0
    unicos = 0
    members_contest = 0
    members_unico = 0
    lects_contest: set[str] = set()
    after_veto = 0
    for members in families.values():
        for group in split_false_friends(members):
            after_veto += 1
            kind = classify_family(group)
            n = len(group)
            if kind == "contest":
                contests += 1
                members_contest += n
                lects_contest.update(m["lang"] for m in group)
            else:
                unicos += 1
                members_unico += n
    return {
        "skeletons": len(families),
        "families_after_gloss_veto": after_veto,
        "contests": contests,
        "unicos": unicos,
        "members_in_contests": members_contest,
        "members_unicos": members_unico,
        "lects_in_a_contest": len(lects_contest),
    }
