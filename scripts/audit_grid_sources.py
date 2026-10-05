#!/usr/bin/env python3
"""Check a lect's grid column against sources that attest each form with its sense.

A cell is confirmed if its form is attested for that concept: in the lect's
Wiktionary Swadesh list, or as a dictionary headword glossed with the concept.
An unconfirmed cell takes the Swadesh list's form when the list has one. A
dictionary only confirms; it never supplies a form, because a gloss match
cannot tell the everyday word from a rare synonym.

What happens to an unconfirmed cell the list does not cover depends on the
lect (MODES): emptied where the column is fabricated, left alone where it is
sound, and nothing at all is changed where no source can check the column.

  fetch    English Wiktionary Swadesh lists → data/sources/wikt_swadesh/
  extract  thin-lect entries of the local French Wiktionary dump
           → data/sources/frwikt_sections.json
  audit    report in docs/eval/grid_sources.md, columns in
           data/sources/grid_columns.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vulgultra.romance_swadesh import concepts
from vulgultra.swadesh_rest import IDS, RESERVED_TABLES

WIKT_DIR = ROOT / "data" / "sources" / "wikt_swadesh"
FRWIKT = ROOT / "data" / "sources" / "frwikt_sections.json"
WORDS = ROOT / "data" / "words"
USER_AGENT = "vulgultra-research/0.1 (+noncommercial; lexical grid sourcing)"

# Lect → where its Wiktionary Swadesh list lives. Gallo is left out on
# purpose: Appendix:Gallo Swadesh list is filled with Walloon words.
WIKT_LISTS = {
    "ist": "Module:Swadesh/data/ist", "pms": "Module:Swadesh/data/pms",
    "lld": "Module:Swadesh/data/lld", "eml": "Module:Swadesh/data/egl",
    "lij": "Module:Swadesh/data/lij", "dlm": "Appendix:Dalmatian Swadesh list",
}
# Lect → (dictionary, language its glosses are in).
DICTIONARIES = {
    "ist": ("words", "en"), "dlm": ("words", "en"), "lld": ("words", "en"),
    "lij": ("words", "en"), "pms": ("words", "en"), "eml": ("words", "en"),
    "gallo": ("words+frwikt", "fr"), "pcd": ("frwikt", "fr"), "frp": ("frwikt", "fr"),
    "ext": ("es-keyed", "es"),
}
LECTS = tuple(DICTIONARIES)

# strict: an unconfirmed cell with no list form is emptied (the column has
#         invented forms: Istriot dormar, vivar; Dalmatian flotar, fluir).
# list:   only cells the Swadesh list covers are touched.
# report: nothing changes. No Swadesh list exists, and the dictionary is in
#         another spelling or too small for a miss to mean anything.
MODES = {
    "ist": "strict", "dlm": "strict",
    "pms": "list", "lij": "list", "eml": "list", "lld": "list",
    "gallo": "report", "pcd": "report", "frp": "report", "ext": "report",
}

# English glosses that count as the concept, beyond the concept's own word.
EN_KEYS = {
    "you_sg": ["you", "thou"], "you_pl": ["you"], "not": ["not", "no"],
    "all": ["all", "everything", "whole"], "many": ["many", "much"],
    "big": ["big", "large", "great"], "small": ["small", "little"],
    "person": ["person", "human", "human being"], "child": ["child", "kid"],
    "forest": ["forest", "wood", "woods"], "fat": ["fat", "grease"],
    "fingernail": ["nail", "fingernail"], "guts": ["guts", "intestine", "intestines", "bowels", "entrails"],
    "belly": ["belly", "abdomen"], "breast": ["breast", "chest"],
    "hit": ["hit", "strike", "beat"], "walk": ["walk", "go"], "lie": ["lie", "lie down"],
    "squeeze": ["squeeze", "press"], "say": ["say", "tell"], "fear": ["fear", "be afraid"],
    "stone": ["stone", "rock"], "earth": ["earth", "soil", "ground", "land"],
    "fog": ["fog", "mist"], "road": ["road", "way", "street", "path"],
    "warm": ["warm", "hot"], "dull": ["dull", "blunt"], "correct": ["correct", "right"],
    "at": ["at", "to"], "def_art": ["the"], "copula": ["be"], "cat_f": ["cat", "female cat"],
    "dog_f": ["bitch", "female dog"],
}
POS_OF = {"noun": {"noun"}, "verb": {"verb"}, "adj": {"adj", "adjective"}}


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text.strip().lower())


def bare(text: str) -> str:
    """Letters only, so a source's stress accents do not hide a match."""
    plain = "".join(ch for ch in unicodedata.normalize("NFD", text.lower()) if not unicodedata.combining(ch))
    return plain.replace("’", "'").strip()


def gloss_parts(gloss: str) -> set[str]:
    """The separate senses a dictionary gloss names, stripped to bare words."""
    gloss = re.sub(r"\{\{[^{}]*\}\}|\([^)]*\)|''+", " ", gloss)
    gloss = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", gloss)
    parts = set()
    for part in re.split(r"[,;/.:]| or | ou ", gloss.lower()):
        part = re.sub(r"^(to|a|an|the|un|une|le|la|les|l'|se|s') ", "", part.strip())
        if part:
            parts.add(part.strip())
    return parts


# ---------------------------------------------------------------------------
# fetch / extract
# ---------------------------------------------------------------------------

def _api(params: dict[str, str]) -> dict:
    query = urllib.parse.urlencode({**params, "format": "json", "formatversion": "2", "maxlag": "5"})
    request = urllib.request.Request(f"https://en.wiktionary.org/w/api.php?{query}", headers={"User-Agent": USER_AGENT})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code not in (429, 503):
                raise
            time.sleep(min(int(error.headers.get("Retry-After") or 0) or 10 * (attempt + 1), 60))
    raise RuntimeError("rate limited")


def fetch() -> None:
    WIKT_DIR.mkdir(parents=True, exist_ok=True)
    data = _api({"action": "query", "titles": "|".join(WIKT_LISTS.values()),
                 "prop": "revisions", "rvprop": "content|ids|timestamp", "rvslots": "main"})
    by_title = {page["title"]: page["revisions"][0] for page in data["query"]["pages"] if page.get("revisions")}
    for lect, title in WIKT_LISTS.items():
        revision = by_title[title]
        text = revision["slots"]["main"]["content"]
        cells: dict[str, list[str]] = {}
        for match in re.finditer(r'm\[(\d+)\]\s*=\s*\{(.*)\}\s*$', text, re.M):
            terms = re.findall(r'term\s*=\s*"([^"]*)"', match.group(2))
            if terms:
                cells[match.group(1)] = terms
        for match in re.finditer(r"\|wrd(\d{3})=(.*)", text):
            terms = re.findall(r"\{\{l\|[^|}]*\|([^|}]+)", match.group(2)) + re.findall(r"\[\[([^\]|]+)", match.group(2))
            if terms:
                cells[str(int(match.group(1)))] = terms
        out = {"lect": lect, "title": title, "revid": revision["revid"], "timestamp": revision["timestamp"], "cells": cells}
        (WIKT_DIR / f"{lect}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{lect}: {len(cells)} cells from {title} (rev {revision['revid']})")


def extract(dump: Path) -> None:
    wanted = {"pcd", "frp", "gallo"}
    out: dict[str, dict[str, list[list[str]]]] = {code: {} for code in wanted}
    section = re.compile(r"==\s*\{\{langue\|([^}|]+)\}\}\s*==")
    title = lang = pos = None
    with dump.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            if "<title>" in line:
                found = re.search(r"<title>(.*?)</title>", line)
                title, lang = (found.group(1) if found else None), None
                continue
            found = section.match(line.strip())
            if found:
                lang, pos = (found.group(1) if found.group(1) in wanted else None), None
            elif lang and line.startswith("==="):
                found = re.search(r"\{\{S\|([^|}]+)", line)
                pos = found.group(1) if found else pos
            elif lang and title and ":" not in title and re.match(r"#[^*:#]", line):
                out[lang].setdefault(title, []).append([pos or "", line[1:].strip()[:220]])
    FRWIKT.parent.mkdir(parents=True, exist_ok=True)
    FRWIKT.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print({code: len(entries) for code, entries in out.items()})


# ---------------------------------------------------------------------------
# audit
# ---------------------------------------------------------------------------

def wikt_cells(lect: str) -> dict[int, list[str]]:
    path = WIKT_DIR / f"{lect}.json"
    if not path.is_file():
        return {}
    cells = json.loads(path.read_text(encoding="utf-8"))["cells"]
    clean: dict[int, list[str]] = {}
    for index, terms in cells.items():
        terms = [nfc(re.sub(r"\s*\(.*?\)", "", term)) for term in terms]
        terms = [term for term in terms if term and "[" not in term and "…" not in term]
        if terms:
            clean[int(index)] = terms
    return clean


def dictionary(lect: str) -> list[tuple[str, set[str], set[str]]]:
    """(headword, gloss parts, parts of speech) for every glossed entry."""
    kind, _ = DICTIONARIES[lect]
    entries: list[tuple[str, set[str], set[str]]] = []
    if "words" in kind:
        data = json.loads((WORDS / f"{lect}_words.json").read_text(encoding="utf-8"))["entries"]
        for head, entry in data.items():
            parts = set().union(*(gloss_parts(g) for g in entry.get("glosses_en") or [""]))
            if parts:
                entries.append((nfc(head), parts, set(entry.get("pos") or [])))
    if "frwikt" in kind and FRWIKT.is_file():
        french_pos = {"nom": "noun", "verbe": "verb", "adjectif": "adj"}
        for head, senses in json.loads(FRWIKT.read_text(encoding="utf-8")).get(lect, {}).items():
            parts = set().union(*(gloss_parts(text) for _, text in senses))
            pos = {french_pos.get(p, p) for p, _ in senses}
            if parts:
                entries.append((nfc(head), parts, pos))
    if kind == "es-keyed":
        data = json.loads((WORDS / f"{lect}_words.json").read_text(encoding="utf-8"))["entries"]
        for spanish, entry in data.items():
            for form in entry.get("ext") or []:
                entries.append((nfc(form), {nfc(spanish)}, set()))
    return entries


def concept_keys(row: dict, gloss_lang: str) -> set[str]:
    cid = row["id"]
    if gloss_lang == "en":
        return set(EN_KEYS.get(cid, [RESERVED_TABLES["en"][cid].lower()]))
    word = nfc(row[gloss_lang])
    return {word, re.sub(r"^(se |s')", "", word)} - {""}


def audit_lect(lect: str, rows: list[dict]) -> list[dict]:
    listed = wikt_cells(lect)
    entries = dictionary(lect)
    _, gloss_lang = DICTIONARIES[lect]
    result = []
    for index, row in enumerate(rows, start=1):
        cid, grid = row["id"], nfc(row[lect])
        keys = concept_keys(row, gloss_lang)
        wanted_pos = POS_OF.get(row["pos"])
        from_list = listed.get(index, []) if index <= 207 else []
        from_dict = sorted({
            head for head, parts, pos in entries
            if parts & keys and (not wanted_pos or not pos or pos & wanted_pos)
        })
        attested = from_list + [head for head in from_dict if head not in from_list]
        usable = [form for form in from_list if " " not in form]
        same = next((form for form in attested if bare(form) == bare(grid)), None) if grid else None
        mode = MODES[lect]
        if not grid:
            status, form = ("filled", usable[0]) if usable and mode != "report" else ("empty", "")
        elif same:
            status, form = ("kept" if same == grid or mode == "report" else "respelled"), (grid if mode == "report" else same)
        elif mode == "report":
            status, form = "unconfirmed", grid
        elif usable:
            status, form = "replaced", usable[0]
        elif mode == "strict" or from_list:
            status, form = "emptied", ""
        else:
            status, form = "unconfirmed", grid
        source = "Swadesh list" if form in from_list else ("dictionary" if form in from_dict else "")
        result.append({"id": cid, "grid": grid, "form": form, "status": status, "source": source,
                       "attested": attested[:6]})
    return result


def audit(output: Path, columns_path: Path) -> None:
    rows = concepts()
    assert [row["id"] for row in rows] == list(IDS)
    columns: dict[str, dict[str, str]] = {}
    lines = [
        "# Grid sources",
        "",
        "Generated by `scripts/audit_grid_sources.py audit`. Do not edit by hand.",
        "",
        "A cell is **kept** if its form is attested for that concept: in the lect's Wiktionary "
        "Swadesh list, or as a dictionary headword glossed with the concept. **Respelled** = "
        "same word, spelled as the source spells it. **Replaced** = no source attests the "
        "grid's form and the Swadesh list has another. **Emptied** = no source attests the "
        "form and the list has none to offer (or only a phrase). **Unconfirmed** = no source "
        "attests the form and it was left as it is.",
        "",
        "Mode: *strict* empties every unconfirmed cell; *list* touches only cells the Swadesh "
        "list covers; *report* changes nothing, because no source on disk can check the column.",
        "",
        "| lect | mode | kept | respelled | replaced | emptied | unconfirmed | filled | empty | sources |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    detail: list[str] = []
    for lect in LECTS:
        cells = audit_lect(lect, rows)
        count = {status: sum(cell["status"] == status for cell in cells)
                 for status in ("kept", "respelled", "replaced", "emptied", "unconfirmed", "filled", "empty")}
        sources = ", ".join(filter(None, [
            f"Swadesh list ({len(wikt_cells(lect))} cells)" if wikt_cells(lect) else "",
            f"dictionary ({len(dictionary(lect))} glossed forms, {DICTIONARIES[lect][1]})",
        ]))
        lines.append(f"| {lect} | {MODES[lect]} | {count['kept']} | {count['respelled']} | {count['replaced']} "
                     f"| {count['emptied']} | {count['unconfirmed']} | {count['filled']} | {count['empty']} | {sources} |")
        if MODES[lect] != "report":
            columns[lect] = {cell["id"]: cell["form"] for cell in cells if cell["form"]}
        changed = [cell for cell in cells if cell["status"] in ("respelled", "replaced", "emptied", "filled")]
        if changed:
            detail += [f"## {lect}", "", "| concept | grid had | now | also in the Swadesh list or dictionary |",
                       "|---|---|---|---|"]
            detail += [
                f"| {cell['id']} | {cell['grid'] or '–'} | {cell['form'] or '–'} "
                f"| {', '.join(a for a in cell['attested'] if a != cell['form']) or '–'} |"
                for cell in changed
            ]
            detail.append("")
        unconfirmed = [f"{cell['id']} *{cell['grid']}*" for cell in cells if cell["status"] == "unconfirmed"]
        if unconfirmed:
            detail += [f"### {lect}: unconfirmed, left as they are", "", ", ".join(unconfirmed), ""]
    output.write_text("\n".join(lines + [""] + detail), encoding="utf-8")
    columns_path.parent.mkdir(parents=True, exist_ok=True)
    columns_path.write_text(json.dumps(columns, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(lines[9:]))
    print(f"Wrote {output} and {columns_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("fetch", "extract", "audit"))
    parser.add_argument("--dump", type=Path, default=ROOT / "xmls" / "frwiktionary-latest-pages-articles.xml")
    parser.add_argument("-o", "--output", type=Path, default=ROOT / "docs" / "eval" / "grid_sources.md")
    parser.add_argument("--columns", type=Path, default=ROOT / "data" / "sources" / "grid_columns.json")
    args = parser.parse_args()
    if args.command == "fetch":
        fetch()
    elif args.command == "extract":
        extract(args.dump)
    else:
        audit(args.output, args.columns)


if __name__ == "__main__":
    main()
