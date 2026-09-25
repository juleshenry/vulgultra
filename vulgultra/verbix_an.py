"""Back-compat wrappers for Aragonese Verbix helpers."""

from __future__ import annotations

from vulgultra.verbix import (  # noqa: F401
    PERSON_BY_ID,
    TENSE_BY_NAME,
    class_from_infinitive as _class_from_infinitive,
    harvest_lemmas as _harvest_lemmas,
    load_or_fetch,
    normalize_class,
    parse_paradigm as _parse_paradigm,
)


def class_from_infinitive(lemma: str) -> str:
    return _class_from_infinitive("an", lemma)


def normalize_an_class(lemma: str, current: str | None = None) -> str:
    return normalize_class("an", lemma, current)


def parse_paradigm(record: dict) -> dict | None:
    return _parse_paradigm("an", record)


def harvest_lemmas(lemmas, *, cache_dir, sleep_s=0.2, force=False):
    return _harvest_lemmas(
        "an", lemmas, cache_dir=cache_dir, sleep_s=sleep_s, force=force,
    )
