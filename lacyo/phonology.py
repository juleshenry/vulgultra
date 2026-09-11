"""
lacyo.phonology — Single source of truth for Lacyo phonological operations.

Provides:
  - IPA-based grapheme-to-phoneme conversion (via epitran)
  - Proper phoneme extraction (multi-character IPA symbols handled correctly)
  - IPA-based syllable counting
  - Phonotactic validation per grammar.tex spec
  - Phoneme-to-orthography mapping
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

# Onset-2 position: only liquids and glides
ONSET2: set[str] = {"l", "r", "j", "w"}

# Obstruents that can occupy onset-1 in a cluster
OBSTRUENTS: set[str] = {"p", "b", "t", "d", "k", "ɡ", "f", "v", "s"}

# Legal codas — any single consonant is fine (naturalistic, respects Romance sources).
# Coda clusters up to 2 are allowed if sonorant precedes obstruent (e.g. /ns/, /nd/, /st/, /rt/).
LEGAL_SINGLE_CODAS: set[str] = CONSONANTS  # any consonant can close a syllable
SONORANTS: set[str] = {"m", "n", "l", "r"}
# For backwards compat (some old code may reference this)
LEGAL_CODAS: set[str] = CONSONANTS

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
    # Voiceless velar fricative
    "x": "ks",
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
    Each vowel nucleus = 1 syllable.
    """
    return max(1, sum(1 for p in phoneme_seq if p in VOWELS))


# ---------------------------------------------------------------------------
# Phonotactic validation (grammar.tex §2.2)
# ---------------------------------------------------------------------------

def syllabify(phoneme_seq: list[str]) -> list[list[str]]:
    """
    Syllabify a Lacyo phoneme sequence using maximal onset principle.
    Returns list of syllables, each a list of phonemes.
    """
    if not phoneme_seq:
        return []

    # Identify vowel positions
    vowel_positions = [i for i, p in enumerate(phoneme_seq) if p in VOWELS]
    if not vowel_positions:
        # No vowels — treat entire thing as one degenerate syllable
        return [phoneme_seq]

    syllables: list[list[str]] = []
    # Assign phonemes to syllables based on vowel nuclei
    for si, vi in enumerate(vowel_positions):
        syl: list[str] = []

        if si == 0:
            # First syllable gets everything up to and including first vowel
            start = 0
        else:
            # Maximal onset: assign as many consonants as possible to this syllable
            prev_vi = vowel_positions[si - 1]
            interlude_start = prev_vi + 1
            interlude_end = vi  # exclusive (vowel itself)
            interlude = phoneme_seq[interlude_start:interlude_end]

            # Determine how many consonants go to onset of this syllable
            # vs coda of previous syllable
            if len(interlude) == 0:
                start = vi
            elif len(interlude) == 1:
                # Single consonant → onset of this syllable
                start = interlude_start
            elif len(interlude) == 2:
                c1, c2 = interlude
                if c1 in OBSTRUENTS and c2 in ONSET2:
                    # Legal onset cluster → both go to this syllable
                    start = interlude_start
                else:
                    # Split: first to prev coda, second to this onset
                    start = interlude_start + 1
                    syllables[-1].append(phoneme_seq[interlude_start])
            else:
                # 3+ consonants: give last 2 to onset if legal cluster, else last 1
                c_pen, c_last = interlude[-2], interlude[-1]
                if c_pen in OBSTRUENTS and c_last in ONSET2:
                    start = interlude_end - 2
                    syllables[-1].extend(phoneme_seq[interlude_start:interlude_end - 2])
                else:
                    start = interlude_end - 1
                    syllables[-1].extend(phoneme_seq[interlude_start:interlude_end - 1])

        # Determine end of this syllable
        # For the last vowel, we only go up to vi+1; trailing consonants
        # are appended separately below to avoid double-counting.
        end = vi + 1

        syl = phoneme_seq[start:end]
        syllables.append(syl)

    # Handle trailing consonants after last vowel
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
    Count phonotactic violations in a Lacyo phoneme sequence.
    Based on grammar.tex §2.2 constraints.
    """
    violations = 0
    syls = syllabify(phoneme_seq)

    for syl in syls:
        cv = [_classify_phoneme(p) for p in syl]

        # Find the vowel nucleus position
        try:
            nuc_idx = cv.index("V")
        except ValueError:
            violations += 1  # syllable with no vowel
            continue

        onset = syl[:nuc_idx]
        coda = syl[nuc_idx + 1:]

        # Constraint 1: Max 2 consonants in coda (3+ is a violation)
        if len(coda) > 2:
            violations += len(coda) - 2

        # Constraint 1b: If coda cluster of 2, must be sonorant+obstruent
        # (e.g. /ns/, /nd/, /rt/, /lk/) — natural in Romance
        if len(coda) == 2:
            if coda[0] not in SONORANTS:
                violations += 1

        # Constraint 2: No onset triples (max 2 consonants in onset)
        if len(onset) > 2:
            violations += len(onset) - 2

        # Constraint 3: Onset cluster rule
        if len(onset) == 2:
            c1, c2 = onset
            if c1 not in OBSTRUENTS or c2 not in ONSET2:
                violations += 1

        # Constraint 4: Any single consonant is a legal coda (naturalistic).
        # No restriction — Romance sources are respected.

    # Constraint 5: No gemination across syllable boundaries
    for i in range(len(syls) - 1):
        if syls[i] and syls[i + 1]:
            if syls[i][-1] == syls[i + 1][0] and _classify_phoneme(syls[i][-1]) == "C":
                violations += 1

    # NOTE: No hard inventory membership check here.
    # The phoneme inventory is EMERGENT — determined by which roots survive
    # annealing. The E_phon energy term pressures the optimizer to minimize
    # inventory size. Only structural phonotactics are enforced above.

    return violations


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
