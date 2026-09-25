# Local source manifest

Large local inputs live under `data/sources/` rather than the repository root.
They are ignored binary/snapshot inputs, while the derived word tables retain
source tags and the scripts below make the transformations reproducible.

| Path | Role | Consumer | Provenance |
|---|---|---|---|
| `data/sources/pdf/Cantemir_Thesis_Final_Draft-converted.pdf` | Istro-Romanian thesis appendix | `scripts/build_ruo_cantemir.py` | Cantemir 2020; see `sources_ruo.md` |
| `data/sources/pdf/oscec-diccionario-castellano-extremec3b1o-ismael-carmona-garcc3ada.pdf` | Extremaduran dictionary | `scripts/build_ext_corpus.py` | OSCEC / Ismael Carmona García |
| `data/sources/pdf/Il Dalmatico.pdf` | Dalmatian human reference | none (no text layer) | bibliography only; see `corpus.md` |
| `data/sources/jsonl/kaikki.org-dictionary-Dalmatian.jsonl` | Dalmatian Kaikki snapshot | `scripts/build_dlm_corpus.py` | Kaikki/Wiktextract |
| `data/sources/jsonl/kaikki.org-dictionary-Romansh.jsonl` | Romansh Kaikki snapshot | `scripts/build_kaikki_corpus.py` | Kaikki/Wiktextract |
| `docs/assets/reference-screenshot.png` | Project reference image | documentation only | formerly a root-level screenshot |

Generated `data/words/*_words.json`, candidates, and evaluations are derived
artifacts. Source snapshots may be regenerated without changing the grammar or
the objective.
