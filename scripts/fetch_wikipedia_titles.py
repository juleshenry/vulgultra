#!/usr/bin/env python3
"""Pair the Latin Wikipedia's article titles with the lects' titles for the same articles.

The Latin Wikipedia's article *Camelus* is linked to the Friulian
Wikipedia's *Camêl* and the Piedmontese *Camel*: two titles for one
subject, set by the people who write those Wikipedias. For the Bible's
plants, animals, metals and tools that is often the only place a small
lect's word is written down next to anything Latin.

Downloads two tables of the Latin Wikipedia (its pages, 10 MB, and their
interlanguage links, 73 MB) and writes
`data/sources/wikipedia/latin_titles.tsv`: `latin`, `lect`, `title`, one-word
titles only, lowercased.

    python3 scripts/fetch_wikipedia_titles.py
"""

from __future__ import annotations

import collections
import gzip
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "sources" / "wikipedia"
TARGET = OUT / "latin_titles.tsv"
USER_AGENT = "vulgultra-research/0.1 (+noncommercial; lexical sourcing)"
DUMP = "https://dumps.wikimedia.org/lawiki/latest/lawiki-latest-{table}.sql.gz"
# The code of a lect's Wikipedia, where it is not the lect's. The Emilian-Romagnol
# Wikipedia mixes the two lects article by article, so it is left out.
WIKI = {"an": "an", "ast": "ast", "co": "co", "ext": "ext", "frp": "frp", "fur": "fur", "gl": "gl", "lad": "lad",
        "lij": "lij", "lld": "lld", "lmo": "lmo", "mwl": "mwl", "nrm": "nrf", "oc": "oc", "pcd": "pcd",
        "pms": "pms", "rm": "rm", "roa-rup": "rup", "sc": "sc", "scn": "scn", "vec": "vec", "wa": "wa",
        "fr": "fr", "es": "es", "pt": "pt", "it": "it", "ca": "ca", "ro": "ro"}
PAGE = re.compile(rb"\((\d+),(\d+),'((?:[^'\\]|\\.)*)',(\d)")
LINK = re.compile(rb"\((\d+),'([^']*)','((?:[^'\\]|\\.)*)'\)")


def table(name: str) -> Path:
    path = OUT / f"lawiki-latest-{name}.sql.gz"
    if not path.is_file():
        OUT.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(DUMP.format(table=name), headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=180) as response:
            path.write_bytes(response.read())
    return path


def one_word(title: bytes) -> str:
    """The title as a lowercase word, or "" for a phrase, a name with a qualifier, or a number."""
    text = title.decode("utf-8", errors="replace").replace("\\'", "'").replace("_", " ")
    text = re.sub(r"\s*\([^)]*\)$", "", text).strip()
    return text.lower() if text and " " not in text and not any(ch.isdigit() for ch in text) else ""


def main() -> None:
    latin: dict[bytes, str] = {}
    with gzip.open(table("page")) as stream:
        for line in stream:
            for page, namespace, title, redirect in PAGE.findall(line):
                if namespace == b"0" and redirect == b"0" and one_word(title):
                    latin[page] = one_word(title)
    kept: collections.Counter = collections.Counter()
    with gzip.open(table("langlinks")) as stream, TARGET.open("w", encoding="utf-8") as out:
        out.write("latin\tlect\ttitle\n")
        for line in stream:
            for page, wiki, title in LINK.findall(line):
                lect = WIKI.get(wiki.decode())
                if lect and page in latin and one_word(title):
                    out.write(f"{latin[page]}\t{lect}\t{one_word(title)}\n")
                    kept[lect] += 1
    print(f"{len(latin):,} one-word Latin titles; pairs kept:", dict(kept.most_common()))


if __name__ == "__main__":
    main()
