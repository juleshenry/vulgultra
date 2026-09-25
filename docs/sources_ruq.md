# Megleno-Romanian (`ruq`) sources

| Source | Status | Ingest |
|---|---|---|
| **[ASJP ROMANIAN_MEGLENO](https://asjp.clld.org/languages/ROMANIAN_MEGLENO)** | 40-item list, Capidan 1925/1935, compiled by Darja Appelganz. ASJP v21 (Wichmann et al. 2025). | **Done:** `data/words/ruq_asjp.txt`. Converted forms in `ruq_words.json` (`asjp`). Swadesh `road` = `drum` (ASJP *path*). Other 40 items already matched the Wiktionary appendix. |
| [Appendix:Megleno-Romanian Swadesh list](https://en.wiktionary.org/wiki/Appendix:Megleno-Romanian_Swadesh_list) | ~195/207 | `RUQ` pack |
| En Wiktionary [`Category:Megleno-Romanian lemmas`](https://en.wiktionary.org/wiki/Category:Megleno-Romanian_lemmas) | 362 lemma pages (336 with glosses) | **Done:** merged into `ruq_words.json` (`wikt_category`). |
| Kaikki / Wikipedia | None | English-edition Kaikki 404; no `ruqwiki` |
| **Capidan 1925** *Meglenoromânii* I ([Wikisource Vol. I](https://ro.wikisource.org/wiki/Meglenorom%C3%A2nii/Volumul_I)) | Foundational grammar + conjugation; a fi often via pp. 172–74 in secondary cites | **Done (tables):** class exemplars + `iri/sam` on `docs/conjugations/ruq.md` |
| **RVID 2.0 / ODRVM** ([GitLab](https://gitlab.com/sbeniamine/Romance_Verbal_Inflection_Dataset)) | 37 lexemes, 2293 IPA forms; Capidan-based, border-generalized | **Done:** `data/sources/rvid_megleno/` → `scripts/harvest_ruq_rvid.py` → `ruq_diseux.json` |
| Atanasov 2002 *Meglenoromâna astăzi* | Modern qualification | Cite for dialectal/modern caveats (not bulk-ingested) |
| Notes | | `docs/eval/ruq_conjugation_notes.md` |
