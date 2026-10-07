# Conjugation corpus and linkage EDA

This is the first morphology-only workstream. It is independent of the Bible
lexicon and does not run the Vulgultra optimizer.

The expected corpus schema is `vulgultra.conjugation.v1`. Each paradigm stores
a lect, lemma, source/class label, provenance, and feature rows whose standard
person-number keys are:

```text
1sg, 2sg, 3sg, 1pl, 2pl, 3pl
```

Cells retain both source forms and explicitly segmented phonemes. Missing
cells stay missing. The loader does not copy a sister lect or guess IPA
boundaries from a compact string.

## Current state

`scripts/build_conjugation_pages.py` harvests local Kaikki JSONL into:

- compact lect pages under `docs/conjugations/` (class → ending inventory →
  representative 6-slot grids)
- normalized JSON under `data/conjugation/sources/{lect}.json`

`data/conjugation/source_manifest.json` marks harvested lects; all 36 are
marked today. Sources other than Kaikki come through their own harvesters:
`scripts/harvest_verbix.py` writes `{lect}_verbix.json`, and the per-lect
ones (`harvest_dlm_verbix.py`, `harvest_ist_verbix.py`,
`harvest_ruo_verbix.py`, `harvest_ruq_rvid.py`, `harvest_gallo_frwikt.py`,
`harvest_picard_diseux.py`, `harvest_rgn_templates.py`,
`harvest_ext_recursos.py`) write `{lect}_diseux.json`. The page builder
merges both into `{lect}.json`.

The tracked reports lag the data. [`eval/conjugation_eda.md`](eval/conjugation_eda.md)
was last written with 20 lects. [`conjugations/gsc.md`](conjugations/gsc.md)
and the index say Gascon has no source, while
`data/conjugation/sources/gsc.json` holds 100 paradigms from Verbix. The
commands below rewrite both.

Orthographic ending inventories live in each JSON file's
`metadata.ending_inventories`. Candidate phoneme links need explicit
`phonemes` lists; harvested rows currently leave those empty on purpose.

## Commands

Rebuild pages + JSON corpus:

```bash
.venv/bin/python3 scripts/build_conjugation_pages.py
```

EDA on the harvested corpus:

```bash
.venv/bin/python3 scripts/conjugation_eda.py \
  --input data/conjugation/sources \
  --output data/eda/conjugation_eda.json \
  --normalized-output data/eda/conjugation_normalized.json \
  --markdown-output docs/eval/conjugation_eda.md \
  --comparison-output docs/eval/conjugation_comparison.md
```

Bootstrap fixture from hand templates (not sourced evidence):

```bash
.venv/bin/python3 scripts/conjugation_eda.py \
  --from-templates \
  --output /tmp/conjugation_eda.json \
  --normalized-output /tmp/conjugation_seed.json \
  --markdown-output /tmp/conjugation_eda.md \
  --comparison-output docs/eval/conjugation_comparison.md
```

## Link analysis

The EDA compares the same six-slot person-number position across tense/mood
rows and records candidate shared suffixes. It also reports cautious shared
prefix candidates within a tense row. These are evidence records, not asserted
morpheme boundaries. Later optimization may enforce high-confidence links;
this phase only makes them inspectable.
