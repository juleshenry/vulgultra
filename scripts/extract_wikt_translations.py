#!/usr/bin/env python3
"""Read the translation tables of the Wiktionary dumps on disk.

An entry of the French Wiktionary lists, sense by sense, the word's
translations: *maison*, "bâtiment d'habitation": Latin *domus*, Occitan
*ostal*, Walloon *måjhon*. A lect's form and a Latin word that stand in one
table translate the same sense, which ties the form to the Latin word
without either being glossed by the other. The same holds in every edition,
whatever language it is written in.

One pass over each dump in `xmls/` keeps the rows of the 30 lects that are
not anchors, and the Latin rows, as `data/sources/wikt_translations/{wiki}.tsv`
(`headword`, `table`, `code`, `form`); `table` numbers the tables of a page.

    python3 scripts/extract_wikt_translations.py            # every dump on disk
    python3 scripts/extract_wikt_translations.py it ca      # these editions
"""

from __future__ import annotations

import argparse
import collections
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DUMPS = ROOT / "xmls"
OUT = ROOT / "data" / "sources" / "wikt_translations"
WIKIS = ("fr", "es", "it", "pt", "ca", "ro", "gl", "oc")
# The codes the editions use for the lects (and for Latin), as the repo's codes.
CODES = {
    "la": "la", "lat": "la",
    "an": "an", "arg": "an", "ast": "ast", "co": "co", "cos": "co", "dlm": "dlm", "egl": "eml", "eml": "eml",
    "ext": "ext", "frp": "frp", "fur": "fur", "gl": "gl", "glg": "gl", "gsc": "gsc", "gallo": "gallo",
    "roa-gal": "gallo", "ist": "ist", "lad": "lad", "lij": "lij", "lld": "lld", "lmo": "lmo", "mwl": "mwl",
    "nrf": "nrf", "nrm": "nrf", "normand": "nrf", "roa-nor": "nrf", "oc": "oc", "oci": "oc", "pcd": "pcd",
    "pms": "pms", "rgn": "rgn", "rm": "rm", "roh": "rm", "ruo": "ruo", "rup": "rup", "roa-rup": "rup",
    "ruq": "ruq", "sc": "sc", "srd": "sc", "sro": "sc", "src": "sc", "scn": "scn", "vec": "vec",
    "wa": "wa", "wln": "wa",
}
TEMPLATE = re.compile(r"\{\{(?:trad[+-]{0,2}|t[+-]?|d|xlatio)\|\s*([a-z-]{2,12})\s*\|([^{}]*)\}\}")
# The Italian edition writes a language template, a colon, and links.
LINKED = re.compile(r"^:?\*+\s*\{\{([a-z-]{2,12})\}\}\s*:\s*(.*)$")
LINK = re.compile(r"\[\[([^\]|#]+)")
TABLE_START = re.compile(r"\{\{(?:trad-début|Trad1|tradini|inici|trad-sus|trad-top|\(|1\||-trad-\}\})|^==")
NUMBERED = re.compile(r"^([atd])(\d+)=(.*)$")


def forms_of(arguments: str) -> list[tuple[str, str]]:
    """(sense number or "", form) for each translation a template names."""
    positional, numbered, senses = [], {}, {}
    for argument in arguments.split("|"):
        argument = argument.strip()
        match = NUMBERED.match(argument)
        if match and match.group(1) in "td":
            numbered[match.group(2)] = match.group(3).strip()
        elif match:
            senses[match.group(2)] = match.group(3).strip()
        elif argument and "=" not in argument:
            positional.append(argument)
    if numbered:   # the Spanish edition: t1=, t2= with the senses in a1=, a2=
        return [(senses.get(n, senses.get("1", "")), form) for n, form in numbered.items()]
    return [("", positional[0])] if positional else []


def clean(form: str) -> str:
    form = unicodedata.normalize("NFC", re.sub(r"''+", "", form)).strip(" .,;:!?‎")
    return "" if not form or any(ch in form for ch in "[]{}<>=/") or len(form) > 40 else form


def extract(wiki: str) -> collections.Counter:
    dump = DUMPS / f"{wiki}wiktionary-latest-pages-articles.xml"
    kept: collections.Counter = collections.Counter()
    OUT.mkdir(parents=True, exist_ok=True)
    title, table = "", 0
    with dump.open(encoding="utf-8", errors="replace") as stream, (OUT / f"{wiki}.tsv").open("w", encoding="utf-8") as out:
        out.write("headword\ttable\tcode\tform\n")
        for line in stream:
            if "<title>" in line:
                match = re.search(r"<title>(.*?)</title>", line)
                title, table = (match.group(1) if match else ""), 0
                continue
            if not title or ":" in title or "{{" not in line and not line.startswith("=="):
                continue
            if TABLE_START.search(line):
                table += 1
            found: list[tuple[str, str, str]] = []
            for code, arguments in TEMPLATE.findall(line):
                if code in CODES:
                    found += [(CODES[code], sense, form) for sense, form in forms_of(arguments)]
            match = LINKED.match(line) if wiki == "it" else None
            if match and match.group(1) in CODES:
                found += [(CODES[match.group(1)], "", form) for form in LINK.findall(match.group(2))]
            for code, sense, form in found:
                form = clean(form)
                if form:
                    out.write(f"{title}\t{table}{'.' + sense if sense else ''}\t{code}\t{form}\n")
                    kept[code] += 1
    return kept


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("wikis", nargs="*", help=f"editions; default: {' '.join(WIKIS)}")
    args = parser.parse_args()
    for wiki in args.wikis or WIKIS:
        kept = extract(wiki)
        print(wiki, sum(kept.values()), dict(kept.most_common()), flush=True)


if __name__ == "__main__":
    main()
