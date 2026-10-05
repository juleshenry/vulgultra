#!/usr/bin/env python3
"""Evidence for the spelling gate: pool segments that have no spelling rule.

The grid is transcribed once. The minimum-σ shortlist is then rebuilt under
each merge scenario, so what a merge costs (lost candidates, longer words,
forms shared between concepts) is measured on the same code path as prep.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vulgultra.candidate_prep import build_candidates
from vulgultra.g2p import UntranscribedError, transcribe_and_repair
from vulgultra.optimizer import Candidate
from vulgultra.phonology import is_vowel, repair
from vulgultra.phonology_constants import IPA_TO_ORTHO
from vulgultra.pipeline import gold_concepts

LEAK, KEPT = "leak", "kept"

GROUPS = {
    LEAK: (
        "Source letters with no reading yet",
        "Not IPA. The lect is transcribed with a sister's backend, which passes the "
        "letter through, and PanPhon accepts letter plus diacritic as a segment. "
        "Each needs a reading in `BACKEND_LEFTOVERS` before it can be spelled.",
    ),
    KEPT: (
        "Kept segments without a spelling",
        "Some daughter uses each of these to tell words apart (`grammar.tex` §2.4), so "
        "none is merged. **Merge to** is only the target the last table uses to "
        "measure what merging would cost.",
    ),
}

# segment → (group, merge target or None, spelling if kept, note). The
# spellings are proposals for Gate G0; nothing in the pipeline reads this.
PROPOSALS: dict[str, tuple[str, tuple[str, ...] | None, str, str]] = {
    "ɾ": (KEPT, ("r",), "", "single r; es ca pt gl contrast it with the strong r (caro/carro)"),
    "ʁ": (KEPT, ("r",), "", "Portuguese strong r"),
    "ʀ": (KEPT, ("r",), "", "the one rhotic of the Oïl lects"),
    "ŋ": (KEPT, ("n",), "", "variant of /n/ in ca oc gsc; a phoneme in Ligurian and Emilian"),
    "ɑ": (KEPT, ("a",), "", "contrasts with a in conservative French (pâte/patte)"),
    "ɐ": (KEPT, ("a",), "", "Ladin ë"),
    "ɒ": (KEPT, ("a",), "å", "Istro-Romanian å, kept as its own letter"),
    "æ": (KEPT, ("e",), "ę", "Istro-Romanian ę, kept as its own letter"),
    "ɛ": (KEPT, ("e",), "è", "open e"),
    "ɔ": (KEPT, ("o",), "ò", "open o"),
    "ə": (KEPT, ("e",), "ë", "schwa"),
    "ɨ": (KEPT, ("i",), "î", "Romanian î/â"),
    "y": (KEPT, ("u",), "ü", "front rounded high"),
    "ø": (KEPT, ("o",), "ö", "front rounded mid"),
    "œ": (KEPT, ("o",), "ö", "front rounded mid, open; one letter with ø"),
    "ɥ": (KEPT, ("w",), "", "front rounded glide; goes with y"),
    "ʒ": (KEPT, ("ʃ",), "j", "j is a free letter"),
    "d͡ʒ": (KEPT, ("t͡ʃ",), "dj", "digraph; the reader is one character at a time today"),
    "t͡s": (KEPT, ("s",), "ts", "digraph, same caveat"),
    "d͡z": (KEPT, ("z",), "dz", "digraph, same caveat"),
    "h": (KEPT, (), "h", "h is a free letter; merging means deleting it"),
    "θ": (KEPT, ("s",), "", "Galician"),
    "ð": (KEPT, ("z",), "", "Romagnol ẓ"),
    "x": (KEPT, ("k",), "", "Spanish jota"),
    "ɑ̃": (KEPT, ("a", "n"), "ã", "nasal vowel; merging restores the nasal consonant"),
    "ɐ̃": (KEPT, ("a", "n"), "ã", "one letter with ɑ̃"),
    "ə̃": (KEPT, ("e", "n"), "", "Romagnol ã"),
    "ɔ̃": (KEPT, ("o", "n"), "õ", ""),
    "õ": (KEPT, ("o", "n"), "õ", "one letter with ɔ̃"),
    "ɛ̃": (KEPT, ("e", "n"), "ẽ", ""),
    "œ̃": (KEPT, ("e", "n"), "ẽ", "one letter with ɛ̃"),
    "ũ": (KEPT, ("u", "n"), "ũ", ""),
}

# PanPhon hands back decomposed segments; match them whatever form is typed here.
PROPOSALS = {unicodedata.normalize("NFD", seg): row for seg, row in PROPOSALS.items()}

SCENARIOS = (
    ("As decided (grammar.tex §2.4)", ()),
    ("If every kept segment were merged too", (KEPT,)),
)


def merge_table(groups: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    """Targets for the chosen groups, with chains (ö → ø → o) followed."""
    direct = {
        seg: tuple(unicodedata.normalize("NFD", part) for part in row[1])
        for seg, row in PROPOSALS.items() if row[0] in groups and row[1] is not None
    }

    def expand(seg: str, seen: frozenset[str] = frozenset()) -> tuple[str, ...]:
        if seg not in direct or seg in seen:
            return (seg,)
        return tuple(out for part in direct[seg] for out in expand(part, seen | {seg}))

    return {seg: expand(seg) for seg in direct}


def shortlist(
    concepts: dict, cache: dict[tuple[str, str], tuple[str, list[str]] | Exception],
    table: dict[str, tuple[str, ...]],
) -> dict[str, list[Candidate]]:
    def transcribe(word: str, lang: str) -> tuple[str, list[str]]:
        if (word, lang) not in cache:
            try:
                cache[(word, lang)] = transcribe_and_repair(word, lang)
            except Exception as error:
                cache[(word, lang)] = error
        result = cache[(word, lang)]
        if isinstance(result, Exception):
            raise result
        ipa, seq = result
        if not table:
            return ipa, seq
        return ipa, repair([out for seg in seq for out in table.get(seg, (seg,))])

    return build_candidates(concepts, transcribe=transcribe)


def spelled(candidate: Candidate) -> bool:
    return all(seg in IPA_TO_ORTHO for seg in candidate.vulgultra_phonemes)


def without_own_form(pool: dict[str, list[Candidate]]) -> int:
    """Concepts left over when each form may serve one concept (maximum matching)."""
    forms = {cid: sorted({tuple(c.vulgultra_phonemes) for c in cands}) for cid, cands in pool.items()}
    owner: dict[tuple[str, ...], str] = {}

    def place(cid: str, seen: set[tuple[str, ...]]) -> bool:
        for form in forms[cid]:
            if form in seen:
                continue
            seen.add(form)
            if form not in owner or place(owner[form], seen):
                owner[form] = cid
                return True
        return False

    return sum(not place(cid, set()) for cid in sorted(forms))


def pool_stats(pool: dict[str, list[Candidate]], n_concepts: int) -> dict[str, int]:
    segments = {seg for cands in pool.values() for c in cands for seg in c.vulgultra_phonemes}
    owners: dict[tuple[str, ...], set[str]] = defaultdict(set)
    for cid, cands in pool.items():
        for c in cands:
            owners[tuple(c.vulgultra_phonemes)].add(cid)
    shared = {form for form, ids in owners.items() if len(ids) > 1}
    return {
        "segments": len(segments),
        "unspelled": sum(seg not in IPA_TO_ORTHO for seg in segments),
        "candidates": sum(len(cands) for cands in pool.values()),
        "spellable": sum(any(spelled(c) for c in cands) for cands in pool.values()),
        "syllables": sum(cands[0].syllables for cands in pool.values()),
        "lost": n_concepts - len(pool),
        "share_some": sum(
            any(tuple(c.vulgultra_phonemes) in shared for c in cands) for cands in pool.values()
        ),
        "forced": without_own_form(pool),
    }


def segment_rows(pool: dict[str, list[Candidate]], roots: dict[str, dict]) -> list[dict]:
    candidates: Counter[str] = Counter()
    concepts: dict[str, set[str]] = defaultdict(set)
    forced: Counter[str] = Counter()
    lects: dict[str, Counter[str]] = defaultdict(Counter)
    example: dict[str, Candidate] = {}
    for cid, cands in pool.items():
        for c in cands:
            for seg in set(c.vulgultra_phonemes):
                candidates[seg] += 1
                concepts[seg].add(cid)
                lects[seg][c.source_lang] += 1
                root = roots.get(cid, {})
                is_root = (root.get("source_lang"), root.get("source_word")) == (c.source_lang, c.source_word)
                if seg not in example or is_root:
                    example[seg] = c
        for seg in set.intersection(*(set(c.vulgultra_phonemes) for c in cands)):
            forced[seg] += 1
    in_roots = Counter(seg for root in roots.values() for seg in set(root.get("ipa", [])))
    return [
        {
            "segment": seg,
            "kind": "V" if is_vowel(seg) else "C",
            "candidates": candidates[seg],
            "concepts": len(concepts[seg]),
            "forced": forced[seg],
            "roots": in_roots.get(seg, 0),
            "lects": ", ".join(f"{lect} {n}" for lect, n in lects[seg].most_common(3)),
            "example": f"{example[seg].source_lang} *{example[seg].source_word}* → `{example[seg].orthography}`",
        }
        for seg in sorted(candidates, key=lambda s: (-candidates[s], s))
        if seg not in IPA_TO_ORTHO
    ]


def rejected_rows(cache: dict) -> list[str]:
    """One row per lect and leftover letter, with the words it blocks."""
    blocked: dict[tuple[str, str], list[str]] = defaultdict(list)
    for (word, lang), result in sorted(cache.items()):
        if isinstance(result, UntranscribedError):
            for leftover in sorted(set(result.leftovers)):
                blocked[(lang, leftover)].append(f"*{word}* → {result.ipa}")
        elif isinstance(result, Exception):
            blocked[(lang, type(result).__name__)].append(f"*{word}*")
    return [
        f"| {lang} | `{leftover}` | {len(words)} | {'; '.join(words[:4])} |"
        for (lang, leftover), words in sorted(blocked.items(), key=lambda item: (item[0][0], -len(item[1])))
    ]


def render(concepts: dict, pools: list[tuple[str, dict[str, list[Candidate]]]],
           roots: dict[str, dict], lexicon_note: str, rejected: list[str]) -> str:
    baseline = pools[0][1]
    rows = segment_rows(baseline, roots)
    n_forms = sum(len(v) for forms in concepts.values() for k, v in forms.items() if k != "__meta__")
    stats = [(name, pool_stats(pool, len(concepts))) for name, pool in pools]
    today = stats[0][1]
    unspellable = sorted(cid for cid, cands in baseline.items() if not any(spelled(c) for c in cands))

    out = [
        "# Orthography gaps",
        "",
        "Generated by `scripts/orthography_gaps.py`. Do not edit by hand.",
        "",
        f"Input: {len(concepts)} concepts and {n_forms} grid forms, transcribed and shortlisted "
        f"with the current code. {lexicon_note}",
        "",
        f"The shortlist holds {today['segments']} segments. The spelling map covers "
        f"{len(IPA_TO_ORTHO)}; {today['unspelled']} have no spelling and print as `⟨IPA⟩`. "
        f"{len(unspellable)} concepts have no shortlisted candidate that can be spelled at all.",
        "",
        "Columns: **cands** = shortlisted candidates containing the segment; "
        "**concepts** = concepts with such a candidate; **forced** = concepts where every "
        "shortlisted candidate contains it; **roots** = roots in the lexicon file that use it. "
        "**Spell as** is a proposal for Gate G0, not a decision.",
        "",
    ]
    for group, (title, blurb) in GROUPS.items():
        members = [row for row in rows if PROPOSALS.get(row["segment"], ("",))[0] == group]
        if not members:
            continue
        out += [f"## {title}", "", blurb, "",
                "| segment | | cands | concepts | forced | roots | lects | merge to | spell as | example | note |",
                "|---|---|---:|---:|---:|---:|---|---|---|---|---|"]
        for row in members:
            _, target, spelling, note = PROPOSALS[row["segment"]]
            out.append(
                f"| {row['segment']} | {row['kind']} | {row['candidates']} | {row['concepts']} "
                f"| {row['forced']} | {row['roots']} | {row['lects']} "
                f"| {'?' if target is None else ' '.join(target) or '∅'} | {spelling or '–'} "
                f"| {row['example']} | {note} |"
            )
        out.append("")
    unclassified = [row for row in rows if row["segment"] not in PROPOSALS]
    if unclassified:
        out += ["## No proposal yet", "",
                "| segment | | cands | concepts | forced | roots | lects | example |",
                "|---|---|---:|---:|---:|---:|---|---|"]
        out += [
            f"| {row['segment']} | {row['kind']} | {row['candidates']} | {row['concepts']} "
            f"| {row['forced']} | {row['roots']} | {row['lects']} | {row['example']} |"
            for row in unclassified
        ]
        out.append("")

    out += [
        "## What the kept segments cost and buy",
        "",
        "The second row rebuilds the minimum-σ shortlist with every kept segment merged "
        "into its target before repair and the legality check. **Spellable** = concepts with at least one candidate the "
        "current map can spell. **Σσ** = sum of each concept's minimum syllable count. "
        "**Contested** = concepts with a shortlisted form that is also shortlisted for "
        "another concept. **Forced homophones** = concepts left without a form of their own "
        "however the others choose.",
        "",
        "| Scenario | segments | unspelled | candidates | spellable | Σσ | no legal candidate | contested | forced homophones |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    out += [
        f"| {name} | {s['segments']} | {s['unspelled']} | {s['candidates']} | {s['spellable']} "
        f"| {s['syllables']} | {s['lost']} | {s['share_some']} | {s['forced']} |"
        for name, s in stats
    ]
    out += [
        "",
        "## Concepts with no spellable candidate today",
        "",
        ", ".join(f"`{cid}`" for cid in unspellable) or "None.",
        "",
        "## Grid forms the transcriber rejects",
        "",
        "The backend left a letter that is not IPA and `BACKEND_LEFTOVERS` has no reading "
        "for it in that lect, so the form cannot compete. An apostrophe is an elision or a "
        "clitic: the grid cell needs a different citation form, not a reading.",
        "",
        "| lect | leftover | forms | examples |",
        "|---|---|---:|---|",
        *(rejected or ["| – | | 0 | |"]),
        "",
    ]
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-l", "--lexicon", default="data/vulgultra_lexicon.json")
    parser.add_argument("-o", "--output", default="docs/eval/orthography_gaps.md")
    args = parser.parse_args()

    concepts = gold_concepts()
    cache: dict[tuple[str, str], tuple[str, list[str]] | Exception] = {}
    pools = [(name, shortlist(concepts, cache, merge_table(groups))) for name, groups in SCENARIOS]

    lexicon_path = Path(args.lexicon)
    roots: dict[str, dict] = {}
    lexicon_note = "No lexicon file was found, so the roots column is empty."
    if lexicon_path.is_file():
        raw = lexicon_path.read_bytes()
        roots = json.loads(raw).get("roots", {})
        lexicon_note = (
            f"The roots column reads `{args.lexicon}` (sha256 `{hashlib.sha256(raw).hexdigest()[:12]}`), "
            "which may come from an older run than the shortlist."
        )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(concepts, pools, roots, lexicon_note, rejected_rows(cache)), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
