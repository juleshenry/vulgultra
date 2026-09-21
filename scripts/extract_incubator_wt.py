#!/usr/bin/env python3
"""Split incubatorwiki dump into per-lect mini MediaWiki XMLs (Wt/{code}/ pages)."""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

# Incubator Wt/ code -> output file stem(s)
TARGETS: dict[str, tuple[str, ...]] = {
    "pms": ("pms",),
    "mwl": ("mwl",),
    "nrf": ("nrf",),       # Norman — prefer over nrm
    "lad": ("lad",),
    "lij": ("lij",),
    "egl": ("egl", "eml"), # Emilian
    "pcd": ("pcd",),
    "frp": ("frp",),
    "fur": ("fur",),
    "nrm": ("nrm",),       # thin
    "ext": ("ext",),       # book source available; Incubator still empty
}

TITLE_RE = re.compile(r"^Wt/([^/]+)/(.+)$")
SKIP_PREFIXES = ("Template:", "Module:", "Category:", "MediaWiki:", "Help:", "User:", "Talk:")


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def extract(dump: Path, out_dir: Path, want: set[str]) -> Counter:
    out_dir.mkdir(parents=True, exist_ok=True)
    handles: dict[str, object] = {}
    counts: Counter = Counter()

    def handle(stem: str):
        if stem not in handles:
            path = out_dir / f"{stem}wiktionary-incubator-pages-articles.xml"
            f = path.open("w", encoding="utf-8")
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.11/">\n')
            handles[stem] = f
        return handles[stem]

    try:
        for _event, elem in ET.iterparse(dump, events=("end",)):
            if local(elem.tag) != "page":
                continue
            title_el = elem.find(".//{*}title")
            if title_el is None or not title_el.text:
                elem.clear()
                continue
            m = TITLE_RE.match(title_el.text)
            if not m:
                elem.clear()
                continue
            code, rest = m.group(1), m.group(2)
            if code not in want:
                elem.clear()
                continue
            if rest.startswith(SKIP_PREFIXES):
                elem.clear()
                continue
            # Drop deep meta paths; keep simple lemmas Wt/code/word
            if "/" in rest:
                elem.clear()
                continue

            xml_page = ET.tostring(elem, encoding="unicode")
            for stem in TARGETS.get(code, (code,)):
                handle(stem).write(xml_page + "\n")
                counts[stem] += 1
            elem.clear()
    finally:
        for stem, f in handles.items():
            f.write("</mediawiki>\n")
            f.close()
            path = out_dir / f"{stem}wiktionary-incubator-pages-articles.xml"
            print(f"wrote {path} ({counts[stem]} pages)")

    return counts


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-i", "--input", default="xmls/incubatorwiki-latest-pages-articles.xml")
    ap.add_argument("-o", "--out-dir", default="xmls/incubator")
    ap.add_argument("--codes", default=",".join(TARGETS))
    args = ap.parse_args()

    dump = Path(args.input)
    if not dump.exists():
        raise SystemExit(f"missing dump: {dump}")
    want = {c.strip() for c in args.codes.split(",") if c.strip()}

    print(f"extracting {sorted(want)} from {dump} → {args.out_dir}")
    counts = extract(dump, Path(args.out_dir), want)
    print("--- totals ---")
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {k:4} {v:6}")
    print("done")


if __name__ == "__main__":
    main()
