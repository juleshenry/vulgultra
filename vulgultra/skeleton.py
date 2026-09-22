"""Join key for lemma families. Not Vulgultra spelling.

The skeleton only buckets source citations so English is not the join.
It is not the alphabet of the language. A candidate keeps its source
form; phonemes come from G2P; letters are rendered from the winning
phoneme string after the contest.

ç is still a c in the source, so it buckets with c, not with s. Whether
that sound is /s/ is G2P plus |Φ|, not this table.
"""

from __future__ import annotations

import re
import unicodedata

# Longest digraphs first. Each maps to one skeleton consonant.
_DIGRAPHS: tuple[tuple[str, str], ...] = (
    ("sch", "s"),
    ("tch", "k"),
    ("ch", "k"),
    ("qu", "k"),
    ("ck", "k"),
    ("gh", "k"),
    ("gu", "k"),
    ("gn", "n"),
    ("nh", "n"),
    ("lh", "l"),
    ("ll", "l"),
    ("rr", "r"),
    ("ss", "s"),
    ("sc", "s"),
    ("sh", "s"),
    ("tx", "k"),
    ("tj", "k"),
    ("ts", "s"),
    ("tz", "s"),
    ("ph", "f"),
    ("th", "t"),
    ("kh", "k"),
    ("dj", "k"),
    ("gi", "k"),
    ("ge", "k"),
)

_LETTER: dict[str, str] = {
    "b": "p", "p": "p",
    "d": "t", "t": "t",
    "g": "k", "k": "k", "c": "k", "q": "k", "ç": "k",
    "f": "f", "v": "f",
    "s": "s", "z": "s", "x": "s",
    "m": "m",
    "n": "n",
    "l": "l",
    "r": "r",
    "j": "k",
    "w": "f",
    "h": "",
    "y": "",
}

_VOWELS = set("aeiou")
_SPACE = re.compile(r"\s+")
# Strip vowel accents only. Cedilla stays a letter (ç), not a pre-spelled s.
_STRIP_MARKS = frozenset({
    0x0300, 0x0301, 0x0302, 0x0303, 0x0304, 0x0306, 0x0308, 0x030A, 0x030C,
})

OBLIQUE = frozenset({"de", "di", "da", "del", "della", "do", "du", "d"})
REFLEXIVE = frozenset({"se", "si", "s"})
HAVE = frozenset({
    "haver", "haber", "avere", "avoir", "ter", "tener", "ave",
    "ho", "ha", "hei", "ai",
})


def _fold(text: str) -> str:
    text = text.lower().strip().replace("ç", "\u0001")
    nfkd = unicodedata.normalize("NFKD", text)
    stripped = "".join(
        c for c in nfkd
        if unicodedata.category(c) != "Mn" or ord(c) not in _STRIP_MARKS
    )
    return stripped.replace("\u0001", "ç")


def split_frame(citation: str) -> tuple[str, str]:
    """Strip closed-class particles. Return (open_word, frame).

    Whole tokens only, plus a trailing -se/-si on a single word longer
    than three letters (gustarse). meteoropatico is left intact.
    """
    raw = citation.strip()
    if not raw:
        return "", "bare"
    folded = _fold(raw)
    tokens = _SPACE.split(folded)
    frame = "bare"
    if len(tokens) > 1:
        if tokens[0] in HAVE:
            tokens = tokens[1:]
            frame = "light_noun"
        if tokens and tokens[0] in REFLEXIVE:
            tokens = tokens[1:]
            frame = "reflexive"
        if tokens and tokens[-1] in OBLIQUE:
            tokens = tokens[:-1]
            frame = "oblique" if frame == "bare" else frame
        if tokens and tokens[0] in OBLIQUE:
            tokens = tokens[1:]
            frame = "oblique" if frame == "bare" else frame
        open_word = " ".join(tokens) if tokens else folded
    else:
        open_word = folded
        if len(open_word) > 4 and open_word.endswith(("se", "si")):
            open_word = open_word[:-2]
            frame = "reflexive"
        elif open_word.endswith(("ar", "er", "ir", "re", "are", "ere", "ire")):
            frame = "direct"
    return open_word, frame


def skeleton(citation: str) -> str:
    """Consonant skeleton of the open morpheme. Empty if fewer than two consonants."""
    open_word, _frame = split_frame(citation)
    text = _fold(open_word).replace(" ", "")
    out: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        hit = False
        for dig, sk in _DIGRAPHS:
            if text.startswith(dig, i):
                if sk:
                    out.append(sk)
                i += len(dig)
                hit = True
                break
        if hit:
            continue
        ch = text[i]
        i += 1
        if ch in _VOWELS:
            continue
        mapped = _LETTER.get(ch, "")
        if mapped:
            out.append(mapped)
    if len(out) < 2:
        return ""
    return "".join(out)
