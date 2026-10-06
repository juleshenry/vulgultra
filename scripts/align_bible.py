#!/usr/bin/env python3
"""Line the Bibles up with the Latin one, verse by verse, and read off each Latin word's counterpart.

Two uses of one aligner.

**The five modern Bibles** (French, Spanish, Portuguese, Italian, Romanian;
`data/bible/texts/`). Their words are brought to dictionary headwords with
the Wiktionary extracts, and each Latin word gets the headword that
Bible uses where the Vulgate has it: *numquid* has no reflex anywhere, and
the Bibles show how the daughters say it. Those words are the keys through
which the lects' dictionaries, glossed in French or Italian, are read
(`data/bible/lexicon/anchor_keys.tsv`), and the commonest are printed side
by side in `docs/eval/bible_anchor_words.md`.

**A lect's own Bible text** (`data/bible/lects/{lect}[-variety].tsv`,
usually one Gospel). Its words are left as written: the form that stands
where the Latin word stands is an attested form of the lect for that word
(`data/bible/lexicon/aligned/{lect}.tsv`).

The aligner is IBM Model 1 run both ways; a link is kept where each word is
the other's best partner in the verse. With one Gospel most words occur once
or twice, so for a lect the model also leans on resemblance: a word of the
verse that looks like the Latin word, like what the modern Bibles have for
it, or like a form a dictionary of the lect already gives.

    python3 scripts/align_bible.py anchors
    python3 scripts/align_bible.py lects            # every text on disk
    python3 scripts/align_bible.py lects fur lmo    # these lects
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import build_bible_lexicon as bible  # noqa: E402

TEXTS = ROOT / "data" / "bible" / "texts"
LECT_TEXTS = ROOT / "data" / "bible" / "lects"
FULL = ROOT / "data" / "sources" / "kaikki_full"
WORDS = ROOT / "data" / "words"
LEXICON = ROOT / "data" / "bible" / "lexicon"
KEYS = LEXICON / "anchor_keys.tsv"
ALIGNED = LEXICON / "aligned"
REPORT = ROOT / "docs" / "eval" / "bible_anchor_words.md"
SHOWN = 500
# The Romanian text's licence is not settled (docs/bible_sources.md): its words stay in data/.
PRINTED = {"fr": "French", "es": "Spanish", "pt": "Portuguese", "it": "Italian"}
POOL = LEXICON / "forms"
ANCHORS = ("fr", "es", "pt", "it", "ro")
SKIPPED_BOOKS = {"PSA"}   # the Vulgate numbers the Psalms one behind, and splits them differently
ITERATIONS = 6
TOKEN = re.compile(r"[^\W\d_]+")


def verses(path: Path) -> dict[tuple[str, str, str], str]:
    with path.open(encoding="utf-8") as stream:
        return {(row["book"], row["chapter"], row["verse"]): row["text"]
                for row in csv.DictReader(stream, delimiter="\t", quoting=csv.QUOTE_NONE)}


def tokens(text: str) -> list[str]:
    return TOKEN.findall(unicodedata.normalize("NFC", text).lower().replace("’", "'"))


def headwords(language: str, counted: collections.Counter) -> dict[str, str]:
    """Word of the Bible's text → its dictionary headword; a form of two headwords goes to the commoner."""
    table: dict[str, set[str]] = collections.defaultdict(set)
    listed = FULL / f"{language}_forms.tsv"   # scripts/fetch_kaikki_full.py --forms
    if listed.is_file():
        with listed.open(encoding="utf-8") as stream:
            for line in stream:
                form, _, head = unicodedata.normalize("NFC", line.rstrip("\n")).lower().partition("\t")
                if form in counted and head:
                    table[form].add(head)
    for path in (FULL / f"{language}.jsonl", WORDS / f"kaikki-{language}.jsonl"):
        if not path.is_file():
            continue
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                entry = json.loads(line)
                head = unicodedata.normalize("NFC", entry.get("word", "")).lower()
                if not head or " " in head:
                    continue
                table[head].add(head)
                for form in entry.get("forms") or []:
                    if {"table-tags", "inflection-template", "class"} & set(form.get("tags") or []):
                        continue
                    # Italian tables mark the stress (dièdi); the link under the form is the plain spelling.
                    spellings = [form.get("form", "")] + [link[1] for link in form.get("links") or [] if len(link) > 1]
                    for spelling in spellings:
                        spelling = unicodedata.normalize("NFC", spelling).lower()
                        if spelling and " " not in spelling and spelling != "-":
                            table[spelling].add(head)
    count: collections.Counter = collections.Counter()
    open_words = {}
    head_of: dict[str, str] = {}
    for word, n in counted.items():
        found = table.get(word, set())
        if len(found) == 1:
            head_of[word] = next(iter(found))
            count[head_of[word]] += n
        elif found:
            open_words[word] = found
        else:
            head_of[word] = word

    def shared(head: str, word: str) -> int:
        return next((i for i, (a, b) in enumerate(zip(head, word)) if a != b), min(len(head), len(word)))

    for word, found in open_words.items():
        # How common each candidate is: the words that can only be its forms, and its own spelling in the text.
        weight = {head: count[head] + counted.get(head, 0) for head in found}
        if word in found:
            # A word that is its own headword stays one (Spanish para, entre) unless the other headword
            # is commoner in its own right (dit goes to dire); hija does not go to hijo.
            other = max(sorted(found - {word}), key=lambda head: count[head])
            pair = len(other) == len(word) >= 4 and shared(other, word) >= len(word) - 1
            head_of[word] = other if count[other] >= counted[word] and not pair else word
        else:
            # Among candidates that are not rare, the one spelt most like the word (hijas: hija, not hijo).
            floor = 0.05 * max(weight.values())
            head_of[word] = max(sorted(found), key=lambda head: (shared(head, word) if weight[head] >= floor else -1, weight[head]))
    return head_of


def shape(word: str) -> frozenset[str]:
    """What two cognates share: the letter pairs of the word, accents off, with its edges marked."""
    bare = "".join(ch for ch in unicodedata.normalize("NFD", word.lower()) if not unicodedata.combining(ch))
    bare = f"^{bare}$"
    return frozenset(bare[i:i + 2] for i in range(len(bare) - 1))


def resemblance(left: frozenset[str], right: frozenset[str]) -> float:
    return 2 * len(left & right) / (len(left) + len(right)) if left and right else 0.0


class Aligner:
    """IBM Model 1 both ways over verse pairs of word ids, with an optional prior on word pairs."""

    def __init__(self, pairs: list[tuple[list[int], list[int]]], sources: int, targets: int) -> None:
        self.sources, self.targets = sources, targets
        source_of, target_of, source_slot, target_slot = [], [], [], []
        seen_sources = seen_targets = 0
        for source, target in pairs:
            left = np.repeat(np.arange(len(source), dtype=np.int32), len(target))
            right = np.tile(np.arange(len(target), dtype=np.int32), len(source))
            source_of.append(np.asarray(source, dtype=np.int64)[left])
            target_of.append(np.asarray(target, dtype=np.int64)[right])
            source_slot.append(seen_sources + left)
            target_slot.append(seen_targets + right)
            seen_sources += len(source)
            seen_targets += len(target)
        self.source_slot, self.target_slot = np.concatenate(source_slot), np.concatenate(target_slot)
        self.slots = (seen_sources, seen_targets)
        self.pair, self.row = np.unique(np.concatenate(source_of) * targets + np.concatenate(target_of), return_inverse=True)
        self.pair_source, self.pair_target = self.pair // targets, self.pair % targets

    def links(self, prior: np.ndarray | None = None) -> dict[tuple[int, int], int]:
        """(source id, target id) → the verses in which each is the other's best partner."""
        prior = np.ones(len(self.pair)) if prior is None else prior
        best = []
        for slot, slots, owner, owners in ((self.target_slot, self.slots[1], self.pair_source, self.sources),
                                           (self.source_slot, self.slots[0], self.pair_target, self.targets)):
            chance = np.ones(len(self.pair))
            for _ in range(ITERATIONS):
                weight = (chance * prior)[self.row]
                share = weight / np.bincount(slot, weights=weight, minlength=slots)[slot]
                expected = np.bincount(self.row, weights=share, minlength=len(self.pair))
                chance = expected / np.maximum(np.bincount(owner, weights=expected, minlength=owners)[owner], 1e-12)
            weight = (chance * prior)[self.row]
            order = np.lexsort((weight, slot))
            last = np.flatnonzero(np.diff(slot[order], append=-1))   # the heaviest row of each slot
            chosen = np.zeros(len(self.row), dtype=bool)
            chosen[order[last]] = True
            best.append(chosen)
        linked, times = np.unique(self.pair[self.row[best[0] & best[1]]], return_counts=True)
        return {(int(pair // self.targets), int(pair % self.targets)): int(n) for pair, n in zip(linked, times)}


def latin_side() -> tuple[dict, dict[str, str], collections.Counter]:
    words, forms = bible.dictionary(), bible.inflected()
    word_of, _, _ = bible.token_words(words, forms)
    counts, _, _ = bible.count_words(words, forms)
    return verses(TEXTS / "la.tsv"), word_of, counts


def paired(latin: dict, other: dict, word_of: dict[str, str], head_of: dict[str, str] | None = None):
    """Verse pairs as word ids, and the two vocabularies."""
    source_ids: dict[str, int] = {}
    target_ids: dict[str, int] = {}
    pairs = []
    for key in sorted(set(latin) & set(other)):
        if key[0] in SKIPPED_BOOKS:
            continue
        source = [word_of.get(token, "?" + token) for token in tokens(bible.plain(latin[key]))]
        target = [head_of.get(token, token) if head_of else token for token in tokens(other[key])]
        if source and target:
            pairs.append(([source_ids.setdefault(word, len(source_ids)) for word in source],
                          [target_ids.setdefault(word, len(target_ids)) for word in target]))
    return pairs, list(source_ids), list(target_ids)


def anchors() -> None:
    latin, word_of, counts = latin_side()
    ALIGNED.mkdir(parents=True, exist_ok=True)
    shown: dict[str, dict[str, list[str]]] = collections.defaultdict(dict)
    reached = {}
    with KEYS.open("w", encoding="utf-8") as keys:
        keys.write("language\tlatin\tword\tlinks\tshare\n")
        for language in ANCHORS:
            text = verses(TEXTS / f"{language}.tsv")
            counted = collections.Counter(token for verse in text.values() for token in tokens(verse))
            pairs, sources, targets = paired(latin, text, word_of, headwords(language, counted))
            found = Aligner(pairs, len(sources), len(targets)).links()
            by_word: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
            for (source, target), n in found.items():
                if not sources[source].startswith("?"):
                    by_word[sources[source]][targets[target]] = n
            kept = 0
            with (ALIGNED / f"{language}.tsv").open("w", encoding="utf-8") as out:
                out.write("latin\tform\tlinks\tshare\ttext\n")
                for word, _ in counts.most_common():
                    total = sum(by_word[word].values())
                    for form, n in by_word[word].most_common(5):
                        cognate = resemblance(shape(word[:-2] if len(word) > 4 else word), shape(form)) >= 0.4
                        if n >= 2 and n / total >= 0.08 or n == 1 and total <= 2 and cognate:
                            keys.write(f"{language}\t{word}\t{form}\t{n}\t{n / total:.2f}\n")
                            out.write(f"{word}\t{form}\t{n}\t{n / total:.2f}\t{language}\n")
                            shown[word].setdefault(language, []).append(f"{form} {round(100 * n / total)}%")
                            kept += 1
            reached[language] = (len(pairs), sum(1 for word in shown if language in shown[word]))
            print(f"{language}: {len(pairs):,} verses, {kept:,} pairs kept", flush=True)
    words = bible.dictionary()
    lines = [
        "# What the modern Bibles say where the Latin has each word", "",
        "Generated by `scripts/align_bible.py anchors`. Do not edit by hand.", "",
        "The Clementine Vulgate is lined up verse by verse with the French (Segond 1910), Spanish "
        "(Reina-Valera 1909), Portuguese (Bíblia Livre 2018) and Italian (Riveduta 1927) Bibles "
        "([`bible_sources.md`](../bible_sources.md)); the Psalms are left out, since the Vulgate numbers "
        "them differently. Each word of a modern Bible is brought to its dictionary headword, and a "
        "Latin word is paired with the headword that stands for it: a pair counts in a verse when each "
        "is the other's best partner there (IBM Model 1, run both ways). The percentage is the share of "
        "the Latin word's pairs that go to that headword; up to three are shown.", "",
        "This answers two things the list of reflexes cannot: what the daughters say for a Latin word "
        "that left no descendant (*autem*, *enim*, *numquid*), and which of a word's descendants a "
        "translator actually reaches for (*dominus*: *seigneur*, *señor*, not *dom*). These headwords "
        "are also the keys through which the small lects' dictionaries are read "
        "([`bible_coverage.md`](bible_coverage.md)). Romanian is aligned too and used the same way; its "
        "words are not printed here because that text's licence is not settled.", "",
        "Known faults: a headword spelt like a form of another word takes that word's place (Spanish "
        "*vino* is read as *venir*, so *vinum* shows no Spanish word); the modern Bibles follow the "
        "Hebrew and Greek, not the Vulgate, so a verse may simply say something else; and a Latin word "
        "the aligner pairs with nothing consistent shows an empty cell.", "",
        "- Verses lined up: " + ", ".join(f"{PRINTED[language]} {reached[language][0]:,}" for language in PRINTED) + ".",
        f"- Latin words with a counterpart, of {len(counts):,}: "
        + ", ".join(f"{PRINTED[language]} {reached[language][1]:,}" for language in PRINTED) + ".", "",
        f"## The {SHOWN} commonest words", "",
        "| rank | Latin | count | sense | " + " | ".join(PRINTED.values()) + " |",
        "|---:|---|---:|---|" + "---|" * len(PRINTED),
    ]
    for rank, (word, n) in enumerate(counts.most_common(SHOWN), 1):
        cells = [", ".join(shown[word].get(language, [])[:3]) for language in PRINTED]
        lines.append(f"| {rank} | {word} | {n:,} | {words[word]['gloss'][:40].replace('|', '/')} | " + " | ".join(cells) + " |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT}")


def references(lect: str) -> dict[str, set[frozenset[str]]]:
    """Latin word → the shapes a form of the lect for it may resemble."""
    found: dict[str, set[frozenset[str]]] = collections.defaultdict(set)
    if KEYS.is_file():
        with KEYS.open(encoding="utf-8") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                found[row["latin"]].add(shape(row["word"]))
    pool = POOL / f"{lect}.tsv"
    if pool.is_file():
        with pool.open(encoding="utf-8") as stream:
            for row in csv.DictReader(stream, delimiter="\t", quoting=csv.QUOTE_NONE):
                if row["route"] not in ("bible", "bridge"):
                    found[row["latin"]].add(shape(row["form"]))
    return found


def lects(wanted: list[str]) -> None:
    latin, word_of, counts = latin_side()
    ALIGNED.mkdir(parents=True, exist_ok=True)
    by_lect: dict[str, list[Path]] = collections.defaultdict(list)
    for path in sorted(LECT_TEXTS.glob("*.tsv")):
        by_lect[path.stem.split("-")[0]].append(path)
    for lect, paths in by_lect.items():
        if wanted and lect not in wanted:
            continue
        known = references(lect)
        rows = []
        for path in paths:
            pairs, sources, targets = paired(latin, verses(path), word_of)
            if not pairs:
                continue
            aligner = Aligner(pairs, len(sources), len(targets))
            target_shapes = [shape(word) for word in targets]
            # In how many verses each word stands: a word of two verses is not rendered by one of two hundred.
            source_verses = collections.Counter(word for source, _ in pairs for word in set(source))
            target_verses = collections.Counter(word for _, target in pairs for word in set(target))
            likeness = np.zeros(len(aligner.pair))
            for index, (source, target) in enumerate(zip(aligner.pair_source, aligner.pair_target)):
                word = sources[source]
                if word.startswith("?"):   # a name: it is spelt much the same everywhere
                    likeness[index] = resemblance(shape(word[1:-2] if len(word) > 5 else word[1:]), target_shapes[target])
                    continue
                stem = shape(word[:-2] if len(word) > 4 else word)
                likeness[index] = max([resemblance(stem, target_shapes[target])]
                                      + [resemblance(seen, target_shapes[target]) for seen in known.get(word, ())])
            found = aligner.links(prior=1 + 8 * likeness ** 2)
            like = {(int(s), int(t)): float(v) for s, t, v in zip(aligner.pair_source, aligner.pair_target, likeness)}
            by_word: dict[str, list[tuple[int, float, str, bool]]] = collections.defaultdict(list)
            for (source, target), n in found.items():
                if not sources[source].startswith("?"):
                    fits = target_verses[target] <= 4 * source_verses[source] + 2
                    by_word[sources[source]].append((n, like[source, target], targets[target], fits))
            for word, linked in by_word.items():
                total = sum(n for n, _, _, _ in linked)
                for n, likeness_here, form, fits in sorted(linked, reverse=True):
                    alike = likeness_here >= 0.5
                    # A single verse counts for a word that has few: one stray link among fifty is noise.
                    if n >= 2 and n / total >= (0.05 if alike else 0.15) or n == 1 and alike and fits and total <= 6:
                        rows.append((word, form, n, n / total, likeness_here, path.stem))
        rank = {word: index for index, (word, _) in enumerate(counts.most_common())}
        with (ALIGNED / f"{lect}.tsv").open("w", encoding="utf-8") as out:
            out.write("latin\tform\tlinks\tshare\tresemblance\ttext\n")
            for word, form, n, share, likeness_here, text in sorted(rows, key=lambda row: (rank.get(row[0], 10 ** 6), -row[2])):
                out.write(f"{word}\t{form}\t{n}\t{share:.2f}\t{likeness_here:.2f}\t{text}\n")
        print(f"{lect}: {len(paths)} text(s), {len({row[0] for row in rows}):,} Latin words with a form, "
              f"{len(rows):,} pairs", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("anchors", "lects"))
    parser.add_argument("lects", nargs="*", help="for `lects`: the lects to align; default: every text on disk")
    args = parser.parse_args()
    if args.command == "anchors":
        anchors()
    else:
        lects(args.lects)


if __name__ == "__main__":
    main()
