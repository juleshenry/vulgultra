# Transcription brief: Pușcariu 1929, "Glosar la volumul I din «Studii istroromâne»"

You are transcribing a printed Istro-Romanian → Romanian glossary (Sextil Pușcariu, *Studii istroromâne* III,
Academia Română 1929, public domain) from page images into a table. Accuracy of the headword spelling,
diacritics included, is the whole point: the words go into a lexicon of attested forms. Never guess, never
normalise, never "correct" a form to Romanian.

## Input
Directory `crops_pus/` (same folder as this brief) holds PNG crops named `pNNNN_L1.png, _L2, _L3, _R1, _R2, _R3`:
page NNNN, left column (L) then right column (R), each column cut top-to-bottom into 3 pieces that OVERLAP by
about three text lines. Reading order: L1, L2, L3, R1, R2, R3. Open every crop of your pages with the Read tool
(it shows images). Read them all; do not skip crops.

## The printed format
`h e a d w o r d[, -ending] POS = Romanian meaning ¹²/₃₄ ⁵/₆; second meaning ⁷/₈ … || Cf. o t h e r`
- Headwords (and all Istro-Romanian words) are LETTER-SPACED ("d e v e t"); Romanian text is set normally.
  Write the headword WITHOUT the letter-spacing: `devet`. Keep printed parentheses in a headword: `(a)cațå`,
  `d(e)`. If two headwords share an entry ("x si y", "x, y"), keep them as printed in the headword field.
- After the headword there may be inflection endings (", -ę", ", -sno") — put them in the `forms` column.
- POS abbreviations as printed: `sb.`, `vb. I` … `vb. IV`, `vb.`, `adj.`, `adv.`, `prep.`, `conj.`, `num.`,
  `pron.`, `interj.`, `art.` etc., sometimes with `refl.`, `trans.`; copy as printed.
- The small fractions (¹⁹/₂₃, ⁸ᵃ/₈ …) are text references: OMIT them. Omit `|| Cf. …` cross-references.
- An entry often continues with spaced phrases and their meanings ("de frikę, de milinę = de frică…").
  Those are examples: OMIT them. Keep only the meaning(s) of the headword itself: the Romanian text right after
  `=`, and further main senses separated by `;`. Short bracketed labels such as `(trans.)`, `(refl.)`,
  `(despre mână)` stay with their sense.
- Entries of the form `x v. y` (pure cross-reference, no `=`) → output with POS `v.` and gloss = the target, so
  they can be filtered later.
- Entries where the headword is only illustrated by a phrase ("dai̯ în: bog ~ sriću = noroc să dea Dumnezeu")
  → output with empty POS and the gloss starting with `în: `.
- Lines at the very top of a page/column that continue an entry from the previous page: ignore.
- Running head ("GLOSAR LA VOL. I", page number) and library stamps/watermarks: ignore.

## Letters (write exactly what is printed, as Unicode)
å (a with ring) · ă (a with breve) · â · ę (e with hook/comma below) · ẹ (e with dot below) · ọ · é á í ó ú
(acute = stress; keep it) · an acute printed on/after ę or å → `ę́`, `ǻ` (base letter + U+0301) ·
i̯ and u̯ (small arc under i/u: i + U+032F) · ț ș (comma below; old print may look like a cedilla — still write
ț ș) · ć č ś š ž ź · ń · l followed by a raised stroke/apostrophe → `l'` · γ (Greek gamma) · ŋ · ð.
Romanian meanings are in 1929 Academy spelling: copy as printed (grave accents on infinitives: `a jupuì`,
`a ridicà`; `â`, `î`, `ă`, `ș`, `ț`).
If you cannot make out a letter or diacritic with confidence, still give your best reading but set `unsure` to 1.
Do not set it to 1 routinely; do set it whenever a diacritic could be one of two.

## Output
For each page write `vision_pus/pNNNN.tsv` (UTF-8, tab-separated, no header), one row per ENTRY in reading order:
`headword<TAB>forms<TAB>pos<TAB>gloss<TAB>unsure`
- `gloss`: the Romanian meaning(s) of the headword, main senses separated by `; `, no references, no examples.
- `unsure`: 0 or 1.
An entry that straddles two crops (overlap) is written once. An entry that starts at the bottom of column R of
your last page and continues on the next page: transcribe what you can see.
Write each page's file as soon as you finish that page (use the Write tool). Do not write anything outside
`vision_pus/`. Do not use OCR tools or the internet; just read the images.

## Report back (short)
Pages done, number of rows per page, number of unsure rows, and any systematic doubt about a letter shape
(e.g. "could not tell ę from ẹ").
