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
