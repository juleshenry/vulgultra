# Licences of the data in git

The project's data is not under one licence: each file keeps the licence of
the source it was taken from, and a table drawn from a share-alike source is
shared under that licence. The table below covers what is in git under
`data/`. What is not in git, and why, is in [`sources.toml`](sources.toml)
(`licence` of each entry; `[[local]]` for what may not be republished). The
table-by-table detail is in the `SOURCES-*.md` notes beside the files and in
[`docs/sources_manifest.md`](../../docs/sources_manifest.md).

Reuse of the non-commercial (NC) parts is limited to non-commercial use. The
GPL texts are in [`licences/`](licences/); the Creative Commons licences are
at <https://creativecommons.org/licenses/>.

## data/sources/

| Folder or file | Source | Licence | Credit |
|---|---|---|---|
| `glossaries/` | One table per source; each row of the `SOURCES-*.md` notes names its licence basis | Public domain (the 19th- and early 20th-century dictionaries, read by OCR); CC BY-SA 4.0 (Wiktionary, Wikisource, Videsott 2020, Kantoniko); CC BY 4.0 (GATITOS); GPL-2.0 or GPL-3.0 (tables from Apertium dictionaries); Unicode License v3 (CLDR) | The source named in the note |
| `glossaries/rup/cunia-2008.tsv` | T. Cunia, *Dictsiunar a limbãljei armãneascã*, 2008: the English glosses | The author's waiver in the preface: the dictionary is "for the time being, without copyright", free for any Aromanian to take from, rework and print. The Romanian and French tables, and the doubtful table that mixes them in, are left out: those glosses are Papahagi's (in copyright) | Tiberius Cunia |
| `glossaries/ist/dallazonca-1978*.tsv` | G. A. Dalla Zonca (1792–1857), *Vocabolario dignanese-italiano*, ed. M. Debeljuh, 1978 | Dalla Zonca's entries only, which are public domain; the editor's 20- and 25-year rights in the edition ran out in 1998 and 2003. The editor's introduction and notes are not in git | Dalla Zonca, ed. Debeljuh (Centro di Ricerche Storiche di Rovigno) |
| `glossaries/*/raw/*_djvu.txt` | archive.org's OCR of public-domain scans | Public domain | archive.org item named in `sources.toml` or the note |
| `glossaries/nrf/pending-licence/` | Parser only; the Jèrriais vocabulary itself is downloaded, not in git | The parser is the project's | Société Jersiaise |
| `wikt_translations/`, `wikt_entries/`, `wikt_sections.json`, `wikt_swadesh/`, `native_wikt/`, `frwikt_blocks/`, `frwikt_sections.json`, `gallo_frwikt/`, `wiktionary/wa_entries.json` | Wiktionary, read from the dumps or through Kaikki | CC BY-SA 4.0 | Wiktionary contributors |
| `jsonl/`, `kaikki_full/` | Wiktionary via Kaikki/Wiktextract | CC BY-SA 4.0 | Wiktionary contributors; kaikki.org |
| `wikipedia/` | Wikipedia dumps | CC BY-SA 4.0 | Wikipedia contributors |
| `wikidata_sitelinks.json` | Wikidata | CC0 | — |
| `saenkoromance/`, `iecor/` | Lexibank CLDF datasets (Saenko 2015; IE-CoR) | CC BY 4.0 | The datasets' `sources.bib` |
| `rvid_megleno/` | Romance Verbal Inflection Dataset 2.0, Megleno-Romanian (Beniamine, Maiden and Round 2020), <https://zenodo.org/records/4039059> | GPL-3.0 | Its `sources.bib` |
| `verbix/`, `ruo_verbix/Istroromanian.html` | Verbix conjugator and documentation | CC BY-NC 3.0 (<https://www.verbix.com/webverbix/termsofuse>) | Verbix, <https://www.verbix.com> |
| `pdf/arlp_2018_vogabulaire_ecole_picard.pdf` (+ `.txt`) | *Ech vogabulaire ed l'ecole in picard*, Agence régionale de la langue picarde, 2018 | CC BY-NC-ND, as printed in the booklet; the `.txt` is its verbatim text. No table is derived from it | Agence régionale de la langue picarde |
| `grid_columns.json`, `sources.toml`, `SOURCES-*.md` | The project | The project's | — |

## data/bible/

| Folder or file | Source | Licence | Credit |
|---|---|---|---|
| `raw/`, `texts/` | eBible `latVUC`, `fraLSG`, `spaRV1909`, `ita1927`; seven1m/open-bibles `ron-rccv` (Cornilescu 1924) | Public domain | — |
| `raw/porbr2018_vpl.zip`, `texts/pt.tsv` | Bíblia Livre, 2018 | CC BY 4.0 (Brazil) | "Bíblia Livre (BLIVRE), Copyright © Diego Santos, Mario Sérgio, e Marco Teles, http://sites.google.com/site/biblialivre/ - fevereiro de 2018. Licença Creative Commons Atribuição 4.0 Brasil" |
| `lects/*.tsv` | Bible texts in the lects; `SOURCES-italy.md` and `SOURCES-west-balkan.md` give each text | Public domain by age (printed 1648–1894) for all but the four below; where Wikisource made the transcription, the transcription is CC BY-SA 4.0 | Wikisource contributors where they transcribed; for `pcd-amienois`, "Source gallica.bnf.fr / BnF" |
| `lects/rup-farsherot.tsv` | eBible `rup`, © 2024 The Word for the World International | CC BY-SA 4.0 | The Word for the World International |
| `lects/pms.tsv`, `lects/wa-liege1862.tsv`, `lects/wa-liege-rochefort.tsv` | Piedmontese and Walloon Wikisource | The site's CC BY-SA 4.0. The translators' own release is not verified, and the two Walloon texts were first printed in 2022 | Wikisource contributors |
| `lects/raw/` | Wikisource pages, Gallica ALTO, archive.org OCR, eBible files: the downloads the texts were built from | As the text built from them | As above |

`lects/oc-provencal.tsv` is not in git: it is built from the CIEL d'Oc e-text,
whose rights are reserved (`sources.toml`).

## data/conjugation/

| Files | Source | Licence | Credit |
|---|---|---|---|
| `sources/*_verbix.json`; `dlm_diseux`, `ist_diseux`, `ruo_diseux` | Verbix | CC BY-NC 3.0 | Verbix |
| `sources/ext_diseux.json` | juanro49/recursos_es-ext | CC0-1.0 | — |
| `sources/gallo_diseux.json`, `gallo_elg.json`, `rgn_diseux.json` | French and English Wiktionary | CC BY-SA 4.0 | Wiktionary contributors |
| `sources/ruq_diseux.json` | Capidan 1925 (public domain) and RVID 2.0 | Public domain; GPL-3.0 for the RVID cells | RVID, as above |
| `sources/pcd_diseux.json` | 40 verb paradigms from Chés Diseux d'Achteure, ches.diseux.free.fr | No licence stated: verb forms, a small part of the site, given with credit | Chés Diseux d'Achteure |
| `sources/{lect}.json` | Kaikki/Wiktionary tables merged with the files above | CC BY-SA 4.0, plus the licence of each merged file | As above |

## data/words/

The per-lect corpora, built by the `scripts/build_*` and `scripts/harvest_*`
scripts. Most rows come from Wiktionary (via Kaikki or the dumps), CC BY-SA
4.0; the Mirandese rows tagged `apertium` are GPL-3.0; the `kaikki-*.jsonl`
files are Kaikki extracts, CC BY-SA 4.0. `ruo_words.json` holds 95
Istro-Romanian forms cited from Cantemir 2020, with credit in its `meta`.
`ext_words.json` is not in git: two thirds of it comes from a dictionary whose
rights are reserved (`sources.toml`).
