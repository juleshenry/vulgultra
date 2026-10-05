#!/usr/bin/env python3
"""Harvest the building-block words of each lect, and how its nouns form the plural.

Pronouns, numerals, prepositions, conjunctions, determiners and the small
adverbs come before any lexicon: every sentence needs them, and they are
picked by hand from what the daughters attest. This script gathers the
evidence for that pick from the Wiktionary extracts on disk
(`data/words/kaikki-{lect}.jsonl`, English glosses) and writes

    docs/building_blocks/{lect}.md          what one lect attests
    docs/eval/building_block_candidates.md  each meaning's shortest forms across lects
    docs/eval/plural_formation.md           plural patterns, lect by lect

A form is listed only where a dictionary entry of that lect glosses it with
the meaning. Nothing is filled in from a sister lect; a lect with no extract
on disk is named as missing.

    python3 scripts/build_building_blocks.py
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
from vulgultra.g2p import transcribe_and_repair  # noqa: E402
from vulgultra.phonology import count_syllables  # noqa: E402
from vulgultra.romance_swadesh import LECT_NAMES, SOURCE_LANGS  # noqa: E402

WORDS = ROOT / "data" / "words"
PAGES = ROOT / "docs" / "building_blocks"
SHORTLIST = ROOT / "docs" / "eval" / "building_block_candidates.md"
PLURALS = ROOT / "docs" / "eval" / "plural_formation.md"
# The extract of a lect, where its file is not named by the lect's code.
EXTRACT = {"eml": "egl"}
# Extracts glossed in French, which the English keys below cannot read yet.
FRENCH_GLOSSED = ("gallo",)

# class → (the parts of speech an entry of that class may carry, its meanings).
# A meaning is the English word a dictionary glosses the form with.
CLASSES: dict[str, tuple[frozenset[str], tuple[str, ...]]] = {
    "Personal pronouns": (frozenset({"pron", "det"}), (
        "I", "me", "you", "thou", "thee", "he", "him", "she", "her", "it", "we", "us", "they", "them",
        "oneself", "himself", "myself", "yourself")),
    "Possessives": (frozenset({"det", "pron", "adj"}), (
        "my", "mine", "your", "yours", "his", "its", "our", "ours", "their", "theirs")),
    "Articles and demonstratives": (frozenset({"det", "article", "pron", "adj"}), (
        "the", "a", "an", "this", "that", "these", "those")),
    "Interrogatives and relatives": (frozenset({"pron", "det", "adv", "conj"}), (
        "who", "whom", "what", "which", "whose", "where", "when", "how", "why", "how much", "how many")),
    "Quantifiers and indefinites": (frozenset({"det", "pron", "adj", "adv"}), (
        "all", "every", "each", "some", "any", "no", "none", "nobody", "no one", "nothing", "something",
        "someone", "somebody", "everything", "everyone", "many", "much", "few", "little", "more", "less",
        "other", "same", "both", "enough", "too much")),
    "Numerals": (frozenset({"num", "adj", "noun", "det"}), (
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven",
        "twelve", "twenty", "thirty", "forty", "fifty", "hundred", "thousand", "first", "second", "third",
        "half")),
    "Prepositions": (frozenset({"prep", "postp", "adv", "contraction"}), (
        "of", "to", "in", "into", "on", "at", "with", "without", "for", "from", "by", "between", "among",
        "under", "over", "above", "before", "after", "until", "against", "through", "towards", "toward",
        "near", "behind", "during", "about", "since", "inside", "outside")),
    "Conjunctions": (frozenset({"conj", "particle", "adv"}), (
        "and", "or", "but", "if", "because", "that", "while", "as", "than", "nor", "although", "so",
        "then", "therefore")),
    "Adverbs and particles": (frozenset({"adv", "particle", "intj"}), (
        "yes", "no", "not", "also", "too", "only", "very", "already", "still", "yet", "now", "here",
        "there", "never", "always", "again", "well", "today", "yesterday", "tomorrow", "perhaps",
        "maybe", "almost")),
}
# Forms of a noun that are a plain plural: nothing but number and gender.
PLAIN = {"plural", "masculine", "feminine", "neuter", "indefinite", "nominative", "accusative", "canonical"}
GENDERS = ("masculine", "feminine", "neuter")


def extract_of(lect: str) -> Path:
    return WORDS / f"kaikki-{EXTRACT.get(lect, lect)}.jsonl"


def entries(lect: str) -> list[dict]:
    path = extract_of(lect)
    if not path.is_file():
        return []
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def reading(form: str, lect: str, pos: str) -> tuple[str, int] | None:
    """The form's sounds and syllable count, or None if the reader rejects it."""
    try:
        _, seq = transcribe_and_repair(form, lect, pos)
    except Exception:
        return None
    return "".join(seq), count_syllables(seq)


def harvest(lect: str) -> dict[str, dict[str, list[tuple[str, str, str]]]]:
    """class → meaning → [(form, part of speech, the gloss as the dictionary gives it)]."""
    found: dict[str, dict[str, list[tuple[str, str, str]]]] = {name: {} for name in CLASSES}
    for entry in entries(lect):
        form, pos = audit.nfc(entry.get("word", "")), entry.get("pos", "")
        if not form or " " in form or form[:1].isupper() and form != "I":
            continue
        for sense in entry.get("senses") or []:
            if {"form-of", "alt-of", "misspelling", "obsolete"} & set(sense.get("tags") or []):
                continue
            for gloss in sense.get("glosses") or []:
                parts = audit.gloss_parts(gloss)
                for name, (allowed, meanings) in CLASSES.items():
                    if pos not in allowed:
                        continue
                    for meaning in meanings:
                        if meaning.lower() in parts:
                            rows = found[name].setdefault(meaning, [])
                            if not any(row[0] == form for row in rows):
                                rows.append((form, pos, gloss[:90]))
    return found


def plural_pattern(singular: str, plural: str) -> str:
    """What turns the singular into the plural: an ending added, an ending replaced, nothing."""
    if singular == plural:
        return "no change"
    shared = 0
    while shared < min(len(singular), len(plural)) and singular[shared] == plural[shared]:
        shared += 1
    dropped, added = singular[shared:], plural[shared:]
    if not dropped:
        return f"+{added}" if len(added) <= 3 else "other"
    if len(dropped) <= 2 and len(added) <= 3:
        return f"-{dropped} +{added}" if added else f"-{dropped}"
    return "other"


def plurals(lect: str) -> dict[str, collections.Counter]:
    """gender → pattern → count, with one stored example per pattern in EXAMPLES."""
    table: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for entry in entries(lect):
        if entry.get("pos") != "noun" or " " in entry.get("word", ""):
            continue
        tags = {tag for sense in entry.get("senses") or [] for tag in sense.get("tags") or []}
        tags |= {arg for head in entry.get("head_templates") or [] for arg in (head.get("args") or {}).values()
                 if isinstance(arg, str)}
        gender = next((g for g in GENDERS if g in tags or g[0] in tags or f"{g[0]}-p" in tags), "gender not given")
        plural = next((audit.nfc(form["form"]) for form in entry.get("forms") or []
                       if "plural" in (form.get("tags") or []) and set(form.get("tags") or []) <= PLAIN
                       and form.get("form") and " " not in form["form"]), None)
        if plural:
            singular = audit.nfc(entry["word"])
            pattern = plural_pattern(singular, plural)
            table[gender][pattern] += 1
            EXAMPLES.setdefault((lect, gender, pattern), f"{singular} → {plural}")
    return table


EXAMPLES: dict[tuple[str, str, str], str] = {}


def page(lect: str, found: dict, plural_table: dict) -> str:
    lines = [f"# {LECT_NAMES.get(lect, lect)} ({lect}): building blocks", "",
             "Generated by `scripts/build_building_blocks.py`. Do not edit by hand.", "",
             "Each form is a dictionary headword of this lect that the English Wiktionary glosses with the "
             "meaning. **Sounds** is the pipeline's reading of the spelling, **σ** its syllable count. "
             "An empty row means no entry on disk has that gloss, not that the lect lacks the word.", ""]
    for name, (_, meanings) in CLASSES.items():
        lines += [f"## {name}", "", "| meaning | form | sounds | σ | glossed as |", "|---|---|---|---:|---|"]
        for meaning in meanings:
            rows = found[name].get(meaning, [])
            if not rows:
                lines.append(f"| {meaning} | | | | |")
            for form, pos, gloss in rows:
                read = reading(form, lect, pos)
                sounds, sigma = read if read else ("not read", "")
                lines.append(f"| {meaning} | *{form}* | {sounds} | {sigma} | {gloss.replace('|', '/')} |")
        lines.append("")
    lines += ["## How nouns form the plural", ""]
    if not plural_table:
        lines += ["No noun on disk has a plural form recorded.", ""]
    for gender in (*GENDERS, "gender not given"):
        counts = plural_table.get(gender)
        if not counts:
            continue
        total = sum(counts.values())
        lines += [f"**{gender}** ({total} nouns)", "", "| singular → plural | nouns | share | example |", "|---|---:|---:|---|"]
        for pattern, n in counts.most_common(8):
            lines.append(f"| {pattern} | {n} | {100 * n // total}% | {EXAMPLES[(lect, gender, pattern)]} |")
        lines.append("")
    return "\n".join(lines)


def shortlist(all_found: dict[str, dict]) -> str:
    lines = ["# Building blocks: the shortest attested forms, meaning by meaning", "",
             "Generated by `scripts/build_building_blocks.py`. Do not edit by hand.", "",
             "For each meaning, every lect's forms are read and grouped by their sounds. A row is one sound "
             "shape, with the lects and spellings that attest it; rows are ordered by syllable count, then by "
             "the number of lects. Up to eight rows are shown. **Lects with a form** counts the lects whose "
             f"extract has the gloss at all, out of {len(all_found)} harvested. This is evidence for a pick "
             "by hand, not a pick.", ""]
    for name, (_, meanings) in CLASSES.items():
        lines += [f"## {name}", ""]
        for meaning in meanings:
            shapes: dict[tuple[int, str], list[str]] = collections.defaultdict(list)
            lects_with = 0
            for lect, found in all_found.items():
                rows = found[name].get(meaning, [])
                lects_with += bool(rows)
                for form, pos, _ in rows:
                    read = reading(form, lect, pos)
                    if read:
                        shapes[(read[1], read[0])].append(f"{lect} *{form}*")
            if not shapes:
                lines += [f"**{meaning}**: no form on disk.", ""]
                continue
            lines += [f"**{meaning}** (lects with a form: {lects_with})", "", "| σ | sounds | lects | attested as |",
                      "|---:|---|---:|---|"]
            ranked = sorted(shapes.items(), key=lambda item: (item[0][0], -len({a.split()[0] for a in item[1]}), item[0][1]))
            for (sigma, sounds), attested in ranked[:8]:
                lines.append(f"| {sigma} | {sounds} | {len({a.split()[0] for a in attested})} | {', '.join(attested[:8])} |")
            lines.append("")
    return "\n".join(lines)


def plural_overview(tables: dict[str, dict]) -> str:
    lines = ["# How the daughters form the plural of a noun", "",
             "Generated by `scripts/build_building_blocks.py`. Do not edit by hand.", "",
             "For every noun whose dictionary entry records a plural, the plural is compared with the singular "
             "spelling: an ending added (`+s`), an ending replaced (`-o +i`), no change, or something else "
             "(a stem change, a suppletive plural). The three commonest patterns per gender are shown with "
             "their share of that gender's nouns. Counts follow what Wiktionary's editors entered, so a small "
             "lect's shares are rough.", "",
             "| lect | gender | nouns | commonest | second | third |", "|---|---|---:|---|---|---|"]
    for lect, table in tables.items():
        for gender in (*GENDERS, "gender not given"):
            counts = table.get(gender)
            if not counts or sum(counts.values()) < 5:
                continue
            total = sum(counts.values())
            top = [f"{pattern} {100 * n // total}% ({EXAMPLES[(lect, gender, pattern)]})" for pattern, n in counts.most_common(3)]
            lines.append(f"| {lect} | {gender} | {total} | " + " | ".join(top + [""] * (3 - len(top))) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    PAGES.mkdir(parents=True, exist_ok=True)
    harvested: dict[str, dict] = {}
    plural_tables: dict[str, dict] = {}
    missing, french = [], []
    for lect in SOURCE_LANGS:
        rows = entries(lect)
        closed = [e for e in rows if e.get("pos") not in ("verb", None)]
        if lect in FRENCH_GLOSSED:
            french.append(lect)
        elif not closed:
            missing.append(lect)
        else:
            harvested[lect] = harvest(lect)
            plural_tables[lect] = plurals(lect)
            (PAGES / f"{lect}.md").write_text(page(lect, harvested[lect], plural_tables[lect]), encoding="utf-8")
    index = ["# Building blocks", "",
             "Generated by `scripts/build_building_blocks.py`. Do not edit by hand.", "",
             "Pronouns, possessives, articles, demonstratives, interrogatives, quantifiers, numerals, "
             "prepositions, conjunctions and the small adverbs, as each lect's dictionary entries attest "
             "them, and how its nouns form the plural. Cross-lect views: "
             "[shortest forms per meaning](../eval/building_block_candidates.md), "
             "[plural formation](../eval/plural_formation.md).", "",
             "| lect | meanings with a form | forms | nouns with a plural |", "|---|---:|---:|---:|"]
    wanted = sum(len(meanings) for _, meanings in CLASSES.values())
    for lect, found in harvested.items():
        filled = sum(1 for by_meaning in found.values() for rows in by_meaning.values() if rows)
        forms = sum(len(rows) for by_meaning in found.values() for rows in by_meaning.values())
        nouns = sum(sum(counts.values()) for counts in plural_tables[lect].values())
        index.append(f"| [{LECT_NAMES.get(lect, lect)}]({lect}.md) | {filled} of {wanted} | {forms} | {nouns} |")
    index += ["", f"**No page yet.** The extract on disk holds verbs only, or there is none: {', '.join(missing)}. "
              f"Glossed in French, which this harvest does not read yet: {', '.join(french)}.", ""]
    (PAGES / "README.md").write_text("\n".join(index), encoding="utf-8")
    SHORTLIST.write_text(shortlist(harvested), encoding="utf-8")
    PLURALS.write_text(plural_overview(plural_tables), encoding="utf-8")
    print("\n".join(index[6:]))
    print(f"Wrote {PAGES}/, {SHORTLIST.name}, {PLURALS.name}")


if __name__ == "__main__":
    main()
