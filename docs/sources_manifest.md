# Local source manifest

Large local inputs live under `data/sources/` rather than the repository root.
They are ignored binary/snapshot inputs, while the derived word tables retain
source tags and the scripts below make the transformations reproducible.

| Path | Role | Consumer | Provenance |
|---|---|---|---|
| `data/sources/pdf/Cantemir_Thesis_Final_Draft-converted.pdf` | Istro-Romanian thesis appendix | `scripts/build_ruo_cantemir.py` | Cantemir 2020; see `sources_ruo.md` |
| `data/sources/pdf/oscec-diccionario-castellano-extremec3b1o-ismael-carmona-garcc3ada.pdf` | Extremaduran dictionary | `scripts/build_ext_corpus.py` | OSCEC / Ismael Carmona García |
| `data/sources/pdf/Il Dalmatico.pdf` | Dalmatian human reference | none (no text layer) | bibliography only; see `corpus.md` |
| `data/sources/jsonl/kaikki.org-dictionary-Dalmatian.jsonl` | Dalmatian Kaikki snapshot | `scripts/build_dlm_corpus.py` | Kaikki/Wiktextract |
| `data/sources/jsonl/kaikki.org-dictionary-Romansh.jsonl` | Romansh Kaikki snapshot | `scripts/build_kaikki_corpus.py` | Kaikki/Wiktextract |
| `data/sources/saenkoromance/*.csv` | Saenko 2015, annotated Swadesh lists, 43 Romance varieties | `scripts/audit_grid_sources.py` | lexibank/saenkoromance, CC-BY-4.0 |
| `data/sources/wikt_swadesh/*.json` | English Wiktionary Swadesh lists, with revision ids | `scripts/audit_grid_sources.py` | en.wiktionary, CC BY-SA |
| `data/sources/iecor/*.csv` | IE-CoR, 170 meanings, 160 Indo-European varieties | `scripts/audit_grid_sources.py` | lexibank/iecor, CC-BY-4.0 |
| `data/sources/wikt_sections.json` | Minority-lect entries of the local French, Spanish, Portuguese, Italian and Catalan Wiktionary dumps | `scripts/audit_grid_sources.py extract` | Wiktionary, CC BY-SA |
| `data/sources/pdf/stich_2001_these_francoprovencal.pdf` (+ `.txt`) | Franco-Provençal: the thesis defining ORB, with a Swadesh list and dictionary | `scripts/audit_grid_sources.py` | Stich 2001, Université Paris V; arpitania.eu |
| `data/sources/pdf/ricaud_mon_canepin_de_galo.pdf` (+ `.txt`) | Gallo: thematic Gallo–French lexicon | `scripts/audit_grid_sources.py` | Romain Ricaud; archive.org `galocanepin` |
| `data/sources/pdf/tiot_diqchionnaire_chti.pdf` (+ `.raw.txt`) | Picard of the Nord: small dictionary | `scripts/audit_grid_sources.py` | paroledechti.com, via the Wayback Machine |
| `data/sources/pdf/dawson_smirnova_2020_dffp_extract.pdf` | Picard: 33-page extract of the *Dictionnaire fondamental français-picard* | none (read by hand) | Agence régionale de la langue picarde, 2020; all rights reserved |
| `data/sources/pdf/arlp_2018_vogabulaire_ecole_picard.pdf` | Picard: school vocabulary | none | Agence régionale de la langue picarde, 2018; CC BY-NC-ND |
| `data/sources/pdf/motier_galo_francaez_2019.pdf` | Gallo: local glossary with IPA | none (read by hand) | Atelier de gallo, Résidence La Perrière, Héric |
| `data/sources/pdf/ferreira_2004_dicionario_mirandes_portugues.pdf` | Mirandese: letter M only | none | Ferreira and Ferreira, edition 0.1, 2004 |
| `data/sources/picard_diseux/mots/` | Picard of the Amiens area: 3,900-entry word list with French glosses and translated examples; the Picard column's reference | `scripts/audit_grid_sources.py fetch` | Chés Diseux, "mes mots à mi", ches.diseux.free.fr; 12 pages |
| `data/sources/wiktionary/wawiktionary-latest-pages-articles.xml.bz2` (+ `wa_entries.json`) | Walloon Wiktionary: 26,000 headwords in the unified spelling, with translations and a standard pronunciation; the Walloon column's reference and the Walloon reader's yardstick | `scripts/audit_grid_sources.py fetch` | dumps.wikimedia.org, CC BY-SA |
| `data/sources/wikidata_sitelinks.json` | The title of each concept's article in the Mirandese, Picard, Norman and Walloon Wikipedias | `scripts/audit_grid_sources.py fetch` | Wikidata, CC0 |
| `data/sources/wikipedia/` | Mirandese, Picard, Norman and Walloon Wikipedia dumps, read as running text | `scripts/audit_grid_sources.py fetch` | dumps.wikimedia.org, CC BY-SA |
| `data/sources/wikt_translations/{edition}.tsv` | Translation tables of 19 Wiktionary editions: the rows of the lects and of Latin | `scripts/extract_wikt_translations.py` (dumps in `xmls/`), `scripts/fetch_kaikki_translations.py` (Kaikki) | Wiktionary, CC BY-SA |
| `data/sources/wikt_entries/{edition}.tsv` | Ten editions' own entries for lect words and Latin words | `scripts/fetch_kaikki_translations.py` | Wiktionary via Kaikki, CC BY-SA |
| `data/sources/native_wikt/{lect}.jsonl` | The Lombard, Sicilian, Venetan, Aromanian, Aragonese, Occitan and Galician Wiktionaries: translations and Latin source of each headword | `scripts/extract_native_wiktionaries.py` | dumps in `xmls/`, CC BY-SA |
| `data/sources/kaikki_full/cognates.tsv` | Cognates named beside a Latin source in Wiktionary etymologies | `scripts/fetch_kaikki_cognates.py` | Kaikki, CC BY-SA |
| `data/sources/kaikki_full/{fr,es,pt,it,ro}_forms.tsv` | Every inflected form with its headword, for reading the modern Bibles | `scripts/fetch_kaikki_full.py --forms` | Kaikki, CC BY-SA |
| `data/sources/wikipedia/latin_titles.tsv` (+ two `lawiki` tables) | Latin Wikipedia titles paired with the lects' titles for the same article | `scripts/fetch_wikipedia_titles.py` | dumps.wikimedia.org, CC BY-SA |
| `data/bible/lects/{lect}[-variety].tsv` | Bible text in the lects, one verse per row: 34 texts for 20 lects | `data/bible/lects/fetch_italy.py`, `fetch_west_balkan.py`; read by `scripts/align_bible.py` | [`sources_bible_lexicon.md`](sources_bible_lexicon.md) |
| `data/bible/lexicon/anchor_keys.tsv`, `aligned/{lect}.tsv` | Each Latin word's counterpart in the five modern Bibles and in the lects' own texts | `scripts/align_bible.py` | derived |
| `data/sources/glossaries/{lect}/*.tsv` | Dictionaries and glossaries of the lects as headword, gloss, gloss language, part of speech; each with its parser | read by `scripts/bible_coverage.py` | [`sources_bible_lexicon.md`](sources_bible_lexicon.md) |
| `docs/assets/reference-screenshot.png` | Project reference image | documentation only | formerly a root-level screenshot |
| `data/sources/apprendeneolatino/` | The Neolatin lesson site, 187 pages as HTML: the model for the layout and lesson tree of `site/` | `scripts/scrape_apprendeneolatino.py` (structure only; see `site/README.md`) | apprendeneolatino.com, fetched with Scrapling on 7 October 2026; all rights with its authors |

Generated `data/words/*_words.json`, candidates, and evaluations are derived
artifacts. Source snapshots may be regenerated without changing the grammar or
the objective.
