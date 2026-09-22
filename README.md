# Vulgultra

*Vulgus* + *ultra*: beyond Vulgar Latin. A constructed language that
**reverses the Vulgar Latin process** and packs the result into as few
phonemic syllables as the attested Romance record allows. Roots are a
knapsack (one repaired candidate per concept). Endings are a small coupled
assignment, solved with simulated annealing.

Canonical spec: [`docs/grammar/grammar.tex`](docs/grammar/grammar.tex).
The optimizer must follow that document.

## Architecture

```
Python prep (G2P + repair)  →  JSON candidates  →  Rust SA  →  JSON lexicon
   vulgultra/                       data/              vulgultra-cli/    data/
```

Python adapts IPA and **repairs before scoring** (glide formation, identical
vowel collapse, last-resort epenthesis; unrepairable forms are discarded).
Root $\sigma$ is a separable knapsack. $|\Phi|$ and lect-diversity couple
the $\sigma$-optimal slice, so Rust SA is justified there.

## Quick Start

```bash
.venv/bin/python3 -m vulgultra.pipeline prep -n 1000 -o data/candidates.json

cd vulgultra-cli && cargo build --release && cd ..
./vulgultra-cli/target/release/vulgultra \
    -i data/candidates.json \
    -o data/vulgultra_lexicon.json \
    -n 2000000
```

## Energy

```
E = 1000 Σ σ(root)                 # never sold
  +   40 |Φ|                       # 40×23 = 920 < 1000
  +    1 (N_src − n_lects)         # |L|=36 < 40; σ-and-Φ tie-break
  + 0.02 × mean(N_src − support)   # finer than one lect
  +  200 Σ σ(ending)
  + 1e5  · collisions
  + 2000 · leftover violations
  +  500 Σ max(0, 2 − d)
```

`N_src = |L| = 36` (daughters only). A thin lect wins a root only on a
σ-tie that does not enlarge Φ. That is the diversity invariant.

## Phonotactics (reverse VL)

- Latin `sC` onsets are legal (undo Western *e*-prothesis)
- Sonorant + glide (`nj`, `lw`) is a legal onset
- Any single coda; `CC` if sonorant+C or `s`+stop
- **Geminates are legal.** Expand `ɛ ɔ` only if 1σ ending rows still collide
- Glides `/j w/` are consonants; syllable count = number of vowels
- Penultimate stress: restoring a 1σ ending puts stress on the stem-final σ

## Morphology

- **Nouns and adjectives:** gender × case (nom/acc/gen) × number = 12 cells, all 1σ
- **Verbs:** one stem; each tense is its own 6-person row from one lect (`amos` → `mos`). Tenses may differ.
- Collision only inside a 6-person row (cross-tense syncretism is Romance-legal)
- Articles `o/a/os/as` mark definiteness only; case marks role
- Copula is suppletive (`so / es / e / som / sos / son`)

## Project structure

```
vulgultra/                  Python package
  phonology.py          IPA, repair, syllabify, orthography
  paradigms.py          12-cell case tables, 1σ verb cells
  optimizer.py          Python SA (testing)
  pipeline.py           prep: G2P → repair → discard → JSON
  realize.py            case, gender, articles, copula

vulgultra-cli/         Rust SA (endings + optional root swaps)
docs/grammar/grammar.tex
docs/eval/34_romance_scorecard.md   # historical name; run is |L| daughters
data/words/             per-lect corpora
xmls/                   Wiktionary / Wikipedia dumps (gitignored)
```

## Source lects

36 Romance daughters, grouped by branch. Latin (`la`) and English (`en`)
are reserved: they never compete in the knapsack.

| Branch | Theme | Lects |
|---|---|---|
| Ibero | `o` (`u` in ast/ext) | `es` Spanish, `pt` Portuguese, `gl` Galician, `an` Aragonese, `ast` Asturian, `ext` Extremaduran, `lad` Ladino, `mwl` Mirandese |
| Occitano | `e` | `oc` Occitan, `ca` Catalan, `gsc` Gascon |
| Oil | `e` | `fr` French, `wa` Walloon, `pcd` Picard, `nrf` Norman, `glw` Gallo |
| Arpitan | `o` | `frp` Franco-Provençal |
| Gallo-Italian | `o` | `lmo` Lombard, `pms` Piedmontese, `lij` Ligurian, `eml` Emilian, `rgn` Romagnol |
| Italo-Dalmatian | `o` / `u` | `it` Italian, `vec` Venetan, `ist` Istriot, `dlm` Dalmatian (`o`); `scn` Sicilian, `co` Corsican (`u`) |
| Rhaeto | mixed | `rm` Romansh, `fur` Friulian, `lld` Ladin |
| Sardinian | `u` | `sc` Sardinian |
| Eastern | `u` | `ro` Romanian, `rup` Aromanian, `ruo` Istro-Romanian, `ruq` Megleno-Romanian |

Norman is `nrf`. Extremaduran is kept (book source). Empty Swadesh cells are legal; corpus glosses fill them when the match is exact.

Corpus counts: [`docs/corpus.md`](docs/corpus.md). Remaining work: [`TODO.md`](TODO.md).

If you want to grow the thin lects, the [Wikimedia Incubator](https://incubator.wikimedia.org/) takes entries.
