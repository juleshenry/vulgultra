#!/usr/bin/env python3
"""Stem-first ending candidate report: 3×2 person tables per TAM.

Each harvested class is its own stem. Related stems are only hinted as a
bucket (a-theme, e-theme, …); their tables are never merged. Stem labels
are written `{ -ar }`. A cell is `-ending (lect)`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vulgultra.conjugation_harvest import (  # noqa: E402
    PERSON_SLOTS,
    aggregate_ending_inventory,
)
from vulgultra.romance_swadesh import SOURCE_LANGS  # noqa: E402

SOURCES = ROOT / "data" / "conjugation" / "sources"
DEFAULT_OUTPUT = ROOT / "docs" / "eval" / "verb_ending_candidates.md"
DEFAULT_IRREGULAR = ROOT / "docs" / "eval" / "verb_ending_candidates_irregular.md"
IRREGULAR_LINK = "verb_ending_candidates_irregular.md"

PERSONS = ("1", "2", "3")
NUMBERS = ("sg", "pl")
VOWELS = set(
    "aeiouàáâãäåæèéêëìíîïòóôõöùúûüýÿăâîøœ"
    "ɔɛəɨʌɐɒʊɪãõũĩỹǫɜɞɘɵɤɯɑæẽ"
)
BUCKET_ORDER = ("a-theme", "e-theme", "i-theme", "re", "esse", "stare", "habere", "other")
ESSE_STEMS = {
    "ser", "essere", "être", "esser", "fi",
    "ête", "étr", "éstr", "ièsi", "saite", "zer",
}
STARE_STEMS = {"estar", "stare"}
HABERE_STEMS = {
    "haber", "haber-ie", "haver", "avere", "avoir", "avè", "aver",
    "aveur", "avea",
    "avair", "aveir", "avar", "avoér", "avér", "avì", "avaer",
}
STEM_BUCKET: dict[str, str] = {
    "-ar": "a-theme", "-are": "a-theme", "-ari": "a-theme",
    "-â": "a-theme", "-à": "a-theme", "-å": "a-theme", "-a": "a-theme", "-ai": "a-theme",
    "-al": "a-theme", "-ur": "a-theme", "-ae": "a-theme", "-êr": "a-theme",
    "-er": "e-theme", "-ere": "e-theme", "-ēr": "e-theme", "-é": "e-theme",
    "-è": "e-theme", "-ea": "e-theme", "-e": "e-theme", "-el": "e-theme",
    "-tcher": "e-theme", "-djer": "e-theme",
    "-ir": "i-theme", "-ire": "i-theme", "-iri": "i-theme",
    "-î": "i-theme", "-ì": "i-theme", "-í": "i-theme", "-éi": "i-theme",
    "-i": "i-theme", "-air": "i-theme", "-yî": "i-theme", "-il": "i-theme",
    "-re": "re", "-ro": "re", "-r": "re", "-rr": "re", "-te": "re",
}

TAM_ORDER = [
    "indicative.present",
    "indicative.imperfect",
    "indicative.preterite",
    "indicative.past",
    "indicative.future",
    "indicative.pluperfect",
    "subjunctive.present",
    "subjunctive.imperfect",
    "subjunctive.past",
    "subjunctive.preterite",
    "subjunctive.future",
    "conditional",
    "conditional.present",
    "imperative",
]


_TEMPLATE_CONJ = re.compile(r"^[a-z]{2,4}-conj-(.+)$", re.I)
_EASTERN_CLASS = re.compile(r"^(IV|III|II|I)(?:-(.+))?$")
_EASTERN_PLAIN = {"I": "-a", "II": "-ea", "III": "-e", "IV": "-i"}
_EASTERN_INFIX = {"ez", "esc"}
_TEMPLATE_STEM = {
    "egl-conj-er1-Modena": "-ēr",
    "egl-conj-ir-Modena": "-ir",
    "egl-conj-er3-Modena": "-er",
    "wa-conj-er-T": "-er",
    "wa-conj-er-R": "-er",
    "wa-conj-er-K": "-er",
    "wa-conj-er-R-eye": "-er",
    "wa-conj-ner": "-er",
    "wa-conj-e": "-e",
    "wa-conj-i": "-i",
    "wa-conj-i-R": "-i",
    "wa-conj-yî": "-yî",
    "wa-conj-lére": "-re",
    "rgn-conj-first": "-êr",
    "rgn-conj-first-cons": "-êr",
    "rgn-conj-first-vow": "-êr",
    "rgn-conj-third-cons": "-ar",
    "rgn-conj-avér": "avér",
    "rgn-conj-vlér": "vlér",
}
_SIMPLE_ENDINGS = {
    "ar", "are", "ari", "er", "ere", "eri", "ir", "ire", "iri", "re", "air",
    "à", "è", "ì", "â", "ê", "î", "é", "í", "á", "å", "éi", "e", "i",
    "al", "el", "il", "ur", "ro", "ae", "rr", "êr", "ér",
}
_STEM_FROM_REST = re.compile(
    r"^(er|ir|re|ar|are|ere|ire|ari|iri|air|e|i)(?:[-0-9].*)?$",
    re.I,
)
_NAMED_STEM = re.compile(r"^[A-Za-zàèìòùâêîôûéíóúäöüåŷî]+$")


def surface_stem(class_source: str) -> str:
    """Strip provider tags to the unique infinitive stem.

    `lad-conj-ar` → `-ar`. `egl-conj-er1-Modena` → `-ēr`. `wa-conj-er-T` → `-er`.
    """
    raw = (class_source or "").strip() or "unknown"
    if raw in _TEMPLATE_STEM:
        return _TEMPLATE_STEM[raw]
    eastern = _EASTERN_CLASS.fullmatch(raw)
    if eastern:
        numeral, suffix = eastern.group(1), eastern.group(2)
        if suffix and suffix not in _EASTERN_INFIX:
            return suffix if suffix.startswith("-") else f"-{suffix}"
        return _EASTERN_PLAIN[numeral]
    match = _TEMPLATE_CONJ.match(raw)
    if not match:
        return raw
    rest = match.group(1)
    if "/" in rest or "auto" in rest.lower():
        return raw
    if rest.startswith("er1"):
        return "-ēr"
    if rest.startswith("er3"):
        return "-er"
    if rest.startswith("first"):
        return "-êr"
    if rest.startswith("third"):
        return "-ar"
    if rest in _SIMPLE_ENDINGS or rest.lower() in _SIMPLE_ENDINGS:
        return rest if rest.startswith("-") else f"-{rest}"
    chunk = _STEM_FROM_REST.match(rest)
    if chunk:
        ending = chunk.group(1)
        return ending if ending.startswith("-") else f"-{ending}"
    # Named irregulars: ast-conj-ser → ser, rgn-conj-avér → avér.
    if _NAMED_STEM.fullmatch(rest) and (
        rest.endswith("r")
        or rest in ESSE_STEMS
        or rest in STARE_STEMS
        or rest in HABERE_STEMS
    ):
        return rest
    return raw


def brace(stem: str) -> str:
    return "{ " + stem + " }"


def stem_anchor(stem: str) -> str:
    return "s-" + stem.replace(" ", "-").replace("/", "-")


def stem_link(stem: str) -> str:
    return f"[{brace(stem)}](#{stem_anchor(stem)})"


def bucket_of(stem: str) -> str:
    if stem in ESSE_STEMS:
        return "esse"
    if stem in STARE_STEMS:
        return "stare"
    if stem in HABERE_STEMS:
        return "habere"
    if stem in STEM_BUCKET:
        return STEM_BUCKET[stem]
    if not (stem.startswith("-") or stem[:1].isupper() or "conj" in stem):
        return "other"
    tail = stem.rsplit("-", 1)[-1].lower()
    if tail in {"ar", "are", "ari", "al", "ur", "ae", "êr"}:
        return "a-theme"
    if tail in {"er", "ere", "eri", "el", "tcher", "djer"}:
        return "e-theme"
    if tail in {"ir", "ire", "iri", "il"}:
        return "i-theme"
    if tail in {"re", "ro", "rr", "r", "te"}:
        return "re"
    return "other"


def stem_sort_key(name: str) -> tuple:
    bucket = bucket_of(name)
    return (BUCKET_ORDER.index(bucket), name.casefold())


def ending_syllables(ending: str) -> int:
    """Vowel groups in the suffix. ∅ and C-only are 0."""
    if ending in {"∅", ""}:
        return 0
    nfd = unicodedata.normalize("NFD", ending.casefold())
    letters = "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")
    count = 0
    in_vowel = False
    for ch in letters:
        vowel = ch in VOWELS
        if vowel and not in_vowel:
            count += 1
        in_vowel = vowel
    return count


def shortest_slot_map(slot_map: dict) -> dict:
    """Keep only the endings at the lowest syllable count in each cell."""
    out: dict = {}
    for slot, endings in slot_map.items():
        if not endings:
            continue
        best = min(ending_syllables(ending) for ending in endings)
        out[slot] = {
            ending: node
            for ending, node in endings.items()
            if ending_syllables(ending) == best
        }
    return out


def md_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def show_ending(ending: str) -> str:
    if ending in {"∅", ""}:
        return "∅"
    if ending.startswith("-"):
        return ending
    return f"-{ending}"


def format_sources(sources: list[tuple[str, str, int]]) -> str:
    """`-ar (es, pt) -are (it)` — class label, then the lects that use it."""
    lects_by_class: dict[str, list[str]] = {}
    for lect, class_source, _support in sources:
        bucket = lects_by_class.setdefault(class_source, [])
        if lect not in bucket:
            bucket.append(lect)
    parts = []
    for class_source in sorted(lects_by_class, key=stem_sort_key):
        lects = [code for code in SOURCE_LANGS if code in lects_by_class[class_source]]
        lects.extend(code for code in lects_by_class[class_source] if code not in lects)
        parts.append(f"{brace(class_source)} ({', '.join(lects)})")
    return " ".join(parts)


def format_cell(endings: dict) -> str:
    """`-o (es, pt) -i (oc, gsc)` grouped by ending, lects in source order."""
    if not endings:
        return "—"
    groups: list[tuple[str, list[str]]] = []
    for ending, node in endings.items():
        lects = []
        for lect, _cls, _sup in node["sources"]:
            if lect not in lects:
                lects.append(lect)
        lects = [code for code in SOURCE_LANGS if code in lects] or lects
        groups.append((ending, lects))
    groups.sort(key=lambda item: (
        min(SOURCE_LANGS.index(code) if code in SOURCE_LANGS else 99 for code in item[1]),
        item[0],
    ))
    return " ".join(
        f"{show_ending(ending)} ({', '.join(lects)})"
        for ending, lects in groups
    )


# lect → class → feature → {endings, support, stem_mode, source}
Inventory = dict[str, dict[str, dict[str, dict]]]


def _row_forms(row: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    for slot in PERSON_SLOTS:
        cell = row.get(slot)
        if isinstance(cell, dict):
            form = cell.get("form")
            if form:
                out[slot] = str(form)
    return out


def inventory_from_paradigms(paradigms: list[dict]) -> dict[str, dict[str, dict]]:
    """Majority endings from serialized paradigms when metadata is empty."""
    grouped: dict[str, dict[str, dict]] = defaultdict(dict)
    # Rebuild the harvest-style lemma map class → lemma → features.
    by_class: dict[str, dict[str, dict]] = defaultdict(dict)
    for paradigm in paradigms:
        lemma = str(paradigm.get("lemma") or "").strip()
        if not lemma:
            continue
        class_source = str(paradigm.get("class_source") or "unknown")
        stem = None
        source = paradigm.get("source")
        if isinstance(source, dict):
            stem = source.get("stem")
        features: dict[str, dict[str, list]] = {}
        cells = paradigm.get("cells") or {}
        for feature, row in cells.items():
            if not isinstance(row, dict):
                continue
            forms = _row_forms(row)
            packed = {
                slot: [{"form": form, "ipa": "", "tags": []}]
                for slot, form in forms.items()
            }
            features[str(feature)] = packed
        if not features:
            continue
        by_class[class_source][lemma] = {
            "stem": stem,
            "features": features,
            "source_url": "",
        }
    for class_source, lemmas in by_class.items():
        grouped[class_source] = aggregate_ending_inventory(lemmas, min_support=1)
    return grouped


def load_inventories() -> tuple[Inventory, dict[str, str]]:
    """Load metadata inventories; fall back to paradigm majority for empty lects."""
    inventories: Inventory = {}
    notes: dict[str, str] = {}
    for lect in SOURCE_LANGS:
        path = SOURCES / f"{lect}.json"
        if not path.is_file():
            notes[lect] = "no source JSON"
            continue
        document = json.loads(path.read_text(encoding="utf-8"))
        meta = document.get("metadata") or {}
        inv = dict(meta.get("ending_inventories") or {})
        source = "metadata.ending_inventories"
        para = inventory_from_paradigms(document.get("paradigms") or [])
        if not inv:
            inv = para
            source = "majority from serialized paradigms (metadata empty)"
        else:
            # Thin complete classes (e.g. dlm -ur) can miss the metadata
            # majority cut and still belong in the candidate tables.
            for class_source, features in para.items():
                if class_source not in inv:
                    inv[class_source] = features
                    source = "metadata.ending_inventories plus paradigm majority"
        if not inv:
            notes[lect] = "no stripable 6-grid"
            continue
        inventories[lect] = {}
        for class_source, features in inv.items():
            packed: dict[str, dict] = {}
            for feature, payload in features.items():
                endings = (payload or {}).get("endings") or {}
                if not endings:
                    continue
                packed[feature] = {
                    "endings": {
                        slot: str(endings[slot])
                        for slot in PERSON_SLOTS
                        if slot in endings
                    },
                    "support": int((payload or {}).get("support") or 0),
                    "stem_mode": str((payload or {}).get("stem_mode") or ""),
                    "source": source,
                }
            if packed:
                stem = surface_stem(class_source)
                if stem in inventories[lect]:
                    dest = inventories[lect][stem]
                    for feature, payload in packed.items():
                        old = dest.get(feature)
                        if old is None or payload["support"] > old["support"]:
                            dest[feature] = payload
                else:
                    inventories[lect][stem] = packed
        if not inventories[lect]:
            notes[lect] = "no stripable 6-grid"
            inventories.pop(lect)
            continue
        notes[lect] = source
    return inventories, notes


def collect_candidates(inventories: Inventory) -> dict:
    """class → feature → slot → ending → {support, sources}."""
    tree: dict = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {
            "support": 0,
            "sources": [],
        })))
    )
    for lect, classes in inventories.items():
        for class_source, features in classes.items():
            for feature, payload in features.items():
                for slot, ending in payload["endings"].items():
                    if ending in {"—", ""}:
                        continue
                    node = tree[class_source][feature][slot][ending]
                    node["support"] += payload["support"]
                    node["sources"].append((lect, class_source, payload["support"]))
    return tree


def lects_for(inventories: Inventory, stem: str) -> list[str]:
    return [lect for lect in SOURCE_LANGS if stem in (inventories.get(lect) or {})]


def stem_lects(inventories: Inventory, class_source: str) -> str:
    sources = [
        (lect, class_source, 0)
        for lect in lects_for(inventories, class_source)
    ]
    return format_sources(sources) or "—"


def index_tables(inventories: Inventory, stems: list[str]) -> list[str]:
    lines = ["# index", ""]
    for bucket in BUCKET_ORDER:
        members = [stem for stem in stems if bucket_of(stem) == bucket]
        if not members:
            continue
        if bucket == "other":
            continue
        lines.extend([
            f"## {bucket}",
            "",
            "| stem | lects |",
            "|---|---|",
        ])
        for stem in members:
            lects = ", ".join(lects_for(inventories, stem)) or "—"
            lines.append(f"| {stem_link(stem)} | {lects} |")
        lines.append("")
    lines.extend([
        "## other",
        "",
        f"[other irregulars]({IRREGULAR_LINK}) — present 6-grid dump, not esse / stare / habere.",
        "",
    ])
    return lines


def other_irregulars_table(
    inventories: Inventory,
    tree: dict,
    stems: list[str],
) -> list[str]:
    """Present 6-grid only. These stems do not get per-TAM analysis."""
    members = [stem for stem in stems if bucket_of(stem) == "other"]
    if not members:
        return []
    lines = [
        "# other irregulars",
        "",
        "Dump of harvested irregulars that are not esse / stare / habere.",
        "Present indicative 6-grid only. Analyzed stems live in",
        f"[verb_ending_candidates.md]({DEFAULT_OUTPUT.name}).",
        "",
        "| stem | lects | 1sg | 2sg | 3sg | 1pl | 2pl | 3pl |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for stem in members:
        features = tree[stem]
        slot_map = features.get("indicative.present") or {}
        lects = ", ".join(lects_for(inventories, stem)) or "—"
        cells = [
            md_cell(format_cell(slot_map.get(slot) or {}))
            for slot in PERSON_SLOTS
        ]
        lines.append(f"| {brace(stem)} | {lects} | " + " | ".join(cells) + " |")
    lines.append("")
    return lines


def person_table(slot_map: dict) -> list[str]:
    """3×2 (person × number) table. Each cell is `-ending (lect, lect)`."""
    lines = [
        "| | sg | pl |",
        "|---|---|---|",
    ]
    for person in PERSONS:
        cells = []
        for number in NUMBERS:
            slot = f"{person}{number}"
            cells.append(md_cell(format_cell(slot_map.get(slot) or {})))
        lines.append(f"| **{person}** | {cells[0]} | {cells[1]} |")
    return lines


def render(inventories: Inventory) -> str:
    tree = collect_candidates(inventories)
    stems = sorted(tree, key=stem_sort_key)
    lines: list[str] = index_tables(inventories, stems)
    analyzed = [stem for stem in stems if bucket_of(stem) != "other"]
    for class_source in analyzed:
        features = tree[class_source]
        tams = [name for name in TAM_ORDER if name in features]
        extra_tams = sorted(name for name in features if name not in TAM_ORDER)
        bucket = bucket_of(class_source)
        lines.extend([
            f'<a id="{stem_anchor(class_source)}"></a>',
            f"# {brace(class_source)}",
            "",
            f"[{bucket}](#{bucket})",
            "",
            stem_lects(inventories, class_source),
            "",
        ])
        for feature in tams + extra_tams:
            lines.extend([
                f"## {feature}",
                "",
            ])
            slot_map = features[feature]
            lines.extend(person_table(slot_map))
            lines.extend([
                "",
                "lowest syllable",
                "",
            ])
            lines.extend(person_table(shortest_slot_map(slot_map)))
            lines.append("")
    missing = [lect for lect in SOURCE_LANGS if lect not in inventories]
    if missing:
        lines.extend([
            "# missing",
            "",
            " ".join(f"{lect}" for lect in missing),
            "",
        ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--irregular-output", type=Path, default=DEFAULT_IRREGULAR)
    args = parser.parse_args()
    inventories, _notes = load_inventories()
    tree = collect_candidates(inventories)
    stems = sorted(tree, key=stem_sort_key)
    text = render(inventories)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    irregular = "\n".join(other_irregulars_table(inventories, tree, stems))
    args.irregular_output.write_text(irregular, encoding="utf-8")
    print(f"wrote {args.output} ({len(text):,} chars)")
    print(f"wrote {args.irregular_output} ({len(irregular):,} chars)")
    print(f"  lects: {len(inventories)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
