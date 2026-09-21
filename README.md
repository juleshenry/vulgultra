# Lacyo

A constructed language that **reverses the Vulgar Latin process** and packs
the result into as few phonemic syllables as the attested Romance record
allows. Roots are a knapsack (one repaired candidate per concept). Endings
are a small coupled assignment, solved with simulated annealing.

Canonical spec: [`docs/grammar/grammar.tex`](docs/grammar/grammar.tex).
The optimizer must follow that document.

## Architecture

```
Python prep (G2P + repair)  →  JSON candidates  →  Rust SA  →  JSON lexicon
   lacyo/                       data/              cyberlatin-cli/    data/
```

Python adapts IPA and **repairs before scoring** (glide formation, identical
vowel collapse, last-resort epenthesis; unrepairable forms are discarded).
Root $\sigma$ is a separable knapsack. $|\Phi|$ and lect-diversity couple
the $\sigma$-optimal slice, so Rust SA is justified there.

## Quick Start

```bash
.venv/bin/python3 -m lacyo.pipeline prep -n 1000 -o data/candidates.json

cd cyberlatin-cli && cargo build --release && cd ..
./cyberlatin-cli/target/release/cyberlatin-cli \
    -i data/candidates.json \
    -o data/lacyo_lexicon.json \
    -n 2000000
```

## Energy

```
E = 1000 Σ σ(root)                 # never sold
  +   40 |Φ|                       # 40×23 = 920 < 1000
  +    1 (N_src − n_lects)         # 34 < 40; σ-and-Φ tie-break
  + 0.02 × mean(N_src − support)   # finer than one lect
  +  200 Σ σ(ending)
  + 1e5  · collisions
  + 2000 · leftover violations
  +  500 Σ max(0, 2 − d)
```

`N_src = 34`. A thin lect wins a root only on a σ-tie that does not
enlarge Φ. That is the diversity invariant.

## Phonotactics (reverse VL)

- Latin `sC` onsets are legal (undo Western *e*-prothesis)
- Sonorant + glide (`nj`, `lw`) is a legal onset
- Any single coda; `CC` if sonorant+C or `s`+stop
- **Geminates are legal.** Expand `ɛ ɔ` only if 1σ ending rows still collide
- Glides `/j w/` are consonants; syllable count = number of vowels
- Penultimate stress: restoring a 1σ ending puts stress on the stem-final σ

## Morphology

- **Nouns and adjectives:** gender × case (nom/acc/gen) × number = 12 cells, all 1σ
- **Verbs:** one lect's person table as a block; every cell clipped to 1σ (`amos` → `mos`)
- Collision only inside a 6-person row (cross-tense syncretism is Romance-legal)
- Articles `o/a/os/as` mark definiteness only; case marks role
- Copula is suppletive (`so / es / e / som / sos / son`)

## Project structure

```
lacyo/                  Python package
  phonology.py          IPA, repair, syllabify, orthography
  paradigms.py          12-cell case tables, 1σ verb cells
  optimizer.py          Python SA (testing)
  pipeline.py           prep: G2P → repair → discard → JSON
  realize.py            case, gender, articles, copula

cyberlatin-cli/         Rust SA (endings + optional root swaps)
docs/grammar/grammar.tex
docs/eval/34_romance_scorecard.md
data/words/             per-lect corpora
xmls/                   Wiktionary / Wikipedia dumps (gitignored)
```

## Source lects (34; English is not a source)

`fr es it pt ca ro gl oc an ast ext lad mwl scn vec lmo pms lij fur eml lld ist wa pcd nrm frp glw gsc la rm sc rup ruo dlm`

Extremaduran is kept (book source). Norman in the code is still `nrm`.
Swadesh `en` lives in `RESERVED_TABLES` only.

If you want to grow the thin lects, the [Wikimedia Incubator](https://incubator.wikimedia.org/) takes entries.
