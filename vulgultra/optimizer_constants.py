"""Optimizer constants, kept in one place for Python/Rust parity.

The weights are the morphology-stage terms in grammar.tex chapter 4.  Root
syllable minimization is a hard shortlist, so it has no tunable weight.
"""

from __future__ import annotations


W_PHON = -1       # maximize observed root segments after the shortest slice
W_END = 200       # one-syllable morphology cost
W_COLL = 100_000  # collisions inside a finite person row
W_TACT = 2_000    # leftover phonotactic violations
W_DIST = 500      # distance shortfall inside a finite person row
DIST_THRESHOLD = 2

VERB_SLOTS_IND = [
    f"{tense}_{person}{number}"
    for tense in ("prs", "pst", "fut")
    for person in ("1", "2", "3")
    for number in ("sg", "pl")
]
VERB_SLOTS_SUBJ = [
    f"{tense}_subj_{person}{number}"
    for tense in ("prs", "pst", "fut")
    for person in ("1", "2", "3")
    for number in ("sg", "pl")
]
VERB_NONFINITE = ["inf", "ptcp_act", "ptcp_pas", "imp_2sg", "imp_2pl"]
VERB_SLOTS = VERB_SLOTS_IND + VERB_SLOTS_SUBJ + VERB_NONFINITE
