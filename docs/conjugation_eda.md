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

`data/conjugation/source_manifest.json` tracks the 36 expected lects. They are
currently marked `pending`: the repository's existing `VERB_TEMPLATES` are
available only as a bootstrap ending fixture, not as collected full
conjugation evidence.

The fixture can exercise the complete schema and report path:

```bash
.venv/bin/python3 scripts/conjugation_eda.py \
  --from-templates \
  --output /tmp/conjugation_eda.json \
  --normalized-output /tmp/conjugation_seed.json \
  --markdown-output /tmp/conjugation_eda.md
```

Real source files can be supplied as one JSON file or a directory of JSON
files:

```bash
.venv/bin/python3 scripts/conjugation_eda.py \
  --input data/conjugation/sources \
  --output data/eda/conjugation_eda.json \
  --normalized-output data/eda/conjugation_normalized.json \
  --markdown-output docs/eval/conjugation_eda.md
```

## Link analysis

The EDA compares the same six-slot person-number position across tense/mood
rows and records candidate shared suffixes. It also reports cautious shared
prefix candidates within a tense row. These are evidence records, not asserted
morpheme boundaries. Later optimization may enforce high-confidence links;
this phase only makes them inspectable.
