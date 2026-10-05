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
ESPEAK_VOICES: dict[str, str] = {
    "fr": "fr-fr", "pcd": "fr-fr", "pt": "pt-pt", "mwl": "pt-pt",
    "es": "es", "an": "an", "ca": "ca", "it": "it",
}
# A lect's own spellings that its reader would misread, rewritten before it
# reads: regular expressions, in order. The target is the reader language's
# spelling of the sound or, between ⟨ ⟩, the sound itself, which is kept
# from the reader; a word with a kept sound is read by Epitran, not by a
# voice. A key lect:pos replaces the lect's table for that part of speech.
# docs/sources_orthography.md gives the source for each table.
_RO_VOWEL = "[aeiouăâî]"
_WA_V = "aeiouàâåéèêëîïôöûü"   # Walloon vowel letters; y is a consonant
# s before a consonant in Romansh and Ladin.
_S_IMPURA = (("s(?=[ptckqf])", "⟨ʃ⟩"), ("s(?=[bdgvlmnr])", "⟨ʒ⟩"))
_Z_TS = (("z+", "⟨t͡s⟩"),)
_FRP = ((rf"en(?![{_WA_V}yn])", "in"), ("(?<![qgo])u(?=[eèéê])", "ou"), ("oa", "oua"))
# Spain's c, z and ll, which the Spanish map reads as American s and y.
_CASTILIAN = (("z", "⟨θ⟩"), ("c(?=[eiéí])", "⟨θ⟩"), ("ll", "⟨ʎ⟩"))
RESPELL: dict[str, tuple[tuple[str, str], ...]] = {
    # Asturian x is ʃ and ḥ an aspirate.
    "ast": (*_CASTILIAN, ("x", "⟨ʃ⟩"), ("ḥ", "⟨h⟩")),
    # Extremaduran h, j, and g before e i, are the aspirate.
    "ext": (*_CASTILIAN, ("(?<!c)h", "⟨h⟩"), ("j", "⟨h⟩"), ("g(?=[eiéí])", "⟨h⟩")),
    # Ladino in the Aki Yerushalayim spelling: sh x = ʃ, dj = d͡ʒ, j = ʒ,
    # z = z, ny = ɲ, h = x, and g is always hard.
    "lad": (("sh|x", "⟨ʃ⟩"), ("dj", "⟨d͡ʒ⟩"), ("j", "⟨ʒ⟩"), ("z", "⟨z⟩"), ("ny", "⟨ɲ⟩"),
            ("(?<!c)h", "⟨x⟩"), ("g(?=[eiéí])", "⟨ɡ⟩")),
    # Occitan and Gascon qu is k.
    "oc": (("qu", "⟨k⟩"),), "gsc": (("qu", "⟨k⟩"),),
    # Picard: the dot of grain.ne is a spelling device, oé is [we], and an
    # infinitive in -tcher ends in [e].
    "pcd": ((r"\.", ""), ("oé", "oué"), ("oè", "ouè"), ("tcher", "tché")),
    # Mirandese: ch is the affricate, x the sibilant.
    "mwl": (("ch", "tch"), ("x", "ch")),
    "scn": _Z_TS, "co": _Z_TS,
    # Piedmontese u after a vowel is the glide of a diphthong (giàun).
    "pms": (("(?<=[aàoòó])u", "⟨w⟩"),),
    # Milanese z is a plain sibilant today.
    "lmo": (("z+", "⟨s⟩"),),
    "ist": (("z", "⟨z⟩"),),
    # Bolognese z and ż, and Romagnol z, are the dental fricatives.
    "eml": (("z", "⟨θ⟩"), ("ż", "⟨ð⟩")),
    "rgn": (("z", "⟨θ⟩"),),
    # Friulian cj and gj are the palatal stops; z is voiced at the start
    # of a word; a final sc is s + k.
    "fur": (("cj", "⟨c⟩"), ("gj", "⟨ɟ⟩"), ("sc$", "⟨sk⟩"), ("^z", "⟨d͡ʒ⟩"), ("z", "⟨t͡s⟩")),
    # Ladin: sc before e i and at the end of a word is ʃ, as is s before a
    # consonant; z and tz are t͡s.
    "lld": (("sc(?=[eiéèëìí]|$)", "⟨ʃ⟩"), *_S_IMPURA, ("tz|z+", "⟨t͡s⟩")),
    # Jèrriais th is [ð]; aun is the nasal of French an.
    "nrf": (("th", "⟨ð⟩"), ("aun", "an")),
    # Franco-Provençal in ORB: en is [ɛ̃], ue and oa begin with [w]; the r
    # of an infinitive in -ar, -ér, -ir is silent.
    "frp": _FRP, "frp:verb": (*_FRP, ("(?<=[aâéêiî])r$", "")),
    # Walloon: the -er of an infinitive is [e]; mer, vier and noer keep their r.
    "wa": ((rf"^(.*[{_WA_V}].*[^{_WA_V}])er$", "\\1é"),),
    # Rumantsch Grischun: tg, and ch before a o u, are the palatal affricate;
    # gl before i or at the end of a word, and gli before a vowel, the
    # palatal l; s before a consonant is ʃ or ʒ and between vowels z; c
    # before e i, and z, are t͡s.
    "rm": (("tsch", "⟨t͡ʃ⟩"), ("sch", "⟨ʃ⟩"), ("c(?=[ei])", "⟨t͡s⟩"), ("z+", "⟨t͡s⟩"), *_S_IMPURA,
           ("(?<=[aeiou])s(?=[aeiou])", "⟨z⟩"), ("tg", "⟨t͡ɕ⟩"), ("ch(?=[aou])", "⟨t͡ɕ⟩"),
           ("gli(?=[aeou])", "⟨ʎ⟩"), ("gl(?=i|s?$)", "⟨ʎ⟩")),
    # Romanian: a final i after a consonant is not a syllable (ochi [okʲ],
    # cinci [t͡ʃint͡ʃ]) unless it is the word's only vowel (zi) or follows a
    # consonant + l or r (negri). An infinitive's final i is stressed.
    "ro": ((rf"^(.*{_RO_VOWEL}.*)chi$", "\\1⟨kʲ⟩"), (rf"^(.*{_RO_VOWEL}.*)ghi$", "\\1⟨ɡʲ⟩"),
           (rf"^(.*{_RO_VOWEL}.*)ci$", "\\1⟨t͡ʃ⟩"), (rf"^(.*{_RO_VOWEL}.*)gi$", "\\1⟨d͡ʒ⟩"),
           (rf"^(.*{_RO_VOWEL}.*(?:(?<={_RO_VOWEL})[lr]|[^aeiouăâîlr]))i$", "\\1⟨ʲ⟩")),
    "ro:verb": (),
}
# A lect whose spelling is regular enough to read by rule, with no borrowed
# reader: at each letter the first pattern that matches there gives the
# sound. Walloon in the unified spelling (rifondou), in the standard
# pronunciation the Walloon Wiktionary gives (prononçaedje zero-cnoxhou):
# ea = ja, oe = wɛ, oi = wa, ae = ɛ, å = ɔ, ô = õ, xh = ʃ, jh = ʒ, sch = sk;
# a vowel is nasal before an n that no vowel follows, and before m at the
# end of a word or before p b; a final e, and a final t d s x z p, are
# silent.
_WA_N = rf"(?:n(?![{_WA_V}y])|m(?=[pb]|$))"   # the n or m of a nasal vowel
RULES: dict[str, tuple[tuple[str, str], ...]] = {
    "wa": (
        (rf"(?<=[^{_WA_V}])es?$", ""), ("gues?$", "ɡ"), ("ques?$", "k"), ("ez$", "e"),
        ("[tdsxzp]+$", ""), ("(?<=n)[cg]$", ""),
        ("tch", "t͡ʃ"), ("dj", "d͡ʒ"), ("sch", "sk"), ("xh", "ʃ"), ("jh", "ʒ"), ("sh", "ʃ"), ("ch", "ʃ"),
        ("gn", "ɲ"), ("qu", "k"), ("gu(?=[eiéèêî])", "ɡ"),
        ("ç|c(?=[eiéèêî])|ss", "s"), ("c", "k"), ("g(?=[eiéèêî])|j", "ʒ"), ("g", "ɡ"), ("x", "ks"),
        ("y", "j"), ("r+", "ʀ"), (r"([bdfklmnptvz])\1", "\\1"),
        ("ieu", "jø"), ("ea", "ja"), ("eu", "ø"), ("oe", "wɛ"), ("oi", "wa"), ("o[uû]", "u"), ("ae|ai|ei", "ɛ"),
        ("ie", "jɛ"), ("i(?=[aàâåeéèêoôuû])", "j"),
        (rf"é{_WA_N}", "ẽ"), (rf"i{_WA_N}", "ɛ̃"), (rf"[ae]{_WA_N}", "ɑ̃"), (rf"o{_WA_N}", "ɔ̃"), (rf"u{_WA_N}", "œ̃"),
        ("å", "ɔ"), ("ô", "õ"), ("o", "ɔ"), ("[aàâ]", "a"), ("é", "e"), ("[eèêë]", "ɛ"), ("[iîï]", "i"), ("[uûü]", "y"),
    ),
}
# What the rules leave to the end of the word: Walloon devoices a final
# obstruent, and a glide beside its own vowel is one sound.
RULES_AFTER: dict[str, tuple[tuple[str, str], ...]] = {
    "wa": (("jj", "j"), ("d͡ʒ$", "t͡ʃ"), ("b$", "p"), ("d$", "t"), ("ɡ$", "k"), ("v$", "f"), ("z$", "s"), ("ʒ$", "ʃ")),
}
# Faults of a borrowed Epitran map, mended for every lect it reads, after
# the lect's own table. Italian: sc is read ʃ before a o u and s + t͡ʃ
# before e i. Spanish: gu before a consonant or at the end of a word is
# read ɡw, and hi before a consonant as the glide alone.
_FR_V = "aeiouyàâéèêëîïôöûüœ"
BACKEND_RESPELL: dict[str, tuple[tuple[str, str], ...]] = {
    # French: ail, eil, euil, ouil + l are a vowel + j, and ai in aile is
    # ɛ (the map reads e, ɛjl, œjl); c and g before e i are s and ʒ (it
    # voices that s between vowels), and a q without u is k; a final e
    # after a consonant is silent in a word with another vowel, but keeps
    # that consonant sounded (the map leaves a schwa after nasal vowel +
    # consonant: crendre); the -er of a longer word is [e]; a final
    # consonant after a nasal vowel is silent (grant, sang, blanc).
    "fra-Latn": (("aill|ail$", "⟨aj⟩"), ("eill|eil$", "⟨ɛj⟩"), ("ouill", "⟨uj⟩"), ("(?:euill|ueill|œill|euil$)", "⟨œj⟩"),
                 ("ail(?=e)", "èl"), ("c(?=[eiéèêîy])", "ç"), ("g(?=[eiéèêîy])", "j"), ("q(?!u)", "qu"),
                 ("oeu|œu", "eu"),
                 (rf"^(.*[{_FR_V}].*[^{_FR_V}⟩])es?$", "\\1⟨⟩"), (rf"^(.*[{_FR_V}].*⟩)es?$", "\\1"),
                 (rf"^(.*[{_FR_V}].*)er$", "\\1é"), (rf"(?<=[aeioâêîôu][nm])[tdcgsp]+$", "")),
    "ita-Latn": (("sci(?=[aouàòù])", "⟨ʃ⟩"), ("sc(?=[eiéèêëìíî])", "⟨ʃ⟩"), ("sc(?=[aouàáâòóôùúûrl])", "⟨sk⟩")),
    "spa-Latn": (("gu(?=[^aeiouáéíóúü]|$)", "⟨ɡu⟩"), ("^h(?=[ií][^aeiouáéíóú])", "")),
    # Sardinian: the i of gi, ci before a consonant is dropped (girare).
    "sro-Latn": (("gi(?=[^aeiou])", "⟨d͡ʒi⟩"), ("ci(?=[^aeiou])", "⟨t͡ʃi⟩")),
}
# The voice's notation rewritten in the grid's, as regular expressions over
# decomposed text, in order: stress and length dropped, affricates tied;
# French y before a vowel is the glide; the Portuguese voice writes a nasal
# vowel as vowel + ŋ and a nasal diphthong as two nasal vowels, puts a schwa
# after ɾ before a consonant, and writes ɹ ʊ ɪ ɑ for ɾ u j a.
_VOWEL = "[aeiouyɐɑɛɔœøəɨ]"
_ESPEAK_COMMON = ((r"[ˈˌː\-]", ""), ("tʃ", "t͡ʃ"), ("dʒ", "d͡ʒ"))
# Iberian b d ɡ are written as the approximants they become between vowels,
# and n as ŋ before a velar; a falling diphthong ends in ɪ or ʊ.
_IBERIAN = (("β", "b"), ("ð", "d"), ("ɣ", "ɡ"), ("ŋ(?=[ɡk])", "n"), ("ɪ", "j"), ("ʊ", "w"), ("ʰ", ""))
# The Spanish and Aragonese voices open e and o in places; neither lect
# has the contrast.
_FIVE_VOWELS = (("ɛ", "e"), ("ɔ", "o"))
_TIED = (("ts", "t͡s"), ("dz", "d͡z"))
ESPEAK_NOTATION: dict[str, tuple[tuple[str, str], ...]] = {
    "fr-fr": (*_ESPEAK_COMMON, ("ʁ", "ʀ"), (rf"y(?={_VOWEL})", "ɥ")),
    "pt-pt": (*_ESPEAK_COMMON, ("ɹ", "ɾ"), ("ʊ", "u"), ("ɪ", "j"), ("ɑ", "a"), ("ɾə", "ɾ"),
              ("ejŋ(?=.)", "e\u0303"), ("ejm(?=[pb])", "e\u0303"),  # nasal e inside a word, a diphthong only at its end
              (rf"({_VOWEL})\u0303?([jw]?)ŋ", "\\1\u0303\\2"),
              ("(\u0303)u\u0303", "\\1w\u0303"), ("(\u0303)[ij]\u0303", "\\1j\u0303"),
              (rf"(?<!{_VOWEL})(?<!\u0303)w$", "u"),
              ("^ʃ(?=[ptk])", "ɨʃ")),  # the voice drops the vowel of es- before a consonant
    "es": (*_ESPEAK_COMMON, *_IBERIAN, *_FIVE_VOWELS),
    "an": (*_ESPEAK_COMMON, *_IBERIAN, *_FIVE_VOWELS),
    "ca": (*_ESPEAK_COMMON, *_TIED, *_IBERIAN),
    # The Italian voice writes an unstressed u as ʊ and a final i as ɪ, and
    # a long consonant double where it does not use the length mark.
    "it": (*_ESPEAK_COMMON, *_TIED, ("ʊ", "u"), ("ɪ", "i"), ("ŋ", "n"), (r"([^\W\d_])\1", "\\1")),
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
    "frp": {**_OIL_E, "ù": "wɛ"},          # ouè
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
    "rup": {"sh": "ʃ", "ts": "t͡s", "dz": "d͡z", "lʒ": "ʎ", "nʒ": "ɲ"},
    "ruq": {"ts": "t͡s", "dz": "d͡z", "lʒ": "ʎ", "nʒ": "ɲ"},
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
