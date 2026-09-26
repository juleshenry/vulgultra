"""Morphology constants and provenance.

The tables implement the closed choices in grammar.tex chapter 3.  The
theme is a branch-level class; the case layer is shared and Latin-derived.
"""

from __future__ import annotations


# grammar.tex §3.1: one theme block per source lect; no sister fallback.
THEME_CLASS: dict[str, str] = {
    "es": "o", "pt": "o", "gl": "o", "an": "o", "lad": "o", "mwl": "o",
    "ast": "u", "ext": "u", "oc": "e", "ca": "e", "gsc": "e",
    "fr": "e", "wa": "e", "pcd": "e", "nrf": "e", "gallo": "e",
    "frp": "o", "lmo": "o", "pms": "o", "lij": "o", "eml": "o", "rgn": "o",
    "it": "o", "vec": "o", "ist": "o", "dlm": "o", "scn": "u", "co": "u",
    "rm": "e", "fur": "e", "lld": "e", "sc": "u",
    "ro": "u", "rup": "u", "ruo": "u", "ruq": "u",
}

CLOSED_NOUN_THEMES = ("o", "u", "e")

# grammar.tex §3.1 and §3.3: slots are stable JSON/Rust interchange names.
NOUN_SLOT_NAMES = [
    "m_nom_sg", "m_acc_sg", "m_gen_sg", "m_nom_pl", "m_acc_pl", "m_gen_pl",
    "f_nom_sg", "f_acc_sg", "f_gen_sg", "f_nom_pl", "f_acc_pl", "f_gen_pl",
]
ADJ_SLOT_NAMES = NOUN_SLOT_NAMES

ARTICLES = {"m_sg": "o", "f_sg": "a", "m_pl": "os", "f_pl": "as"}
COPULA_PRS = {"1sg": "so", "1pl": "som", "2sg": "es", "2pl": "sos", "3sg": "e", "3pl": "son"}
PERSON_OF = {"i": "1sg", "we": "1pl", "you_sg": "2sg", "you_pl": "2pl", "he": "3sg", "they": "3pl"}
