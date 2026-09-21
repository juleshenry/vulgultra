"""
lacyo.pipeline — End-to-end pipeline for generating a Lacyo lexicon.

Steps:
  1. Get top N words by Zipf frequency from Romance languages
  2. Cross-reference to find shared concepts (words appearing in 2+ languages)
  3. Convert each candidate to IPA via epitran
  4. Adapt to Lacyo phonotactics
  5. Feed into SA optimizer
  6. Output the complete lexicon
"""

from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from lacyo.phonology import (
    word_to_ipa, ipa_to_lacyo, count_syllables, count_violations,
    to_orthography, extract_phonemes, PHONEME_INVENTORY,
    phonemic_edit_distance, overlay_spelling_contrasts, repair,
)
from lacyo.optimizer import (
    Candidate, Genome, SAResult, anneal,
    NOUN_SLOTS, VERB_SLOTS, ADJ_SLOTS,
    compute_energy,
)
from lacyo.romance_swadesh import SOURCE_LANGS


# ---------------------------------------------------------------------------
# Step 1: Get word lists from multiple Romance languages
# ---------------------------------------------------------------------------

LANGUAGES = list(SOURCE_LANGS)


def get_top_words(n: int = 1000, langs: list[str] | None = None) -> dict[str, list[str]]:
    """Get top N words by frequency for each Romance language."""
    from wordfreq import top_n_list

    result: dict[str, list[str]] = {}
    for lang in (langs or LANGUAGES):
        words = top_n_list(lang, n)
        # Filter: only alpha words, length >= 2 (skip single letters)
        words = [w for w in words if w.isalpha() and len(w) >= 2]
        result[lang] = words
    return result


# ---------------------------------------------------------------------------
# Step 2: Cross-reference shared concepts
# ---------------------------------------------------------------------------

def find_shared_concepts(
    word_lists: dict[str, list[str]],
    min_languages: int = 2,
) -> dict[str, dict[str, str]]:
    """
    Find words that appear in multiple Romance languages (likely cognates).
    
    Strategy: For each word in each language, check if it appears in other
    language lists too (exact match or near-match). This is a rough heuristic —
    proper cognate detection would use etymological databases. But for PoC,
    shared orthographic forms work well for Romance languages.
    
    Returns: concept_id → {lang: word}
    """
    # Index: word → set of languages it appears in
    word_to_langs: dict[str, set[str]] = defaultdict(set)
    word_to_lang_form: dict[str, dict[str, str]] = defaultdict(dict)

    for lang, words in word_lists.items():
        for word in words:
            # Normalize: strip accents for matching purposes
            normalized = _normalize_for_matching(word)
            word_to_langs[normalized].add(lang)
            word_to_lang_form[normalized][lang] = word

    # Also collect unique words (only in 1 language) — we want ~1000 concepts total
    shared: dict[str, dict[str, str]] = {}
    unshared: dict[str, dict[str, str]] = {}

    for normalized, langs in word_to_langs.items():
        concept_id = f"concept_{normalized}"
        if len(langs) >= min_languages:
            shared[concept_id] = word_to_lang_form[normalized]
        elif len(langs) == 1:
            lang = list(langs)[0]
            unshared[concept_id] = word_to_lang_form[normalized]

    # Merge: prefer shared concepts, fill with unshared up to ~1000
    concepts = dict(shared)
    remaining = 1000 - len(concepts)
    if remaining > 0:
        for cid, forms in list(unshared.items())[:remaining]:
            concepts[cid] = forms

    return concepts


def gold_concepts(langs: list[str] | None = None) -> dict[str, dict[str, str]]:
    """
    Meaning-aligned concepts from the Romance Swadesh gold list.
    English ids are keys only — never source forms.
    """
    from lacyo.romance_swadesh import SOURCE_LANGS, concepts as swadesh_concepts

    wanted = tuple(langs or SOURCE_LANGS)
    for lang in wanted:
        if lang == "en":
            raise ValueError("English is not a Lacyo source language")
        if lang not in SOURCE_LANGS:
            raise ValueError(f"Unsupported source language: {lang}")

    out: dict[str, dict[str, str]] = {}
    for row in swadesh_concepts():
        forms: dict[str, str] = {}
        for lang in wanted:
            form = row[lang].strip()
            if form:
                forms[lang] = form
        if forms:
            out[row["id"]] = forms
    return out


def _normalize_for_matching(word: str) -> str:
    """Strip accents and normalize for cognate matching."""
    import unicodedata
    nfkd = unicodedata.normalize('NFKD', word.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


# ---------------------------------------------------------------------------
# Step 3+4: Convert to candidates
# ---------------------------------------------------------------------------

def build_candidates(
    concepts: dict[str, dict[str, str]],
) -> dict[str, list[Candidate]]:
    """
    Convert concept word lists to Candidate objects.
    Each candidate gets IPA transcription and Lacyo adaptation.
    """
    all_candidates: dict[str, list[Candidate]] = {}
    errors = 0

    for concept_id, lang_words in concepts.items():
        cands: list[Candidate] = []
        for lang, word in lang_words.items():
            try:
                ipa = word_to_ipa(word, lang)
                lacyo_phonemes = repair(
                    overlay_spelling_contrasts(word, ipa_to_lacyo(ipa))
                )

                if not lacyo_phonemes:
                    continue  # empty after adaptation

                viol = count_violations(lacyo_phonemes)
                if viol:
                    continue  # unrepairable — discard, do not score as a death penalty

                cand = Candidate(
                    concept=concept_id,
                    source_lang=lang,
                    source_word=word,
                    ipa=ipa,
                    lacyo_phonemes=lacyo_phonemes,
                    orthography=to_orthography(lacyo_phonemes),
                    syllables=count_syllables(lacyo_phonemes),
                    violations=0,
                )
                cands.append(cand)
            except Exception as e:
                errors += 1
                continue

        if cands:
            all_candidates[concept_id] = normalize_morphemes(cands)

    if errors:
        print(f"  Warning: {errors} G2P errors skipped")

    return all_candidates


def _similar(a: list[str], b: list[str]) -> bool:
    """Same adapted form, or near-allomorph of an attested form. No clipping."""
    if a == b:
        return True
    return phonemic_edit_distance(a, b) <= 1


def _support_of(seq: list[str], originals: list[Candidate]) -> int:
    n = 0
    for o in originals:
        if o.lacyo_phonemes == seq or phonemic_edit_distance(o.lacyo_phonemes, seq) <= 1:
            n += 1
    return n


def normalize_morphemes(cands: list[Candidate]) -> list[Candidate]:
    """
    Collapse attested allomorphs of the same word into one candidate.

    gato/gatto → one gato. Does not invent gat by stripping -o.
    A shorter unrelated form (xa ← chat) stays a separate candidate;
    syllables still decide between them.
    """
    originals = list(cands)
    pool = list(cands)

    for c in pool:
        c.support = max(1, _support_of(c.lacyo_phonemes, originals))

    parent = list(range(len(pool)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[rj] = ri

    for i in range(len(pool)):
        for j in range(i + 1, len(pool)):
            if _similar(pool[i].lacyo_phonemes, pool[j].lacyo_phonemes):
                union(i, j)

    clusters: dict[int, list[Candidate]] = {}
    for i, c in enumerate(pool):
        clusters.setdefault(find(i), []).append(c)

    kept: list[Candidate] = []
    for group in clusters.values():
        best = min(
            group,
            key=lambda c: (
                c.violations,
                c.syllables,
                -c.support,
                len(c.lacyo_phonemes),
                c.source_lang,
            ),
        )
        kept.append(best)

    kept.sort(key=lambda c: (c.violations, c.syllables, -c.support, c.source_lang))
    return kept


# ---------------------------------------------------------------------------
# Step 5+6: Run optimizer and produce output
# ---------------------------------------------------------------------------

def format_genome(result: SAResult) -> dict:
    """Convert SA result to serializable dict."""
    genome = result.genome

    # Collect final phoneme inventory
    all_phonemes: set[str] = set()
    roots_out: dict[str, dict] = {}

    for concept in genome.selections:
        root = genome.get_root(concept)
        all_phonemes.update(extract_phonemes(root.lacyo_phonemes))
        roots_out[concept] = {
            "ipa": root.lacyo_phonemes,
            "orthography": root.orthography,
            "source_lang": root.source_lang,
            "source_word": root.source_word,
            "syllables": root.syllables,
            "violations": root.violations,
        }

    # Endings
    noun_endings_out: dict[str, dict[str, str]] = {}
    for cls_id, cls_endings in genome.noun_endings.items():
        noun_endings_out[cls_id] = {
            slot: to_orthography(seq) for slot, seq in cls_endings.items()
        }
        for seq in cls_endings.values():
            all_phonemes.update(extract_phonemes(seq))

    verb_endings_out: dict[str, dict[str, str]] = {}
    for cls_id, cls_endings in genome.verb_endings.items():
        verb_endings_out[cls_id] = {
            slot: to_orthography(seq) for slot, seq in cls_endings.items()
        }
        for seq in cls_endings.values():
            all_phonemes.update(extract_phonemes(seq))

    adj_endings_out: dict[str, str] = {
        slot: to_orthography(seq) for slot, seq in genome.adj_endings.items()
    }
    for seq in genome.adj_endings.values():
        all_phonemes.update(extract_phonemes(seq))

    return {
        "version": "2.0",
        "metadata": {
            "total_concepts": len(roots_out),
            "total_energy": result.energy,
            "iterations": result.iterations,
            "acceptance_rate": round(result.acceptance_rate, 4),
        },
        "energy_breakdown": {k: round(v, 2) for k, v in result.breakdown.items()},
        "phoneme_inventory": sorted(all_phonemes),
        "phoneme_count": len(all_phonemes),
        "roots": roots_out,
        "noun_endings": noun_endings_out,
        "verb_endings": verb_endings_out,
        "adj_endings": adj_endings_out,
    }


def print_summary(result: SAResult):
    """Print a human-readable summary of the optimization result."""
    genome = result.genome
    roots = genome.all_roots()

    print("\n" + "=" * 70)
    print("  LACYO LEXICON — OPTIMIZATION RESULT")
    print("=" * 70)

    print(f"\n  Concepts:       {len(roots)}")
    print(f"  Iterations:     {result.iterations:,}")
    print(f"  Accept rate:    {result.acceptance_rate:.1%}")
    print(f"  Total energy:   {result.energy:,.0f}")

    print(f"\n  Energy breakdown:")
    for name, val in result.breakdown.items():
        print(f"    {name:12s}  {val:>12,.0f}")

    # Phoneme inventory
    all_phonemes: set[str] = set()
    for r in roots:
        all_phonemes.update(extract_phonemes(r.lacyo_phonemes))
    for e in genome.all_endings():
        all_phonemes.update(extract_phonemes(e))
    print(f"\n  Phoneme inventory ({len(all_phonemes)} phonemes):")
    print(f"    {sorted(all_phonemes)}")

    # Syllable distribution
    syl_counts = [r.syllables for r in roots]
    from collections import Counter
    syl_dist = Counter(syl_counts)
    print(f"\n  Root syllable distribution:")
    for s in sorted(syl_dist):
        pct = syl_dist[s] / len(roots) * 100
        bar = "█" * int(pct / 2)
        print(f"    {s} syl: {syl_dist[s]:>4d} ({pct:>5.1f}%) {bar}")
    avg_syl = sum(syl_counts) / len(syl_counts)
    print(f"    avg:  {avg_syl:.2f} syllables")

    # Violation count
    violations = sum(r.violations for r in roots)
    print(f"\n  Root violations: {violations}")

    # Show noun endings
    print(f"\n  Noun endings (class 1):")
    for cls_id, cls_endings in genome.noun_endings.items():
        print(f"    {cls_id}:")
        for slot, seq in cls_endings.items():
            print(f"      {slot:8s} → -{to_orthography(seq)}")

    # Show some verb endings
    print(f"\n  Verb endings (class 1, indicative present):")
    for cls_id, cls_endings in genome.verb_endings.items():
        prs_slots = {k: v for k, v in cls_endings.items() if k.startswith("prs_") and "subj" not in k}
        for slot, seq in prs_slots.items():
            print(f"    {slot:12s} → -{to_orthography(seq)}")
        break

    # Show adjective endings
    print(f"\n  Adjective endings:")
    for slot, seq in genome.adj_endings.items():
        print(f"    {slot:8s} → -{to_orthography(seq)}")

    # Show sample words
    print(f"\n  Sample roots (first 30):")
    sorted_roots = sorted(roots, key=lambda r: r.syllables)
    for r in sorted_roots[:30]:
        print(f"    {r.orthography:12s}  ({r.syllables}σ)  ← {r.source_lang}:{r.source_word}")

    print("\n" + "=" * 70)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def _load_concepts(
    n_words: int,
    langs: list[str],
    concepts_source: str,
) -> dict[str, dict[str, str]]:
    if "en" in langs:
        raise ValueError("English is not a Lacyo source language")

    if concepts_source == "swadesh":
        print(f"\n[1/3] Loading Swadesh gold concepts ({', '.join(langs)})...")
        t0 = time.time()
        concepts = gold_concepts(langs)
        print(f"  {len(concepts)} meaning-aligned concepts")
        print(f"  done in {time.time()-t0:.1f}s")
        return concepts

    if concepts_source != "wordfreq":
        raise ValueError(f"Unknown concepts source: {concepts_source}")

    print(f"\n[1/3] Getting top {n_words} words from {len(langs)} Romance languages...")
    t0 = time.time()
    word_lists = get_top_words(n_words, langs)
    for lang, words in word_lists.items():
        print(f"  {lang}: {len(words)} words")
    print(f"  done in {time.time()-t0:.1f}s")

    print(f"\n[2/3] Cross-referencing concepts...")
    t0 = time.time()
    concepts = find_shared_concepts(word_lists, min_languages=1)
    return concepts


def run_pipeline(
    n_words: int = 1000,
    sa_iterations: int = 200_000,
    output_path: str = "data/lacyo_lexicon.json",
    seed: int = 42,
    langs: list[str] | None = None,
    concepts_source: str = "wordfreq",
):
    """Run the complete Lacyo E2E pipeline."""

    langs = langs or list(LANGUAGES)
    print("=" * 70)
    print("  LACYO E2E PIPELINE")
    print("=" * 70)

    concepts = _load_concepts(n_words, langs, concepts_source)
    multi = sum(1 for v in concepts.values() if len(v) >= 2)
    print(f"  {len(concepts)} concepts ({multi} shared across 2+ languages)")

    # Step 3+4: Build candidates
    print(f"\n[3/5] Building candidates (IPA → Lacyo adaptation)...")
    t0 = time.time()
    candidates = build_candidates(concepts)
    total_cands = sum(len(v) for v in candidates.values())
    print(f"  {len(candidates)} concepts with {total_cands} total candidates")
    legal = sum(1 for cands in candidates.values() for c in cands if c.is_legal)
    print(f"  {legal}/{total_cands} candidates are phonotactically legal")
    print(f"  done in {time.time()-t0:.1f}s")

    # Step 5: Optimize
    print(f"\n[4/5] Running simulated annealing ({sa_iterations:,} max iterations)...")
    t0 = time.time()
    result = anneal(
        candidates,
        max_iterations=sa_iterations,
        seed=seed,
    )
    print(f"  done in {time.time()-t0:.1f}s")

    # Step 6: Output
    print(f"\n[5/5] Writing output...")
    output = format_genome(result)
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"  Written to {out_path}")
    print(f"  {len(output['roots'])} roots, {output['phoneme_count']} phonemes used")

    # Summary
    print_summary(result)

    return result, output


def _parse_langs(langs: list[str] | str | None) -> list[str]:
    if langs is None:
        return list(LANGUAGES)
    if isinstance(langs, str):
        langs = [p.strip() for p in langs.split(",") if p.strip()]
    if not langs:
        raise ValueError("At least one source language is required")
    if "en" in langs:
        raise ValueError("English is not a Lacyo source language")
    return langs


def candidates_to_export(candidates: dict[str, list[Candidate]]) -> dict:
    export = {"concepts": {}}
    for concept_id, cands in candidates.items():
        export["concepts"][concept_id] = [
            {
                "concept": c.concept,
                "source_lang": c.source_lang,
                "source_word": c.source_word,
                "ipa": c.ipa,
                "lacyo_phonemes": c.lacyo_phonemes,
                "orthography": c.orthography,
                "syllables": c.syllables,
                "violations": c.violations,
                "support": c.support,
            }
            for c in cands
        ]
    return export


def run_prep(
    n_words: int = 1000,
    output_path: str = "data/candidates.json",
    langs: list[str] | str | None = None,
    concepts_source: str = "wordfreq",
):
    """
    Python-only prep stage: get word lists, build candidates, export JSON
    for the Rust SA optimizer.
    """
    langs = _parse_langs(langs)
    print("=" * 70)
    print("  LACYO PREP — Python G2P Pipeline")
    print("=" * 70)

    concepts = _load_concepts(n_words, langs, concepts_source)
    multi = sum(1 for v in concepts.values() if len(v) >= 2)
    print(f"  {len(concepts)} concepts ({multi} with 2+ language forms)")

    print(f"\n[build] Building candidates (IPA → Lacyo adaptation)...")
    t0 = time.time()
    candidates = build_candidates(concepts)
    total_cands = sum(len(v) for v in candidates.values())
    legal = sum(1 for cands in candidates.values() for c in cands if c.is_legal)
    print(f"  {len(candidates)} concepts with {total_cands} total candidates")
    print(f"  {legal}/{total_cands} candidates are phonotactically legal")
    print(f"  done in {time.time()-t0:.1f}s")

    export = candidates_to_export(candidates)
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)
    print(f"\n  Candidates written to {out_path}")
    print(f"  Ready for Rust optimizer: cyberlatin-cli -i {out_path}")

    return export


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Lacyo Pipeline")
    sub = parser.add_subparsers(dest="command")

    # prep subcommand — Python-only, exports JSON for Rust
    prep_p = sub.add_parser("prep", help="Prepare candidates (Python G2P → JSON)")
    prep_p.add_argument("-n", "--num-words", type=int, default=1000,
                        help="Number of top words per language")
    prep_p.add_argument("-o", "--output", type=str, default="data/candidates.json",
                        help="Output candidates JSON path")
    prep_p.add_argument("--langs", type=str, default=",".join(LANGUAGES),
                        help="Comma-separated source languages (no English)")
    prep_p.add_argument("--concepts", type=str, default="wordfreq",
                        choices=["wordfreq", "swadesh"],
                        help="Concept source: wordfreq (orthographic) or swadesh (meaning-aligned)")

    # run subcommand — full Python pipeline (slower, for testing)
    run_p = sub.add_parser("run", help="Full Python pipeline (slow, for testing)")
    run_p.add_argument("-n", "--num-words", type=int, default=1000,
                       help="Number of top words per language")
    run_p.add_argument("-i", "--iterations", type=int, default=200_000,
                       help="Max SA iterations")
    run_p.add_argument("-o", "--output", type=str, default="data/lacyo_lexicon.json",
                       help="Output JSON path")
    run_p.add_argument("-s", "--seed", type=int, default=42,
                       help="Random seed")
    run_p.add_argument("--langs", type=str, default=",".join(LANGUAGES),
                        help="Comma-separated source languages (no English)")
    run_p.add_argument("--concepts", type=str, default="wordfreq",
                        choices=["wordfreq", "swadesh"],
                        help="Concept source: wordfreq (orthographic) or swadesh (meaning-aligned)")

    args = parser.parse_args()

    if args.command == "prep":
        run_prep(
            n_words=args.num_words,
            output_path=args.output,
            langs=args.langs,
            concepts_source=args.concepts,
        )
    elif args.command == "run":
        run_pipeline(
            n_words=args.num_words,
            sa_iterations=args.iterations,
            output_path=args.output,
            seed=args.seed,
            langs=_parse_langs(args.langs),
            concepts_source=args.concepts,
        )
    else:
        parser.print_help()
