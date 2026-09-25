"""Small G2P boundary used by candidate preparation.

Keeping transcription here makes it clear that source evidence is converted
to IPA before repair and scoring; the public functions remain re-exported by
``phonology`` for existing scripts.
"""

from __future__ import annotations

from vulgultra.phonology import ipa_to_vulgultra, overlay_spelling_contrasts, repair, word_to_ipa


def transcribe_and_repair(word: str, lang: str) -> tuple[str, list[str]]:
    """Return source IPA and the repaired Vulgultra segment sequence."""
    ipa = word_to_ipa(word, lang)
    seq = overlay_spelling_contrasts(word, ipa_to_vulgultra(ipa))
    return ipa, repair(seq)
