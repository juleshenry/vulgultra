#!/usr/bin/env python3
"""Check a lect's grid column against sources that attest each form with its sense.

A cell is confirmed if its form is attested for that concept: in a Swadesh
list for the lect (English Wiktionary's, or Saenko's 2015 annotated lists),
or as a dictionary headword glossed with the concept. An unconfirmed cell
takes a list's form when a list has one. A dictionary only confirms; it never
supplies a form, because a gloss match cannot tell the everyday word from a
rare synonym.

What happens to an unconfirmed cell the list does not cover depends on the
lect (MODES): emptied where the column is fabricated, left alone where it is
sound, and nothing at all is changed where no source can check the column.

  fetch    English Wiktionary Swadesh lists → data/sources/wikt_swadesh/
           Saenko 2015 (lexibank/saenkoromance, CC-BY-4.0) → data/sources/saenkoromance/
  extract  thin-lect entries of the local French Wiktionary dump
           → data/sources/frwikt_sections.json
  audit    report in docs/eval/grid_sources.md, columns in
           data/sources/grid_columns.json
"""

from __future__ import annotations

import argparse
import csv
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
SAENKO_DIR = ROOT / "data" / "sources" / "saenkoromance"
SAENKO_URL = "https://raw.githubusercontent.com/lexibank/saenkoromance/master/cldf/"
FRWIKT = ROOT / "data" / "sources" / "frwikt_sections.json"
WORDS = ROOT / "data" / "words"
USER_AGENT = "vulgultra-research/0.1 (+noncommercial; lexical grid sourcing)"

# Lect → where its Wiktionary Swadesh list lives. Gallo is left out on
# purpose: Appendix:Gallo Swadesh list is filled with Walloon words.
_MODULE = "Module:Swadesh/data/"
WIKT_LISTS = {
    **{lect: _MODULE + lect for lect in (
        "an", "ast", "ca", "es", "fr", "fur", "gl", "ist", "it", "lad", "lij", "lld", "lmo",
        "oc", "pms", "pt", "rgn", "rm", "ro", "rup", "scn", "vec")},
    "eml": _MODULE + "egl",
    "dlm": "Appendix:Dalmatian Swadesh list",
    "ruo": "Appendix:Istro-Romanian Swadesh list",
    "ruq": "Appendix:Megleno-Romanian Swadesh list",
}
# Lect → Saenko's doculects for it, the one nearest the column first.
SAENKO = {
    "ruo": ["istroromanian"], "ruq": ["meglenoromanian"], "rup": ["aromanian"], "ro": ["romanian"],
    "dlm": ["dalmatian"], "fur": ["friulian"], "lld": ["gardeneseladin", "fassanoladin"],
    "rm": ["rumantschgrischun", "sursilvanromansh", "surmiranromansh", "valladerromansh"],
    "pms": ["lanzotorinesepiemontese", "barbaniapiemontese", "carmagnolapiemontese", "vercellesepiemontese"],
    "rgn": ["ravennateromagnol"], "eml": ["carpigianoemiliano", "reggianoemiliano", "ferrareseemiliano"],
    "lij": ["genoeseligurian", "rapalloligurian", "stellaligurian"],
    "vec": ["venicevenetian", "primierovenetian", "bellunesevenetian"],
    "it": ["standarditalian", "grossetoitalian"], "sc": ["logudorese", "campidanese"],
    "scn": ["palermitansicilian", "messinesesicilian", "cataniansicilian", "southeasternsicilian"],
    "ca": ["centralcatalan", "northwesterncatalan", "valenciancatalan"],
    "es": ["castilianspanish"], "oc": ["provencaloccitan"],
}
# Saenko's concept names that differ from the grid's ids.
SAENKO_IDS = {"ashes": "ash", "burntr": "burn", "clawnail": "fingernail", "fatn": "fat",
              "flyv": "fly", "thou": "you_sg", "walkgo": "walk"}
# Lect → (dictionary, language its glosses are in). Default: the lect's own
# word list, English glosses.
DICTIONARIES = {
    "gallo": ("words+frwikt", "fr"), "pcd": ("frwikt", "fr"), "frp": ("frwikt", "fr"),
    "ext": ("es-keyed", "es"),
}

# strict: an unconfirmed cell with no list form is emptied (the column had
#         invented forms: Istriot dormar, vivar; Dalmatian flotar, fluir).
# list:   only cells a Swadesh list covers are touched; an empty cell a
#         list covers is filled.
# report: nothing changes (the default). Ladin stays here: its column is
#         Val Badia, and both lists are other valleys.
MODES = {
    "ist": "strict", "dlm": "strict",
    "pms": "list", "lij": "list", "eml": "list", "ruo": "list",
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
# Dictionary spellings that write the same Extremaduran word as the grid's
# Castilian-style spelling: ombri/hombri, quatru/cuatru, yerva/yerba, muger/mujel.
EXT_SPELLING = (("ç", "z"), ("ss", "s"), ("v", "b"), ("h", ""), ("qua", "cua"), ("quo", "cuo"),
                ("ge", "je"), ("gi", "ji"), ("x", "j"))


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text.strip().lower())


def bare(text: str) -> str:
    """Letters only, so a source's stress accents do not hide a match."""
    plain = "".join(ch for ch in unicodedata.normalize("NFD", text.lower()) if not unicodedata.combining(ch))
    return plain.replace("’", "'").strip()


def spelling_key(lect: str, form: str) -> str:
    """What two spellings of one word share: no accents, and for Extremaduran no convention."""
    key = bare(form)
    if lect == "ext":
        for written, same_as in EXT_SPELLING:
            key = key.replace(written, same_as)
        key = re.sub(r"l$", "r", key)
    return key


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
    by_title = {}
    titles = sorted(set(WIKT_LISTS.values()))
    for start in range(0, len(titles), 20):
        data = _api({"action": "query", "titles": "|".join(titles[start:start + 20]),
                     "prop": "revisions", "rvprop": "content|ids|timestamp", "rvslots": "main"})
        by_title.update({page["title"]: page["revisions"][0]
                         for page in data["query"]["pages"] if page.get("revisions")})
        time.sleep(1.5)
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
    SAENKO_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("forms.csv", "languages.csv", "parameters.csv", "sources.bib"):
        request = urllib.request.Request(SAENKO_URL + name, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=90) as response:
            (SAENKO_DIR / name).write_bytes(response.read())
    print(f"Saenko 2015: {SAENKO_DIR}")


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
        terms = [re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", term) for term in terms]
        terms = [nfc(re.sub(r"\s*\(.*?\)", "", term)) for term in terms]
        terms = [term for term in terms if term and "[" not in term and "…" not in term]
        # Eastern lists cite verbs with the infinitive particle: a mânca.
        terms += [term[2:] for term in terms if term.startswith("a ") and term[2:] not in terms]
        if terms:
            clean[int(index)] = terms
    return clean


_SAENKO_ROWS: list[dict[str, str]] = []


def saenko_cells(lect: str) -> dict[str, list[str]]:
    """Concept id → the source spellings Saenko records, nearest doculect first."""
    path = SAENKO_DIR / "forms.csv"
    if lect not in SAENKO or not path.is_file():
        return {}
    if not _SAENKO_ROWS:
        with path.open(encoding="utf-8", newline="") as stream:
            _SAENKO_ROWS.extend(csv.DictReader(stream))
    cells: dict[str, list[str]] = {}
    for doculect in SAENKO[lect]:
        for row in _SAENKO_ROWS:
            if row["Language_ID"] != doculect:
                continue
            name = row["Parameter_ID"].split("_", 1)[1]
            cid = SAENKO_IDS.get(name, name)
            for spelling in re.findall(r"[{]([^}]*)[}]", row["Value"]):
                # Two private-use glyphs of the source's font, identified from the
                # transcription beside them: a stress mark on ę, and non-syllabic i.
                spelling = spelling.replace("\uedc1", "").replace("\uee2d", "i")
                form = nfc(spelling).replace("ţ", "ț").replace("ş", "ș")
                # Bartoli's Dalmatian notation is a phonetic transcription, not a
                # spelling the grid can hold.
                if "͡" in form or any(unicodedata.category(ch) == "Co" for ch in form):
                    continue
                if form and form not in cells.setdefault(cid, []):
                    cells[cid].append(form)
    return cells


def dictionary(lect: str) -> list[tuple[str, set[str], set[str]]]:
    """(headword, gloss parts, parts of speech) for every glossed entry."""
    kind, _ = DICTIONARIES.get(lect, ("words", "en"))
    entries: list[tuple[str, set[str], set[str]]] = []
    if "words" in kind and (WORDS / f"{lect}_words.json").is_file():
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
    saenko = saenko_cells(lect)
    entries = dictionary(lect)
    _, gloss_lang = DICTIONARIES.get(lect, ("words", "en"))
    result = []
    for index, row in enumerate(rows, start=1):
        cid, grid = row["id"], nfc(row[lect])
        keys = concept_keys(row, gloss_lang)
        wanted_pos = POS_OF.get(row["pos"])
        from_list = listed.get(index, []) if index <= 207 else []
        from_list = from_list + [form for form in saenko.get(cid, []) if form not in from_list]
        from_dict = sorted({
            head for head, parts, pos in entries
            if parts & keys and (not wanted_pos or not pos or pos & wanted_pos)
        })
        attested = from_list + [head for head in from_dict if head not in from_list]
        usable = [form for form in from_list if " " not in form]
        same = grid if grid in attested else next(
            (form for form in attested if spelling_key(lect, form) == spelling_key(lect, grid)), None)
        same = same if grid else None
        mode = MODES.get(lect, "report")
        if not grid:
            status, form = ("filled", usable[0]) if usable and mode != "report" else ("empty", "")
        elif same:
            status, form = ("kept" if same == grid or mode == "report" else "respelled"), (grid if mode == "report" else same)
        elif mode == "report":
            status, form = "unconfirmed", grid
        elif usable:
            status, form = "replaced", usable[0]
        elif mode == "strict":
            status, form = "emptied", ""
        else:
            status, form = "unconfirmed", grid
        found = same or form
        source = "Swadesh list" if found in from_list else ("dictionary" if found in from_dict else "")
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
        "A cell is **kept** if its form is attested for that concept: in a Swadesh list for the "
        "lect (English Wiktionary's, or Saenko 2015), or as a dictionary headword glossed with "
        "the concept. **Respelled** = "
        "same word, spelled as the source spells it. **Replaced** = no source attests the "
        "grid's form and the Swadesh list has another. **Emptied** = no source attests the "
        "form and the list has none to offer (or only a phrase). **Unconfirmed** = no source "
        "attests the form and it was left as it is.",
        "",
        "Mode: *strict* empties every unconfirmed cell; *list* touches only cells a Swadesh "
        "list covers; *report* changes nothing and only counts. The sources column gives the "
        "number of cells or forms each source has for the lect.",
        "",
        "| lect | mode | kept | respelled | replaced | emptied | unconfirmed | filled | empty | sources |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    detail: list[str] = []
    for lect in [code for code in rows[0] if code not in ("id", "gloss_es", "pos")]:
        cells = audit_lect(lect, rows)
        count = {status: sum(cell["status"] == status for cell in cells)
                 for status in ("kept", "respelled", "replaced", "emptied", "unconfirmed", "filled", "empty")}
        mode = MODES.get(lect, "report")
        sources = ", ".join(filter(None, [
            f"Wiktionary list ({len(wikt_cells(lect))})" if wikt_cells(lect) else "",
            f"Saenko ({len(saenko_cells(lect))})" if saenko_cells(lect) else "",
            f"dictionary ({len(dictionary(lect))} forms)" if dictionary(lect) else "",
        ])) or "none"
        lines.append(f"| {lect} | {mode} | {count['kept']} | {count['respelled']} | {count['replaced']} "
                     f"| {count['emptied']} | {count['unconfirmed']} | {count['filled']} | {count['empty']} | {sources} |")
        if mode != "report":
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
