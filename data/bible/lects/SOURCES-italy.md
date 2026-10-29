# Bible text for the lects of Italy, the Alps and the Adriatic

Built by `fetch_italy.py` (this folder) from the files under `raw/italy/`. Run of 2026-10-05/06.

```sh
python3 data/bible/lects/fetch_italy.py            # fetch what is missing, rebuild all 25 files
python3 data/bible/lects/fetch_italy.py --check    # also compare verses per chapter with la.tsv
python3 data/bible/lects/fetch_italy.py --notes    # print every repair the script made
```

Lects covered: vec, lmo, pms, lij, eml, rgn, fur, lld, rm, sc, scn, dlm. Nothing was found for
**co** (Corsican) and **ist** (Istriot); see the end. Other `.tsv` files in this folder
(frp, gsc, oc, pcd, wa, rup, nrf …) come from other scripts.

## The texts

"Level" is Wikisource's proofreading level of the pages used: 4 validated, 3 proofread, 1 not
proofread (OCR as uploaded). "PD by age" is my statement, from the year of printing; the
translators' death years were not looked up except where given.

| File | Lect, variety | Book or passage | Translator | Year | Where from | Licence basis as the source states it | Verses |
|---|---|---|---|---|---|---|---:|
| `vec.tsv` | Venetan, Venice | MAT | Gianjacopo Fontana | 1859, London, printed for L.-L. Bonaparte | <https://vec.wikisource.org/wiki/Il_Vangelo_di_S._Matteo_volgarizzato_in_dialetto_veneziano>, pages of the index "Il Vangelo di S. Matteo volgarizzato in dialetto veneziano dal sig. Gianjacopo Fontana, Londra 1859.pdf" (scan: Google Books `K91UAAAAcAAJ`) | PD by age (1859). Wikisource text, site terms CC BY-SA 4.0. Level 3 (128 pages) | 1,070 |
| `lmo-milanese.tsv` | Lombard, Milanese | MAT | Antonio Picozzi | 1859, London, Bonaparte | <https://it.wikisource.org/wiki/Il_Vangelo_di_S._Matteo_volgarizzato_in_dialetto_milanese> | Scan is archive.org `il-vangelo-di-s-matteo-volgarizzato-in-milanese`, whose metadata says Public Domain Mark 1.0. Level 3 (126 pages), 4 (1) | 1,070 |
| `lmo-bergamasco.tsv` | Lombard, Bergamasque | MAT | Pasino Locatelli | 1860, London, Bonaparte | <https://it.wikisource.org/wiki/Il_Vangelo_di_S._Matteo_volgarizzato_in_dialetto_bergamasco> | Scan is archive.org `il-vangelo-di-s-matteo-volgarizzato-in-dialetto-bergamasco`, Public Domain Mark 1.0. Level 3 (110 pages), 4 (12) | 1,070 |
| `pms.tsv` | Piedmontese | whole Bible: the 73 books of `la.tsv` plus ESG, LJE, S3Y, SUS, BEL | "La Bibia piemontèisa", ed. Pàul E. Castlin-a (Paolo Castellina) and Majo Galin-a; Old Testament largely Majo Galin-a and Giovanna Gribaud (1980s, in the review *La Slòira*); New Testament a revision of the Piedmontese New Testament of "1841" (so the presentation page) | living text, pages last edited 2026-07-13 | <https://pms.wikisource.org/wiki/La_Bibia_piemontèisa> (1,416 pages under that title) | pms.wikisource states "Creative Commons Attribution-Share Alike 4.0" (API `rightsinfo`, kept in `raw/italy/pmsws_rights/`). See "Rights: Piedmontese" | 35,398 |
| `lij.tsv` | Ligurian, Genoese | MAT | Giuseppe Olivieri ("Gioxeppe Oivê" on the index page) | 1860, London, Bonaparte | <https://lij.wikisource.org/wiki/L'Evangeliu_segundu_Mattê>, pages of the index "U santu Evangeliu segundu Mattè.pdf" | PD by age (1860). Wikisource text. **Level 1: not proofread** | 1,070 |
| `rgn.tsv` | Romagnol, Faenza | MAT | Antonio Morri | 1864 (index page) or 1865 (Commons), London, Bonaparte | 1:1 to 7:2 from <https://wikisource.org/wiki/É_vangëli_ṡgönd_s._Matí> (level 3); the rest from the text layer of <https://commons.wikimedia.org/wiki/File:É-vangëli-ṡgönd-s.-Matí.djvu> (scan: Google Books `1d1UAAAAcAAJ`) | Commons: "Public domain". **896 of the 1,070 verses are OCR, not proofread** | 1,070 |
| `fur.tsv` | Friulian | MAT | Pietro dal Pozzo | 1860, London, Bonaparte | text layer of <https://commons.wikimedia.org/wiki/File:Pietro_dal_Pozzo_-_Il_Vangelo_di_S._Matteo_volgarizzato_in_dialetto_friulano.djvu> (scan: Google Books `PN1UAAAAcAAJ`); the it.wikisource transcription has three pages only | Commons: "Public domain". **OCR, not proofread** | 1,070 |
| `eml-bolognese.tsv`, `eml-ferrarese.tsv`, `eml-mirandolese.tsv`, `eml-modenese.tsv`, `eml-parmigiano.tsv`, `eml-reggiano.tsv` | Emilian, six towns | LUK 15:11-32 | collected by Bernardino Biondelli (1804-1886); the Bolognese is signed Camillo Minarelli in the book | 1853, *Saggio sui dialetti gallo-italici*, Milan | <https://wikisource.org/wiki/La_parobola_del_Figliol_Prodigo_LMO>, subpages 3, 9, 13, 14, 16, 17 | PD by age (1853). Wikisource text. **The spelling is the Wikisource transcriber's, not Biondelli's** (book: "Un zert òm avè du fiù … al pàder", page: "Un zert om avè dû fiû … al päder") | 22 each |
| `lld-badiot.tsv`, `lld-mareo.tsv`, `lld-gherdeina.tsv`, `lld-fascian-cazet.tsv`, `lld-fascian-brach.tsv` | Ladin: Val Badia, Mareo/Enneberg, Gherdëina, Fassa (cazet, brach) | LUK 15:11-32 | Joseph Theodor Haller | 1832 | <https://wikisource.org/wiki/Parabola_del_Figliol_Prodigo_BAD>, `…_MAR`, `…_GRD`, `…_CAZ`, `…_BRA` ("grafia originale") | PD by age (1832). Wikisource text | 22 each |
| `lld-fodom.tsv` | Ladin, Fodom | LUK 15:11-32 | Joseph Theodor Haller | 1832 | <https://wikisource.org/wiki/La_Parabola_del_Figliol_Prodigo_FOD> | PD by age. **"Grafia moderna": the editors' respelling**; Haller's own spelling of this version is not on Wikisource | 22 |
| `rm-sursilvan.tsv` | Romansh, Sursilvan | JHN 18-19 | Luci Gabriel (1597-1663), *Ilg Nief Testament* | 1648, Basel; as reprinted in C. Decurtins (d. 1916), *Rätoromanische Chrestomathie* I, Erlangen 1896, pp. 60-65 | <https://it.wikisource.org/wiki/Pagina:Decurtins_-_Rätoromanische_chrestomathie,_I.djvu/117> to `/122` | PD by age. Wikisource text. **Level 1: not proofread** | 82 |
| `rm-vallader.tsv` | Romansh, Vallader | PSA 90-106, Hebrew numbering | Jacobus Anthonius Vulpius, "Biblia pitschna" | preface dated Ftan 1666; as reprinted in Decurtins, *Chrestomathie* VI, Erlangen 1904, pp. 527-546 | <https://it.wikisource.org/wiki/Pagina:Decurtins_-_Rätoromanische_chrestomathie,_VI.djvu/545> to `/564` | PD by age. Wikisource text. Level 3 | 321 |
| `sc-logudorese.tsv` | Sardinian, Logudorese | JON | Giovanni Spano (1803-1878) | 1861, London, Bonaparte | <https://wikisource.org/wiki/Index:La_profezia_di_Giona_(Spano,_1861).djvu> | PD by age. Wikisource text. Level 4 | 48 |
| `sc-campidanese.tsv` | Sardinian, Campidanese of Cagliari | JON | Federigo Abis | 1861, London, Bonaparte | <https://wikisource.org/wiki/Index:La_profezia_di_Giona_(Abis,_1861).djvu> | PD by age. Wikisource text. Level 4 | 48 |
| `scn.tsv` | Sicilian | SNG 1:5-14, 2:9-17, 4:4-12 (**fragment**) | not stated on the pages fetched (Bonaparte's *Il Cantico de' Cantici di Salomone, volgarizzato in dialetto siciliano*); **not verified** | about 1860 (**not verified**) | <https://wikisource.org/wiki/Index:Il_Cantico_de'_Cantici_di_Salomone,_volgarizzato_in_dialetto_siciliano.djvu>, pages 10, 12, 15: the only ones transcribed | Commons marks the scan "Public domain" (Google Books `gUFQAQAAMAAJ`). **Level 1: not proofread** | 28 |
| `dlm.tsv` | Dalmatian, Vegliote | LUK 15:11-32 | Giambattista Cubich | written 1841 | <https://wikisource.org/wiki/La_parabola_del_Figliol_Prodigo_DLM>. The page names no edition; its wording agrees with the text printed in M. Bartoli, *Das Dalmatische* (Vienna 1906), compared on verses 11-12 in archive.org's OCR of `das-dalmatische` | PD by age (1841; Bartoli d. 1946). Wikisource text | 22 |

Total 42,631 verses in 25 files.

## Rights: Piedmontese

`pms.tsv` is the one text here that is not old. What the source says:

- pms.wikisource's licence for its pages is CC BY-SA 4.0 (`raw/italy/pmsws_rights/000.json`,
  `query.rightsinfo`).
- The presentation page <https://pms.wikisource.org/wiki/La_Bibia_piemontèisa/Presentassion>
  names the editors (above). 23 of its 27 revisions, 2017-2024, are by the account
  `Pcastellina` (same file). That the account is Paolo Castellina is an inference from the name.
- The same page says the version "a l'é basà an sël travaj editorial sientìfich" of the English
  NET Bible, and that the New Testament revises the nineteenth-century Piedmontese one.

Not settled by the source: whether the 1980s Old Testament of Galin-a and Gribaud was released
by its translators under the wiki's licence, and whether leaning on the NET Bible (a copyrighted
translation) matters. CC BY-SA asks for attribution and share-alike; the file is not tracked.

## Alignment with la.tsv

- The six Matthews (`vec`, `lmo-milanese`, `lmo-bergamasco`, `lij`, `rgn`, `fur`): 28 chapters,
  1,070 verses, the same number of verses as `la.tsv` in every chapter. Same for Jonah (48, 4
  chapters) and John 18-19 (40 and 42).
- `pms.tsv` follows modern numbering (Hebrew for the Old Testament, Greek for the
  deuterocanonical books). Chapters differing from `la.tsv` by more than two verses:
  GEN 40 (19 vs 23: verses 12-15 have no marker and sit inside 40:11); LEV 5 (26 vs 19) and 6
  (23 vs 30); JOB 39 (30 vs 35), 40 (24 vs 28), 41 (34 vs 25); ISA 29 (21 vs 24: the page stops
  at 21); PSA: 100 of 150 psalms, because Psalm n here is Vulgate n-1 from 10 to 147 and titles
  are not counted as verses; EST 10 (3 vs 13) and no EST 11-16 (the Greek parts are book ESG);
  DAN 3 (30 vs 100), 4 (37 vs 34) and no DAN 13-14 (books S3Y, SUS, BEL); no BAR 6 (book LJE);
  TOB (10 chapters), JDT (9), SIR (35 of 51), 1MA 1, 7, 16: translated from the Greek, other
  verse division. Every other chapter of every book is within two verses.
- `rm-vallader.tsv`: Psalm n is Vulgate n-1; verse counts are the Hebrew ones (17, 16, 15, 5,
  23, 11, 13, 12, 9, 9, 5, 8, 28, 22, 35, 45, 48).

## What the script does to the text

Everywhere: wiki markup, templates, footnotes, page headers, running heads, verse numbers and
chapter headings go; words hyphenated at a line end are joined; whitespace is collapsed; NFC.
The first word of a chapter stays in capitals as printed ("LIBRO de la generazion").

- **Verses the source runs together.** Split at the number when it stands inside the text
  (`lmo-bergamasco` 9:6, 23:11). Split by hand, at first words written into the script, where
  the source has no number: `lmo-milanese` 22:6; `lmo-bergamasco` 5:30, 9:29; `rm-vallader`
  92:6, 93:3, 104:34 (and 98:1, which has no "1.").
- **`lij.tsv`**: Cyrillic letters that the OCR put for Latin look-alikes are mapped back; verse
  numbers read "2O", "3l", "l7" are taken as 20, 31, 17; "[sic]" marks go. Other OCR slips stay
  ("i11" for "in" at 26:69).
- **`fur.tsv`, OCR part of `rgn.tsv`**: the running title and tokens made only of digits are
  removed from inside verses. What stays: lines where the OCR lost the spaces (fur 4:24, 10:37,
  12:35, 17:21, 22:2, 24:36; rgn 22 verses, among them 7:6, 8:12, 9:17, 10:22, 10:29, 10:37,
  12:21, 13:41, 13:42, 13:50, 15:8, 17:1), stray letters (fur 7:29 ends in " E", 14:36 in
  " A1", 20:1 has "AL L", 24:34 "T G"), "1" for "l" (fur 22:31, 23:20; rgn 19:6), and in rgn
  the dots of ṡ, ż, ṅ, which the OCR often drops and the proofread chapters keep.
- **`lmo-bergamasco.tsv`**: two slips of the transcription stay: "0 Pare" (26:39), "de 1:" (27:35).
- **`pms.tsv`**: a chapter page counts as its chapter whatever its `chapter=` field says;
  mistyped verse numbers take the number their neighbours leave free ("5:4" between 5:39 and
  5:41); a verse number used twice has its texts joined; the page "2Cronache 11" (a stray copy
  of 1 Chronicles 11) is skipped; section titles, footnotes, the bracketed speaker labels of the
  Song of Songs and oracle titles of Amos go, "[Intërludi]" (Selah) stays. 179 such repairs
  (`--notes`). ESG repeats chapter labels in the source and is unreliable. Three verses are the
  translators' placeholders: DEU 1:7 "-", LUK 23:17 "[...]", ROM 16:24 "[-].".
- **`rm-vallader.tsv`**: the summaries and superscriptions before verse 1, the reprint's page
  and folio marks and its marginal line numbers (isolated multiples of five) go. The reprint's
  marks of emendation stay ("E(p)[g]ipta").
- **`rm-sursilvan.tsv`**: running heads, reference letters "(a)", marginal line numbers, page
  marks, chapter summaries and the cross-references at the foot of each page go.
- **`scn.tsv`**: the three pages carry no chapter heading; chapters 1, 2 and 4 are assigned in
  the script from what the verses say.
- **Parables**: one verse per line in the source. Lines holding several verses are split at
  first words written into the script: `lld-gherdeina` (27, 28, 30, 31), `lld-fascian-cazet`
  (32), `lld-fodom` (26, 27).

## Raw files

`raw/italy/{source}/NNN.json` are MediaWiki API responses as received (wikitext with revision
ids and timestamps): `vecws_veneziano`, `itws_milanese`, `itws_bergamasco`, `lijws_genovese`,
`mulws_romagnol`, `mulws_giona_spano1861`, `mulws_giona_abis1861`, `mulws_cantico_siciliano`,
`mulws_parabola` (17 pages, Ladin and Dalmatian), `mulws_parabola_biondelli` (59 pages),
`itws_chrestomathie_i`, `itws_chrestomathie_vi`, `pmsws_bibia` (1,416 pages),
`pmsws_rights`. `commons_djvu_text` is the Commons `imageinfo` response holding the two DjVu
text layers. `raw/ebible_translations.csv` is eBible's catalogue: it has no entry for any of
the fourteen lects.

`raw/italy/rejected/` holds two archive.org OCR files that were examined and are not used:

- `lasanctabibliaqu00colo_djvu.txt`: *La Sancta Biblia … in lingua ladina d'Engiadina bassa*
  (Vallader, 1867/1870), <https://archive.org/details/lasanctabibliaqu00colo>. ü comes out as
  "ii", "ti", "tt"; the daggers of the cross-references as stray letters inside verses; chapter
  headings as "CHAP. 11.", "XL" for XI, "XXL" for XXI; about sixty verse numbers lost in
  Matthew 1-10 alone. Not clean enough to split.
- `ilgnieftestamen00gabrgoog_djvu.txt`: *Ilg Nief Testament* (Sursilvan, Chur 1820),
  <https://archive.org/details/ilgnieftestamen00gabrgoog>. 35 of 260 chapter headings and 5,584
  of 7,957 verse numbers can be recognised.

## Looked for and not found

- **Corsican**: no transcribed Bible text. Bonaparte's Matthew (1861) is a Google Books scan
  (`Yt1UAAAAcAAJ`), not on Commons or archive.org. Five Corsican versions of the Prodigal Son
  are in C. Salvioni, "Versioni sarde, corse e caprajese della parabola del figliuol prodigo"
  (1913), on archive.org with verse numbers; the OCR misreads u and o throughout ("ornimi" for
  the first noun) and the item is labelled CC BY-NC-ND 4.0 by its uploader. Not fetched.
- **Istriot**: the multilingual Wikisource has 214 Istriot pages (songs, tales, a Decameron
  novella), none biblical. The 1835 Rovigno, Valle and Dignano versions of the Prodigal Son are
  reported printed by Salvioni and Vidossich in *Archeografo Triestino* 1919; no digital text of
  it was found on archive.org or Wikisource.
- **Scans without text**: Sicilian Matthew (Scalia 1861) and Song of Songs on Commons (DjVu, empty
  text layer); Bolognese Matthew (Pepoli 1862) and the Sardinian Matthews (Spano 1858, Abis 1860)
  not found on Commons or archive.org.
