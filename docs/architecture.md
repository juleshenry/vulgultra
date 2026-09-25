# Architecture and evidence flow

The durable specification is [`docs/grammar/grammar.tex`](grammar/grammar.tex);
the dated thoughts file remains a working note. The implementations share
this boundary:

```text
source snapshots → meaning grid → G2P/repair → σ-shortlist → root SA
       │               │              │             │             │
 data/sources/     evidence       phonology      candidates    Rust runtime
       └────────────────────────────── audit metadata ────────────────┘
```

Python modules are split by concern. `pipeline_constants.py` owns paths,
language order, and schema names; `phonology_constants.py` owns spelling and
G2P tables; `morphology_constants.py` owns the grammar's theme, slot, article,
and copula tables; and `optimizer_constants.py` owns chapter 4 weights.
`grid.py` normalizes evidence-bearing cells, `g2p.py` transcribes and repairs,
`candidate_prep.py` applies legality and the hard minimum-syllable filter, and
`serialization.py` defines the interchange envelope. `pipeline.py` remains the
CLI/orchestration facade for existing scripts.

`vulgultra-cli/src/lib.rs` remains the public Rust facade. Its domain modules
(`phonology`, `morphology`, `optimization`, and `io`) expose the same public
helpers while keeping the JSON schema and CLI exports stable.

The complete aligned grid is retained for evidence. For each concept, Python
keeps only legal candidates with the minimum repaired phonemic syllable count.
Root annealing moves only inside that slice and maximizes the union of selected
root segments. Morphology is enumerated afterward; its legality, collision,
distance, and one-syllable costs are separate from lexical root selection.
Source spread and inferred morpheme uniformity remain audit fields, never
objective terms.
