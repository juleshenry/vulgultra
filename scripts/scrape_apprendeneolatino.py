#!/usr/bin/env python3
"""Scrape apprendeneolatino.com, the lesson site the Learn Vulgultra site is modelled on.

Every page in the site's sitemap is fetched with Scrapling and kept as HTML
under data/sources/apprendeneolatino/ (ignored by git: it is someone else's
text). What the site skeleton takes from it is the structure only, printed
at the end: the lesson tree, category by category, as site/sidebar.yml
mirrors it.

Scrapling is not in the project's .venv. Run this with the Python that has
it, for example `python3.12 scripts/scrape_apprendeneolatino.py`. A page
already on disk is not fetched again; pass --refetch to replace it.
"""

from __future__ import annotations

import argparse
import re
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

from scrapling.fetchers import Fetcher
from scrapling.parser import Selector

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.apprendeneolatino.com"
OUT = ROOT / "data" / "sources" / "apprendeneolatino"
# A lesson page whose sidebar lists every category.
SIDEBAR_PAGE = "/lessons/pronunciation/alphabet"
EXTRA_PATHS = ("/es/", "/img/logo.svg")


def page_file(path: str) -> Path:
    name = unquote(path).strip("/").replace("/", "__") or "index"
    return OUT / "pages" / f"{name}.html"


def fetch(path: str, dest: Path, refetch: bool) -> str:
    """Save one URL. Returns "cached", the HTTP status, or the error."""
    if dest.exists() and dest.stat().st_size and not refetch:
        return "cached"
    for _ in range(3):
        try:
            response = Fetcher.get(BASE + path, stealthy_headers=True, timeout=30)
        except Exception as error:  # a dropped connection; try again
            status = repr(error)[:100]
        else:
            status = str(response.status)
            if response.status == 200:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(response.body)
                return status
        time.sleep(1.5)
    return status


def sitemap_paths(refetch: bool) -> list[str]:
    dest = OUT / "sitemap.xml"
    fetch("/sitemap.xml", dest, refetch)
    locations = re.findall(r"<loc>(.*?)</loc>", dest.read_text(encoding="utf-8"))
    return sorted({urlparse(location).path or "/" for location in locations})


def selector(path: str) -> Selector:
    return Selector(page_file(path).read_text(encoding="utf-8"))


def lesson_tree() -> list[dict]:
    """The sidebar's top-level entries, each with the lessons on its category page."""
    menu = selector(SIDEBAR_PAGE).css("ul.theme-doc-sidebar-menu")[0]
    tree = []
    for item in menu.xpath("./li"):
        link = item.xpath("./div/a | ./a")[0]
        node = {"title": link.get_all_text(strip=True), "href": unquote(link.attrib["href"]), "lessons": []}
        if node["href"].startswith("/category/"):
            for card in selector(node["href"]).css("article a.card"):
                heading = card.css("h2")[0]
                node["lessons"].append({
                    "title": heading.attrib.get("title") or heading.get_all_text(strip=True),
                    "href": unquote(card.attrib["href"]),
                })
        tree.append(node)
    return tree


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--refetch", action="store_true", help="fetch pages that are already on disk")
    args = parser.parse_args()

    paths = sitemap_paths(args.refetch)
    failed = {}
    for path in paths:
        status = fetch(path, page_file(path), args.refetch)
        if status not in ("cached", "200"):
            failed[path] = status
        if status != "cached":
            time.sleep(0.25)
    home = page_file("/").read_text(encoding="utf-8")
    stylesheets = re.findall(r'href="(/assets/css/[^"]+\.css)"', home)
    for path in (*EXTRA_PATHS, *stylesheets):
        name = unquote(path).strip("/").replace("/", "__") or "index"
        status = fetch(path, OUT / "assets" / name, args.refetch)
        if status not in ("cached", "200"):
            failed[path] = status

    tree = lesson_tree()
    for node in tree:
        print(f"{node['title']}  {node['href']}")
        for lesson in node["lessons"]:
            print(f"    {lesson['title']}  {lesson['href']}")
    lessons = sum(len(node["lessons"]) for node in tree)
    print(f"\n{len(paths)} pages in the sitemap, {len(tree)} sidebar entries, {lessons} lessons; saved under {OUT}")
    if failed:
        print(f"not fetched: {failed}")


if __name__ == "__main__":
    main()
