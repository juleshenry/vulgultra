# Istro-Romanian (`ruo`) sources

| Source | Status | Ingest |
|---|---|---|
| **Cantemir 2020 thesis** `Cantemir_Thesis_Final_Draft-converted.pdf` | Southern IR/Vlashki vs Daco-Romanian; appendix wordlist + numbered examples (p. 40–41 word-final `/l/` deletion, etc.) | **Done:** IR IPA → practical spelling in `ruo_words.json` (`cantemir2020`). Swadesh overlays in `RUO_OVERRIDES` (incl. attested `sănze` blood). |
| En Wiktionary `Category:Istro-Romanian lemmas` | ~109 lemmas | Done (`wikt_category`). |
| **[Appendix:Istro-Romanian Swadesh list](https://en.wiktionary.org/wiki/Appendix:Istro-Romanian_Swadesh_list)** | 207-concept list; ~140 filled | **Done:** `RUO_WIKT_SWADESH` (first citation form). `sănze` blood kept over appendix `sânže`. Empty cells not filled with Daco-Romanian. |
| Kaikki / Wikipedia | None | English-edition Kaikki 404; no `ruowiki`. |
| Kovačec / Byhan / vlaski-zejanski | Dictionaries / site | Not bulk-open. Do not scrape. |

Cantemir appendix columns are Daco-Romanian orthography, DR IPA, **IR IPA**, English. IR lemmas are the IPA column, not the Romanian spelling. Example (p. 40, ex. 27): DR `['fo.kul]` ~ IR `['fo.ku]` ‘the fire’ → `foku`.
