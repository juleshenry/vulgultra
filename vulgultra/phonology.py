"""
vulgultra.phonology — IPA, repair, syllabify, orthography (grammar.tex).

Repair runs before scoring. Geminates and Latin sC onsets are legal.
Syllable count = vowel nuclei. Glides are consonants.
"""

from __future__ import annotations

import re
import functools
import unicodedata
from typing import Optional

import epitran
import panphon
from panphon.featuretable import FeatureTable
from vulgultra.phonology_constants import IPA_TO_ORTHO, LANG_CODES, ORTHO_TO_IPA

# ---------------------------------------------------------------------------
# Corpus-derived phone inventory
# ---------------------------------------------------------------------------

# These mutable sets are populated from IPA transcriptions of the forms in the
# active grid. They are working indexes, not a predefined Vulgultra inventory.
CONSONANTS: set[str] = set()
VOWELS: set[str] = set()
PHONEME_INVENTORY: set[str] = set()
ONSET2: set[str] = set()
OBSTRUENTS: set[str] = set()
S_LIKE: set[str] = set()
SONORANTS: set[str] = set()
LEGAL_SINGLE_CODAS: set[str] = CONSONANTS
LEGAL_CODAS: set[str] = CONSONANTS
VOWELS_EXPANDED: set[str] = set()

_FEATURES = FeatureTable()
_FEATURE_INDEX = {name: i for i, name in enumerate(_FEATURES.names)}


@functools.lru_cache(maxsize=None)
def _segment_features(segment: str) -> dict[str, str]:
    vector = _FEATURES.segment_to_vector(segment)
    if not vector:
        return {}
    return dict(zip(_FEATURES.names, vector))


def is_vowel(segment: str) -> bool:
    """Use PanPhon syllabicity/consonant features, not a hand-set phone list."""
    features = _segment_features(segment)
    return features.get("syl") == "+" and features.get("cons") == "-"


def is_consonant(segment: str) -> bool:
    features = _segment_features(segment)
    return features.get("cons") == "+" or not is_vowel(segment)


def _is_sonorant(segment: str) -> bool:
    return _segment_features(segment).get("son") == "+"


def _is_obstruent(segment: str) -> bool:
    features = _segment_features(segment)
    return features.get("cons") == "+" and features.get("son") == "-"


def _is_s_like(segment: str) -> bool:
    features = _segment_features(segment)
    return features.get("strid") == "+" and features.get("cont") == "+"


def _is_onset2(segment: str) -> bool:
    features = _segment_features(segment)
    return (
        (features.get("cons") == "-" and features.get("syl") == "-")
        or features.get("lat") == "+"
        or (features.get("son") == "+" and features.get("cont") == "+"
            and features.get("cor") == "+")
    )


def configure_inventory(segments: set[str] | list[str] | tuple[str, ...]) -> None:
    """Index the segments actually found in the active Romance grid."""
    observed = set(segments)
    vowels = {p for p in observed if is_vowel(p)}
    consonants = observed - vowels
    for target, values in (
        (PHONEME_INVENTORY, observed),
        (VOWELS, vowels),
        (CONSONANTS, consonants),
        (SONORANTS, {p for p in consonants if _is_sonorant(p)}),
        (OBSTRUENTS, {p for p in consonants if _is_obstruent(p)}),
        (S_LIKE, {p for p in consonants if _is_s_like(p)}),
        (ONSET2, {p for p in consonants if _is_onset2(p)}),
    ):
        target.clear()
        target.update(values)

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# G2P engines (lazily initialized)
# ---------------------------------------------------------------------------

_g2p_cache: dict[str, epitran.Epitran] = {}

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
# IPA → Vulgultra phoneme sequence
# ---------------------------------------------------------------------------

# Regex for length mark
_LENGTH_RE = re.compile(r"ː")

# Stress marks to strip
_STRESS_RE = re.compile(r"[ˈˌ]")

# Syllable boundary
_SYLLABLE_BOUNDARY_RE = re.compile(r"[.\-]")


def _normalize_ipa(ipa: str) -> str:
    """Normalize IPA string before tokenization."""
    ipa = unicodedata.normalize("NFC", ipa)
    # Strip stress marks
    ipa = _STRESS_RE.sub("", ipa)
    # Strip syllable boundaries
    ipa = _SYLLABLE_BOUNDARY_RE.sub("", ipa)
    # Strip phonetic length; segment identity and quality remain intact.
    ipa = _LENGTH_RE.sub("", ipa)
    return ipa


def tokenize_ipa(ipa: str) -> list[str]:
    """
    Segment IPA with PanPhon's full IPA segment inventory. No Vulgultra
    phoneme list controls which source segments can enter the candidate pool.
    """
    return [segment for segment in _FEATURES.segs_safe(_normalize_ipa(ipa)) if segment.strip()]


def adapt_to_vulgultra(ipa_tokens: list[str]) -> list[str]:
    """
    Identity adaptation: candidate segments stay as transcribed. Phonological
    adaptation/repair may change a sequence, but does not collapse a source
    segment to a hand-picked target inventory.
    """
    return list(ipa_tokens)


def overlay_spelling_contrasts(word: str, phonemes: list[str]) -> list[str]:
    """Keep /v/ when the source *spells* v.

    Spanish and Catalan G2P merge v→b (Iberian phonology). Vulgultra has both
    /b/ and /v/; inventory is not being minimized. Trust the letter.
    """
    import unicodedata
    letters = unicodedata.normalize("NFKD", word.lower())
    letters = [c for c in letters if c.isalpha() and c not in "h"]
    out = list(phonemes)
    li = 0
    for i, p in enumerate(out):
        if not is_consonant(p):
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


def ipa_to_vulgultra(ipa: str) -> list[str]:
    """Full pipeline: raw IPA string → list of Vulgultra phonemes."""
    tokens = tokenize_ipa(ipa)
    return adapt_to_vulgultra(tokens)


def word_to_vulgultra(word: str, lang: str) -> list[str]:
    """Convert orthographic word → Vulgultra phoneme sequence."""
    ipa = word_to_ipa(word, lang)
    return overlay_spelling_contrasts(word, ipa_to_vulgultra(ipa))


# ---------------------------------------------------------------------------
# Phoneme extraction (replacement for broken set(list(word)))
# ---------------------------------------------------------------------------

def extract_phonemes(phoneme_seq: list[str]) -> set[str]:
    """Return every distinct segment carried by the candidate sequence."""
    return set(phoneme_seq)


# ---------------------------------------------------------------------------
# Syllable counting (IPA-based, not orthographic)
# ---------------------------------------------------------------------------

def count_syllables(phoneme_seq: list[str]) -> int:
    """
    Count syllables in a Vulgultra phoneme sequence.
    Each vowel nucleus = 1 syllable. Glides /j w/ are consonants, so
    /fwe/ and /aj/ are still 1σ.
    """
    return max(1, sum(1 for p in phoneme_seq if is_vowel(p)))


def last_syllable(phoneme_seq: list[str]) -> list[str]:
    """Final syllable only — used to force 1σ endings."""
    syls = syllabify(phoneme_seq)
    return syls[-1] if syls else list(phoneme_seq)


# ---------------------------------------------------------------------------
# Phonotactic validation (grammar.tex §2.2)
# ---------------------------------------------------------------------------

def legal_onset_cluster(c1: str, c2: str) -> bool:
    """Reverse-VL onsets: obstruent+liquid/glide, sonorant+glide, s/ʃ+C."""
    if _is_onset2(c2) and (_is_obstruent(c1) or _is_sonorant(c1) or _is_s_like(c1)):
        return True
    if _is_s_like(c1) and c1 != c2:
        return True
    return False


def legal_onset_triple(c1: str, c2: str, c3: str) -> bool:
    return _is_s_like(c1) and legal_onset_cluster(c2, c3)


def legal_coda_cluster(c1: str, c2: str) -> bool:
    if _is_sonorant(c1):
        return True
    if _is_s_like(c1) and _is_obstruent(c2):
        return True
    return False


def syllabify(phoneme_seq: list[str]) -> list[list[str]]:
    """
    Maximal onset, with Latin sC onsets legal (reverse of Western prothesis).
    Returns list of syllables, each a list of phonemes.
    """
    if not phoneme_seq:
        return []

    vowel_positions = [i for i, p in enumerate(phoneme_seq) if is_vowel(p)]
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
    if is_vowel(p):
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
        if b is not None and is_vowel(a) and is_vowel(b):
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
    """Render mapped symbols and visibly delimit IPA without a spelling rule."""
    return "".join(
        IPA_TO_ORTHO[p] if p in IPA_TO_ORTHO else f"⟨{p}⟩"
        for p in phoneme_seq
    )


def from_orthography(ortho: str) -> list[str]:
    """Decode the conventional map plus explicitly delimited IPA segments."""
    result: list[str] = []
    i = 0
    while i < len(ortho):
        if ortho[i] == "⟨":
            end = ortho.find("⟩", i + 1)
            if end >= 0:
                segment = ortho[i + 1:end]
                if segment:
                    result.append(segment)
                i = end + 1
                continue
        ch = ortho[i].lower()
        if ch in ORTHO_TO_IPA:
            result.append(ORTHO_TO_IPA[ch])
        else:
            # Do not silently erase a segment when reading a future spelling.
            result.append(ch)
        i += 1
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
