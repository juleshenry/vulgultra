#!/usr/bin/env python3
"""Check a lect's grid column against sources that attest each form with its sense.

A cell is confirmed if its form is attested for that concept: in a Swadesh
list for the lect (English Wiktionary, Saenko 2015, IE-CoR, and for
Franco-Provençal Stich 2001), or as a dictionary headword glossed with the
concept. An unconfirmed cell takes a
list's form when a list has one. A dictionary only confirms; it never
supplies a form, because a gloss match cannot tell the everyday word from a
rare synonym.

What happens to an unconfirmed cell no list covers depends on the lect
(MODES): emptied where the column was fabricated, left alone otherwise.

  fetch    English Wiktionary Swadesh lists → data/sources/wikt_swadesh/
           Saenko 2015 (lexibank/saenkoromance, CC-BY-4.0) → data/sources/saenkoromance/
           IE-CoR (lexibank/iecor, CC-BY-4.0) → data/sources/iecor/
  extract  minority-lect entries of the local Wiktionary dumps (French,
           Spanish, Portuguese, Italian, Catalan), with their definitions
           → data/sources/wikt_sections.json
  audit    report in docs/eval/grid_sources.md, columns in
           data/sources/grid_columns.json
"""

from __future__ import annotations

import argparse
import csv
import functools
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

SOURCES = ROOT / "data" / "sources"
WIKT_DIR = SOURCES / "wikt_swadesh"
WORDS = ROOT / "data" / "words"
VENDOR = ROOT / "vendor"
USER_AGENT = "vulgultra-research/0.1 (+noncommercial; lexical grid sourcing)"
LEXIBANK = "https://raw.githubusercontent.com/lexibank/{repo}/master/cldf/{name}"

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
# Lect → the doculects a CLDF list has for it, the one nearest the column first.
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
IECOR = {
    "frp": ["Franco-Provençal"], "lmo": ["Milanese"], "lld": ["Ladin"], "wa": ["Walloon"],
    "fur": ["Friulian"], "sc": ["Sardinian: Logudoro", "Sardinian: Nuoro"],
    "dlm": ["Dalmatian: Vegliote"], "ruq": ["Megleno-Romanian"], "fr": ["French"],
    "pt": ["Portuguese"], "it": ["Italian"], "es": ["Spanish"], "ca": ["Catalan"], "ro": ["Romanian"],
}
# A list's concept names that differ from the grid's ids.
SAENKO_IDS = {"ashes": "ash", "burntr": "burn", "clawnail": "fingernail", "fatn": "fat",
              "flyv": "fly", "thou": "you_sg", "walkgo": "walk"}
IECOR_IDS = {"chest": "breast", "nail": "fingernail", "fly_V": "fly", "hot": "warm"}
# Lists that confirm a cell but never fill one: a phonetic notation the grid
# cannot hold (Dalmatian), or a local spelling where the column is ORB.
CONFIRM_ONLY = {"dlm": {"Saenko", "IE-CoR"}, "frp": {"IE-CoR"}}

# Lect → vendored Apertium bilingual dictionary: (file, side the lect is on,
# language of the other side).
APERTIUM = {
    "gsc": ("apertium-oci-spa/apertium-oci-spa.oci-spa.dix", "l", "es"),
    "an": ("apertium-spa-arg/apertium-spa-arg.spa-arg.dix", "r", "es"),
    "ast": ("apertium-spa-ast/apertium-spa-ast.spa-ast.dix", "r", "es"),
}
# Occitan entries carry their variety; Gascon takes its own and the shared ones.
OCI_MONODIX = VENDOR / "apertium-oci" / "apertium-oci.oci.metadix"
# Lects whose own word list is glossed in French or keyed by Spanish headword.
FR_GLOSSED_WORDS = ("gallo",)
ES_KEYED = ("ext",)
# Entries for a lect in another language's Wiktionary, extracted from the
# local dumps: lect → (wiki, the code that wiki uses). The definitions are
# in the wiki's language.
WIKT_SECTIONS = SOURCES / "wikt_sections.json"
OTHER_WIKTS = {
    "pcd": [("fr", "pcd")], "frp": [("fr", "frp")], "gallo": [("fr", "gallo")],
    "nrf": [("fr", "normand")], "wa": [("fr", "wa")],
    "mwl": [("pt", "mwl"), ("es", "mwl"), ("fr", "mwl")], "lad": [("es", "lad"), ("fr", "lad")],
    "ext": [("es", "ext")], "an": [("es", "an"), ("fr", "an")], "ast": [("es", "ast"), ("fr", "ast")],
    "gl": [("pt", "gl"), ("es", "gl"), ("fr", "gl"), ("it", "gl"), ("ca", "gl")],
    "oc": [("fr", "oc"), ("ca", "oc"), ("es", "oc")],
    "sc": [("fr", "sc"), ("it", "sc"), ("it", "sro"), ("es", "sc")], "co": [("fr", "co"), ("it", "co")],
    "lmo": [("fr", "lmo"), ("it", "lmo")], "pms": [("fr", "pms"), ("it", "pms")],
    "lij": [("fr", "lij"), ("it", "lij")], "vec": [("fr", "vec"), ("it", "vec")],
    "scn": [("fr", "scn"), ("it", "scn")], "fur": [("fr", "fur"), ("it", "fur")],
    "rm": [("fr", "rm")], "lld": [("fr", "lld"), ("it", "lld")], "rup": [("fr", "rup")],
}
# How each wiki opens a language section, and how it starts a definition.
WIKI_SECTION = {
    "fr": r"==\s*\{\{langue\|([^}|]+)\}\}\s*==",
    "es": r"==\s*\{\{lengua\|([^}|]+)\}\}\s*==",
    "pt": r"=\s*\{\{-([a-z-]{2,12})-\}\}\s*=",
    "it": r"==\s*\{\{-([a-z-]{2,12})-\}\}\s*==",
    "ca": r"==\s*\{\{-([a-z-]{2,12})-\}\}\s*==",
}
WIKI_DEFINITION = {wiki: r"#(?![*:#])\s*(.*)" for wiki in WIKI_SECTION} | {"es": r";\s*\d+[^:]*:\s*(.*)"}

# Stich 2001, the thesis that defines the ORB spelling of Franco-Provençal
# (text of the PDF from arpitania.eu, via pdftotext -layout). It holds a
# Swadesh list in ORB with English glosses, and an ORB–French dictionary.
STICH = SOURCES / "pdf" / "stich_2001_these_francoprovencal.txt"
# The list's English glosses that are not the grid's own English word.
STICH_IDS = {"ashes": "ash", "thou": "you_sg", "ye": "you_pl", "woods": "forest", "human being": "person",
             "moutain": "mountain"}  # the thesis's own typo

# Two dictionaries fetched as PDFs and read as text (pdftotext; the Gallo
# one with -layout, for its two columns).
CANEPIN = SOURCES / "pdf" / "ricaud_mon_canepin_de_galo.txt"      # Gallo, by theme
CHTI = SOURCES / "pdf" / "tiot_diqchionnaire_chti.raw.txt"         # Picard of the Nord

# strict: an unconfirmed cell with no list form is emptied (the column had
#         invented forms: Istriot dormar, vivar; Dalmatian flotar, fluir).
# list:   only cells a Swadesh list covers are touched; an empty cell a
#         list covers is filled.
# report: nothing changes (the default). Ladin stays here: its column is
#         Val Badia, and the lists are other valleys.
MODES = {
    "ist": "strict", "dlm": "strict",
    "pms": "list", "lij": "list", "eml": "list", "ruo": "list", "frp": "list",
}

# The big lect a small one would be padded from. An unconfirmed cell that is
# letter for letter its sister's form is the signature of padding.
SISTER = {
    "ruo": "ro", "ruq": "ro", "rup": "ro", "ist": "it", "dlm": "it", "vec": "it", "co": "it", "scn": "it",
    "rgn": "it", "eml": "it", "lmo": "it", "pms": "it", "lij": "it", "fur": "it", "lld": "it", "rm": "it",
    "sc": "it", "ext": "es", "an": "es", "ast": "es", "lad": "es", "mwl": "pt", "gl": "pt", "gsc": "oc",
    "wa": "fr", "pcd": "fr", "nrf": "fr", "gallo": "fr", "frp": "fr",
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
POS_OF = {"noun": {"noun", "n"}, "verb": {"verb", "vblex", "vbser", "vbhaver", "vbmod"},
          "adj": {"adj", "adjective"}}
# Dictionary spellings that write the same Extremaduran word as the grid's
# Castilian-style spelling: ombri/hombri, quatru/cuatru, yerva/yerba, muger/mujel.
EXT_SPELLING = (("ç", "z"), ("ss", "s"), ("v", "b"), ("h", ""), ("qua", "cua"), ("quo", "cuo"),
                ("ge", "je"), ("gi", "ji"), ("x", "j"))

Entry = tuple[str, frozenset[str], frozenset[str], str]  # headword, gloss parts, pos, gloss language


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


def is_spelling(form: str) -> bool:
    """False for a phonetic notation: tie bars, non-syllabic marks, private-use glyphs."""
    return not any(ch in "̯͡" or unicodedata.category(ch) == "Co" for ch in form)


def gloss_parts(gloss: str) -> frozenset[str]:
    """The separate senses a dictionary gloss names, stripped to bare words."""
    gloss = re.sub(r"\{\{[^{}]*\}\}|\([^)]*\)|''+", " ", gloss)
    gloss = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", gloss)
    parts = set()
    for part in re.split(r"[,;/.:]| or | ou ", gloss.lower()):
        part = re.sub(r"^(to|a|an|the|un|une|le|la|les|l'|se|s') ", "", part.strip())
        if part:
            parts.add(part.strip())
    return frozenset(parts)


# ---------------------------------------------------------------------------
# fetch / extract
# ---------------------------------------------------------------------------

def _get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return response.read()
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
        query = urllib.parse.urlencode({
            "action": "query", "titles": "|".join(titles[start:start + 20]), "prop": "revisions",
            "rvprop": "content|ids|timestamp", "rvslots": "main",
            "format": "json", "formatversion": "2", "maxlag": "5"})
        data = json.loads(_get(f"https://en.wiktionary.org/w/api.php?{query}"))
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
    for repo in ("saenkoromance", "iecor"):
        (SOURCES / repo).mkdir(parents=True, exist_ok=True)
        for name in ("forms.csv", "languages.csv", "parameters.csv"):
            (SOURCES / repo / name).write_bytes(_get(LEXIBANK.format(repo=repo, name=name)))
        print(f"lexibank/{repo}: {SOURCES / repo}")


def extract(dumps: Path) -> None:
    wanted: dict[str, set[str]] = {}
    for pairs in OTHER_WIKTS.values():
        for wiki, code in pairs:
            wanted.setdefault(wiki, set()).add(code)
    out: dict[str, dict[str, dict[str, list[str]]]] = {}
    for wiki, codes in sorted(wanted.items()):
        dump = dumps / f"{wiki}wiktionary-latest-pages-articles.xml"
        if not dump.is_file():
            continue
        section, definition = re.compile(WIKI_SECTION[wiki]), re.compile(WIKI_DEFINITION[wiki])
        found: dict[str, dict[str, list[str]]] = {}
        title = lang = None
        with dump.open(encoding="utf-8", errors="replace") as stream:
            for line in stream:
                if "<title>" in line:
                    match = re.search(r"<title>(.*?)</title>", line)
                    title, lang = (match.group(1) if match else None), None
                    continue
                # A page's first section header sits on the same line as its <text> tag.
                match = section.search(line)
                if match:
                    lang = match.group(1) if match.group(1) in codes else None
                    continue
                match = definition.match(line) if lang and title and ":" not in title else None
                if match and match.group(1).strip():
                    found.setdefault(lang, {}).setdefault(title, []).append(match.group(1).strip()[:200])
        out[wiki] = found
        print(wiki, {code: len(entries) for code, entries in sorted(found.items())}, flush=True)
    WIKT_SECTIONS.parent.mkdir(parents=True, exist_ok=True)
    WIKT_SECTIONS.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# sources
# ---------------------------------------------------------------------------

def _add(cells: dict[str, list[str]], cid: str, form: str) -> None:
    if form and form not in cells.setdefault(cid, []):
        cells[cid].append(form)


def wikt_cells(lect: str) -> dict[str, list[str]]:
    path = WIKT_DIR / f"{lect}.json"
    cells: dict[str, list[str]] = {}
    if not path.is_file():
        return cells
    for index, terms in json.loads(path.read_text(encoding="utf-8"))["cells"].items():
        if int(index) > 207:
            continue
        terms = [re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", term) for term in terms]
        terms = [nfc(re.sub(r"\s*\(.*?\)", "", term)) for term in terms]
        for term in terms:
            if "[" in term or "…" in term:
                continue
            _add(cells, IDS[int(index) - 1], term)
            if term.startswith("a "):  # Eastern lists cite verbs with the particle: a mânca
                _add(cells, IDS[int(index) - 1], term[2:])
    return cells


@functools.cache
def _cldf(repo: str) -> tuple[list[dict[str, str]], dict[str, str], dict[str, str]]:
    folder = SOURCES / repo
    if not (folder / "forms.csv").is_file():
        return [], {}, {}

    def table(name: str) -> list[dict[str, str]]:
        with (folder / name).open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    languages = {row["ID"]: row["Name"] for row in table("languages.csv")}
    parameters = {row["ID"]: row["Name"] for row in table("parameters.csv")}
    return table("forms.csv"), languages, parameters


def saenko_cells(lect: str) -> dict[str, list[str]]:
    """The source spellings Saenko records in braces, nearest doculect first."""
    forms, _, parameters = _cldf("saenkoromance")
    cells: dict[str, list[str]] = {}
    for doculect in SAENKO.get(lect, ()):
        for row in forms:
            if row["Language_ID"] != doculect:
                continue
            name = parameters[row["Parameter_ID"]]
            for spelling in re.findall(r"[{]([^}]*)[}]", row["Value"]):
                # Two private-use glyphs of the source's font, identified from the
                # transcription beside them: a stress mark on ę, and non-syllabic i.
                spelling = spelling.replace("", "").replace("", "i")
                form = nfc(spelling).replace("ţ", "ț").replace("ş", "ș")
                if is_spelling(form):
                    _add(cells, SAENKO_IDS.get(name, name), form)
    return cells


def iecor_cells(lect: str) -> dict[str, list[str]]:
    forms, languages, parameters = _cldf("iecor")
    cells: dict[str, list[str]] = {}
    for variety in IECOR.get(lect, ()):
        for row in forms:
            if languages.get(row["Language_ID"]) != variety:
                continue
            name = parameters[row["Parameter_ID"]]
            form = nfc(row["Form"])
            if is_spelling(form):
                _add(cells, IECOR_IDS.get(name, name), form)
    return cells


@functools.cache
def _stich_lines() -> list[str]:
    return STICH.read_text(encoding="utf-8").split("\n") if STICH.is_file() else []


def stich_cells(lect: str) -> dict[str, list[str]]:
    """Stich's Swadesh list: ORB form, English gloss, French, Occitan, in columns."""
    cells: dict[str, list[str]] = {}
    lines = _stich_lines()
    if lect != "frp" or not lines:
        return cells
    start = next(i for i, line in enumerate(lines)
                 if re.match(r"\s*francoprovençal\s+anglais\s+français\s+occitan", line))
    end = next(i for i in range(start, len(lines)) if "de base à Swadesh pour étudier" in lines[i])
    by_english: dict[str, str] = {}
    for cid in IDS:
        by_english.setdefault(RESERVED_TABLES["en"][cid].lower(), cid)
    for line in lines[start + 1:end]:
        columns = re.split(r"\s{2,}", line.strip())
        if len(columns) < 3:
            continue
        english = columns[1].lower()
        head = re.sub(r"\s*\(.*", "", english).strip(" ?")
        cid = STICH_IDS.get(head) or by_english.get(head)
        if head == "right":
            cid = "correct" if "correct" in english else "right"
        if cid is None:
            continue
        for form in re.split(r",\s*|/", columns[0]):
            form = form.strip(" ?")
            if not is_spelling(form):
                continue
            # aou(i)r is two spellings; the fuller one first.
            _add(cells, cid, nfc(re.sub(r"[()]", "", form)))
            _add(cells, cid, nfc(re.sub(r"\([^)]*\)", "", form)))
    return cells


def _stich_dictionary() -> list[Entry]:
    """ORB headword or indented derivative, two spaces, French glosses, Latin etymon."""
    entries: list[Entry] = []
    lines = _stich_lines()
    start = next((i for i, line in enumerate(lines) if re.match(r"a\s{2,}à \(sert parfois", line)), None)
    if start is None:
        return entries
    for line in lines[start:]:
        found = re.match(r"\s*(\S[^\s]*(?: [mf]\.| pl\.)?)\s{2,}(\S.*)$", line)
        if not found:
            continue
        gloss = re.sub(r"\b[A-ZÀ-Ý*][A-ZÀ-Ý*-]{2,}\b", " ", found.group(2))  # Latin etyma are in capitals
        parts = gloss_parts(gloss)
        for head in re.split(r"/", re.sub(r" (?:[mf]\.|pl\.)$", "", found.group(1))):
            head = nfc(re.sub(r"[()]", "", head))
            if head and parts and is_spelling(head):
                entries.append((head, parts, frozenset(), "fr"))
    return entries


@functools.cache
def lists(lect: str) -> tuple[tuple[str, dict[str, list[str]]], ...]:
    found = (("Stich 2001", stich_cells(lect)), ("Wiktionary", wikt_cells(lect)),
             ("Saenko", saenko_cells(lect)), ("IE-CoR", iecor_cells(lect)))
    return tuple((name, cells) for name, cells in found if cells)


def _apertium(lect: str) -> list[Entry]:
    relative, side, gloss_lang = APERTIUM[lect]
    path = VENDOR / relative
    if not path.is_file():
        return []
    allowed = None
    if lect == "gsc" and OCI_MONODIX.is_file():
        allowed = set()
        for tag in re.findall(r"<e [^>]*>", OCI_MONODIX.read_text(encoding="utf-8")):
            lemma, alt = re.search(r'lm="([^"]*)"', tag), re.search(r'alt="([^"]*)"', tag)
            if lemma and (alt is None or alt.group(1) == "oci@gascon"):
                allowed.add(nfc(lemma.group(1)))

    def lemma_and_pos(side_xml: str) -> tuple[str, str]:
        tags = re.findall(r'<s n="([^"]*)"', side_xml)
        return nfc(re.sub(r"<b/>", " ", re.sub(r"<(?!b/)[^>]*>", "", side_xml))), (tags[0] if tags else "")

    entries: list[Entry] = []
    text = path.read_text(encoding="utf-8")
    pairs = re.findall(r"<p>\s*<l>(.*?)</l>\s*<r>(.*?)</r>\s*</p>", text, re.S)
    pairs += [(same, same) for same in re.findall(r"<i>(.*?)</i>", text, re.S)]
    for left, right in pairs:
        ours, theirs = (left, right) if side == "l" else (right, left)
        (head, pos), (gloss, _) = lemma_and_pos(ours), lemma_and_pos(theirs)
        if head and gloss and (allowed is None or head in allowed):
            entries.append((head, frozenset({gloss}), frozenset({pos}), gloss_lang))
    return entries


def _canepin() -> list[Entry]:
    """Ricaud, Mon canepin de galo: Gallo on the left, French on the right."""
    entries: list[Entry] = []
    if not CANEPIN.is_file():
        return entries
    article = r"^(?:un|ene|le|la|les|lez|du|des|de la|l['’]|d['’])\s*"
    for line in CANEPIN.read_text(encoding="utf-8").split("\n"):
        columns = re.split(r"\s{2,}", line.strip())
        if len(columns) != 2 or not all(columns):
            continue
        parts = gloss_parts(columns[1])
        for head in columns[0].split(","):
            head = re.sub(article, "", nfc(re.sub(r"\([^)]*\)", "", head)))
            if head and parts and " " not in head:
                entries.append((head, parts, frozenset(), "fr"))
    return entries


def _chti() -> list[Entry]:
    """Tiot diqchionnaire chti: headword [pronunciation] (class) : French."""
    entries: list[Entry] = []
    if not CHTI.is_file():
        return entries
    for line in CHTI.read_text(encoding="utf-8").split("\n"):
        found = re.match(r"(.+?)\s*(?:\[[^\]]*\])?\s*\(([^)]*)\)\s*:\s*(.+)$", line.strip())
        if found:
            head, parts = nfc(re.sub(r"\([^)]*\)", "", found.group(1))), gloss_parts(found.group(3))
            if head and parts and " " not in head:
                entries.append((head, parts, frozenset(), "fr"))
    return entries


@functools.cache
def _wikt_sections() -> dict:
    return json.loads(WIKT_SECTIONS.read_text(encoding="utf-8"))


@functools.cache
def dictionary(lect: str) -> tuple[Entry, ...]:
    """Every glossed entry on disk for the lect."""
    entries: list[Entry] = []
    words = WORDS / f"{lect}_words.json"
    if lect in ES_KEYED and words.is_file():
        for spanish, entry in json.loads(words.read_text(encoding="utf-8"))["entries"].items():
            entries += [(nfc(form), frozenset({nfc(spanish)}), frozenset(), "es") for form in entry.get("ext") or []]
    elif words.is_file():
        gloss_lang = "fr" if lect in FR_GLOSSED_WORDS else "en"
        for head, entry in json.loads(words.read_text(encoding="utf-8"))["entries"].items():
            parts = frozenset().union(*(gloss_parts(g) for g in entry.get("glosses_en") or [""]))
            if parts:
                entries.append((nfc(head), parts, frozenset(entry.get("pos") or []), gloss_lang))
    if lect in APERTIUM:
        entries += _apertium(lect)
    if lect in OTHER_WIKTS and WIKT_SECTIONS.is_file():
        sections = _wikt_sections()
        for wiki, code in OTHER_WIKTS[lect]:
            for head, senses in sections.get(wiki, {}).get(code, {}).items():
                parts = frozenset().union(*(gloss_parts(text) for text in senses))
                if parts:
                    entries.append((nfc(head), parts, frozenset(), wiki))
    if lect == "frp":
        entries += _stich_dictionary()
    if lect == "gallo":
        entries += _canepin()
    if lect == "pcd":
        entries += _chti()
    return tuple(entries)


def concept_keys(row: dict, gloss_lang: str) -> set[str]:
    cid = row["id"]
    if gloss_lang == "en":
        return set(EN_KEYS.get(cid, [RESERVED_TABLES["en"][cid].lower()]))
    word = nfc(row[gloss_lang])
    return {word, re.sub(r"^(se |s')", "", word), re.sub(r"se$", "", word)} - {""}


# ---------------------------------------------------------------------------
# audit
# ---------------------------------------------------------------------------

def audit_lect(lect: str, rows: list[dict]) -> list[dict]:
    mode = MODES.get(lect, "report")
    confirm_only = CONFIRM_ONLY.get(lect, set())
    result = []
    for row in rows:
        cid, grid = row["id"], nfc(row[lect])
        wanted_pos = POS_OF.get(row["pos"])
        keys = {lang: concept_keys(row, lang) for lang in ("en", "fr", "es", "pt", "it", "ca")}
        from_list: list[str] = []
        usable: list[str] = []
        for name, cells in lists(lect):
            for form in cells.get(cid, []):
                if form not in from_list:
                    from_list.append(form)
                    # A phrase or an elided clitic (s'empouegnér) is not a citation form.
                    if not re.search(r"[ '’]", form) and name not in confirm_only:
                        usable.append(form)
        from_dict = sorted({
            head for head, parts, pos, lang in dictionary(lect)
            if parts & keys[lang] and (not wanted_pos or not (pos - {""}) or pos & wanted_pos)
        })
        attested = from_list + [head for head in from_dict if head not in from_list]
        same = grid if grid in attested else next(
            (form for form in attested if spelling_key(lect, form) == spelling_key(lect, grid)), None)
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
        result.append({"id": cid, "grid": grid, "form": form, "status": status, "attested": attested[:6],
                       "sister": bool(grid) and grid == nfc(row.get(SISTER.get(lect, ""), ""))})
    return result


def audit(output: Path, columns_path: Path) -> None:
    rows = concepts()
    assert [row["id"] for row in rows] == list(IDS)
    statuses = ("kept", "respelled", "replaced", "emptied", "unconfirmed", "filled", "empty")
    columns: dict[str, dict[str, str]] = {}
    lines = [
        "# Grid sources",
        "",
        "Generated by `scripts/audit_grid_sources.py audit`. Do not edit by hand.",
        "",
        "A cell is **kept** if its form is attested for that concept: in a Swadesh list for the "
        "lect (English Wiktionary, Saenko 2015, IE-CoR), or as a dictionary headword glossed with "
        "the concept. **Respelled** = same word, spelled as the source spells it. **Replaced** = "
        "no source attests the grid's form and a list has another. **Emptied** = no source "
        "attests the form and no list has one to offer. **Unconfirmed** = no source attests the "
        "form and it was left as it is; that is a gap in the sources, not a known error.",
        "",
        "Mode: *strict* empties every unconfirmed cell; *list* touches only cells a Swadesh "
        "list covers; *report* changes nothing and only counts. **= sister** counts the "
        "unconfirmed cells that are letter for letter the form of the big lect next door "
        "(French for Gallo, Portuguese for Mirandese): the signature of padding. The sources "
        "column gives the number of cells or forms each source has for the lect.",
        "",
        "| lect | mode | kept | respelled | replaced | emptied | unconfirmed | = sister | filled | empty | sources |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    detail: list[str] = []
    for lect in [code for code in rows[0] if code not in ("id", "gloss_es", "pos")]:
        cells = audit_lect(lect, rows)
        count = {status: sum(cell["status"] == status for cell in cells) for status in statuses}
        mode = MODES.get(lect, "report")
        sources = [f"{name} ({len(found)})" for name, found in lists(lect)]
        if dictionary(lect):
            sources.append(f"dictionary ({len(dictionary(lect))} forms)")
        padded = sum(cell["status"] == "unconfirmed" and cell["sister"] for cell in cells)
        numbers = [count[status] for status in statuses[:5]] + [padded] + [count[status] for status in statuses[5:]]
        lines.append(f"| {lect} | {mode} | " + " | ".join(map(str, numbers)) + f" | {', '.join(sources) or 'none'} |")
        if mode != "report":
            columns[lect] = {cell["id"]: cell["form"] for cell in cells if cell["form"]}
        changed = [cell for cell in cells if cell["status"] in ("respelled", "replaced", "emptied", "filled")]
        if changed:
            detail += [f"## {lect}", "", "| concept | grid had | now | also in a list or dictionary |",
                       "|---|---|---|---|"]
            detail += [
                f"| {cell['id']} | {cell['grid'] or '–'} | {cell['form'] or '–'} "
                f"| {', '.join(a for a in cell['attested'] if a != cell['form']) or '–'} |"
                for cell in changed
            ]
            detail.append("")
        unconfirmed = [
            f"{cell['id']} *{cell['grid']}*" + ("=" if cell["sister"] else "")
            + (f" ({', '.join(cell['attested'])})" if cell["attested"] else "")
            for cell in cells if cell["status"] == "unconfirmed"
        ]
        if unconfirmed:
            detail += [f"### {lect}: unconfirmed, left as they are", "",
                       "`=` marks a form identical to the sister lect's. In brackets: what the lists "
                       "and dictionaries have for that concept, to pick from.", "", "; ".join(unconfirmed), ""]
    output.write_text("\n".join(lines + [""] + detail), encoding="utf-8")
    columns_path.parent.mkdir(parents=True, exist_ok=True)
    columns_path.write_text(json.dumps(columns, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(lines[16:]))
    print(f"Wrote {output} and {columns_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("fetch", "extract", "audit"))
    parser.add_argument("--dumps", type=Path, default=ROOT / "xmls", help="folder of Wiktionary dumps")
    parser.add_argument("-o", "--output", type=Path, default=ROOT / "docs" / "eval" / "grid_sources.md")
    parser.add_argument("--columns", type=Path, default=SOURCES / "grid_columns.json")
    args = parser.parse_args()
    if args.command == "fetch":
        fetch()
    elif args.command == "extract":
        extract(args.dumps)
    else:
        audit(args.output, args.columns)


if __name__ == "__main__":
    main()
