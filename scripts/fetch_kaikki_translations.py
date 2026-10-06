#!/usr/bin/env python3
"""Stream Kaikki's extracts of Wiktionary editions and keep their translation tables.

The same reading as `extract_wikt_translations.py`, for the editions that
are not on disk as dumps: English first (3.3 GB, the largest set of
translation tables there is), then German, Russian, Polish, Dutch, Greek,
Czech, Chinese, Japanese, Turkish and Kurdish. Nothing is stored but the rows
of the lects and of Latin: `data/sources/wikt_translations/{edition}.tsv`
(`headword`, `table`, `code`, `form`), where `table` is the part of speech
and the sense the table is headed with.

Those editions also have entries of their own for words of the lects (the
Polish one has 400 Dalmatian words, glossed in Polish) and for Latin words.
Both are kept as `data/sources/wikt_entries/{edition}.tsv` (`code`, `word`,
`pos`, `gloss`): a lect's word and a Latin word glossed alike in Polish are
matched without anyone reading Polish. The English edition's entries are
the extracts already on disk, so only its tables are taken.

    python3 scripts/fetch_kaikki_translations.py            # every edition not yet on disk
    python3 scripts/fetch_kaikki_translations.py en de
"""

from __future__ import annotations

import argparse
import collections
import gzip
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from extract_wikt_translations import CODES, OUT, clean  # noqa: E402

ENTRIES = ROOT / "data" / "sources" / "wikt_entries"
USER_AGENT = "vulgultra-research/0.1 (+noncommercial morphology corpus)"
MARK = b'"lang_code": "'
ENGLISH = "https://kaikki.org/dictionary/English/kaikki.org-dictionary-English.jsonl"
OTHER = "https://kaikki.org/{edition}wiktionary/raw-wiktextract-data.jsonl.gz"
EDITIONS = ("en", "de", "ru", "pl", "nl", "el", "cs", "zh", "ja", "tr", "ku")


def fetch(edition: str) -> tuple[collections.Counter, collections.Counter]:
    url = ENGLISH if edition == "en" else OTHER.format(edition=edition)
    kept: collections.Counter = collections.Counter()
    entries: collections.Counter = collections.Counter()
    OUT.mkdir(parents=True, exist_ok=True)
    ENTRIES.mkdir(parents=True, exist_ok=True)
    partial, partial_entries = OUT / f"{edition}.tsv.part", ENTRIES / f"{edition}.tsv.part"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response, partial.open("w", encoding="utf-8") as out, \
            partial_entries.open("w", encoding="utf-8") as listed_entries:
        out.write("headword\ttable\tcode\tform\n")
        listed_entries.write("code\tword\tpos\tgloss\n")
        for line in (response if edition == "en" else gzip.GzipFile(fileobj=response)):
            at = line.find(MARK)
            own = line[at + len(MARK):line.find(b'"', at + len(MARK))].decode("ascii", "replace") if at >= 0 else ""
            if b'"translations"' not in line and (edition == "en" or own not in CODES):
                continue
            entry = json.loads(line)
            head = entry.get("word", "")
            if not head or "\t" in head:
                continue
            code = CODES.get(entry.get("lang_code", ""))
            if code and edition != "en" and " " not in head:
                for sense in (entry.get("senses") or [])[:4]:
                    if sense.get("form_of") or sense.get("alt_of"):
                        continue
                    for gloss in (sense.get("glosses") or [])[:1]:
                        gloss = gloss.replace("\t", " ").replace("\n", " ").strip()[:160]
                        if gloss:
                            listed_entries.write(f"{code}\t{head}\t{entry.get('pos', '')}\t{gloss}\n")
                            entries[code] += 1
            # A table the extractor could tie to one sense sits under that sense.
            listed = list(entry.get("translations") or [])
            for sense in entry.get("senses") or []:
                listed += sense.get("translations") or []
            for translation in listed:
                code = CODES.get(translation.get("code") or translation.get("lang_code") or "")
                form = clean(translation.get("word") or "")
                if code and form:
                    sense = str(translation.get("sense") or translation.get("sense_index") or "")
                    table = f"{entry.get('pos', '')}: {sense}".replace("\t", " ").replace("\n", " ")[:120]
                    out.write(f"{head}\t{table}\t{code}\t{form}\n")
                    kept[code] += 1
    partial.rename(OUT / f"{edition}.tsv")
    if edition == "en":
        partial_entries.unlink()
    else:
        partial_entries.rename(ENTRIES / f"{edition}.tsv")
    return kept, entries


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("editions", nargs="*", help=f"default: those of {' '.join(EDITIONS)} not yet on disk")
    parser.add_argument("--force", action="store_true", help="fetch again what is already on disk")
    args = parser.parse_args()
    for edition in args.editions or EDITIONS:
        if (OUT / f"{edition}.tsv").is_file() and not args.force:
            print(f"{edition}: on disk", flush=True)
            continue
        kept, entries = fetch(edition)
        print(edition, "tables:", sum(kept.values()), dict(kept.most_common()), flush=True)
        print(edition, "entries:", sum(entries.values()), dict(entries.most_common()), flush=True)


if __name__ == "__main__":
    main()
