# Roadmap

Vulgultra is built class by class, in the order below, and the lexicon comes
last because every word in it needs the classes before it: a letter for each
of its sounds, endings to take, small words to stand beside. The order was
set on 7 October 2026.

Verb conjugation is built by hand (harvest → per-lect pages → shortlist →
manual picks) and its files are not touched from this roadmap; everything
else is. Canonical spec stays [`docs/grammar/grammar.tex`](docs/grammar/grammar.tex).
A step changes the spec only after its gate. The decisions each gate needs
are queued, step by step, in [`docs/decisions.md`](docs/decisions.md).

## The order

| Step | What | Harvested | Picked | Waits on |
|---:|---|---|---|---|
| 0 | Spelling, and choosing among equally short forms | the evidence is in | nothing | two decisions |
| 1 | Verbs | per-lect pages and a shortlist | by hand, outside this roadmap | — |
| 2 | Small words: prepositions, conjunctions, pronouns, articles | 162 meanings in all 36 lects | nothing | the case decision; person labels from the verbs |
| 3 | Nouns and adjectives | plural patterns only | nothing | a harvest that is not built yet |
| 4 | Numerals | 23 meanings in all 36 lects | nothing | step 3, for the ordinals |
| 5 | Proper nouns | nothing | nothing | a rule for where a name's form comes from |
| 6 | Lexicon, the Bible first | 8,069 Bible words, with candidate forms in every lect | nothing | steps 0 to 5 |

After the lexicon: derivation, syntax, then a dictionary, texts and the
primer.

```
0 spelling ──┐
1 verbs ─────┼─> 2 small words ──> 3 nouns, adjectives ──> 4 numerals ──> 5 proper nouns ──> 6 lexicon ──> derivation, syntax, texts
```

Steps 0 and 1 run side by side. Sourcing for step 6 was done ahead of its
turn (5 and 6 October) and is finished for now; selection has not started.

## Method (every class)

Each grammatical class goes through the same four steps as the verbs. Nothing
grammatical is selected automatically.

1. **Harvest.** Attested forms per lect, with source.
2. **Pages.** One comparison page per lect under `docs/<class>/`.
3. **Cross-lect minimal shortlist.** For each cell or meaning, every attested
   candidate ranked by phonemic syllables, with lect support and the
   collisions a choice would create.
4. **Manual pick.** The choice is made by hand at the step's gate, then encoded
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
  only in a step's encode stage, after its gate.
- **Work is committed on `main`.** No branch per step.
- **Axioms hold.** Daughters only, attested only, no padding a thin lect from
  a sister. A lect with no data for a class gets an empty page.
- **Sources.** Open sources are fetched as needed. Never scraped: Pledari,
  DRG, TalkBank, Verbix site-wide, vlaski-zejanski. A text whose licence is
  not settled stays under `data/` and is never committed. Reading scanned
  pages by eye costs usage and is asked first.

## What the code does today

| Area | State |
|---|---|
| Spelling | 62 sounds are in use among the shortlisted forms; 39 have no letter and print in `⟨IPA⟩` brackets. |
| Roots | 213 Swadesh meanings, Σσ 224, all under the ignored `data/` folder. Not stable: another random seed changes 138 of them. |
| Noun table | One 12-ending table from the spec (`grammar.tex` §3.1), chosen as a block by the optimizer. No per-noun gender, stem or class. |
| Noun realisation | `vulgultra/realize.py` only produces singulars, assigns case by word position, and takes gender from a 25-noun hand list (everything else is masculine). |
| Root + ending junction | Endings are glued onto spelling strings with an ASCII vowel test. Every noun ending starts with a vowel, and many roots end in one. |
| Small words in code | Six subject pronouns, numerals 1–5, three prepositions, three conjunctions, `o/a/os/as`, a present-only copula. No object or possessive pronouns, no `ke`. |
| Proper nouns | None. |
| Syntax | One paragraph in the spec (`grammar.tex` ch. 5). |

## Step 0. Spelling, and choosing among equally short forms

Nothing picked in any later step can be written down, or stay picked, until
these two are settled. The transcription and the sound inventory are already
decided and in code (the record is at the end of this file).

**Gate G0** (decisions 0.1 and 0.2):

1. **Spelling.** Per sound, a letter, a digraph or a diacritic, or leave it
   in brackets. Evidence and a proposal per sound:
   [`docs/eval/orthography_gaps.md`](docs/eval/orthography_gaps.md).
2. **Selection among ties.** 114 of the 213 meanings have several equally
   short candidates and nothing ranks them. What replaces chance, whether a
   homophone costs anything, and whether an approved root is pinned so that
   growing the lexicon cannot change it.

After the gate:

- [ ] Encode the spelling map and a reader that handles digraphs.
- [ ] Carry the source's stress through transcription and mark it when it is
      not penultimate. Today stress marks are stripped, and most readers do
      not emit them, so the source of each word's stress has to be decided
      per lect.
- [ ] Rerun prep → Rust SA → join, and refresh the scorecard (last run
      2026-10-05, before the gate).
- [ ] Tracked lexicon listing under `docs/lexicon/`, so every later change
      shows up as a diff (`data/` is ignored).

Loose ends in the readers, none of which blocks the gate: ten grid forms are
still rejected (nine have an apostrophe, one a letter no source explains);
Istro-Romanian *c* and its central vowel are not ruled; the Venetan,
Istro-Romanian and Gallo columns mix spellings; Norman and Ladino may still
hold some French and Spanish.

## Step 1. Verbs

Built by hand, outside this roadmap. The harvest, one page per lect
([`docs/conjugations/`](docs/conjugations/)) and the shortlist
(`docs/eval/verb_ending_candidates.html`) exist; the picks are being made.

What the later steps need from it:

| Needed | For |
|---|---|
| Final tense/mood and person slot names | lexicon schema, realiser |
| Reflexive and subject-pronoun conventions; whether the subject pronoun can be dropped | step 2 |
| Whether participles decline like adjectives | step 3, derivation |
| One format for hand-picked tables, nouns and verbs alike (several classes, any number of cells); today both sides hard-code one class | step 3 |
| What a verb's lexicon entry is (which attested form is the root; its theme) | Bible verbs in step 6 |
| Full copula paradigm | syntax |

Shared with the verb work, so changes are announced first: `add_ending` in
`vulgultra/realize.py` joins endings for verbs and nouns alike;
`enumerate_endings`, `ending_catalog` and the Rust output writer handle both
tables together; and `romance_swadesh.py`, `realize.py` and `optimizer.py`
import `PERSONS` and `VERB_TEMPLATES`, so reshaping those stops everything
non-verbal from importing.

## Step 2. Small words

Prepositions, conjunctions, personal pronouns by person and role (subject,
object, indirect, possessive, reflexive), articles, demonstratives,
interrogatives and the relative, quantifiers, and the small adverbs (yes,
not, also, only, very, more, already, still). One paradigm at a time.

- [x] Harvest (`scripts/build_building_blocks.py`): one page per lect, all 36,
      under [`docs/building_blocks/`](docs/building_blocks/README.md), and the
      shortest attested forms for each of 162 meanings in
      [`docs/eval/building_block_candidates.md`](docs/eval/building_block_candidates.md).
- [ ] A form is matched on any sense of its entry, so a secondary sense puts
      it in a row where it is not the plain word (French *à* and *en* under
      *of*).
- [ ] The pronoun and article tables are sorted by the dictionary's wording
      and are noisy (Spanish *ellos* is missing from its row; neologisms
      appear). They need sorting into clean paradigms.
- [ ] The shortlist does not show collisions yet: every clash of a candidate
      with an existing root, ending, article or copula form (today `o`
      water/article, `e` wing/copula, `a` at/article).

**Gate G2** (decisions 2.1 to 2.7). First whether a noun or pronoun changes by
role: if nouns have no case, prepositions do that work, as in every daughter;
if they keep one, each preposition needs a case to govern. Then articles
(both, one or none), then the words themselves, each paradigm picked by hand.

- [ ] **Encode** the picks in a `*_constants.py` table; update `grammar.tex`.

## Step 3. Nouns and adjectives

- [x] Every word class fetched for the eight large lects whose extract held
      only verbs (`scripts/fetch_kaikki_full.py`, into
      `data/sources/kaikki_full/`).
- [x] Plural patterns by gender, tallied per lect
      ([`docs/eval/plural_formation.md`](docs/eval/plural_formation.md)).
- [ ] **Harvest.** `vulgultra/declension_harvest.py`: gender, the four
      gender × number forms, plural-formation classes, adjective feminine and
      plural, and for Romanian and Aromanian the surviving case and definite
      forms. Apertium `.dix` paradigms under `vendor/` as a second source.
      Output `data/declension/sources/{lect}.json` (`vulgultra.declension.v1`).
- [ ] **Pages.** `scripts/build_declension_pages.py` → `docs/declensions/{lect}.md`.
- [ ] **Shortlist.** `scripts/noun_ending_candidates.py` →
      `docs/eval/noun_ending_candidates.html`. Also marks, for each of the
      spec's 12 cells, whether any daughter attests it.
- [ ] **Junction table.** What hiatus, a glide, dropping the root's final
      vowel, or a linking consonant each do to syllable count and homophones.

**Gate G3** (decisions 3.1 and 3.2, and the endings once the shortlist
exists). How the plural is formed; two genders or three (Aromanian and
Romanian have a neuter); one table or several classes; whether a zero ending
is allowed (it contradicts axiom 5 and the stress rule); the junction rule;
how a noun gets its gender; whether adjectives share the table. The case
question is settled at step 2.

- [ ] **Encode** the picks in `vulgultra/morphology_constants.py`; noun
      selection reads that table instead of searching; update `grammar.tex` §3.1–3.3.
- [ ] **Realise** on segment lists (`is_vowel`, `repair`, `count_violations`,
      `to_orthography`), with the plural reachable, gender from the lexicon
      entry, and penultimate stress assigned. `gender`, `decl_class` and
      `stem` are joined onto roots the way `gloss_en` and `pos` are today
      (`vulgultra/lexicon_fields.py`).

## Step 4. Numerals

- [x] Harvested with the small words: zero to twelve, the tens to fifty,
      hundred, thousand, first to third, half, in all 36 lects
      ([`docs/eval/building_block_candidates.md`](docs/eval/building_block_candidates.md),
      *Numerals*).
- [ ] The rest of the tens, and how each daughter builds the numbers above
      ten (a fused word, or ten-and-one).
- [ ] The Bible's own numerals: 69 of its 8,069 words are numerals, many of
      them ordinals and distributives (*quinquagenus*, fifty each).

**Gate G4** (decision 4.1). One to ten, the tens, hundred, thousand; the rule
for building the numbers between; whether ordinals are words of their own or
built, and that they inflect like the adjectives of step 3.

## Step 5. Proper nouns

Not started, and absent from every earlier plan. The Vulgate has about 4,000
name forms that are no dictionary word (*Israel*, *David*, *Ierusalem*,
*Iesus, Iesu, Iesum*): 29,500 words of running text, one in twenty. About a
hundred more are in the dictionary as words (*Aegyptus*, *Iudaeus*,
*Galilaeus*). The dictionary fetches so far left names out on purpose.

- [ ] **Names table.** Bring the Vulgate's name forms to one entry each, with
      counts (*Moyses, Moysen, Moysi* are one name).
- [ ] **Harvest.** Each name as the five modern Bibles and the lects' own
      Bible texts write it (`scripts/align_bible.py` already pairs a Latin
      word it cannot trace with the word that looks like it), and
      Wiktionary's proper-noun entries as a second source.
- [ ] **Pages and shortlist**, like any class.

**Gate G5** (decisions 5.1 and 5.2). Where a name's form comes from: the
daughters, like any other word, or one fixed source adapted by rule. Whether
a name inflects. What happens to a sound the inventory lacks.

## Step 6. Lexicon, the Bible first

Sourcing, done:

- [x] Six Bibles on disk, one verse per row (`scripts/fetch_bible_texts.py`,
      [`docs/bible_sources.md`](docs/bible_sources.md)): the Clementine
      Vulgate, Segond 1910, Reina-Valera 1909, Bíblia Livre, Riveduta 1927
      and Cornilescu. The Romanian licence is not settled; the text is local
      only.
- [x] Latin as the word list (decision 6.1, to confirm): the Vulgate's
      612,000 words traced to 8,069 dictionary words, each with the daughter
      forms Wiktionary lists as its reflexes (`scripts/build_bible_lexicon.py`,
      [`docs/eval/bible_lexicon.md`](docs/eval/bible_lexicon.md)).
- [x] The five modern Bibles aligned to the Latin verse by verse
      (`scripts/align_bible.py anchors`,
      [`docs/eval/bible_anchor_words.md`](docs/eval/bible_anchor_words.md)):
      about 3,700 Latin words get the word each Bible uses for them.
- [x] Every lect has a form for 2,000 or more of the 8,069 words
      (`scripts/bible_coverage.py`,
      [`docs/eval/bible_coverage.md`](docs/eval/bible_coverage.md)), from
      translation tables, the lects' own Wiktionaries and Bible texts, and
      some forty dictionaries and glossaries
      ([`docs/sources_bible_lexicon.md`](docs/sources_bible_lexicon.md)).
      29 lects have 2,000 firm; the weakest are Istro-Romanian (619 firm),
      Megleno-Romanian (737) and Emilian (1,222).

Selection, not started:

- [ ] Check the gloss and two-step candidates by sense before they compete
      for a root.
- [ ] From the pool to the optimizer. Each Bible word becomes a row whose
      cells are the pool's forms (`data/bible/lexicon/forms/{lect}.tsv`). The
      importer on disk (`scripts/build_bible_grid.py`) takes five hand-made
      spreadsheets for the anchors only and has to be replaced. Row ids must
      be project-owned and never reused: an id equal to a Swadesh id is
      merged silently and overwrites its part of speech and gloss (`right`,
      `lie`, `back` are already taken).
- [ ] Pins. Selection is not incremental: adding words changes roots already
      chosen (decision 0.2).
- [ ] First slice: the commonest words that are not small words, numerals or
      names, through prep → Rust SA → join. The homophone count is reported
      with every slice.
- [ ] Verb entries wait on what a verb's lexicon entry is (step 1).
- [ ] The page readings still open for the thinnest lects, if wanted
      (decision 6.5; the list is in `docs/sources_bible_lexicon.md`).

**Gate G6, homophones at scale.** The policy is set at Gate G0; this gate
checks it against the first slice. 202 of the 213 roots are one syllable, and
a review estimate puts roughly a tenth of words in a homophone pair at 1,000
meanings under the present policy, and far more when most cells come from a
few lects.

After the Bible, a second word list for the anchors if one is wanted: the
Intercontinental Dictionary Series and NorthEuraLex (both on lexibank, CC-BY)
give about 1,300 and 1,000 meanings for French, Spanish, Portuguese, Italian,
Romanian and Catalan.

## After the lexicon

- **Derivation.** Adverb formation, comparison, participles used as
  adjectives, numeral composition if step 4 left any, nominalised
  infinitives, by the same method. Kept small: morpheme uniformity is not a
  goal, so each meaning keeps its own shortest attested form.
- **Syntax.** Expand `grammar.tex` ch. 5 into a specification: noun-phrase
  order, how roles are marked, negation, questions, `ke` clauses, pronoun
  placement, coordination, comparison, possession. Sentence realisation takes
  role-labelled input instead of going by word position. Needs the verb table:
  every demo sentence has a verb or the copula.
- **Dictionary, texts, primer.** A tracked dictionary export under
  `docs/lexicon/`; sample texts with a report of what cannot yet be produced;
  a refreshed `books/beginners-guide/`.

## Record: the foundations, to 5 October 2026

Kept as written at the time; a later entry supersedes an earlier figure.
Decided at Gate G0 and in code: the transcription is fixed first, and the
inventory has eleven merges, each with its ground, in `grammar.tex` §2.4
(`SEGMENT_MERGES`, `LECT_MERGES`). All four rhotics are kept, /x/ is kept,
and so is everything else some daughter uses to tell words apart.

- [x] Candidates keep their concept's part of speech (was `verb` on every root).
- [x] Tests that pin today's noun, adjective and sentence realisation
      (`vulgultra/test_realize.py`).
- [x] Orthography evidence: [`docs/eval/orthography_gaps.md`](docs/eval/orthography_gaps.md),
      from `scripts/orthography_gaps.py`.
- [x] `gloss_en` and `pos` joined onto roots after the optimizer
      (`vulgultra/lexicon_fields.py`, no Rust change). `gender`, `decl_class`
      and `stem` use the same join once step 3 produces them.
- [x] Encode the approved merges at transcription.

The first evidence run (September), which set the gate's questions:

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

Transcription and sourcing of the Swadesh grid:

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
