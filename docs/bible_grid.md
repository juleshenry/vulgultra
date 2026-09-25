# Bible-anchored Romance grid

The main lexicon is a meaning grid, not a cognate detector. A row is one
concept/sense; the 36 Romance lects are columns. French `chien`, Italian
`cane`, Romanian `câine`, Portuguese `cão`, and Spanish `perro` can therefore
occupy the same `dog` row without being treated as one etymological family.

## Data flow

1. Obtain five licensed/allowed anchor lexicons: French, Spanish, Portuguese,
   Italian, and Romanian. The repository does not download Bible text or
   silently extract word meanings. Their forms must be aligned to stable
   `concept_id`s, with edition, license, and Bible verse references recorded.
2. Put them at `data/bible/lexicons/{fr,es,pt,it,ro}.tsv` and compile those
   files with `scripts/build_bible_grid.py`.
3. Add direct or nearest-equivalent forms from other lects in the same grid.
   An unknown cell stays unknown; a genuine lexical gap is not inferred from
   missing data. `nearest_equivalent` and `attested_phrase` must be explicit
   and cited, not machine-guessed from spelling.
4. Prep merges the Bible grid with the 36-lect meaning grid, transcribes every
   occupied form to IPA, derives its working segment
   inventory from those forms, removes illegal candidates, and retains only
   each concept's minimum-syllable candidates.
5. Simulated annealing can choose only within those minimum-syllable ties. It
   maximizes the distinct observed root segment inventory; morphology is then
   selected from attested tables plus productive grid-inventory endings.

## Import format

Provide one UTF-8 TSV per anchor language at
`data/bible/lexicons/{fr,es,pt,it,ro}.tsv`. Required columns:

```text
concept_id  gloss_en  pos  form  edition  license  verse_refs
```

`relation` is optional (`direct`, `nearest_equivalent`, or
`attested_phrase`); `source_url` is optional. Separate multiple verse
references with semicolons. Multiple rows may express real lexical
alternatives for one concept and lect. The builder rejects inconsistent
edition/license metadata within a language file.

Use `pos=proper_noun` (or `character`) for names. These rows remain in the
grid and candidate shortlist, but realization keeps the winning name
invariant rather than applying noun case/number endings.

```sh
python3 scripts/build_bible_grid.py
python3 -m vulgultra.pipeline prep --bible-grid data/bible/concept_grid.json
```

For the complete prep → Rust SA → report flow, use one command after the TSVs
exist:

```sh
python3 scripts/run_vulgultra.py --bible-input-dir data/bible/lexicons
```

That command performs the following deterministic chain:

```text
five TSV lexicons
    → data/bible/concept_grid.json
    → 36-lect grid + Bible rows
    → IPA candidates + minimum-σ shortlist
    → Rust root annealing + ending selection
    → data/vulgultra_lexicon.json
    → docs/eval/34_romance_scorecard.md
```

The generated JSON contains only lexicon forms and references, not Bible
verse text. The verse-aligned [BibleNLP/eBible corpus](https://github.com/BibleNLP/ebible)
is a candidate source: its translations align to canonical book/chapter/verse
references, and translation-level licensing must be retained. Verse alignment
is useful evidence and context, but it does not itself identify which word in
one verse translates which word in another. The lexical concept alignment
must remain reviewable.

The repository currently has no imported Bible editions/lexicons. Until those
are supplied, the grid-default pipeline uses the existing 36-lect core grid;
it does not claim Bible coverage for an unfilled cell.
