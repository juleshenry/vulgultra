# Roadmap: everything except verb conjugation

Verb conjugation is being built by hand (harvest → per-lect pages → shortlist
→ manual picks). This roadmap covers the rest of the language so it can move
in parallel: noun and adjective declension, closed classes, the lexicon,
syntax, and the first real texts.

Canonical spec stays [`docs/grammar/grammar.tex`](docs/grammar/grammar.tex).
A stage changes the spec only after its gate.

## Method (every class)

Each grammatical class goes through the same four steps as the verbs. Nothing
grammatical is selected automatically.

1. **Harvest.** Attested forms per lect, with source, into
   `data/<class>/sources/{lect}.json`.
2. **Pages.** One comparison page per lect under `docs/<class>/`.
3. **Cross-lect minimal shortlist.** For each cell or concept, every attested
   candidate ranked by phonemic syllables, with lect support and the
   collisions a choice would create. One HTML page under `docs/eval/`.
4. **Manual pick.** The choice is made by hand at the stage gate, then encoded
   in a `*_constants.py` table with rationale and written into `grammar.tex`.

Open-class roots keep the enshrined algorithm (shortest legal attested form,
then annealing over ties). The method above is for everything that is a
paradigm or a closed set.

## Ground rules

- **Verb files are off limits to this roadmap:**
  `vulgultra/conjugation_harvest.py`, `vulgultra/verbix.py`,
  `scripts/build_conjugation_pages.py`, `scripts/verb_ending_candidates.py`,
  `scripts/harvest_*.py`, `docs/conjugations/`, the verb half of
  `vulgultra/paradigms.py`, and `assemble_verb_rows` in
  `vulgultra/optimizer.py`. Helpers are imported from them, never changed.
- **New files by default.** Shared files (`paradigms.py`, `optimizer.py`,
  `realize.py`, `morphology_constants.py`, `lib.rs`, `grammar.tex`) are edited
  only in a stage's encode step, after its gate.
- **One branch per stage.**
- **Axioms hold.** Daughters only, attested only, no padding a thin lect from
  a sister. A lect with no data for a class gets an empty page.
- **Downloads are confirmed each time** (Kaikki re-fetch, Bible editions).

## Where things stand (5 October 2026)

| Area | State |
|---|---|
| Noun table | One 12-ending table from the spec (`grammar.tex` §3.1), chosen as a block by the optimizer. No per-noun gender, stem or class. |
| Noun realisation | `vulgultra/realize.py` only produces singulars, assigns case by word position, and takes gender from a 25-noun hand list (everything else is masculine). |
| Root + ending junction | Endings are glued onto spelling strings with an ASCII vowel test. 40 of 213 roots end in a vowel and every noun ending starts with one. |
| Spelling | The spelling map covers 23 segments; the inventory has 64. 117 of 213 roots print with `⟨IPA⟩` brackets. |
| Closed classes | Six subject pronouns, numerals 1–5, three prepositions, three conjunctions, `o/a/os/as`, a present-only copula. No object or possessive pronouns, no `ke`. |
| Lexicon | 213 concepts, all in the gitignored `data/` folder. No tracked dictionary. |
| Bible grid | Importer exists (`scripts/build_bible_grid.py`); the five input TSVs do not. |
| Nominal source data | 25 smaller lects have nouns with gender and plurals in local Kaikki dumps. The dumps for es, pt, gl, ca, fr, it, ro, lmo, eml are verb-only. No local data for ext, gsc, pcd, frp, ruo, ruq. |
| Syntax | One paragraph in the spec (`grammar.tex` ch. 5). |

## Stage 0. Foundations

- [x] Candidates keep their concept's part of speech (was `verb` on every root).
- [ ] Tests that pin today's noun, adjective and sentence realisation.
- [ ] Orthography evidence table: every unspelled segment, how many roots use
      it, which merges the spec already orders but the code does not perform
      (`grammar.tex` §2.3: ʝ→j, x→k, ɲ→nj, ʎ→lj), a proposed spelling for
      each survivor.
- [ ] Lexicon entries carry `gloss_en`, `pos`, `gender`, `decl_class`, `stem`.

**Gate G0, spelling.** Per segment: merge it, spell it (letter, digraph or
diacritic), or leave it bracketed. Blocks any readable text.

## Stage 1. Nouns and adjectives

- [ ] **Fetch.** `scripts/fetch_kaikki_nominals.py`: noun, adjective, pronoun,
      determiner, article and numeral rows for es, pt, gl, ca, fr, it, ro, lmo
      into `data/words/kaikki-{code}-nominal.jsonl` (verb dumps untouched).
- [ ] **Harvest.** `vulgultra/declension_harvest.py`: gender, the four
      gender × number forms, plural-formation classes, adjective feminine and
      plural, and for Romanian and Aromanian the surviving case and definite
      forms. Apertium `.dix` paradigms under `vendor/` as a second source.
      Output `data/declension/sources/{lect}.json` (`vulgultra.declension.v1`).
- [ ] **Pages.** `scripts/build_declension_pages.py` → `docs/declensions/{lect}.md`.
- [ ] **Shortlist.** `scripts/noun_ending_candidates.py` →
      `docs/eval/noun_ending_candidates.html`. Also marks, for each of the
      spec's 12 cells, whether any daughter attests it.
- [ ] **Junction table.** What hiatus, glide, dropping the root's final vowel,
      or a linking consonant each do to syllable count and homophones.

**Gate G1, nouns.** Endings; the case layer (keep the Latin-derived
nom/acc/gen of the spec, use only what daughters attest, or drop case); one
table or several classes; the junction rule; how a noun gets its gender;
whether adjectives share the table.

- [ ] **Encode** the picks in `vulgultra/morphology_constants.py`; noun
      selection reads that table instead of searching; update `grammar.tex` §3.1–3.3.
- [ ] **Realise** on segment lists (`is_vowel`, `repair`, `count_violations`,
      `to_orthography`), with plural and genitive reachable, gender from the
      lexicon entry, and penultimate stress assigned.

## Stage 2. Closed classes

Same method, one paradigm at a time: personal pronouns by person, number and
role (subject, object, indirect, possessive, reflexive); demonstratives;
interrogatives and relatives (`ke`); quantifiers; articles; numerals 0–10,
tens, hundred, thousand; prepositions; conjunctions; particles (yes, not,
also, only, very, more, already, still).

- [ ] **Harvest** each paradigm per lect into `data/closed_class/sources/{lect}.json`.
- [ ] **Pages.** `docs/closed_class/{lect}.md`, laid out as paradigm tables.
- [ ] **Shortlist.** `docs/eval/closed_class_candidates.html`: per cell, the
      attested candidates by syllables, and every collision with an existing
      root, ending, article or copula form (today: `o` water/article, `e`
      wing/copula, `a` at/article).

**Gate G2, closed classes.** Each paradigm picked by hand: pronouns (the one
place every daughter still shows case), possessives, demonstratives, numeral
composition above ten, which case each preposition governs, indefinite
article yes or no.

Needs from the verb work: final person labels, reflexive `se`, pro-drop.

## Stage 3. Bible-grid lexicon

**Gate G3a, sourcing (before any download).** The five editions and their
licences, the concept-ID spine, the first slice, and the alignment method.

- [ ] Alignment tooling that turns verse-aligned editions into reviewable
      candidate rows, then writes accepted rows to
      `data/bible/lexicons/{fr,es,pt,it,ro}.tsv`.
- [ ] First slice through `scripts/build_bible_grid.py` → prep → Rust SA → lexicon.
- [ ] Fill the other 31 lects with cited forms only; make the gloss overlay
      respect part of speech (`vulgultra/pipeline.py`).
- [ ] Homophone audit as the lexicon grows.

**Gate G3b, homophones.** The objective has no collision term and 196 of 213
roots are one syllable. Policy is decided before the lexicon passes a few
hundred concepts.

Verb entries wait on the verb outcome.

## Stage 4. Grammatical derivation

Adverb formation, comparison, participles used as adjectives, numeral
composition, nominalised infinitives, by the same method. Kept small:
morpheme uniformity is not a goal, so each concept keeps its own shortest
attested form. **Gate G4.**

## Stage 5. Syntax

Expand `grammar.tex` ch. 5 into a specification: noun-phrase order, how roles
map to case, negation, questions, `ke` clauses, pronoun placement,
coordination, comparison, possession. Sentence realisation takes
role-labelled input so case comes from the role, not from word position.
Demo sentences cover plural, genitive, negation, question and subordinate
clause. **Gate G5.**

## Stage 6. Dictionary, texts, primer

- [ ] Tracked dictionary export under `docs/lexicon/` (`data/` is ignored).
- [ ] Sample texts with a coverage report of what cannot yet be produced.
- [ ] Refresh `books/beginners-guide/`.

## Order

```
Stage 0 ──G0──┐
              ├─> Stage 1 ──G1──> encode + realise ──> Stage 2 ──G2──┐
G3a ──> Stage 3 tooling (alongside Stage 1) ──────────> first slice ──G3b──> Stages 4, 5 ──> Stage 6
```

## Handoffs from the verb work

| Needed | For |
|---|---|
| Final tense/mood and person slot names | lexicon schema, realiser |
| What a verb's lexicon entry is (which attested form is the root; its theme) | Bible verbs in Stage 3 |
| Whether participles decline like adjectives | Stage 1 encode, Stage 4 |
| Reflexive and subject-pronoun conventions | Stage 2 |
| Full copula paradigm | Stage 5 |
