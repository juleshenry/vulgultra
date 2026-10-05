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


# grammar.tex §2.4 keeps all four rhotics, and §2.2 lets a liquid follow an
# obstruent in an onset. PanPhon's features alone miss the uvular ones, so
# French très came out with a repair vowel between t and ʀ.
RHOTICS: tuple[str, ...] = ("r", "ɾ", "ʀ", "ʁ")

# grammar.tex §2.4, reverse Vulgar Latin: in every lect the segment becomes
# the sequence it arose from. Code merges nothing that section does not list.
SEGMENT_MERGES: dict[str, tuple[str, ...]] = {
    "ʎ": ("l", "j"), "ɲ": ("n", "j"), "ʝ": ("j",),
}

# grammar.tex §2.4, not a contrast: a predictable variant of another sound,
# merged only in the lects where it is one. Ladin ɐ is a phoneme and stays.
_OC_VARIANTS = {"β": ("b",), "ɱ": ("n",)}
_PT_VARIANTS = {"ɐ": ("a",), "kʷ": ("k", "w"), "w̃": ("w",), "j̃": ("j",)}
LECT_MERGES: dict[str, dict[str, tuple[str, ...]]] = {
    "oc": _OC_VARIANTS, "gsc": _OC_VARIANTS,
    "gl": {"ʊ": ("o",), "ɪ": ("e",), "ɐ": ("a",)},
    "pt": _PT_VARIANTS, "mwl": _PT_VARIANTS,
}


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

# A second reader, espeak-ng, for the lects where the borrowed Epitran map
# was measured wrong (docs/eval/readers.md): against IE-CoR's transcriptions
# of the same words Epitran reads 93 of 165 French words and 19 of 168
# Portuguese words segment for segment. Lect → voice. Used when the program
# is installed; without it the Epitran backend below still reads the lect.
ESPEAK_VOICES: dict[str, str] = {"fr": "fr-fr", "pcd": "fr-fr", "pt": "pt-pt", "mwl": "pt-pt"}
# A lect's own spellings, rewritten as the voice's language spells that
# sound, in order. Picard: the dot of grain.ne is a spelling device, oé is
# [we], and an infinitive in -tcher ends in [e]. Mirandese: ch is the
# affricate, x the sibilant.
ESPEAK_RESPELL: dict[str, tuple[tuple[str, str], ...]] = {
    "pcd": ((".", ""), ("oé", "oué"), ("oè", "ouè"), ("tcher", "tché")),
    "mwl": (("ch", "tch"), ("x", "ch")),
}
# The voice's notation rewritten in the grid's, as regular expressions over
# decomposed text, in order: stress and length dropped, affricates tied;
# French y before a vowel is the glide; the Portuguese voice writes a nasal
# vowel as vowel + ŋ and a nasal diphthong as two nasal vowels, puts a schwa
# after ɾ before a consonant, and writes ɹ ʊ ɪ ɑ for ɾ u j a.
_VOWEL = "[aeiouyɐɑɛɔœøəɨ]"
_ESPEAK_COMMON = ((r"[ˈˌː\-]", ""), ("tʃ", "t͡ʃ"), ("dʒ", "d͡ʒ"))
ESPEAK_NOTATION: dict[str, tuple[tuple[str, str], ...]] = {
    "fr-fr": (*_ESPEAK_COMMON, ("ʁ", "ʀ"), (rf"y(?={_VOWEL})", "ɥ")),
    "pt-pt": (*_ESPEAK_COMMON, ("ɹ", "ɾ"), ("ʊ", "u"), ("ɪ", "j"), ("ɑ", "a"), ("ɾə", "ɾ"),
              ("ejŋ(?=.)", "e\u0303"), ("ejm(?=[pb])", "e\u0303"),  # nasal e inside a word, a diphthong only at its end
              (rf"({_VOWEL})\u0303?([jw]?)ŋ", "\\1\u0303\\2"),
              ("(\u0303)u\u0303", "\\1w\u0303"), ("(\u0303)[ij]\u0303", "\\1j\u0303"),
              (rf"(?<!{_VOWEL})(?<!\u0303)w$", "u")),
}


# What a borrowed backend leaves untranscribed, per lect: leftover → reading.
# A leftover is a source letter the backend does not know, or the base
# letter it did convert plus the diacritic it left behind (French è comes
# out as ə + grave). Each reading is the letter's value in that lect's own
# orthography; docs/sources_orthography.md gives the source for each. Only
# leftovers seen in the grid are listed; anything else is rejected by name
# in g2p.transcribe_and_repair, not guessed.
_OIL_E = {"ə̀": "ɛ", "ə̂": "ɛ",         # è, ê
          "dʒ": "d͡ʒ", "tʃ": "t͡ʃ"}       # dj, tch: one sound, read as two
_STRESS_ONLY = {"é": "e", "í": "i", "ú": "u", "à": "a", "á": "a"}
# Istro-Romanian letters that mean the same in every one of its spellings.
# The acute is a dictionary's stress mark.
_RUO_LETTERS = {"š": "ʃ", "ž": "ʒ", "ǩ": "t͡ʃ", "å": "ɒ", "ę": "æ", "ľ": "ʎ", "ń": "ɲ",
                "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u"}
BACKEND_LEFTOVERS: dict[str, dict[str, str]] = {
    "fr": {**_OIL_E, "ù": "u"},            # où
    "frp": _OIL_E,
    # ao is the diphthong of dao, iao, chaod; oé and ouè are [we] and [wɛ].
    "gallo": {**_OIL_E, "ao": "aw", "aɔ": "aw", "œ́": "we", "ù": "wɛ"},
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
    # Romanian oa and ea are rising diphthongs, read as two vowels.
    "ro": {"oa": "wa", "ea": "ja"},
    "rup": {"sh": "ʃ", "ts": "t͡s", "dz": "d͡z", "lʒ": "ʎ"},
    "ruq": {"ts": "t͡s", "dz": "d͡z", "lʒ": "ʎ"},
    # Istro-Romanian in its Croatian-based spelling: j is the glide, which
    # the Romanian backend reads ʒ; ž is the fricative. The affricate the
    # backend makes of ge, gi is listed so its ʒ is left alone.
    "ruo": {"d͡ʒ": "d͡ʒ", "lʒ": "ʎ", "nʒ": "ɲ", "ʒ": "j", **_RUO_LETTERS},
    # The same column in Romanian-based or mixed spelling: j is ʒ there.
    "ruo-ro": _RUO_LETTERS,
    # Bolognese spelling: å and ä are vowels of their own, ṡ is the voiced
    # s, final c' and g' are affricates. ć is the same affricate in the
    # Mirandolese spelling.
    "eml": {"ṅ": "ŋ", "ṡ": "z", "å": "ʌ", "ä": "æ", "k'": "t͡s", "ɡ'": "d͡z", "ḱ": "t͡ʃ"},
    # ẓ comes out as s + dot. ë and ö are centring diphthongs, one syllable.
    "rgn": {"ṣ": "ð", "ș": "z", "ş": "z", "ọ": "o", "ë": "ɛ", "ö": "ɔ", "ã": "ə̃"},
    "fur": {"ķ": "t͡ʃ"},                    # ç
    "ca": {"ķ": "s"},
    "lad": {"ķ": "s"},
    "lmo": {"ö": "ø", "ü": "y"},
    "lld": {"ö": "ø", "ü": "y", "ë": "ɐ"},
    # Piedmontese writes /u/ as o, /y/ as u and /ø/ as eu; ò is the open o.
    "pms": {"ë": "ə", "eu": "ø", "o": "u", "u": "y"},
}

# A column that mixes two spellings: lect → (letters only the backend's own
# spelling has, the leftover table for a form that has one). The
# Istro-Romanian column is part Croatian-based, part Romanian-based.
BACKEND_NATIVE_LETTERS: dict[str, tuple[str, str]] = {"ruo": ("ăîșț", "ruo-ro")}
