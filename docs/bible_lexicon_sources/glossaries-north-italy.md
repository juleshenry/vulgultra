# Glossary sources: northern Italy and the Alps

Lects: rgn Romagnol, pms Piedmontese, lij Ligurian, lld Ladin, lmo Lombard, eml Emilian,
rm Romansh, fur Friulian, vec Venetan. Written 2026-10-05/06; the run was stopped by a usage
limit before the OCR work was finished, so this file also records what is half done.

Every table has the header `headword	gloss	gloss_lang	pos`. Each lect folder holds `raw/`
(downloads, untouched), the tables, and the `parse_*.py` that made them.

**What "sample" means below.** I printed 50 random rows of a table next to the source text and
read them; a row counts as right when the headword and the gloss are what the source gives.
Where the parser was changed after the sample was read, that is said: the final file was then
not sampled again.

## Tables on disk

| lect | variety | file | rows | headwords | source | licence basis, as stated | sample |
|---|---|---|---|---|---|---|---|
| pms | not named (modern Turin-based spelling) | `pms/pmswikisource-dissionari.tsv` | 22,481 | 14,912 | Piedmontese Wikisource, "Dissionari Italian-Piemontèis" | site licence CC BY-SA 4.0 | 49/50, then parser changed |
| lld | 13 idioms, one file each | `lld/videsott-2020-vll1.{idiom}.tsv` | 79,140 in all | see below | Videsott (ed.) 2020, Vocabolar dl ladin leterar 1 | CC BY-SA 4.0, printed in the book | 48/50, then parser changed |
| lld | not named | `lld/cldr.tsv` | 634 | 634 | Unicode CLDR | Unicode License v3 | 50/50 |
| lij | not named (Genoese) | `lij/gatitos.tsv` | 4,031 | 3,324 | GATITOS | CC BY 4.0 | 50/50 |
| lij | not named | `lij/cldr.tsv` | 2,668 | 2,661 | Unicode CLDR | Unicode License v3 | 50 read before the last parser change |
| lmo | not named | `lmo/gatitos.tsv` | 4,901 | 4,039 | GATITOS | CC BY 4.0 | 50/50 |
| rm | 7 files by idiom | `rm/dewiktionary.{idiom}.tsv` | 1,214 in all | see below | German Wiktionary (Kaikki extract) | CC BY-SA 4.0 | 50/50 (idioms pooled) |
| rm | not named | `rm/cldr.tsv` | 3,069 | 3,065 | Unicode CLDR | Unicode License v3 | 50 read before the last parser change |
| fur | not named | `fur/gatitos.tsv` | 5,707 | 4,300 | GATITOS | CC BY 4.0 | 50/50 |
| fur | not named | `fur/dewiktionary.tsv` | 178 | 174 | German Wiktionary (Kaikki extract) | CC BY-SA 4.0 | 50/50 |
| fur | not named | `fur/cldr.tsv` | 557 | 557 | Unicode CLDR | Unicode License v3 | 50/50 |
| vec | not named | `vec/gatitos.tsv` | 4,793 | 3,732 | GATITOS | CC BY 4.0 | 50/50 |
| vec | not named | `vec/dewiktionary.tsv` | 157 | 150 | German Wiktionary (Kaikki extract) | CC BY-SA 4.0 | 50/50 |
| vec | Venetian (city of Venice) | `vec/gamba-1845-vocabolario-veneto-toscano.venexian.tsv` | 323 | 323 | Gamba (ed.) 1845, glossary of the Raccolta di poesie in dialetto veneziano | book: public domain (1845); transcription: CC BY-SA 4.0 | 50/50 |

rgn and eml have no table: see "Raw material without a table".

### Piedmontese Wikisource, "Dissionari Italian-Piemontèis"

- URL: https://pms.wikisource.org/wiki/Dissionari_Italian-Piemontèis (one page per letter; 28 pages fetched through the MediaWiki API: the 26 letters, the title page and one note; revision ids and dates in `pms/raw/pmswikisource_dissionari_italian_piemonteis/_revisions.json`).
- Author: the wiki's contributors; almost all of it by user Pcastellina. Latest revision seen 2026-01-11.
- What it is: a working Italian → Piedmontese glossary "for those who translate from Italian into Piedmontese for this site", about 5,100 Italian entries, by its own words "not yet a complete work". Gloss language Italian.
- Licence: the API's site-rights statement gives Creative Commons Attribution-Share Alike 4.0. Whether the compiler drew on printed dictionaries still in copyright is **unverified**.
- Parse: the dictionary is turned round, so each Piedmontese equivalent is a headword and the Italian entry word its gloss; a sub-sense in brackets stays in the gloss ("Badare (aver cura)"). Left out: usage examples in square brackets, derived words after ">", equivalents longer than four words, equivalents with a slash or a stray bracket.
- Sample: 49 of 50 right. The wrong row had lost its sub-sense (`arpròcc` glossed "Sermone" where the source says "Sermone (predicozzo)"). I then changed the parser to carry such mid-list sub-senses and to drop glosses cut in half by irregular markup; **the final file was not sampled again**.
- Note: about 2,000 rows have no part of speech (phrases inside an entry). About 135 headwords begin with a capital or an apostrophe (`Dio`, `Natal`, `‘me`); they are the source's.

### Videsott (ed.) 2020, Vocabolar dl ladin leterar 1 (VLL)

- Title: Vocabolar dl ladin leterar / Vocabolario del ladino letterario / Wörterbuch des literarischen Ladinisch, 1: Lessich documenté dant l 1879. Scripta Ladina Brixinensia V. Bozen-Bolzano University Press, 2020. ISBN 978-88-6046-168-1. Paul Videsott with D. Dellagiacoma, I. Marchione, N. Chiocchetti, G. Mischí, J. A. Dorigo; etymologies checked by O. Gsell.
- URL: https://archive.org/details/oapen-20.500.12657-22501 (OAPEN handle 20.500.12657/22501). PDF of 1,275 pages, born digital: no OCR involved.
- Licence, from the imprint page: "This work–excluding the cover and the quotations–is licensed under the Creative Commons Attribuition-ShareAlike 4.0 International License." Only lemmas, idiom forms and the Italian and German equivalents are taken; no quotation.
- What it is: every word found in Ladin literary texts written before 1879, about 5,200 lemmas. Each entry gives the form of the word in each valley idiom in today's school spelling, then per sense an Italian and a German equivalent and the list of idioms whose dictionaries record that sense. So two rows per sense: `gloss_lang` it and de.
- Idioms and files (rows / headwords): badiot = "gad." 9,617 / 3,767; badia = "Badia" 8,927 / 3,464; mareo = "mar." 6,583 / 2,420; gherdeina = "grd." 8,163 / 3,277; fascian = "fas." 8,213 / 3,313; brach 4,589 / 1,727; cazet 2,854 / 989; moenat 2,616 / 927; fodom = "fod." 8,398 / 3,434; col = "col." 3,498 / 1,319; anpezan = "amp." 7,127 / 2,845; ladin-dolomitan = "LD" 5,849 / 2,603; micura-de-ru = "MdR" 2,706 / 1,071.
  - `ladin-dolomitan` is the planned written standard, not a spoken idiom. `micura-de-ru` is the language of one author, Micurà de Rü, 1833. Decide whether either counts as an attested lect form.
- Parse rule: a form gets a row only under the senses the book lists for its idiom; mar. and Badia count as covered by gad., caz./bra./moe. by fas., col. by fod. That inheritance is my reading, not a statement of the book.
- Left out: 1,420 phrases (given only in the lemma's spelling), 255 senses of a past participle used as adjective (the idiom line holds the infinitive), 431 lemmas with no line of idiom forms. Place and personal names have pos `other`.
- Sample: 50 rows read against the PDF text: 48 right, 1 wrong, 1 I could not locate. The wrong one was a participle sense (`auzar` glossed "gehoben"); I then removed that whole class. **The final files were not sampled again.** Before that sample I had fixed a bug that leaked one sense's idioms into the next; the 50 rows were drawn after that fix.
- Not taken, and worth having: the etymology field (Ⓔ) names the Latin etymon of most lemmas in capitals ("AD + MALE HABITUS"). The four-column table has no place for it.

### GATITOS

- Title: GATITOS multilingual lexicon, distributed with the SMOL dataset. Google. I recall the paper as Jones, Caswell and others, 2023: **from memory, not checked**.
- URL: https://huggingface.co/datasets/google/smol, folder `gatitos/`, files `en_{lect}.jsonl` and `{lect}_en.jsonl`. Of the nine lects only fur, lij, lmo and vec are in it.
- Licence: the dataset card's licence field is `cc-by-4.0`.
- What it is: about 4,000 frequent English words and short phrases translated by hand; gloss language English, no part of speech, no variety named. For Lombard that matters: the spelling looks like one of the unified modern orthographies, but the source does not say which.
- Sample: 50 of 50 rows per lect reproduce a source pair exactly. The source's own choice of sense is sometimes odd for a polysemous English prompt (fur `grup` = "crops", `cicatrîs` = "pit"; lij `alimentâ` = "grocery"). Capitalisation mirrors the English ("Yes" → `Scì`).

### German Wiktionary

- URL: https://kaikki.org/dewiktionary/raw-wiktextract-data.jsonl.gz (file dated 2026-10-01, 309 MB, read as a stream by `rm/fetch_dewiktionary.py`; only the nine lects kept, in `raw/dewiktionary_north_italy.jsonl`, copied into rm/, fur/ and vec/).
- Licence: Wiktionary text is under CC BY-SA 4.0. That is Wikimedia's standing licence; I did not re-read the statement on this run.
- Counts of entries in the extract: Romansh 742, Venetian 242, Friulian 220, Piedmontese 3, Lombard 2, Ladin 2, Ligurian 1. Tables only for the first three. Inflected forms are left out.
- Romansh files by the idiom label on each sense: rumantsch-grischun 396 rows, vallader 378, puter 332, sursilvan 51, unspecified 26, surmiran 15, sutsilvan 11, engadin 5.
- Gloss: the German translation given for the sense, else the German definition as written ("der Esel"). Proper names have pos `other`.

### Unicode CLDR

- URL: https://github.com/unicode-org/cldr, branch main, `common/annotations/{rm,lij}.xml` and `common/main/{rm,lij,lld,fur}.xml`, each with its English counterpart.
- Licence: each file's header says `SPDX-License-Identifier: Unicode-3.0`.
- What it is: names of emoji and symbols (rm and lij only), of languages, scripts, countries, months, weekdays, date words and units, paired with English by key. Mostly proper names and modern terms; of little weight for a Bible lexicon beyond country names, animals and calendar words.
- Variety: not named. The Ladin file reads like Val Badia Ladin (`chësc`, `vëgn`, `mercui`): **my impression, unverified**.
- Sample: lld and fur 50/50 on the final files. For rm and lij I read 50 rows each before the last parser change (which added about 300 and 940 rows and removed abbreviations such as "last F"); the final rm and lij files were not sampled again.

### Gamba (ed.) 1845, "Vocabolario veneto-toscano"

- The four-page glossary at the end of "Raccolta di poesie in dialetto veneziano d'ogni secolo nuovamente ordinata ed accresciuta", ed. Bartolommeo Gamba, Venezia, G. Cecchini, 1845.
- URL: https://vec.wikisource.org/wiki/Raccolta_di_poesie_in_dialetto_veneziano/Vocabolario_veneto-toscano (Page namespace, pages 501–504 of the index; all four at proofread level 3).
- Licence: public domain by date of publication (1845); the transcription is under the wiki's CC BY-SA 4.0.
- Headwords keep the book's capital initial; a few are printed as two variants or with a bracket (`Zozo o zo`, `Brusa-camisa (a)`).

## Raw material without a table

### rgn Romagnol: nothing usable yet

`rgn/raw/` holds:

- `vocabolarioromag00morruoft_djvu.txt`: Antonio Morri, Vocabolario romagnolo-italiano, Faenza 1840, archive.org `vocabolarioromag00morruoft` (University of Toronto scan, 910 leaves, marked NOT_IN_COPYRIGHT). The OCR text was made with an English model and has **no accents at all**. On the one page I looked at (leaf n56) the book prints its headwords in capitals and small capitals **with** accents (`ANDÈ`, `FÈR`, `LASSÈS ANDÊ`). So every headword that carries an accent is wrong in the text. The gloss side is good: `HEADWORD, s. m. Gloss, Gloss. definition`.
- `vocabolarioroma0{0,1,2}mattgoog_djvu.txt` and one `_abbyy.gz`: Antonio Mattioli, Vocabolario romagnolo-italiano, Imola 1879, three Google scans (788, 809, 797 leaves), OCR by ABBYY FineReader 8. Layout: `Headword. ITALIAN EQUIVALENT, sf. definition`. The Italian equivalents in small capitals and the grammatical label read well. The bold headwords do not: on the one passage I compared with the page image (leaf n46 of scan 00, eight headwords) about two were exact in any one scan, and all three scans lose the same marks (`Arbaltê` comes out `Arbalte` or `Arbalté`), so voting between scans does not repair it. The scans are bitonal; Tesseract (ita+fra) on that page did no better. This is one passage, not a sample.
- `incubator_wt_rgn.jsonl`: the Romagnol test Wiktionary on Wikimedia Incubator (`Wt/rgn`, 106 pages, CC BY-SA). Definitions are written in Romagnol; only about 25 entries carry an Italian or English translation line. Not parsed.

What a table would take: the Italian side of both dictionaries can be parsed from the text on disk in an hour or two. The Romagnol headword cannot be trusted from any OCR I tried, and Romagnol spelling lives in its accents. Either a person keys the headwords from the page images (Morri is a clean colour scan), or a table is accepted with headwords "right apart from accents" and labelled so.

### eml Emilian: one promising text, not parsed

`eml/raw/b33521621_djvu.txt`: Claudio Ermanno Ferrari, Vocabolario bolognese-italiano, colle voci francesi corrispondenti, 1835, archive.org `b33521621` (Wellcome Library scan, 676 leaves). Variety: Bolognese. Public domain by date; the author's death year was not checked. Unlike the others this text is archive.org's own recent OCR (Tesseract 5.3, `fra+ita`), 86,849 lines.

State, from two stretches I read (about 120 lines): headwords stand in capitals at the start of a line and look clean (`AMMUNTAR`, `AMMUTIR`, `FIUBBA`, `FIUCCON`, `FIVRA`, `CUSSEIN`). The weak side is the Italian equivalent, set in italics straight after the headword, whose first letters are often misread (`Æfrbbia` for Fibbia, `fume` for Fiume, `Vappone` for Nappone). French equivalents follow in brackets. I was stopped before checking a page image, so whether the capital headwords carry accents in print is **unverified**.

What a table would take: a parser for `HEADWORD[, pos]. Italian … (French)`; a filter that keeps a gloss only when its words are in an Italian word list (the repo has one); then 50 rows against page images. A few hours. No table should be trusted before that check.

### pms Piedmontese: Sant'Albino pilot, OCR done for 40 pages, no parser

Vittorio di Sant'Albino, Gran dizionario piemontese-italiano, 1859. Two scans on archive.org: `bub_gb_1QKH9Ow6SXkC` (Florence national library, 1,262 leaves) and `grandizionariopi00sant` (University of Illinois, 1,270 leaves). `pms/raw/` holds both OCR texts, both PDFs (366 MB and 202 MB), and:

- `bub_gb_1QKH9Ow6SXkC_pages/`: 40 full-size page images, every thirtieth leaf from 40 to 1210.
- `bub_gb_1QKH9Ow6SXkC_tesseract/`: my Tesseract (ita+fra, tessdata_best) word tables for those 40 leaves. The folder also holds 163 header-only files left by a first run that failed (a missing config file); the runner treats them as not done and overwrites them. I deleted nothing.

Findings: archive.org's OCR of both scans mangles the bold headwords (`Argcnt` for Argent, `JrSSanì` for Arssanì). Tesseract on one full-size page of each scan gave headwords that all look plausible but one or two (`Arbraf` in one run, `Arbruf` in another): **eyeballed, not checked against the image**. The Florence PDF holds its pages only 685 px wide and is useless for OCR; page images have to be fetched one by one (1,262 requests) or from the 1.0 GB `_jp2.zip`. About 8 CPU-seconds a page.

What a table would take: fetch and read the remaining leaves (about 3 CPU-hours), do the same for the second scan, keep a headword only when both scans agree, parse `Headword. Italian equivalents. definition`, sample against images. Sant'Albino writes few accents, so this is the 19th-century dictionary most likely to clear 85%.

### lij Ligurian: Casaccia PDF, not parsed

`lij/raw/dizionariogenove00casauoft.pdf`: Giovanni Casaccia, Dizionario genovese-italiano, 1876 (archive.org `dizionariogenove00casauoft`, Toronto scan, 890 pages, full-size images in the PDF). archive.org's OCR turns the bold display type of the headwords into noise (`!Ba>da<l\lflFìa` for Badalûffa). Tesseract (ita+fra) on one page got 4 of 7 headwords exact and failed on û, â and æ (`Badalùffa`, `Bæäâ`, `Boedin`); three renderings of the page disagreed on exactly those letters. Below the bar as it stands.

### vec: two more proofread pieces, downloaded, not parsed

`vec/raw/vecwikisource/`: Giovanni da Schio, Saggio del dialetto vicentino, Padova 1855, vocabulary pages 13–34 (22 pages, proofread; Vicentino). The entries are short essays (`'''Gnaro'''. Nido.` next to half a page on an etymology), so only entries with a one-line gloss would make clean rows. Also 8 pages of a "Piccolo Dizionario Vernàcolo Veronese" from V. Fontana (ed.), Il dialetto e la lingua, Verona 1924: etymological notes rather than a glossary, and the editor's death year was not checked, so its status is **unverified**.

## Tools

`north-italy-tools/ocr_pdf_tesseract.py` (re-OCR of a PDF or a folder of page images, resumable), `north-italy-tools/fetch_ia_pages.py` (page images from archive.org, one a second), `north-italy-tools/tessdata/` (Italian and French `tessdata_best` models, Apache-2.0).
