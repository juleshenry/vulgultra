#!/usr/bin/env python3
"""Read the lects' own Wiktionaries: each headword's translations and its Latin source.

The Lombard, Sicilian, Venetan, Aromanian, Aragonese, Occitan and Galician
Wiktionaries define their words in the lect itself, which no key reaches.
But an entry also lists translations (Lombard *cà*: Italian *casa*, English
*house*) and often names the Latin word it comes from. Those two are kept,
one row per headword, in `data/sources/native_wikt/{lect}.jsonl`:
`word`, `pos`, `latin` (the Latin words the etymology names) and `glosses`
(language → the translations given).

    python3 scripts/extract_native_wiktionaries.py            # every dump on disk
    python3 scripts/extract_native_wiktionaries.py lmo scn
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DUMPS = ROOT / "xmls"
OUT = ROOT / "data" / "sources" / "native_wikt"
# Lect → (name of its dump, the code its language sections carry).
NATIVE = {"lmo": ("lmo", "lmo"), "scn": ("scn", "scn"), "vec": ("vec", "vec"), "rup": ("roa_rup", "roa-rup"),
          "an": ("an", "an"), "oc": ("oc", "oc"), "gl": ("gl", "gl")}
GLOSS_LANGS = {"en", "fr", "es", "it", "pt", "ca", "ro", "de", "la"}
# The Lombard edition names a translation's language in Lombard.
NAMED = {"italian": "it", "ingles": "en", "frances": "fr", "spagnoeul": "es", "catalan": "ca", "latin": "la",
         "portoghes": "pt", "romen": "ro", "todesch": "de"}
# Section templates that look like a two-letter language code and are not one.
NOT_A_LANGUAGE = {"ex", "ap", "ab"}
SECTION = re.compile(r"\{\{[-=]([a-z-]{2,8})[-=]\}\}")
TEMPLATE = re.compile(r"\{\{(?:t[+-]?|trad[+-]{0,2}|trans|xlatio)\|\s*([a-z-]{2,8})\s*\|([^{}|]*)")
LINKED = re.compile(r"^[:*\s]*\{\{([a-zà-ÿ-]{2,12})\}\}\s*:\s*(.*)$")
LINK = re.compile(r"\[\[([^\]|#]+)")
LATIN = (
    re.compile(r"\{\{etimologia\|[a-z-]+\|la\|([^|}]+)"),
    re.compile(r"\{\{Etimolochía\|lat[ií]n\w*\|([^|}]+)"),
    re.compile(r"\{\{etil\|la\|[a-z-]+\}\}[^\[\n]{0,12}\[\[([^\]|#]+)"),
    re.compile(r"(?i)\blat[iì]n\w*[^\[\n]{0,25}\[\[([^\]|#]+)"),
)
POS = (("noun", r"\{\{-(?:noun|nom|sost|sust)"), ("verb", r"\{\{-verb"), ("adj", r"\{\{-(?:adj|agg)"),
       ("adv", r"\{\{-adv"), ("pron", r"\{\{-pron(?:oun|om)"), ("prep", r"\{\{-prep"), ("conj", r"\{\{-con[jg]"),
       ("num", r"\{\{-num"))


def is_language(code: str, native: str) -> bool:
    return code == native or len(code) == 2 and code not in NOT_A_LANGUAGE or code in {
        "ast", "nap", "grc", "ang", "fur", "lmo", "scn", "vec", "pms", "lij", "eml", "roa-rup", "roa-tara", "sdc"}


def plain_latin(word: str) -> str:
    decomposed = unicodedata.normalize("NFD", word.lower().strip(" *'\"."))
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def extract(lect: str) -> collections.Counter:
    dump_name, native = NATIVE[lect]
    dump = DUMPS / f"{dump_name}wiktionary-latest-pages-articles.xml"
    tally: collections.Counter = collections.Counter()
    OUT.mkdir(parents=True, exist_ok=True)
    title, inside, row = "", False, None

    def close(out) -> None:
        if row and (row["latin"] or row["glosses"]):
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            tally["entries"] += 1
            tally["with Latin"] += bool(row["latin"])
            for language in row["glosses"]:
                tally[language] += 1

    with dump.open(encoding="utf-8", errors="replace") as stream, (OUT / f"{lect}.jsonl").open("w", encoding="utf-8") as out:
        for line in stream:
            if "<title>" in line:
                close(out)
                match = re.search(r"<title>(.*?)</title>", line)
                title, inside, row = (match.group(1) if match else ""), False, None
                continue
            if not title or ":" in title:
                continue
            for code in SECTION.findall(line):
                if is_language(code, native):
                    inside = code == native
                    if inside and row is None:
                        row = {"word": unicodedata.normalize("NFC", title), "pos": "", "latin": [], "glosses": {}}
            if not inside or row is None:
                continue
            if not row["pos"]:
                row["pos"] = next((name for name, pattern in POS if re.search(pattern, line)), "")
            for pattern in LATIN:
                for word in pattern.findall(line):
                    word = plain_latin(word)
                    if word and " " not in word and word not in row["latin"]:
                        row["latin"].append(word)
            found = [(code, form) for code, form in TEMPLATE.findall(line)]
            match = LINKED.match(line)
            if match:
                found += [(NAMED.get(match.group(1), match.group(1)), form) for form in LINK.findall(match.group(2))]
            for code, form in found:
                form = unicodedata.normalize("NFC", form).strip(" '‎")
                if code in GLOSS_LANGS and form and len(form) < 40 and form not in row["glosses"].setdefault(code, []):
                    row["glosses"][code].append(form)
            row["glosses"] = {code: forms for code, forms in row["glosses"].items() if forms}
        close(out)
    return tally


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("lects", nargs="*", help=f"default: {' '.join(NATIVE)}")
    args = parser.parse_args()
    for lect in args.lects or NATIVE:
        print(lect, dict(extract(lect).most_common()), flush=True)


if __name__ == "__main__":
    main()
