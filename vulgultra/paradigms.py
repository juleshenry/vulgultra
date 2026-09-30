"""Attested lect paradigms plus productive, grid-segment ending proposals.

Attested verb person cells keep the lect's whole ending (amos stays amos);
noun/adjective case cells are clipped to 1σ. The optimizer
may mix lects across cells and uses concordance (shared person coda across
tenses) only as a length tie-breaker. Productive alternatives are assembled
separately from the observed shortlisted segment inventory. Realization
never falls back to “conjugate like Spanish” for Aragonese, Ladino,
Romansh, etc.
"""

from __future__ import annotations

from collections.abc import Iterable

from vulgultra.phonology import (
    from_orthography, last_syllable, to_orthography,
)
from vulgultra.morphology_constants import (
    CLOSED_NOUN_THEMES, NOUN_SLOT_NAMES, ADJ_SLOT_NAMES, THEME_CLASS,
)


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


def closed_noun_blocks() -> dict[str, list[list[str]]]:
    """Spec table on each theme. Adjectives use the same cells."""
    return {
        theme: _case_block(theme, "a", theme + "s", "as")
        for theme in CLOSED_NOUN_THEMES
    }


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
    "rgn": _case_block("o", "a", "os", "as"),
    "lld": _case_block("e", "a", "es", "es"),
    "ist": _case_block("o", "a", "os", "as"),
    "co": _case_block("u", "a", "i", "e"),
    "ca": _case_block("e", "a", "s", "es"),
    "oc": _case_block("e", "a", "s", "es"),
    "gsc": _case_block("e", "a", "s", "es"),
    "fr": _case_block("e", "a", "s", "s"),
    "wa": _case_block("e", "a", "s", "s"),
    "pcd": _case_block("e", "a", "s", "s"),
    "nrf": _case_block("e", "a", "s", "s"),
    "frp": _case_block("o", "a", "s", "s"),
    "gallo": _case_block("e", "a", "s", "s"),
    "ro": _case_block("u", "a", "i", "e"),
    "rup": _case_block("u", "a", "i", "e"),
    "ruo": _case_block("u", "a", "i", "e"),
    "ruq": _case_block("u", "a", "i", "e"),
    "sc": _case_block("u", "a", "os", "as"),
    "rm": _case_block("el", "a", "s", "s"),
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
    "rgn": ("a", "en", "e", "i", "a", "a"),           # Romagnol 1sg -a, 1pl -en, 3sg=3pl
    "lld": ("e", "on", "es", "eis", "a", "on"),
    "ist": ("o", "emo", "i", "e", "a", "a"),
    "co": ("u", "emu", "i", "ate", "a", "anu"),        # Corsican 1pl -emu vs Italian -amo
    "ca": ("o", "em", "es", "eu", "a", "en"),
    "oc": ("i", "am", "as", "atz", "a", "an"),         # Occitan 1sg -i, 2pl -atz
    "gsc": ("i", "am", "as", "atz", "a", "an"),
    "fr": ("e", "on", "es", "ez", "e", "ent"),
    "wa": ("e", "ans", "es", "oz", "e", "nut"),        # Walloon 2pl -oz, 3pl -nut
    "pcd": ("e", "ons", "es", "ez", "e", "tte"),
    "nrf": ("e", "ons", "es", "ez", "e", "ent"),
    "frp": ("o", "ens", "as", "ed", "e", "ont"),
    "gallo": ("e", "ons", "es", "ez", "e", "ent"),
    "ro": ("u", "em", "i", "ats", "e", "u"),
    "rup": ("u", "am", "i", "ats", "e", "u"),
    "ruo": ("u", "em", "i", "ets", "e", "u"),
    "ruq": ("u", "um", "i", "ats", "a", "u"),          # Megleno 1pl -um
    "sc": ("o", "amus", "as", "ades", "at", "ant"),    # Sardinian 3sg -at
    "rm": ("el", "ein", "as", "eis", "a", "an"),       # Romansh 1sg -el
    "dlm": ("o", "mo", "s", "te", "a", "nu"),
}

# Past / future / subjunctive themes by lect (not borrowed wholesale).
_THEMES: dict[str, tuple[str, str, str]] = {
    "es": ("i", "ra", "e"), "pt": ("i", "ra", "e"), "gl": ("i", "ra", "e"),
    "an": ("i", "ra", "e"), "ast": ("i", "ra", "e"), "ext": ("i", "ra", "e"),
    "lad": ("i", "ra", "e"), "mwl": ("i", "ra", "e"),
    "it": ("e", "re", "i"), "scn": ("e", "ri", "i"), "vec": ("e", "ra", "i"),
    "lmo": ("e", "ra", "i"), "pms": ("e", "ra", "e"), "lij": ("e", "re", "i"),
    "fur": ("e", "ar", "i"), "eml": ("e", "ra", "i"), "rgn": ("e", "ra", "i"),
    "lld": ("e", "ra", "e"),
    "ist": ("e", "ra", "i"), "co": ("e", "re", "i"),
    "ca": ("i", "re", "i"), "oc": ("e", "ra", "e"), "gsc": ("e", "ra", "e"),
    "fr": ("e", "ra", "i"), "wa": ("e", "ra", "i"), "pcd": ("e", "ra", "i"),
    "nrf": ("e", "ra", "i"), "frp": ("e", "ra", "e"), "gallo": ("e", "ra", "i"),
    "ro": ("i", "re", "e"), "rup": ("i", "re", "e"), "ruo": ("i", "re", "e"),
    "ruq": ("i", "re", "e"),
    "sc": ("e", "ai", "e"), "rm": ("e", "ar", "e"),
    "dlm": ("e", "ra", "i"),
}


def _verb_block(persons: tuple[str, ...], pst: str, fut: str, subj: str) -> list[list[str]]:
    """Present = person endings of that lect; other tenses = theme + person coda.

    Verb cells keep the attested ending whole (amos stays amos, no 1σ
    clipping); the optimizer's syllable term still prefers shorter cells
    among candidates. Only noun/adjective case cells are clipped.
    """
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
    out.extend(from_orthography(nf) for nf in ("r", "nt", "t", "a", "e"))
    return out


VERB_TEMPLATES: dict[str, list[list[str]]] = {
    lang: _verb_block(persons, *_THEMES[lang])
    for lang, persons in PERSONS.items()
}


def productive_grid_blocks(
    segments: Iterable[str],
) -> tuple[list[list[str]], list[list[str]]]:
    """Build productive 1σ tables from segments in the shortlisted grid.

    Productive shapes stay 1σ for both nouns and verbs: they are assembled
    proposals, not attested endings, so they never earn a second syllable.

    These are *combinations* of observed segments, not attested morphemes or
    claims about any source lect's morphology. Candidate shapes are V, CV,
    VC, and CVC; the ordinary phonotactic validator filters the pool.
    """
    from vulgultra.phonology import count_syllables, count_violations, is_vowel

    observed = set(segments)
    vowels = sorted(p for p in observed if is_vowel(p))
    consonants = sorted(observed - set(vowels))
    if not vowels:
        return [], []

    pool: set[tuple[str, ...]] = {(v,) for v in vowels}
    pool.update((c, v) for c in consonants for v in vowels)
    pool.update((v, c) for v in vowels for c in consonants)
    pool.update((c1, v, c2) for c1 in consonants for v in vowels for c2 in consonants)
    forms = sorted(
        (form for form in pool
         if count_syllables(list(form)) == 1 and count_violations(list(form)) == 0),
        key=lambda form: (len(form), form),
    )
    if not forms:
        return [], []

    def choose_block(size: int) -> list[list[str]]:
        # Greedy novelty fill. No minimum-distance constraint: nouns never
        # had one, and finite verb rows no longer do (syncretism is legal).
        chosen: list[tuple[str, ...]] = []
        used: set[tuple[str, ...]] = set()
        covered: set[str] = set()
        for _slot in range(size):
            available = [form for form in forms if form not in used] or forms
            form = min(
                available,
                key=lambda candidate: (-len(set(candidate) - covered), len(candidate), candidate),
            )
            chosen.append(form)
            used.add(form)
            covered.update(form)
        return [list(form) for form in chosen]

    # Noun/adjective table has 12 gender × case × number cells. The verb
    # block has six 6-person rows followed by five non-finite cells.
    return choose_block(12), choose_block(41)

# No donor map. Missing lect = bug.
CONJUGATION_DONOR: dict[str, str] = {}

# Re-exported above for callers that historically imported these from here.
