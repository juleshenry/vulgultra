#!/usr/bin/env python3
"""Build lect-internal conjugation pages and a vulgultra.conjugation.v1 corpus.

Pages are organized by each lect's own conjugation classes. Each class shows
a sourced orthographic ending inventory (6-person grids) plus a few
representative lemmas. Gaps stay explicit. Hand-authored optimizer templates
are never presented as Wiktionary evidence.
"""

from __future__ import annotations

from collections import defaultdict
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vulgultra.conjugation_harvest import (  # noqa: E402
    MAX_REPRESENTATIVES,
    PERSON_SLOTS,
    aggregate_ending_inventory,
    build_lect_document,
    group_by_class,
    harvest_kaikki_file,
    is_complete_row,
    row_forms,
    select_representatives,
)
from vulgultra.romance_swadesh import LECT_NAMES, SOURCE_LANGS  # noqa: E402
from vulgultra.verbix import LECT_CONFIG as VERBIX_LECTS  # noqa: E402
from vulgultra.verbix import normalize_class as normalize_verbix_class  # noqa: E402

WORDS = ROOT / "data" / "words"
OUT_PAGES = ROOT / "docs" / "conjugations"
OUT_JSON = ROOT / "data" / "conjugation" / "sources"
MANIFEST = ROOT / "data" / "conjugation" / "source_manifest.json"

DIRECT_FILES = {
    "an": ["kaikki-an.jsonl"],
    "ast": ["kaikki-ast.jsonl"],
    "ca": ["kaikki-ca.jsonl"],
    "co": ["kaikki-co.jsonl", "kaikki-co-fr.jsonl"],
    "dlm": ["kaikki-dlm.jsonl"],
    "eml": ["kaikki-eml.jsonl"],
    "es": ["kaikki-es.jsonl"],
    "fr": ["kaikki-fr.jsonl"],
    "fur": ["kaikki-fur.jsonl"],
    "gl": ["kaikki-gl.jsonl"],
    "glw": ["kaikki-glw.jsonl"],
    "ist": ["kaikki-ist.jsonl"],
    "it": ["kaikki-it.jsonl"],
    "lad": ["kaikki-lad.jsonl"],
    "lij": ["kaikki-lij.jsonl"],
    "lld": ["kaikki-lld.jsonl"],
    "lmo": ["kaikki-lmo.jsonl"],
    "mwl": ["kaikki-mwl.jsonl"],
    "nap": ["kaikki-nap.jsonl"],
    "nrf": ["kaikki-nrf.jsonl"],
    "oc": ["kaikki-oc.jsonl"],
    "pms": ["kaikki-pms.jsonl"],
    "pt": ["kaikki-pt.jsonl"],
    "rgn": ["kaikki-rgn.jsonl"],
    "rm": ["kaikki-rm.jsonl"],
    "ro": ["kaikki-ro.jsonl"],
    "rup": ["kaikki-rup.jsonl"],
    "sc": ["kaikki-sc.jsonl"],
    "scn": ["kaikki-scn.jsonl"],
    "vec": ["kaikki-vec.jsonl"],
    "wa": ["kaikki-wa.jsonl"],
}

# Lects whose Kaikki/Wiktionary class tags should collapse to infinitive endings.
ENDING_NORMALIZE_LECTS = set(VERBIX_LECTS) | {
    "es", "pt", "gl", "ca", "fr", "it", "ro", "an", "ast", "mwl", "oc",
}


def markdown_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def section_heading(class_source: str) -> str:
    """Page is already per-lect; label the paradigm cue, not 'Class'."""
    if class_source.startswith("-"):
        return f"## Ending: `{class_source}`"
    if class_source in {"unknown", "other", "ext-unparsed"}:
        return f"## `{class_source}`"
    # Eastern Romance conjugations: I, I-ez, II, III, IV, IV-esc, I-å, …
    if class_source in {"I", "II", "III", "IV", "fi"} or class_source.startswith(
        ("I-", "II-", "III-", "IV-", "I.", "II.", "III.", "IV.")
    ):
        return f"## Conjugation: `{class_source}`"
    if "conj" in class_source or class_source.startswith(("ast-", "scn-", "an-", "oc-", "egl-", "lmo-")):
        return f"## `{class_source}`"
    return f"## Irregular: `{class_source}`"


def collect_kaikki(lect: str) -> tuple[dict, dict, list[str], dict[str, int]]:
    paradigms: dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    lemma_meta: dict = {}
    input_files = [name for name in DIRECT_FILES.get(lect, []) if (WORDS / name).is_file()]
    counts = {
        "verb_lemmas": 0,
        "inflected_forms": 0,
        "form_of_entries": 0,
        "classified_cells": 0,
        "unclassified_forms": 0,
    }
    seen: set[tuple] = set()
    for filename in input_files:
        harvest_kaikki_file(
            WORDS / filename,
            filename=filename,
            paradigms=paradigms,
            lemma_meta=lemma_meta,
            counts=counts,
            seen=seen,
        )
    return paradigms, lemma_meta, input_files, counts


def collect_extremaduran() -> tuple[dict, dict, list[str], dict[str, int]]:
    folder = ROOT / "vendor" / "recursos_es-ext" / "Conjugacion verbos"
    paradigms: dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    lemma_meta: dict = {}
    sources: list[str] = []
    count = 0
    if folder.is_dir():
        for path in sorted(folder.glob("*.ext.txt")):
            sources.append(str(path.relative_to(ROOT)))
            lemma = path.name[:-8]
            text = path.read_text(encoding="utf-8", errors="replace").strip()
            if text:
                paradigms[lemma]["source-layout.unparsed"]["?"] = [{
                    "form": text,
                    "ipa": "",
                    "tags": [],
                    "source_file": str(path.relative_to(ROOT)),
                    "source_url": "",
                    "ambiguous_slot": True,
                    "raw_block": True,
                }]
                lemma_meta[lemma] = {
                    "class_source": "ext-unparsed",
                    "stem": None,
                    "source_url": "",
                }
                count += 1
    return paradigms, lemma_meta, sources, {"raw_tables": count, "classified_cells": 0}


def normalize_ending_classes(lect: str, lemma_meta: dict) -> None:
    """Collapse provider tags into infinitive endings (+ irregulars)."""
    if lect not in ENDING_NORMALIZE_LECTS:
        return
    for lemma, meta in lemma_meta.items():
        meta["class_source"] = normalize_verbix_class(
            lect, lemma, meta.get("class_source"),
        )


def merge_conjugation_json(
    lect: str,
    paradigms: dict,
    lemma_meta: dict,
    counts: dict[str, int],
    files: list[str],
    path: Path,
    *,
    source_tag: str,
    normalize: bool = True,
) -> int:
    """Merge a vulgultra.conjugation.v1 file into the in-memory harvest."""
    if not path.is_file():
        return 0
    document = json.loads(path.read_text(encoding="utf-8"))
    added = 0
    source_name = path.name
    for paradigm in document.get("paradigms") or []:
        lemma = str(paradigm.get("lemma") or "").strip()
        if not lemma:
            continue
        source = paradigm.get("source") if isinstance(paradigm.get("source"), dict) else {}
        page_url = str(source.get("url") or "")
        attested = bool(source.get("attested", True))
        class_source = str(paradigm.get("class_source") or "unknown")
        meta = lemma_meta.setdefault(lemma, {
            "class_source": class_source,
            "stem": None,
            "source_url": page_url,
        })
        if meta.get("class_source") in {None, "", "unknown"}:
            meta["class_source"] = class_source
        if normalize and lect in ENDING_NORMALIZE_LECTS:
            meta["class_source"] = normalize_verbix_class(
                lect, lemma, meta.get("class_source"),
            )
        elif class_source and meta.get("class_source") in {None, "", "unknown"}:
            meta["class_source"] = class_source
        else:
            # Prefer explicit class from this document for hand corpora.
            if class_source not in {"", "unknown"}:
                meta["class_source"] = class_source
        if page_url and not meta.get("source_url"):
            meta["source_url"] = page_url
        for feature, row in (paradigm.get("cells") or {}).items():
            if not isinstance(row, dict):
                continue
            for slot, cell in row.items():
                if slot not in PERSON_SLOTS or not isinstance(cell, dict):
                    continue
                form = str(cell.get("form") or "").strip()
                if not form:
                    continue
                existing = paradigms[lemma][feature].get(slot) or []
                if any(str(item.get("form") or "").strip() == form for item in existing):
                    continue
                record = {
                    "form": form,
                    "ipa": "",
                    "tags": [feature.replace(".", ", "), source_tag],
                    "source_file": source_name,
                    "source_url": page_url,
                    "source_kind": (
                        f"{source_tag}-attested" if attested else f"{source_tag}-generated"
                    ),
                    "ambiguous_slot": False,
                }
                if existing:
                    paradigms[lemma][feature][slot].append(record)
                else:
                    paradigms[lemma][feature][slot] = [record]
                    counts["classified_cells"] += 1
                    added += 1
    if source_name not in files:
        files.append(source_name)
    return added


def merge_verbix(
    lect: str,
    paradigms: dict,
    lemma_meta: dict,
    counts: dict[str, int],
    files: list[str],
) -> bool:
    """Merge `{lect}_verbix.json` into paradigms. Returns True if merged."""
    path = OUT_JSON / f"{lect}_verbix.json"
    added = merge_conjugation_json(
        lect, paradigms, lemma_meta, counts, files, path,
        source_tag="verbix",
        normalize=True,
    )
    counts["verbix_slots_added"] = added
    return added > 0 or path.is_file()


def source_paradigms(lect: str) -> tuple[dict, dict, list[str], dict[str, int], str]:
    if lect == "ext":
        paradigms, lemma_meta, files, counts = collect_extremaduran()
        note = "local Extremenho and Spanish comparison tables; raw layout preserved"
        return paradigms, lemma_meta, files, counts, note
    paradigms, lemma_meta, files, counts = collect_kaikki(lect)
    note = "Wiktionary/Wiktextract form-of entries" if files else "none currently collected locally"
    merged = merge_verbix(lect, paradigms, lemma_meta, counts, files)
    # Hand / site corpora (e.g. Picard Chés Diseux).
    extra = OUT_JSON / f"{lect}_diseux.json"
    diseux_added = merge_conjugation_json(
        lect, paradigms, lemma_meta, counts, files, extra,
        source_tag="diseux",
        normalize=False,
    )
    normalize_ending_classes(lect, lemma_meta)
    bits = []
    if any(name.startswith("kaikki-") for name in files):
        bits.append("Wiktionary/Wiktextract form-of entries")
    if merged:
        bits.append("Verbix (CC BY-NC 3.0; https://www.verbix.com)")
    if diseux_added or extra.is_file():
        if lect == "pcd":
            bits.append("Chés Diseux d'Achteure (http://ches.diseux.free.fr/conj/)")
        elif lect == "ruo":
            bits.append(
                "Verbix Istro-Romanian docs "
                "(https://docs.verbix.com/Languages/Istroromanian)"
            )
        elif lect == "ruq":
            bits.append(
                "Capidan 1925 / Romance Verbal Inflection Dataset 2.0 "
                "(Oxford ODRVM; GPLv3)"
            )
        else:
            bits.append(f"local `{extra.name}` corpus")
    if bits:
        note = " plus ".join(bits)
    return paradigms, lemma_meta, files, counts, note


def feature_full_grid_count(lemmas: dict[str, dict]) -> int:
    features_with_full = set()
    for meta in lemmas.values():
        for feature, cells in meta["features"].items():
            if is_complete_row(row_forms(cells)):
                features_with_full.add(feature)
    return len(features_with_full)


def has_classified_finite(lemmas: dict[str, dict]) -> bool:
    for meta in lemmas.values():
        for feature, cells in meta["features"].items():
            if feature.startswith("nonfinite.") or feature == "unclassified":
                continue
            if feature.startswith("source-layout"):
                continue
            if any(row_forms(cells).values()):
                return True
    return False


def render_ending_table(inventory: dict[str, dict]) -> list[str]:
    lines = [
        "### Person-slot inventory",
        "",
        "Orthographic suffixes stripped from complete six-slot rows. "
        "`∅` is an empty suffix; `—` marks a missing slot in a partial pattern.",
        "",
        "| Feature | Support | Mode | 1sg | 2sg | 3sg | 1pl | 2pl | 3pl |",
        "|---|---:|---|---|---|---|---|---|---|",
    ]
    for feature, info in sorted(inventory.items()):
        endings = info["endings"]
        display = []
        for slot in PERSON_SLOTS:
            value = endings[slot]
            if value in {"—", "∅"}:
                display.append(value)
            else:
                display.append(f"-{markdown_escape(value)}")
        lines.append(
            f"| `{feature}` | {info['support']} | `{info['stem_mode']}` | "
            + " | ".join(display)
            + " |"
        )
    lines.append("")
    return lines


def render_representative(
    lemma: str,
    meta: dict,
) -> list[str]:
    lines = [f"#### `{lemma}`", ""]
    stem = meta.get("stem")
    if stem:
        lines.append(f"Stem: `{stem}`.")
        lines.append("")
    features = meta["features"]
    finite = []
    for feature, cells in features.items():
        if feature.startswith("nonfinite.") or feature in {"unclassified"}:
            continue
        if feature.startswith("source-layout"):
            continue
        if not any(row_forms(cells).values()):
            continue
        finite.append((feature, cells))
    finite.sort(
        key=lambda item: (
            0 if item[0] == "indicative.present" else 1,
            0 if is_complete_row(row_forms(item[1])) else 1,
            item[0],
        ),
    )
    shown = 0
    for feature, cells in finite:
        lines.extend([
            f"##### `{feature}`",
            "",
            "| Slot | Form |",
            "|---|---|",
        ])
        for slot in PERSON_SLOTS:
            records = cells.get(slot) or []
            if not records:
                lines.append(f"| `{slot}` | — |")
                continue
            record = next(
                (item for item in records if str(item.get("form") or "").strip() not in {"", "-"}),
                records[0],
            )
            form = markdown_escape(str(record.get("form") or "—"))
            lines.append(f"| `{slot}` | {form} |")
        lines.append("")
        shown += 1
        if shown >= 8:
            remaining = len(finite) - shown
            if remaining > 0:
                lines.append(f"_…{remaining} more tense/mood rows in the JSON corpus._")
                lines.append("")
            break
    if shown == 0:
        lines.append("_No classified person-number cells for this lemma._")
        lines.append("")
    return lines


def render_page(
    lect: str,
    paradigms: dict,
    lemma_meta: dict,
    files: list[str],
    counts: dict[str, int],
    source_note: str,
) -> str:
    name = LECT_NAMES.get(lect, lect)
    lines = [
        f"# {name} (`{lect}`) conjugation data",
        "",
        "> Source-observed forms from the local corpus. Empty cells are data gaps.",
        "> Pages are organized by this lect's own conjugation classes. Class labels",
        "> are not aligned across lects.",
        "",
        f"- Source set: {source_note if files else 'none currently collected locally'}",
        f"- Source files: {', '.join(f'`{file}`' for file in files) if files else 'none'}",
        f"- Lemmas with forms: **{len(paradigms)}**",
        f"- Verb lemma entries: **{counts.get('verb_lemmas', 0)}**",
        f"- Inflected form records: **{counts.get('inflected_forms', counts.get('raw_tables', 0))}**",
        f"- Separate form-of entries: **{counts.get('form_of_entries', 0)}**",
        f"- Classified person-slot observations: **{counts.get('classified_cells', 0)}**",
        "",
        "Person slots: `1sg`, `2sg`, `3sg`, `1pl`, `2pl`, `3pl`.",
        "",
    ]
    if not paradigms:
        lines.extend([
            "## Collection status",
            "",
            "No local form-of conjugation corpus is currently available for this lect.",
            "The repository's optimizer template is intentionally not presented as",
            "a sourced conjugation paradigm. Add source-backed data to populate this page.",
            "",
        ])
        return "\n".join(lines)

    if lect == "ext":
        lines.extend([
            "## Raw local tables",
            "",
            "Extremaduran sources are flattened text without stable six-slot labels.",
            f"Stored raw tables: **{counts.get('raw_tables', 0)}**.",
            "",
        ])
        return "\n".join(lines)

    grouped = group_by_class(paradigms, lemma_meta)
    rich = []
    sparse = []
    for class_source, lemmas in grouped.items():
        inventory = aggregate_ending_inventory(lemmas)
        full_features = feature_full_grid_count(lemmas)
        bucket = (class_source, lemmas, inventory, full_features)
        # Show representatives whenever person slots exist, even if no row is
        # complete enough for an ending inventory (common in thin Kaikki dumps).
        if inventory or full_features or has_classified_finite(lemmas):
            rich.append(bucket)
        else:
            sparse.append(bucket)
    # Prefer classes with ending inventories, then fuller grids, then size.
    rich.sort(key=lambda item: (-len(item[2]), -item[3], -len(item[1]), item[0]))
    sparse.sort(key=lambda item: (-len(item[1]), item[0]))

    lines.extend([
        "## Coverage by ending",
        "",
        "| Ending / paradigm | Lemmas | Features with a full 6-grid | Inventories |",
        "|---|---:|---:|---:|",
    ])
    for class_source, lemmas, inventory, full_features in rich + sparse:
        lines.append(
            f"| `{class_source}` | {len(lemmas)} | {full_features} | {len(inventory)} |"
        )
    lines.append("")

    for class_source, lemmas, inventory, _full in rich:
        lines.extend([section_heading(class_source), ""])
        stems = sorted({str(meta.get("stem")) for meta in lemmas.values() if meta.get("stem")})
        if stems[:5]:
            sample = ", ".join(f"`{stem}`" for stem in stems[:5])
            extra = f" (+{len(stems) - 5} more)" if len(stems) > 5 else ""
            lines.append(f"Template stem args observed: {sample}{extra}.")
            lines.append("")
        if inventory:
            lines.extend(render_ending_table(inventory))
        else:
            lines.extend([
                "### Person-slot inventory",
                "",
                "No majority ending pattern with enough complete six-slot rows yet.",
                "",
            ])
        reps = select_representatives(
            lemmas, class_source=class_source, limit=MAX_REPRESENTATIVES,
        )
        lines.extend(["### Representative lemmas", ""])
        for lemma in reps:
            lines.extend(render_representative(lemma, lemmas[lemma]))

    if sparse:
        lines.extend([
            "## Sparse / unclassified",
            "",
            "Paradigms without a full six-slot inventory (count only).",
            "",
            "| Ending / paradigm | Lemmas |",
            "|---|---:|",
        ])
        for class_source, lemmas, _inventory, _full in sparse:
            lines.append(f"| `{class_source}` | {len(lemmas)} |")
        lines.append("")

    return "\n".join(lines)


def update_manifest(sourced_lects: set[str]) -> None:
    if not MANIFEST.is_file():
        return
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in data.get("lects", []):
        lect = item.get("lect")
        if lect in sourced_lects:
            item["status"] = "harvested"
            item["source"] = "data/conjugation/sources/" + f"{lect}.json"
        elif lect == "ext":
            item["status"] = "raw-unaligned"
        # leave other pending
    MANIFEST.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    OUT_PAGES.mkdir(parents=True, exist_ok=True)
    OUT_JSON.mkdir(parents=True, exist_ok=True)
    index = [
        "# Conjugation data by lect",
        "",
        "Each linked page is organized by that lect's own conjugation classes.",
        "Pages show sourced six-slot ending inventories and a few representative",
        "lemmas. They do not copy sister-lect forms or substitute the optimizer's",
        "hand-built ending templates. Normalized JSON lives under",
        "`data/conjugation/sources/`.",
        "",
        "| Lect | Name | Classes w/ inventory | Lemmas | Classified slots |",
        "|---|---|---:|---:|---:|",
    ]
    sourced: set[str] = set()
    for lect in SOURCE_LANGS:
        paradigms, lemma_meta, files, counts, note = source_paradigms(lect)
        page = render_page(lect, paradigms, lemma_meta, files, counts, note)
        (OUT_PAGES / f"{lect}.md").write_text(page, encoding="utf-8")

        inventory_classes = 0
        lemma_count = len(paradigms)
        if files and lect != "ext":
            grouped = group_by_class(paradigms, lemma_meta)
            document = build_lect_document(lect, grouped)
            (OUT_JSON / f"{lect}.json").write_text(
                json.dumps(document, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            inventory_classes = len(document["metadata"].get("ending_inventories") or {})
            if document["paradigms"]:
                sourced.add(lect)
        elif lect == "ext" and files:
            # Keep ext out of the normalized six-slot corpus until aligned.
            pass

        if files:
            index.append(
                f"| [`{lect}`]({lect}.md) | {LECT_NAMES.get(lect, lect)} | "
                f"{inventory_classes} | {lemma_count} | {counts.get('classified_cells', 0)} |"
            )
        else:
            index.append(
                f"| [`{lect}`]({lect}.md) | {LECT_NAMES.get(lect, lect)} | — | — | not yet sourced |"
            )

    (OUT_PAGES / "README.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    update_manifest(sourced)
    print(f"wrote {len(SOURCE_LANGS)} lect pages to {OUT_PAGES}")
    print(f"wrote {len(sourced)} conjugation JSON files to {OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
