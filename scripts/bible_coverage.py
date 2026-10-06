#!/usr/bin/env python3
"""What the 36 lects have, and lack, of the Bible's vocabulary, and the forms themselves.

For every word of the Latin Bible (`scripts/build_bible_lexicon.py`) a lect
has a form by one of three routes, strongest first:

    reflex     Wiktionary lists the form under the Latin word as its descendant
    etymology  an entry of the lect says it comes from that Latin word
    gloss      a dictionary entry of the lect is glossed with one of the Latin
               word's first senses; in a dictionary glossed in French, Spanish,
               Portuguese, Italian or Catalan, with that language's own reflex
               of the Latin word
    bridge     as gloss, but the French (Spanish, ...) word is itself only a
               gloss match for the Latin word: two steps, the weakest route

Dictionaries are everything `audit_grid_sources.dictionaries()` reads (the
Wiktionary extracts, Apertium, the other Wiktionaries' entries, Stich,
Ricaud, Chés Diseux, the Extremaduran dictionary, the Walloon Wiktionary)
plus the extracts of the building-block harvest. Writes the candidate forms
to `data/bible/lexicon/forms/{lect}.tsv` and the report
`docs/eval/bible_coverage.md`.

    python3 scripts/bible_coverage.py
"""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import audit_grid_sources as audit  # noqa: E402
import build_bible_lexicon as bible  # noqa: E402
import build_building_blocks as blocks  # noqa: E402
from vulgultra.romance_swadesh import LECT_NAMES, SOURCE_LANGS  # noqa: E402

REPORT = ROOT / "docs" / "eval" / "bible_coverage.md"
POOL = ROOT / "data" / "bible" / "lexicon" / "forms"
TOP = 1000
TARGET = 2000
LATIN_CODES = {"la", "la-vul", "la-lat", "la-med", "la-ecc", "la-cla", "LL.", "VL.", "ML."}
ETYMOLOGY = {"inh", "inh+", "bor", "bor+", "der", "der+", "lbor", "slbor", "uder", "inh-lite"}
ROUTES = ("reflex", "etymology", "gloss", "bridge")
# The lects other dictionaries are glossed in; read first, so their forms can serve as keys.
ANCHORS = ("fr", "es", "pt", "it", "ca")
BRIDGE_KEYS = 6   # at most this many forms of an anchor lect stand in for a Latin word


def extracts(lect: str) -> list[tuple[Path, str]]:
    """Every dictionary extract on disk for the lect, with the language of its glosses."""
    code = blocks.EXTRACT.get(lect, lect)
    found = [(blocks.FULL / f"{lect}.jsonl", "en"), (blocks.FRWIKT / f"{lect}.jsonl", "fr"),
             (blocks.WORDS / f"kaikki-{code}.jsonl", "fr" if lect in blocks.FRENCH_GLOSSED else "en")]
    return [(path, language) for path, language in found if path.is_file()]


def lect_evidence(lect: str, forms: dict, words: dict) -> tuple[dict[str, set[str]], dict[str, dict[str, set[str]]]]:
    """(Latin word → forms whose entry cites it, gloss language → sense → forms) for one lect."""
    cited: dict[str, set[str]] = collections.defaultdict(set)
    senses: dict[str, dict[str, set[str]]] = collections.defaultdict(lambda: collections.defaultdict(set))
    for path, language in extracts(lect):
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                entry = json.loads(line)
                head = audit.nfc(entry.get("word", ""))
                if not head or " " in head:
                    continue
                for template in entry.get("etymology_templates") or []:
                    args = template.get("args") or {}
                    if template.get("name") in ETYMOLOGY and args.get("2") in LATIN_CODES and args.get("3"):
                        latin = bible.plain(args["3"]).strip("*-")
                        for word in ({latin} & set(words)) or (forms.get(latin, set()) & set(words)):
                            cited[word].add(head)
                for sense in entry.get("senses") or []:
                    for gloss in sense.get("glosses") or []:
                        for part in audit.gloss_parts(gloss):
                            senses[language][part].add(head)
    for _, entries in audit.dictionaries(lect):
        for head, parts, _, language in entries:
            if " " not in head:
                for part in parts:
                    senses[language][part].add(head)
    return cited, senses


def main() -> None:
    words, forms = bible.dictionary(), bible.inflected()
    counts, _, _ = bible.count_words(words, forms)
    ranked = counts.most_common()
    explained = sum(counts.values())
    english = {word: {part for gloss in words[word]["glosses"][:2] for part in audit.gloss_parts(gloss)
                      if len(part.split()) <= 3} for word, _ in ranked}
    POOL.mkdir(parents=True, exist_ok=True)
    has: dict[str, dict[str, str]] = {}   # lect → Latin word → the strongest route that gives a form
    anchor_forms: dict[str, dict[str, set[str]]] = {}   # anchor lect → Latin word → its forms, lowercased
    for lect in (*ANCHORS, *(lect for lect in SOURCE_LANGS if lect not in ANCHORS)):
        cited, senses = lect_evidence(lect, forms, words)
        found: dict[str, str] = {}
        with (POOL / f"{lect}.tsv").open("w", encoding="utf-8") as out:
            out.write("rank\tlatin\troute\tform\n")
            for rank, (word, _) in enumerate(ranked, 1):
                reflexes = words[word]["reflexes"]
                by_route = {"reflex": set(reflexes.get(lect, ())), "etymology": cited.get(word, set()),
                            "gloss": set(), "bridge": set()}
                for language, index in senses.items():
                    keys = english[word] if language == "en" else {form.lower() for form in reflexes.get(language, ())}
                    for key in keys:
                        by_route["gloss"] |= index.get(key, set())
                    if language != "en" and lect not in ANCHORS:
                        for key in anchor_forms.get(language, {}).get(word, set()) - keys:
                            by_route["bridge"] |= index.get(key, set())
                if lect in ANCHORS:   # the anchor's own forms, strongest first, as keys for the others
                    own = [form.lower() for route in ROUTES[:3] for form in sorted(by_route[route])]
                    anchor_forms.setdefault(lect, {})[word] = set(list(dict.fromkeys(own))[:BRIDGE_KEYS])
                seen: set[str] = set()
                for route in ROUTES:
                    for form in sorted(by_route[route] - seen):
                        out.write(f"{rank}\t{word}\t{route}\t{form}\n")
                    seen |= by_route[route]
                    if by_route[route]:
                        found.setdefault(word, route)
        has[lect] = found
    lects_with = {word: sum(1 for lect in SOURCE_LANGS if word in has[lect]) for word, _ in ranked}
    top = [word for word, _ in ranked[:TOP]]
    reached = [lect for lect in SOURCE_LANGS if len(has[lect]) >= TARGET]
    lines = [
        "# What the lects have of the Bible's vocabulary", "",
        "Generated by `scripts/bible_coverage.py`. Do not edit by hand.", "",
        f"The Latin Bible has {len(ranked):,} distinct dictionary words "
        "([`bible_lexicon.md`](bible_lexicon.md)). A lect has a form for one of them by a **reflex** "
        "(Wiktionary lists the form under the Latin word), by **etymology** (an entry of the lect says it "
        "comes from that Latin word), or by **gloss** (a dictionary entry of the lect is glossed with one of "
        "the Latin word's first senses; in a dictionary glossed in French, Spanish, Portuguese, Italian or "
        "Catalan, with that language's reflex of the Latin word). A **bridge** is the same in two steps: "
        "the French or Spanish word in the gloss is itself only a gloss match for the Latin word. Each word "
        "is counted once, under the strongest route. **Share of the text** weighs each word by how often the Bible uses it. A gloss "
        "match is a candidate to check, not a confirmed translation. The forms are in "
        "`data/bible/lexicon/forms/{lect}.tsv`.", "",
        f"{len(reached)} of {len(SOURCE_LANGS)} lects have a form for {TARGET:,} words or more.", "",
        f"| lect | reflex | etymology | gloss | bridge | words with a form | of the {TOP:,} commonest | share of the text |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    order = sorted(SOURCE_LANGS, key=lambda lect: -len(has[lect]))
    for lect in order:
        found = has[lect]
        by = collections.Counter(found.values())
        text_share = 100 * sum(counts[word] for word in found) / explained
        mark = "" if len(found) >= TARGET else " ↓"
        lines.append(f"| {LECT_NAMES.get(lect, lect)} ({lect}) | {by['reflex']:,} | {by['etymology']:,} | {by['gloss']:,} | {by['bridge']:,} "
                     f"| {len(found):,}{mark} | {sum(1 for word in top if word in found)} | {text_share:.0f}% |")
    nowhere = [(word, n) for word, n in ranked if not lects_with[word]]
    thin = [(word, n) for word, n in ranked[:TOP] if 0 < lects_with[word] < 5]
    lines += [
        "", f"↓ marks a lect below {TARGET:,}.", "",
        "## What is missing", "",
        f"- **In no lect at all:** {len(nowhere):,} of the {len(ranked):,} words, "
        f"{100 * sum(n for _, n in nowhere) / explained:.0f}% of the text. "
        f"Among the {TOP:,} commonest: {sum(1 for word, _ in nowhere if word in set(top))}.",
        f"- **In fewer than five lects**, among the {TOP:,} commonest: {len(thin)}.",
        f"- **In thirty lects or more:** {sum(1 for word, _ in ranked if lects_with[word] >= 30):,} words; "
        f"in ten or more: {sum(1 for word, _ in ranked if lects_with[word] >= 10):,}.", "",
        "### The commonest words with a form in no lect", "",
        ", ".join(f"*{word}* ({n:,}; {words[word]['gloss'][:40]})" for word, n in nowhere[:80]), "",
        f"### Among the {TOP:,} commonest, in fewer than five lects", "",
        ", ".join(f"*{word}* ({words[word]['gloss'][:30]}; {lects_with[word]})" for word, _ in thin[:120]), "",
        f"### What each lect lacks among the {TOP:,} commonest", "",
        "| lect | missing | the commonest of them |", "|---|---:|---|",
    ]
    for lect in order:
        missing = [word for word in top if word not in has[lect]]
        lines.append(f"| {lect} | {len(missing)} | " + ", ".join(missing[:15]) + " |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[6:9] + lines[9:48]))


if __name__ == "__main__":
    main()
