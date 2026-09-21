"""Native declension/conjugation per lect.

Every SOURCE_LANGS code has its own person table. Realization never
falls back to “conjugate like Spanish” for Aragonese, Ladino, Romansh, etc.
Tense/mood is a theme on that same person row (one stem, one lect).
"""

from __future__ import annotations

from lacyo.phonology import from_orthography, last_syllable, to_orthography


def _one_sigma(s: str) -> str:
    """Force a 1σ ending: keep the last syllable of an attested cell."""
    return to_orthography(last_syllable(from_orthography(s)))


def _row(*cells: str) -> list[list[str]]:
    return [from_orthography(_one_sigma(c)) for c in cells]


# Reverse Vulgar Latin case on a lect theme vowel.
# Slots: m_nom_sg m_acc_sg m_gen_sg m_nom_pl m_acc_pl m_gen_pl
#        f_nom_sg f_acc_sg f_gen_sg f_nom_pl f_acc_pl f_gen_pl
# Acc.sg restores -m as -n; gen.sg -is/-es undoes the VL gen=nom.pl merger;
# acc.pl keeps the lect's -s plural; gen.pl clips Latin -ōrum/-ārum.
def _case_block(m: str, f: str, m_acc_pl: str, f_acc_pl: str) -> list[list[str]]:
    def with_vowel(cell: str, theme: str) -> str:
        if any(ch in "aeiou" for ch in cell):
            return cell
        return theme + cell

    def acc_sg(theme: str) -> str:
        if theme[-1] not in "aeiou":
            return theme[:-1] + "n"  # us → un, el → en
        return theme + "n"

    return _row(
        m, acc_sg(m), "is", "i", with_vowel(m_acc_pl, m), "or",
        f, acc_sg(f), "es", "e", with_vowel(f_acc_pl, f), "ar",
    )


NOUN_TEMPLATES: dict[str, list[list[str]]] = {
    "es": _case_block("o", "a", "os", "as"),
    "pt": _case_block("o", "a", "os", "as"),
    "gl": _case_block("o", "a", "os", "as"),
    "an": _case_block("o", "a", "os", "as"),
    "ext": _case_block("u", "a", "us", "as"),
    "lad": _case_block("o", "a", "os", "as"),
    "mwl": _case_block("o", "a", "os", "as"),
    "ast": _case_block("u", "a", "os", "es"),
    "it": _case_block("o", "a", "os", "as"),
    "scn": _case_block("u", "a", "os", "as"),
    "vec": _case_block("o", "a", "os", "as"),
    "lmo": _case_block("o", "a", "os", "as"),
    "pms": _case_block("o", "a", "os", "as"),
    "lij": _case_block("o", "a", "os", "as"),
    "fur": _case_block("i", "e", "s", "is"),
    "eml": _case_block("o", "a", "os", "as"),
    "lld": _case_block("e", "a", "es", "es"),
    "ist": _case_block("o", "a", "os", "as"),
    "ca": _case_block("e", "a", "s", "es"),
    "oc": _case_block("e", "a", "s", "es"),
    "gsc": _case_block("e", "a", "s", "es"),
    "fr": _case_block("e", "a", "s", "s"),
    "wa": _case_block("e", "a", "s", "s"),
    "pcd": _case_block("e", "a", "s", "s"),
    "nrm": _case_block("e", "a", "s", "s"),
    "frp": _case_block("o", "a", "s", "s"),
    "glw": _case_block("e", "a", "s", "s"),
    "ro": _case_block("u", "a", "i", "e"),
    "rup": _case_block("u", "a", "i", "e"),
    "ruo": _case_block("u", "a", "i", "e"),
    "sc": _case_block("u", "a", "os", "as"),
    "rm": _case_block("el", "a", "s", "s"),
    "la": _case_block("us", "a", "os", "as"),
    "dlm": _case_block("o", "a", "os", "as"),
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
    """Present = person endings of that lect; other tenses = theme + person coda.

    Every cell is clipped to 1σ (amos → mos): the extra syllable is a theme
    already on the stem, reverse of VL theme-vowel fusion.
    """
    out: list[list[str]] = []
    for theme, series in (
        ("", persons),
        (pst, persons),
        (fut, persons),
    ):
        for p in series:
            cell = p if not theme else (theme + p[-1] if len(p) > 1 else theme + p)
            out.append(from_orthography(_one_sigma(cell)))
    for p in persons:
        out.append(from_orthography(_one_sigma(subj + (p[-1] if len(p) > 1 else p))))
    for p in persons:
        out.append(from_orthography(_one_sigma("i" + (p[-1] if len(p) > 1 else p))))
    for p in persons:
        out.append(from_orthography(_one_sigma("a" + (p[-1] if len(p) > 1 else p))))
    out.extend(_row("r", "nt", "t", "a", "e"))
    return out


VERB_TEMPLATES: dict[str, list[list[str]]] = {
    lang: _verb_block(persons, *_THEMES[lang])
    for lang, persons in PERSONS.items()
}

# No donor map. Missing lect = bug.
CONJUGATION_DONOR: dict[str, str] = {}

NOUN_SLOT_NAMES = [
    "m_nom_sg", "m_acc_sg", "m_gen_sg", "m_nom_pl", "m_acc_pl", "m_gen_pl",
    "f_nom_sg", "f_acc_sg", "f_gen_sg", "f_nom_pl", "f_acc_pl", "f_gen_pl",
]
ADJ_SLOT_NAMES = NOUN_SLOT_NAMES
