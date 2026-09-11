"""Native declension/conjugation per lect.

Every SOURCE_LANGS code has its own person table. Realization never
falls back to “conjugate like Spanish” for Aragonese, Ladino, Romansh, etc.
Tense/mood is a theme on that same person row (one stem, one lect).
"""

from __future__ import annotations

from lacyo.phonology import from_orthography


def _row(*cells: str) -> list[list[str]]:
    return [from_orthography(c) for c in cells]


# m_sg, f_sg, m_pl, f_pl
NOUN_TEMPLATES: dict[str, list[list[str]]] = {
    "es": _row("o", "a", "os", "as"),
    "pt": _row("o", "a", "os", "as"),
    "gl": _row("o", "a", "os", "as"),
    "an": _row("o", "a", "os", "as"),
    "ext": _row("u", "a", "us", "as"),
    "lad": _row("o", "a", "os", "as"),
    "mwl": _row("o", "a", "os", "as"),
    "ast": _row("u", "a", "os", "es"),
    "it": _row("o", "a", "i", "e"),
    "scn": _row("u", "a", "i", "i"),
    "vec": _row("o", "a", "i", "e"),
    "lmo": _row("o", "a", "i", "e"),
    "pms": _row("o", "a", "i", "e"),
    "lij": _row("o", "a", "i", "e"),
    "fur": _row("i", "e", "s", "is"),
    "eml": _row("o", "a", "i", "e"),
    "lld": _row("e", "a", "es", "es"),
    "ist": _row("o", "a", "i", "e"),
    "ca": _row("e", "a", "s", "es"),
    "oc": _row("e", "a", "s", "es"),
    "gsc": _row("e", "a", "s", "es"),
    "fr": _row("e", "e", "s", "s"),
    "wa": _row("e", "e", "s", "s"),
    "pcd": _row("e", "e", "s", "s"),
    "nrm": _row("e", "e", "s", "s"),
    "frp": _row("o", "a", "s", "s"),
    "glw": _row("e", "e", "s", "s"),
    "ro": _row("u", "a", "i", "e"),
    "rup": _row("u", "a", "i", "e"),
    "ruo": _row("u", "a", "i", "e"),
    "sc": _row("u", "a", "os", "as"),
    "rm": _row("el", "a", "s", "s"),
    "la": _row("us", "a", "i", "ae"),
    "dlm": _row("o", "a", "i", "e"),
}

ADJ_TEMPLATES = NOUN_TEMPLATES

# Person order matches VERB_SLOTS: 1sg, 1pl, 2sg, 2pl, 3sg, 3pl
# Distinctive cells kept even at 2σ (amos, amus, ein, atz).
PERSONS: dict[str, tuple[str, ...]] = {
    "es": ("o", "mos", "as", "is", "a", "an"),
    "pt": ("o", "mos", "as", "is", "a", "am"),
    "gl": ("o", "mos", "as", "des", "a", "an"),
    "an": ("o", "amos", "as", "az", "a", "an"),       # Aragonese 2pl -az
    "ast": ("o", "amos", "es", "ais", "a", "en"),
    "ext": ("o", "amos", "as", "ais", "a", "an"),
    "lad": ("o", "amos", "as", "ax", "a", "an"),       # Ladino 2pl -ásh → ax (/ʃ/)
    "mwl": ("o", "amos", "as", "ais", "a", "an"),
    "it": ("o", "amo", "i", "ate", "a", "ano"),
    "scn": ("u", "amu", "i", "ati", "a", "anu"),
    "vec": ("o", "emo", "i", "e", "a", "a"),           # 3sg = 3pl
    "lmo": ("i", "om", "et", "ii", "a", "en"),
    "pms": ("o", "oma", "e", "e", "a", "o"),
    "lij": ("o", "amo", "i", "ae", "a", "an"),
    "fur": ("i", "in", "is", "is", "e", "in"),
    "eml": ("o", "em", "i", "iv", "a", "en"),
    "lld": ("e", "on", "es", "eis", "a", "on"),
    "ist": ("o", "emo", "i", "e", "a", "a"),
    "ca": ("o", "em", "es", "eu", "a", "en"),
    "oc": ("i", "am", "as", "atz", "a", "an"),         # Occitan 1sg -i, 2pl -atz
    "gsc": ("i", "am", "as", "atz", "a", "an"),
    "fr": ("e", "on", "es", "ez", "e", "ent"),
    "wa": ("e", "ans", "es", "oz", "e", "nut"),        # Walloon 2pl -oz, 3pl -nut
    "pcd": ("e", "ons", "es", "ez", "e", "tte"),
    "nrm": ("e", "ons", "es", "ez", "e", "ent"),
    "frp": ("o", "ens", "as", "ed", "e", "ont"),
    "glw": ("e", "ons", "es", "ez", "e", "ent"),
    "ro": ("u", "em", "i", "ats", "e", "u"),
    "rup": ("u", "am", "i", "ats", "e", "u"),
    "ruo": ("u", "em", "i", "ets", "e", "u"),
    "sc": ("o", "amus", "as", "ades", "at", "ant"),    # Sardinian 3sg -at
    "rm": ("el", "ein", "as", "eis", "a", "an"),       # Romansh 1sg -el
    "la": ("o", "mus", "s", "tis", "t", "nt"),         # Latin
    "dlm": ("o", "mo", "s", "te", "a", "nu"),
}

# Past / future / subjunctive themes by lect (not borrowed wholesale).
_THEMES: dict[str, tuple[str, str, str]] = {
    "es": ("i", "ra", "e"), "pt": ("i", "ra", "e"), "gl": ("i", "ra", "e"),
    "an": ("i", "ra", "e"), "ast": ("i", "ra", "e"), "ext": ("i", "ra", "e"),
    "lad": ("i", "ra", "e"), "mwl": ("i", "ra", "e"),
    "it": ("e", "re", "i"), "scn": ("e", "ri", "i"), "vec": ("e", "ra", "i"),
    "lmo": ("e", "ra", "i"), "pms": ("e", "ra", "e"), "lij": ("e", "re", "i"),
    "fur": ("e", "ar", "i"), "eml": ("e", "ra", "i"), "lld": ("e", "ra", "e"),
    "ist": ("e", "ra", "i"),
    "ca": ("i", "re", "i"), "oc": ("e", "ra", "e"), "gsc": ("e", "ra", "e"),
    "fr": ("e", "ra", "i"), "wa": ("e", "ra", "i"), "pcd": ("e", "ra", "i"),
    "nrm": ("e", "ra", "i"), "frp": ("e", "ra", "e"), "glw": ("e", "ra", "i"),
    "ro": ("i", "re", "e"), "rup": ("i", "re", "e"), "ruo": ("i", "re", "e"),
    "sc": ("e", "ai", "e"), "rm": ("e", "ar", "e"), "la": ("ba", "bi", "a"),
    "dlm": ("e", "ra", "i"),
}


def _verb_block(persons: tuple[str, ...], pst: str, fut: str, subj: str) -> list[list[str]]:
    """Present = person endings of that lect; other tenses = theme + person coda."""
    out: list[list[str]] = []
    for theme, series in (
        ("", persons),
        (pst, persons),
        (fut, persons),
    ):
        for p in series:
            cell = p if not theme else (theme + p[-1] if len(p) > 1 else theme + p)
            out.append(from_orthography(cell))
    for p in persons:
        out.append(from_orthography(subj + (p[-1] if len(p) > 1 else p)))
    for p in persons:
        out.append(from_orthography("i" + (p[-1] if len(p) > 1 else p)))
    for p in persons:
        out.append(from_orthography("a" + (p[-1] if len(p) > 1 else p)))
    out.extend(_row("r", "nt", "t", "a", "e"))
    return out


VERB_TEMPLATES: dict[str, list[list[str]]] = {
    lang: _verb_block(persons, *_THEMES[lang])
    for lang, persons in PERSONS.items()
}

# No donor map. Missing lect = bug.
CONJUGATION_DONOR: dict[str, str] = {}

NOUN_SLOT_NAMES = ["m_sg", "f_sg", "m_pl", "f_pl"]
ADJ_SLOT_NAMES = NOUN_SLOT_NAMES
