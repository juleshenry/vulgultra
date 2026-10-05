#!/usr/bin/env python3
"""Check the pipeline's reading of grid forms against scholarly transcriptions.

IE-CoR and Saenko 2015 transcribe their word lists. Wherever one of them has
the very spelling a grid cell holds, its transcription is compared with what
the pipeline reads from that spelling: the syllable count, which the
objective minimises, and the segments, which the roots are made of.

The two sources do not write alike (affricates without a tie bar, long
consonants doubled, diphthongs as two vowels), so their transcriptions are
passed through the same repair as the pipeline's before counting, and the
segment comparison ignores stress, length and allophones of b d ɡ and r.

    python3 scripts/reader_check.py            # → docs/eval/readers.md
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import audit_grid_sources as audit  # noqa: E402
from vulgultra.g2p import transcribe_and_repair  # noqa: E402
from vulgultra.phonology import (  # noqa: E402
    ESPEAK_VOICES, count_syllables, espeak_reading, ipa_to_vulgultra, repair, unknown_segments,
)
from vulgultra.phonology_constants import LANG_CODES  # noqa: E402

TIED = (("tʃ", "t͡ʃ"), ("dʒ", "d͡ʒ"), ("ts", "t͡s"), ("dz", "d͡z"), ("tɕ", "t͡ɕ"))
SAME_SOUND = (("ʁ", "r"), ("ʀ", "r"), ("ɾ", "r"), ("β", "b"), ("ð", "d"), ("ɣ", "ɡ"), ("i̯", "j"), ("u̯", "w"))


def plain(ipa: str) -> str:
    """A transcription without stress, length or syllable marks, affricates tied."""
    ipa = re.sub(r"[ˈˌ.ː‿\s\-]", "", unicodedata.normalize("NFD", ipa)).replace("͡", "")
    ipa = re.sub(r"(.)\1", r"\1", ipa)  # a long consonant written double
    for loose, tied in TIED:
        ipa = ipa.replace(loose, tied)
    return ipa


def comparable(ipa: str) -> str:
    ipa = plain(ipa).replace("͡", "")
    for variant, sound in SAME_SOUND:
        ipa = ipa.replace(unicodedata.normalize("NFD", variant), sound)
    return ipa


def sourced(lect: str) -> dict[tuple[str, str], tuple[str, str]]:
    """(concept, spelling) → (source, transcription), for the doculect nearest the column."""
    found: dict[tuple[str, str], tuple[str, str]] = {}
    forms, languages, parameters = audit._cldf("iecor")
    for variety in audit.IECOR.get(lect, ())[:1]:
        for row in forms:
            if languages.get(row["Language_ID"]) == variety and row["Phonemic"]:
                name = parameters[row["Parameter_ID"]]
                found.setdefault((audit.IECOR_IDS.get(name, name), audit.nfc(row["Form"])), ("IE-CoR", row["Phonemic"]))
    forms, _, parameters = audit._cldf("saenkoromance")
    for doculect in audit.SAENKO.get(lect, ())[:1]:
        for row in forms:
            if row["Language_ID"] != doculect or not row["Segments"]:
                continue
            name = parameters[row["Parameter_ID"]]
            for spelling in re.findall(r"[{]([^}]*)[}]", row["Value"]):
                found.setdefault((audit.SAENKO_IDS.get(name, name), audit.nfc(spelling)),
                                 ("Saenko", row["Segments"].replace(" ", "")))
    return found


def check(lect: str, rows: list[dict]) -> dict | None:
    transcriptions = sourced(lect)
    cells = same_count = same_segments = 0
    differ: list[str] = []
    for row in rows:
        form = audit.nfc(row[lect])
        hit = transcriptions.get((row["id"], form))
        if not form or not hit:
            continue
        try:
            theirs = repair(ipa_to_vulgultra(plain(hit[1]), lect))
        except Exception:
            continue
        if unknown_segments(theirs):
            continue
        cells += 1
        try:
            ipa, mine = transcribe_and_repair(form, lect)
        except Exception:
            differ.append(f"*{form}* rejected")
            continue
        same_segments += comparable(ipa) == comparable(hit[1])
        if count_syllables(mine) == count_syllables(theirs):
            same_count += 1
        else:
            differ.append(f"*{form}* {''.join(mine)} ({count_syllables(mine)}) for {plain(hit[1])} ({count_syllables(theirs)})")
    if not cells:
        return None
    return {"lect": lect, "cells": cells, "count": same_count, "segments": same_segments, "differ": differ}


def reader_of(lect: str) -> str:
    voice = ESPEAK_VOICES.get(lect)
    if voice and espeak_reading("a", lect) is not None:
        return f"espeak-ng {voice}"
    return f"Epitran {LANG_CODES[lect]}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-o", "--output", type=Path, default=ROOT / "docs" / "eval" / "readers.md")
    args = parser.parse_args()
    rows = audit.concepts()
    results = [result for lect in rows[0] if lect not in ("id", "gloss_es", "pos")
               for result in [check(lect, rows)] if result]
    total = sum(r["cells"] for r in results)
    lines = [
        "# Readers checked against scholarly transcriptions",
        "",
        "Generated by `scripts/reader_check.py`. Do not edit by hand.",
        "",
        "For every grid cell whose spelling IE-CoR or Saenko 2015 also has, the pipeline's reading of "
        "that spelling is set beside their transcription. **Same syllables**: both give the same "
        "number of syllables, the quantity the objective minimises. **Same segments**: both give the "
        "same sounds, stress, length and allophones of *b d ɡ r* aside. The sources' own notation "
        "accounts for part of the gap (a diphthong written as two vowels, a different valley's "
        "pronunciation), so read the columns as a floor, not as an error rate.",
        "",
        "| lect | reader | cells | same syllables | same segments |",
        "|---|---|---:|---:|---:|",
    ]
    for r in results:
        lines.append(f"| {r['lect']} | {reader_of(r['lect'])} | {r['cells']} | {r['count']} ({100 * r['count'] // r['cells']}%) "
                     f"| {r['segments']} ({100 * r['segments'] // r['cells']}%) |")
    lines += [f"| all | | {total} | {sum(r['count'] for r in results)} "
              f"({100 * sum(r['count'] for r in results) // total}%) "
              f"| {sum(r['segments'] for r in results)} ({100 * sum(r['segments'] for r in results) // total}%) |", ""]
    for r in results:
        if r["differ"]:
            lines += [f"## {r['lect']}: syllable counts that differ", "", "; ".join(r["differ"]), ""]
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(line for line in lines if line.startswith("| ")))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
