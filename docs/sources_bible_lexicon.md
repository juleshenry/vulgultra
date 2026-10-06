# Where the lects' Bible vocabulary comes from

Hand-written, 6 October 2026. It records every source behind the count in
[`eval/bible_coverage.md`](eval/bible_coverage.md): what it is, its licence
basis as the source states it, how far its text can be trusted, and what was
looked at and left out. The field notes of the five searches that found most
of it are kept beside this page in [`bible_lexicon_sources/`](bible_lexicon_sources/);
where a note and this page differ, this page is later.

All the data is under `data/`, which is not tracked. Nothing here is
redistributed by the repository: the scripts rebuild it from the sources.

## What changed

On 5 October only 14 of the 36 lects had a form for 2,000 of the Bible's
words by reflex and etymology, and 34 once dictionary glosses were read. All
36 are now over 2,000, and the thin ones have moved the most:

| lect | 5 October | now | of which firm |
|---|---:|---:|---:|
| Istro-Romanian | 811 | 3,078 | 542 |
| Megleno-Romanian | 1,297 | 2,622 | 737 |
| Romagnol | 2,118 | 2,844 | 1,453 |
| Piedmontese | 2,399 | 6,726 | 5,019 |
| Ligurian | 2,488 | 5,479 | 2,534 |
| Istriot | 2,603 | 5,752 | 1,900 |
| Sardinian | 2,649 | 7,020 | 4,347 |
| Dalmatian | 2,802 | 3,891 | 2,075 |
| Ladin | 2,952 | 6,018 | 2,744 |
| Lombard | 3,089 | 6,771 | 3,933 |
| Emilian | 3,153 | 4,718 | 1,222 |
| Romansh | 3,481 | 5,107 | 3,029 |
| Mirandese | 3,493 | 4,290 | 2,164 |

"Firm" is the honest column: a form that a reflex, an etymology, a cognate
note, a translation table or the lect's own Bible gives; or that two separate
sources give by gloss; or that one source gives by gloss and that has the
shape of the word's reflexes in the other lects (Romagnol *sèmpar*, glossed
"always", beside *sempre* and *siempre*). The rest are candidates found
through one dictionary gloss or through a two-step match, and need a sense
check before they compete for a root. In a sample of 25 Romagnol forms the
shape test passed, about 20 were the right word.

## The kinds of source

### 1. Wiktionary, read five more ways

All CC BY-SA. The first three need no gloss language: they tie a lect's form
to the Latin word directly.

| What | Script | Size |
|---|---|---|
| **Translation tables.** A form and a Latin word listed in one table translate the same sense. The French, Spanish, Italian, Portuguese, Catalan, Romanian, Galician and Occitan dumps in `xmls/`; the English, German, Russian, Polish, Dutch, Greek, Czech, Chinese, Japanese, Turkish and Kurdish editions streamed from Kaikki | `extract_wikt_translations.py`, `fetch_kaikki_translations.py` | 144,000 rows from the English edition, 99,000 from the French, 20,000 to 40,000 from most others |
| **Cognates named in etymologies.** The Romanian entry *apă* comes from *aqua* and names Aromanian *apã*, Megleno-Romanian *apu* | `fetch_kaikki_cognates.py` | 23,700 rows |
| **Latin Wikipedia titles.** *Camelus* is linked to the Friulian article *Camêl* | `fetch_wikipedia_titles.py` | 66,800 one-word Latin titles; a few hundred Bible words per lect |
| **The lects' own Wiktionaries.** Each entry's translations and the Latin word its etymology names: Lombard (13,400 entries with an Italian translation), Sicilian (13,500; 5,100 name a Latin source), Occitan (20,800), Galician (12,100), Venetan (1,700), Aragonese, Aromanian | `extract_native_wiktionaries.py` | |
| **Other editions' entries for lect words.** The Polish Wiktionary has 417 Dalmatian, 217 Istriot and 756 Aromanian entries; the Russian 1,435 Friulian. The same editions' Latin entries give the keys, so nobody has to read Polish | `fetch_kaikki_translations.py` | 5,000 to 20,000 lect rows per edition |
| **Lect sections of six editions**, now asked for every lect of every edition (it was a hand list) | `audit_grid_sources.py extract` | |

The Chinese, Kurdish and Japanese editions largely import the English one's
tables, so they count as one witness with it, and their headwords are not used
as keys.

### 2. The five modern Bibles, lined up with the Latin

`scripts/align_bible.py anchors`. Each word of the French, Spanish,
Portuguese, Italian and Romanian Bibles is brought to its dictionary headword
(form tables from Kaikki, `fetch_kaikki_full.py --forms`), and each Latin word
is paired with the headword that stands for it verse by verse. The Psalms are
renumbered to the Vulgate's count first. About 3,700 Latin words get a
counterpart in each language. The commonest are printed in
[`eval/bible_anchor_words.md`](eval/bible_anchor_words.md).

This is what reads the small lects' dictionaries. A Ligurian dictionary glossed
in Italian is matched to a Latin word through the Italian word the Bible uses
for it, not only through that word's Italian reflex. *Numquid* has no reflex
anywhere; the Bibles say *forse*, *acaso*, *oare*.

### 3. Bible text in the lects themselves

`scripts/align_bible.py lects`. The form standing where the Latin word stands
is an attested form of the lect for that word. Full provenance, verse counts
against the Latin and what was rejected:
[`texts-italy.md`](bible_lexicon_sources/texts-italy.md),
[`texts-west-balkan.md`](bible_lexicon_sources/texts-west-balkan.md).

| Lect | Text | Verses | Licence basis | State of the text |
|---|---|---:|---|---|
| Piedmontese | *La Bibia piemontèisa*, whole Bible, Piedmontese Wikisource | 35,398 | site licence CC BY-SA 4.0; see open questions | proofread |
| Venetan | Matthew, Fontana 1859 | 1,070 | public domain by age | proofread |
| Lombard | Matthew in Milanese (Picozzi 1859) and Bergamasque (Locatelli 1860) | 1,070 each | Public Domain Mark | proofread |
| Ligurian | Matthew in Genoese, Olivieri 1860 | 1,070 | public domain by age | scan's text, not proofread; reads clean |
| Friulian | Matthew, dal Pozzo 1860 | 1,070 | Commons: public domain | scan's text, not proofread; reads clean |
| Romagnol | Matthew in the speech of Faenza, Morri 1865 | 1,070 | Commons: public domain | proofread to 7:2; after that the scan's text, which loses the dots of ṡ ż ṅ |
| Aromanian | Matthew, Mark and eight letters, Farsherot of Albania, 2024 | 2,174 | CC BY-SA 4.0, eBible | publisher's text |
| Walloon | Matthew (Liège, 1862) and Mark (Liège, undated) | 1,069 and 676 | Wikisource CC BY-SA; see open questions | proofread |
| Occitan | Genesis in Provençal, Mistral 1910 | 1,530 | work in the public domain; see open questions | clean |
| Picard | Matthew in the speech of Amiens, Paris 1863 | 1,022 | Gallica: public domain | Gallica's raw machine reading of a phonetic spelling: unreliable word by word |
| Mirandese | Luke 1-10 and 1 Corinthians 7, Monteiro 1894 | 544 | Commons: public domain | machine reading; nasal vowels come out as other letters |
| Romansh | Psalms 90-106 in Vallader (Vulpius 1666), John 18-19 in Sursilvan (Gabriel 1648) | 321 and 82 | public domain by age | the first proofread, the second not |
| Sardinian | Jonah in Logudorese (Spano 1861) and Campidanese (Abis 1861) | 48 each | public domain by age | proofread |
| Emilian, Ladin, Dalmatian, Franco-Provençal, Norman, Gascon | the Prodigal Son, Luke 15:11-32, in six towns of Emilia, six valleys, Veglia, Vionnaz, central Normandy, the Gers | 22 each | public domain by age | Emilian in the Wikisource transcriber's spelling, Fodom in a modern respelling |
| Sicilian | three passages of the Song of Songs | 28 | Commons: public domain | not proofread |

Nothing was found for Corsican, Istriot, Asturian, Aragonese, Extremaduran,
Ladino in Latin script, Gallo, Megleno-Romanian or Istro-Romanian. The
Asturian and Galician Matthews of 1861 exist as scans only.

**How an unproofread text is used.** A form from a clean scan counts as
attested when the same spelling turns up in two verses, or a dictionary has
it. A form from a scan that goes wrong the same way every time (Romagnol after
7:2, Mirandese, Picard) counts only when a dictionary has it. Otherwise the
word is counted in the **scan** column: it is in the text, its spelling has to
be checked against the page.

### 4. Dictionaries and glossaries

Under `data/sources/glossaries/{lect}/`, each with the script that made it.
Provenance, sample checks and rejected sources:
[`glossaries-balkan-adriatic.md`](bible_lexicon_sources/glossaries-balkan-adriatic.md),
[`glossaries-north-italy.md`](bible_lexicon_sources/glossaries-north-italy.md),
[`glossaries-islands-iberia-oil.md`](bible_lexicon_sources/glossaries-islands-iberia-oil.md).
"Checked" is the share of 50 random rows with the right headword and gloss.

| Lect | Source | Rows | Licence basis | Checked |
|---|---|---:|---|---|
| Istro-Romanian | Pușcariu, glossary to *Studii istroromâne* I (1929), 23 of 33 pages read from the page images | 1,214 | public domain (d. 1948) | 13 of 13 on one column; no 50-row sample |
| Istro-Romanian | Glavina's two word lists of 1904, in the same book, 11 of 32 pages read | 272 | public domain | not checked; 59 footnoted forms set aside |
| Megleno-Romanian | Capidan, *Dicționar meglenoromân* (1935), machine reading | 1,832, of which 361 name a Latin source | public domain where the term is life + 70 (d. 1953) | one page compared; 951 entries with his special letters set aside |
| Dalmatian | Bartoli, *Das Dalmatische* II (1906), the Vegliote word list | 2,585 | public domain (d. 1946) | not sampled; 1,486 uncertain rows set aside |
| Istriot | Dalla Zonca, *Vocabolario dignanese-italiano* (written before 1857, printed 1978), whole book | 15,527 | see open questions | reproduces the earlier A-D table row for row; not sampled |
| Aromanian | Cunia, *Dictsiunar a limbãljei armãneascã* (2008): English, Romanian and French glosses | 42,784 each | author's waiver; see open questions | not measured |
| Emilian | Ferrari, *Vocabolario bolognese-italiano* (1835), machine reading | 4,045 | Public Domain Mark | headwords right on the page compared, but accents on capitals are lost: counted as scan |
| Piedmontese | *Dissionari Italian-Piemontèis*, Piedmontese Wikisource | 22,481 | CC BY-SA 4.0 | 49 of 50 |
| Ladin | Videsott (ed.), *Vocabolar dl ladin leterar* 1 (2020), eleven valley idioms | 70,600 | CC BY-SA 4.0 | 48 of 50 |
| Sardinian | Apertium Sardinian-Italian and Catalan-Sardinian | 24,908 and 22,076 | GPL | 50 of 50 |
| Ladino | Kantoniko (the Ladinokomunita dictionary data) | 10,277 | CC BY-SA 4.0 | 50 of 50 |
| Corsican | Apertium Corsican-Italian; Corsican Wiktionary, with 1,441 Latin sources | 3,075; 11,767 | GPL; CC BY-SA | 50 and 49 of 50 |
| Gascon | Apertium Occitan-French and Occitan-Catalan, the Gascon and Aranese forms; Lespy and Raymond 1887; Cénac-Moncaut 1863 | 53,000; 14,600; 2,200 | GPL; public domain | 49 to 50 of 50; the two books read for plausibility only |
| Norman | Du Bois and Travers 1856, Decorde 1852 (Project Gutenberg, proofread); Métivier 1870 (Guernsey) | 9,466; 3,069; 1,451 | public domain | 49, 50, 48 of 50 |
| Gallo | Orain 1886 | 1,406 | public domain | 48 of 50, plausibility only |
| Friulian, Ligurian, Lombard, Venetan | GATITOS (Google), 4,000 common English words translated by hand | 4,000 to 5,700 each | CC BY 4.0 | 50 of 50 |
| Romansh, Friulian, Venetan | German Wiktionary entries; Unicode CLDR names | small | CC BY-SA; Unicode licence | 50 of 50 |

Set aside and not counted:

- **Tables their parser could not vouch for** (`*.doubtful.tsv`): Hécart 1834,
  Corblet 1851 and Ledieu 1893 for Picard (16,000 rows between them), Fleury
  1886 and Joret 1881 for Norman, Coulabin 1891 for Gallo, and the uncertain
  rows of Bartoli, Capidan, Cunia and Dalla Zonca. Each was under 85% on a
  read of 50 rows.
- **An earlier stage of a lect**: medieval Béarnais and the Gascon charters.
- **Written standards that are nobody's speech**: Ladin Dolomitan and Micurà
  de Rü's common Ladin of 1833.
- **A source with no licence stated**: the Société Jersiaise's Jèrriais
  vocabulary (6,841 rows), kept in `nrf/pending-licence/` and not read.

## Open questions on licence

None of this is published by the repository, but you should know where the
footing is soft.

1. **Cunia's Aromanian dictionary.** The author's preface waives copyright
   "for the time being" for "any Aromanian" and names no licence. His English
   glosses are his own; the Romanian and French ones are taken from Papahagi's
   1974 dictionary, which is in copyright. All three tables are used for
   matching.
2. **Dalla Zonca.** The 1978 imprint reserves rights. The public-domain case
   is an argument, not a statement of the source: the author died in 1857, and
   the rights in a first printing and in a critical edition have run out. The
   editor's introduction and supplement are left out.
3. **The Piedmontese Bible.** Wikisource publishes it under CC BY-SA. Whether
   the Old Testament's translators released their text themselves, and whether
   its stated reliance on a copyrighted English Bible's editorial work matters,
   the source does not settle.
4. **The Walloon Matthew** was written in 1862 and first printed in 2022, so a
   publication right on that printing is possible. Who released the Walloon
   Mark is not verified.
5. **Mistral's Genesis.** The work is in the public domain; the e-text used
   carries a rights notice from the centre that digitised it. The same
   printing is on Occitanica under an open licence, as page images only.
6. **Capidan** died in 1953: public domain where the term is life plus 70.

## What is left to do

In order of what it would buy:

- **Istro-Romanian.** Ten pages finish Pușcariu's glossary. Glavina's other
  21 pages and Maiorescu's 1,350-word vocabulary (German glosses) can be read
  by machine. Popovici 1909 (72 pages, 2,748 words) and Byhan 1899 (224 pages)
  can only be read from the page images.
- **Megleno-Romanian.** The 951 Capidan entries set aside need reading from
  the page. Papahagi 1902 has a machine reading of its glossary pages and no
  parser. Weigand 1892 is a PDF only.
- **Romagnol.** Morri 1840 and Mattioli 1879 are on disk; the machine reading
  gets the Italian side right and the Romagnol headwords wrong. They need a
  person, or a reader, on the page images.
- **Emilian.** Ferrari's accents: the same.
- **Dalmatian.** Ive 1886, a 19-page index: page images are on disk, the
  reading was not run.
- **Mirandese.** Leite de Vasconcelos's etymological vocabulary (700 entries,
  each with its Latin source): the long s defeats one reading; two would do.
- **Ladin.** The Videsott dictionary names the Latin source of most entries;
  the parser does not keep it yet.
- **Piedmontese, Ligurian.** Sant'Albino 1859 and Casaccia 1876 are on disk
  unread.
- **Live dictionary sites not touched**, each needing permission or a bulk
  file: Casu's Logudorese dictionary, INFCOR for Corsican, Lo Congrès for
  Gascon, DEIZE for Genoese, the Rovigno Istriot dictionaries. PanLex now
  states CC BY-NC-SA and offers no file.
