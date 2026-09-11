# Lacyo

A constructed language derived from computational optimization over the Romance
language family. Lacyo uses simulated annealing to discover optimal roots,
fusional endings, and phoneme inventory by minimizing a multi-term energy
function across ~3000 concepts extracted from French, Spanish, Italian, and
Portuguese.

## Architecture

```
Python prep (G2P)  →  JSON candidates  →  Rust SA optimizer  →  JSON lexicon
   lacyo/                data/              cyberlatin-cli/         data/
```

**Python** handles phonological data preparation (epitran G2P is Python-only).
**Rust** handles the simulated annealing hot loop (millions of iterations in
seconds).

## Quick Start

```bash
# 1. Python prep: extract top-1000 words, IPA transcription, candidate building
.venv/bin/python3 -m lacyo.pipeline prep -n 1000 -o data/candidates.json

# 2. Rust optimizer: simulated annealing over candidates
cd cyberlatin-cli && cargo build --release && cd ..
./cyberlatin-cli/target/release/cyberlatin-cli \
    -i data/candidates.json \
    -o data/lacyo_lexicon.json \
    -n 2000000

# Output: data/lacyo_lexicon.json (lexicon + endings + phoneme inventory)
```

## Energy Function

The optimizer minimizes:

```
E = w_syl  · Σ syllables(root_i)       # prefer short roots
  + w_phon · |Φ|                        # minimize phoneme inventory size
  + w_end  · Σ syllables(ending_j)      # prefer short endings
  + w_coll · collisions                 # no duplicate endings in a paradigm
  + w_tact · violations                 # phonotactic well-formedness
  + w_dist · distinctiveness_penalty    # endings must be perceptually distinct
```

The phoneme inventory is **emergent** — the 23-phoneme set (18C + 5V) is the
search space ceiling. Whichever phonemes survive in the optimized roots become
the actual inventory. `E_phon` pressures the optimizer to use fewer phonemes.

## Phonotactics

Naturalistic, respecting Romance source material:
- Any single consonant is a legal coda
- Coda clusters up to 2 allowed if sonorant precedes obstruent (e.g. /ns/, /nd/, /rt/)
- Onset clusters: obstruent + liquid/glide (e.g. /pl/, /tr/, /kw/)
- No gemination across syllable boundaries
- Diphthongs are unit phonemes

## Fusional Morphology

Latin-style fusional endings encode multiple grammatical features simultaneously:
- **Nouns:** 6 slots (nom/acc/gen × sg/pl)
- **Verbs:** 3 tenses × 3 persons × 2 numbers × 2 moods + inf/participles/imperatives
- **Adjectives:** sg/pl

Endings are optimized alongside roots to maximize distinctiveness within paradigms.

## Project Structure

```
lacyo/                  Python package
  phonology.py          IPA tokenization, G2P, phonotactics, orthography
  optimizer.py          Python SA (testing only, too slow for production)
  pipeline.py           E2E pipeline: prep (export JSON) and run (full Python)

cyberlatin-cli/         Rust SA optimizer
  src/lib.rs            Core types, energy function, mutation, incremental cache
  src/main.rs           CLI, progress bar, SA loop, summary output

data/                   Pipeline I/O
  candidates.json       Python prep output → Rust input
  lacyo_lexicon.json    Optimizer output (roots + endings + inventory)
  morphemes/            Morpheme databases (Latin, Greek, Romance)
  words/                Parsed Wiktionary word lists (Incubator languages)

docs/grammar/
  grammar.tex           Full language specification (~900 lines)
docs/eval/
  34_romance_scorecard.md   Swadesh run over the 34 Romance lects


xmls/                   Wiktionary dumps (not tracked in git)
   1. an      — Aragonese
   2. ast     — Asturian
   3. ca      — Catalan
   4. dlm     — Dalmatian
   5. eml     — Emiliano-Romagnolo
   6. es      — Spanish
   7. ext     — Extremaduran
   8. fr      — French
   9. frp     — Franco-Provençal
  10. fur     — Friulian
  11. gl      — Galician
  12. glw     — Gallo
  13. gsc     — Gascon
  14. ist     — Istriot
  15. it      — Italian
  16. la      — Latin
  17. lad     — Ladino
  18. lij     — Ligurian
  19. lld     — Ladin
  20. lmo     — Lombard
  21. mwl     — Mirandese
  22. nrm     — Norman
  23. oc      — Occitan
  24. pcd     — Picard
  25. pms     — Piedmontese
  26. pt      — Portuguese
  27. rm      — Romansh
  28. ro      — Romanian
  29. roa-rup — Aromanian
  30. ruo     — Istro-Romanian
  31. sc      — Sardinian
  32. scn     — Sicilian
  33. vec     — Venetian
  34. wa      — Walloon

  English is **not** a source language. A dump may still sit in `xmls/`
  and Swadesh `en` lives in `RESERVED_TABLES` for a later experiment.

  *(If you'd like to contribute to these low-resource Romance languages, head over to the [Wikimedia Incubator](https://incubator.wikimedia.org/) and start adding entries!)*
```

## Spec

The canonical language specification is in `docs/grammar/grammar.tex` (note: this is currently a draft). It covers
phonology, morphology, the energy function, pipeline architecture, syntax,
worked examples, and open questions.

**Important:** The `cyberlatin-cli` optimizer must strictly flow from the constraints and rules defined in `grammar.tex`. Any updates to the language's phonotactics, morphology, or grammar should first be specified in the TeX document before being implemented in the Rust CLI.
  20. pms — Piedmontese (170 words extracted from incubator)
  21. pcd — Picard (4 words extracted from incubator)
  22. mwl — Mirandese (24 words extracted from incubator)
  23. lij — Ligurian (0 words extracted from incubator)
  24. lad — Ladino (4 words extracted from incubator)
  25. frp — Franco-Provençal (2 words extracted from incubator)
  26. fur — Friulian (1 words extracted from incubator)
  27. nrm — Norman (0 words extracted from incubator)
  28. ext — Extremaduran (0 words extracted from incubator)
  29. eml — Emiliano-Romagnolo (0 words extracted from incubator)
  30. lld — Ladin (0 words extracted from incubator)
  31. gsc — Gascon (0 words extracted from incubator)
  32. dlm — Dalmatian (0 words extracted from incubator)
  33. ist — Istriot (0 words extracted from incubator)
  34. ruo — Istro-Romanian (0 words extracted from incubator)
  35. glw — Gallo (0 words extracted from incubator)

  *(If you'd like to contribute to these low-resource Romance languages, head over to the [Wikimedia Incubator](https://incubator.wikimedia.org/) and start adding entries!)*
```
Python prep (G2P)  →  JSON candidates  →  Rust SA optimizer  →  JSON lexicon
   lacyo/                data/              cyberlatin-cli/         data/
```

**Python** handles phonological data preparation (epitran G2P is Python-only).
**Rust** handles the simulated annealing hot loop (millions of iterations in
seconds).

## Quick Start

```bash
# 1. Python prep: extract top-1000 words, IPA transcription, candidate building
.venv/bin/python3 -m lacyo.pipeline prep -n 1000 -o data/candidates.json

# 2. Rust optimizer: simulated annealing over candidates
cd cyberlatin-cli && cargo build --release && cd ..
./cyberlatin-cli/target/release/cyberlatin-cli \
    -i data/candidates.json \
    -o data/lacyo_lexicon.json \
    -n 2000000

# Output: data/lacyo_lexicon.json (lexicon + endings + phoneme inventory)
```

## Energy Function

The optimizer minimizes:

```
E = w_syl  · Σ syllables(root_i)       # prefer short roots
  + w_phon · |Φ|                        # minimize phoneme inventory size
  + w_end  · Σ syllables(ending_j)      # prefer short endings
  + w_coll · collisions                 # no duplicate endings in a paradigm
  + w_tact · violations                 # phonotactic well-formedness
  + w_dist · distinctiveness_penalty    # endings must be perceptually distinct
```

The phoneme inventory is **emergent** — the 23-phoneme set (18C + 5V) is the
search space ceiling. Whichever phonemes survive in the optimized roots become
the actual inventory. `E_phon` pressures the optimizer to use fewer phonemes.

## Phonotactics

Naturalistic, respecting Romance source material:
- Any single consonant is a legal coda
- Coda clusters up to 2 allowed if sonorant precedes obstruent (e.g. /ns/, /nd/, /rt/)
- Onset clusters: obstruent + liquid/glide (e.g. /pl/, /tr/, /kw/)
- No gemination across syllable boundaries
- Diphthongs are unit phonemes

## Fusional Morphology

Latin-style fusional endings encode multiple grammatical features simultaneously:
- **Nouns:** 6 slots (nom/acc/gen × sg/pl)
- **Verbs:** 3 tenses × 3 persons × 2 numbers × 2 moods + inf/participles/imperatives
- **Adjectives:** sg/pl

Endings are optimized alongside roots to maximize distinctiveness within paradigms.

## Project Structure

```
lacyo/                  Python package
  phonology.py          IPA tokenization, G2P, phonotactics, orthography
  optimizer.py          Python SA (testing only, too slow for production)
  pipeline.py           E2E pipeline: prep (export JSON) and run (full Python)

cyberlatin-cli/         Rust SA optimizer
  src/lib.rs            Core types, energy function, mutation, incremental cache
  src/main.rs           CLI, progress bar, SA loop, summary output

data/                   Pipeline I/O
  candidates.json       Python prep output → Rust input
  lacyo_lexicon.json    Optimizer output (roots + endings + inventory)
  morphemes/            Morpheme databases (Latin, Greek, Romance)
  words/                Parsed Wiktionary word lists (Incubator languages)

docs/grammar/
  grammar.tex           Full language specification (~900 lines)
docs/eval/
  34_romance_scorecard.md   Swadesh run over the 34 Romance lects


xmls/                   Wiktionary dumps (not tracked in git)
   1. an      — Aragonese (4,224 words)
   2. ast     — Asturian (70,474 words)
   3. ca      — Catalan (605,760 words)
   4. dlm     — Dalmatian (0 words extracted from incubator)
   5. eml     — Emiliano-Romagnolo (0 words extracted from incubator)
   6. es      — Spanish (941,141 words)
   7. ext     — Extremaduran (0 words extracted from incubator)
   8. fr      — French (6,547,625 words)
   9. frp     — Franco-Provençal (81 words extracted from incubator)
  10. fur     — Friulian (37 words extracted from incubator)
  11. gl      — Galician (89,747 words)
  12. glw     — Gallo (0 words extracted from incubator)
  13. gsc     — Gascon (0 words extracted from incubator)
  14. ist     — Istriot (0 words extracted from incubator)
  15. it      — Italian (579,610 words)
  16. la      — Latin (41,102 words)
  17. lad     — Ladino (88 words extracted from incubator)
  18. lij     — Ligurian (137 words extracted from incubator)
  19. lld     — Ladin (0 words extracted from incubator)
  20. lmo     — Lombard (35,741 words)
  21. mwl     — Mirandese (579 words extracted from incubator)
  22. nrm     — Norman (2 words extracted from incubator)
  23. oc      — Occitan (72,316 words)
  24. pcd     — Picard (765 words extracted from incubator)
  25. pms     — Piedmontese (3,068 words extracted from incubator)
  26. pt      — Portuguese (498,451 words)
  27. rm      — Romansh (2 words)
  28. ro      — Romanian (180,294 words)
  29. roa-rup — Aromanian (1,336 words)
  30. ruo     — Istro-Romanian (0 words extracted from incubator)
  31. sc      — Sardinian (3 words)
  32. scn     — Sicilian (21,939 words)
  33. vec     — Venetian (5,068 words)
  34. wa      — Walloon (41,328 words)

  English is not a source. Reserved Swadesh `en` is in `lacyo/swadesh_rest.py`
  (`RESERVED_TABLES`) for later; the dump may remain in `xmls/`.

  *(If you'd like to contribute to these low-resource Romance languages, head over to the [Wikimedia Incubator](https://incubator.wikimedia.org/) and start adding entries!)*

scripts/                  Python scripts
  latin_word_zoo.py     Generates a comparative vocabulary table across 12 Romance languages
```

## Spec

The canonical language specification is in `docs/grammar/grammar.tex` (note: this is currently a draft). It covers
phonology, morphology, the energy function, pipeline architecture, syntax,
worked examples, and open questions.

**Important:** The `cyberlatin-cli` optimizer must strictly flow from the constraints and rules defined in `grammar.tex`. Any updates to the language's phonotactics, morphology, or grammar should first be specified in the TeX document before being implemented in the Rust CLI.
