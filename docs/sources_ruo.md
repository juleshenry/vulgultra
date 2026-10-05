# Istro-Romanian (`ruo`) sources

| Source | Status | Ingest |
|---|---|---|
| **Cantemir 2020 thesis** [`data/sources/pdf/Cantemir_Thesis_Final_Draft-converted.pdf`](../data/sources/pdf/Cantemir_Thesis_Final_Draft-converted.pdf) | Southern IR/Vlashki vs Daco-Romanian; appendix wordlist + numbered examples (p. 40–41 word-final `/l/` deletion, etc.) | **Done:** IR IPA → practical spelling in `ruo_words.json` (`cantemir2020`). Swadesh overlays in `RUO_OVERRIDES` (incl. attested `sănze` blood). |
| En Wiktionary `Category:Istro-Romanian lemmas` | ~109 lemmas | Done (`wikt_category`). |
| **[Appendix:Istro-Romanian Swadesh list](https://en.wiktionary.org/wiki/Appendix:Istro-Romanian_Swadesh_list)** | 207-concept list; 140 filled | **Done:** `RUO_WIKT_SWADESH` (first citation form). `sănze` blood kept over appendix `sânže`. Empty appendix cells stay empty. |
| En Wiktionary translation tables and Latin descendant lists | 107 translations, 202 descendants citing an Istro-Romanian form | **Done:** `RUO_WIKT_ENTRIES`, 8 cells (table below). |
| **Saenko 2015**, *Annotated Swadesh wordlists for the Romance group* (Global Lexicostatistical Database; CLDF at [lexibank/saenkoromance](https://github.com/lexibank/saenkoromance), CC-BY-4.0) | 110 concepts, with source spelling, transcription and stress | **Done:** `RUO_SAENKO`, 18 cells. Local copy in `data/sources/saenkoromance/`. |
| Kaikki / Wikipedia | None | English-edition Kaikki 404; no `ruowiki`. |
| Kovačec / Byhan / vlaski-zejanski | Dictionaries / site | Not bulk-open. Do not scrape. |
| **Verbix Istro-Romanian docs** + scanned notes | Four conjugations + -éi/-úi; present/imperfect/future/perfect/conditional | **Done:** `scripts/harvest_ruo_verbix.py` → `data/conjugation/sources/ruo_diseux.json`, page `docs/conjugations/ruo.md`. Secondary summary — prefer Neiescu/Kovačec/Oxford for formal citation. See `docs/eval/ruo_conjugation_notes.md`. |

Cantemir appendix columns are Daco-Romanian orthography, DR IPA, **IR IPA**, English. IR lemmas are the IPA column, not the Romanian spelling. Example (p. 40, ex. 27): DR `['fo.kul]` ~ IR `['fo.ku]` ‘the fire’ → `foku`.

## Grid column, re-sourced 5 October 2026

The column used to start from a 213-form list in Daco-Romanian, and only the
140 cells the Swadesh appendix fills were replaced. The other 73 kept the
Romanian word (66 letter-for-letter the `ro` column: *respira, corect,
zâmbi, animal*), against axiom 3. That list is gone: the column is now 148
attested cells and 65 empty ones.

Searched for the 73: the Swadesh appendix (re-read live); the 109 pages of
`Category:Istro-Romanian lemmas`; every English Wiktionary page with an
Istro-Romanian translation, cognate or descendant (506 pages, 277 distinct
forms); the Cantemir entries in `ruo_words.json`; the Istro-Romanian entries
and translations in the local French, Portuguese, Spanish and Galician
Wiktionary dumps; the Verbix page. Found, with the sense:

| Concept | Form | Where |
|---|---|---|
| thick | gros | en.wiktionary *gros*, Istro-Romanian adjective "thick"; Latin *grossus*, descendants |
| liver | ficåt | en.wiktionary *ficåt*; translation under *liver* |
| bite | mučcå | en.wiktionary, translation under *bite* ("cut into by clamping the teeth") |
| hold | țire | en.wiktionary, translation under *hold*, spelled *ţire*; Verbix has *tiré* |
| hit | båte | en.wiktionary, translation under *beat* ("to hit, to knock, to pound"). Also the appendix form for *fight* |
| fingernail | ungľă | en.wiktionary, Latin *ungula*, descendants. Cantemir has *ungile* "the nails" |
| lie | zåc | en.wiktionary, Latin *iaceo*, descendants. Form as cited; it may be a 1sg |
| copula | fi | en.wiktionary, translation under *be*; Latin *sum*, descendants; fr.wiktionary *fi* "Être"; Verbix class IV |

Not used:

- *trage*: the Verbix class III model, so attested as a verb, but no source
  gives its meaning. Probably "pull".
- *uscu* (Latin *exsuco*, descendants) is the verb; the concept *dry* is the adjective.
- *frikę* "fear" (Romanian Wikipedia) is a noun; the concept is the verb.

`data/words/ruo_words.json` had 185 entries whose only source was the old
padded column. The 184 not in the attested column were dropped (519 → 335).

## Saenko 2015, added 5 October 2026

Saenko gives each word in the spelling of his sources, with a transcription
and the stress. Eighteen cells now follow him: fourteen that were empty
(*seed* semínțę, *root* córen, *bark* córa, *fat* måst, *horn* corn, *tail*
códę, *swim* pliví, *fly* letí, *sand* salbún, *cloud* oblåc, *smoke* dim,
*dry* uscåt, *far* lårgo, *thin* supțíre), *feather* pęna (his source marks
the stress on ę with a glyph outside Unicode, dropped here), and three where
his sense-aligned form replaces one taken from a descendant list: *fingernail*
úngľe (was ungľă), *liver* ficåț (was ficåt), *lie* začå (was zåc). He also
confirms *bite* mučcå. The column is now 163 attested cells and 50 empty.
