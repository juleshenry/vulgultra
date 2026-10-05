"""Small G2P boundary used by candidate preparation.

Keeping transcription here makes it clear that source evidence is converted
to IPA before repair and scoring; the public functions remain re-exported by
``phonology`` for existing scripts.
"""

from __future__ import annotations

from vulgultra.phonology import (
    ipa_to_vulgultra, overlay_spelling_contrasts, repair, unknown_segments, word_to_ipa,
)


class UntranscribedError(ValueError):
    """The backend left letters that are not IPA; the form cannot compete."""

    def __init__(self, word: str, lang: str, ipa: str, leftovers: list[str]) -> None:
        super().__init__(f"{lang} {word!r} → {ipa!r}: untranscribed {' '.join(leftovers)}")
        self.word, self.lang, self.ipa, self.leftovers = word, lang, ipa, leftovers


def transcribe_and_repair(word: str, lang: str) -> tuple[str, list[str]]:
    """Return source IPA and the repaired Vulgultra segment sequence."""
    ipa = word_to_ipa(word, lang)
    seq = ipa_to_vulgultra(ipa)
    leftovers = unknown_segments(seq)
    if leftovers:
        raise UntranscribedError(word, lang, ipa, leftovers)
    return ipa, repair(overlay_spelling_contrasts(word, seq))
