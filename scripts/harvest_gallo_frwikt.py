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
# ELG-spelling pages: kept for reference, not merged into the gallo lect.
OUT_ELG = ROOT / "data" / "conjugation" / "sources" / "gallo_elg.json"
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
    "étr": "étr", "éstr": "étr", "ói": "ói", "alae": "aler", "se nalae": "aler",
}

_OIL_COMPL = re.compile(r"^(?:qu['’]|q['’]|qe)\s*", re.I)
# "vous / v'etes": pronoun alternation, not a form variant.
_OIL_ALT = re.compile(r"^vous\s*/\s*", re.I)
# vóz is the ELG spelling of vous; il/ol lists 3rd-person pronoun variants.
_OIL_WORD = re.compile(r"^(?:je|tu|vous|vóz|il/ol|il|ol|i)\s+", re.I)
_OIL_ELIDE = re.compile(r"^[jtv]['’]", re.I)
# Reflexive clitics, proclitic (je me nall) and enclitic imperative (nall tei).
_REFL_WORD = re.compile(r"^(?:me|te|se|nóz|nous|vóz|vous)\s+", re.I)
_REFL_ELIDE = re.compile(r"^[mts]['’]\s*", re.I)
_REFL_ENCLITIC = re.compile(r"\s+(?:tei|toi|te|nóz|nous|vóz|vous)$", re.I)

# éstr lists only clipped ’taes / ’taet; restore the full et- imperfect.
_CLIPPED_ET = re.compile(r"^['’]t")
# Pages written in the ELG spelling announce it in the heading: "chauntae (ELG)".
# ABCD is the Wiktionnaire / kaikki default and stays the canonical Gallo lect.
_ELG_HEADING = re.compile(r"^Conjugaison de [^\n,]*\(ELG\)")


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


def is_reflexive(lemma: str) -> bool:
    return bool(re.match(r"^(?:se\s+|s['’])", lemma.strip(), re.I))


def strip_pronoun(form: str, *, reflexive: bool = False) -> str:
    """One variant line → bare verb form."""
    text = form.strip().rstrip("*").strip()
    for _ in range(4):
        nxt = _OIL_COMPL.sub("", text).strip()
        nxt = _OIL_ALT.sub("", nxt).strip()
        nxt = _OIL_WORD.sub("", nxt).strip()
        nxt = _OIL_ELIDE.sub("", nxt).strip()
        if reflexive:
            nxt = _REFL_WORD.sub("", nxt).strip()
            nxt = _REFL_ELIDE.sub("", nxt).strip()
            nxt = _REFL_ENCLITIC.sub("", nxt).strip()
        if nxt == text:
            break
        text = nxt
    return text.strip("-").strip()


def cell_forms(raw: str, *, reflexive: bool = False) -> list[str]:
    """All variants in a cell, in page order: 'il chauntt\\nil chauntan' → both."""
    forms: list[str] = []
    for line in raw.split("\n"):
        form = strip_pronoun(line, reflexive=reflexive)
        form = _CLIPPED_ET.sub("et", form)
        for piece in form.split("/"):
            piece = piece.strip()
            if not piece or piece == "-" or " " in piece or piece in forms:
                continue
            forms.append(piece)
    return forms


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
    """Several tables on one page are regional radicals / variants.

    The pages state the first table is built on the infinitive's radical
    ("La première forme conjuguée se forme sur le même radical que
    l'infinitif"), so it supplies the primary form; later tables and extra
    lines inside a cell are kept as `variants`.
    """
    reflexive = is_reflexive(lemma)
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
        row = cells.setdefault(feature, {})
        for slot, raw in mapping:
            forms = cell_forms(raw, reflexive=reflexive)
            if not forms:
                continue
            cell = row.get(slot)
            if cell is None:
                cell = row[slot] = {
                    "form": forms[0],
                    "variants": [],
                    "phonemes": [],
                    "source_label": feature,
                    "source_url": url,
                }
                forms = forms[1:]
            for form in forms:
                if form != cell["form"] and form not in cell["variants"]:
                    cell["variants"].append(form)
        if not row:
            cells.pop(feature)
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


# Genuine suppletive forms the foreign-form check would otherwise drop.
SUPPLETIVE = {("faèrr", "indicative.present", "3pl")}  # fon "they do"


def stem_key(text: str) -> str:
    bare = re.sub(r"^(?:se\s+|s['’])", "", text.strip(), flags=re.I)
    return fold(bare)[:2].replace("y", "i")


def drop_foreign_forms(lemma: str, cells: dict[str, dict]) -> list[str]:
    """Drop forms copied from another verb.

    Wiktionnaire pages carry paste errors: chauntae's whole present
    subjunctive is balhae's (bauj), prandr's preterite 3sg is póvit
    (pouvoir). A row or cell is foreign when its opening letters occur
    nowhere else in the verb, including the lemma. Real stem alternations
    (teni → tienrae, perier → prie) always recur across several cells.
    """
    dropped: list[str] = []

    def keys_outside(skip_feature: str | None, skip_slot: str | None) -> set[str]:
        keys = {stem_key(lemma)}
        for feature, row in cells.items():
            for slot, cell in row.items():
                if feature == skip_feature and (skip_slot is None or slot == skip_slot):
                    continue
                keys.add(stem_key(cell["form"]))
        return keys

    for feature, row in list(cells.items()):
        own = {stem_key(cell["form"]) for cell in row.values()}
        if own and not own & keys_outside(feature, None):
            dropped.append(f"{feature} ({' '.join(c['form'] for c in row.values())})")
            cells.pop(feature)
    for feature, row in list(cells.items()):
        for slot, cell in list(row.items()):
            if (lemma, feature, slot) in SUPPLETIVE:
                continue
            if stem_key(cell["form"]) not in keys_outside(feature, slot):
                dropped.append(f"{feature}.{slot} ({cell['form']})")
                row.pop(slot)
        if not row:
            cells.pop(feature)
    return dropped


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
    irregular = class_from_lemma(lemma) in IRREGULAR.values()
    if not irregular:
        for where in drop_foreign_forms(lemma, cells):
            print(f"  drop {lemma} {where}: belongs to another verb")
    if not cells:
        return None
    orthography = "ELG" if _ELG_HEADING.search(clean_html(html)) else "ABCD"
    return {
        "lect": "gallo",
        "lemma": lemma,
        "orthography": orthography,
        "class_source": class_from_lemma(lemma),
        "regularity": "irregular" if irregular else "regular",
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
    by_spelling: dict[str, list[dict]] = {"ABCD": [], "ELG": []}
    for title in titles:
        packed = parse_page(title)
        if not packed:
            print(f"  skip {title}")
            continue
        present = packed["cells"].get("indicative.present", {})
        print(
            f"  {packed['lemma']} [{packed['orthography']}] class={packed['class_source']} "
            f"present={len(present)} tams={len(packed['cells'])}"
        )
        by_spelling[packed["orthography"]].append(packed)
    for orthography, path in (("ABCD", OUT), ("ELG", OUT_ELG)):
        paradigms = by_spelling[orthography]
        document = {
            "schema": "vulgultra.conjugation.v1",
            "metadata": {
                "lect": "gallo",
                "orthography": orthography,
                "purpose": f"Gallo conjugations from Wiktionnaire Conjugaison:gallo ({orthography} spelling)",
                "provider": "fr.wiktionary.org",
                "attribution": "Wiktionnaire Catégorie:Conjugaison en gallo (CC BY-SA)",
                "ending_inventories": {},
                "optimizer_involved": False,
            },
            "paradigms": sorted(paradigms, key=lambda item: item["lemma"]),
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {path} paradigms={len(paradigms)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
