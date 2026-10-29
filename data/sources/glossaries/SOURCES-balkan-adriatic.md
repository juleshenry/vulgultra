# Glossary sources: Istro-Romanian, Megleno-Romanian, Istriot, Dalmatian, Aromanian

State on 6 October 2026. The work was stopped by a usage limit before it was finished: the tables listed
in section 1 exist; the jobs in section 3 are half-done. "Not measured" means nobody read a 50-row sample
against the source. All paths are relative to `data/sources/glossaries/`.

## 1. Tables on disk

Header of every table: `headword	gloss	gloss_lang	pos`.

| Lect | Table | Rows | Source | Licence basis | Sample precision |
|---|---|---|---|---|---|
| ruo | `ruo/wiktionary-kaikki.tsv` | 57 | Polish (52), Czech, German Wiktionary: Istro-Romanian entries and translation-table cells, via Kaikki raw extracts, https://kaikki.org/plwiktionary/rawdata.html (same path for cs, de) | Wiktionary text, CC BY-SA 4.0 | 12 rows read, 12 faithful to the entry; no 50-row sample (57 rows in all) |
| ruo | `ruo/wiktionary-ro.tsv` | 1 | Romanian Wiktionary dump, https://dumps.wikimedia.org/rowiktionary/latest/ | CC BY-SA 4.0 | the one row is right |
| ruq | `ruq/wiktionary-kaikki.tsv` | 43 | Polish, Russian, German Wiktionary via Kaikki | CC BY-SA 4.0 | 12 rows read, 12 faithful; no 50-row sample |
| ruq | `ruq/wiktionary-ro.tsv` | 1 | Romanian Wiktionary dump | CC BY-SA 4.0 | the one row is right |
| ist | `ist/dallazonca-1978.tsv` | 4,791 | G. A. Dalla Zonca, *Vocabolario dignanese-italiano*, ed. M. Debeljuh, Collana degli Atti del Centro di Ricerche Storiche di Rovigno 2, Trieste (LINT) 1978; scan https://archive.org/details/RovignoAtti-02-1978 | see 2.2: no open licence; public-domain argument, owner to confirm | not measured. **Letters A to D only** (a 516, b 898, c 2,277, d 1,094 rows) |
| ist | `ist/dallazonca-1978.doubtful.tsv` | 59 | same; rows the parser did not trust | same | not measured |
| ist | `ist/wiktionary-kaikki.tsv` | 257 | Polish (213 entries), Russian, Czech, Turkish Wiktionary via Kaikki | CC BY-SA 4.0 | 50 rows read, 50 faithful to the entry |
| ist | `ist/wiktionary-ro.tsv` | 4 | Romanian Wiktionary dump | CC BY-SA 4.0 | 4 rows, all right |
| dlm | `dlm/wiktionary-kaikki.tsv` | 436 | Polish (404 entries), Russian, Czech, German Wiktionary via Kaikki | CC BY-SA 4.0 | 50 rows read, 50 faithful (Polish Wiktionary files numerals as adjectives; kept as given) |
| dlm | `dlm/wiktionary-ro.tsv` | 101 | Romanian Wiktionary dump: 16 Dalmatian entries and 85 translation cells | CC BY-SA 4.0 | not measured (first rows looked right) |
| rup | `rup/cunia-2008.tsv` | 42,784 | T. Cunia, *Dictsiunar a Limbãljei Armãneascã*, early edition, December 2008 (title page: Editura Cartea Aromãnã, 2010); born-digital PDF, https://archive.org/details/DictsiunarArmanescuDec2008 ; English glosses | see 2.1 | not measured. A mechanical check found the gloss verbatim under the headword for 37 of 50 sampled rows; the 13 misses were not examined (the 8 I looked at are plausible pairs, so the check, not the row, may be at fault) |
| rup | `rup/cunia-2008-ro.tsv` | 46,611 | same; Romanian glosses | see 2.1; these glosses are taken from Papahagi 1974 | not measured |
| rup | `rup/cunia-2008-fr.tsv` | 44,700 | same; French glosses | see 2.1; taken from Papahagi 1974 | not measured |
| rup | `rup/cunia-2008.doubtful.tsv` | 486 | same; headwords that failed the parser's cross-check | see 2.1 | not measured |
| rup | `rup/wiktionary-kaikki.tsv` | 1,223 | Russian (873), Polish, Dutch, German, Czech, Turkish, Greek Wiktionary via Kaikki | CC BY-SA 4.0 | 50 rows read, 50 faithful (many are country and chemical-element names) |
| rup | `rup/wiktionary-ro.tsv` | 762 | Romanian Wiktionary dump: about 240 Aromanian entries and 617 translation cells | CC BY-SA 4.0 | 25 rows read: 24 right, 1 is an "alternative form of" note, not a meaning |

Scripts: `parse_wiktionary-kaikki.py` and `parse_wiktionary-ro.py` in each lect folder (the lect is taken
from the folder name; raw input in `raw/kaikki-*.jsonl` and `raw/rowiktionary.pages.jsonl`);
`ist/parse_dallazonca-1978.py` (+ `ocr_dallazonca.py`, `reread_dallazonca.py`); `rup/parse_cunia-2008.py`.
The Dalla Zonca and Cunia parsers were written by helpers that were cut off before they wrote their notes;
what is said about them here comes from the script headers and from the files.

## 2. What the two big sources say about reuse

### 2.1 Cunia 2008 (Aromanian)

- The author's preface, page 6 of the PDF, right column, in Aromanian: "Sh-tra si sã shtibã: cum feci cu
  tuti cãrtsãli di la Editura Cartea Aromãnã, mini nu voi s-ljau ndrepturi di “copyright”. Voi ca
  dictsiunarlu s-hibã, tri tora di oarã, fãrã “copyright”; mini voi ca itsi armãn, s-poatã s-lja pãrtsã dit
  el, s-li lucreadzã, s-li alãxeascã, s-li tipuseascã, etc. fãrã nitsiun ambodyiu (cheadicã) di partea-a
  mea." In English (my translation): "And so that it is known: as I did with all the books of Editura
  Cartea Aromãnã, I do not want to take 'copyright' rights. I want the dictionary to be, for the time
  being, without 'copyright'; I want any Aromanian to be able to take parts of it, work on them, change
  them, print them, etc., with no hindrance on my part."
- Page 3 of the PDF: he sends this version "prit internet la armãnjlji tsi vor s-u aibã" (over the internet
  to the Aromanians who want it).
- The archive.org item carries a CC0 1.0 mark. It was set by the uploader (fabricius.iucundus), not
  demonstrably by the author.
- Limits: the waiver says "for the time being" and "any Aromanian"; it names no licence. The author died in
  2016 (from memory, not checked). The dictionary compiles T. Papahagi's *Dicționarul dialectului aromân*
  (1974; Papahagi died 1977, in copyright until 2048), Mihăileanu 1901 and Dalametra 1906, and the preface
  says the Romanian and French translations are taken from Papahagi's dictionary ("turnarea-a zboarãlor tu
  limbili rumãneascã shi frãntseascã, mini u ljau dit dictsiunarlu-al Papahagi"). The English glosses are
  Cunia's own. So the English table rests on the author's waiver alone; the Romanian and French tables also
  carry Papahagi's wording, which Cunia could not waive.

### 2.2 Dalla Zonca 1978 (Istriot of Dignano)

- The volume says, on the imprint page: "Prima edizione: settembre 1978 — Proprietà letteraria riservata
  secondo le leggi vigenti — Edizioni LINT Trieste". Nothing else about reuse.
- The archive.org item has no licence field; it was uploaded by a third party into the collection
  `ricerche-storiche-rovigno`.
- The public-domain argument is mine, not the source's: the author died in 1857 (from memory, not checked
  against the volume), so the dictionary text is out of copyright; it was first printed in 1978, and the
  25-year right in previously unpublished works and the 20-year right in critical editions (Italian law)
  ran out in 2003 and 1998. The editor's presentation, introduction and notes are not public domain and
  are not in the table. Owner to confirm before use.

## 3. Half-done work

### Istro-Romanian (ruo)

All four books are public domain: Pușcariu (died 1948) and Glavina (died 1925), printed 1929; Maiorescu
(died 1864), edition of 1900; Popovici (died 1928), 1909; Byhan (died 1942), 1899. The PDFs are in
`ruo/raw/`.

| Source | Pages | Done | Where | What is left |
|---|---|---|---|---|
| S. Pușcariu, *Studii istroromâne* III (Academia Română, 1929), "Glosar la volumul I": Istro-Romanian headword, part of speech, Romanian meaning. https://archive.org/details/sextil-puscariu-studii-istroromane-vol.-3-1929 | PDF pp. 303–335 (33) | 23 pages read from the page images by a model: PDF 303–307, 311–315, 319–331; 1,122 entry rows | `ruo/raw/puscariu_1929_glosar-vol1_page-readings/pNNNN.tsv` (columns: headword, forms, pos as printed, gloss, unsure 0/1; rules in `READING-RULES.md`) | 10 pages: PDF 308–310, 316–318, 332–335 (the last one or two may hold no entries; not checked). No table built, no sample checked. Tesseract gets about two headwords in three right here (letter-spaced type with å, ę, i̯), so reading the images is the only way to exact headwords |
| A. Glavina, two word lists of 1904 reprinted in the same volume: Romanian → Istro-Romanian (list III) and Istro-Romanian → Romanian (list IV) | PDF pp. 183–214 (32, some of them editor's prose) | 11 pages read from the images: PDF 183–188, 199–203; 316 rows. Tesseract (Latin model) for all 32 pages | `ruo/raw/glavina_1904_page-readings/` (columns: list, left of `=`, right of `=`, footnote marks); `ruo/raw/puscariu_1929_tesseract-latin_pp183-214/` | 21 pages unread. OCR looked clean on the three pages I compared with the image, so a parser over the OCR may be enough; it is not written. Pușcariu's footnotes mark many of Glavina's forms as misprints or Daco-Romanianisms: rows with a footnote mark should be set aside |
| I. Maiorescu, *Itinerar în Istria și vocabular istriano-român*, 2nd ed. 1900. https://archive.org/details/ioan-maiorescu-itinerar-in-istria-1900 | PDF pp. 105–146 (42), about 1,350 words | Tesseract (ron+deu) for 6 pages, PDF 105–110 | `ruo/raw/maiorescu_1900_tesseract-ron-deu_pp105-110/` | 36 pages of OCR, then a parser (headword; German gloss in the closing parentheses). On the one page compared, OCR had the headwords right but for one (ê read as â). OCR is probably enough; not proven |
| I. Popovici, *Dialectele romîne din Istria* II (texte și glosar), Halle 1909. https://archive.org/details/josif-popovici-dialectele-romane-in-istria-partea-1-1909 (the file named "partea 1 - 1909") | printed pp. 97–168 (72), 2,748 words by the author's count, Romanian and German glosses | nothing | PDF only | Everything. The archive.org OCR and three Tesseract models all misread the italic headwords ("Ămflâ" comes out as "Îmflă", "Ámflá", "dnună"). Reading page images is the only way, and at this scan quality some diacritics are uncertain even by eye |
| A. Byhan, "Istrorumänisches Glossar", *Jahresbericht des Instituts für rumänische Sprache zu Leipzig* VI, 1899. https://archive.org/details/jahresberichtde24unkngoog | printed pp. 173–396 (224) | nothing | PDF only | Everything. Google's OCR loses the special letters; the German gloss is in italics inside running discussion. Image reading only |

### Megleno-Romanian (ruq): no table from the books

| Source | Pages | Done | Where | What is left |
|---|---|---|---|---|
| Th. Capidan, *Meglenoromânii* III, *Dicționar meglenoromân*, Academia Română, 1935 (Commons dates its copy 1933). https://archive.org/details/capidan-theodor-dictionar-meglenoroman-scan_202508 | 338 PDF pages | The helper re-ran Tesseract (Latin model, 600 dpi, hOCR with character boxes) on all 338 pages. The archive.org OCR (Tesseract 5.3) and scan are saved too | `ruq/raw/capidan_1935_tesseract-latin_hocr/` (338 `.hocr.gz` + 338 `.txt`), `ruq/raw/capidan_1935_archiveorg_*` | No parser, no table. In the archive.org OCR, headwords with special letters are wrong ("Anvâts", "AnvirzQs"); plain-letter headwords and the Romanian glosses read well. I have not looked at the new OCR. Licence: author died 1953, public domain where the term is life + 70 since 1 January 2024; United States status not checked |
| Pericle Papahagi (died 1943), *Megleno-Românii*, 1902. https://archive.org/details/pericle-papahagi-megleno-romanii-1902 | 136 PDF pages | Tesseract (Latin) for PDF pp. 50–125 (76) | `ruq/raw/papahagi_1902_tesseract-latin_hocr_pdfpp50-125/`, PDF in `ruq/raw/` | No parser. Which of those pages hold the glossary: not recorded |
| G. Weigand (died 1930), *Vlacho-Meglen*, 1892. https://archive.org/details/vlachomeglenein00weiggoog | 131 PDF pages | PDF saved | `ruq/raw/weigand_1892_vlacho-meglen.pdf` | Everything |

### Dalmatian (dlm): no table from the books

| Source | Pages | Done | Where | What is left |
|---|---|---|---|---|
| M. Bartoli (died 1946), *Das Dalmatische* II, Wien 1906, "Anhang: Vegliotisches Wortverzeichnis", cols. 169–240. https://archive.org/details/das-dalmatische (Public Domain Mark) | 36 PDF pages (odd pages 537–607) | Own OCR, first pass, on all 36 pages; a second pass re-reading single words was running when the helper stopped. OCR script and parser written | `dlm/raw/bartoli_1906_wortverzeichnis_ocr.partA.jsonl` (1,787 lines), `.partB.jsonl` (1,791 lines), `dlm/raw/bartoli_1906_hocr_cache/`, `dlm/ocr_bartoli-1906-vegliote.py`, `dlm/parse_bartoli-1906-vegliote.py` | The parser expects `raw/bartoli_1906_wortverzeichnis_ocr.jsonl`, which was never written: the two parts have to be merged (and the second pass finished or dropped), then the parser run and a sample read. No new page OCR should be needed |
| A. Ive (died 1937), *L'antico dialetto di Veglia*, Archivio Glottologico Italiano IX, 1886, "Indice lessicale", pp. 168–186. https://archive.org/details/iveanticodialettodiveglia | 19 pages | OCR script and parser written; page images downloaded | `dlm/ocr_ive-1886-veglia.py`, `dlm/parse_ive-1886-veglia.py`, `dlm/raw/ive_1886_antico_dialetto_di_veglia_jp2.zip` | The OCR output the parser expects (`raw/ive_1886_indice_lessicale_ocr.jsonl`) is not there: 19 pages of OCR, then parse and sample |

### Istriot (ist)

Dalla Zonca: the table stops at D, but the helper's re-OCR covers the whole book
(`ist/raw/dallazonca_1978_reocr_ita_words.tsv.gz`, leaves 0–394; dictionary on leaves 32–335). Running
`python3 ist/parse_dallazonca-1978.py` should give E to Z with no new OCR. I did not run it: the helper was
in the middle of a repair of initial "ò" misread as "d", using second readings that are only in
`ist/raw/unfinished_scratch/`, and a re-run may overwrite the present A–D table with a different one. No
sample has been read against the page images.

### Aromanian (rup)

| Source | Pages | Done | Where | What is left |
|---|---|---|---|---|
| Pericle Papahagi (died 1943), *Basme aromâne și glosar*, 1905, glossary pp. 507–748. https://archive.org/details/basmearomneiglo00papagoog | 244 PDF pages (538–781) | Tesseract (Latin, 400 dpi) on all 244 pages; parser written that keeps a row only when this OCR and archive.org's own OCR agree on the headword | `rup/raw/papahagi_1905_tesseract-latin/` (244 `.tsv.gz`), `rup/raw/papahagi_1905_*_djvu.txt`, `rup/parse_papahagi-1905-glosar.py` | Run the parser, read a sample. No table was produced, so I do not know how many rows survive the agreement test |
| I. Dalametra, *Dicționar macedo-român*, Academia Română, 1906. https://archive.org/details/dicionarmacedor00unkngoog | 244 PDF pages | PDF saved; test OCR of a few pages only | `rup/raw/dalametra_1906_dicionarmacedor00unkngoog.pdf` | Everything. Google's OCR text is unusable; needs a full re-OCR. Author's death year not found |
| `apertium/apertium-ron-rup` bilingual dictionary (GitHub) | 34 KB | downloaded | `rup/raw/apertium-ron-rup.ron-rup.dix` | Not parsed. The repository has no licence file (Apertium's habit is GPL; not verified here) |
| G. Weigand (died 1930), *Die Aromunen* II, 1894, glossary. https://archive.org/details/diearomunenethno02weiguoft | — | archive.org OCR text saved | `rup/raw/unfinished_scratch/weigand_1894_aromunen2_djvu.txt` | Everything |

## 4. Looked at and rejected

| Source | Reason |
|---|---|
| *Il Dalmatico* (Istituto della Enciclopedia Italiana, 2000; `data/sources/pdf/Il Dalmatico.pdf`, archive.org `il-dalmatico_202207`) | Aldo Duro's Italian translation of Bartoli 1906; the translation is in copyright (translator died 2000, from memory). The "Public Domain Mark" on archive.org was set by the uploader. Not OCRed. The 1906 German original replaces it |
| T. Papahagi, *Dicționarul dialectului aromân* (1963, 1974), scans on archive.org | Author died 1977: in copyright |
| A. Ciorănescu, *Dicționarul etimologic român* (cites Aromanian, Megleno- and Istro-Romanian cognates) through dexonline's public database (GPL v2) | Marked not distributable in dexonline's source table and absent from the public download: of 1,245,250 definitions in it, 23 cite such a form |
| Wikidata lexemes (CC0) | Too few: Aromanian 15, Dalmatian 9, Istro-Romanian 2, Megleno-Romanian 2, Istriot 1 |
| Lexibank / CLDF | Only `saenkoromance` covers these lects, and it is already in the repository |
| Zenodo | No lexical dataset for any of the five |
| PanLex | The snapshot page no longer lists downloads and the database host does not resolve; nothing obtained |
| Croatian, Venetian, Serbo-Croatian Wiktionary | 36, 14 and 0 pages mention these lects; not parsed |
| Kaikki has no Romanian edition | The Romanian Wiktionary dump was parsed instead |
| Capidan, *Meglenoromânii* on Romanian Wikisource | Only volume I (history and grammar) is transcribed; the dictionary (volume III) is a PDF on Commons with no transcription |
| `apertium/apertium-rup` | Monolingual, no glosses |
| `istro-romanian/istro-romanian.github.io` (GitHub) | Mirror of a community site; no dictionary file, no open licence |
| Google's OCR text of Dalametra 1906, Byhan 1899, Weigand 1892 | Unusable for headwords |

## 5. Leads that need the owner's decision

- In-copyright Istriot dictionaries published by the Centro di Ricerche Storiche, Rovigno, scanned on
  archive.org by a third party with no licence: Pellizzer, *Vocabolario del dialetto di Rovigno d'Istria*
  (1992, `RovignoAtti-10-1992`); Cernecca, *Dizionario del dialetto di Valle d'Istria* (1986,
  `RovignoAtti-08-1986`); Balbi and Moscarda Budić, *Vocabolario del dialetto di Gallesano d'Istria* (2003,
  `RovignoAtti-20-2003`); Cergna, *Vocabolario del dialetto di Valle d'Istria* (2016, `RovignoAtti-41-2016`);
  Forlani, botanical terms of Dignano (1988). Not downloaded. Permission would have to come from the Centro.
- Public-domain Istriot works by A. Ive on archive.org, not examined by me: *Saggi di dialetto rovignese*
  (1888, `saggididialettor00ivea`), *I dialetti ladino-veneti dell'Istria* (1900, `idialettiladino00ivegoog`),
  *Canti popolari istriani* (1877). The Istriot helper downloaded their OCR text but left no note.
- Pușcariu 1929 also prints "Listele lui Bartoli" (printed pp. 97 onward): Istro-Romanian answers for about
  650 Romanian words, village by village. Public domain; not attempted.
- Cunia's dictionary and Dalla Zonca's: see section 2.
