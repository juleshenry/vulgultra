"""
vulgultra.pipeline — End-to-end pipeline for generating a Vulgultra lexicon.

Steps:
  1. Get top N words by Zipf frequency from Romance languages
  2. Cross-reference to find shared concepts (words appearing in 2+ languages)
  3. Convert each candidate to IPA via epitran
  4. Adapt to Vulgultra phonotactics
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

from vulgultra.phonology import (
    word_to_ipa, ipa_to_vulgultra, count_syllables, count_violations,
    to_orthography, extract_phonemes, PHONEME_INVENTORY, VOWELS,
    overlay_spelling_contrasts, repair, tokenize_ipa, configure_inventory,
    is_vowel,
)
from vulgultra.optimizer import (
    Candidate, Genome, SAResult, anneal,
    NOUN_SLOTS, VERB_SLOTS, ADJ_SLOTS,
    compute_energy,
)
from vulgultra.romance_swadesh import SOURCE_LANGS

_WORDS_DIR = Path(__file__).resolve().parents[1] / "data" / "words"
_BIBLE_GRID_PATH = Path(__file__).resolve().parents[1] / "data" / "bible" / "concept_grid.json"
_GLOSS_INDEX: dict[str, dict[str, list[str]]] = {}
BIBLE_LANGS = ("fr", "es", "pt", "it", "ro")


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


def gold_concepts(
    langs: list[str] | None = None,
    bible_grid_path: str | Path | None = None,
) -> dict[str, dict[str, list[dict[str, str]]]]:
    """
    Meaning-aligned Romance concept grid, enriched by an optional Bible lexicon.

    English ids/glosses are labels only — never source forms. Each occupied
    cell carries one or more forms with evidence and relation metadata. The
    optional Bible grid can add Biblical concepts and attested alternatives;
    exact English-gloss matches in per-lect dictionaries only fill empty cells.
    """
    from vulgultra.romance_swadesh import SOURCE_LANGS, concepts as swadesh_concepts

    wanted = tuple(langs or SOURCE_LANGS)
    for lang in wanted:
        if lang == "en":
            raise ValueError("English is not a Vulgultra source language")
        if lang not in SOURCE_LANGS:
            raise ValueError(f"Unsupported source language: {lang}")

    out: dict[str, dict[str, list[dict[str, str]]]] = {}
    pos_of: dict[str, str] = {}
    gloss_of: dict[str, str] = {}
    for row in swadesh_concepts():
        pos_of[row["id"]] = row["pos"]
        # Concept ids are stable English keys; Spanish display glosses do not
        # participate in lexical matching.
        gloss_of[row["id"]] = row["id"].replace("_", " ")
        forms: dict[str, list[dict[str, str]]] = {}
        for lang in wanted:
            form = row[lang].strip()
            if form:
                forms[lang] = [{
                    "form": form,
                    "evidence": "curated-romance-grid",
                    "relation": "direct",
                }]
        if forms:
            out[row["id"]] = forms

    grid_path = Path(bible_grid_path) if bible_grid_path else _BIBLE_GRID_PATH
    if grid_path.is_file():
        _merge_bible_grid(out, pos_of, gloss_of, grid_path, wanted)
    return overlay_word_glosses(out, wanted, pos_of, gloss_of)


def _merge_bible_grid(
    concepts: dict[str, dict[str, list[dict[str, str]]]],
    pos_of: dict[str, str],
    gloss_of: dict[str, str],
    path: Path,
    langs: tuple[str, ...],
) -> None:
    """Merge human-aligned, per-translation Bible lexicon rows into the grid."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "vulgultra.bible-grid.v1":
        raise ValueError(f"{path}: expected schema vulgultra.bible-grid.v1")
    rows = data.get("concepts")
    if not isinstance(rows, list):
        raise ValueError(f"{path}: concepts must be an array")

    wanted = set(langs)
    for row in rows:
        cid = str(row.get("id") or "").strip()
        if not cid:
            raise ValueError(f"{path}: concept row has no id")
        gloss = str(row.get("gloss_en") or row.get("gloss") or cid).strip()
        pos = str(row.get("pos") or "").strip()
        gloss_of[cid] = gloss
        if pos:
            pos_of[cid] = pos
        cells = concepts.setdefault(cid, {})
        for lang, raw_forms in (row.get("forms") or {}).items():
            if lang not in SOURCE_LANGS:
                raise ValueError(f"{path}: {lang!r} is not a daughter lect")
            if lang not in wanted:
                continue
            for item in _form_records(raw_forms):
                form = item["form"].strip()
                if not form:
                    continue
                evidence = item.get("evidence") or "Bible-lexicon"
                record = {
                    "form": form,
                    "evidence": json.dumps(evidence, ensure_ascii=False, sort_keys=True)
                    if isinstance(evidence, (dict, list)) else str(evidence),
                    "relation": str(item.get("relation") or "direct"),
                }
                if record not in cells.setdefault(lang, []):
                    cells[lang].append(record)


def overlay_word_glosses(
    concepts: dict[str, dict[str, list[dict[str, str]]]],
    langs: tuple[str, ...],
    pos_of: dict[str, str] | None = None,
    gloss_of: dict[str, str] | None = None,
) -> dict[str, dict[str, list[dict[str, str]]]]:
    """Fill empty concept cells from per-lect words.json exact glosses."""
    pos_of = pos_of or {}
    gloss_of = gloss_of or {}
    filled = 0
    for lang in langs:
        index = _gloss_index(lang)
        if not index:
            continue
        for cid, forms in concepts.items():
            if forms.get(lang):
                continue
            gloss = gloss_of.get(cid, cid)
            lemmas = _best_lemmas(index, cid, pos_of.get(cid, ""), gloss)
            if lemmas:
                forms[lang] = [{
                    "form": lemma,
                    "evidence": "exact-English-gloss-lexicon",
                    "relation": "gloss-equivalent",
                } for lemma in lemmas]
                filled += len(lemmas)
    if filled:
        print(f"  corpus gloss overlay: filled {filled} empty cells")
    return concepts


def _gloss_index(lang: str) -> dict[str, list[str]]:
    if lang in _GLOSS_INDEX:
        return _GLOSS_INDEX[lang]
    path = _WORDS_DIR / f"{lang}_words.json"
    index: dict[str, list[str]] = defaultdict(list)
    if not path.is_file():
        _GLOSS_INDEX[lang] = {}
        return _GLOSS_INDEX[lang]
    data = json.loads(path.read_text(encoding="utf-8"))
    for lemma, rec in (data.get("entries") or {}).items():
        if not isinstance(rec, dict):
            continue
        pos = rec.get("pos") or []
        if "character" in pos:
            continue
        raw = rec.get(lang) or lemma or ""
        if isinstance(raw, list):
            raw = raw[0] if raw else ""
        word = str(raw).strip()
        if len(word) < 2:
            continue
        for g in rec.get("glosses_en") or []:
            for key in _gloss_keys(g):
                if word not in index[key]:
                    index[key].append(word)
    _GLOSS_INDEX[lang] = dict(index)
    return _GLOSS_INDEX[lang]


def _gloss_keys(gloss: str) -> list[str]:
    g = gloss.strip().lower().split(",")[0].split(";")[0].strip()
    return [g] if g else []


def _best_lemmas(
    index: dict[str, list[str]], cid: str, pos: str = "", gloss: str = "",
) -> list[str]:
    spaced = cid.replace("_", " ")
    keys = [cid, spaced, gloss.strip().lower()]
    if pos == "verb":
        keys.extend([f"to {cid}", f"to {spaced}", f"to {gloss.strip().lower()}"])
    hits: list[str] = []
    for k in keys:
        hits.extend(index.get(k, []))
    if not hits:
        return []
    # Keep alternatives: the syllable shortlist, not spelling length, decides.
    return sorted(set(hits), key=lambda w: (w.casefold(), w))


def _form_records(raw: object) -> list[dict[str, str]]:
    """Normalize a grid cell from a string, object, or list of either."""
    if isinstance(raw, str):
        raw_forms: list[object] = [raw]
    elif isinstance(raw, list):
        raw_forms = raw
    elif isinstance(raw, dict):
        if "form" in raw or "word" in raw:
            raw_forms = [raw]
        else:
            return []
    else:
        return []

    out: list[dict[str, str]] = []
    for value in raw_forms:
        if isinstance(value, str):
            record = {"form": value, "evidence": "grid", "relation": "direct"}
        elif isinstance(value, dict):
            form = str(value.get("form") or value.get("word") or "").strip()
            if not form:
                continue
            evidence = value.get("evidence") or value.get("source") or "grid"
            record = {
                "form": form,
                "evidence": json.dumps(evidence, ensure_ascii=False, sort_keys=True)
                if isinstance(evidence, (dict, list)) else str(evidence),
                "relation": str(value.get("relation") or "direct"),
            }
        else:
            continue
        if record["form"].strip():
            out.append(record)
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
    concepts: dict[str, dict[str, object]],
) -> dict[str, list[Candidate]]:
    """
    Convert concept word lists to Candidate objects.
    Each candidate gets IPA transcription and Vulgultra adaptation.
    """
    all_candidates: dict[str, list[Candidate]] = {}
    errors = 0
    prepared: list[tuple[str, str, dict[str, str], str, list[str]]] = []
    observed_segments: set[str] = set()

    # Transcribe the complete active grid first. Phoneme indexes and feature
    # classes are then derived from actual Romance candidate forms, never from
    # a predeclared target inventory.
    for concept_id, lang_forms in concepts.items():
        for lang, raw_forms in lang_forms.items():
            for record in _form_records(raw_forms):
                try:
                    ipa = word_to_ipa(record["form"], lang)
                    segments = tokenize_ipa(ipa)
                    if not segments:
                        continue
                    prepared.append((concept_id, lang, record, ipa, segments))
                    observed_segments.update(segments)
                except Exception:
                    errors += 1

    configure_inventory(observed_segments)

    for concept_id, lang, record, ipa, segments in prepared:
        cands: list[Candidate] = []
        word = record["form"]
        try:
            vulgultra_phonemes = repair(
                overlay_spelling_contrasts(word, ipa_to_vulgultra(ipa))
            )
            if not vulgultra_phonemes:
                continue
            if count_violations(vulgultra_phonemes):
                continue
            cands.append(Candidate(
                concept=concept_id,
                source_lang=lang,
                source_word=word,
                ipa=ipa,
                vulgultra_phonemes=vulgultra_phonemes,
                orthography=to_orthography(vulgultra_phonemes),
                syllables=count_syllables(vulgultra_phonemes),
                violations=0,
                evidence=record.get("evidence", "grid"),
                relation=record.get("relation", "direct"),
            ))
        except Exception:
            errors += 1
            continue
        all_candidates.setdefault(concept_id, []).extend(cands)

    for concept_id, cands in list(all_candidates.items()):
        cands = normalize_morphemes(cands)
        # Stage 1 is a hard operation: only the legal minimum-σ slice is
        # exported. Stage 2 (SA) can never trade a syllable for inventory.
        min_syllables = min(c.syllables for c in cands)
        all_candidates[concept_id] = [
            c for c in cands if c.syllables == min_syllables
        ]

    if errors:
        print(f"  Warning: {errors} G2P errors skipped")

    return all_candidates


def _degeminate(seq: list[str]) -> tuple[str, ...]:
    """Collapse geminate consonants. Vowels stay, so a long vowel is not a geminate."""
    out: list[str] = []
    for p in seq:
        if out and out[-1] == p and not is_vowel(p):
            continue
        out.append(p)
    return tuple(out)


def normalize_morphemes(cands: list[Candidate]) -> list[Candidate]:
    """Attach a reusable adapted-stem/morpheme-support count to each form.

    Support counts lects whose repaired form matches exactly, or matches
    after geminate consonants collapse (gato / gatto). Candidates are not
    merged: an identical string from another lect stays, so the diversity
    term can assign that lect label. Distance ≤ 1 is not an allomorph.
    """
    keys = [_degeminate(c.vulgultra_phonemes) for c in cands]
    counts: dict[tuple[str, ...], int] = defaultdict(int)
    for key in keys:
        counts[key] += 1
    for c, key in zip(cands, keys):
        c.morpheme_key = "|".join(key)
        c.support = max(1, counts[key])
    cands.sort(key=lambda c: (c.violations, c.syllables, -c.support, c.source_lang))
    return cands


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
        all_phonemes.update(extract_phonemes(root.vulgultra_phonemes))
        roots_out[concept] = {
            "ipa": root.vulgultra_phonemes,
            "orthography": root.orthography,
            "source_lang": root.source_lang,
            "source_word": root.source_word,
            "syllables": root.syllables,
            "violations": root.violations,
            "evidence": root.evidence,
            "relation": root.relation,
            "morpheme_key": root.morpheme_key,
            "morpheme_support": root.support,
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
    print("  VULGULTRA LEXICON — OPTIMIZATION RESULT")
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
        all_phonemes.update(extract_phonemes(r.vulgultra_phonemes))
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
    bible_grid_path: str | Path | None = None,
) -> dict[str, dict[str, object]]:
    if "en" in langs:
        raise ValueError("English is not a Vulgultra source language")

    if concepts_source in {"grid", "swadesh"}:
        print(f"\n[1/3] Loading meaning grid ({', '.join(langs)})...")
        t0 = time.time()
        concepts = gold_concepts(langs, bible_grid_path)
        print(f"  {len(concepts)} meaning-aligned concepts")
        active_bible_grid = Path(bible_grid_path) if bible_grid_path else _BIBLE_GRID_PATH
        if active_bible_grid.is_file():
            print(f"  Bible lexicon grid: {active_bible_grid}")
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
    output_path: str = "data/vulgultra_lexicon.json",
    seed: int = 42,
    langs: list[str] | None = None,
    concepts_source: str = "grid",
    bible_grid_path: str | Path | None = None,
):
    """Run the complete Vulgultra E2E pipeline."""

    langs = langs or list(LANGUAGES)
    print("=" * 70)
    print("  VULGULTRA E2E PIPELINE")
    print("=" * 70)

    concepts = _load_concepts(n_words, langs, concepts_source, bible_grid_path)
    write_concept_grid(concepts, "data/concept_grid.json", bible_grid_path)
    multi = sum(1 for v in concepts.values() if len(v) >= 2)
    print(f"  {len(concepts)} concepts ({multi} shared across 2+ languages)")

    # Step 3+4: Build candidates
    print(f"\n[3/5] Building candidates (IPA → Vulgultra adaptation)...")
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
        raise ValueError("English is not a Vulgultra source language")
    return langs


def ending_catalog() -> dict:
    """Noun themes and verb blocks. Rust anneals roots; it does not own tables."""
    from vulgultra.paradigms import VERB_TEMPLATES, closed_noun_blocks

    nouns = closed_noun_blocks()
    return {
        "noun_slots": list(NOUN_SLOTS),
        "verb_slots": list(VERB_SLOTS),
        "noun_blocks": {
            name: [list(cell) for cell in cells]
            for name, cells in nouns.items()
        },
        "verb_blocks": {
            lang: [list(cell) for cell in cells]
            for lang, cells in VERB_TEMPLATES.items()
        },
    }


def candidates_to_export(candidates: dict[str, list[Candidate]]) -> dict:
    export = {
        "algorithm": {
            "grid": "meaning-aligned Romance concept grid",
            "stage_1": "legal minimum-syllable shortlist per concept",
            "stage_2": "anneal phoneme inventory, lect coverage, and morpheme support",
        },
        "concepts": {},
        "ending_catalog": ending_catalog(),
    }
    for concept_id, cands in candidates.items():
        export["concepts"][concept_id] = [
            {
                "concept": c.concept,
                "source_lang": c.source_lang,
                "source_word": c.source_word,
                "ipa": c.ipa,
                "vulgultra_phonemes": c.vulgultra_phonemes,
                "orthography": c.orthography,
                "syllables": c.syllables,
                "violations": c.violations,
                "support": c.support,
                "morpheme_key": c.morpheme_key,
                "evidence": c.evidence,
                "relation": c.relation,
            }
            for c in cands
        ]
    return export


def write_concept_grid(
    concepts: dict[str, dict[str, object]],
    output_path: str | Path,
    bible_grid_path: str | Path | None = None,
) -> None:
    """Write the auditable aligned grid separately from its σ shortlist."""
    rows = []
    for cid, cells in sorted(concepts.items()):
        forms = {}
        for lang, raw in sorted(cells.items()):
            records = _form_records(raw)
            if records:
                forms[lang] = records
        rows.append({"id": cid, "forms": forms})
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "schema": "vulgultra.concept-grid.v1",
        "metadata": {
            "source": "romance_swadesh grid plus optional Bible lexicon grid",
            "daughter_lects": list(SOURCE_LANGS),
            "bible_lexicon_languages": list(BIBLE_LANGS),
            "bible_grid_loaded": Path(bible_grid_path).is_file()
            if bible_grid_path else _BIBLE_GRID_PATH.is_file(),
        },
        "concepts": rows,
    }, indent=2, ensure_ascii=False), encoding="utf-8")


def run_prep(
    n_words: int = 1000,
    output_path: str = "data/candidates.json",
    langs: list[str] | str | None = None,
    concepts_source: str = "grid",
    grid_output_path: str = "data/concept_grid.json",
    bible_grid_path: str | Path | None = None,
):
    """
    Python-only prep stage: get word lists, build candidates, export JSON
    for the Rust SA optimizer.
    """
    langs = _parse_langs(langs)
    print("=" * 70)
    print("  VULGULTRA PREP — Python G2P Pipeline")
    print("=" * 70)

    concepts = _load_concepts(n_words, langs, concepts_source, bible_grid_path)
    multi = sum(1 for v in concepts.values() if len(v) >= 2)
    print(f"  {len(concepts)} concepts ({multi} with 2+ language forms)")

    print(f"\n[build] Building candidates (IPA → Vulgultra adaptation)...")
    t0 = time.time()
    candidates = build_candidates(concepts)
    total_cands = sum(len(v) for v in candidates.values())
    legal = sum(1 for cands in candidates.values() for c in cands if c.is_legal)
    print(f"  {len(candidates)} concepts with {total_cands} total candidates")
    print(f"  {legal}/{total_cands} candidates are phonotactically legal")
    print(f"  done in {time.time()-t0:.1f}s")

    write_concept_grid(concepts, grid_output_path, bible_grid_path)
    export = candidates_to_export(candidates)
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)
    print(f"\n  Candidates written to {out_path}")
    print(f"  Ready for Rust optimizer: vulgultra-cli -i {out_path}")

    return export


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Vulgultra Pipeline")
    sub = parser.add_subparsers(dest="command")

    # prep subcommand — Python-only, exports JSON for Rust
    prep_p = sub.add_parser("prep", help="Prepare candidates (Python G2P → JSON)")
    prep_p.add_argument("-n", "--num-words", type=int, default=1000,
                        help="Number of top words per language")
    prep_p.add_argument("-o", "--output", type=str, default="data/candidates.json",
                        help="Output candidates JSON path")
    prep_p.add_argument("--langs", type=str, default=",".join(LANGUAGES),
                        help="Comma-separated source languages (no English)")
    prep_p.add_argument("--concepts", type=str, default="grid",
                        choices=["grid", "swadesh", "wordfreq"],
                        help="Default grid is meaning-aligned; wordfreq is exploratory only")
    prep_p.add_argument("--grid-output", type=str, default="data/concept_grid.json",
                        help="Write the full aligned grid before minimum-σ filtering")
    prep_p.add_argument("--bible-grid", type=str, default=None,
                        help="Optional Bible lexicon grid; default data/bible/concept_grid.json")

    # run subcommand — full Python pipeline (slower, for testing)
    run_p = sub.add_parser("run", help="Full Python pipeline (slow, for testing)")
    run_p.add_argument("-n", "--num-words", type=int, default=1000,
                       help="Number of top words per language")
    run_p.add_argument("-i", "--iterations", type=int, default=200_000,
                       help="Max SA iterations")
    run_p.add_argument("-o", "--output", type=str, default="data/vulgultra_lexicon.json",
                       help="Output JSON path")
    run_p.add_argument("-s", "--seed", type=int, default=42,
                       help="Random seed")
    run_p.add_argument("--langs", type=str, default=",".join(LANGUAGES),
                        help="Comma-separated source languages (no English)")
    run_p.add_argument("--concepts", type=str, default="grid",
                       choices=["grid", "swadesh", "wordfreq"],
                       help="Default grid is meaning-aligned; wordfreq is exploratory only")
    run_p.add_argument("--bible-grid", type=str, default=None,
                       help="Optional Bible lexicon grid; default data/bible/concept_grid.json")

    args = parser.parse_args()

    if args.command == "prep":
        run_prep(
            n_words=args.num_words,
            output_path=args.output,
            langs=args.langs,
            concepts_source=args.concepts,
            grid_output_path=args.grid_output,
            bible_grid_path=args.bible_grid,
        )
    elif args.command == "run":
        run_pipeline(
            n_words=args.num_words,
            sa_iterations=args.iterations,
            output_path=args.output,
            seed=args.seed,
            langs=_parse_langs(args.langs),
            concepts_source=args.concepts,
            bible_grid_path=args.bible_grid,
        )
    else:
        parser.print_help()
