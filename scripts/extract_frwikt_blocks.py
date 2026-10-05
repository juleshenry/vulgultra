#!/usr/bin/env python3
"""Pull the entries of the lects that have no English-glossed extract out of the French Wiktionary dump.

Picard, Franco-Provençal, Gascon, Extremaduran, Istro-Romanian and
Megleno-Romanian have entries in the French Wiktionary (`xmls/`), glossed in
French, under a part-of-speech header. One row per headword and part of
speech, shaped like a Kaikki row so the building-block harvest reads both,
in `data/sources/frwikt_blocks/{lect}.jsonl`. Gascon is the Occitan entries
labelled gascon.

    python3 scripts/extract_frwikt_blocks.py
"""

from __future__ import annotations

import collections
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DUMP = ROOT / "xmls" / "frwiktionary-latest-pages-articles.xml"
OUT = ROOT / "data" / "sources" / "frwikt_blocks"
LECTS = {"pcd": "pcd", "frp": "frp", "ext": "ext", "ruo": "ruo", "ruq": "ruq", "oc": "gsc"}  # the wiki's code → ours
POS = {
    "nom": "noun", "nom commun": "noun", "adjectif": "adj", "adverbe": "adv", "adverbe interrogatif": "adv",
    "pronom": "pron", "pronom personnel": "pron", "pronom démonstratif": "pron", "pronom indéfini": "pron",
    "pronom interrogatif": "pron", "pronom possessif": "pron", "pronom relatif": "pron",
    "adjectif possessif": "det", "adjectif démonstratif": "det", "adjectif indéfini": "det",
    "adjectif interrogatif": "det", "déterminant": "det", "adjectif numéral": "num", "numéral": "num",
    "article": "article", "article défini": "article", "article indéfini": "article",
    "article partitif": "article", "préposition": "prep", "conjonction": "conj",
    "conjonction de coordination": "conj", "particule": "particle", "interjection": "intj",
}
SECTION = re.compile(r"==\s*\{\{langue\|([^}|]+)\}\}\s*==")
HEADER = re.compile(r"===+\s*\{\{S\|([^|}]+)((?:\|[^}]*)?)\}\}")
GENDER = (("{{m}}", "masculine"), ("{{f}}", "feminine"), ("{{mf}}", "masculine"), ("{{n}}", "neuter"), ("{{p}}", "plural"))


def main() -> None:
    rows: dict[str, dict[tuple[str, str], dict]] = collections.defaultdict(dict)
    title = code = pos = None
    gascon = False
    with DUMP.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            if "<title>" in line:
                match = re.search(r"<title>(.*?)</title>", line)
                title, code, pos = (html.unescape(match.group(1)) if match else None), None, None
                continue
            match = SECTION.search(line)
            if match:
                code, pos = (match.group(1) if match.group(1) in LECTS else None), None
                continue
            if not code or not title or ":" in title or " " in title:
                continue
            match = HEADER.search(line)
            if match:
                pos = None if "flexion" in match.group(2) else POS.get(match.group(1).strip().lower())
                gascon = False
                continue
            if not pos:
                continue
            text = html.unescape(line).strip()
            gascon = gascon or "gascon" in text.lower()
            if text.startswith("'''"):
                tags = [tag for mark, tag in GENDER if mark in text]
                rows[code].setdefault((title, pos), {"tags": [], "glosses": [], "gascon": False})["tags"] += tags
            elif re.match(r"#(?![*:#])", text):
                row = rows[code].setdefault((title, pos), {"tags": [], "glosses": [], "gascon": False})
                row["glosses"].append(text.lstrip("# ")[:200])
                row["gascon"] = row["gascon"] or gascon
    OUT.mkdir(parents=True, exist_ok=True)
    for code, lect in LECTS.items():
        kept = 0
        with (OUT / f"{lect}.jsonl").open("w", encoding="utf-8") as out:
            for (word, part), row in rows[code].items():
                if row["glosses"] and (code != "oc" or row["gascon"]):
                    out.write(json.dumps({"word": word, "pos": part, "gloss_lang": "fr", "forms": [],
                                          "senses": [{"glosses": row["glosses"], "tags": sorted(set(row["tags"]))}]},
                                         ensure_ascii=False) + "\n")
                    kept += 1
        print(f"{lect}: {kept} entries", flush=True)


if __name__ == "__main__":
    main()
