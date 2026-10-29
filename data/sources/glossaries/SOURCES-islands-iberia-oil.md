# Glossary sources: sc, mwl, lad, co, ext, pcd, gallo, nrf, gsc

Written 2026-10-06 at a forced wrap-up (usage limit). Everything below describes what is on disk
under `data/sources/glossaries/{lect}/`. Tables have the header `headword gloss gloss_lang pos`
unless noted. Nothing was committed; no tracked file was touched.

**How to read "sample".** Two different checks exist, and they are not equal:

- **measured**: I read 50 random rows and counted those with the right headword and the right
  gloss, as the source gives them. Done for every table built from structured data or from a
  proofread transcription.
- **read at wrap-up**: the OCR-derived tables were built by three helper agents that were cut off
  before reporting. Their own checks are lost. I read 50 random rows of each afterwards and judged
  them on plausibility only (garbled headword, truncated or non-gloss text). **None of these was
  compared with the page scans**, so a plausible-looking but misread headword counts as right
  here. Treat the figures as upper bounds.

Rights: "PD" rows give publication year and author's death year; `NOT_IN_COPYRIGHT` is
archive.org's own `possible-copyright-status` field where I saw it. I did not verify death years
against an authority file; those marked (unverified) are from memory or not found.

**`.doubtful.tsv`.** `scripts/bible_coverage.py` reads every `{lect}/*.tsv` and skips names
containing `.doubtful`. At wrap-up I renamed seven tables that way, and changed the output name in
their parsers to match, so that nothing below the bar is counted without a decision:
`pcd/hecart-1834-rouchi`, `nrf/fleury-1886-hague`, `nrf/joret-1881-bessin` (existed before; under
85 % on my read), and `pcd/corblet-1851`, `pcd/corblet-1851-old-picard`, `pcd/ledieu-1893-demuin`,
`gallo/coulabin-1891-rennes` (written at wrap-up by parsers nobody had signed off). Renaming one
back is all it takes to count it. The three that existed before were being read by the coverage
script until now, so its next run will show lower Picard and Norman counts.

## Sardinian (sc)

| table | variety | source | licence basis | rows / headwords | sample |
|---|---|---|---|---|---|
| `apertium-srd-ita-lsc.tsv` | LSC (Limba Sarda Comuna) | Apertium Sardinian-Italian bilingual dictionary, Apertium contributors, ongoing (fetched 2026-10-05). https://github.com/apertium/apertium-srd-ita | GPL-3.0 (repository licence) | 24,908 / 20,654, glosses it | measured 50/50 |
| `apertium-cat-srd-lsc.tsv` | LSC | Apertium Catalan-Sardinian bilingual dictionary. https://github.com/apertium/apertium-cat-srd | GPL-3.0 | 22,076 / 17,212, glosses ca | measured 50/50 (2 of the 50 are doubtful translations in the source itself) |

Proper nouns, acronyms and single letters are left out. Parsers: `parse_apertium-srd-ita-lsc.py`,
`parse_apertium-cat-srd-lsc.py`.

In `sc/raw/`, not parsed: `vocabolariosardo00spanuoft_djvu.txt` (Spano, Vocabolario
sardo-italiano e italiano-sardo, 1851-52; Spano d. 1878; NOT_IN_COPYRIGHT) and
`dizionariusardui00porruoft_djvu.txt` (Porru, Dizionariu sardu-italianu, 2nd ed. 1866; Porru
d. 1836). Both are archive.org OCR whose small-capital headwords are badly misread
(`AccHiccHiAMENTL'`, `Bjssìnu`); the two Google scans of Spano are worse. No table: OCR too poor.

## Mirandese (mwl)

No table. `mwl/raw/` holds:

- `estudosdephilolo01vascuoft_djvu.txt`, `estudosdephilolo02vascuoft_djvu.txt`: archive.org OCR of
  J. Leite de Vasconcelos, Estudos de philologia mirandesa, 2 vols, 1900-01 (author d. 1941;
  NOT_IN_COPYRIGHT). Vol. 2 pp. 149-227 is a "Vocabulário etymologico" of about 700 entries, each
  `headword — Portuguese gloss` followed by `Hist. Lat. etymon`.
- `V.IIESTUDOSDEPHILOLOGIAMIRANDESAVOL.2_djvu.txt`: a better OCR (ABBYY 9) of vol. 2 from the
  archive.org item of that name.
- `leite-1901-vol2-vocabulary-pages/`: 69 of the 79 page images of that vocabulary (leaves
  n158-n236 of `estudosdephilolo02vascuoft`) with my Tesseract `por` reading of each. The run was
  cut off; leaves are missing at the end.

State: the headwords are in bold italic with long s (`ſ`) and tildes. Every OCR reads `ſ` as
`f`, `j` or `/` (`acuſar` -> `acufar`, `acujar`), drops cedillas in italics and reads initial
`lh` as `Ih`. Tesseract is clearly the best reading but single-witness precision is below 85 %.
The plan I did not finish: accept a headword only where Tesseract and an ABBYY text agree letter
for letter, and drop headwords with a medial `f` unless the Portuguese gloss has one.
`draft_parse_leite-1901-vocabulary.UNFINISHED.py` is the prototype entry splitter (prints, writes
nothing); `ocr_leite-1901-vocabulary.UNFINISHED.sh` is the download-and-OCR loop.

## Ladino (lad)

| table | variety | source | licence basis | rows / headwords | sample |
|---|---|---|---|---|---|
| `kantoniko-jeneral.tsv` | general (origins Jeneral, Ladinokomunita, Ladinadores, Aki Yerushalayim, Torah-Tanah, Otros, NA) | Kantoniko Ladino dictionary data (G. Szabo and contributors), grown from the Diksionaryo de Ladinokomunita spreadsheet (Orgun, Portal, Ruiz Tinoco); commit 671c948 of 2026-06-22. https://github.com/kantoniko/ladino-diksionaryo-data | CC BY-SA 4.0 (LICENSE and README of the repository) | 9,846 / 3,495; glosses en, es, fr, pt | measured 50/50 over all seven files |
| `kantoniko-estanbol.tsv`, `-izmir`, `-salonik`, `-balkanes`, `-gresia`, `-sarayevo` | the regional origin the entry names | same | same | 224, 149, 44, 7, 5, 2 rows | (same sample) |

Latin script throughout. Plurals, feminines of masculine entries and conjugation tables are not
taken as headwords; Turkish and Hebrew glosses are left out. Parser: `parse_kantoniko.py` (needs
PyYAML).

## Corsican (co)

| table | variety | source | licence basis | rows / headwords | sample |
|---|---|---|---|---|---|
| `apertium-cos-ita.tsv` | not stated | Apertium Corsican-Italian bilingual dictionary. https://github.com/apertium/apertium-cos-ita | GPL-3.0 | 3,075 / 3,032, glosses it | measured 50/50 (with the two below) |
| `apertium-cos-por.tsv`, `apertium-spa-cos.tsv` | not stated | Apertium Corsican-Portuguese, Spanish-Corsican (stubs). github.com/apertium/apertium-cos-por, apertium-spa-cos | GPL-3.0 | 49, 54 rows | (same sample) |
| `cowiktionary-cismuntincu.tsv` | cismuntincu (northern), as tagged on the entry | Corsican Wiktionary, dump `cowiktionary-latest` fetched 2026-10-05. https://dumps.wikimedia.org/cowiktionary/latest/ | CC BY-SA 4.0 (site rights info) | 2,719 / 471 | measured 49/50 over the three files (the one error, a bracketed aside taken as an equivalent, is fixed) |
| `cowiktionary-pumuntincu.tsv` | pumuntincu (southern) | same | same | 2,343 / 400 | (same sample) |
| `cowiktionary-unmarked.tsv` | no tag on the entry | same | same | 6,705 / 1,231 | (same sample) |
| `cowiktionary-latin-etyma.tsv` | in a column | same; header is `headword latin_etymon variety pos` | same | 1,441 / 1,308 | measured 50/50 |

The Wiktionary tables mix two kinds of row: translations listed in a Corsican entry (glosses it,
es, fr, en, pt, ca, la) and Italian/Spanish/French/English/Latin entries whose whole definition is
a link to a Corsican word (headword = that Corsican word). Capitalised headwords are left out.
The etyma file is an extra: the Latin word each Corsican entry says it comes from.
Parsers: `parse_apertium-cos.py`, `parse_cowiktionary.py`.

In `co/raw/`, not parsed: `recueildesentenc00filiuoft_djvu.txt` (J. M. Filippi, Recueil de
sentences et dictons usités en Corse avec traduction et lexique, 1906; NOT_IN_COPYRIGHT per
archive.org; author's death year unverified). Its Corsican-French lexique has about 2,400 entries
`Headword — Gloss`; in the archive.org OCR about a quarter of the headwords are misread
(`Abuiidaiiza`). `filippi-1906-lexique-pages/` has 18 page images and two Tesseract readings of
17 of them (of 66 leaves, n30-n95); the test page read far better. Cut off;
`ocr_filippi-1906-lexique.UNFINISHED.sh` is the loop. `apertium-cos.cos.dix` is the monolingual
dictionary (no glosses).

## Extremaduran (ext)

No table; `ext/raw/` is empty. Nothing that meets the terms was found (see the report).

## Picard (pcd)

All three are archive.org scans re-read with Tesseract 5 by a helper (`reocr.py`); headwords
printed in capitals are lower-cased.

| table | variety | source | licence basis | rows / headwords | sample |
|---|---|---|---|---|---|
| `hecart-1834-rouchi.doubtful.tsv` | Rouchi (Valenciennes, French Hainaut) | G. A. J. Hécart, Dictionnaire rouchi-français, 3rd ed., 1834. https://archive.org/details/dictionnairerouc00hcuoft | PD: 1834, author d. 1838; NOT_IN_COPYRIGHT | 9,324 / 8,963, fr | read at wrap-up: about 40/50. **Under 85 %**: glosses with OCR damage, a few garbled or run-on headwords, descriptive text taken as gloss |
| `corblet-1851.doubtful.tsv` | Picardy proper (Somme and neighbours) | J. Corblet, Glossaire étymologique et comparatif du patois picard, ancien et moderne, 1851. https://archive.org/details/glossairetymol00corbuoft | PD: 1851, author d. 1886; NOT_IN_COPYRIGHT | 4,980 / 4,845, fr | read at wrap-up: about 46/50. **Table produced at wrap-up** by running the helper's parser as it was left |
| `corblet-1851-old-picard.doubtful.tsv` | Old Picard (the book's asterisked words "no longer in use") | same | same | 447 / 447 | 15 rows read, all plausible; keep out of a modern lexicon |
| `ledieu-1893-demuin.doubtful.tsv` | Démuin (Somme) | A. Ledieu, Petit glossaire du patois de Démuin, 1893. https://archive.org/details/petitglossairedu00lediuoft | PD: 1893, author d. 1912 | 1,915 / 1,787, fr | read at wrap-up: about 42/50. **Under 85 %** (truncated headwords such as `oire`, `usse`). **Produced at wrap-up** |

Also in `pcd/raw/`, re-OCRed by the helper but with no parser: `dictionnairedupa00vermuoft_tesseract.txt`
(Vermesse, Dictionnaire du patois de la Flandre française ou wallonne, 1867; d. 1865) and
`lepatoisboulonna02haig_tesseract.txt` (Haigneré, Le patois boulonnais, vol. 2, 1903). And
`apertium-pcd.pcd.dix`: a 7 KB monolingual stub, no glosses.

## Gallo (gallo)

| table | variety | source | licence basis | rows / headwords | sample |
|---|---|---|---|---|---|
| `orain-1886-ille-et-vilaine.tsv` | Ille-et-Vilaine | A. Orain, Glossaire patois du département d'Ille-et-Vilaine, 1886. archive.org scan saved as `raw/glossaire_patois_ille_vilaine.pdf` (identifier not recorded by me) | PD: 1886, author d. 1918 | 1,406 / 1,393, fr | read at wrap-up: about 48/50. Headword kept only where Tesseract and archive.org's ABBYY text agree. Several `pos` values are wrong (phrases tagged adv) |
| `coulabin-1891-rennes.doubtful.tsv` | Rennes | H. Coulabin, Dictionnaire des locutions populaires du bon pays de Rennes-en-Bretagne, 1891. https://archive.org/details/dictionnairedesl00couluoft | NOT_IN_COPYRIGHT per archive.org; author's death year unverified | 943 / 933, fr | read at wrap-up: about 44/50. **Produced at wrap-up** by running the helper's parser as left (it reads 1,485 entries and keeps 943). The book records Rennes popular speech, regional French included (`tonton`, `taper`, `dalle`) |

Also in `gallo/raw/`, not parsed: `leparlerdolois00lecouoft_djvu.txt` (Le parler dolois, Dol
area; author and rights not checked by me).

## Norman (nrf)

| table | variety | source | licence basis | rows / headwords | sample |
|---|---|---|---|---|---|
| `dubois-travers-1856-mainland.tsv` | mainland | L. Du Bois, Glossaire du patois normand, augmented by J. Travers, 1856. Project Gutenberg eBook #30904, a proofread transcription (not OCR). https://www.gutenberg.org/ebooks/30904 | PD: 1856, Du Bois d. 1855, Travers d. 1888 (unverified); Project Gutenberg public-domain text | 9,466 / 8,873, fr | measured 49/50 |
| `decorde-1852-bray.tsv` | mainland, Pays de Bray | J.-E. Decorde, Dictionnaire du patois du pays de Bray, 1852. Project Gutenberg eBook #51005, proofread (not OCR). https://www.gutenberg.org/ebooks/51005 | PD: 1852, author d. 1881; Project Gutenberg public-domain text | 3,069 / 3,036, fr | measured 50/50 |
| `metivier-1870-guernesiais.tsv` | Guernésiais | G. Métivier, Dictionnaire franco-normand ou recueil des mots particuliers au dialecte de Guernesey, 1870. https://archive.org/details/DictionnaireFranco-normand | PD: 1870, author d. 1881 | 1,451 / 1,424, fr | read at wrap-up: about 48/50. Helper's rule: two Tesseract readings (300 and 400 dpi) must agree on the headword |
| `fleury-1886-hague.doubtful.tsv` | mainland, La Hague | J. Fleury, Essai sur le patois normand de la Hague, 1886. https://archive.org/details/essisurlepatoisn00fleuuoft | PD: 1886, author d. 1894 | 2,038 / 1,916, fr | read at wrap-up: about 40/50, and Fleury's diacritics (`-âë`, `-i'ei`) come out inconsistently, so the true figure is lower. **Under 85 %**. Single OCR witness (archive.org text) |
| `joret-1881-bessin.doubtful.tsv` | mainland, Bessin | C. Joret, Essai sur le patois normand du Bessin, suivi d'un dictionnaire étymologique, 1881. https://archive.org/details/essaisurlepatois00joreuoft | PD: 1881, author d. 1914 | 2,323 / 2,233, fr | read at wrap-up: about 42/50. **Under 85 %** (truncated glosses `pi`, `v`; garbled phonetic spellings). Single OCR witness |

Dubois and Decorde print headwords in capitals; they are lower-cased, nothing else changed.

### `nrf/pending-licence/`

`sdllj-vocabulaithe-jerriais.tsv` (6,841 rows / 6,620 headwords, Jèrriais, glosses en; read
about 49/50), its parser and `raw/vocab.txt`. Source: the "Vocabulaithe Jèrriais-Angliais" that
the Section de la langue Jèrriaise of the Société Jersiaise offers as a text download ("6,500
terms in text format - downloadable"), https://members.societe-jersiaise.org/sdllj/vocab.txt.
**No licence is stated anywhere on the page or in the file**, so it does not meet the terms for a
source. It is kept in its own folder so nothing picks it up by accident; using it is the owner's
decision.

### Also in `nrf/raw/`, no table

`moisy-1887_tesseract-fra.txt` and `normand_centre_djvu.txt` (Moisy, Dictionnaire de patois
normand, 1887; d. 1886; archive.org item `normand_moisy`); `dictionnairedupa00dumuoft_djvu.txt`
(Du Méril, 1849; OCR poor); `glossairedupato00romdgoog_djvu.txt` (Romdahl, Glossaire du patois du
Val de Saire, 1881; not looked at by me); the scan PDFs.

## Gascon (gsc)

| table | variety | source | licence basis | rows / headwords | sample |
|---|---|---|---|---|---|
| `apertium-oci-fra-gascon.tsv` | Gascon (pairs marked `oci@gascon`) | Apertium Occitan-French bilingual dictionary. https://github.com/apertium/apertium-oci-fra | GPL-3.0 | 15,930 / 13,538, fr | measured 50/50 (with the Aranese file) |
| `apertium-oci-fra-aranese.tsv` | Aranese (`oci@aran`) | same | GPL-3.0 | 646 / 557, fr | (same sample) |
| `apertium-oci-fra-shared.tsv` | unmarked pairs, under the form Apertium generates for Gascon | same, with https://github.com/apertium/apertium-oci | GPL-3.0 | 26,839 / 23,015, fr | measured 49/50 (one Lengadocian-looking form, `creancièr`) |
| `apertium-oci-cat-aranese.tsv` | Aranese | Apertium Occitan-Catalan. https://github.com/apertium/apertium-oci-cat | GPL-2.0 | 2,489 / 2,164, ca | measured 49/50 (with the shared file) |
| `apertium-oci-cat-shared.tsv` | unmarked pairs, Gascon form | same | GPL-2.0 | 7,054 / 6,496, ca | (same sample) |
| `cenac-moncaut-1863-gers.tsv` | Gers, spoken (unmarked words) | J. Cénac-Moncaut, Dictionnaire gascon-français, dialecte du département du Gers, 1863. https://archive.org/details/dictionnairegas00cngoog (Tesseract re-OCR by a helper) | PD: 1863, author d. 1871; NOT_IN_COPYRIGHT | 1,794 / 1,775, fr | read at wrap-up: about 49/50 |
| `cenac-moncaut-1863-gers-dastros.tsv`, `-charters.tsv` | words the author marks as taken from the 17th-c. poet Dastros / from dated medieval charters | same | same | 425, 157 rows | not read; keep out of a modern lexicon |
| `lespy-raymond-1887-bearnais.tsv` | Béarnais, modern (headwords the book prints in capitals) | V. Lespy & P. Raymond, Dictionnaire béarnais ancien et moderne, 2 vols, 1887. https://archive.org/details/dictionnaireba01lesp, .../dictionnaireba02lesp (archive.org OCR) | PD: 1887, authors d. 1897 and 1878 | 10,837 / 8,745, fr | read at wrap-up: about 47/50 |
| `lespy-raymond-1887-bearnais-old.tsv` | Old Béarnais (entries opening in lower case) | same | same | 1,827 / 1,630 | 25 read, about 24 plausible; keep out of a modern lexicon |
| `lespy-raymond-1887-bearnais-other-forms.tsv` | lower-case forms after a capital headword: old form or local variant, the book does not say which | same | same | 3,754 / 2,986 | 25 read, about 23 plausible |

Apertium (`parse_apertium-oci.py`, one script for the five tables). The left side of an
Apertium pair is a lemma key, not a spelling: the monolingual dictionary
(`raw/apertium-oci.oci.metadix`) decides what each variety writes. The headword is therefore the
citation form that dictionary generates for the variety: `nacional` becomes Gascon `nacionau`,
`cabdèl` becomes `cabdèth` (1,242 French-side and 968 Catalan-side rows differ from the key).
Forms it only accepts on input for the variety (Lengadocian `manjar`, `uòu`) are dropped, as are
Lengadocian-only pairs (`alt="oci"`). "Shared" still means "valid for all varieties according to
Apertium"; some of it is Lengadocian in practice (`-ièr`), so it is weaker evidence for Gascon
than the marked file. Cénac-Moncaut and Lespy use their own pre-normative spellings, kept as
printed.

## Parsers without a finished table

| parser | state |
|---|---|
| `nrf/parse_moisy-1887-mainland.py` | **Crashes** (`RuntimeError: generator raised StopIteration` in `entries()`); no table. Both inputs it compares are in `nrf/raw/`. |
| `pcd/parse_corblet-1851.py` | Runs; it had written no table when the helper died. I ran it at wrap-up: tables above. Not checked against the scan. |
| `pcd/parse_ledieu-1893-demuin.py` | Same: runs, table written at wrap-up, about 84 % on a read. Needs a rule for truncated headwords. |
| `gallo/parse_coulabin-1891-rennes.py` | Same: runs, table written at wrap-up. Drops a third of the entries it finds (390 with no usable gloss, 123 where the two OCR readings disagree). |
| `mwl/draft_parse_leite-1901-vocabulary.UNFINISHED.py` | Prototype, prints only. See Mirandese. |

`*/ocr_*.py`, `pcd/reocr.py`, `nrf/ocr_tesseract.py`: the helpers' Tesseract loops (they fetch
page images from archive.org; the images are not kept). `gallo/ocr/`, `gsc/ocr/`: their OCR text.
