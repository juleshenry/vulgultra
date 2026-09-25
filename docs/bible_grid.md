# Bible-anchored Romance grid

The main lexicon is a meaning grid, not a cognate detector. A row is one
concept/sense; the 36 Romance lects are columns. French `chien`, Italian
`cane`, Romanian `câine`, Portuguese `cão`, and Spanish `perro` can therefore
occupy the same `dog` row without being treated as one etymological family.

## Data flow

1. Start with the five anchor lexicons: French, Spanish, Portuguese, Italian,
   and Romanian. Their forms must be aligned to stable `concept_id`s, with
   edition, license, and Bible verse references recorded.
2. Compile those files with `scripts/build_bible_grid.py`.
3. Add direct or nearest-equivalent forms from other lects in the same grid.
   An unknown cell stays unknown; a genuine lexical gap is not inferred from
   missing data. `nearest_equivalent` and `attested_phrase` must be explicit
   and cited, not machine-guessed from spelling.
4. Prep transcribes every grid form to IPA, derives its working segment
   inventory from those forms, removes illegal candidates, and retains only
   each concept's minimum-syllable candidates.
5. Simulated annealing can choose only within those minimum-syllable ties. It
   maximizes the distinct observed segment inventory, then lect coverage,
   then cross-lect same-stem/morpheme support.

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

```sh
python3 scripts/build_bible_grid.py
python3 -m vulgultra.pipeline prep --bible-grid data/bible/concept_grid.json
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
