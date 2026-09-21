"""Surface realization: case, gender, articles, verbs, copula.

Nouns inflect gender × case × number (reverse VL nom/acc/gen).
Adjectives copy that table. Definite articles o/a/os/as mark definiteness
only (not role). Copula is suppletive (é/e).
"""

from __future__ import annotations

from lacyo.optimizer import VERB_SLOTS
from lacyo.paradigms import PERSONS, VERB_TEMPLATES
from lacyo.phonology import count_syllables, from_orthography, to_orthography
from lacyo.romance_swadesh import GENDER_PAIRS, concepts as swadesh_concepts

# Closed class: one vowel, gender-marked. Not the Swadesh winner (el/la).
ARTICLES = {
    "m_sg": "o",
    "f_sg": "a",
    "m_pl": "os",
    "f_pl": "as",
}

# Suppletive present of ser/être/essere — 3sg is é, written e.
COPULA_PRS = {
    "1sg": "so",
    "1pl": "som",
    "2sg": "es",
    "2pl": "sos",
    "3sg": "e",
    "3pl": "son",
}

_PAIR_GENDER = {}
for _m, _f in GENDER_PAIRS:
    _PAIR_GENDER[_m] = "m"
    _PAIR_GENDER[_f] = "f"

# Inherent gender for demo (and common) nouns. Romance majority, ES/PT-first.
INHERENT_GENDER: dict[str, str] = {
    **_PAIR_GENDER,
    "woman": "f", "wife": "f", "mother": "f",
    "man": "m", "husband": "m", "father": "m",
    "child": "m",
    "water": "f", "night": "f", "moon": "f", "earth": "f", "sea": "f",
    "sun": "m", "fire": "m", "wind": "m", "fish": "m", "dog": "m",
    "day": "m", "year": "m", "sky": "m", "river": "m", "stone": "m",
}

_POS = {row["id"]: row["pos"] for row in swadesh_concepts()}

PERSON_OF = {
    "i": "1sg",
    "we": "1pl",
    "you_sg": "2sg",
    "you_pl": "2pl",
    "he": "3sg",
    "they": "3pl",
}


def gender_of(concept_id: str) -> str:
    return INHERENT_GENDER.get(concept_id, "m")


def add_ending(stem: str, ending: str) -> str:
    """Attach an ending. Merge same vowels (da+am→dam); replace a theme
    vowel only if a nucleus remains (kome+a→koma, ve+o→veo)."""
    if not ending:
        return stem
    if stem and stem[-1] in "aeiou" and ending[0] in "aeiou":
        chopped = stem[:-1]
        if stem[-1] == ending[0] or any(c in "aeiou" for c in chopped):
            stem = chopped
    return stem + ending


def verb_stem(infinitive: str) -> str:
    inf = infinitive.lower()
    for theme, suf in (
        ("a", "are"), ("e", "ere"), ("i", "ire"),
        ("a", "ari"), ("i", "iri"), ("e", "eri"),
    ):
        if inf.endswith(suf):
            left = inf[: -len(suf)]
            if any(c in "aeiou" for c in left):
                return left
            if left:
                return left + theme  # dare → da, not d
    for suf in ("ar", "er", "ir"):
        left = inf[: -len(suf)]
        if inf.endswith(suf) and any(c in "aeiou" for c in left):
            return left
    if inf.endswith("r") and len(inf) > 1:
        stem = inf[:-1]
        if any(c in "aeiou" for c in stem):
            return stem
    return inf


def endings_for_lang(lang: str) -> dict[str, str]:
    """Paradigm of that lect. Missing lang is a bug, not a sister fallback."""
    if lang not in VERB_TEMPLATES:
        raise KeyError(f"no conjugation table for {lang!r}")
    tmpl = VERB_TEMPLATES[lang]
    return {slot: to_orthography(seq) for slot, seq in zip(VERB_SLOTS, tmpl)}


def inflect_verb(
    infinitive: str,
    person: str,
    tense: str,
    verb_endings: dict[str, str],
    source_lang: str | None = None,
) -> str:
    endings = endings_for_lang(source_lang) if source_lang else verb_endings
    slot = f"{tense}_{person}"
    stem = verb_stem(infinitive)
    ending = endings.get(slot, "")
    if ending and stem.endswith(ending):
        return stem
    return add_ending(stem, ending)


def inflect_noun(
    stem: str,
    gender: str,
    number: str,
    noun_endings: dict[str, str],
    case: str = "nom",
) -> str:
    slot = f"{gender}_{case}_{number}"
    fallback = "o" if gender == "m" else "a"
    if case == "acc":
        fallback = "on" if gender == "m" else "an"
    elif case == "gen":
        fallback = "is" if gender == "m" else "es"
    return add_ending(stem, noun_endings.get(slot, fallback))


def inflect_adj(
    stem: str,
    gender: str,
    number: str,
    adj_endings: dict[str, str],
    case: str = "nom",
) -> str:
    slot = f"{gender}_{case}_{number}"
    return add_ending(stem, adj_endings.get(slot, "o" if gender == "m" else "a"))


def article(gender: str, number: str = "sg") -> str:
    return ARTICLES[f"{gender}_{number}"]


def copula(person: str) -> str:
    return COPULA_PRS.get(person, COPULA_PRS["3sg"])


def _subject_person(tokens: list[str]) -> str:
    for tok in tokens:
        if tok in PERSON_OF:
            return PERSON_OF[tok]
    return "3sg"


def realize_sentence(
    tokens: list[str],
    roots: dict[str, dict],
    verb_endings: dict[str, str],
    adj_endings: dict[str, str],
    candidates: dict | None = None,
    noun_endings: dict[str, str] | None = None,
) -> list[dict[str, str]]:
    """
    tokens → list of {form, src, concept, role}.
    def_art is not a word: it triggers o/a on the following noun.
    """
    person = _subject_person(tokens)
    out: list[dict[str, str]] = []
    pending_art = False
    np_gender = "m"

    for i, tok in enumerate(tokens):
        if tok == "def_art":
            pending_art = True
            continue

        pos = _POS.get(tok, "")
        root = roots.get(tok, {})
        stem = root.get("orthography", tok)
        src = root.get("source_lang", "?")

        if pos == "noun":
            np_gender = gender_of(tok)
            closed = set(ARTICLES.values()) | set(COPULA_PRS.values())
            if stem in closed and candidates and tok in candidates:
                alts = [
                    c for c in candidates[tok]
                    if c.orthography not in closed and c.violations == 0
                ]
                if alts:
                    alt = min(alts, key=lambda c: (c.syllables, -c.support, c.source_lang))
                    stem = alt.orthography
                    src = alt.source_lang
            if pending_art:
                out.append({
                    "form": article(np_gender),
                    "src": "pt",
                    "concept": "def_art",
                    "role": "art",
                })
                pending_art = False
            if noun_endings:
                stem = inflect_noun(stem, np_gender, "sg", noun_endings, case="nom")
            out.append({"form": stem, "src": src, "concept": tok, "role": "noun"})
            continue

        if pos == "adj":
            form = inflect_adj(stem, np_gender, "sg", adj_endings, case="nom")
            out.append({"form": form, "src": src, "concept": tok, "role": "adj"})
            continue

        if tok == "copula":
            out.append({
                "form": copula(person),
                "src": "pt",
                "concept": "copula",
                "role": "cop",
            })
            continue

        if pos == "verb":
            form = inflect_verb(stem, person, "prs", verb_endings, source_lang=src)
            out.append({"form": form, "src": src, "concept": tok, "role": "verb"})
            continue

        out.append({"form": stem, "src": src, "concept": tok, "role": pos or "x"})

    return out


def form_syllables(form: str) -> int:
    return count_syllables(from_orthography(form))
