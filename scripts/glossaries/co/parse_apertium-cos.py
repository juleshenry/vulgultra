#!/usr/bin/env python3
"""Apertium bilingual dictionary -> headword/gloss table.

Reads an Apertium bidix (`<e><p><l>..</l><r>..</r></p></e>`) from raw/ and
writes one row per translation pair. The lect's side supplies the headword
exactly as spelled; the other side supplies the gloss.

Kept: every pair, whatever its direction restriction (r="LR"/"RL"), since
both sides are words of their languages either way.
Dropped: proper nouns (np), entries flagged i="yes" (ignored by Apertium),
regex entries, entries whose lect side is empty, pure punctuation/digits,
all-capital tokens (acronyms, Roman numerals) and single letters.

    python3 parse_apertium-cos.py
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
# (raw file, side the lect is on, gloss language, {variety attribute value or None: output file})
JOBS = [
    ("apertium-cos-ita.cos-ita.dix", "l", "it", {None: "apertium-cos-ita.tsv"}),
    ("apertium-cos-por.cos-por.dix", "l", "pt", {None: "apertium-cos-por.tsv"}),
    ("apertium-spa-cos.spa-cos.dix", "r", "es", {None: "apertium-spa-cos.tsv"}),
]
# Apertium entries may carry alt="..."/v="..."/vl=/vr= naming a variety.
VARIETY_ATTRS = ("alt", "v", "vl", "vr")

POS = {
    "n": "noun", "vblex": "verb", "vbser": "verb", "vbhaver": "verb", "vbmod": "verb", "vaux": "verb",
    "adj": "adj", "adv": "adv", "preadv": "adv", "prn": "pron", "rel": "pron", "num": "num",
    "pr": "prep", "cnjcoo": "conj", "cnjsub": "conj", "cnjadv": "conj",
    "det": "other", "predet": "other", "ij": "other", "abbr": "other", "acr": "other",
}


def side_text(xml: str) -> tuple[str, list[str]]:
    tags = re.findall(r'<s n="([^"]*)"\s*/>', xml)
    text = re.sub(r"<b\s*/>", " ", xml)
    text = re.sub(r"<[^>]*>", "", text)
    text = unicodedata.normalize("NFC", re.sub(r"\s+", " ", text).strip())
    return text, tags


def parse(path: Path, side: str):
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    for match in re.finditer(r"<e(\s[^>]*)?>(.*?)</e>", text, re.S):
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', match.group(1) or ""))
        body = match.group(2)
        if attrs.get("i") == "yes" or "<re>" in body:
            continue
        pair = re.search(r"<p>\s*<l>(.*?)</l>\s*<r>(.*?)</r>\s*</p>", body, re.S)
        if pair:
            left, right = pair.group(1), pair.group(2)
        else:
            same = re.search(r"<i>(.*?)</i>", body, re.S)
            if not same:
                continue
            left = right = same.group(1)
        ours, theirs = (left, right) if side == "l" else (right, left)
        (head, tags), (gloss, gloss_tags) = side_text(ours), side_text(theirs)
        if not head or not gloss or "np" in tags or "np" in gloss_tags:
            continue
        if not re.search(r"[^\W\d_]", head) or not re.search(r"[^\W\d_]", gloss):
            continue
        if head.isupper() or len(head) == 1:
            continue  # acronyms, Roman numerals, letter names
        variety = next((attrs[a] for a in VARIETY_ATTRS if a in attrs), None)
        first = tags[0] if tags else (gloss_tags[0] if gloss_tags else "")
        yield head, gloss, POS.get(first, "other" if first else ""), variety


def main() -> None:
    for raw, side, gloss_lang, outputs in JOBS:
        rows: dict[str | None, list[tuple[str, str, str]]] = {key: [] for key in outputs}
        seen: set[tuple] = set()
        skipped: dict[str, int] = {}
        for head, gloss, pos, variety in parse(HERE / "raw" / raw, side):
            if variety not in outputs:
                skipped[variety] = skipped.get(variety, 0) + 1
                continue
            key = (variety, head, gloss, pos)
            if key not in seen:
                seen.add(key)
                rows[variety].append((head, gloss, pos))
        for variety, name in outputs.items():
            with (HERE / name).open("w", encoding="utf-8") as out:
                out.write("headword\tgloss\tgloss_lang\tpos\n")
                for head, gloss, pos in rows[variety]:
                    out.write(f"{head}\t{gloss}\t{gloss_lang}\t{pos}\n")
            print(f"{name}: {len(rows[variety])} rows, {len({r[0] for r in rows[variety]})} headwords")
        if skipped:
            print("  other varieties left out:", skipped)


if __name__ == "__main__":
    main()
