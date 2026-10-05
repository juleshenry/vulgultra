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

Picard, Mirandese and Gallo have no list. Their columns were picked by hand
(docs/sources_grid.md) and are only verified here, cell by cell, in three
tiers: a glossed source (dictionary headword, or the lect's Wikipedia title
for the concept), a translated example sentence, or the lect's Wikipedia as
running text, where the meaning rests on the cognate.

  fetch    English Wiktionary Swadesh lists → data/sources/wikt_swadesh/
           Saenko 2015 (lexibank/saenkoromance, CC-BY-4.0) → data/sources/saenkoromance/
           IE-CoR (lexibank/iecor, CC-BY-4.0) → data/sources/iecor/
           Wikidata sitelinks, three Wikipedia dumps, the Chés Diseux word list
           → data/sources/{wikidata_sitelinks.json,wikipedia/,picard_diseux/mots/}
  extract  minority-lect entries of the local Wiktionary dumps (French,
           Spanish, Portuguese, Italian, Catalan), with their definitions
           → data/sources/wikt_sections.json
  audit    report in docs/eval/grid_sources.md, columns in
           data/sources/grid_columns.json
"""

from __future__ import annotations

import argparse
import bz2
import collections
import csv
import functools
import html
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

# Chés Diseux, "mes mots à mi": a 3,900-entry Picard–French word list of the
# Amiens area with translated examples (ches.diseux.free.fr/vrac/mots_0.htm).
DISEUX = SOURCES / "picard_diseux" / "mots"
DISEUX_URL = "http://ches.diseux.free.fr/vrac/"
# The lect's Wikipedia: its article title for a concept (Wikidata sitelinks),
# and its text as a corpus.
SITELINKS = SOURCES / "wikidata_sitelinks.json"
WIKIPEDIA = SOURCES / "wikipedia"
WIKI_OF = {"mwl": "mwlwiki", "pcd": "pcdwiki", "nrf": "nrmwiki", "wa": "wawiki"}
DUMP_URL = "https://dumps.wikimedia.org/{wiki}/latest/{wiki}-latest-pages-articles.xml.bz2"
# The Walloon Wiktionary, from its dump: headwords in the unified spelling
# with translations into French and English, and for half of them the
# standard pronunciation (prononçaedje zero-cnoxhou). Section name → the
# grid's part of speech.
WIKTIONARY = SOURCES / "wiktionary"
WA_DUMP = WIKTIONARY / "wawiktionary-latest-pages-articles.xml.bz2"
WA_ENTRIES = WIKTIONARY / "wa_entries.json"
WA_POS = {"sustantif": "noun", "Su": "noun", "viebe": "verb", "Vi": "verb", "VE": "verb",
          "addjectif": "adj", "Addj": "adj", "adviebe": "adv", "Adv": "adv", "prono": "pron", "Pro": "pron",
          "nombe": "num", "No": "num", "divancete": "prep", "Div": "prep", "aloyrece": "conj", "Alo": "conj"}

# A form the lect shares with its big sister needs this many corpus tokens;
# a form of its own needs one.
CORPUS_MIN = 3
# Concept → English Wikipedia article, for the sitelinks.
ARTICLES = {
    "woman": "Woman", "man": "Man", "person": "Person", "child": "Child", "wife": "Wife",
    "husband": "Husband", "mother": "Mother", "father": "Father", "animal": "Animal", "fish": "Fish",
    "bird": "Bird", "dog": "Dog", "louse": "Louse", "snake": "Snake", "worm": "Worm", "tree": "Tree",
    "forest": "Forest", "fruit": "Fruit", "seed": "Seed", "leaf": "Leaf", "root": "Root",
    "bark": "Bark (botany)", "flower": "Flower", "grass": "Poaceae", "rope": "Rope", "skin": "Skin",
    "meat": "Meat", "blood": "Blood", "bone": "Bone", "fat": "Fat", "egg": "Egg",
    "horn": "Horn (anatomy)", "tail": "Tail", "feather": "Feather", "hair": "Hair", "head": "Head",
    "ear": "Ear", "eye": "Eye", "nose": "Nose", "mouth": "Mouth", "tooth": "Tooth", "tongue": "Tongue",
    "fingernail": "Nail (anatomy)", "foot": "Foot", "leg": "Leg", "knee": "Knee", "hand": "Hand",
    "wing": "Wing", "belly": "Abdomen", "guts": "Gastrointestinal tract", "neck": "Neck",
    "back": "Human back", "breast": "Breast", "heart": "Heart", "liver": "Liver", "sun": "Sun",
    "moon": "Moon", "star": "Star", "water": "Water", "rain": "Rain", "river": "River", "lake": "Lake",
    "sea": "Sea", "salt": "Salt", "stone": "Rock (geology)", "sand": "Sand", "dust": "Dust",
    "earth": "Earth", "cloud": "Cloud", "fog": "Fog", "sky": "Sky", "wind": "Wind", "snow": "Snow",
    "ice": "Ice", "smoke": "Smoke", "fire": "Fire", "ash": "Ash", "road": "Road",
    "mountain": "Mountain", "red": "Red", "green": "Green", "yellow": "Yellow", "white": "White",
    "black": "Black", "night": "Night", "day": "Day", "year": "Year", "name": "Name", "cat": "Cat",
}

# strict: an unconfirmed cell with no list form is emptied (the column had
#         invented forms: Istriot dormar, vivar; Dalmatian flotar, fluir).
# list:   only cells a Swadesh list covers are touched; an empty cell a
#         list covers is filled.
# report: nothing changes (the default). Ladin stays here: its column is
#         Val Badia, and the lists are other valleys.
# picked: the column was picked by hand; nothing changes, each cell is
#         only verified, and reported with the sources that attest it.
MODES = {
    "ist": "strict", "dlm": "strict",
    "pms": "list", "lij": "list", "eml": "list", "ruo": "list", "frp": "list",
    "mwl": "picked", "pcd": "picked", "gallo": "picked", "wa": "picked",
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
# Words of the gloss language that count as the concept, beyond the grid's
# own word in that language (the grid's French for "stand" is tenir).
MORE_KEYS = {
    "fr": {
        "i": ["moi"], "you_sg": ["toi"], "he": ["lui"], "they": ["eux"], "this": ["celui-ci", "ce"],
        "that": ["ça"], "not": ["pas", "ne pas"], "all": ["tous"], "some": ["quelque"],
        "big": ["gros"], "heavy": ["pesant"], "thin": ["maigre", "fin"], "person": ["individu", "gens"],
        "wife": ["femme"], "husband": ["époux"], "animal": ["bête"], "snake": ["couleuvre"],
        "forest": ["bois"], "seed": ["semence"], "meat": ["chair"], "hair": ["cheveux"],
        "guts": ["boyau", "boyaux", "tripes", "intestin"], "breast": ["poitrine"],
        "suck": ["téter"], "hear": ["ouïr"], "smell": ["flairer"], "fight": ["se battre", "battre"],
        "hit": ["battre", "taper", "cogner", "heurter"], "scratch": ["griffer"], "dig": ["bêcher", "fouir"],
        "lie": ["coucher", "se coucher"], "sit": ["s'asseoir"], "stand": ["debout"], "fall": ["choir"],
        "squeeze": ["serrer"], "throw": ["lancer"], "tie": ["attacher", "nouer"], "swell": ["gonfler"],
        "river": ["fleuve"], "stone": ["caillou"], "fog": ["brume"], "ash": ["cendres"],
        "road": ["chemin"], "year": ["an"], "new": ["neuf"], "bad": ["méchant"], "dirty": ["crasseux"],
        "sharp": ["tranchant", "pointu", "coupant"], "wet": ["humide"], "correct": ["juste"],
        "near": ["proche", "près de"], "in": ["en"], "because": ["parce que", "car"], "many": ["beaucoup"],
        "eat": ["manger"], "wipe": ["essuyer"],
    },
    "pt": {
        "snake": ["cobra"], "fog": ["neblina"], "belly": ["barriga"], "hair": ["pelo"],
        "dirty": ["porco"], "wide": ["comprido"], "husband": ["homem"], "dust": ["poeira"],
    },
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
    fetch_wikipedia()
    fetch_diseux()


def fetch_wikipedia() -> None:
    """Sitelinks of the concepts' articles, and the three small Wikipedias."""
    by_title: dict[str, dict[str, str]] = {}
    titles = sorted(set(ARTICLES.values()))
    sites = "|".join(sorted(set(WIKI_OF.values())))
    for start in range(0, len(titles), 45):
        query = urllib.parse.urlencode({
            "action": "wbgetentities", "sites": "enwiki", "titles": "|".join(titles[start:start + 45]),
            "props": "sitelinks", "sitefilter": sites + "|enwiki", "format": "json", "maxlag": "5"})
        data = json.loads(_get(f"https://www.wikidata.org/w/api.php?{query}"))
        for qid, entity in data.get("entities", {}).items():
            links = {site: link["title"] for site, link in entity.get("sitelinks", {}).items()}
            if "enwiki" in links:
                by_title[links.pop("enwiki")] = {"qid": qid, **links}
        time.sleep(1.5)
    SITELINKS.write_text(json.dumps({cid: by_title.get(title) for cid, title in ARTICLES.items()},
                                    ensure_ascii=False, indent=1), encoding="utf-8")
    WIKIPEDIA.mkdir(parents=True, exist_ok=True)
    WIKTIONARY.mkdir(parents=True, exist_ok=True)
    targets = [WIKIPEDIA / f"{wiki}-latest-pages-articles.xml.bz2" for wiki in sorted(set(WIKI_OF.values()))]
    for target in [*targets, WA_DUMP]:
        if not target.is_file():
            target.write_bytes(_get(DUMP_URL.format(wiki=target.name.split("-")[0])))
            time.sleep(2)
    print(f"sitelinks: {SITELINKS}; dumps: {WIKIPEDIA}")


def fetch_diseux() -> None:
    """The word list is a chain of pages, each naming the next."""
    DISEUX.mkdir(parents=True, exist_ok=True)
    name = "mots_a.htm"
    while name.startswith("mots_"):
        target = DISEUX / name
        if not target.is_file():
            target.write_bytes(_get(DISEUX_URL + name))
            time.sleep(3)
        following = re.findall(r'navbas\([^)]*,"([^"]*)"\)', target.read_text(encoding="utf-8"))
        name = following[-1] if following else ""
    print(f"Chés Diseux: {DISEUX}")


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
def _diseux() -> tuple[list[Entry], list[tuple[str, str]]]:
    """Chés Diseux: headwords with a French gloss, and Picard examples with their French."""
    entries: list[Entry] = []
    pairs: list[tuple[str, str]] = []
    for path in sorted(DISEUX.glob("mots_*.htm")) if DISEUX.is_dir() else []:
        text = path.read_text(encoding="utf-8").replace("\u00ad", "")
        for found in re.finditer(r'<span class="cab">(.*?)</span><span class="nb">.*?</span>(.*?)<p class="v">', text, re.S):
            head = html.unescape(re.sub(r"<[^>]*>", "", found.group(1)))
            head = re.sub(r"\s*\([^)]*\)", "", head.strip().split("\n")[-1]).strip()  # a letter's heading precedes its first word
            body = html.unescape(found.group(2))
            for picard, french in re.findall(r"<i>(.*?)</i>\s*\(([^)]*)\)", body, re.S):
                pairs.append((re.sub(r"<[^>]*>", "", picard), french))
            gloss = re.sub(r"<i>.*?</i>\s*(\([^)]*\))?|<[^>]*>|\[[^\]]*\]", " ", body, flags=re.S)
            gloss = re.sub(r"^[^:]*:", "", gloss, count=1)  # the word class
            parts = gloss_parts(re.sub(r"\bmais aussi\b", ",", gloss))
            for index, form in enumerate(part.strip() for part in head.split(",")):
                # tchien, tchien.ne: a feminine after the comma; blanc, blanque. An ending alone is skipped.
                if form and parts and " " not in form and (index == 0 or len(form) > 3):
                    entries.append((nfc(form), parts, frozenset(), "fr"))
    return entries, pairs


@functools.cache
def wa_wiktionary() -> dict[str, dict]:
    """Headword → {"ipa": [...], "senses": [[pos, [French], [English]], ...]} from the Walloon Wiktionary."""
    if WA_ENTRIES.is_file():
        return json.loads(WA_ENTRIES.read_text(encoding="utf-8"))
    if not WA_DUMP.is_file():
        return {}
    entries: dict[str, dict] = {}
    with bz2.open(WA_DUMP, "rt", encoding="utf-8") as stream:
        pages = re.findall(r"<page>.*?</page>", stream.read(), flags=re.S)
    for page in pages:
        if "<ns>0</ns>" not in page or "{{L|wa}}" not in page:
            continue
        title = nfc(html.unescape(re.search(r"<title>(.*?)</title>", page).group(1)))
        body = html.unescape(re.search(r"<text[^>]*>(.*?)</text>", page, flags=re.S).group(1))
        section = re.search(r"==\s*\{\{L\|wa\}\}\s*==(.*?)(?=\n==\s*\{\{L\||\Z)", body, flags=re.S)
        if not section:
            continue
        ipa = [nfc(part) for line in section.group(1).split("\n") if "{{pzc}}" in line
               for group in re.findall(r"\{\{AFE\|([^}]*)\}\}", line)
               for part in group.split("|") if part and "=" not in part]
        senses: list[list] = []
        pos = ""
        for chunk in re.split(r"\n(?==+\s*\{\{H\|)", section.group(1)):
            header = re.match(r"=+\s*\{\{H\|([^|}]+)", chunk)
            name = header.group(1) if header else ""
            pos = WA_POS.get(name, pos)
            if name in ("ratournaedjes", "Ra"):
                found = {lang: re.findall(rf"\{{\{{t\+?\|{lang}\|([^|}}]+)", chunk) for lang in ("fr", "en")}
                for line in chunk.split("\n"):
                    row = re.match(r"\|\s*(fr|en)\s*=\s*(.*)", line)
                    if row:
                        found[row.group(1)] += re.findall(r"\[\[([^\]|#]+)", row.group(2))
            else:  # a French gloss under the definition: F. chienne.
                found = {"en": [], "fr": [
                    part.strip(" .") for gloss in re.findall(r"\{\{lang\|fr\|F\.\s*([^}]*)\}\}", chunk)
                    for part in re.split(r"[,;]", gloss) if part.strip(" .")]}
            if found["fr"] or found["en"]:
                senses.append([pos, sorted({nfc(word).lower() for word in found["fr"]}),
                               sorted({nfc(word).lower() for word in found["en"]})])
        entries[title] = {"ipa": ipa, "senses": senses}
    WA_ENTRIES.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")
    return entries


@functools.cache
def dictionaries(lect: str) -> tuple[tuple[str, tuple[Entry, ...]], ...]:
    """Every glossed entry on disk for the lect, by source."""
    found: list[tuple[str, list[Entry]]] = []
    words = WORDS / f"{lect}_words.json"
    if lect in ES_KEYED and words.is_file():
        found.append(("word list", [
            (nfc(form), frozenset({nfc(spanish)}), frozenset(), "es")
            for spanish, entry in json.loads(words.read_text(encoding="utf-8"))["entries"].items()
            for form in entry.get("ext") or []]))
    elif words.is_file():
        gloss_lang = "fr" if lect in FR_GLOSSED_WORDS else "en"
        entries = []
        for head, entry in json.loads(words.read_text(encoding="utf-8"))["entries"].items():
            parts = frozenset().union(*(gloss_parts(g) for g in entry.get("glosses_en") or [""]))
            if parts:
                entries.append((nfc(head), parts, frozenset(entry.get("pos") or []), gloss_lang))
        found.append(("fr.wiktionary" if gloss_lang == "fr" else "en.wiktionary", entries))
    if lect in APERTIUM:
        found.append(("Apertium", _apertium(lect)))
    if lect in OTHER_WIKTS and WIKT_SECTIONS.is_file():
        sections = _wikt_sections()
        for wiki, code in OTHER_WIKTS[lect]:
            entries = []
            for head, senses in sections.get(wiki, {}).get(code, {}).items():
                parts = frozenset().union(*(gloss_parts(text) for text in senses))
                if parts:
                    entries.append((nfc(head), parts, frozenset(), wiki))
            found.append((f"{wiki}.wiktionary", entries))
    if lect == "wa":
        found.append(("wa.wiktionary", [
            (head, frozenset(words), frozenset({pos} - {""}), lang)
            for head, entry in wa_wiktionary().items() for pos, french, english in entry["senses"]
            for lang, words in (("fr", french), ("en", english)) if words]))
    if lect == "frp":
        found.append(("Stich 2001", _stich_dictionary()))
    if lect == "gallo":
        found.append(("Ricaud", _canepin()))
    if lect == "pcd":
        found.append(("Chés Diseux", _diseux()[0]))
        found.append(("Tiot diqchionnaire", _chti()))
    merged: dict[str, list[Entry]] = {}
    for label, entries in found:
        merged.setdefault(label, []).extend(entries)
    return tuple((label, tuple(entries)) for label, entries in merged.items() if entries)


@functools.cache
def dictionary(lect: str) -> tuple[Entry, ...]:
    return tuple(entry for _, entries in dictionaries(lect) for entry in entries)


WORD = r"[^\W\d_]+(?:[-.][^\W\d_]+)*"


def words_of(text: str) -> set[str]:
    return set(re.findall(WORD, nfc(text).replace("’", "'")))


@functools.cache
def examples(lect: str) -> tuple[tuple[str, set[str], set[str]], ...]:
    """Sentences in the lect with a French translation: source, its words, the French words."""
    found: list[tuple[str, set[str], set[str]]] = []
    if lect == "pcd":
        found += [("Chés Diseux", words_of(picard), words_of(french)) for picard, french in _diseux()[1]]
    if lect == "gallo" and CANEPIN.is_file():
        for line in CANEPIN.read_text(encoding="utf-8").split("\n"):
            columns = re.split(r"\s{2,}", line.strip())
            if len(columns) == 2 and all(columns) and "Canepin de Galo" not in line:
                found.append(("Ricaud", words_of(columns[0]), words_of(columns[1])))
    return tuple(found)


@functools.cache
def sitelinks(lect: str) -> dict[str, str]:
    """Concept → the title of its article in the lect's Wikipedia."""
    wiki = WIKI_OF.get(lect)
    if not wiki or not SITELINKS.is_file():
        return {}
    links = json.loads(SITELINKS.read_text(encoding="utf-8"))
    # A title may carry a disambiguation: cawe (antomeye).
    return {cid: re.sub(r"\s*\(.*\)$", "", nfc(link[wiki])) for cid, link in links.items() if link and wiki in link}


@functools.cache
def corpus(lect: str) -> dict[str, int]:
    """How often each word occurs in the articles of the lect's Wikipedia."""
    wiki = WIKI_OF.get(lect)
    dump = WIKIPEDIA / f"{wiki}-latest-pages-articles.xml.bz2"
    counts_file = WIKIPEDIA / f"{wiki}_words.json"
    if not wiki or not dump.is_file():
        return {}
    if counts_file.is_file():
        return json.loads(counts_file.read_text(encoding="utf-8"))
    counts: collections.Counter[str] = collections.Counter()
    article = in_text = False
    with bz2.open(dump, "rt", encoding="utf-8", errors="replace") as stream:
        for line in stream:
            if "<ns>" in line:
                article = "<ns>0</ns>" in line
            in_text = in_text or "<text" in line
            if in_text and article:
                line = re.sub(r"<[^>]*>|\{\{[^{}]*\}\}|\[\[(?:[^\]|]*\|)?|\]\]|https?://\S+", " ", html.unescape(line))
                counts.update(re.findall(WORD, line.lower()))
            in_text = in_text and "</text>" not in line
    counts_file.write_text(json.dumps(counts, ensure_ascii=False), encoding="utf-8")
    return counts


def concept_keys(row: dict, gloss_lang: str) -> set[str]:
    cid = row["id"]
    if gloss_lang == "en":
        return set(EN_KEYS.get(cid, [RESERVED_TABLES["en"][cid].lower()]))
    word = nfc(row[gloss_lang])
    more = set(MORE_KEYS.get(gloss_lang, {}).get(cid, ()))
    return ({word, re.sub(r"^(se |s')", "", word), re.sub(r"se$", "", word)} | more) - {""}


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
        title = sitelinks(lect).get(cid)
        attested = from_list + [head for head in from_dict if head not in from_list]
        if title and title not in attested:
            attested.append(title)
        same = grid if grid in attested else next(
            (form for form in attested if spelling_key(lect, form) == spelling_key(lect, grid)), None)
        if not grid:
            status, form = ("filled", usable[0]) if usable and mode != "report" else ("empty", "")
        elif same and (mode != "picked" or same == grid):
            status, form = ("kept" if same == grid or mode == "report" else "respelled"), (grid if mode == "report" else same)
        elif mode == "report":
            status, form = "unconfirmed", grid
        elif mode == "picked":
            status, form = picked_status(lect, grid, keys["fr"], grid == nfc(row.get(SISTER.get(lect, ""), ""))), grid
        elif usable:
            status, form = "replaced", usable[0]
        elif mode == "strict":
            status, form = "emptied", ""
        else:
            status, form = "unconfirmed", grid
        evidence: list[str] = []
        if mode == "picked" and grid:
            evidence += [name for name, cells in lists(lect) if grid in cells.get(cid, [])]
            evidence += [label for label, entries in dictionaries(lect) if any(
                head == grid and parts & keys[lang] for head, parts, _, lang in entries)]
            evidence += ["Wikipedia title"] * (title == grid)
            evidence += sorted({f"example in {source}" for source, theirs, french in examples(lect)
                                if in_example(grid, keys["fr"], theirs, french)})
            if corpus(lect).get(grid):
                evidence.append(f"Wikipedia text ×{corpus(lect)[grid]}")
        result.append({"id": cid, "grid": grid, "form": form, "status": status, "attested": attested[:6],
                       "evidence": evidence,
                       "sister": bool(grid) and grid == nfc(row.get(SISTER.get(lect, ""), ""))})
    return result


def in_example(form: str, french_keys: set[str], theirs: set[str], french: set[str]) -> bool:
    """The form, or its plural, in a sentence whose French has the concept's word, or its plural."""
    return bool({form, form + "s", form + "x"} & theirs) and bool(
        french & (french_keys | {key + "s" for key in french_keys} | {key + "x" for key in french_keys}))


def picked_status(lect: str, form: str, french_keys: set[str], same_as_sister: bool) -> str:
    """A hand-picked form no glossed source has: a translated example, or running text."""
    if any(in_example(form, french_keys, theirs, french) for _, theirs, french in examples(lect)):
        return "example"
    if corpus(lect).get(form, 0) >= (CORPUS_MIN if same_as_sister else 1):
        return "corpus"
    return "unconfirmed"


def audit(output: Path, columns_path: Path) -> None:
    rows = concepts()
    assert [row["id"] for row in rows] == list(IDS)
    statuses = ("kept", "example", "corpus", "respelled", "replaced", "emptied", "unconfirmed", "filled", "empty")
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
        "A hand-picked column (mode *picked*) is only verified. Beyond **kept**, a cell may be "
        "attested by an **example**: the form stands in a sentence of the lect whose French "
        "translation has the concept's word; or by the **corpus**: the form occurs in the lect's "
        "Wikipedia, and its meaning rests on the cognate. A form identical to the big sister "
        f"lect's needs {CORPUS_MIN} corpus tokens, a form of the lect's own needs one.",
        "",
        "Mode: *strict* empties every unconfirmed cell; *list* touches only cells a Swadesh "
        "list covers; *report* changes nothing and only counts. **= sister** counts the "
        "unconfirmed cells that are letter for letter the form of the big lect next door "
        "(French for Gallo, Portuguese for Mirandese): the signature of padding. The sources "
        "column gives the number of cells or forms each source has for the lect.",
        "",
        "| lect | mode | kept | example | corpus | respelled | replaced | emptied | unconfirmed | = sister | filled | empty | sources |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    detail: list[str] = []
    for lect in [code for code in rows[0] if code not in ("id", "gloss_es", "pos")]:
        cells = audit_lect(lect, rows)
        count = {status: sum(cell["status"] == status for cell in cells) for status in statuses}
        mode = MODES.get(lect, "report")
        sources = [f"{name} ({len(found)})" for name, found in lists(lect)]
        if dictionary(lect):
            sources.append(f"dictionary ({len(dictionary(lect))} forms)")
        if sitelinks(lect):
            sources.append(f"Wikipedia titles ({len(sitelinks(lect))})")
        if examples(lect):
            sources.append(f"examples ({len(examples(lect))})")
        if corpus(lect):
            sources.append(f"Wikipedia text ({sum(corpus(lect).values()):,} words)")
        padded = sum(cell["status"] == "unconfirmed" and cell["sister"] for cell in cells)
        numbers = [count[status] for status in statuses[:7]] + [padded] + [count[status] for status in statuses[7:]]
        lines.append(f"| {lect} | {mode} | " + " | ".join(map(str, numbers)) + f" | {', '.join(sources) or 'none'} |")
        if mode == "picked":
            detail += [f"## {lect}: picked by hand, verified here", "",
                       "| concept | form | status | attested by |", "|---|---|---|---|"]
            detail += [f"| {cell['id']} | {cell['form']} | {cell['status']} | {', '.join(cell['evidence']) or '–'} |"
                       for cell in cells if cell["form"]]
            detail += ["", "Empty: " + ", ".join(cell["id"] for cell in cells if not cell["form"]) + ".", ""]
        elif mode != "report":
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
        unconfirmed = [] if mode == "picked" else [
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
    print("\n".join(line for line in lines if line.startswith("| ")))
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
