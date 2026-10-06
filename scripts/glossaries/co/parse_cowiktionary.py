#!/usr/bin/env python3
"""Corsican Wiktionary dump -> headword/gloss tables.

Two kinds of evidence, both written by the co.wiktionary editors:

  direct   a Corsican entry ({{-co-}}) with a translation table
           (`:*{{it}}: [[osso]]`): headword = page title, gloss = each
           Italian/Spanish/French/English/Portuguese/Catalan/Latin translation.
  reverse  an Italian/Spanish/French/English/Latin/... entry whose definition
           line is nothing but links to Corsican words (`# [[granu]]`):
           headword = the Corsican word, gloss = the page title.

The headword line of a Corsican entry may tag it {{cism}} (cismuntincu,
northern) or {{pum}} (pumuntincu, southern); rows go to the file of their
headword's tag, or to "unmarked". Capitalised headwords (proper names) are left out. Latin etyma stated in the entry
("vene da u latinu "[[ossum]]"") go to cowiktionary-latin-etyma.tsv.

    python3 parse_cowiktionary.py
"""
from __future__ import annotations

import bz2
import html
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
DUMP = HERE / "raw" / "cowiktionary-latest-pages-articles.xml.bz2"
GLOSS_LANGS = ("it", "es", "fr", "en", "pt", "ca", "la")
POS = {"noun": "noun", "verb": "verb", "adj": "adj", "adverb": "adv", "adv": "adv", "pronoun": "pron",
       "prep": "prep", "conj": "conj", "num": "num", "phrase": "other", "art": "other", "interj": "other"}
SKIP_POS = {"name", "symbol", "acronym", "prov"}
NOT_SECTION = set(POS) | SKIP_POS | {"rel", "pron", "etym", "trans", "hyph", "lnstc", "src", "syn", "ref",
                                     "var", "example", "drv", "ant"}


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text.strip())


def pages():
    xml = bz2.open(DUMP, "rt", encoding="utf-8").read()
    for page in re.findall(r"<page>(.*?)</page>", xml, re.S):
        if re.search(r"<ns>(\d+)</ns>", page).group(1) != "0":
            continue
        title = html.unescape(re.search(r"<title>(.*?)</title>", page).group(1))
        text = re.search(r"<text[^>]*>(.*?)</text>", page, re.S)
        yield nfc(title), html.unescape(text.group(1)) if text else ""


def sections(text: str):
    """(language code, body) for each language section of a page."""
    marks = [m for m in re.finditer(r"\{\{-([a-z]{2,3}(?:-[a-z]{3})?)-\}\}", text) if m.group(1) not in NOT_SECTION]
    for i, mark in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        yield mark.group(1), text[mark.end():end]


def pos_blocks(body: str):
    """(pos, block) for each part-of-speech block of a language section."""
    marks = [m for m in re.finditer(r"\{\{-([a-z]+)-\}\}", body) if m.group(1) in POS or m.group(1) in SKIP_POS]
    for i, mark in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        if mark.group(1) in POS:
            yield POS[mark.group(1)], body[mark.end():end]


def links(text: str) -> list[str]:
    found = []
    for target, shown in re.findall(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]*))?\]\]", text):
        word = nfc(shown or target)
        if word and ":" not in target:
            found.append(word)
    return found


def main() -> None:
    variety: dict[str, str] = {}
    direct: list[tuple[str, str, str, str]] = []
    reverse: list[tuple[str, str, str, str]] = []
    etyma: list[tuple[str, str, str]] = []
    for title, text in pages():
        for lang, body in sections(text):
            if lang == "co":
                tag = re.search(r"'''[^\n]*\{\{(cism|pum)\}\}", body)
                if tag:
                    variety[title] = {"cism": "cismuntincu", "pum": "pumuntincu"}[tag.group(1)]
                for pos, block in pos_blocks(body):
                    for code, cell in re.findall(r"^:?\*\s*\{\{(\w+)\}\}\s*:(.*)$", block, re.M):
                        if code in GLOSS_LANGS:
                            for gloss in links(cell):
                                direct.append((title, gloss, code, pos))
                    etym = re.search(r"\{\{-etym-\}\}\s*\n([^\n]*)", block)
                    if etym and re.search(r"\blatinu\b", etym.group(1)):
                        tail = etym.group(1)[re.search(r"\blatinu\b", etym.group(1)).end():]
                        for etymon in re.findall(r'^\s*"\[\[([^\]|]+)\]\]"|\bo\s+"\[\[([^\]|]+)\]\]"', tail):
                            etyma.append((title, nfc(etymon[0] or etymon[1]), pos))
            elif lang in GLOSS_LANGS:
                for pos, block in pos_blocks(body):
                    for line in re.findall(r"^#(?![:*])(.*)$", block, re.M):
                        rest = re.sub(r"\[\[[^\]]*\]\]", "", line)
                        rest = re.sub(r"\([^)]*\)|\{\{[^}]*\}\}", "", rest)
                        if re.sub(r"[\s,;.]", "", rest):
                            continue  # a prose definition, not a list of Corsican equivalents
                        for head in links(re.sub(r"\([^)]*\)", "", line)):   # bracketed links are asides
                            reverse.append((head, title, lang, pos))

    out_rows: dict[str, list[tuple[str, str, str, str]]] = {"cismuntincu": [], "pumuntincu": [], "unmarked": []}
    seen: set[tuple] = set()
    for row in direct + reverse:
        if row[0][:1].isupper():
            continue  # proper names (Corsican writes common nouns and language names in lower case)
        if row not in seen:
            seen.add(row)
            out_rows[variety.get(row[0], "unmarked")].append(row)
    for name, rows in out_rows.items():
        with (HERE / f"cowiktionary-{name}.tsv").open("w", encoding="utf-8") as out:
            out.write("headword\tgloss\tgloss_lang\tpos\n")
            for row in rows:
                out.write("\t".join(row) + "\n")
        print(f"cowiktionary-{name}.tsv: {len(rows)} rows, {len({r[0] for r in rows})} headwords")
    with (HERE / "cowiktionary-latin-etyma.tsv").open("w", encoding="utf-8") as out:
        out.write("headword\tlatin_etymon\tvariety\tpos\n")
        for head, etymon, pos in dict.fromkeys(etyma):
            out.write(f"{head}\t{etymon}\t{variety.get(head, '')}\t{pos}\n")
    print(f"cowiktionary-latin-etyma.tsv: {len(set(etyma))} rows")
    print(f"direct rows {len(set(direct))}, reverse rows {len(set(reverse))}")


if __name__ == "__main__":
    main()
