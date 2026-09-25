# Historical evaluation: legacy scoring

This is a preserved record of the pre-September-2026 objective. It is not a
current acceptance target and does not describe the grammar now used by the
code.

The legacy score used a weighted root-syllable term, a phoneme term, a source-
lect coverage bonus, and a same-stem support term. Its recorded mixed run was:

| snapshot | root syllables | root inventory | total energy |
|---|---:|---:|---:|
| legacy SA / set-cover | 223 | 22 | 257981 |
| legacy support-shortest | 223 | 22 | 257993 |

The current rule is instead a hard legal minimum-syllable shortlist followed by
root inventory maximization; source spread and morpheme uniformity are audit
fields only. See [`34_romance_scorecard.md`](34_romance_scorecard.md) for the
current generated report and [`../grammar/grammar.tex`](../grammar/grammar.tex)
for the specification.
