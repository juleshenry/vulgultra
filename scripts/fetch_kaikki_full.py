#!/usr/bin/env python3
"""Stream the Kaikki extracts of the big lects and keep every word class but verbs.

`data/words/kaikki-{code}.jsonl` holds verbs only for these lects (it feeds
the conjugation harvest and is left alone). The building blocks need the
rest: pronouns, determiners, numerals, prepositions, conjunctions, adverbs,
and nouns and adjectives with their plural and feminine forms. Each dump is
several hundred MB; only dictionary-form rows are kept, trimmed to the
fields the harvest reads, in `data/sources/kaikki_full/{code}.jsonl`.

    python3 scripts/fetch_kaikki_full.py            # every lect not yet on disk
    python3 scripts/fetch_kaikki_full.py es it      # these lects
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "sources" / "kaikki_full"
USER_AGENT = "vulgultra-research/0.1 (+noncommercial morphology corpus)"
LECTS = {"es": "Spanish", "pt": "Portuguese", "gl": "Galician", "ca": "Catalan", "fr": "French",
         "it": "Italian", "ro": "Romanian", "lmo": "Lombard"}
KEEP = {"pron", "det", "article", "num", "prep", "postp", "conj", "adv", "particle", "intj", "contraction",
        "noun", "adj"}
CLOSED = {"pron", "det", "article", "prep", "postp", "conj", "particle", "contraction", "num"}
# Inflected forms worth keeping for a noun or adjective.
FORM_TAGS = {"plural", "feminine", "masculine", "neuter"}


def url(name: str) -> str:
    return f"https://kaikki.org/dictionary/{name}/kaikki.org-dictionary-{name}.jsonl"


def trimmed(entry: dict) -> dict | None:
    """The entry's dictionary-form senses and the forms the harvest reads, or None."""
    # An object pronoun or an inflected article is entered as a form of its headword
    # (me: "accusative of yo"), so the closed classes keep those senses.
    closed = entry.get("pos") in CLOSED
    senses = [{"glosses": sense.get("glosses") or [], "tags": sense.get("tags") or []}
              for sense in entry.get("senses") or []
              if sense.get("glosses") and (closed or not sense.get("form_of") and not sense.get("alt_of"))]
    if not senses:
        return None
    forms = [{"form": form["form"], "tags": form.get("tags") or []} for form in entry.get("forms") or []
             if form.get("form") and FORM_TAGS & set(form.get("tags") or [])][:12]
    sounds = [sound["ipa"] for sound in entry.get("sounds") or [] if sound.get("ipa")][:2]
    heads = [{"args": head.get("args") or {}} for head in entry.get("head_templates") or []][:1]
    return {"word": entry["word"], "pos": entry["pos"], "senses": senses, "forms": forms,
            "head_templates": heads, "sounds": [{"ipa": ipa} for ipa in sounds]}


def fetch(code: str, name: str) -> tuple[int, int]:
    OUT.mkdir(parents=True, exist_ok=True)
    partial = OUT / f"{code}.jsonl.part"
    read = kept = 0
    request = urllib.request.Request(url(name), headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response, partial.open("w", encoding="utf-8") as out:
        for line in response:
            read += 1
            if b'"pos": "verb"' in line or b'"pos": "name"' in line:
                continue
            entry = json.loads(line)
            if entry.get("pos") not in KEEP or " " in entry.get("word", " "):
                continue
            row = trimmed(entry)
            if row:
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
                kept += 1
    partial.rename(OUT / f"{code}.jsonl")
    return read, kept


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("lects", nargs="*", help="lect codes; default: every lect not yet on disk")
    parser.add_argument("--force", action="store_true", help="fetch again what is already on disk")
    args = parser.parse_args()
    for code in args.lects or LECTS:
        target = OUT / f"{code}.jsonl"
        if target.is_file() and not args.force:
            print(f"{code}: on disk", flush=True)
            continue
        read, kept = fetch(code, LECTS[code])
        print(f"{code}: kept {kept} of {read} rows → {target}", flush=True)


if __name__ == "__main__":
    main()
