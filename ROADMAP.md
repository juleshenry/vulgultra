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
- [x] Tests that pin today's noun, adjective and sentence realisation
      (`vulgultra/test_realize.py`).
- [x] Orthography evidence: [`docs/eval/orthography_gaps.md`](docs/eval/orthography_gaps.md),
      from `scripts/orthography_gaps.py`.
- [x] `gloss_en` and `pos` joined onto roots after the optimizer
      (`vulgultra/lexicon_fields.py`, no Rust change). `gender`, `decl_class`
      and `stem` use the same join once Stage 1 produces them.

What the evidence shows:

- 41 of the 64 segments in the shortlist have no spelling. 4 are merges the
  spec already orders, 4 are source letters that were never transcribed
  (`ë ö ü ã`), 13 are narrow detail from a single G2P backend (four different
  r's), and 20 are real contrasts.
- Merging costs nothing but inventory. At every level of merging the total
  minimum syllable count stays 229, every concept keeps a legal candidate,
  and exactly one homophone is forced (`fight`/`hit`).
- The transcriber rejects 254 grid forms and prep only prints a count: ruo 68
  of 213, gsc 33, frp 25, oc 24, pcd 24, and French *père, mère, où, forêt*.
- Among equally short forms the root is decided by lect-code order: of 193
  concepts with a choice of lect, 171 take the alphabetically first code, and
  the anneal ends at the energy it started with.

**Gate G0, inventory, spelling and selection.** In this order, because each
answer changes which roots win:

1. Transcription: fix the rejected forms and the untranscribed letters first.
   **Decided: yes.** Done; see below.
2. Inventory: merge or keep. **Decided and in code.** Eleven merges, each
   with its ground, in `grammar.tex` §2.4 (`SEGMENT_MERGES`, `LECT_MERGES`).
   All four rhotics are kept, /x/ is kept, and so is everything else some
   daughter uses to tell words apart.
3. Spelling: per kept segment, a letter, digraph or diacritic, or leave it bracketed.
4. Selection among ties: what replaces lect-code order, whether homophones
   cost anything, and whether approved roots are pinned so that growing the
   grid cannot change them.

Transcription, as fixed:

- [x] Readings for the letters a borrowed backend leaves untranscribed
      (`BACKEND_LEFTOVERS` in `vulgultra/phonology_constants.py`). Rejected
      grid forms: 260 → 26.
- [x] A form with an unread letter is rejected by name
      (`UntranscribedError`), counted per lect by prep and itemised in the
      orthography report.
- [x] Readings looked up and sourced in
      [`docs/sources_orthography.md`](docs/sources_orthography.md): Romagnol
      and Emilian letters, Ladin *ë*, and Istro-Romanian *j* (the glide in
      its Croatian-based spelling). Rejected grid forms: 26 → 15.
- [ ] The 15 left all contain an apostrophe (`s'assir`, `p'tit`, `ch'la`);
      they need a different citation form in the grid, not a reading.
- [ ] Rulings needed, listed with their sources in the same file: Walloon
      *xh* (four dialect values, none of them the /ks/ it gets now);
      Istro-Romanian *c* and its central vowel; Aromanian *nj*;
      Piedmontese *o, u* (/u/, /y/, read as o, u); Occitan and Gascon *qu*
      (/k/, read as /ky/). Each is accepted today with the wrong sound, and
      one that drops or adds a vowel changes which form is shortest.
- [x] Istro-Romanian column re-sourced. 73 of its 213 cells were a
      Daco-Romanian list left in place wherever the Swadesh appendix was
      empty. 8 now carry an attested form, 65 are empty; see
      [`docs/sources_ruo.md`](docs/sources_ruo.md).
- [ ] The same check for the other thin columns. Franco-Provençal, Picard,
      Istriot, Gallo, Piedmontese, Ladin, Emilian, Ligurian, Extremaduran
      and Dalmatian have all 213 cells filled, and under a third of those
      forms (under half for Dalmatian) appear in the lect's own word list.
      That does not show padding, only that the word lists cannot confirm
      the column.

Also decided: **stress** is penultimate by default; a word stressed elsewhere
in its source lect keeps that stress, marked with an accent (`grammar.tex`
§2.5).

After the gate:

- [x] Encode the approved merges at transcription.
- [ ] Encode the spelling map and a reader that handles digraphs.
- [ ] Carry the source's stress through transcription and mark it when it is
      not penultimate. Today stress marks are stripped, and most backends do
      not emit them, so the source of each word's stress has to be decided
      per lect.
- [ ] Rerun prep → Rust SA → join, and refresh the scorecard.
- [ ] Tracked lexicon listing under `docs/lexicon/`, so every later change to
      the foundations shows up as a diff (`data/`, `*.json`, `*.csv`, `*.txt`
      and any `lexicons/` folder are ignored).

## Stage 1. Nouns and adjectives

- [ ] **Fetch.** `scripts/fetch_kaikki_full.py`: every part of speech, with
      form-of rows and IPA, for es, pt, gl, ca, fr, it, ro, lmo into
      `data/sources/kaikki_full/{code}.jsonl`. Fetched once; it also feeds
      the gloss overlay and Bible lemmatisation. Not under `data/words/`:
      `scripts/build_kaikki_corpus.py` globs `kaikki-*.jsonl` there and would
      overwrite the word tables.
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
- [ ] **Personal pronouns, harvested here** rather than in Stage 2: they are
      the only place every daughter still shows case, so the case decision
      below needs their pages.

**Gate G1, nouns.** Endings; the case layer (keep the Latin-derived
nom/acc/gen of the spec, use only what daughters attest, or drop case); how
an indirect object is marked (the spec has no dative); one table or several
classes; neuter or not (Aromanian has neuter nouns); whether a zero ending is
allowed (it contradicts axiom 5 and the stress rule); the junction rule; how
a noun gets its gender; whether adjectives share the table.

- [ ] **Encode** the picks in `vulgultra/morphology_constants.py`; noun
      selection reads that table instead of searching; update `grammar.tex` §3.1–3.3.
- [ ] **Realise** on segment lists (`is_vowel`, `repair`, `count_violations`,
      `to_orthography`), with plural and genitive reachable, gender from the
      lexicon entry, and penultimate stress assigned.

## Stage 2. Closed classes

Same method, one paradigm at a time: personal pronouns by person, number and
role (subject, object, indirect, possessive, reflexive; pages from Stage 1);
demonstratives;
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
licences, the concept-ID spine, the first slice, the alignment method, and
which derived words (adverbs, participles, numerals) are rows of their own.

Known before the gate:

- Concept ids must be project-owned and never reused. A Bible id equal to a
  Swadesh id is merged silently and overwrites its part of speech and gloss
  (`right`, `lie`, `back` are already taken).
- The TSV importer takes the five anchors only; every other lect gets a
  Bible cell only through the gloss overlay. Seven non-anchor lects have
  word lists with no glosses at all (ca, gl, lmo, gsc, pcd, frp, ext), so
  they cannot receive one. Catalan alone supplies 48 of the 213 roots today.
- Selection is not incremental: adding or removing concepts changes roots
  already chosen. Pins (Gate G0) come first.

- [ ] Alignment tooling that turns verse-aligned editions into reviewable
      candidate rows, then writes accepted rows to
      `data/bible/lexicons/{fr,es,pt,it,ro}.tsv`.
- [ ] First slice through `scripts/build_bible_grid.py` → prep → Rust SA → lexicon.
- [ ] Fill path for the other 31 lects, cited forms only (the full Kaikki
      fetch, Apertium bilingual dictionaries under `vendor/`), run before
      selection; the gloss overlay respects part of speech (`vulgultra/pipeline.py`).
- [ ] Homophone count reported with every slice.

**Gate G3b, homophones at scale.** The policy is set at Gate G0; this gate
checks it against the first slice. 196 of 213 roots are one syllable, and a
review estimate puts roughly a tenth of words in a homophone pair at 1,000
concepts under the present policy, and far more when most cells come from a
few lects.

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
clause. Blocked on the verb table: every demo sentence has a verb or the
copula. **Gate G5.**

## Stage 6. Dictionary, texts, primer

- [ ] Tracked dictionary export under `docs/lexicon/` (`data/` is ignored).
- [ ] Sample texts with a coverage report of what cannot yet be produced.
- [ ] Refresh `books/beginners-guide/`.

## Order

```
Stage 0 ──G0──> encode, rerun, tracked listing ──┐
                                                 ├─> Stage 1 ──G1──> encode + realise ──> Stage 2 ──G2──┐
G3a ──> Stage 3 tooling (alongside Stage 1) ─────────────────────────> first slice ──G3b──> Stages 4, 5 ──> Stage 6
```

## Handoffs from the verb work

| Needed | For |
|---|---|
| Final tense/mood and person slot names | lexicon schema, realiser |
| What a verb's lexicon entry is (which attested form is the root; its theme) | Bible verbs in Stage 3 |
| Whether participles decline like adjectives | Stage 1 encode, Stage 4 |
| Reflexive and subject-pronoun conventions | Stage 2 |
| Full copula paradigm | Stage 5 |
| One format for hand-picked tables, nouns and verbs alike (several classes, any number of cells); today both sides hard-code one class | Stage 1 encode |

Shared with the verb work, so changes are announced first: `add_ending` in
`vulgultra/realize.py` joins endings for verbs and nouns alike;
`enumerate_endings`, `ending_catalog` and the Rust output writer handle both
tables together; and `romance_swadesh.py`, `realize.py` and `optimizer.py`
import `PERSONS` and `VERB_TEMPLATES`, so reshaping those stops everything
non-verbal from importing.
