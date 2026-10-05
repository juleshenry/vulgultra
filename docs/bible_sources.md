# Bible source texts

Six complete Bibles, one verse per row, as raw material for a lexicon drawn
from Bible vocabulary. `scripts/fetch_bible_texts.py` downloads them into
`data/bible/raw/` and writes `data/bible/texts/{code}.tsv` (`book`, `chapter`,
`verse`, `text`) and `data/bible/freq/{code}.tsv` (`word`, `count`). `data/` is
not tracked; one command rebuilds all of it:

```sh
.venv/bin/python3 scripts/fetch_bible_texts.py
```

Counts are from the run of 2026-10-05. The eBible archives were generated on
2026-10-02; eBible regenerates them, so a later download can differ. The
Romanian file is pinned to a commit.

| Code | Edition | Licence or public-domain basis, as the source states it | Source | Books | Verses | Word forms |
|---|---|---|---|---:|---:|---:|
| `la` | Clementine Vulgate. eBible `latVUC`, described there as "Clementine Vulgate of 1598 with Glossa Ordinaria Migne edition 1880" (the gloss is in footnotes, which are not in the verse-per-line file) | "Public Domain" | <https://ebible.org/Scriptures/details.php?id=latVUC>, file <https://ebible.org/Scriptures/latVUC_vpl.zip> | 73 | 35,809 | 46,398 |
| `fr` | Louis Segond, 1910. eBible `fraLSG` | "This Bible is in the Public Domain. It is not copyrighted." | <https://ebible.org/Scriptures/details.php?id=fraLSG>, file <https://ebible.org/Scriptures/fraLSG_vpl.zip> | 66 | 31,170 | 24,735 |
| `es` | Reina-Valera, 1909. eBible `spaRV1909` | "Public Domain", "Dominio Público" | <https://ebible.org/Scriptures/details.php?id=spaRV1909>, file <https://ebible.org/Scriptures/spaRV1909_vpl.zip> | 66 | 31,084 | 28,144 |
| `pt` | Bíblia Livre, 2018: Almeida's 1819 translation (Textus Receptus edition) updated, Brazilian spelling. eBible `porbr2018` | "copyright © 2018 Diego Santos, Mario Sérgio, e Marco Teles", "made available to you under the terms of the Creative Commons Attribution license 4.0" (CC BY 4.0) | <https://ebible.org/Scriptures/details.php?id=porbr2018>, file <https://ebible.org/Scriptures/porbr2018_vpl.zip> | 66 | 31,102 | 26,079 |
| `it` | Riveduta, 1927. eBible `ita1927` | "Public Domain" | <https://ebible.org/Scriptures/details.php?id=ita1927>, file <https://ebible.org/Scriptures/ita1927_vpl.zip> | 66 | 31,102 | 31,856 |
| `ro` | Dumitru Cornilescu's translation in the "Romanian Corrected Cornilescu Version" (RCCV), file dated 2013-09-09 | "Public Domain" in the open-bibles README. Not settled: see below | <https://github.com/seven1m/open-bibles/blob/5b378569502e65f45a0b6f16687df024b2934460/README.md>, file <https://raw.githubusercontent.com/seven1m/open-bibles/5b378569502e65f45a0b6f16687df024b2934460/ron-rccv.usfx.xml> | 66 | 31,102 | 20,714 |

## Licence notes

The five eBible statements were read on each details page and again in the
`{id}_about.htm` file inside each downloaded archive, which keeps the statement
next to the text. The catalogue <https://ebible.org/Scriptures/translations.csv>
gives the same: `Copyright` is "public domain" for `latVUC`, `fraLSG`,
`spaRV1909` and `ita1927`, a copyright line for `porbr2018`, and
`Redistributable` is `True` for all five.

Portuguese is the only edition with a condition. The source asks for this
credit: "Bíblia Livre (BLIVRE), Copyright © Diego Santos, Mario Sérgio, e Marco
Teles, http://sites.google.com/site/biblialivre/ - fevereiro de 2018. Licença
Creative Commons Atribuição 4.0 Brasil". Changes to the text must be indicated.

The eBible page for `ita1927` also carries the line "The Diodati Bible was
published in 1885". The text is not Diodati's: Genesis 1:1 reads "Nel principio
Iddio creò i cieli e la terra", where eBible's Diodati (`ita1885`) has "il cielo
e la terra".

Romanian is the weak one. eBible has no complete Romanian Bible in Latin script
that is public domain or openly licensed: `ron1924` is Cornilescu 1924 in
Cyrillic script, `ronbl` (Biblia Liberă, public domain) is a New Testament only,
and `ronbtf` is marked not redistributable. The RCCV file comes from
seven1m/open-bibles, a collection of "public domain and freely licensed bibles"
whose README lists it as "Public Domain"; the README is saved beside the file as
`data/bible/raw/open-bibles-README.md`. That label is the whole basis. The
README names no rights holder or upstream for this file, eBible has no `ronrccv`
entry today, and a Wayback Machine search under `ebible.org/ronrccv` returned
nothing.

Two other sources speak to the same translation and disagree. eBible says of
its Cyrillic edition (<https://ebible.org/Scriptures/details.php?id=ron1924>):
"This Bible translation is permanently in the public domain (not copyrighted)
due to copyright expiration." GEN 1:1, PSA 23:1,
MAT 6:33, JHN 3:16 and ROM 8:28 quoted on that page match the RCCV wording once
transliterated. CrossWire's `RomCor` module, a Bible Society text of the
translation, says: "Copyrighted. Distribution permitted to CrossWire Bible
Society", and "Copyright of the Cornilescu Bible © 1924 belongs to British and
Foreign Bible Society"
(<https://www.crosswire.org/ftpmirror/pub/sword/raw/mods.d/romcor.conf>). That
module was not used. The same file gives Cornilescu's death as 1975. What
follows is an inference, not a statement by any of these sources: where the term
runs 95 years from publication, a 1924 text is out of copyright; where it runs
70 years from the translator's death, the claim would last through 2045.

## The text as stored

The eBible files are the `*_vpl.xml` member of each archive, which eBible
describes as Bible text only, with formatting, notes, introductions and
non-canonical titles removed. The Romanian USFX file has no notes; book titles
are dropped and a verse is the text between two verse markers. Psalm titles are
part of verse text in all six.

The script changes the text in four ways. It normalises to NFC and collapses
runs of whitespace. In Italian it removes 229 inline markers such as `(H24-2)`
and `(G9-51)`, which record the verse number of the printed edition, and three
chapter headings left inside verses (`Matteo Capitolo 4` at the end of
MAT 3:17, and likewise at 5:48 and 20:34). In Spanish it drops 18 verse numbers
that have no text.

Spelling is the edition's own and is not normalised:

- Latin uses `æ`, `œ`, `ë` and `j` (`cælum`, `Israël`, `ejus`): 2,914 word
  forms contain `æ` or `œ`, 1,321 contain `j`.
- Spanish has the accents of 1909: `á` 19,324 times against `a` 357, `ó` 863
  against `o` 50, `fué` 1,723 and no `fue`. The first word of a chapter is in
  capitals (`EN el principio`).
- Romanian writes `ş` and `ţ` with a cedilla (U+015F, U+0163), never the
  comma-below `ș` and `ț`: 4,954 of its 20,714 word forms, 92,757 of 697,991
  tokens. Forms will not match a comma-below word list until these are mapped.
- Italian keeps the forms of 1927 (`Iddio`, `Figliuolo`).

A word in the frequency tables is a run of letters, lowercased, with
apostrophes (`'` or `’`) and hyphens kept between letters. French and Italian
elisions therefore stay whole (`l’éternel`, `dell’eterno`: 3,791 and 3,399
forms), as do Portuguese and Romanian clitic groups (`disse-lhe`, `l-a`: 2,755
and 1,793 forms). The count of word forms is the number of rows.

## Versification

Keys are (`book`, `chapter`, `verse`) as numbered in each source file. No
mapping between numbering systems is applied, so an equal key does not always
mean the same verse.

Portuguese, Italian and Romanian have exactly the same 31,102 keys.

Spanish has those keys less 18: NUM 12:16, 29:40; 1SA 23:29; 2SA 20:26;
2CH 33:25; JOB 35:16, 38:39–41, 40:20–24; HOS 11:12; JON 1:17; ACT 19:41;
2CO 13:14. The text of those verses sits under a neighbouring number. In
NUM 13, NUM 30, 1SA 24, HOS 12 and JON 2 the Spanish verse number is one higher
than in the other three (`es` NUM 13:2 is `pt` NUM 13:1) and in JOB 39 three
higher; the last verse of the chapter then holds what is left over (`es`
JOB 39:30 runs on to the end of `pt` JOB 40:5). In JOB 40 the Spanish number is
five lower (`es` 40:1 is `pt` 40:6) and in 2CH 33:11–24 one lower, verse 10
holding two verses. In 2SA 20:25, JOB 35:15, ACT 19:40 and 2CO 13:13 two verses
are joined.

French has 31,170 keys: 114 that the other four lack, and 46 of theirs
missing. The verse count differs from Portuguese in 106 chapters. In 62 psalms
the title is numbered as verse 1 (as two verses in Psalms 51, 52, 54 and 60),
so every verse after it is one or two higher: `fr` PSA 3:1 and 3:2 together are
`pt` PSA 3:1. The other 44 chapters, in 20 books, put a chapter boundary a few
verses away or split verses differently (EXO 7–8, LEV 5–6, NUM 29–30, 1SA 20
and 23–24, JOB 38–41, ECC 4–5 and 11–12, HOS 1–2 and 11–12, JON 1–2, MIC 4–5,
NAM 1–2, among others).

Latin differs most.

- Seven books are only in the Vulgate: TOB (298 verses), JDT (346), WIS (439),
  SIR (1,592), BAR (213, six chapters), 1MA (929) and 2MA (558), 4,375 verses.
- Two shared books are longer. EST runs to 16 chapters; 10:4–16:24 (108
  verses) is only in Latin. DAN runs to 14 chapters; chapter 3 has 100 verses
  against 30, and chapters 13–14 (107 verses) are only in Latin.
- Psalms are numbered differently. Latin 1–8 are the others' 1–8; Latin 9 is
  their 9 and 10 (`la` 9:22 is `pt` 10:1); Latin 10–112 are their 11–113;
  Latin 113 is their 114 and 115 (`la` 113:9 is `pt` 115:1); Latin 114 and 115
  are their 116 (`la` 115:1 is `pt` 116:10); Latin 116–145 are their 117–146;
  Latin 146 and 147 are their 147 (`la` 147:1 is `pt` 147:12); 148–150 agree.
  Titles are numbered as in French, so within a psalm the Latin verse number
  is often one or two higher: `la` PSA 50:1–3 and `fr` PSA 51:1–3 are `pt`
  PSA 51:1.
- Outside Psalms and those additions, 60 chapters in 27 books have a different
  verse count from Portuguese: by one verse in 54 of them, by up to nine in
  the rest (JOB 41 has 25 verses in Latin and 34 in Portuguese).

Shared keys:

| Editions | Keys in common |
|---|---:|
| all six | 30,261 |
| `fr` `es` `pt` `it` `ro` | 31,047 |
| `la` and `fr` | 30,321 |
| `la` and `es` | 30,286 |
| `la` and `pt` | 30,298 |
| `la` and `it` | 30,298 |
| `la` and `ro` | 30,298 |

Latin has 31,434 keys in the 66 shared books; 1,136 of them are not in
Portuguese, and 804 Portuguese keys are not in Latin. Of the 30,261 keys common
to all six, 1,706 are in Psalms. The 1,575 of those in Psalms 10–147 pair a
Latin verse with a verse of a different psalm, or in 147 with a different part
of it. Only the 35 in Psalms 1 and 148–150 sit in psalms with the same verse
count in Latin and Portuguese. The other 28,555 keys are outside Psalms.
