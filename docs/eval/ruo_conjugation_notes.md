# Istro-Romanian verb conjugations — notes

## What we ingested

`docs/conjugations/ruo.md` and `data/conjugation/sources/ruo_diseux.json`
compile the four main conjugations from Verbix’s Istro-Romanian documentation
and scanned notes:

| Class | Citation infinitives | Model finite lemma |
|---|---|---|
| I (`I-å`) | `clămå`, `stå`, `turnå`, `zucå` | `rugå` |
| II (`II-é`) | `ramaré`, `ve`, `tiré`, `be` | `tiré` / imperfect from `cadé` |
| III (`III-e`) | `båte`, `årde`, `pl'erde`, `zacl'ide` | `trage` / `båte` |
| IV (`IV-í`) | `durmi`, `avzí`, `fi`, `cuperí` | `avzí` |
| IV-éi | `bivéi`, `movéi`, `piséi`, `frustikéi`, `cupéi` | `cupéi` |
| IV-úi | `carúi`, `radúi` | infinitive only so far |

Tenses covered where Verbix supplies them: present, imperfect, future
(conditional-future table), analytic perfect (`participle + ve`), analytic
conditional (`res/rei/re/… + infinitive`). Subjunctive present is noted as
identical to indicative present with `se` / `neca`.

## Citation quality

Verbix is a compact secondary summary (good for browsing). For formal work
prefer:

- Neiescu (descriptive Istro-Romanian tradition)
- Kovačec 1998
- Oxford Eastern Romance chapter covering Istro-/Megleno-/Aromanian
- Oxford ORA paper on Istro-Romanian verbs in `-[ɛi]` and `-[ui]`

Local phonology thesis (not full paradigms): Cantemir 2020 in
`data/sources/pdf/Cantemir_Thesis_Final_Draft-converted.pdf`.

## -éi / -úi

Verbix notes: verbs in **-véi** and **-úi** are iterative; **-éi** verbs may
be perfective or imperfective. These are the Slavic-contact-influenced
innovative classes beyond the four inherited conjugations.

## vs Daco-Romanian (quick cues)

| | Istro-Romanian | Romanian (standard) |
|---|---|---|
| Class count | 4 (+ -éi/-úi) | 4 |
| 1pl present | often `-n` (word-final *m→n*) | `-m` |
| Imperfect 3sg | frequently with inserted `-j-` (`fat͡ʃeja`) | diphthongal `-ea` |
| Future | synthetic class endings (`rugår…`) + analytic options | mainly analytic `voi` + infinitive |
| Perfect | participle + auxiliary `ve` | `am/ai/a…` + participle |

A full cell-by-cell comparison matrix against Romanian still needs a matched
lemma set; start from `rugå`~`ruga`, `avzí`~`auzi`, `durmi`~`dormi`,
`båte`~`bate`.

## Rebuild

```bash
.venv/bin/python3 scripts/harvest_ruo_verbix.py
.venv/bin/python3 scripts/build_conjugation_pages.py
```
