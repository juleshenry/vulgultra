"""Harvest Kaikki/Wiktextract verb forms into lect-internal 6-slot grids.

Class labels stay language-internal. Orthographic ending inventories are
derived from complete person rows; missing cells stay missing.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable
from urllib.parse import quote

PERSON_SLOTS = ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")

SLOT_PERSON_TAGS = {
    "1sg": ("first-person", "singular"),
    "2sg": ("second-person", "singular"),
    "3sg": ("third-person", "singular"),
    "1pl": ("first-person", "plural"),
    "2pl": ("second-person", "plural"),
    "3pl": ("third-person", "plural"),
}

MOODS = {
    "indicative": "indicative",
    "subjunctive": "subjunctive",
    "conditional": "conditional",
    "imperative": "imperative",
}
TENSES = {
    "present": "present",
    "preterite": "preterite",
    "past": "past",
    "imperfect": "imperfect",
    "future": "future",
    "pluperfect": "pluperfect",
    "historic": "historic-past",
    "remote": "remote-past",
}

MAX_REPRESENTATIVES = 3
MIN_INVENTORY_SUPPORT = 3


def decode_tags(tags: list[str]) -> tuple[str | None, str, bool]:
    """Return person slot, feature id, and whether person/number is ambiguous."""
    tagset = {str(tag).lower().replace("_", "-") for tag in tags}
    person_tokens = [
        ("1", "first-person"), ("2", "second-person"), ("3", "third-person"),
    ]
    persons = [person for person, tag in person_tokens if tag in tagset]
    numbers = [number for number in ("singular", "plural") if number in tagset]
    ambiguous = len(persons) != 1 or len(numbers) != 1
    slot = (
        f"{persons[0]}{'sg' if numbers[0] == 'singular' else 'pl'}"
        if not ambiguous else None
    )

    if "infinitive" in tagset:
        feature = "nonfinite.infinitive"
    elif "gerund" in tagset or "present-participle" in tagset:
        feature = "nonfinite.gerund"
    elif "participle" in tagset:
        part = "-".join(sorted(tagset & {"past", "present", "active", "passive"})) or "unspecified"
        feature = f"nonfinite.participle-{part}"
    else:
        # Conditional often co-occurs with "indicative"; prefer conditional.
        if "conditional" in tagset:
            mood = "conditional"
        else:
            mood = next((name for tag, name in MOODS.items() if tag in tagset), None)
        tense = next((name for tag, name in TENSES.items() if tag in tagset), None)
        # Wiktionary form-of rows often tag tense alone under an indicative table.
        if mood is None and tense is not None:
            mood = "indicative"
        feature = ".".join(piece for piece in (mood, tense) if piece) or "unclassified"
    return slot, feature, ambiguous


def recover_conjugation_persons(forms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Fill 1sg/3sg/3pl when Wiktextract leaves only number on a conjugation cell.

    Dalmatian, Istriot, and Romagnol tables list persons in 1sg–3pl order.
    2sg/1pl/2pl are often tagged; leftover singulars fill 1sg then 3sg, leftover
    plurals fill the remaining plural slots. Already-tagged cells stay put.
    """
    recovered: list[dict[str, Any]] = [
        dict(item) if isinstance(item, dict) else item  # type: ignore[misc]
        for item in forms
    ]
    group: list[int] = []
    group_feature: str | None = None

    def inject(rec: dict[str, Any], slot: str) -> None:
        tags = [str(tag) for tag in rec.get("tags") or []]
        tags = [tag for tag in tags if tag != "error-unrecognized-form"]
        have = {tag.lower().replace("_", "-") for tag in tags}
        for piece in SLOT_PERSON_TAGS[slot]:
            if piece not in have:
                tags.append(piece)
        rec["tags"] = tags

    def flush() -> None:
        nonlocal group, group_feature
        if not group:
            return
        tagged: set[str] = set()
        unlabeled_sg: list[int] = []
        unlabeled_pl: list[int] = []
        for idx in group:
            rec = recovered[idx]
            if not isinstance(rec, dict):
                continue
            tags = [str(tag).lower().replace("_", "-") for tag in rec.get("tags") or []]
            slot, _feature, ambiguous = decode_tags(tags)
            if slot and not ambiguous:
                tagged.add(slot)
                continue
            if "singular" in tags:
                unlabeled_sg.append(idx)
            elif "plural" in tags:
                unlabeled_pl.append(idx)
        sg_needed = [slot for slot in ("1sg", "2sg", "3sg") if slot not in tagged]
        pl_needed = [slot for slot in ("1pl", "2pl", "3pl") if slot not in tagged]
        for idx, slot in zip(unlabeled_sg, sg_needed):
            rec = recovered[idx]
            if isinstance(rec, dict):
                inject(rec, slot)
        for idx, slot in zip(unlabeled_pl, pl_needed):
            rec = recovered[idx]
            if isinstance(rec, dict):
                inject(rec, slot)
        group = []
        group_feature = None

    for idx, rec in enumerate(recovered):
        if not isinstance(rec, dict):
            continue
        tags = [str(tag).lower().replace("_", "-") for tag in rec.get("tags") or []]
        if rec.get("source") != "conjugation":
            continue
        if "table-tags" in tags or "inflection-template" in tags:
            flush()
            continue
        if "infinitive" in tags or "gerund" in tags or "participle" in tags:
            flush()
            continue
        _slot, feature, _ambiguous = decode_tags(tags)
        if group and feature != group_feature:
            flush()
        group_feature = feature
        group.append(idx)
    flush()
    return recovered


def primary_conj_template(templates: object) -> tuple[str, str | None]:
    """Pick the lect-internal conj class and optional stem arg."""
    if not isinstance(templates, list):
        return "unknown", None
    candidates: list[dict[str, Any]] = []
    for item in templates:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        if not name or "conj" not in name.lower():
            continue
        if "table" in name.lower():
            continue
        candidates.append(item)
    if not candidates:
        return "unknown", None
    # Prefer the most specific template (longer name), then first listed.
    chosen = sorted(candidates, key=lambda item: (-len(str(item.get("name"))), str(item.get("name"))))[0]
    name = str(chosen.get("name"))
    args = chosen.get("args") if isinstance(chosen.get("args"), dict) else {}
    stem = None
    for key in ("1", "stem", "root", "base"):
        value = args.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            stem = text
            break
    return name, stem


def form_of_lemmas(sense: dict) -> list[str]:
    return sorted({
        str(item.get("word", "")).strip()
        for item in sense.get("form_of", [])
        if isinstance(item, dict) and item.get("word")
    })


def longest_common_prefix(strings: Iterable[str]) -> str:
    values = [value for value in strings if value]
    if not values:
        return ""
    prefix = values[0]
    for value in values[1:]:
        while prefix and not value.startswith(prefix):
            prefix = prefix[:-1]
        if not prefix:
            break
    return prefix


def row_forms(cells: dict[str, list[dict[str, Any]]]) -> dict[str, str]:
    """Pick one orthographic form per person slot."""
    out: dict[str, str] = {}
    for slot in PERSON_SLOTS:
        records = cells.get(slot) or []
        for record in records:
            form = str(record.get("form") or "").strip()
            if form and form != "-":
                out[slot] = form
                break
    return out


def is_complete_row(forms: dict[str, str]) -> bool:
    return all(forms.get(slot) for slot in PERSON_SLOTS)


def usable_stem(stem: str | None) -> str | None:
    """Reject Wiktionary template junk like `-/à` or `<+,ie>`."""
    if not stem:
        return None
    text = stem.strip()
    if not text:
        return None
    if any(ch in text for ch in "/<>+*{}[]"):
        return None
    if len(text) < 1:
        return None
    return text


def strip_endings(
    forms: dict[str, str],
    stem: str | None = None,
) -> tuple[dict[str, str], str, str] | None:
    """Return (endings, stem_used, stem_mode) for a complete or near-complete row."""
    occupied = [forms[slot] for slot in PERSON_SLOTS if forms.get(slot)]
    if len(occupied) < 4:
        return None
    # Periphrastic / compound cells ("habría librau") are not single suffixes.
    if any(" " in form for form in occupied):
        return None

    mode = "template"
    used = usable_stem(stem) or ""
    if not used:
        used = longest_common_prefix(occupied)
        mode = "lcp"
    if not used:
        return None

    endings: dict[str, str] = {}
    nonempty = 0
    for slot in PERSON_SLOTS:
        form = forms.get(slot)
        if not form:
            endings[slot] = "—"
            continue
        if not form.startswith(used):
            return None
        ending = form[len(used):]
        endings[slot] = ending if ending else "∅"
        if ending:
            nonempty += 1
    if nonempty < 4:
        return None
    return endings, used, mode


def score_lemma(features: dict[str, dict[str, list[dict[str, Any]]]]) -> tuple[int, int, int]:
    """Prefer lemmas with more complete 6-grids, especially present."""
    complete = 0
    present_bonus = 0
    classified = 0
    for feature, cells in features.items():
        forms = row_forms(cells)
        classified += sum(1 for slot in PERSON_SLOTS if forms.get(slot))
        if is_complete_row(forms):
            complete += 1
            if feature == "indicative.present":
                present_bonus = 1
    return (complete, present_bonus, classified)


def select_representatives(
    lemmas: dict[str, dict[str, Any]],
    *,
    class_source: str = "",
    limit: int = MAX_REPRESENTATIVES,
) -> list[str]:
    """Pick the fullest lemmas; keep a verb-named irregular class lemma."""
    ranked = sorted(
        lemmas.items(),
        key=lambda item: (score_lemma(item[1]["features"]), item[0]),
        reverse=True,
    )
    chosen: list[str] = []
    # e.g. ast-conj-ser → prefer lemma "ser" when present
    tail = class_source.rsplit("-", 1)[-1] if class_source else ""
    if tail and tail in lemmas:
        chosen.append(tail)
    for lemma, _meta in ranked:
        if lemma not in chosen:
            chosen.append(lemma)
        if len(chosen) >= limit:
            break
    return chosen


def aggregate_ending_inventory(
    lemmas: dict[str, dict[str, Any]],
    *,
    min_support: int = MIN_INVENTORY_SUPPORT,
) -> dict[str, dict[str, Any]]:
    """Majority orthographic endings per feature for one conj class."""
    by_feature: dict[str, list[tuple[tuple[str, ...], str, str]]] = defaultdict(list)
    for meta in lemmas.values():
        stem = meta.get("stem")
        for feature, cells in meta["features"].items():
            forms = row_forms(cells)
            if not is_complete_row(forms):
                continue
            stripped = strip_endings(forms, stem)
            if not stripped:
                continue
            endings, used, mode = stripped
            pattern = tuple(endings[slot] for slot in PERSON_SLOTS)
            by_feature[feature].append((pattern, used, mode))

    inventory: dict[str, dict[str, Any]] = {}
    for feature, rows in sorted(by_feature.items()):
        support_needed = 1 if len(lemmas) < min_support else min_support
        if len(rows) < support_needed:
            continue
        counts = Counter(pattern for pattern, _used, _mode in rows)
        pattern, support = counts.most_common(1)[0]
        modes = Counter(mode for _pattern, _used, mode in rows if _pattern == pattern)
        inventory[feature] = {
            "endings": {slot: pattern[index] for index, slot in enumerate(PERSON_SLOTS)},
            "support": support,
            "variants": len(counts),
            "stem_mode": modes.most_common(1)[0][0],
        }
    return inventory


def group_by_class(
    paradigms: dict[str, dict[str, dict[str, list[dict[str, Any]]]]],
    lemma_meta: dict[str, dict[str, Any]],
) -> dict[str, dict[str, dict[str, Any]]]:
    """class_source → lemma → {stem, features, source_url}."""
    grouped: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for lemma, features in paradigms.items():
        meta = lemma_meta.get(lemma, {})
        class_source = str(meta.get("class_source") or "unknown")
        grouped[class_source][lemma] = {
            "stem": meta.get("stem"),
            "source_url": meta.get("source_url") or "",
            "features": features,
        }
    return dict(grouped)


def wiktionary_url(word: str) -> str:
    return "https://en.wiktionary.org/wiki/" + quote(word.replace(" ", "_"))


def store_form(
    paradigms: dict,
    seen: set[tuple],
    counts: dict[str, int],
    *,
    lemma: str,
    form: str,
    tags: list[str],
    ipa: str,
    filename: str,
    source_url: str,
    source_kind: str,
) -> None:
    slot, feature, ambiguous = decode_tags(tags)
    text = form.strip()
    if not text:
        return
    cell_key = slot or "?"
    record_key = (lemma, feature, cell_key, text, tuple(tags))
    if record_key in seen:
        return
    seen.add(record_key)
    paradigms[lemma][feature][cell_key].append({
        "form": text,
        "ipa": ipa,
        "tags": tags,
        "source_file": filename,
        "source_url": source_url,
        "source_kind": source_kind,
        "ambiguous_slot": ambiguous,
    })
    if slot:
        counts["classified_cells"] += 1
    else:
        counts["unclassified_forms"] += 1


def harvest_kaikki_file(
    path: Any,
    *,
    filename: str,
    paradigms: dict,
    lemma_meta: dict[str, dict[str, Any]],
    counts: dict[str, int],
    seen: set[tuple],
) -> None:
    """Ingest one Kaikki JSONL into paradigms + lemma_meta."""
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entry = json_loads(line)
        except ValueError:
            continue
        if entry.get("pos") != "verb":
            continue
        word = str(entry.get("word") or "").strip()
        if not word:
            continue
        sounds = entry.get("sounds") or []
        ipa = next(
            (
                str(sound.get("ipa"))
                for sound in sounds
                if isinstance(sound, dict) and sound.get("ipa")
            ),
            "",
        )
        source_url = wiktionary_url(word)
        class_source, stem = primary_conj_template(entry.get("inflection_templates"))
        has_lemma_sense = any(
            isinstance(sense, dict) and not sense.get("form_of")
            for sense in entry.get("senses", [])
        )
        if has_lemma_sense:
            counts["verb_lemmas"] += 1
            meta = lemma_meta.setdefault(word, {
                "class_source": "unknown",
                "stem": None,
                "source_url": source_url,
            })
            if class_source != "unknown":
                meta["class_source"] = class_source
            if stem and not meta.get("stem"):
                meta["stem"] = stem
            meta["source_url"] = source_url
            raw_forms = [
                item for item in (entry.get("forms") or [])
                if isinstance(item, dict)
            ]
            for form_record in recover_conjugation_persons(raw_forms):
                tags = sorted(str(tag) for tag in form_record.get("tags", []))
                if "inflection-template" in tags or "table-tags" in tags:
                    continue
                form_text = str(form_record.get("form") or "")
                if "{{" in form_text:
                    continue
                source_kind = str(form_record.get("source") or "lemma-form")
                form_ipa = str(form_record.get("ipa") or ipa)
                store_form(
                    paradigms, seen, counts,
                    lemma=word,
                    form=form_text,
                    tags=tags,
                    ipa=form_ipa,
                    filename=filename,
                    source_url=source_url,
                    source_kind=source_kind,
                )
                if form_record.get("form"):
                    counts["inflected_forms"] += 1

        for sense in entry.get("senses", []):
            if not isinstance(sense, dict):
                continue
            lemmas = form_of_lemmas(sense)
            if not lemmas:
                continue
            tags = sorted({str(tag) for tag in sense.get("tags", [])})
            for lemma in lemmas:
                counts["form_of_entries"] += 1
                lemma_meta.setdefault(lemma, {
                    "class_source": "unknown",
                    "stem": None,
                    "source_url": wiktionary_url(lemma),
                })
                store_form(
                    paradigms, seen, counts,
                    lemma=lemma,
                    form=word,
                    tags=tags,
                    ipa=ipa,
                    filename=filename,
                    source_url=source_url,
                    source_kind="form-of-entry",
                )


def json_loads(text: str) -> dict[str, Any]:
    import json
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("expected object")
    return data


def paradigm_to_v1(
    lect: str,
    lemma: str,
    meta: dict[str, Any],
) -> dict[str, Any] | None:
    """Convert one harvested lemma into a vulgultra.conjugation.v1 paradigm."""
    cells: dict[str, dict[str, dict[str, Any]]] = {}
    for feature, slot_map in meta["features"].items():
        if feature.startswith("nonfinite.") or feature == "unclassified":
            continue
        row: dict[str, dict[str, Any]] = {}
        for slot in PERSON_SLOTS:
            forms = row_forms({slot: slot_map.get(slot, [])})
            form = forms.get(slot)
            if not form:
                continue
            record = next(
                (
                    item for item in slot_map.get(slot, [])
                    if str(item.get("form") or "").strip() == form
                ),
                {},
            )
            cell: dict[str, Any] = {
                "form": form,
                "phonemes": [],
                "source_label": ",".join(record.get("tags") or []),
                "source_url": record.get("source_url") or meta.get("source_url") or "",
            }
            if record.get("ipa"):
                cell["ipa"] = record["ipa"]
            row[slot] = cell
        if row:
            cells[feature] = row
    if not cells:
        return None
    return {
        "lect": lect,
        "lemma": lemma,
        "class_source": str(meta.get("class_source") or "unknown"),
        "regularity": "unknown",
        "source": {
            "attested": True,
            "title": f"Wiktionary:{lemma}",
            "url": meta.get("source_url") or wiktionary_url(lemma),
            "stem": meta.get("stem"),
        },
        "cells": cells,
    }


def build_lect_document(
    lect: str,
    grouped: dict[str, dict[str, dict[str, Any]]],
    *,
    max_paradigms_per_class: int = 40,
) -> dict[str, Any]:
    """Build a conjugation.v1 document with ending inventories in metadata.

    Inventories use the full lemma set. Serialized paradigms are capped per
    class (preferring complete six-slot rows) so large Kaikki dumps stay usable.
    """
    paradigms: list[dict[str, Any]] = []
    inventories: dict[str, dict[str, Any]] = {}
    total_lemmas = 0
    for class_source, lemmas in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        total_lemmas += len(lemmas)
        inventory = aggregate_ending_inventory(lemmas)
        if inventory:
            inventories[class_source] = inventory
        ranked = sorted(
            lemmas.items(),
            key=lambda item: (score_lemma(item[1]["features"]), item[0]),
            reverse=True,
        )
        kept = 0
        for lemma, meta in ranked:
            if kept >= max_paradigms_per_class:
                break
            packed = {
                "stem": meta.get("stem"),
                "source_url": meta.get("source_url"),
                "class_source": class_source,
                "features": meta["features"],
            }
            paradigm = paradigm_to_v1(lect, lemma, packed)
            if paradigm:
                paradigms.append(paradigm)
                kept += 1
    return {
        "schema": "vulgultra.conjugation.v1",
        "metadata": {
            "lect": lect,
            "purpose": "sourced Kaikki/Wiktextract conjugation harvest",
            "ending_inventories": inventories,
            "lemma_count": total_lemmas,
            "serialized_paradigms": len(paradigms),
            "max_paradigms_per_class": max_paradigms_per_class,
            "optimizer_involved": False,
        },
        "paradigms": paradigms,
    }
