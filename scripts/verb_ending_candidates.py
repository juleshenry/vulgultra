#!/usr/bin/env python3
"""Verb ending shortlist: every lect's regular endings, per theme × TAM × person.

Regular only. Each lect-class contributes the six-ending row that the most
lemmas of that class share (`metadata.ending_inventories`, built over the
full lemma set, inchoative infix already moved into the stem). Its support
is the number of verbs that follow that row. Classes are pooled by their
Latin conjugation (a/e/i/re theme), not by the spelling of the infinitive:
French `-er` and Piedmontese `-é` are Latin -ARE, so a-theme.

Nothing is dropped for length: 2σ endings (`-amos`) compete whole. σ is the
ending read as Vulgultra orthography after repair (glide formation), which
is how the optimizer reads an ending.

Irregular and named classes (esse, habere, stare, ire, …) go to the
irregular report as full words.
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vulgultra.conjugation_harvest import PERSON_SLOTS, row_forms  # noqa: E402
from vulgultra.phonology import from_orthography, is_vowel, repair  # noqa: E402
from vulgultra.romance_swadesh import SOURCE_LANGS  # noqa: E402

SOURCES = ROOT / "data" / "conjugation" / "sources"
DEFAULT_OUTPUT = ROOT / "docs" / "eval" / "verb_ending_candidates.md"
DEFAULT_IRREGULAR = ROOT / "docs" / "eval" / "verb_ending_candidates_irregular.md"

THEMES = ("a", "e", "i", "re")
THEME_TITLE = {
    "a": "a-theme (Latin -ĀRE)",
    "e": "e-theme (Latin -ĒRE)",
    "i": "i-theme (Latin -ĪRE)",
    "re": "re-theme (Latin -ERE)",
}
THIN = 5

# Canonical TAMs, in display order. Source labels map onto these.
TAMS = (
    "indicative.present",
    "indicative.imperfect",
    "indicative.preterite",
    "indicative.future",
    "indicative.pluperfect",
    "subjunctive.present",
    "subjunctive.imperfect",
    "subjunctive.future",
    "conditional",
    "imperative",
)
TAM_ALIASES = {
    "indicative.past": "indicative.preterite",
    "conditional.present": "conditional",
    "imperative.present": "imperative",
    "subjunctive.past": "subjunctive.imperfect",
    # Wiktionary's "preterite subjunctive" (ast, lad, lmo, sc, rm) is the
    # -ra/-se imperfect subjunctive.
    "subjunctive.preterite": "subjunctive.imperfect",
}

# Latin conjugation of each lect-class. Generic endings first; per-lect
# entries override where the infinitive spelling hides the Latin class.
GENERIC_THEME = {
    "-ar": "a", "-are": "a", "-ari": "a", "-à": "a", "-â": "a", "-a": "a",
    "-al": "a", "-ur": "a", "-ae": "a",
    "-er": "e", "-ere": "e", "-ê": "e", "-é": "e", "-è": "e", "-ea": "e",
    "-el": "e", "-éi": "e", "-ei": "e",
    "-ir": "i", "-ire": "i", "-iri": "i", "-î": "i", "-ì": "i", "-í": "i",
    "-i": "i", "-il": "i", "-yî": "a",
    "-re": "re", "-ro": "re", "-te": "re", "-r": "re", "-rr": "re", "-e": "re",
}
LECT_THEME = {
    # Oïl -er is Latin -ĀRE.
    "fr": {"-er": "a"}, "gallo": {"-er": "a"}, "nrf": {"-er": "a", "-ier": "a"},
    "pcd": {"-er": "a", "-tcher": "a", "-djer": "a"},
    "wa": {"-er": "a", "-eur": "e", "-ur": "e", "-î": "i", "-e": "re"},
    # Gallo-Italian / Rhaeto: stressed -é/-èr/-er from -ĀRE.
    "pms": {"-é": "a", "-è": "e", "-e": "re"},
    "lld": {"-er": "a", "-é": "e"},
    "eml": {"-ēr": "a", "-èr": "a", "-er": "re", "-îr": "i", "-ôr": "a"},
    "rgn": {"-êr": "a", "-ér": "a", "-ar": "re", "-ìr": "i"},
    "fur": {"-i": "re"},
    "lij": {"-e": "re"},
    "lmo": {"-er": "re"},
    "rm": {"-air": "e", "-eir": "e"},
    "co": {"-e": "re"},
    # Sicilian -iri merges Latin -ĒRE / -ERE / -ĪRE.
    "scn": {"-iri": "i"},
    "sc": {"-ai": "a", "-ei": "e"},
    "dlm": {"-er": "e"},
    # Romanian families: -a I, -ea II, -e III, -i/-î IV.
    "ro": {"-e": "re", "-î": "i"},
    "ruq": {"I": "a", "I-ez": "a", "II": "e", "III": "re", "IV": "i", "IV-esc": "i"},
    "ruo": {"I-å": "a", "II-é": "e", "III-e": "re", "IV-éi": "i", "IV-í": "i"},
}

_SPELL = str.maketrans({
    "ț": "t", "ţ": "t", "ș": "s", "ş": "s", "ʦ": "ts", "ʣ": "dz", "ł": "l",
    "š": "s", "ž": "z", "č": "c", "ə": "e", "ă": "a", "â": "a", "î": "i",
    "å": "o", "ŭ": "u", "ẽ": "e", "ẓ": "z", "ç": "s", "ñ": "n", "'": "", "’": "",
})


def theme_of(lect: str, class_source: str) -> str | None:
    override = LECT_THEME.get(lect, {})
    if class_source in override:
        return override[class_source]
    return GENERIC_THEME.get(class_source)


def canonical_tam(feature: str) -> str | None:
    feature = TAM_ALIASES.get(feature, feature)
    return feature if feature in TAMS else None


def ending_sigma(ending: str) -> int:
    """σ of an ending read as Vulgultra orthography after repair; ∅ is 0."""
    if ending in {"∅", ""}:
        return 0
    text = unicodedata.normalize("NFC", ending.lower())
    # Non-syllabic marks (ruq transcription): u̯ i̯ e̯ are glides.
    text = text.replace("u\u032f", "w").replace("i\u032f", "j").replace("e\u032f", "j")
    text = text.translate(_SPELL)
    text = "".join(
        ch for ch in unicodedata.normalize("NFD", text)
        if unicodedata.category(ch) != "Mn"
    )
    try:
        return sum(1 for seg in repair(from_orthography(text)) if is_vowel(seg))
    except Exception:  # noqa: BLE001 - unknown symbol: fall back to vowel groups
        groups, inside = 0, False
        for ch in text:
            vowel = ch in "aeiouy"
            groups += vowel and not inside
            inside = vowel
        return groups


def load_regular() -> tuple[dict, dict]:
    """theme → tam → slot → ending → [(lect, class, support)]; plus notes."""
    tree: dict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    notes: dict = {"no_data": [], "unthemed": defaultdict(list), "dropped_tams": defaultdict(set)}
    for lect in SOURCE_LANGS:
        path = SOURCES / f"{lect}.json"
        if not path.is_file():
            notes["no_data"].append(lect)
            continue
        inventories = json.loads(path.read_text(encoding="utf-8"))["metadata"].get(
            "ending_inventories"
        ) or {}
        if not inventories:
            notes["no_data"].append(lect)
        for class_source, features in inventories.items():
            theme = theme_of(lect, class_source)
            if theme is None:
                notes["unthemed"][lect].append(class_source)
                continue
            best: dict[str, dict] = {}
            for feature, payload in features.items():
                tam = canonical_tam(feature)
                if tam is None:
                    notes["dropped_tams"][lect].add(feature)
                    continue
                if tam not in best or payload["support"] > best[tam]["support"]:
                    best[tam] = payload
            for tam, payload in best.items():
                for slot, ending in payload["endings"].items():
                    if ending in {"—", ""}:
                        continue
                    tree[theme][tam][slot][ending].append(
                        (lect, class_source, int(payload["support"]))
                    )
    return tree, notes


def show(ending: str) -> str:
    return "∅" if ending in {"∅", ""} else f"-{ending}"


def format_candidates(endings: dict) -> str:
    """`**-amos** 2σ — es 6937 · gl 1862`, ordered by σ then total support.

    Candidates that no lect backs with THIN+ verbs collapse into one
    trailing `thin:` line: one-lemma rows mostly carry stem alternations.
    """
    ranked = sorted(
        endings.items(),
        key=lambda item: (ending_sigma(item[0]), -sum(s for _l, _c, s in item[1]), item[0]),
    )
    parts, thin = [], []
    for ending, sources in ranked:
        sigma = ending_sigma(ending)
        ordered = sorted(sources, key=lambda src: -src[2])
        if ordered[0][2] < THIN:
            lects = ", ".join(f"{lect} {support}" for lect, _cls, support in ordered)
            thin.append(f"{show(ending)} {sigma}σ ({lects})")
            continue
        lects = " · ".join(
            f"{lect} {support}" + ("*" if support < THIN else "")
            for lect, _cls, support in ordered
        )
        parts.append(f"**{show(ending)}** {sigma}σ — {lects}")
    if thin:
        parts.append("<sub>thin: " + " · ".join(thin) + "</sub>")
    return "<br>".join(parts) or "—"


def theme_section(theme: str, tams: dict) -> list[str]:
    lines = [f'<a id="{theme}"></a>', f"## {THEME_TITLE[theme]}", ""]
    for tam in TAMS:
        slots = tams.get(tam)
        if not slots:
            continue
        lines.extend([f"### {tam}", "", "| | candidates |", "|---|---|"])
        for slot in PERSON_SLOTS:
            lines.append(f"| **{slot}** | {format_candidates(slots.get(slot) or {})} |")
        lines.append("")
    return lines


def render(tree: dict, notes: dict) -> str:
    covered = sorted(
        {lect for tams in tree.values() for slots in tams.values()
         for endings in slots.values() for srcs in endings.values() for lect, _c, _s in srcs},
        key=SOURCE_LANGS.index,
    )
    lines = [
        "# Verb ending shortlist",
        "",
        "Regular verbs only. Each cell lists every lect's regular ending for that",
        "theme, tense and person: `**-ending** σ — lect support`. Support is the",
        "number of verbs in that lect-class that follow the regular row",
        f"(`*` = fewer than {THIN}, thin evidence). Candidates are ordered by σ,",
        "then by total support. 2σ endings are kept whole. Inchoative infixes",
        "(-isc-, -esc-/-ez-, -eix-, -iss-, -zc-) are part of the stem.",
        "",
        f"Lects with regular data ({len(covered)}): {', '.join(covered)}.",
        "",
        "Themes: " + " · ".join(f"[{THEME_TITLE[t]}](#{t})" for t in THEMES if t in tree),
        "",
    ]
    for theme in THEMES:
        if theme in tree:
            lines.extend(theme_section(theme, tree[theme]))
    lines.extend(["## Not in the shortlist", ""])
    if notes["no_data"]:
        lines.append(f"- No regular inventory: {', '.join(notes['no_data'])}.")
    for lect in SOURCE_LANGS:
        classes = notes["unthemed"].get(lect)
        if classes:
            lines.append(
                f"- {lect}: irregular / unclassed ({', '.join(sorted(classes))}) —"
                f" see [irregulars]({DEFAULT_IRREGULAR.name})."
            )
    for lect in SOURCE_LANGS:
        dropped = notes["dropped_tams"].get(lect)
        if dropped:
            lines.append(f"- {lect}: unmapped TAM labels {', '.join(sorted(dropped))}.")
    lines.append("")
    return "\n".join(lines)


def render_irregular() -> str:
    """Full-word present rows for classes outside the four themes."""
    lines = [
        "# Irregular verbs (present indicative)",
        "",
        "Classes outside the a/e/i/re themes: copula, auxiliaries, ire, and",
        "suppletive verbs. Full words, one row per lemma.",
        "",
        "| lect | class | lemma | 1sg | 2sg | 3sg | 1pl | 2pl | 3pl |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for lect in SOURCE_LANGS:
        path = SOURCES / f"{lect}.json"
        if not path.is_file():
            continue
        for paradigm in json.loads(path.read_text(encoding="utf-8")).get("paradigms") or []:
            class_source = str(paradigm.get("class_source") or "unknown")
            if theme_of(lect, class_source) is not None:
                continue
            cells = paradigm.get("cells", {}).get("indicative.present") or {}
            forms = row_forms({slot: [cell] for slot, cell in cells.items()})
            if not forms:
                continue
            row = " | ".join(forms.get(slot, "—") for slot in PERSON_SLOTS)
            lines.append(f"| {lect} | {class_source} | {paradigm['lemma']} | {row} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--irregular-output", type=Path, default=DEFAULT_IRREGULAR)
    args = parser.parse_args()
    tree, notes = load_regular()
    text = render(tree, notes)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    irregular = render_irregular()
    args.irregular_output.write_text(irregular, encoding="utf-8")
    print(f"wrote {args.output} ({len(text):,} chars)")
    print(f"wrote {args.irregular_output} ({len(irregular):,} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
