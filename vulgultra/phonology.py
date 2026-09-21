"""
lacyo.phonology — IPA, repair, syllabify, orthography (grammar.tex).

Repair runs before scoring. Geminates and Latin sC onsets are legal.
Syllable count = vowel nuclei. Glides are consonants.
"""

from __future__ import annotations

import re
import functools
from typing import Optional

import epitran
import panphon
from panphon.featuretable import FeatureTable

# ---------------------------------------------------------------------------
# Lacyo phoneme inventory (grammar.tex Ch.2)
# ---------------------------------------------------------------------------

CONSONANTS: set[str] = {
    "p", "b", "t", "d", "k", "ɡ",       # plosives
    "m", "n",                             # nasals
    "f", "v", "s", "z", "ʃ",             # fricatives
    "t͡ʃ",                                # affricate (single phoneme!)
    "l",                                  # lateral
    "r",                                  # tap/trill
    "j", "w",                             # approximants / glides
}

VOWELS: set[str] = {"a", "e", "i", "o", "u"}

PHONEME_INVENTORY: set[str] = CONSONANTS | VOWELS

# Onset-2 position: liquids and glides (also after a sonorant: /nj/, /lw/)
ONSET2: set[str] = {"l", "r", "j", "w"}

# Obstruents, including postalveolar (needed for /ʃt/, /t͡ʃr/)
OBSTRUENTS: set[str] = {"p", "b", "t", "d", "k", "ɡ", "f", "v", "s", "z", "ʃ", "t͡ʃ"}
S_LIKE: set[str] = {"s", "z", "ʃ"}

# Legal codas — any single consonant. CC: sonorant+C or s/ʃ + stop (Latin est, port).
LEGAL_SINGLE_CODAS: set[str] = CONSONANTS
SONORANTS: set[str] = {"m", "n", "l", "r"}
LEGAL_CODAS: set[str] = CONSONANTS

# Extra mid vowels: only if 1σ ending packing fails (grammar.tex). Not in the ceiling yet.
VOWELS_EXPANDED: set[str] = {"ɛ", "ɔ"}

# ---------------------------------------------------------------------------
# Phoneme-to-orthography mapping (grammar.tex Table 2.5)
# ---------------------------------------------------------------------------

IPA_TO_ORTHO: dict[str, str] = {
    "p": "p", "b": "b", "t": "t", "d": "d", "k": "k", "ɡ": "g",
    "m": "m", "n": "n",
    "f": "f", "v": "v", "s": "s", "z": "z",
    "ʃ": "x", "t͡ʃ": "c",
    "l": "l", "r": "r",
    "j": "y", "w": "w",
    "a": "a", "e": "e", "i": "i", "o": "o", "u": "u",
}

ORTHO_TO_IPA: dict[str, str] = {v: k for k, v in IPA_TO_ORTHO.items()}

# ---------------------------------------------------------------------------
# Phoneme mapping: non-Lacyo IPA → nearest Lacyo equivalent (grammar.tex §5.3)
# ---------------------------------------------------------------------------

PHONEME_MAP: dict[str, str] = {
    # French uvular → alveolar
    "ʁ": "r", "ʀ": "r", "ɣ": "r",
    # Front rounded → back
    "y": "u", "ø": "o", "œ": "o",
    # Lax vowels → tense
    "ɛ": "e", "ɔ": "o", "ɪ": "i", "ʊ": "u",
    # Schwa / near-open / Romanian close central
    "ə": "e", "ɐ": "a", "ɨ": "i", "î": "i",
    # Nasal vowels → V+n (handled in adapt_ipa)
    "ɑ̃": "an", "ɛ̃": "en", "ɔ̃": "on", "œ̃": "on",
    "ã": "an", "ẽ": "en", "ĩ": "in", "õ": "on", "ũ": "un",
    # Open back
    "ɑ": "a", "æ": "a",
    # Voiced postalveolar → voiceless (nearest Lacyo equivalent)
    "ʒ": "ʃ",
    # Dental fricatives
    "θ": "t", "ð": "d",
    # Palatal nasal/lateral → sequences
    "ɲ": "nj", "ʎ": "lj",
    # Glottal
    "ʔ": "", "h": "",
    # Labiodental approximant
    "ʋ": "v",
    # Palatal approximant (Spanish ll yeísmo)
    "ʝ": "j",
    # Voiceless velar fricative (Romanian/Istro-RO h) — not /ks/
    "x": "k",
    "χ": "k",
    # Other affricates
    "d͡ʒ": "dz", "t͡s": "ts",
    # Flap
    "ɾ": "r",
    # Labial-velar
    "ɥ": "w",
    # Long vowels (strip length)
    "aː": "a", "eː": "e", "iː": "i", "oː": "o", "uː": "u",
}

# ---------------------------------------------------------------------------
# G2P engines (lazily initialized)
# ---------------------------------------------------------------------------

_g2p_cache: dict[str, epitran.Epitran] = {}

LANG_CODES: dict[str, str] = {
    "fr": "fra-Latn",
    "es": "spa-Latn",
    "it": "ita-Latn",
    "pt": "por-Latn",
    "ca": "cat-Latn",
    "ro": "ron-Latn",
    "gl": "glg-Latn",
    "oc": "oci-Latn",
    # Sister G2P for the rest of the README corpus (no native epitran map)
    "an": "spa-Latn",
    "ast": "spa-Latn",
    "ext": "spa-Latn",
    "lad": "spa-Latn",
    "mwl": "por-Latn",
    "sc": "sro-Latn",
    "scn": "ita-Latn",
    "vec": "ita-Latn",
    "lmo": "ita-Latn",
    "pms": "ita-Latn",
    "lij": "lij-Latn",
    "fur": "ita-Latn",
    "eml": "ita-Latn",
    "lld": "ita-Latn",
    "ist": "ita-Latn",
    "rm": "ita-Latn",
    "la": "ita-Latn",
    "wa": "fra-Latn",
    "pcd": "fra-Latn",
    "nrm": "fra-Latn",
    "frp": "fra-Latn",
    "glw": "fra-Latn",
    "gsc": "oci-Latn",
    "dlm": "ita-Latn",
    "rup": "ron-Latn",
    "ruo": "ron-Latn",
}


def _get_g2p(lang: str) -> epitran.Epitran:
    """Get or create an epitran G2P engine for a language."""
    if lang not in _g2p_cache:
        code = LANG_CODES.get(lang)
        if code is None:
            raise ValueError(f"Unsupported language: {lang}")
        _g2p_cache[lang] = epitran.Epitran(code)
    return _g2p_cache[lang]


def word_to_ipa(word: str, lang: str) -> str:
    """Convert an orthographic word to IPA using epitran."""
    epi = _get_g2p(lang)
    return epi.transliterate(word.lower().strip())


# ---------------------------------------------------------------------------
# IPA → Lacyo phoneme sequence
# ---------------------------------------------------------------------------

# Multi-char IPA tokens to recognize BEFORE splitting by character.
# Order matters: longer tokens first.
_MULTI_CHAR_IPA = sorted(
    [p for p in PHONEME_INVENTORY if len(p) > 1] +
    [p for p in PHONEME_MAP if len(p) > 1],
    key=len, reverse=True
)

# Regex for nasal vowel diacritics (combining tilde U+0303)
_NASAL_RE = re.compile(r"([aeiouyɛɔœøɑ])\u0303")

# Regex for length mark
_LENGTH_RE = re.compile(r"ː")

# Stress marks to strip
_STRESS_RE = re.compile(r"[ˈˌ]")

# Syllable boundary
_SYLLABLE_BOUNDARY_RE = re.compile(r"[.\-]")


def _normalize_ipa(ipa: str) -> str:
    """Normalize IPA string before tokenization."""
    # Strip stress marks
    ipa = _STRESS_RE.sub("", ipa)
    # Strip syllable boundaries
    ipa = _SYLLABLE_BOUNDARY_RE.sub("", ipa)
    # Handle combining tilde (nasal vowels) → V + n
    ipa = _NASAL_RE.sub(lambda m: PHONEME_MAP.get(m.group(0), m.group(1) + "n"), ipa)
    # Strip length marks
    ipa = _LENGTH_RE.sub("", ipa)
    return ipa


def tokenize_ipa(ipa: str) -> list[str]:
    """
    Tokenize an IPA string into a list of IPA segments.
    Handles multi-character symbols (t͡ʃ, etc.) correctly.
    """
    ipa = _normalize_ipa(ipa)
    tokens: list[str] = []
    i = 0
    while i < len(ipa):
        matched = False
        # Try multi-char tokens longest first
        for mc in _MULTI_CHAR_IPA:
            if ipa[i:i+len(mc)] == mc:
                tokens.append(mc)
                i += len(mc)
                matched = True
                break
        if not matched:
            ch = ipa[i]
            if ch.strip():  # skip whitespace
                tokens.append(ch)
            i += 1
    return tokens


def adapt_to_lacyo(ipa_tokens: list[str]) -> list[str]:
    """
    Map a sequence of IPA tokens to Lacyo phonemes.
    Non-Lacyo phonemes are mapped via PHONEME_MAP.
    Unknown phonemes are dropped.
    """
    result: list[str] = []
    for tok in ipa_tokens:
        if tok in PHONEME_INVENTORY:
            result.append(tok)
        elif tok in PHONEME_MAP:
            mapped = PHONEME_MAP[tok]
            if mapped:
                # mapped could be multi-char like "nj"
                result.extend(tokenize_ipa(mapped))
        # else: drop unknown phoneme
    return result


def overlay_spelling_contrasts(word: str, phonemes: list[str]) -> list[str]:
    """Keep /v/ when the source *spells* v.

    Spanish and Catalan G2P merge v→b (Iberian phonology). Lacyo has both
    /b/ and /v/; inventory is not being minimized. Trust the letter.
    """
    import unicodedata
    letters = unicodedata.normalize("NFKD", word.lower())
    letters = [c for c in letters if c.isalpha() and c not in "h"]
    out = list(phonemes)
    li = 0
    for i, p in enumerate(out):
        if p not in CONSONANTS:
            continue
        while li < len(letters) and letters[li] in "aeiou":
            li += 1
        if li >= len(letters):
            break
        letter = letters[li]
        li += 1
        if p == "b" and letter == "v":
            out[i] = "v"
    return out


def ipa_to_lacyo(ipa: str) -> list[str]:
    """Full pipeline: raw IPA string → list of Lacyo phonemes."""
    tokens = tokenize_ipa(ipa)
    return adapt_to_lacyo(tokens)


def word_to_lacyo(word: str, lang: str) -> list[str]:
    """Convert orthographic word → Lacyo phoneme sequence."""
    ipa = word_to_ipa(word, lang)
    return overlay_spelling_contrasts(word, ipa_to_lacyo(ipa))


# ---------------------------------------------------------------------------
# Phoneme extraction (replacement for broken set(list(word)))
# ---------------------------------------------------------------------------

def extract_phonemes(phoneme_seq: list[str]) -> set[str]:
    """Extract the set of distinct Lacyo phonemes from a phoneme sequence."""
    return set(phoneme_seq) & PHONEME_INVENTORY


# ---------------------------------------------------------------------------
# Syllable counting (IPA-based, not orthographic)
# ---------------------------------------------------------------------------

def count_syllables(phoneme_seq: list[str]) -> int:
    """
    Count syllables in a Lacyo phoneme sequence.
    Each vowel nucleus = 1 syllable. Glides /j w/ are consonants, so
    /fwe/ and /aj/ are still 1σ.
    """
    return max(1, sum(1 for p in phoneme_seq if p in VOWELS))


def last_syllable(phoneme_seq: list[str]) -> list[str]:
    """Final syllable only — used to force 1σ endings."""
    syls = syllabify(phoneme_seq)
    return syls[-1] if syls else list(phoneme_seq)


# ---------------------------------------------------------------------------
# Phonotactic validation (grammar.tex §2.2)
# ---------------------------------------------------------------------------

def legal_onset_cluster(c1: str, c2: str) -> bool:
    """Reverse-VL onsets: obstruent+liquid/glide, sonorant+glide, s/ʃ+C."""
    if c2 in ONSET2 and (c1 in OBSTRUENTS or c1 in SONORANTS or c1 in S_LIKE):
        return True
    if c1 in S_LIKE and c1 != c2:
        return True
    return False


def legal_onset_triple(c1: str, c2: str, c3: str) -> bool:
    return c1 in S_LIKE and legal_onset_cluster(c2, c3)


def legal_coda_cluster(c1: str, c2: str) -> bool:
    if c1 in SONORANTS:
        return True
    if c1 in S_LIKE and c2 in OBSTRUENTS:
        return True
    return False


def syllabify(phoneme_seq: list[str]) -> list[list[str]]:
    """
    Maximal onset, with Latin sC onsets legal (reverse of Western prothesis).
    Returns list of syllables, each a list of phonemes.
    """
    if not phoneme_seq:
        return []

    vowel_positions = [i for i, p in enumerate(phoneme_seq) if p in VOWELS]
    if not vowel_positions:
        return [phoneme_seq]

    syllables: list[list[str]] = []
    for si, vi in enumerate(vowel_positions):
        if si == 0:
            start = 0
        else:
            prev_vi = vowel_positions[si - 1]
            interlude_start = prev_vi + 1
            interlude_end = vi
            interlude = phoneme_seq[interlude_start:interlude_end]

            if len(interlude) == 0:
                start = vi
            elif len(interlude) == 1:
                start = interlude_start
            elif len(interlude) == 2:
                c1, c2 = interlude
                if legal_onset_cluster(c1, c2):
                    start = interlude_start
                else:
                    start = interlude_start + 1
                    syllables[-1].append(phoneme_seq[interlude_start])
            else:
                if len(interlude) >= 3 and legal_onset_triple(
                    interlude[-3], interlude[-2], interlude[-1]
                ):
                    start = interlude_end - 3
                    syllables[-1].extend(phoneme_seq[interlude_start:start])
                elif legal_onset_cluster(interlude[-2], interlude[-1]):
                    start = interlude_end - 2
                    syllables[-1].extend(phoneme_seq[interlude_start:start])
                else:
                    start = interlude_end - 1
                    syllables[-1].extend(phoneme_seq[interlude_start:start])

        end = vi + 1
        syllables.append(phoneme_seq[start:end])

    last_vi = vowel_positions[-1]
    trailing = phoneme_seq[last_vi + 1:]
    if trailing and syllables:
        syllables[-1].extend(trailing)

    return syllables


def _classify_phoneme(p: str) -> str:
    """Classify a phoneme as 'C' (consonant) or 'V' (vowel)."""
    if p in VOWELS:
        return "V"
    return "C"


def count_violations(phoneme_seq: list[str]) -> int:
    """
    Structural phonotactics after repair. Geminates are legal (Italo-Romance
    / Sardinian). Hiatus is repaired before scoring, not fined here.
    """
    violations = 0
    syls = syllabify(phoneme_seq)

    for syl in syls:
        cv = [_classify_phoneme(p) for p in syl]
        try:
            nuc_idx = cv.index("V")
        except ValueError:
            violations += 1
            continue

        onset = syl[:nuc_idx]
        coda = syl[nuc_idx + 1:]

        if len(coda) > 2:
            violations += len(coda) - 2
        if len(coda) == 2 and not legal_coda_cluster(coda[0], coda[1]):
            violations += 1

        if len(onset) > 3:
            violations += len(onset) - 3
        elif len(onset) == 3:
            if not legal_onset_triple(onset[0], onset[1], onset[2]):
                violations += 1
        elif len(onset) == 2:
            if not legal_onset_cluster(onset[0], onset[1]):
                violations += 1

    return violations


def repair(phoneme_seq: list[str]) -> list[str]:
    """Repair-or-keep. Prefer operations that do not add a syllable.

    Order (reverse Vulgar Latin, then shorten):
      1. i/u before a vowel → glide (acqua /akkua/ → /akkwa/)
      2. collapse identical vowels (cîine /t͡ʃiine/ → /t͡ʃine/)
      3. if still illegal, epenthesize /e/ in the leftover cluster
    Geminates are not degeminated.
    """
    seq = [p for p in phoneme_seq if p]
    if not seq:
        return seq

    # Glide formation + identical-vowel collapse (may reduce σ)
    out: list[str] = []
    i = 0
    while i < len(seq):
        a = seq[i]
        b = seq[i + 1] if i + 1 < len(seq) else None
        if b is not None and a in VOWELS and b in VOWELS:
            if a == b:
                out.append(a)
                i += 2
                continue
            if a == "i":
                out.append("j")
                i += 1
                continue
            if a == "u":
                out.append("w")
                i += 1
                continue
            out.append(a)
            out.append("j")
            i += 1
            continue
        out.append(a)
        i += 1
    seq = out

    if count_violations(seq) == 0:
        return seq

    # Epenthesis /e/ at the first illegal cluster (adds σ; last resort)
    repaired: list[str] = []
    syls = syllabify(seq)
    changed = False
    for syl in syls:
        cv = [_classify_phoneme(p) for p in syl]
        try:
            nuc_idx = cv.index("V")
        except ValueError:
            repaired.extend(syl)
            continue
        onset = syl[:nuc_idx]
        nucleus = syl[nuc_idx]
        coda = syl[nuc_idx + 1:]
        if not changed and len(onset) >= 2 and (
            (len(onset) == 2 and not legal_onset_cluster(onset[0], onset[1]))
            or (len(onset) >= 3 and not (
                legal_onset_triple(onset[0], onset[1], onset[2])
                if len(onset) == 3 else False
            ))
        ):
            repaired.append(onset[0])
            repaired.append("e")
            repaired.extend(onset[1:])
            repaired.append(nucleus)
            repaired.extend(coda)
            changed = True
        elif not changed and len(coda) >= 2 and not legal_coda_cluster(coda[0], coda[1]):
            repaired.extend(onset)
            repaired.append(nucleus)
            repaired.append(coda[0])
            repaired.append("e")
            repaired.extend(coda[1:])
            changed = True
        else:
            repaired.extend(syl)
    return repaired if repaired else seq


def is_phonotactically_legal(phoneme_seq: list[str]) -> bool:
    """Check if a phoneme sequence is phonotactically legal."""
    return count_violations(phoneme_seq) == 0


# ---------------------------------------------------------------------------
# Orthographic rendering
# ---------------------------------------------------------------------------

def to_orthography(phoneme_seq: list[str]) -> str:
    """Convert a Lacyo phoneme sequence to orthographic form."""
    return "".join(IPA_TO_ORTHO.get(p, "?") for p in phoneme_seq)


def from_orthography(ortho: str) -> list[str]:
    """Convert Lacyo orthography back to phoneme sequence."""
    result: list[str] = []
    for ch in ortho.lower():
        if ch in ORTHO_TO_IPA:
            result.append(ORTHO_TO_IPA[ch])
    return result


# ---------------------------------------------------------------------------
# Phonemic edit distance
# ---------------------------------------------------------------------------

def phonemic_edit_distance(seq1: list[str], seq2: list[str]) -> int:
    """Levenshtein edit distance over phoneme sequences."""
    m, n = len(seq1), len(seq2)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        for jj in range(1, n + 1):
            temp = dp[jj]
            if seq1[i - 1] == seq2[jj - 1]:
                dp[jj] = prev
            else:
                dp[jj] = 1 + min(prev, dp[jj], dp[jj - 1])
            prev = temp
    return dp[n]
