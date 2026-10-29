# Transcription brief: Glavina's two Istro-Romanian glossaries (in Pușcariu, *Studii istroromâne* III, 1929)

You are transcribing two printed word lists by Andrei Glavina (1904), reprinted by Pușcariu in 1929 (public
domain), from page images into a table. Accuracy of the Istro-Romanian spelling, diacritics included, is the
whole point: the words go into a lexicon of attested forms. Never guess, never normalise, never "correct".

## Input
Directory `crops_gla/` (same folder as this brief): PNG crops `pNNNN_C1.png` (top half) and `pNNNN_C2.png`
(bottom half) of page NNNN; the two halves OVERLAP by a few lines. Open every crop of your pages with the Read
tool (it shows images). The running head says which list a page belongs to:
- "GLAVINA III" = *Glosar româno-istroromân*: each line is `Romanian word = Istro-Romanian word[, forms][: example sentence]`
- "GLAVINA IV" = *Glosar istroromân-dacoromân*: each entry is
  `Istro-Romanian word[, forms] = Romanian meaning[: example sentence]`, or, without `=`,
  `Istro-Romanian word[, forms]: description in Romanian`.
Some pages are editor's prose (introduction, remarks) with no list: write an empty file for those.
At the bottom of most pages there are footnotes in smaller type (numbered ¹), ²³) …): do NOT transcribe the
footnotes, but DO record which entries carry a footnote number (see `note` below), because the notes often
say the form is a misprint or a Daco-Romanianism.

## What to write
For each page write `vision_gla/pNNNN.tsv` (UTF-8, tab-separated, no header), one row per list entry, in order:
`list<TAB>left<TAB>right<TAB>note`
- `list`: `III` or `IV` (from the running head).
- `left`: everything printed before the `=` (for IV entries without `=`: everything before the first `:`),
  exactly as printed, but WITHOUT footnote numbers.
- `right`: everything after the `=` up to, but not including, the `:` that introduces the example sentence
  (drop the example). For IV entries without `=`: the description after the `:`, up to the first full stop
  or semicolon.
- `note`: the footnote number(s) attached to this entry, as digits separated by spaces, each prefixed by the
  side it sits on: `L23` for a number on the left of `=`, `R27` for one on the right side before the example,
  `X26` for one inside the example sentence. Empty if none. A printed "(!)" is not a footnote: keep it in the
  text where it stands.
Continuation lines of a long example belong to the entry above (and are dropped with the example).
Section letters (A, B, Cs …) are not entries. An entry cut by the overlap is written once.

## Letters (write exactly what is printed, as Unicode)
Glavina writes with his own Romanian/Croatian/Hungarian-based spelling. You will meet: ă â î ș ț (write
comma-below ș ț even if the print looks like a cedilla), é á í ó ú (acute), è à ì ò (grave — Romanian
infinitives such as `cântà`, `clădì` have a grave), ĕ ŭ ĭ (breve), ā ō ū (macron, e.g. `kōkoci`, `kuvatā`),
å (a with ring), č ć š ž, `cs`, `zs`, `lj`, `nj`, `k`. Copy each as printed. If you cannot tell which
diacritic a letter has, give your best reading and append `?` to the `note` field.

## Report back (short)
Pages done, rows per page (III and IV), pages with no list, and any systematic doubt about a letter shape.
Write each page's file as soon as you finish it (Write tool). Do not write outside `vision_gla/`. No OCR tools,
no internet: just read the images. Do the pages yourself; do not delegate.
