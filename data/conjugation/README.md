# Romance conjugation corpus

Sourced, normalized conjugation paradigms for morphology EDA. Independent of
the Bible lexicon and of the optimizer.

## Layout

- `sources/{lect}.json` — `vulgultra.conjugation.v1` harvest from local Kaikki
  JSONL (and similar). Built by `scripts/build_conjugation_pages.py`.
- `source_manifest.json` — per-lect collection status.
- Human-readable class pages: `docs/conjugations/{lect}.md`.

## Schema

```json
{
  "schema": "vulgultra.conjugation.v1",
  "metadata": {
    "lect": "ast",
    "ending_inventories": {
      "ast-conj-ar": {
        "indicative.present": {
          "endings": {"1sg": "o", "2sg": "es", "3sg": "a", "1pl": "amos", "2pl": "áis", "3pl": "en"},
          "support": 776,
          "stem_mode": "template"
        }
      }
    }
  },
  "paradigms": [
    {
      "lect": "ast",
      "lemma": "abandonar",
      "class_source": "ast-conj-ar",
      "source": {"attested": true, "url": "...", "stem": "abandon"},
      "cells": {
        "indicative.present": {
          "1sg": {"form": "abandono", "phonemes": [], "ipa": "..."}
        }
      }
    }
  ]
}
```

Person keys are always `1sg`, `2sg`, `3sg`, `1pl`, `2pl`, `3pl`. Missing cells
stay absent. `phonemes` stay empty until an explicit segmentation is supplied;
the EDA does not split compact IPA.

Class labels are lect-internal (`ast-conj-ar`, `scn-conj-*`, …). They are not
aligned across lects.

## Fetch Kaikki verb lemmas

```bash
.venv/bin/python3 scripts/fetch_kaikki_verbs.py es pt gl ca fr it ro lmo eml
```

Streams Kaikki dumps and keeps **lemma rows with conjugation `forms`** only
(full dumps are huge form-of noise).

## Verbix fill

```bash
.venv/bin/python3 scripts/harvest_verbix.py es pt an gsc frp --limit 120
```

Writes `sources/{lect}_verbix.json` and caches under `data/sources/verbix/`.
CC BY-NC 3.0; cite [Verbix](https://www.verbix.com). Gascon uses Verbix’s
Occitan engine (`oci`) under lect code `gsc`.

Picard (`pcd`) comes from Chés Diseux d'Achteure:

```bash
.venv/bin/python3 scripts/harvest_picard_diseux.py
```

Istro-Romanian (`ruo`) from Verbix docs + scanned notes:

```bash
.venv/bin/python3 scripts/harvest_ruo_verbix.py
```

Megleno-Romanian (`ruq`) from Capidan 1925 + RVID 2.0:

```bash
.venv/bin/python3 scripts/harvest_ruq_rvid.py
```


## Rebuild

```bash
.venv/bin/python3 scripts/build_conjugation_pages.py

.venv/bin/python3 scripts/conjugation_eda.py \
  --input data/conjugation/sources \
  --output data/eda/conjugation_eda.json \
  --normalized-output data/eda/conjugation_normalized.json \
  --markdown-output docs/eval/conjugation_eda.md \
  --comparison-output docs/eval/conjugation_comparison.md
```

Bootstrap ending templates (not sourced evidence):

```bash
.venv/bin/python3 scripts/conjugation_eda.py \
  --from-templates \
  --normalized-output data/eda/conjugation_templates_seed.json
```
