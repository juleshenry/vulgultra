"""Harvest Kaikki/Wiktextract verb forms into lect-internal 6-slot grids.

Class labels stay language-internal. Orthographic ending inventories are
derived from complete person rows; missing cells stay missing.
"""

from __future__ import annotations

import re
import unicodedata
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
    "imperfect": "imperfect",
    "future": "future",
    "pluperfect": "pluperfect",
    # it/fr/eml "historic past" and ro/rup/dlm "perfect" are the simple preterite.
    "historic": "preterite",
    "remote": "preterite",
    "perfect": "preterite",
    "past": "past",
}
# Particles hyphenated onto the verb (Aromanian conditional s-cãntari).
PREFIX_PARTICLES = {"rup": re.compile(r"^s-")}
# Lects cited by 1sg: the class comes from the long infinitive in the table.
INFINITIVE_CLASS = {"rup": (("are", "ari"), ("ere", "eri"), ("ire", "iri"))}
# Tables Wiktextract could not parse (every cell error-unrecognized-form, person
# lost). The forms are all in the record; this only puts them back in their
# Wiktionary cells, in page order.
RESEGMENT: dict[tuple[str, str], dict[str, tuple[str, ...]]] = {
    ("rup", "escu"): {
        "1sg": ("escu", "hiu"), "2sg": ("eshti", "esci", "hii"),
        "3sg": ("easti", "easte", "easci"), "1pl": ("him", "himu"),
        "2pl": ("hits", "hitsã"), "3pl": ("suntu", "sun"),
    },
}
# Bare "past" (no historic/perfect tag): the preterite in co, the imperfect in pms.
BARE_PAST = {"pms": "imperfect"}
# Periphrastic rows and negative imperatives are not person endings.
SKIP_TAGS = {"multiword-construction", "anterior", "negative"}

# Subject clitics written into Kaikki conjugation cells (NB: obligatory in
# these lects). Stripped so the cell is the verb form alone.
SUBJECT_CLITICS: dict[str, tuple[str, ...]] = {
    "fur": ("o", "tu", "al", "e", "a", "i"),
    "vec": ("el", "ła", "la", "i", "łe", "le", "te", "ti", "a"),
    "lij": ("mi", "ti", "o", "a", "i", "e", "se", "me", "ve", "ne", "te"),
    "pms": ("mi", "i", "it", "a", "at", "as", "is", "I"),
}

# Inchoative infixes are stem allomorphs, not person endings (grammar.tex):
# `finisco` is fin·isc·o, so its ending is -o like `dormo`. Each pair is
# (infix as written, what the stem shows without it); the rightmost
# occurrence in each form is removed before the stem is split off.
INCHOATIVE_INFIXES: dict[str, tuple[tuple[str, str], ...]] = {
    "it": (("isc", ""),), "sc": (("isc", ""),), "scn": (("isc", ""),),
    "co": (("isc", ""),), "lij": (("isc", ""),),
    "vec": (("iss", ""),), "lmo": (("iss", ""),), "pms": (("iss", ""),),
    "fur": (("iss", ""),), "eml": (("iss", ""),),
    "ro": (("eaz", ""), ("ez", ""), ("esc", ""), ("ește", "e"), ("ești", "i"),
           ("ăsc", ""), ("ășt", "")),
    "rup": (("eadz", ""), ("edz", ""), ("ãsc", ""), ("ez", "")),
    "ruq": (("e̯az", ""), ("ez", ""), ("esc", ""), ("eʃt", "")),
    "ruo": (("ésc", ""), ("éš", "")),
    "ca": (("eix", ""), ("ix", ""), ("esc", "")),
    "oc": (("iss", ""), ("isc", "")), "gsc": (("iss", ""), ("isc", "")),
    "fr": (("iss", ""),), "wa": (("ixh", ""), ("iss", "")),
    "pcd": (("ich", ""), ("iss", "")), "nrf": (("iss", ""),),
    "rm": (("esch", ""), ("eg", "")),
    "es": (("zc", "c"),), "gl": (("zc", "c"),), "ast": (("zc", "c"),),
}

MAX_REPRESENTATIVES = 3
MIN_INVENTORY_SUPPORT = 3


def lect_from_filename(filename: str) -> str:
    """`kaikki-fur.jsonl` → `fur`."""
    name = str(filename).rsplit("/", 1)[-1]
    if name.startswith("kaikki-"):
        name = name[len("kaikki-"):]
    return name.split(".", 1)[0]


# Object / reflexive clitics written before the verb in pronominal lemmas
# (es `me la zumbo`, ca `m'adiro`, it `mi zittisco`) or hyphenated after it
# (pt `queixo-me`). Stripped so the cell is the verb form alone.
_IBERO_OBJ = ("me", "te", "se", "nos", "os", "vos", "la", "las", "lo", "los", "le", "les")
_ITALO_OBJ = ("mi", "ti", "si", "ci", "vi", "ne", "lo", "la", "li", "le", "gli",
              "me", "te", "se", "ce", "ve")
OBJECT_CLITICS: dict[str, tuple[str, ...]] = {
    "es": _IBERO_OBJ, "ast": _IBERO_OBJ, "an": _IBERO_OBJ, "ext": _IBERO_OBJ,
    "lad": _IBERO_OBJ,
    "gl": ("me", "te", "se", "nos", "vos", "o", "a", "os", "as", "lle", "lles", "che"),
    "pt": ("me", "te", "se", "nos", "vos", "o", "a", "os", "as", "lhe", "lhes"),
    "mwl": ("me", "te", "se", "mos", "bos", "l", "la", "ls", "las", "le", "les"),
    "ca": ("em", "et", "es", "ens", "us", "el", "la", "els", "les", "li", "hi", "en", "ho",
           "me", "te", "se", "ne"),
    "oc": ("me", "te", "se", "nos", "vos", "lo", "la", "los", "las", "li", "i", "ne"),
    "it": _ITALO_OBJ, "co": _ITALO_OBJ, "scn": _ITALO_OBJ, "sc": _ITALO_OBJ,
    "ro": ("mă", "te", "se", "ne", "vă", "își", "îmi", "îți", "îl", "o", "îi", "le", "și"),
}
_ELIDED_OBJ = re.compile(r"^(?:[mtsnlcv]|ens|us)['’](?=\w)")
_HYPHEN_OBJ_LECTS = {"pt", "gl", "mwl", "ca"}


def strip_object_clitics(lect: str, form: str) -> str:
    """`me la zumbo` → `zumbo`, `m'adiro` → `adiro`, `queixo-me` → `queixo`."""
    clitics = OBJECT_CLITICS.get(lect)
    if not clitics:
        return form
    words = form.split()
    while len(words) > 1 and words[0] in clitics:
        words = words[1:]
    if len(words) == 1:
        word = words[0]
        if lect in {"ca", "oc", "it", "co", "scn", "sc"}:
            word = _ELIDED_OBJ.sub("", word)
        if lect in _HYPHEN_OBJ_LECTS and "-" in word:
            head, _, tail = word.partition("-")
            if head and tail.replace("-", "") and all(
                part in clitics or part in {"hi", "ho", "en", "n'hi"} for part in tail.split("-")
            ):
                word = head
        words = [word]
    return " ".join(words)


def strip_subject_clitics(lect: str, form: str) -> str:
    """`o fevelavi` → `fevelavi`; a bare clitic (`al`) → ``."""
    clitics = SUBJECT_CLITICS.get(lect)
    text = strip_object_clitics(lect, form.strip())
    if lect in PREFIX_PARTICLES:
        text = PREFIX_PARTICLES[lect].sub("", text)
    if not clitics:
        return text
    words = text.split()
    while words and words[0] in clitics:
        words = words[1:]
    if words and lect == "pms" and words[0][:2] in {"l'", "l’"}:
        words[0] = words[0][2:]
    return " ".join(words)


def _bare(text: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFD", text)
        if unicodedata.category(ch) != "Mn"
    )


def plain_spelling(form_record: dict[str, Any], form: str) -> str:
    """Drop pedagogical stress marks Wiktionary adds (it `pàrlo` → `parlo`).

    The record's first link carries the standard spelling; use it only when
    the two differ by diacritics alone.
    """
    for link in form_record.get("links") or []:
        if isinstance(link, list) and len(link) == 2 and link[0] == form:
            target = str(link[1]).split("#", 1)[0].strip()
            if target and target != form and _bare(target) == _bare(form):
                return target
    return form


def decode_tags(tags: list[str], lect: str = "") -> tuple[str | None, str, bool]:
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
        if tense == "past":
            tense = BARE_PAST.get(lect, "preterite")
        if tagset & SKIP_TAGS:
            mood, tense = "skip", None
        # Wiktionary form-of rows often tag tense alone under an indicative table.
        if mood is None and tense is not None:
            mood = "indicative"
        feature = ".".join(piece for piece in (mood, tense) if piece) or "unclassified"
    return slot, feature, ambiguous


def resegment(
    forms: list[dict[str, Any]], cells: dict[str, tuple[str, ...]]
) -> list[dict[str, Any]]:
    """Re-tag unparsed present-indicative forms with their known cells."""
    slot_of = {form: slot for slot, row in cells.items() for form in row}
    out: list[dict[str, Any]] = []
    for rec in forms:
        tags = rec.get("tags") or []
        form = str(rec.get("form") or "")
        if "error-unrecognized-form" not in tags:
            out.append(rec)
        elif form in slot_of:
            out.append({**rec, "tags": ["indicative", "present", *SLOT_PERSON_TAGS[slot_of[form]]]})
    return out


def recover_conjugation_persons(
    forms: list[dict[str, Any]],
    lect: str = "",
) -> list[dict[str, Any]]:
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
    extras: list[dict[str, Any]] = []

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
            slot, _feature, ambiguous = decode_tags(tags, lect)
            if slot and not ambiguous:
                tagged.add(slot)
                continue
            if "singular" in tags:
                unlabeled_sg.append(idx)
            elif "plural" in tags:
                unlabeled_pl.append(idx)
        sg_needed = [slot for slot in ("1sg", "2sg", "3sg") if slot not in tagged]
        pl_needed = [slot for slot in ("1pl", "2pl", "3pl") if slot not in tagged]
        if len(unlabeled_sg) == 1 and sg_needed == ["1sg", "3sg"]:
            # One shared cell for je/il (nrf `aime`): it fills both persons.
            twin = dict(recovered[unlabeled_sg[0]])
            twin["tags"] = list(twin.get("tags") or [])
            inject(twin, "3sg")
            extras.append(twin)
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
        slot, feature, ambiguous = decode_tags(tags, lect)
        # Adjacent tables can decode to the same feature (rgn present indicative
        # then subjunctive). A slot or number that is already full starts a
        # new table instead of pooling six more forms into this one.
        number = "singular" if "singular" in tags else "plural" if "plural" in tags else ""
        in_group = [
            [str(t).lower().replace("_", "-") for t in recovered[i].get("tags") or []]
            for i in group
        ]
        slot_seen = bool(slot) and not ambiguous and any(
            decode_tags(other, lect)[0] == slot for other in in_group
        )
        number_full = bool(number) and sum(number in other for other in in_group) >= 3
        if group and (feature != group_feature or slot_seen or number_full):
            flush()
        group_feature = feature
        group.append(idx)
    flush()
    return recovered + extras


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
        forms = [
            str(record.get("form") or "").strip()
            for record in cells.get(slot) or []
        ]
        forms = [form for form in forms if form and form != "-"]
        # A reflexive or periphrastic alternate (`me fiai`) listed first must
        # not hide the synthetic form and knock the row out of the inventory.
        single = [form for form in forms if " " not in form]
        if single or forms:
            out[slot] = (single or forms)[0]
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


def drop_inchoative(lect: str, forms: dict[str, str]) -> dict[str, str]:
    """Move the inchoative infix into the stem: finisco → fino (fin + o)."""
    out = dict(forms)
    for slot, form in forms.items():
        # Per form, the first listed variant it contains (ro lucrez / lucrează).
        for infix, keep in INCHOATIVE_INFIXES.get(lect, ()):
            at = form.rfind(infix)
            if at > 0:
                out[slot] = form[:at] + keep + form[at + len(infix):]
                break
    return out


def strip_endings(
    forms: dict[str, str],
    stem: str | None = None,
    lect: str = "",
) -> tuple[dict[str, str], str, str] | None:
    """Return (endings, stem_used, stem_mode) for a complete or near-complete row."""
    if lect in INCHOATIVE_INFIXES:
        reduced = drop_inchoative(lect, forms)
        if reduced != forms:
            forms, stem = reduced, None
    occupied = [forms[slot] for slot in PERSON_SLOTS if forms.get(slot)]
    if len(occupied) < 4:
        return None
    # Periphrastic / compound cells ("habría librau") are not single suffixes.
    if any(" " in form for form in occupied):
        return None

    mode = "template"
    used = usable_stem(stem) or ""
    # Template stem args are sometimes another word (nrf `aveir`, eml `èser`,
    # co gerund): fall back to the row's own common prefix.
    if not used or not all(form.startswith(used) for form in occupied):
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


def infinitive_stem(lemma: str, class_source: str) -> str | None:
    """`comer` in class `-er` → `com`; None when the class is not an ending."""
    if not class_source.startswith("-"):
        return None
    bare = _bare(re.sub(r"^(?:se\s+|s['’])", "", lemma.strip().lower()))
    ending = _bare(class_source[1:].lower())
    if not ending or not bare.endswith(ending) or len(bare) == len(ending):
        return None
    return bare[: -len(ending)]


def regular_endings(
    forms: dict[str, str], stem: str | None, lect: str,
) -> dict[str, str] | None:
    """Endings cut at the infinitive stem, or None if the row changes stem.

    Regular row: every form starts with the infinitive stem. The inchoative
    infix is stem (finisco → fin·o), so it is removed first. Stem
    alternations (cuerro/correr, conozo/conocer, tengo/tener) fail. Stress
    marks are ignored when matching (lij màngio / mangiâ).
    """
    if not stem:
        return None
    reduced = drop_inchoative(lect, forms) if lect in INCHOATIVE_INFIXES else forms
    endings: dict[str, str] = {}
    for slot in PERSON_SLOTS:
        form = unicodedata.normalize("NFC", reduced.get(slot) or "")
        bare = _bare(form.lower())
        if not form or not bare.startswith(stem) or len(bare) != len(form):
            return None
        endings[slot] = form[len(stem):] or "∅"
    return endings


def aggregate_ending_inventory(
    lemmas: dict[str, dict[str, Any]],
    *,
    min_support: int = MIN_INVENTORY_SUPPORT,
    lect: str = "",
    class_source: str = "",
) -> dict[str, dict[str, Any]]:
    """Regular endings per feature for one conj class.

    A regular row keeps the infinitive stem in all six forms; the class's
    ending row is the most common among regular rows (all rows when no
    lemma qualifies, e.g. classes named after one irregular verb).
    """
    by_feature: dict[str, list[tuple[tuple[str, ...], str, str, bool]]] = defaultdict(list)
    for lemma, meta in lemmas.items():
        stem = meta.get("stem")
        lemma_stem = infinitive_stem(meta.get("infinitive") or lemma, class_source)
        for feature, cells in meta["features"].items():
            forms = row_forms(cells)
            if not is_complete_row(forms):
                continue
            stripped = strip_endings(forms, stem, lect)
            if not stripped:
                continue
            endings, used, mode = stripped
            cut = regular_endings(forms, lemma_stem, lect)
            if cut:
                endings, used, mode = cut, lemma_stem or used, "infinitive"
            pattern = tuple(endings[slot] for slot in PERSON_SLOTS)
            by_feature[feature].append((pattern, used, mode, cut is not None))

    inventory: dict[str, dict[str, Any]] = {}
    for feature, rows in sorted(by_feature.items()):
        support_needed = 1 if len(lemmas) < min_support else min_support
        if len(rows) < support_needed:
            continue
        regular = [row for row in rows if row[3]]
        pool = regular or rows
        counts = Counter(row[0] for row in pool)
        pattern, support = counts.most_common(1)[0]
        modes = Counter(row[2] for row in pool if row[0] == pattern)
        inventory[feature] = {
            "endings": {slot: pattern[index] for index, slot in enumerate(PERSON_SLOTS)},
            "support": support,
            "variants": len(counts),
            "stem_mode": modes.most_common(1)[0][0],
            "regular_rows": len(regular),
            "rows": len(rows),
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
            "infinitive": meta.get("infinitive"),
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
    lect: str = "",
) -> None:
    slot, feature, ambiguous = decode_tags(tags, lect)
    if feature.startswith("skip"):
        return
    text = strip_subject_clitics(lect, form)
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
    lect = lect_from_filename(filename)
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
            if lect in INFINITIVE_CLASS:
                infinitive = next((
                    str(item.get("form") or "") for item in raw_forms
                    if item.get("source") == "conjugation"
                    and "infinitive" in (item.get("tags") or [])
                ), "")
                for spellings in INFINITIVE_CLASS[lect]:
                    if infinitive.endswith(spellings):
                        meta["infinitive"] = infinitive[: -len(spellings[0])] + spellings[0]
                        meta["class_source"] = f"-{spellings[0]}"
                        break
            if (lect, word) in RESEGMENT:
                raw_forms = resegment(raw_forms, RESEGMENT[(lect, word)])
            for form_record in recover_conjugation_persons(raw_forms, lect):
                tags = sorted(str(tag) for tag in form_record.get("tags", []))
                if "inflection-template" in tags or "table-tags" in tags:
                    continue
                form_text = str(form_record.get("form") or "")
                if "{{" in form_text:
                    continue
                form_text = plain_spelling(form_record, form_text)
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
                    lect=lect,
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
                    lect=lect,
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
        inventory = aggregate_ending_inventory(lemmas, lect=lect, class_source=class_source)
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
