# Verse-keyed Bible text for the western and Balkan thin lects

Built by `fetch_west_balkan.py` (`python3 data/bible/lects/fetch_west_balkan.py --check --offline`
rebuilds every TSV from `raw/` and compares it with `data/bible/texts/la.tsv`).
State on 2026-10-06. Work was stopped early; the rows marked **unfinished** or **OCR** say what is wrong with them.

| file | lect | variety | book / passage | translator | year | source | licence basis as the source states it | verses kept | state |
|---|---|---|---|---|---|---|---|---|---|
| `wa-liege1862.tsv` | wa | Liège, 19th-century spelling | Matthew (whole) | F. Bailleux, N. Defrecheux, A. Hock for the Société liégeoise de littérature wallonne (commissioned by Bonaparte, from Sacy's French) | written 1862, first printed 2022 | https://wa.wikisource.org/wiki/Évangile_selon_saint_Mathieu_SLLW (28 chapter pages, via api.php) | Wikisource text, CC BY-SA 4.0; the three translators are listed there without a copyright term (19th-century authors). Death years 1866 / 1874 / 1901 are from memory, not checked. First printing was 2022 (*Li Novia Tèstamint è walon*, ed. J. Hamblenne), so a 25-year publication right on that edition is possible in the EU: not checked. | 1,069 | clean, proofread transcription |
| `wa-liege-rochefort.tsv` | wa | Liège, Feller spelling | Mark (whole) | anonymous monk of Rochefort abbey ("On p'tit monne"); typed and edited by J. Hamblenne | undated (20th c.), printed 2022 | https://wa.wikisource.org/wiki/Evandjîle_sorlon_Marc | Only the site licence (CC BY-SA 4.0). Translator anonymous and undated, so public domain cannot be shown and I could not verify who released it. **Licence unverified.** | 676 | clean text; free, line-broken modern translation with its own verse divisions |
| `rup-farsherot.tsv` | rup | Farsherot (Albania) | Matthew, Mark, 1-2 Timothy, Titus, Philemon, 1-3 John, Jude | The Word for the World Europe | 2024 | https://ebible.org/Scriptures/details.php?id=rup (`rup_vpl.zip`; USFM kept too) | "copyright © 2024 The Word for the World International … Creative Commons Attribution Share-Alike license 4.0" | 2,174 | clean |
| `oc-provencal.tsv` | oc | Provençal (Mistralian spelling) | Genesis (whole) | Frédéric Mistral (d. 1914), from the Vulgate | Paris, Champion, 1910 | https://biblio.cieldoc.com/libre/integral/libr0066.pdf (CIEL d'Oc typed e-text) | Work is public domain (1910; translator d. 1914). **But the e-text itself ends "© Centre International de l'Écrit en Langue d'Oc 1997 … Còpi interdicho … Tous droits réservés"** over its typing and layout. Your call. A scan of the 1910 printing under "Licence ouverte" is https://www.occitanica.eu/items/show/214 (image only, in `raw/`, not used). | 1,530 | clean; seven e-text slips repaired in the script |
| `pcd-amienois.tsv` | pcd | Amiens, É. Paris's phonetic spelling | Matthew | Édouard Paris (1814-1874), from Sacy's French, for Bonaparte | London 1863 | https://gallica.bnf.fr/ark:/12148/bd6t5346572x (ALTO OCR through the Gallica document API) | Gallica record: "domaine public" | 1,022 of 1,070 | **OCR, not proofread, unfinished.** Five page views are not downloaded (75, 116-118, 120). Do not trust single words. |
| `mwl-monteiro1894.tsv` | mwl | Mirandese (central, Póvoa) | Luke 1-10; 1 Corinthians 7 | Bernardo Fernandes Monteiro (c.1825-1906 per Wikisource; its template also says 1926) | *Revista de Educação e Ensino* vol. 9, 1894 | https://commons.wikimedia.org/wiki/File:Revista_de_educação_e_ensino_(Vol._9).pdf (Google Books scan; my own tesseract OCR of 40 pages, cached in `raw/ocr_mwl_revista1894/`) | Commons: "Public domain" (1894) | 544 (LUK 504, 1CO 40) | **OCR, not proofread.** Nasal vowels are wrong throughout (see below). |
| `frp-vionnaz.tsv` | frp | Vionnaz, Bas-Valais; Gilliéron's phonetic notation | Luke 15:11-32 | recorded by Jules Gilliéron (d. 1926, from memory) | *Patois de la commune de Vionnaz*, 1880 | https://fr.wikisource.org/wiki/Patois_de_la_commune_de_Vionnaz_(Bas-Valais)/Appendice/5 (Page: scans 146-148) | Wikisource, CC BY-SA 4.0; 1880 printing | 22 | clean, proofread on Wikisource; verse numbers are mine (one printed paragraph per verse, v. 12 takes two) |
| `nrf-centre-normandie.tsv` | nrf | mainland Norman, "patois du centre de la Normandie" (not Jèrriais, not Guernésiais) | Luke 15:11-32 | not named | in L. Favre, *Parabole de l'enfant prodigue en divers dialectes, patois de la France*, Niort 1879, pp. 148-149 | https://archive.org/details/paraboledelenfan00favr | no rights statement on the item; 1879 printing | 22 | I corrected the OCR against the page images in `raw/ia_paraboledelenfan00favr_pages/` (leaves 157-158); my reading, not independently checked |
| `gsc-gers.tsv` | gsc | Gascon of the Gers, 1807 spelling | Luke 15:11-32 | sent by M. Cazeaux, secretary-general of the Gers prefecture, for the 1807 survey | same book, pp. 72-74 | https://archive.org/details/paraboledelenfan00favr | as above | 22 | as above (leaves 81-83) |

## Alignment against the Vulgate (whole books)

Chapters whose verse count differs from `la.tsv` by more than two:

- `wa-liege1862`, `wa-liege-rochefort`, `rup-farsherot`, `oc-provencal`: none.
- `pcd-amienois`: chapter 10 (32 against 42: verses 5-14 are on the missing view 75), chapter 18 (28 against 35: 30-35 on missing views), chapter 19 (only 16-24; its heading is on a missing view, so the chapter number is inferred).
- `mwl-monteiro1894`: Luke 8 (53 against 56: verses 8, 20, 21 were not found by number and sit inside the verse before).

Smaller differences:

- `wa-liege1862`: Matthew 9:26 is absent from the transcription (its "26." is verse 27; renumbered in the script). Two other slips repaired: 13:31 was numbered 30, 14:34 had no number.
- `wa-liege-rochefort`: the translator's own divisions give Mark 1:46, 4:41, 9:50 and lack 8:39, 13:37; 10:8 and 15:25 have no number and sit in the verse before.
- `rup-farsherot`: modern numbering: Matthew 17:27, Mark 4:41 and 9:50, 3 John 15 exist; Mark 8:39 does not.
- `pcd-amienois`: verses with no number of their own, left inside the verse before: 3:11, 5:11, 6:32-33, 11:5, 11:11, 14:12, 17:5, 18:11, 24:15, 27:11. 28:20 ends with the colophon "FINICHMIN d' SIN MATIU".
- `mwl-monteiro1894`: Luke 1:70, 2:5, 2:28, 2:52, 6:13, 9:62 not found by number (2:53 exists instead of 2:52). 1 Corinthians 7:1 begins with a superscription sentence that is not part of the verse.

## What the two OCR files are worth

- **pcd**: Gallica's OCR (mean word confidence about 0.68). "l'" is often read as F, P, V or T ("dé F sort" for "dé l' sort"), drop capitals at chapter openings are lost or garbled, and line ends are sometimes cut. Verse boundaries are reliable; spellings are not.
- **mwl**: the print marks nasal vowels with a tilde (ã ẽ ĩ õ ũ). The OCR turns them into â ê î ô, à, ã or a bare vowel: "relaciõ" reads "relaciô", "ũ filho" reads "à filho", "fôrũ" reads "fôrã". Any ending with a nasal vowel has to be read off the scan (`raw/commons_Revista_de_educacao_e_ensino_Vol_9.pdf`, PDF pages 155-169, 186-188, 256-269, 504-511).

## In `raw/` but not turned into a TSV

- `commons_El_Evangelio_segun_San_Mateo_traducido_al_dialecto_gallego.pdf`: Galician Matthew, J. Sánchez de Santa María for Bonaparte, London 1861 (Commons, from Galiciana, "Public domain"). Image only, pages 715 px wide. A tesseract trial got about nine words in ten right on a page I checked by hand and could not be split into chapters and verses reliably, so no TSV and the OCR cache was deleted.
- `occitanica_214_mistral_genesi_1910.pdf`: page images of Mistral's Genesis (86 MB, no text layer); kept only as the openly licensed witness of the text in `oc-provencal.tsv`.
- `ia_paraboladesemina00bona_djvu.txt`: Bonaparte's Parable of the Sower in 72 languages (1857); none of these lects is in it.
- `wa_wikisource_nt_index_probe.json`: index and author pages of the Walloon New Testament; not used by the script.
