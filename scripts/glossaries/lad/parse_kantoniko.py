#!/usr/bin/env python3
"""Kantoniko Ladino dictionary (YAML word files) -> headword/gloss tables.

Source: raw/kantoniko-ladino-diksionaryo-data/words/*.yaml (CC BY-SA 4.0),
which grew out of the Diksionaryo de Ladinokomunita spreadsheet.

Each file is one word with one or more "versions". Kept as headwords: the
first version, and any later version that is not a plural and not the
feminine of a masculine first version (those are inflected forms, not
entries). Conjugation tables are ignored. One row per translation value in
English, Spanish, French and Portuguese (Turkish and Hebrew are left out).

The file's `orijen` field names where the word is used. Regional origins
(Estanbol, Izmir, Salonik, Sarayevo, Balkanes, Gresia) get their own file;
everything else (Jeneral, Ladinokomunita, Ladinadores, Aki Yerushalayim,
Torah-Tanah, Otros, NA) goes to kantoniko-jeneral.tsv.

    python3 parse_kantoniko.py
"""
from __future__ import annotations

import unicodedata
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
WORDS = HERE / "raw" / "kantoniko-ladino-diksionaryo-data" / "words"
LANGS = {"inglez": "en", "kasteyano": "es", "fransez": "fr", "portugez": "pt"}
POS = {"verb": "verb", "noun": "noun", "adjective": "adj", "adverb": "adv", "preposition": "prep",
       "pronoun": "pron", "artikolo": "other"}
REGIONAL = {"Estanbol": "estanbol", "Izmir": "izmir", "Salonik": "salonik", "Sarayevo": "sarayevo",
            "Balkanes": "balkanes", "Gresia": "gresia"}


def clean(text) -> str:
    return unicodedata.normalize("NFC", " ".join(str(text).split()))


def main() -> None:
    rows: dict[str, list[tuple[str, str, str, str]]] = {"jeneral": []}
    seen: set[tuple] = set()
    for path in sorted(WORDS.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        versions = data.get("versions") or []
        if not versions:
            continue
        pos = POS.get(str(data.get("grammar")), "")
        variety = REGIONAL.get(str(data.get("orijen")), "jeneral")
        first_gender = versions[0].get("gender")
        for index, version in enumerate(versions):
            if index and (version.get("number") == "plural"
                          or (version.get("gender") == "feminine" and first_gender == "masculine")):
                continue
            head = clean(version.get("ladino") or "")
            if not head:
                continue
            for field, lang in LANGS.items():
                values = (version.get("translations") or {}).get(field) or []
                for value in values if isinstance(values, list) else [values]:
                    gloss = clean(value)
                    key = (variety, head, gloss, lang, pos)
                    if gloss and key not in seen:
                        seen.add(key)
                        rows.setdefault(variety, []).append((head, gloss, lang, pos))
    for variety, found in sorted(rows.items()):
        name = f"kantoniko-{variety}.tsv"
        with (HERE / name).open("w", encoding="utf-8") as out:
            out.write("headword\tgloss\tgloss_lang\tpos\n")
            for row in found:
                out.write("\t".join(row) + "\n")
        print(f"{name}: {len(found)} rows, {len({r[0] for r in found})} headwords")


if __name__ == "__main__":
    main()
