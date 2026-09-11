# TODO

## Extract Incubator `Wt/` pages into per-lect corpora

Source dump (already in tree, gitignored):

`xmls/incubatorwiki-latest-pages-articles.xml`

Split / filter pages under these prefixes into something the full-corpus pipeline can ingest (same shape as `*wiktionary-latest-pages-articles.xml` word lists, or a gloss-aligned JSON). Prefer `nrf` over thin `nrm` for Norman.

| Wt/ | ~pages | lect | notes |
|---|---:|---|---|
| `pms` | 11k | Piedmontese | |
| `mwl` | 12k | Mirandese | |
| `nrf` | 10k | Norman | **use this**, not empty `nrm` |
| `lad` | 4k | Ladino | |
| `lij` | 3.5k | Ligurian | |
| `egl` | 3.3k | Emilian | maps to our `eml` / `egl` |
| `pcd` | 2k | Picard | |
| `frp` | 1.6k | Franco-Provençal | |
| `fur` | 190 | Friulian | thin but real |
| `nrm` | 182 | Norman | thin — prefer `nrf` |
| `ext` | 1 | Extremaduran | basically empty; low priority |

Still no useful dump: `gsc` Gascon, `dlm` Dalmatian, `ist` Istriot, `ruo` Istro-Romanian, `glw` Gallo, `lld` Ladin.
