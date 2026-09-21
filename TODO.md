# TODO

## Extract Incubator `Wt/` pages into per-lect corpora

**Done (2026-09-20).** Script: `scripts/extract_incubator_wt.py`  
Output: `xmls/incubator/{code}wiktionary-incubator-pages-articles.xml`

Source dump: `xmls/incubatorwiki-latest-pages-articles.xml`

Lemma pages extracted (templates / deep paths skipped — counts are real entries, not raw `Wt/` string hits):

| code | pages | lect | notes |
|---|---:|---|---|
| `pms` | 3023 | Piedmontese | |
| `nrf` | 1526 | Norman | **use this**, not `nrm` |
| `pcd` | 768 | Picard | |
| `mwl` | 590 | Mirandese | |
| `egl` / `eml` | 152 | Emilian | same pages, both stems |
| `lij` | 141 | Ligurian | |
| `lad` | 107 | Ladino | |
| `frp` | 83 | Franco-Provençal | |
| `fur` | 37 | Friulian | thin |
| `nrm` | 2 | Norman | thin — prefer `nrf` |

**Extremaduran (`ext`):** corpus built.

- Script: `scripts/build_ext_corpus.py`
- Output: `data/words/ext_words.json` (gitignored under `data/`)
- Sources:
  - `vendor/recursos_es-ext` ([juanro49/recursos_es-ext](https://github.com/juanro49/recursos_es-ext))
  - `oscec-diccionario-castellano-extremec3b1o-ismael-carmona-garcc3ada.pdf` (Carmona / OSCEC 2017)
  - `xmls/extwiki-latest-pages-articles.xml`

### Open-source pulls (careful)

**Wikipedia dumps** in `xmls/wiki/*.bz2`:  
`an fur frp lad lij lld mwl nap pcd pms rm sc vec eml roa_rup`

**Apertium** clones in `vendor/` (GPL linguistic data):  
`apertium-arg`, `apertium-spa-arg`, `apertium-ast`, `apertium-spa-ast`, `apertium-oci`, `apertium-oci-spa`, `apertium-srd`, `apertium-ita-srd`, `apertium-scn`, `apertium-mwl`, `apertium-glg`, `apertium-nap`, `apertium-fra-cat`  
(no official `apertium-fur` / `apertium-lld` / `apertium-vec` repos)

**Romansh sourcing ladder** — full writeup: `docs/sources_romansh.md`

| Tier | Source | Ingest? | Status |
|---|---|---|---|
| 1 | Kaikki / Wiktextract JSONL | **yes** | `kaikki.org-dictionary-Romansh.jsonl` → `data/words/rm_words.json` (~2323 lemmas) |
| 2 | DRG TEI/XML (Trier digitization) | only if bulk dump appears | Online UI [online.drg.ch](https://online.drg.ch/); **no verified public TEI dump** — do not scrape |
| 3 | DRG PDF / scans | reference only | Per-volume PDFs exist; bad for bulk lexicon |
| 4 | Pledari Grond via [dicziunari](https://github.com/farscrl/dicziunari) | only with legal export | GitHub = scripts + `_short` samples; full JSON not redistributable |

**Dalmatian (`dlm`):** Kaikki JSONL ingested → `data/words/dlm_words.json` (~1179 lemmas); Swadesh overlays in `DLM_KAIKKI_OVERRIDES`.

**Kaikki/Wiktextract JSONL** in `data/words/kaikki-{code}.jsonl` → `{code}_words.json` (`scripts/build_kaikki_corpus.py`):

| lemmas | code | lect |
|---:|---|---|
| 33927 | ast | Asturian |
| 11244 | nrf | Norman |
| 7157 | oc | Occitan |
| 5991 | lld | Ladin |
| 4604 | vec | Venetan |
| 4104 | rup | Aromanian |
| 3134 | egl | Emilian |
| 3123 | scn | Sicilian |
| 2598 | wa | Walloon |
| 2524 | lad | Ladino |
| 2323 | rm | Romansh |
| 1991 | fur | Friulian |
| 1759 | lij | Ligurian |
| 1618 | an | Aragonese |
| 1532 | nap | Neapolitan |
| 1422 | rgn | Romagnol |
| 1302 | sc | Sardinian |
| 1179 | dlm | Dalmatian |
| 1033 | pms | Piedmontese |
| 911 | co | Corsican |
| 624 | mwl | Mirandese |

Kaikki miss (404 on English edition): Picard, Franco-Provençal/Arpitan, Gascon, Istro-Romanian. Gallo exists on the **French** edition (`frwiktionary/Gallo`, 11566 words) — ingested as `glw`.

### 10k collection (2026-09-20)

Scripts: `scripts/collect_10k.py` (Apertium dix/lexd + `oci@gascon` + aliases), `scripts/harvest_dump_types.py` (`--title-limit`), `scripts/build_kaikki_corpus.py`.

Bar: ≥10k **lemmas** in `{code}_words.json` **or** ≥10k Wikipedia running-text **types** (`meta.n_wiki_types`). Wiki article titles are not merged into lemma entries.

| code | lemmas | wiki types | CLEAR via | notes |
|---|---:|---:|---|---|
| fr | 61007 | 0 | lemmas | Apertium fra-cat |
| es | 39396 | 0 | lemmas | Apertium spa-arg / spa-ast |
| it | 25000 | 0 | lemmas | itwiktionary titles (capped) |
| pt | 25000 | 0 | lemmas | ptwiktionary titles (capped) |
| ca | 60501 | 0 | lemmas | Apertium fra-cat |
| ro | 25000 | 0 | lemmas | rowiktionary titles (capped) |
| gl | 48775 | 0 | lemmas | Apertium glg |
| oc | 235721 | 0 | lemmas | wikt dump + Apertium oci metadix |
| an | 58746 | 488318 | both | Apertium arg |
| ast | 59792 | 0 | lemmas | Kaikki + Apertium ast |
| ext | 19910 | 0 | lemmas | GitHub + Carmona PDF |
| lad | 2612 | 97202 | wiki types | |
| mwl | 60207 | 177906 | both | Apertium mwl lexd |
| scn | 59909 | 0 | lemmas | wikt + Apertium scn |
| vec | 9205 | 335220 | wiki types | |
| lmo | 35741 | 0 | lemmas | wikt dump |
| pms | 4053 | 205321 | wiki types | |
| lij | 1896 | 238624 | wiki types | |
| fur | 2028 | 102924 | wiki types | |
| eml | 3286 | 193327 | wiki types | alias of egl + emlwiki |
| lld | 5991 | 208097 | wiki types | |
| wa | 42716 | 0 | lemmas | wikt dump |
| pcd | 765 | 126753 | wiki types | |
| nrm | 11244 | 0 | lemmas | alias of nrf (prefer nrf) |
| frp | 82 | 77352 | wiki types | |
| glw | 11566 | 0 | lemmas | Kaikki **frwiktionary** Gallo |
| gsc | 66615 | 0 | lemmas | Apertium `oci@gascon` / `oci@aran` |
| la | 41282 | 0 | lemmas | wikt dump |
| rm | 2325 | 138265 | wiki types | Pledari still rights-gated |
| sc | 103702 | 183635 | both | Apertium srd |
| rup | 5337 | 65489 | wiki types | roa_rupwiki |
| nap | 1532 | 116086 | wiki types | |
| nrf | 11244 | 0 | lemmas | Kaikki Norman |

**Still under 10k (open-source ceiling):**

| code | lemmas | wiki types | why it stops here |
|---|---:|---:|---|
| ist | 1034 | 0 | Kaikki max. TalkBank CHA zip is auth-gated. Verbix: one public page only. No Wikipedia. PanLex API host did not resolve. |
| dlm | 1179 | 0 | Kaikki max. No Wikipedia. `Il Dalmatico.pdf` is a scan (tiff2pdf) — no text layer. |
| ruo | 305 | 0 | No Kaikki, no Wikipedia. En Wiktionary category ~109 lemmas + Swadesh. Byhan/Kovačec dictionaries are not bulk-open. Do not scrape vlaski-zejanski. |

### Next
- [ ] Wire `{code}_words.json` + incubator XMLs + wiki dumps + Apertium dix into gloss-aligned ingest
- [ ] Prefer `nrf` over `nrm` in `SOURCE_LANGS` / G2P donor map when Norman is used from dumps
- [ ] Romansh: if Pledari exports arrive → `vendor/dicziunari/db/data/` → convert
- [ ] Re-check later whether IDRG publishes DRG TEI as a dump
- [ ] Istriot: user login/download TalkBank CHA zip → `vendor/istriot/`
- [ ] PanLex snapshot if a per-language extract appears (do not pull the 2GB lite zip just for three lects)

