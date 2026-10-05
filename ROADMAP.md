# Roadmap: everything except verb conjugation

Verb conjugation is being built by hand (harvest → per-lect pages → shortlist
→ manual picks). This roadmap covers the rest of the language so it can move
in parallel: noun and adjective declension, closed classes, the lexicon,
syntax, and the first real texts.

Canonical spec stays [`docs/grammar/grammar.tex`](docs/grammar/grammar.tex).
A stage changes the spec only after its gate.

## Goal and order (stated 2026-10-05)

The goal is a lexicon at the level of the Bible, annealed word by word. The
213-meaning Swadesh grid is an illustration and a test bed for the readers
and the optimizer, not the product: no more work goes into polishing its
columns for their own sake.

First come the building blocks every sentence needs, picked by hand from
what the daughters attest: personal pronouns, possessives, articles and
demonstratives, interrogatives, quantifiers, numerals, prepositions,
conjunctions, the small adverbs, and how a noun forms its plural. Then the
Bible lexicon.

- [x] First harvest of the building blocks, from the Wiktionary extracts on
      disk (`scripts/build_building_blocks.py`): one page per lect under
      [`docs/building_blocks/`](docs/building_blocks/README.md), the
      shortest attested forms for each of 162 meanings in
      [`docs/eval/building_block_candidates.md`](docs/eval/building_block_candidates.md),
      and plural patterns by gender in
      [`docs/eval/plural_formation.md`](docs/eval/plural_formation.md).
      29 lects have a page. For Spanish, Portuguese, Galician, Catalan,
      French, Italian, Romanian and Lombard the extract on disk held only
      verbs, so every other word class was fetched into
      `data/sources/kaikki_full/` (`scripts/fetch_kaikki_full.py`).
- [ ] Seven lects have no page. Gallo is glossed in French; Extremaduran,
      Gascon, Picard, Franco-Provençal, Istro-Romanian and Megleno-Romanian
      have no English-glossed extract. The French Wiktionary dump in `xmls/`
      has French-glossed entries for Gallo, Picard, Franco-Provençal and
      Gascon; the others need their own sources (Carmona García, the
      Wiktionary lists).
- [ ] A form is matched on any sense of its entry, so a secondary sense
      puts it in a row where it is not the plain word (French *à* and *en*
      under *of*).
- [ ] Object, indirect and reflexive pronouns, and gender and number of
      articles and possessives, are listed under one English gloss today
      (*you*, *the*); the pages show the dictionary's wording but do not
      sort the forms into a paradigm yet.

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
- [ ] Ten forms are still rejected. Nine contain an apostrophe (`s'assêre`,
      `p'tit`, `ch'la`) and need a different citation form in the grid, not
      a reading; one has a letter no source explains (Emilian `źnòć`).
- [x] Rulings on letters read with the wrong sound, each with its source in
      the same file: Walloon *xh* is ʃ (the Walloon Wiktionary's standard
      pronunciation), Aromanian *nj* is ɲ, Occitan and Gascon *qu* is k,
      Bolognese *z, ż* are θ, ð, Piedmontese *o, u* are u, y.
- [ ] Not ruled: Istro-Romanian *c* and its central vowel, because the
      column mixes two spellings.
- [x] Istro-Romanian column re-sourced. 73 of its 213 cells were a
      Daco-Romanian list left in place wherever the Swadesh appendix was
      empty. 8 now carry an attested form, 65 are empty; see
      [`docs/sources_ruo.md`](docs/sources_ruo.md).
- [x] Six more columns re-sourced against Wiktionary's Swadesh lists
      (`scripts/audit_grid_sources.py`; what changed is in
      [`docs/sources_grid.md`](docs/sources_grid.md)). Istriot and Dalmatian
      held invented forms: 173 and 123 of their 213 cells were respelled,
      replaced or emptied. Ligurian, Emilian and Piedmontese had 124, 150
      and 62 cells respelled or replaced; Ladin 9.
- [x] More sources: Saenko 2015 and IE-CoR (scholarly Swadesh lists with
      spelling, transcription and stress), the vendored Apertium bilingual
      dictionaries, Stich 2001 for Franco-Provençal, the minority-lect
      entries of the local Wiktionary dumps, and two PDF dictionaries. The
      audit reports on all 36 columns
      ([`docs/eval/grid_sources.md`](docs/eval/grid_sources.md)).
      Franco-Provençal is re-sourced from Stich; Gascon went from no source
      to 136 confirmed cells.
- [x] **Picard, Mirandese and Gallo were padded from French and Portuguese**
      (100, 90 and 89 of their unconfirmed cells were the sister's form). No
      Swadesh list exists for them, so the three columns were picked by hand
      from one reference source each and are verified cell by cell by the
      audit: Mirandese from the Portuguese Wiktionary's Mirandese entries and
      the Mirandese Wikipedia (200 cells, 13 empty); Picard from the Chés
      Diseux word list of the Amiens area (192 cells, 21 empty); Gallo from
      the French Wiktionary's entries and Ricaud's lexicon (157 cells, 56
      empty). The record is in [`docs/sources_grid.md`](docs/sources_grid.md).
- [x] **Walloon** held the word for cat in its *dog* cell and French in
      another dozen. The column was picked again in the unified spelling
      from the Walloon Wiktionary (26,000 headwords with translations) and
      the Walloon Wikipedia: 120 cells stand, 93 are replaced, none is empty,
      all 213 verified by the audit
      ([`docs/sources_grid.md`](docs/sources_grid.md), fifth pass).
- [ ] Norman and Ladino show the padding signature more weakly (42 and 48
      cells). Ladin, Lombard, Romansh, Sardinian, Extremaduran and Venetan
      have many unconfirmed cells that are not the sister's form: spelling
      or variety, to be settled per lect.
- [x] Saenko's and IE-CoR's transcriptions are the yardstick, not the
      reader. `scripts/reader_check.py` compares the pipeline's reading of
      every grid form they also have
      ([`docs/eval/readers.md`](docs/eval/readers.md)). Feeding the scholarly
      transcriptions in directly was rejected: they cover half the grid, in
      two notations, and often another variety than the column's.
- [x] **Every lect is read by the reader that measures best**
      ([`docs/sources_orthography.md`](docs/sources_orthography.md)).
      Epitran's borrowed maps read 56% of French and 13% of Portuguese words
      with the right sounds, and had faults of the same kind in every
      family. Now: an espeak-ng voice for French, Spanish, Italian,
      Portuguese, Catalan and Aragonese (and, after respelling, Picard and
      Mirandese); rules of its own for Walloon; Epitran for the rest, with
      each lect's own letters read first and each map's faults mended.
      Syllable counts agree with the scholarly transcriptions in 99% of
      1,492 cells (97% before) and every sound in 79% (62%). Spanish is read
      as Castilian (θ, ʎ), Catalan as Central Catalan.
- [x] The three faults listed on 2026-10-05 are fixed: Romansh *tg, gl, ch*
      (47 of 47 checked cells now have the right syllable count), Romanian
      final *-i* (the reader is told the part of speech: *ochi* is one
      syllable, *muri* two), and the stray final vowel of the French map.
- [x] The gloss overlay no longer fills a cell the curated grid leaves
      empty. It had put 51 forms back, most of them the wrong sense or part
      of speech (Corsican *cravatta*, a necktie, for the verb *tie*;
      Mirandese *mintira*, a lie, for *lie down*). It now applies only to
      concepts added by a Bible grid, and respects part of speech there.
- [x] Prep → Rust SA → join rerun on 2026-10-05 with all of the above (the
      September files are in `data/backups/2026-10-05/`): 213 roots, Σσ 224
      (230 before). **The roots are not stable yet.** 114 concepts have more
      than one shortest candidate and nothing ranks them, so the annealer
      picks among equals at random: the same candidates with seed 43 instead
      of 42 give 138 different roots of 213, at the same Σσ. 168 roots
      differ from September's. This is the tie-break decision of Gate G0,
      now with a measured cost.
- [ ] Still read wrongly, listed in `docs/sources_orthography.md`: forms
      with an apostrophe (Norman *p'tit, t'nin*), the mixed spellings of the
      Venetan, Istro-Romanian and Gallo columns, and stress, which no reader
      carries into the pipeline although espeak-ng and the Walloon
      Wiktionary mark it.
- [ ] The readers added sounds the spelling map has no letter for: 62
      segments are in the shortlist, 39 unspelled (57 and 34 before). New:
      Romansh t͡ɕ, Friulian c and ɟ, Romanian kʲ and t͡sʲ, Castilian and
      Bolognese θ. Each has a row in
      [`docs/eval/orthography_gaps.md`](docs/eval/orthography_gaps.md).

After the gate:

- [x] Encode the approved merges at transcription.
- [ ] Encode the spelling map and a reader that handles digraphs.
- [ ] Carry the source's stress through transcription and mark it when it is
      not penultimate. Today stress marks are stripped, and most backends do
      not emit them, so the source of each word's stress has to be decided
      per lect.
- [ ] Rerun prep → Rust SA → join, and refresh the scorecard (last run
      2026-10-05, before the gate).
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

- [x] Six Bibles on disk, one verse per row (`scripts/fetch_bible_texts.py`,
      [`docs/bible_sources.md`](docs/bible_sources.md)): the Clementine
      Vulgate, Segond 1910, Reina-Valera 1909, Bíblia Livre, Riveduta 1927
      and Cornilescu. The Romanian licence is not settled; the text is
      local only. 30,261 verse keys are shared by all six, but the Vulgate
      numbers the Psalms one behind, and no mapping table exists yet.
- [x] Latin as the word list (proposed 2026-10-05, to confirm): the
      Vulgate's 612,000 words traced to 8,134 dictionary words, each with
      the daughter forms Wiktionary lists as its reflexes
      (`scripts/fetch_latin_descendants.py`, `scripts/build_bible_lexicon.py`,
      [`docs/eval/bible_lexicon.md`](docs/eval/bible_lexicon.md)). 5,209
      have a reflex in at least one lect, 1,400 in ten or more.
- [ ] The decisions this opens are queued in order in
      [`docs/decisions.md`](docs/decisions.md).

**Gate G3a, sourcing (before any download).** The five editions and their
licences, the concept-ID spine, the first slice, the alignment method, and
which derived words (adverbs, participles, numerals) are rows of their own.

A possible spine and second lexicon for the anchors: the Intercontinental
Dictionary Series and NorthEuraLex (both on lexibank, CC-BY) give about 1,300
and 1,000 concepts for French, Spanish, Portuguese, Italian, Romanian and
Catalan, keyed to Concepticon ids.

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
