# Megleno-Romanian verb conjugations — notes

## What we ingested

`docs/conjugations/ruq.md` and `data/conjugation/sources/ruq_diseux.json`
compile Capidan-based Megleno-Romanian paradigms:

| Layer | Content |
|---|---|
| **Capidan-tradition orthography** | Class exemplars `căntári`, `lucrári`, `cădeári`, `bátiri`, `durmíri`, `sirbíri`, plus `iri/sam` (a fi) |
| **RVID 2.0 IPA** | 37 lexemes / 2293 forms from Oxford ODRVM scrape (Beniamine, Maiden & Round 2020) |
| **Vendored subset** | `data/sources/rvid_megleno/` (GPLv3) |

## Citation stack (as recommended)

1. **Table / base paradigm:** Capidan 1925, *Meglenoromânii* I (*Istoria și graiul lor*), with page numbers for published claims (a fi often via pp. 172–74 in secondary literature). Wikisource: [Volumul I](https://ro.wikisource.org/wiki/Meglenorom%C3%A2nii/Volumul_I).
2. **Normalized morphology / IPA:** Romance Verbal Inflection Dataset 2.0 ← Oxford Online Database of Romance Verb Morphology.
3. **Modern qualification:** Atanasov 2002, *Meglenoromâna astăzi*.
4. **Comparative framing:** Oxford Handbook chapter on Romanian / Istro- / Megleno- / Aromanian.

RVID’s language note: Capidan’s survey is **to some extent a generalization** over Megleno-Romanian varieties of the Greek–Macedonian border area.

## Four conjugations (+ subclasses)

| Class | Citation infinitive (label) | Present 1sg exemplar |
|---|---|---|
| I | `căntári` | `cǫ́nt` |
| I-ez | `lucrári` | `lucréz` |
| II | `cădeári` | `cad` |
| III | `bátiri` | `bat` |
| IV | `durmíri` | `dorm` |
| IV-esc | `sirbíri` | `sirbés` |
| fi | `iri` / `sam` | `jes` |

**Infinitive caveat:** Capidan/Oxford note that the short infinitive is virtually extinct as a verbal form; infinitive rows here are **citation / lexical labels**, not a Romanian-style productive infinitive slot.

## Contact morphology

Capidan and later work note Macedonian/Bulgarian contact effects (e.g. 1sg `-m`, 2sg `-ș` on some verbs). Friedman’s work on Macedonian inflections in Megleno-Romanian is the specialist lead for aspect and borrowed inflection.

## Rebuild

```bash
# if rvid_megleno/ missing, clone RVID and re-filter Megleno rows
.venv/bin/python3 scripts/harvest_ruq_rvid.py
.venv/bin/python3 scripts/build_conjugation_pages.py
```
