"""Phonology data shared by the Python implementation.

These are transcription and spelling conventions, not a closed Vulgultra
inventory.  The inventory itself is measured from the active meaning grid;
see grammar.tex, chapters 2 and 4.
"""

from __future__ import annotations


# grammar.tex Table 2.5: the conventional spelling of an observed segment.
IPA_TO_ORTHO: dict[str, str] = {
    "p": "p", "b": "b", "t": "t", "d": "d", "k": "k", "ɡ": "g",
    "m": "m", "n": "n", "f": "f", "v": "v", "s": "s", "z": "z",
    "ʃ": "x", "t͡ʃ": "c", "l": "l", "r": "r", "j": "y", "w": "w",
    "a": "a", "e": "e", "i": "i", "o": "o", "u": "u",
}
ORTHO_TO_IPA: dict[str, str] = {v: k for k, v in IPA_TO_ORTHO.items()}


# Epitran backends used by the source-language evidence.  Sister lects use
# branch G2P only as a transcription fallback; they do not become the source.
LANG_CODES: dict[str, str] = {
    "es": "spa-Latn", "pt": "por-Latn", "gl": "glg-Latn",
    "an": "spa-Latn", "ast": "spa-Latn", "ext": "spa-Latn",
    "lad": "spa-Latn", "mwl": "por-Latn",
    "oc": "oci-Latn", "ca": "cat-Latn", "gsc": "oci-Latn",
    "fr": "fra-Latn", "wa": "fra-Latn", "pcd": "fra-Latn",
    "nrf": "fra-Latn", "gallo": "fra-Latn", "frp": "fra-Latn",
    "lmo": "ita-Latn", "pms": "ita-Latn", "lij": "lij-Latn",
    "eml": "ita-Latn", "rgn": "ita-Latn",
    "it": "ita-Latn", "scn": "ita-Latn", "vec": "ita-Latn",
    "co": "ita-Latn", "ist": "ita-Latn", "dlm": "ita-Latn",
    "rm": "ita-Latn", "fur": "ita-Latn", "lld": "ita-Latn",
    "sc": "sro-Latn",
    "ro": "ron-Latn", "rup": "ron-Latn", "ruo": "ron-Latn", "ruq": "ron-Latn",
    "la": "ita-Latn",  # reserved ancestor, useful only to legacy callers
}


# Typographic slips in backend output; no claim about any lect.
# Occitan emits ASCII g for IPA ɡ; Galician puts the affricate tie bar last.
BACKEND_TYPOS: tuple[tuple[str, str], ...] = (("g", "ɡ"), ("tʃ͡", "t͡ʃ"))

# What a borrowed backend leaves untranscribed, per lect: leftover → reading.
# A leftover is a source letter the backend does not know, or the base
# letter it did convert plus the diacritic it left behind (French è comes
# out as ə + grave). Each reading is the letter's value in that lect's own
# orthography; docs/sources_orthography.md gives the source for each. Only
# leftovers seen in the grid are listed; anything else is rejected by name
# in g2p.transcribe_and_repair, not guessed.
_OIL_E = {"ə̀": "ɛ", "ə̂": "ɛ"}          # è, ê
_STRESS_ONLY = {"é": "e", "í": "i", "ú": "u", "à": "a", "á": "a"}
BACKEND_LEFTOVERS: dict[str, dict[str, str]] = {
    "fr": {**_OIL_E, "ù": "u"},            # où
    "frp": _OIL_E,
    "gallo": _OIL_E,
    "nrf": {**_OIL_E, "ù": "u", "â": "a"},  # oî read wa, circumflex left on a
    "pcd": {**_OIL_E, "œ́": "we"},          # oé, the Picard reflex of French oi
    "wa": {**_OIL_E, "å": "ɔ"},
    # Quality is already transcribed (è → ɛ, ó → u); the accent left over
    # marks stress only.
    "oc": _STRESS_ONLY,
    "gsc": _STRESS_ONLY,
    "gl": {"ú": "u", "j́": "i"},           # í beside a vowel is a full vowel
    # Eastern digraphs the Romanian backend reads letter by letter (lj comes
    # out as l + ʒ). Listed before ž so a real l + ž is not caught.
    "rup": {"sh": "ʃ", "ts": "t͡s", "dz": "d͡z", "lʒ": "ʎ"},
    "ruq": {"ts": "t͡s", "dz": "d͡z", "lʒ": "ʎ"},
    # Istro-Romanian in its Croatian-based spelling: j is the glide, which
    # the Romanian backend reads ʒ; ž is the fricative. The affricate the
    # backend makes of ge, gi is listed so its ʒ is left alone.
    "ruo": {
        "d͡ʒ": "d͡ʒ", "lʒ": "ʎ", "nʒ": "ɲ", "ʒ": "j",
        "š": "ʃ", "ž": "ʒ", "ǩ": "t͡ʃ", "å": "ɒ", "ę": "æ",
    },
    # ć; a marked s is the voiced one; macron = length.
    "eml": {"ṅ": "ŋ", "ḱ": "t͡ʃ", "ṣ": "z", "ū": "u", "ī": "i", "ō": "o"},
    # ẓ comes out as s + dot. ë and ö are centring diphthongs, one syllable.
    "rgn": {"ṣ": "ð", "ș": "z", "ş": "z", "ọ": "o", "ë": "ɛ", "ö": "ɔ", "ã": "ə̃"},
    "fur": {"ķ": "t͡ʃ"},                    # ç
    "ca": {"ķ": "s"},
    "lad": {"ķ": "s"},
    "lmo": {"ö": "ø", "ü": "y"},
    "lld": {"ö": "ø", "ü": "y", "ë": "ɐ"},
    "pms": {"ë": "ə"},
}

# A column that mixes two spellings. A form with a letter only the backend's
# own spelling has is already read correctly and takes no leftover readings.
# The Istro-Romanian column is part Croatian-based, part Romanian.
BACKEND_NATIVE_LETTERS: dict[str, str] = {"ruo": "ăîșț"}
