#!/usr/bin/env python3
"""Fetch six public-domain or openly licensed Bibles and write them one verse per row.

Latin (Clementine Vulgate), French (Segond 1910), Spanish (Reina-Valera 1909),
Portuguese (Bíblia Livre) and Italian (Riveduta 1927) are eBible.org's
verse-per-line archives; Romanian (Cornilescu, corrected spelling) is the USFX
file of seven1m/open-bibles, pinned to a commit. Downloads stay in
`data/bible/raw/` and are fetched once; the licence statement travels with
them (`*_about.htm` inside each archive, the open-bibles README). Each edition
becomes `data/bible/texts/{code}.tsv` (book, chapter, verse, text: USFM book
codes, the source file's verse numbering, plain tabs, no quoting) and
`data/bible/freq/{code}.tsv` (word, count). Editions, licences and
versification are in `docs/bible_sources.md`.

    python3 scripts/fetch_bible_texts.py            # all six; downloads only what is not on disk
    python3 scripts/fetch_bible_texts.py la ro      # these editions
    python3 scripts/fetch_bible_texts.py --force    # download again
"""

from __future__ import annotations

import argparse
import re
import shutil
import time
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIBLE = ROOT / "data" / "bible"
RAW, TEXTS, FREQ = BIBLE / "raw", BIBLE / "texts", BIBLE / "freq"
USER_AGENT = "vulgultra-research/0.1 (+noncommercial)"
PAUSE = 2.0  # seconds between downloads
EBIBLE = "https://ebible.org/Scriptures/"
OPEN_BIBLES = "https://raw.githubusercontent.com/seven1m/open-bibles/5b378569502e65f45a0b6f16687df024b2934460/"
# Per edition, the files kept in data/bible/raw/: the text first, then what states its licence.
FILES = {
    "la": {"latVUC_vpl.zip": EBIBLE + "latVUC_vpl.zip"},
    "fr": {"fraLSG_vpl.zip": EBIBLE + "fraLSG_vpl.zip"},
    "es": {"spaRV1909_vpl.zip": EBIBLE + "spaRV1909_vpl.zip"},
    "pt": {"porbr2018_vpl.zip": EBIBLE + "porbr2018_vpl.zip"},
    "it": {"ita1927_vpl.zip": EBIBLE + "ita1927_vpl.zip"},
    "ro": {"ron-rccv.usfx.xml": OPEN_BIBLES + "ron-rccv.usfx.xml",
           "open-bibles-README.md": OPEN_BIBLES + "README.md"},
}
MODERN = ("fr", "es", "pt", "it", "ro")
# What is not Bible text in the verse-per-line files: eBible's inline record of a verse's
# number in the printed edition, "(H24-2)" or "(G9-51)", and three chapter headings left
# inside Matthew in the Riveduta source.
RESIDUE = re.compile(r"\([A-Z]\d+-\d+\)|Matteo Capitolo \d+")
# A word: letters, with apostrophes and hyphens kept between letters.
WORD = re.compile(r"[^\W\d_]+(?:['’-][^\W\d_]+)*")
# USFX elements that hold no verse text.
USFX_SKIP = {"id", "ide", "h", "f", "x"}


def download(url: str, target: Path) -> None:
    partial = target.with_name(target.name + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response, partial.open("wb") as out:
        shutil.copyfileobj(response, out)
    partial.rename(target)
    time.sleep(PAUSE)


def vpl_rows(path: Path):
    """The verses of an eBible verse-per-line archive; its `*_vpl.xml` carries USFM book codes."""
    with zipfile.ZipFile(path) as archive:
        name = next(name for name in archive.namelist() if name.endswith("_vpl.xml"))
        with archive.open(name) as stream:
            for verse in ET.parse(stream).getroot().iter("v"):
                yield verse.get("b"), verse.get("c"), verse.get("v"), "".join(verse.itertext())


def usfx_events(element: ET.Element):
    """Walk in document order: ("c", n), ("v", n) and ("text", s); titles and notes are left out."""
    for child in element:
        if child.tag in ("c", "v"):
            yield child.tag, child.get("id")
        elif child.tag not in USFX_SKIP and not child.get("sfm"):
            if child.text:
                yield "text", child.text
            yield from usfx_events(child)
        if child.tail:
            yield "text", child.tail


def usfx_rows(path: Path):
    """The verses of a USFX file: `c` and `v` are milestones, a verse runs to the next one."""
    for book in ET.parse(path).getroot().iter("book"):
        chapter = verse = None
        text: list[str] = []
        for kind, value in usfx_events(book):
            if kind == "text":
                text.append(value)
                continue
            if verse:
                yield book.get("id"), chapter, verse, "".join(text)
            chapter, verse = (value, None) if kind == "c" else (chapter, value)
            text = []
        if verse:
            yield book.get("id"), chapter, verse, "".join(text)


def clean(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", RESIDUE.sub(" ", text)).split())


def build(code: str) -> tuple[int, int, int]:
    """Write the edition's text and frequency tables; return its books, verses and word forms."""
    source = RAW / next(iter(FILES[code]))
    rows = [(book, chapter, verse, clean(text))
            for book, chapter, verse, text in (vpl_rows if source.suffix == ".zip" else usfx_rows)(source)]
    rows = [row for row in rows if row[3]]  # a verse number the edition leaves empty is not a verse
    counts = Counter(word for row in rows for word in WORD.findall(row[3].lower()))
    for folder in (TEXTS, FREQ):
        folder.mkdir(parents=True, exist_ok=True)
    with (TEXTS / f"{code}.tsv").open("w", encoding="utf-8", newline="") as out:
        out.write("book\tchapter\tverse\ttext\n")
        out.writelines("\t".join(row) + "\n" for row in rows)
    with (FREQ / f"{code}.tsv").open("w", encoding="utf-8", newline="") as out:
        out.write("word\tcount\n")
        out.writelines(f"{word}\t{count}\n" for word, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])))
    return len({row[0] for row in rows}), len(rows), len(counts)


def keys(code: str) -> set[tuple[str, ...]]:
    with (TEXTS / f"{code}.tsv").open(encoding="utf-8") as stream:
        next(stream)
        return {tuple(line.split("\t", 3)[:3]) for line in stream}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("codes", nargs="*", help=f"edition codes ({' '.join(FILES)}); default: all")
    parser.add_argument("--force", action="store_true", help="download again what is already on disk")
    args = parser.parse_args()
    if unknown := set(args.codes) - set(FILES):
        parser.error(f"unknown edition: {' '.join(sorted(unknown))}")
    RAW.mkdir(parents=True, exist_ok=True)
    for code in args.codes or FILES:
        for name, url in FILES[code].items():
            if args.force or not (RAW / name).is_file():
                download(url, RAW / name)
                print(f"{code}: fetched {url}", flush=True)
        books, verses, forms = build(code)
        print(f"{code}: {books} books, {verses} verses, {forms} word forms → {TEXTS / f'{code}.tsv'}", flush=True)
    if all((TEXTS / f"{code}.tsv").is_file() for code in FILES):
        found = {code: keys(code) for code in FILES}
        modern = set.intersection(*(found[code] for code in MODERN))
        print(f"shared (book, chapter, verse) keys: all six {len(modern & found['la'])}; "
              f"{' '.join(MODERN)} {len(modern)}; "
              + "; ".join(f"la+{code} {len(found['la'] & found[code])}" for code in MODERN), flush=True)


if __name__ == "__main__":
    main()
