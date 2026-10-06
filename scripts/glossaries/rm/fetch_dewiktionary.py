#!/usr/bin/env python3
"""Stream the Kaikki extract of the German Wiktionary and keep the north-Italian / Alpine lects.

The extract is about 300 MB gzipped; it is read as a stream and only the
entries of the lects below are written, to
`data/sources/glossaries/rm/raw/dewiktionary_north_italy.jsonl`
(all nine lects in one file: only Romansh turned out to have a usable number).

    python3 data/sources/glossaries/rm/fetch_dewiktionary.py
"""

from __future__ import annotations

import collections
import gzip
import json
import urllib.request
from pathlib import Path

URL = "https://kaikki.org/dewiktionary/raw-wiktextract-data.jsonl.gz"
AGENT = "vulgultra-research/0.1 (+noncommercial; lexical sourcing)"
HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
# Wiktionary language codes of the nine lects (Romansh is "rm"; Emilian "egl"/"eml").
LECTS = {"rm", "roh", "fur", "lld", "lmo", "pms", "lij", "eml", "egl", "rgn", "vec"}


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    counts: collections.Counter[tuple[str, str]] = collections.Counter()
    request = urllib.request.Request(URL, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(request, timeout=300) as response, \
            gzip.GzipFile(fileobj=response) as stream, \
            (RAW / "dewiktionary_north_italy.jsonl").open("w", encoding="utf-8") as out:
        for raw in stream:
            line = raw.decode("utf-8")
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            code = entry.get("lang_code") or ""
            counts[(code, entry.get("lang") or "")] += 1
            if code in LECTS:
                out.write(line)
    table = sorted(((code, name, n) for (code, name), n in counts.items()), key=lambda row: -row[2])
    (RAW / "dewiktionary_lang_counts.json").write_text(
        json.dumps(table, ensure_ascii=False, indent=0), encoding="utf-8")
    for code, name, n in table:
        if code in LECTS:
            print(code, name, n)


if __name__ == "__main__":
    main()
