#!/usr/bin/env python3
"""Verb ending shortlist: every lect's regular endings, per theme × TAM × person.

Regular only. A regular verb keeps its infinitive stem in all six forms
(inchoative infix counts as stem); each lect-class contributes the ending
row most of its regular verbs share (`metadata.ending_inventories`, built
over the full lemma set). Its support is the number of verbs that follow
that row. Classes are pooled by their Latin conjugation (a/e/i/re theme),
not by the spelling of the infinitive: French `-er` and Piedmontese `-é`
are Latin -ARE, so a-theme.

Nothing is dropped for length: 2σ endings (`-amos`) compete whole. σ is
counted in the source lect's own phonology, faithful to the original
inventory (see `ending_sigma`).

esse, stare and habere get full-word sections; other irregulars are listed
as full words at the end. Output is one self-contained HTML page with a
3 × 2 grid (person × number) per tense.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vulgultra.conjugation_harvest import PERSON_SLOTS, row_forms  # noqa: E402
from vulgultra.romance_swadesh import LECT_BRANCHES, LECT_NAMES, SOURCE_LANGS  # noqa: E402

SOURCES = ROOT / "data" / "conjugation" / "sources"
DEFAULT_OUTPUT = ROOT / "docs" / "eval" / "verb_ending_candidates.html"

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
    # Aromanian long infinitive: -are I, -ere mostly III (unstressed), -ire IV.
    "rup": {"-ere": "re"},
    "ruq": {"I": "a", "I-ez": "a", "II": "e", "III": "re", "IV": "i", "IV-esc": "i"},
    "ruo": {"I-å": "a", "II-é": "e", "III-e": "re", "IV-éi": "i", "IV-í": "i"},
}

def theme_of(lect: str, class_source: str) -> str | None:
    override = LECT_THEME.get(lect, {})
    if class_source in override:
        return override[class_source]
    return GENERIC_THEME.get(class_source)


def canonical_tam(feature: str) -> str | None:
    feature = TAM_ALIASES.get(feature, feature)
    return feature if feature in TAMS else None


OIL = {"fr", "wa", "pcd", "nrf", "gallo", "frp"}
EASTERN = {"ro", "rup", "ruq", "ruo"}
# Unmarked i + vowel at the end of the word is a stressed-í hiatus
# (pt comia, ca temien, sc timia, co parleria); es/gl/ast write it -ía.
HIATUS_IA = {"pt", "ca", "co", "sc"}
# Final -ii is a hiatus (it finii, co finii); ro -ii is [ij].
HIATUS_II = {"it", "co", "sc", "scn"}
# A doubled vowel spells one long vowel (lmo -aróo).
LONG_DOUBLE = {"lmo", "eml"}
# Nasal diphthongs (-ão, -ões, -ãe) are one nucleus.
NASAL_DIPHTHONG = {"pt", "mwl", "gl"}
_HIGH = set("iuyìíîïùúûü")
_STRESSED_HIGH = set("íúìù")
_VOWELS = set("aeiouàáâãäåèéêëìíîïòóôõöùúûüăæœøǫəɐɛɔɨʊɪāēīōūȧėȯ")
_MARKED = set("áàâéèêíìîóòôúùû")


def _base(ch: str) -> str:
    return unicodedata.normalize("NFD", ch)[0]


def ending_sigma(ending: str, lect: str = "", word: bool = False) -> int:
    """σ the ending adds in its source lect's own phonology; ∅ is 0.

    Source-faithful, per lect: a falling or rising diphthong is one nucleus
    (-áis, -éis, -eu, -ai, -iamo); two non-high vowels, or a stressed high
    vowel next to a vowel (-ía), are a hiatus. An i between two vowels is
    an onset (sc -aia = a.ja). Oïl final -e/-es/-ent are silent (parle,
    parlent) and oi/oa/oè are /wa wɛ/. Eastern Romance final -i after a
    consonant is non-syllabic (-ați, cânți) and ea/oa are diphthongs.
    pt/ca/co/sc unmarked final -ia is a stressed-í hiatus (comia); it/co
    final -ii is a hiatus (finii); pt nasal -ão/-õe are one nucleus; lmo
    doubled vowels are long. Transcribed glides (u̯, i̯, e̯) are not nuclei.
    With word=True the input is a whole word, so a silent Oïl -e never
    takes the word's only vowel (fr es, gallo ses are 1σ).
    """
    if ending in {"∅", ""}:
        return 0
    text = unicodedata.normalize("NFD", ending.lower().replace("ˈ", "").replace("ˌ", ""))
    # Non-syllabic mark (U+032F) makes the preceding vowel a glide.
    text = re.sub(r".\u032f", "j", text)
    text = unicodedata.normalize("NFC", text)
    if lect in OIL:
        stripped = re.sub(r"e(?:s|nt)?$", "", text)
        if not word or set(stripped) & _VOWELS:
            text = stripped
        text = re.sub(r"o(?=[aàâeèéêi])", "w", text)
    if lect in EASTERN:
        # The ending follows the stem consonant, so a bare -i is non-syllabic too.
        text = "" if text == "i" else re.sub(r"(?<=[^aeiouăâîe])i$", "", text)
        text = text.replace("ea", "a").replace("oa", "a")
    if lect in NASAL_DIPHTHONG:
        text = re.sub(r"([ãõ])[eoiu]", r"\1", text)
    # An unstressed i/y between two vowels is the next syllable's onset.
    text = re.sub(r"(?<=[aeouàáâãèéêòóôõăə])[iy](?=[aeouàáâèéêòóôăə])", "j", text)
    if lect in HIATUS_IA and not _MARKED & set(text):
        text = re.sub(r"i(?=[aeo][^aeiou]*$)", "í", text)
    if lect in HIATUS_II:
        text = re.sub(r"ii$", "íi", text)
    sigma = 0
    run: list[str] = []
    for ch in text + " ":
        if ch in _VOWELS:
            run.append(ch)
            continue
        if run:
            sigma += 1
            for left, right in zip(run, run[1:]):
                if lect in LONG_DOUBLE and _base(left) == _base(right):
                    continue
                hiatus = (left not in _HIGH and right not in _HIGH) or (
                    left in _STRESSED_HIGH or right in _STRESSED_HIGH
                )
                sigma += hiatus
            run = []
    return sigma


# Latin esse / stare / habere: one row of full words per lect, since their
# stems are suppletive. Lemma spellings follow each source.
NAMED_VERBS: dict[str, dict[str, tuple[str, ...]]] = {
    "esse": {
        "es": ("ser",), "pt": ("ser",), "gl": ("ser",), "an": ("ser",), "ast": ("ser",),
        "ext": ("sel",), "lad": ("ser",), "mwl": ("ser",), "oc": ("èsser",),
        "ca": ("ser",), "fr": ("être",), "wa": ("esse",), "pcd": ("ête",),
        "nrf": ("ête",), "gallo": ("étr",), "pms": ("esse",), "eml": ("èser",),
        "rgn": ("es",), "it": ("essere",), "scn": ("èssiri",), "vec": ("èser",),
        "co": ("esse",), "dlm": ("saite", "zer"), "rm": ("esser",), "fur": ("jessi",),
        "sc": ("èssere", "essi"), "ist": ("ièsi",), "ro": ("fi",), "rup": ("escu",),
        "ruq": ("iri / sam",),
    },
    "stare": {
        "es": ("estar",), "pt": ("estar",), "gl": ("estar",), "an": ("estar",),
        "ext": ("estal",), "mwl": ("star",), "ca": ("estar",), "gsc": ("estar",),
        "it": ("stare",), "ruq": ("stare",),
    },
    "habere": {
        "es": ("haber",), "pt": ("haver",), "gl": ("haber",), "an": ("haber",),
        "ast": ("haber",), "ext": ("avel",), "mwl": ("haber",), "oc": ("aver",),
        "ca": ("haver",), "gsc": ("aver",), "fr": ("avoir",), "wa": ("aveur",),
        "pcd": ("avoér",), "nrf": ("aver", "aveir"), "gallo": ("avair",),
        "frp": ("avêr",), "lmo": ("avè",), "pms": ("avèj",), "lij": ("avéi",),
        "eml": ("avair",), "rgn": ("avér",), "it": ("avere",), "vec": ("aver",),
        "co": ("avè",), "dlm": ("avar",), "rm": ("haver", "avair"), "lld": ("avei",),
        "ist": ("avì",), "ro": ("avea",), "rup": ("am",), "ruq": ("habere",),
    },
}
NAMED_TITLE = {
    "esse": "esse (to be)",
    "stare": "stare (to stand / be)",
    "habere": "habere (to have)",
}


def load_named() -> dict:
    """verb → tam → slot → form → [lect]: full words, primary form per lect."""
    tree: dict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    lemmas: dict = defaultdict(list)
    for lect in SOURCE_LANGS:
        path = SOURCES / f"{lect}.json"
        if not path.is_file():
            continue
        paradigms = json.loads(path.read_text(encoding="utf-8")).get("paradigms") or []
        for verb, by_lect in NAMED_VERBS.items():
            wanted = by_lect.get(lect, ())
            for paradigm in paradigms:
                if paradigm.get("lemma") not in wanted:
                    continue
                lemmas[verb].append((lect, paradigm["lemma"]))
                for feature, row in (paradigm.get("cells") or {}).items():
                    tam = canonical_tam(feature)
                    if tam is None:
                        continue
                    for slot, cell in row.items():
                        form = str((cell or {}).get("form") or "").strip()
                        if slot in PERSON_SLOTS and form and lect not in tree[verb][tam][slot][form]:
                            tree[verb][tam][slot][form].append(lect)
    return tree, lemmas


def rank_words(forms: dict) -> list[tuple[str, int, list[str]]]:
    """(form, σ, lects), ordered by σ then number of lects."""
    by_sigma: dict[tuple[str, int], list[str]] = defaultdict(list)
    for form, lects in forms.items():
        for lect in lects:
            by_sigma[(form, ending_sigma(form, lect, word=True))].append(lect)
    ranked = sorted(by_sigma.items(), key=lambda item: (item[0][1], -len(item[1]), item[0][0]))
    return [(form, sigma, lects) for (form, sigma), lects in ranked]


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


def rank_candidates(endings: dict) -> tuple[list, list]:
    """(main, thin) lists of (ending, σ, [(lect, class, support)]), by σ then support.

    σ is per source lect, so one spelling can split (-es: fr 0σ, es 1σ).
    Candidates that no lect backs with THIN+ verbs go to `thin`: one-lemma
    rows mostly carry stem alternations.
    """
    by_sigma: dict[tuple[str, int], list] = defaultdict(list)
    for ending, sources in endings.items():
        for source in sources:
            by_sigma[(ending, ending_sigma(ending, source[0]))].append(source)
    ranked = sorted(
        by_sigma.items(),
        key=lambda item: (item[0][1], -sum(s for _l, _c, s in item[1]), item[0][0]),
    )
    main, thin = [], []
    for (ending, sigma), sources in ranked:
        ordered = sorted(sources, key=lambda src: -src[2])
        (thin if ordered[0][2] < THIN else main).append((ending, sigma, ordered))
    return main, thin


def irregular_rows() -> dict[str, list[tuple[str, str, dict[str, str]]]]:
    """lect → [(class, lemma, present row)] for verbs outside the themes."""
    named = {(lect, lemma) for by_lect in NAMED_VERBS.values()
             for lect, lemmas in by_lect.items() for lemma in lemmas}
    rows: dict[str, list] = defaultdict(list)
    for lect in SOURCE_LANGS:
        path = SOURCES / f"{lect}.json"
        if not path.is_file():
            continue
        for paradigm in json.loads(path.read_text(encoding="utf-8")).get("paradigms") or []:
            class_source = str(paradigm.get("class_source") or "unknown")
            if theme_of(lect, class_source) is not None or (lect, paradigm.get("lemma")) in named:
                continue
            cells = paradigm.get("cells", {}).get("indicative.present") or {}
            forms = row_forms({slot: [cell] for slot, cell in cells.items()})
            if forms:
                rows[lect].append((class_source, paradigm["lemma"], forms))
    return rows


BRANCH_OF = {lect: branch for branch, lects in LECT_BRANCHES.items() for lect in lects}
GRID = (("1", "1sg", "1pl"), ("2", "2sg", "2pl"), ("3", "3sg", "3pl"))


def _lect(lect: str, support: int | None = None, class_source: str = "") -> str:
    count = "" if support is None else f"<b>{support:,}</b>"
    thin = " thin" if support is not None and support < THIN else ""
    title = LECT_NAMES.get(lect, lect) + (f" · class {class_source}" if class_source else "")
    return (
        f'<span class="lect b-{BRANCH_OF.get(lect, "x")}{thin}" data-lect="{lect}"'
        f' title="{html.escape(title)}">{lect}{count}</span>'
    )


def _cand(text: str, sigma: int, lects: str, codes: list[str]) -> str:
    return (
        f'<div class="cand" data-lects="{" ".join(codes)}"><span class="form">{html.escape(text)}</span>'
        f'<span class="sig s{min(sigma, 3)}">{sigma}σ</span><span class="lects">{lects}</span></div>'
    )


def _ending_row(ending: str, sigma: int, sources: list) -> str:
    chips = "".join(_lect(lect, support, cls) for lect, cls, support in sources)
    return _cand(show(ending), sigma, chips, [lect for lect, _c, _s in sources])


def _ending_cell(endings: dict) -> str:
    main, thin = rank_candidates(endings)
    parts = [_ending_row(*cand) for cand in main]
    if thin:
        inner = "".join(_ending_row(*cand) for cand in thin)
        parts.append(f'<details class="thinbox"><summary>{len(thin)} thin</summary>{inner}</details>')
    return "".join(parts) or '<span class="none">—</span>'


def _word_cell(forms: dict) -> str:
    return "".join(
        _cand(form, sig, "".join(_lect(l) for l in lects), lects)
        for form, sig, lects in rank_words(forms)
    ) or '<span class="none">—</span>'


def _grid(slots: dict, cell) -> str:
    rows = "".join(
        f'<tr><th scope="row">{person}</th><td>{cell(slots.get(sg) or {})}</td>'
        f"<td>{cell(slots.get(pl) or {})}</td></tr>"
        for person, sg, pl in GRID
    )
    return (
        '<table class="grid"><thead><tr><th></th><th>singular</th><th>plural</th></tr></thead>'
        f"<tbody>{rows}</tbody></table>"
    )


def _section(anchor: str, title: str, intro: str, tams: dict, cell) -> str:
    present = [tam for tam in TAMS if tams.get(tam)]
    tabs = "".join(f'<a href="#{anchor}-{tam}">{tam.replace(".", " ")}</a>' for tam in present)
    blocks = "".join(
        f'<section class="tam" id="{anchor}-{tam}"><h3>{tam.replace(".", " · ")}</h3>'
        f"{_grid(tams[tam], cell)}</section>"
        for tam in present
    )
    return (
        f'<section class="verb" id="{anchor}"><h2>{html.escape(title)}</h2>{intro}'
        f'<nav class="tams">{tabs}</nav>{blocks}</section>'
    )


def _mini(forms: dict[str, str]) -> str:
    rows = "".join(
        f"<tr><th>{person}</th><td>{html.escape(forms.get(sg, '—'))}</td>"
        f"<td>{html.escape(forms.get(pl, '—'))}</td></tr>"
        for person, sg, pl in GRID
    )
    return f'<table class="mini"><tbody>{rows}</tbody></table>'


def render_html(tree: dict, notes: dict, named: dict, named_lemmas: dict, irregular: dict) -> str:
    covered = sorted(
        {lect for tams in tree.values() for slots in tams.values()
         for endings in slots.values() for srcs in endings.values() for lect, _c, _s in srcs},
        key=SOURCE_LANGS.index,
    )
    nav = [(t, THEME_TITLE[t]) for t in THEMES if t in tree]
    nav += [(v, NAMED_TITLE[v]) for v in NAMED_VERBS if v in named]
    nav.append(("irregular", "Other irregulars"))
    body = []
    for theme in THEMES:
        if theme in tree:
            body.append(_section(
                theme, THEME_TITLE[theme],
                '<p class="note">Regular endings. Number = verbs in that lect-class that follow the row.</p>',
                tree[theme], _ending_cell,
            ))
    for verb in NAMED_VERBS:
        if verb in named:
            listed = ", ".join(
                f"{lect} <i>{html.escape(lemma)}</i>" for lect, lemma in named_lemmas.get(verb, [])
            )
            body.append(_section(
                verb, NAMED_TITLE[verb],
                f'<p class="note">Full words (suppletive stems). Lemmas: {listed}.</p>',
                named[verb], _word_cell,
            ))
    groups = "".join(
        f'<details class="irr" data-lects="{lect}"><summary>{_lect(lect)} {html.escape(LECT_NAMES.get(lect, lect))}'
        f' <span class="count">{len(rows)}</span></summary><div class="minis">'
        + "".join(
            f'<figure><figcaption><i>{html.escape(lemma)}</i> <span>{html.escape(cls)}</span></figcaption>{_mini(forms)}</figure>'
            for cls, lemma, forms in rows
        )
        + "</div></details>"
        for lect, rows in irregular.items()
    )
    body.append(
        '<section class="verb" id="irregular"><h2>Other irregulars</h2>'
        '<p class="note">Present indicative, full words, for verbs outside the four themes and esse / stare / habere.</p>'
        f"{groups}</section>"
    )
    not_listed = []
    if notes["no_data"]:
        not_listed.append(f"No regular inventory: {', '.join(notes['no_data'])}.")
    for lect in SOURCE_LANGS:
        dropped = notes["dropped_tams"].get(lect)
        if dropped:
            not_listed.append(f"{lect}: unmapped TAM labels {', '.join(sorted(dropped))}.")
    chips = "".join(
        f'<button type="button" class="chip b-{BRANCH_OF.get(l, "x")}" data-lect="{l}"'
        f' title="{html.escape(LECT_NAMES.get(l, l))}">{l}</button>'
        for l in SOURCE_LANGS
    )
    page = PAGE.format(
        nav="".join(f'<a href="#{a}">{html.escape(t)}</a>' for a, t in nav),
        covered=len(covered),
        thin=THIN,
        chips=chips,
        body="".join(body),
        notes="".join(f"<li>{html.escape(n)}</li>" for n in not_listed),
    )
    return page


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Verb Ending Shortlist</title>
<style>
:root {{
  --bg: #fbfaf7; --panel: #ffffff; --ink: #1d1c1a; --muted: #6b675f; --line: #e4e0d8;
  --accent: #8a3b12; --s0: #e7f3ea; --s1: #eef1fb; --s2: #fbf1e3; --s3: #fbe7e7;
  --ibero: #c0392b; --occitano: #d68910; --oil: #2e6fb7; --arpitan: #6c5ce7;
  --gallo_italian: #16a085; --italo_dalmatian: #27ae60; --rhaeto: #8e44ad;
  --sardinian: #b9770e; --eastern: #34495e; --dim: .22;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #161514; --panel: #1f1e1c; --ink: #ece9e2; --muted: #a39e94; --line: #34322e;
    --accent: #f0a36b; --s0: #1f3326; --s1: #232a3d; --s2: #3a2e1c; --s3: #3d2222;
    --eastern: #9fb3c8; --ibero: #ef7a6c; --oil: #74a7e8; --rhaeto: #c08be0;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #161514; --panel: #1f1e1c; --ink: #ece9e2; --muted: #a39e94; --line: #34322e;
  --accent: #f0a36b; --s0: #1f3326; --s1: #232a3d; --s2: #3a2e1c; --s3: #3d2222;
  --eastern: #9fb3c8; --ibero: #ef7a6c; --oil: #74a7e8; --rhaeto: #c08be0;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--ink);
  font: 15px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif; }}
header {{ padding: 20px 16px 8px; max-width: 1200px; margin: 0 auto; }}
h1 {{ font-size: 1.5rem; margin: 0 0 6px; }}
h2 {{ font-size: 1.25rem; margin: 28px 0 4px; color: var(--accent); }}
h3 {{ font-size: 1rem; margin: 18px 0 6px; text-transform: capitalize; }}
p.note, .lede {{ color: var(--muted); margin: 4px 0; }}
.bar {{ background: var(--bg); border-bottom: 1px solid var(--line); padding: 8px 16px; }}
@media (min-width: 900px) {{ .bar {{ position: sticky; top: 0; z-index: 5; }} }}
.bar-inner {{ max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; gap: 6px; }}
.bar nav a, nav.tams a {{ color: var(--ink); text-decoration: none; padding: 3px 9px; border-radius: 999px;
  border: 1px solid var(--line); background: var(--panel); white-space: nowrap; font-size: .85rem; }}
.bar nav, nav.tams {{ display: flex; gap: 6px; overflow-x: auto; padding-bottom: 2px; }}
nav.tams {{ margin: 8px 0; }}
.chips {{ display: flex; flex-wrap: wrap; gap: 4px; align-items: center; }}
.chips .label {{ color: var(--muted); font-size: .8rem; margin-right: 4px; }}
.chip {{ font: inherit; font-size: .75rem; padding: 1px 8px; border-radius: 999px; cursor: pointer;
  border: 1px solid var(--line); background: var(--panel); color: var(--ink); }}
.chip::before {{ content: ""; display: inline-block; width: 7px; height: 7px; border-radius: 50%;
  background: var(--c); margin-right: 5px; vertical-align: 1px; }}
.chip.on {{ background: var(--c); border-color: var(--c); color: #fff; }}
.chip.on::before {{ background: #fff; }}
.tools {{ display: flex; gap: 12px; align-items: center; font-size: .8rem; color: var(--muted); flex-wrap: wrap; }}
.tools button {{ font: inherit; background: none; border: 1px solid var(--line); color: var(--ink);
  border-radius: 6px; padding: 1px 8px; cursor: pointer; }}
main {{ max-width: 1200px; margin: 0 auto; padding: 0 16px 60px; }}
table.grid {{ width: 100%; border-collapse: separate; border-spacing: 0; table-layout: fixed;
  background: var(--panel); border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }}
table.grid th {{ font-weight: 600; color: var(--muted); font-size: .8rem; padding: 6px 8px; text-align: left;
  border-bottom: 1px solid var(--line); }}
table.grid thead th:first-child, table.grid tbody th {{ width: 34px; text-align: center; }}
table.grid tbody th {{ font-size: 1.1rem; color: var(--ink); border-right: 1px solid var(--line); }}
table.grid td {{ vertical-align: top; padding: 6px; border-bottom: 1px solid var(--line); }}
table.grid td + td {{ border-left: 1px solid var(--line); }}
table.grid tr:last-child td, table.grid tr:last-child th {{ border-bottom: 0; }}
.cand {{ display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 6px; padding: 3px 4px; border-radius: 6px; }}
.cand + .cand {{ border-top: 1px dashed var(--line); }}
.form {{ font-family: "Iowan Old Style", Georgia, serif; font-size: 1.05rem; font-weight: 600; }}
.sig {{ font-size: .7rem; padding: 0 5px; border-radius: 4px; }}
.s0 {{ background: var(--s0); }} .s1 {{ background: var(--s1); }} .s2 {{ background: var(--s2); }} .s3 {{ background: var(--s3); }}
.lects {{ display: flex; flex-wrap: wrap; gap: 3px; }}
.lect {{ font-size: .72rem; padding: 0 5px; border-radius: 4px; border-left: 3px solid var(--c);
  background: color-mix(in srgb, var(--c) 12%, transparent); }}
.lect b {{ font-weight: 500; color: var(--muted); margin-left: 3px; }}
.lect.thin {{ opacity: .7; font-style: italic; }}
.b-ibero {{ --c: var(--ibero); }} .b-occitano {{ --c: var(--occitano); }} .b-oil {{ --c: var(--oil); }}
.b-arpitan {{ --c: var(--arpitan); }} .b-gallo_italian {{ --c: var(--gallo_italian); }}
.b-italo_dalmatian {{ --c: var(--italo_dalmatian); }} .b-rhaeto {{ --c: var(--rhaeto); }}
.b-sardinian {{ --c: var(--sardinian); }} .b-eastern {{ --c: var(--eastern); }}
details.thinbox summary {{ cursor: pointer; font-size: .75rem; color: var(--muted); padding: 2px 4px; }}
details.thinbox .cand {{ opacity: .8; }}
body.hide-thin details.thinbox {{ display: none; }}
body.filtering .cand:not(.hit) {{ opacity: var(--dim); }}
body.filtering.only .cand:not(.hit) {{ display: none; }}
body.filtering .lect.sel {{ outline: 2px solid var(--c); }}
.none {{ color: var(--muted); }}
details.irr {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; margin: 6px 0; padding: 6px 10px; }}
details.irr summary {{ cursor: pointer; }}
details.irr .count {{ color: var(--muted); font-size: .8rem; }}
body.filtering details.irr:not(.hit) {{ display: none; }}
.minis {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 8px; margin-top: 8px; }}
figure {{ margin: 0; border: 1px solid var(--line); border-radius: 6px; padding: 4px 6px; }}
figcaption span {{ color: var(--muted); font-size: .75rem; }}
table.mini {{ border-collapse: collapse; width: 100%; font-size: .85rem; }}
table.mini th {{ color: var(--muted); width: 16px; font-weight: 500; }}
table.mini td {{ padding: 1px 4px; }}
.terms {{ margin: 8px 0; }}
.terms summary {{ cursor: pointer; color: var(--accent); }}
.terms dl {{ display: grid; grid-template-columns: max-content 1fr; gap: 4px 12px; margin: 8px 0; }}
.terms dt {{ font-weight: 600; }} .terms dd {{ margin: 0; color: var(--muted); }}
@media (max-width: 640px) {{
  .terms dl {{ grid-template-columns: 1fr; }}
  table.grid thead th:first-child, table.grid tbody th {{ width: 24px; }}
  .form {{ font-size: .95rem; }}
}}
</style>
</head>
<body>
<header>
  <h1>Verb ending shortlist</h1>
  <p class="lede">Every lect's regular ending for each theme, tense and person, laid out as
  person × number. Candidates are ordered by σ (syllables, counted in the source lect's own
  phonology), then by support. <i>Thin</i> = fewer than {thin} verbs back it.
  {covered} lects have regular data.</p>
  <details class="terms"><summary>Terms</summary><dl>
    <dt>σ</dt><dd>Syllable count: the number of vowel peaks the ending (or word) adds. fr <i>-ent</i> 0σ, ro <i>-ați</i> 1σ, es <i>-amos</i> 2σ.</dd>
    <dt>Glide</dt><dd>An <i>i</i> or <i>u</i> said as a consonant, /j/ or /w/ (the <i>y</i> in <i>yes</i>). It never makes a syllable.</dd>
    <dt>Diphthong</dt><dd>A vowel plus a glide in one syllable. Falling: es <i>-áis</i>, <i>-éis</i>, ca <i>-eu</i>. Rising: it <i>-iamo</i>, ro <i>-ea</i>. 1σ.</dd>
    <dt>Hiatus</dt><dd>Two neighbouring vowels in separate syllables: es <i>-ía</i> (<i>co-mí-a</i>), pt <i>comia</i>, it <i>finii</i>. Each counts 1σ.</dd>
    <dt>Inchoative infix</dt><dd>A piece some verbs insert between stem and ending (it <i>fin-isc-o</i>); counted as stem.</dd>
    <dt>Support</dt><dd>The number after a lect: how many regular verbs in that lect-class use the ending.</dd>
  </dl></details>
</header>
<div class="bar"><div class="bar-inner">
  <nav>{nav}</nav>
  <div class="chips"><span class="label">Highlight lects:</span>{chips}</div>
  <div class="tools">
    <label><input type="checkbox" id="only"> hide non-matching</label>
    <label><input type="checkbox" id="thin" checked> show thin</label>
    <button type="button" id="clear">clear</button>
  </div>
</div></div>
<main>
{body}
<section class="verb"><h2>Not in the shortlist</h2><ul>{notes}</ul></section>
</main>
<script>
(() => {{
  const KEY = "verb-shortlist";
  let state = {{ lects: [], only: false, thin: true }};
  try {{ Object.assign(state, JSON.parse(localStorage.getItem(KEY) || "{{}}")); }} catch (e) {{}}
  const save = () => {{ try {{ localStorage.setItem(KEY, JSON.stringify(state)); }} catch (e) {{}} }};
  const apply = () => {{
    const sel = new Set(state.lects);
    document.body.classList.toggle("filtering", sel.size > 0);
    document.body.classList.toggle("only", state.only);
    document.body.classList.toggle("hide-thin", !state.thin);
    document.querySelectorAll(".chip").forEach(c => c.classList.toggle("on", sel.has(c.dataset.lect)));
    document.querySelectorAll(".cand, details.irr").forEach(el => {{
      const hit = (el.dataset.lects || "").split(" ").some(l => sel.has(l));
      el.classList.toggle("hit", hit);
    }});
    document.querySelectorAll(".lect").forEach(el => el.classList.toggle("sel", sel.has(el.dataset.lect)));
    document.getElementById("only").checked = state.only;
    document.getElementById("thin").checked = state.thin;
  }};
  document.querySelectorAll(".chip").forEach(c => c.addEventListener("click", () => {{
    const l = c.dataset.lect;
    state.lects = state.lects.includes(l) ? state.lects.filter(x => x !== l) : [...state.lects, l];
    save(); apply();
  }}));
  document.getElementById("only").addEventListener("change", e => {{ state.only = e.target.checked; save(); apply(); }});
  document.getElementById("thin").addEventListener("change", e => {{ state.thin = e.target.checked; save(); apply(); }});
  document.getElementById("clear").addEventListener("click", () => {{ state.lects = []; save(); apply(); }});
  apply();
}})();
</script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    tree, notes = load_regular()
    named, named_lemmas = load_named()
    page = render_html(tree, notes, named, named_lemmas, irregular_rows())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(page, encoding="utf-8")
    print(f"wrote {args.output} ({len(page):,} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
