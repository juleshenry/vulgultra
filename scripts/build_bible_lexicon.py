#!/usr/bin/env python3
"""Turn the Latin Bible into a ranked word list, each word with its daughter forms.

Latin gives no forms to Vulgultra (daughters only). It gives the list: the
Vulgate's words, counted, are the vocabulary a Bible needs, and each Latin
word names a family of daughter words that Wiktionary records as its
reflexes. This script reads

    data/bible/texts/la.tsv                 scripts/fetch_bible_texts.py
    data/sources/kaikki_full/la.jsonl       scripts/fetch_latin_descendants.py
    data/sources/kaikki_full/la_forms.tsv

and writes `data/bible/lexicon/la_words.tsv` (every word: count, part of
speech, gloss, the lects with a reflex, the reflexes) and the report
`docs/eval/bible_lexicon.md`.

    python3 scripts/build_bible_lexicon.py
"""

from __future__ import annotations

import collections
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from vulgultra.g2p import transcribe_and_repair  # noqa: E402
from vulgultra.phonology import count_syllables  # noqa: E402
from vulgultra.romance_swadesh import SOURCE_LANGS  # noqa: E402

TEXT = ROOT / "data" / "bible" / "texts" / "la.tsv"
LATIN = ROOT / "data" / "sources" / "kaikki_full" / "la.jsonl"
FORMS = ROOT / "data" / "sources" / "kaikki_full" / "la_forms.tsv"
WORDS = ROOT / "data" / "bible" / "lexicon" / "la_words.tsv"
REPORT = ROOT / "docs" / "eval" / "bible_lexicon.md"
# Wiktionary's code for a lect, where it is not ours.
CODE = {"egl": "eml", "roa-gal": "gallo"}
SHOWN = 150       # rows of the main table
READ_TOP = 400    # words whose reflexes are read aloud for the shortest-form column
ENCLITICS = ("que", "ne", "ve")


def plain(text: str) -> str:
    """The Clementine spelling brought to the dictionary's: æ, œ, j, accents."""
    text = text.lower().replace("æ", "ae").replace("œ", "oe").replace("ǽ", "ae").replace("j", "i")
    return "".join(ch for ch in unicodedata.normalize("NFD", text) if not unicodedata.combining(ch))


def dictionary() -> dict[str, dict]:
    """Latin word → parts of speech, first gloss, and reflexes by lect."""
    words: dict[str, dict] = {}
    with LATIN.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            entry = words.setdefault(row["word"], {"pos": [], "gloss": "", "reflexes": collections.defaultdict(list)})
            if row["pos"] not in entry["pos"]:
                entry["pos"].append(row["pos"])
            entry["gloss"] = entry["gloss"] or (row["glosses"][0] if row["glosses"] else "")
            for code, form in row["descendants"]:
                lect = CODE.get(code, code)
                if lect in SOURCE_LANGS and form not in entry["reflexes"][lect]:
                    entry["reflexes"][lect].append(form)
    return words


def inflected() -> dict[str, set[str]]:
    forms: dict[str, set[str]] = collections.defaultdict(set)
    with FORMS.open(encoding="utf-8") as stream:
        for line in stream:
            fields = line.rstrip("\n").split("\t")
            if len(fields) >= 2 and fields[0] and fields[1]:
                forms[fields[0]].add(fields[1])
    return forms


def count_words(words: dict, forms: dict) -> tuple[collections.Counter, collections.Counter, int]:
    """Dictionary words counted over the text, the tokens no entry explains, and the token total."""
    tokens: collections.Counter[str] = collections.Counter()
    with TEXT.open(encoding="utf-8") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            tokens.update(re.findall(r"[^\W\d_]+", plain(row["text"])))

    def readings(token: str) -> set[str]:
        found = set(forms.get(token, ())) & set(words) | ({token} if token in words else set())
        if not found:
            for enclitic in ENCLITICS:
                if token.endswith(enclitic) and len(token) > len(enclitic) + 1:
                    found |= readings(token[: -len(enclitic)])
        return found

    counts: collections.Counter[str] = collections.Counter()
    open_tokens: dict[str, set[str]] = {}
    unknown: collections.Counter[str] = collections.Counter()
    for token, n in tokens.items():
        found = readings(token)
        if len(found) == 1:
            counts[next(iter(found))] += n
        elif found:
            open_tokens[token] = found
        else:
            unknown[token] = n
    for token, found in open_tokens.items():  # a form of two words goes to the commoner one
        counts[max(sorted(found), key=lambda word: counts[word])] += tokens[token]
    return counts, unknown, sum(tokens.values())


def shortest(word: str, entry: dict) -> str:
    """The reflex with the fewest syllables, as the pipeline reads it."""
    best: tuple[int, int, str] | None = None
    for lect, reflexes in entry["reflexes"].items():
        for form in reflexes:
            if " " in form:
                continue
            try:
                _, seq = transcribe_and_repair(form, lect, entry["pos"][0])
            except Exception:
                continue
            key = (count_syllables(seq), len(seq), f"{''.join(seq)} ({lect} *{form}*)")
            best = min(best, key) if best else key
    return f"{best[0]}σ {best[2]}" if best else ""


def main() -> None:
    words, forms = dictionary(), inflected()
    counts, unknown, total = count_words(words, forms)
    ranked = counts.most_common()
    explained = sum(counts.values())
    WORDS.parent.mkdir(parents=True, exist_ok=True)
    with WORDS.open("w", encoding="utf-8") as out:
        out.write("rank\tword\tcount\tpos\tgloss\tlects\treflexes\n")
        for rank, (word, n) in enumerate(ranked, 1):
            entry = words[word]
            reflexes = "; ".join(f"{lect}: {', '.join(found)}" for lect, found in entry["reflexes"].items())
            out.write(f"{rank}\t{word}\t{n}\t{','.join(entry['pos'])}\t{entry['gloss'][:80]}\t{len(entry['reflexes'])}\t{reflexes}\n")

    def share(top: int) -> str:
        return f"{100 * sum(n for _, n in ranked[:top]) / total:.0f}%"

    with_reflex = [word for word, _ in ranked if words[word]["reflexes"]]
    wide = [word for word in with_reflex if len(words[word]["reflexes"]) >= 10]
    by_pos = collections.Counter(words[word]["pos"][0] for word, _ in ranked)
    orphans = [(word, n) for word, n in ranked if not words[word]["reflexes"]][:60]
    lines = [
        "# The Bible's vocabulary, from the Latin text", "",
        "Generated by `scripts/build_bible_lexicon.py`. Do not edit by hand.", "",
        "The Clementine Vulgate is read word by word; each word is traced to its dictionary entry in the "
        "English Wiktionary's Latin (an inflected form through the entry that names its headword), and the "
        "entries are counted. Latin supplies the list and the count, never a form: the last two columns "
        "show which daughters have a reflex of the word and the shortest one. A reflex is whatever "
        "Wiktionary lists under the Latin entry, inherited or borrowed, and may have drifted in meaning; "
        "the modern Bibles are the check on that.", "",
        f"- Words in the text: {total:,}. Traced to a dictionary entry: {explained:,} ({100 * explained / total:.0f}%).",
        f"- Distinct dictionary words: {len(ranked):,}. With a reflex in at least one of the 36 lects: "
        f"{len(with_reflex):,}; in ten or more: {len(wide):,}.",
        f"- The 100 commonest words are {share(100)} of the text, the 500 commonest {share(500)}, "
        f"the 1,000 commonest {share(1000)}, the 2,000 commonest {share(2000)}.",
        "- By part of speech: " + ", ".join(f"{pos} {n:,}" for pos, n in by_pos.most_common(8)) + ".",
        "- A form that belongs to two words (*est* of *sum* and of *edo*) is counted for the commoner word.", "",
        f"## The {SHOWN} commonest words", "",
        "| rank | Latin | part of speech | count | gloss | lects with a reflex | shortest reflex |",
        "|---:|---|---|---:|---|---:|---|",
    ]
    for rank, (word, n) in enumerate(ranked[:SHOWN], 1):
        entry = words[word]
        lines.append(f"| {rank} | {word} | {', '.join(entry['pos'])} | {n:,} | {entry['gloss'][:60].replace('|', '/')} "
                     f"| {len(entry['reflexes'])} | {shortest(word, entry)} |")
    lines += ["", "## Common words no daughter continues", "",
              "The commonest words with no reflex listed in any of the 36 lects. The daughters say these "
              "another way, which the five modern Bibles will show verse by verse.", "",
              ", ".join(f"*{word}* ({n:,})" for word, n in orphans), "",
              "## Words of the text with no dictionary entry", "",
              "Mostly names. The commonest: " + ", ".join(f"{token} ({n:,})" for token, n in unknown.most_common(50)) + ".", ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[6:11]))
    print(f"Wrote {WORDS} and {REPORT}")


if __name__ == "__main__":
    main()
