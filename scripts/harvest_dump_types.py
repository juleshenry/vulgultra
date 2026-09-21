#!/usr/bin/env python3
"""Harvest lemma titles / word types from Wiktionary + Wikipedia dumps we already have."""

from __future__ import annotations

import argparse
import bz2
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
XMLS = ROOT / "xmls"
WIKI = XMLS / "wiki"
INC = XMLS / "incubator"
OUT = ROOT / "data" / "words"

WORD_RE = re.compile(r"[^\W\d_]{2,}", re.UNICODE)
SKIP_NS = (
    "Wikipedia:", "Wiktionary:", "Category:", "Template:", "Module:",
    "Help:", "File:", "MediaWiki:", "User:", "Talk:", "Special:",
    "Portal:", "Draft:", "TimedText:",
)

# Highest-leverage lects that were <10k kaikki but have dumps
DEFAULT_CODES = [
    "oc", "scn", "an", "vec", "lld", "pms", "sc", "wa", "la", "lmo",
    "rup", "lij", "mwl", "fur", "lad", "frp", "pcd", "nap", "rm",
]


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def is_content_title(title: str) -> bool:
    if not title or title.startswith(SKIP_NS):
        return False
    if ":" in title and title.split(":", 1)[0][0].isupper():
        return False
    return True


def stream_pages(path: Path):
    opener = bz2.open if path.suffix == ".bz2" else open
    with opener(path, "rt", encoding="utf-8", errors="replace") as f:
        for _ev, elem in ET.iterparse(f, events=("end",)):
            if local(elem.tag) != "page":
                continue
            title_el = elem.find(".//{*}title")
            text_el = elem.find(".//{*}text")
            title = title_el.text if title_el is not None else None
            text = text_el.text if text_el is not None else None
            yield title, text
            elem.clear()


def harvest_wikt(path: Path, limit: int | None = None) -> set[str]:
    titles: set[str] = set()
    for title, _text in stream_pages(path):
        if title and is_content_title(title):
            titles.add(title)
            if limit and len(titles) >= limit:
                break
    return titles


def harvest_wiki(path: Path, max_pages: int | None = None) -> tuple[set[str], set[str]]:
    titles: set[str] = set()
    types: set[str] = set()
    n = 0
    for title, text in stream_pages(path):
        if not title or not is_content_title(title):
            continue
        titles.add(title)
        if text:
            for w in WORD_RE.findall(text):
                if 2 <= len(w) <= 40:
                    types.add(w.casefold())
        n += 1
        if max_pages and n >= max_pages:
            break
    return titles, types


def find_wikt(code: str) -> Path | None:
    candidates = [
        XMLS / f"{code}wiktionary-latest-pages-articles.xml",
        XMLS / f"roa_{code}wiktionary-latest-pages-articles.xml",
        XMLS / f"roa-{code}wiktionary-latest-pages-articles.xml",
        INC / f"{code}wiktionary-incubator-pages-articles.xml",
    ]
    if code == "rup":
        candidates.insert(0, XMLS / "roa_rupwiktionary-latest-pages-articles.xml")
    for p in candidates:
        if p.exists():
            return p
    return None


def find_wiki(code: str) -> Path | None:
    candidates = [
        WIKI / f"{code}wiki-latest-pages-articles.xml.bz2",
        WIKI / f"roa_{code}wiki-latest-pages-articles.xml.bz2",
        WIKI / f"roa-{code}wiki-latest-pages-articles.xml.bz2",
        XMLS / f"{code}wiki-latest-pages-articles.xml",
        XMLS / f"{code}wiki-latest-pages-articles.xml.bz2",
    ]
    if code == "rup":
        candidates.insert(0, WIKI / "roa_rupwiki-latest-pages-articles.xml.bz2")
    if code in ("eml", "egl"):
        candidates.insert(0, WIKI / "emlwiki-latest-pages-articles.xml.bz2")
    for p in candidates:
        if p.exists():
            return p
    return None


def merge_into_words_json(code: str, titles: set[str], types: set[str]) -> None:
    dest = OUT / f"{code}_words.json"
    if dest.exists():
        data = json.loads(dest.read_text(encoding="utf-8"))
    else:
        data = {"meta": {"lang": code, "n_entries": 0}, "entries": {}}
    entries = data.setdefault("entries", {})
    added = 0
    for t in titles:
        if t not in entries:
            entries[t] = {code: t, "pos": [], "glosses_en": [], "sources": ["dump_title"]}
            added += 1
        else:
            srcs = entries[t].setdefault("sources", [])
            if "dump_title" not in srcs:
                srcs.append("dump_title")
    data["meta"]["lang"] = code
    data["meta"]["n_entries"] = len(entries)
    if titles:
        data["meta"]["n_dump_titles"] = len(titles)
    if types:
        data["meta"]["n_wiki_types"] = len(types)
    dest.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    wiki_n = data["meta"].get("n_wiki_types", 0)
    print(f"  merged +{added} titles → {dest.name} now {len(entries)} entries; wiki types {wiki_n}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("codes", nargs="*", default=DEFAULT_CODES)
    ap.add_argument("--wiki-max-pages", type=int, default=0, help="0 = all pages")
    ap.add_argument(
        "--title-limit",
        type=int,
        default=0,
        help="stop after N Wiktionary content titles (0 = all)",
    )
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    max_pages = args.wiki_max_pages or None
    title_limit = args.title_limit or None

    print(f"{'code':6} {'wikt':>8} {'wikiT':>8} {'wikiTypes':>10} {'status'}")
    for code in args.codes:
        wikt_p = find_wikt(code)
        wiki_p = find_wiki(code)
        titles: set[str] = set()
        types: set[str] = set()
        wikt_n = wiki_t = wiki_ty = 0
        if wikt_p:
            print(f"{code}: harvesting wikt {wikt_p.name}…", flush=True)
            titles |= harvest_wikt(wikt_p, limit=title_limit)
            wikt_n = len(titles)
        if wiki_p:
            print(f"{code}: harvesting wiki {wiki_p.name}…", flush=True)
            wt, ty = harvest_wiki(wiki_p, max_pages=max_pages)
            types |= ty
            wiki_t, wiki_ty = len(wt), len(ty)
        if not titles and not types:
            print(f"{code:6} {'—':>8} {'—':>8} {'—':>10}  no dump")
            continue
        # Wiktionary titles → lemmas; wiki running-text types counted only
        merge_into_words_json(code, titles, types)
        n = json.loads((OUT / f"{code}_words.json").read_text())["meta"]["n_entries"]
        flag = "CLEAR" if n >= 10_000 or wiki_ty >= 10_000 else "under"
        print(f"{code:6} {wikt_n:8} {wiki_t:8} {wiki_ty:10}  {flag} entries={n}", flush=True)


if __name__ == "__main__":
    main()
