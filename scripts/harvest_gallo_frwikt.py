#!/usr/bin/env python3
"""Harvest Gallo conjugations from French Wiktionary Conjugaison:gallo pages.

Source: https://fr.wiktionary.org/wiki/Catégorie:Conjugaison_en_gallo
Subject pronouns are stripped so ending inventories can run.
"""

from __future__ import annotations

import html as html_lib
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data" / "conjugation" / "sources" / "gallo_diseux.json"
CACHE = ROOT / "data" / "sources" / "gallo_frwikt"
USER_AGENT = "vulgultra-research/0.1 (+noncommercial; cite Wiktionnaire)"
API = "https://fr.wiktionary.org/w/api.php"
SLOTS = ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")

SKIP_TITLES = {
    "conjugaison:gallo",
    "conjugaison:gallo/premier groupe",
    "conjugaison:gallo/deuxième groupe",
    "conjugaison:gallo/deuxieme groupe",
    "conjugaison:gallo/troisième groupe",
    "conjugaison:gallo/troisieme groupe",
}

IRREGULAR = {
    "aler": "aler", "avair": "avair", "aveir": "avair",
    "étr": "étr", "éstr": "étr", "ói": "ói", "se nalae": "aler",
}

_OIL_COMPL = re.compile(r"^(?:qu['’]|q['’]|qe)\s*", re.I)
_OIL_WORD = re.compile(r"^(?:je|j['’]|tu|t['’]|vous|v['’]|il|i)\s+", re.I)
_OIL_ELIDE = re.compile(r"^[jtv]['’]", re.I)


def fold(text: str) -> str:
    stripped = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode()
    return stripped.lower().strip()


def class_from_lemma(lemma: str) -> str:
    low = lemma.lower().strip()
    if low in IRREGULAR:
        return IRREGULAR[low]
    for ending in ("air", "ae", "er", "ir", "rr", "i", "r"):
        if low.endswith(ending):
            return f"-{ending}"
    return "other"


def clean_html(text: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = html_lib.unescape(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"[^\S\n]+", " ", text)
    text = re.sub(r"\n+", "\n", text).strip()
    text = text.rstrip("*").strip()
    return text


def strip_pronoun(form: str) -> str:
    text = form.strip()
    text = text.split("\n")[0].strip().rstrip("*").strip()
    for _ in range(3):
        nxt = _OIL_COMPL.sub("", text).strip()
        nxt = _OIL_WORD.sub("", nxt).strip()
        nxt = _OIL_ELIDE.sub("", nxt).strip()
        if nxt == text:
            break
        text = nxt
    return text.strip("-").strip()


def tense_feature(mood: str | None, header: str) -> str | None:
    left = fold(header)
    if not mood or not left:
        return None
    if any(bit in left for bit in ("compose", "plus-que", "anterieur", "passe 1", "passe 2")):
        # Dual headers: left is simple, right is compound. Only the left th
        # is passed in, so "passe compose" as a left header should be skipped.
        if left.startswith("passe compose") or left.startswith("plus-que") or "anterieur" in left:
            return None
        if left in {"passe 1", "passe 2"}:
            return None
    if mood == "indicative":
        if left.startswith("present"):
            return "indicative.present"
        if "imparfait" in left:
            return "indicative.imperfect"
        if "passe simple" in left:
            return "indicative.preterite"
        if left.startswith("futur"):
            return "indicative.future"
    if mood == "subjunctive":
        if left.startswith("present 2"):
            return "subjunctive.present-2"
        if left.startswith("present"):
            return "subjunctive.present"
        if "imparfait" in left:
            return "subjunctive.imperfect"
    if mood == "conditional" and left.startswith("present"):
        return "conditional"
    if mood == "imperative":
        return "imperative"
    return None


def parse_html(html: str, lemma: str, url: str) -> dict[str, dict]:
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, flags=re.I | re.S)
    mood: str | None = None
    feature: str | None = None
    buffer: list[str] = []
    cells: dict[str, dict] = {}

    def flush() -> None:
        nonlocal buffer, feature
        if not feature or not buffer:
            buffer = []
            return
        if feature == "imperative":
            mapping = list(zip(("2sg", "1pl", "2pl"), buffer[:3]))
        else:
            mapping = list(zip(SLOTS, buffer[:6]))
        row = {}
        for slot, form in mapping:
            form = strip_pronoun(form)
            if not form or form == "-":
                continue
            # Keep the first graphic variant (before slash).
            form = form.split("/")[0].strip()
            if " " in form:
                continue
            row[slot] = {
                "form": form,
                "phonemes": [],
                "source_label": feature,
                "source_url": url,
            }
        if row:
            cells[feature] = row
        buffer = []

    for raw in rows:
        heading = re.search(r"<h3[^>]*>(.*?)</h3>", raw, flags=re.I | re.S)
        if heading:
            flush()
            feature = None
            title = fold(clean_html(heading.group(1)))
            if "indicatif" in title:
                mood = "indicative"
            elif "subjonctif" in title:
                mood = "subjunctive"
            elif "conditionnel" in title:
                mood = "conditional"
            elif "imperatif" in title:
                mood = "imperative"
                feature = "imperative"
            else:
                mood = mood
            continue
        ths = [clean_html(cell) for cell in re.findall(r"<th[^>]*>(.*?)</th>", raw, flags=re.I | re.S)]
        tds = [
            cell for cell in (
                clean_html(raw_cell)
                for raw_cell in re.findall(r"<td[^>]*>(.*?)</td>", raw, flags=re.I | re.S)
            )
            if cell
        ]
        if ths and not tds:
            flush()
            feature = tense_feature(mood, ths[0])
            continue
        if tds and feature:
            buffer.append(tds[0])
            limit = 3 if feature == "imperative" else 6
            if len(buffer) >= limit:
                flush()
                feature = None
    flush()
    return cells


def fetch(url: str, dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 200:
        return dest.read_text(encoding="utf-8", errors="replace")
    delay = 8
    last_error: Exception | None = None
    for _attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as response:
                data = response.read().decode("utf-8", errors="replace")
            dest.write_text(data, encoding="utf-8")
            time.sleep(1.2)
            return data
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in {429, 503, 502}:
                raise
            time.sleep(delay)
            delay = min(delay * 2, 60)
    raise last_error or RuntimeError(url)


def list_titles() -> list[str]:
    titles: list[str] = []
    cont = ""
    while True:
        query = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": "Catégorie:Conjugaison en gallo",
            "cmlimit": "500",
            "format": "json",
        }
        if cont:
            query["cmcontinue"] = cont
        url = API + "?" + urllib.parse.urlencode(query)
        payload = json.loads(fetch(url, CACHE / f"category_{len(titles)}.json"))
        members = payload.get("query", {}).get("categorymembers") or []
        for item in members:
            title = str(item.get("title") or "")
            if item.get("ns") != 116:
                continue
            if fold(title) in SKIP_TITLES:
                continue
            if "/" not in title:
                continue
            titles.append(title)
        cont = (payload.get("continue") or {}).get("cmcontinue") or ""
        if not cont:
            break
    return titles


def parse_page(title: str) -> dict | None:
    lemma = title.split("/", 1)[-1]
    query = {
        "action": "parse",
        "page": title,
        "prop": "text",
        "format": "json",
    }
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", title)
    url = API + "?" + urllib.parse.urlencode(query)
    payload = json.loads(fetch(url, CACHE / f"{slug}.json"))
    html = ((payload.get("parse") or {}).get("text") or {}).get("*") or ""
    if not html:
        return None
    page_url = "https://fr.wiktionary.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))
    cells = parse_html(html, lemma, page_url)
    if not cells:
        return None
    return {
        "lect": "gallo",
        "lemma": lemma,
        "class_source": class_from_lemma(lemma),
        "regularity": "irregular" if class_from_lemma(lemma) in IRREGULAR.values() else "regular",
        "source": {
            "attested": True,
            "title": title,
            "url": page_url,
            "provider": "fr.wiktionary.org",
        },
        "cells": cells,
    }


def main() -> int:
    titles = list_titles()
    print(f"category members: {len(titles)}")
    paradigms: list[dict] = []
    for title in titles:
        packed = parse_page(title)
        if not packed:
            print(f"  skip {title}")
            continue
        present = packed["cells"].get("indicative.present", {})
        print(f"  {packed['lemma']} class={packed['class_source']} present={len(present)} tams={len(packed['cells'])}")
        paradigms.append(packed)
    document = {
        "schema": "vulgultra.conjugation.v1",
        "metadata": {
            "lect": "gallo",
            "purpose": "Gallo conjugations from Wiktionnaire Conjugaison:gallo",
            "provider": "fr.wiktionary.org",
            "attribution": "Wiktionnaire Catégorie:Conjugaison en gallo (CC BY-SA)",
            "ending_inventories": {},
            "optimizer_involved": False,
        },
        "paradigms": sorted(paradigms, key=lambda item: item["lemma"]),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT} paradigms={len(paradigms)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
