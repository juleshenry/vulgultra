# One parser per source

Each folder holds the scripts that turned one lect's dictionaries and
glossaries into the tables `scripts/bible_coverage.py` reads
(`data/sources/glossaries/{lect}/{source}.tsv`: `headword`, `gloss`,
`gloss_lang`, `pos`, and `latin_etymon` where the source names one).
[`../bible_lects/`](../bible_lects/) holds the two scripts that fetched the
lects' Bible texts into `data/bible/lects/`.

They were written source by source during the searches of 5 and 6 October
2026 and are kept as they ran. Each says at its top what it reads and how
the printed entry is laid out. They have not been reviewed beyond the sample
checks recorded in [`docs/sources_bible_lexicon.md`](../../docs/sources_bible_lexicon.md).

A parser expects to sit beside its `raw/` folder, so it runs from the data
tree, not from here:

    python3 scripts/glossaries/sync.py          # copy the scripts next to the data
    python3 data/sources/glossaries/ruq/parse_capidan-1935.py

- `parse_*.py` rebuilds a table from `raw/`.
- `ocr_*.py`, `reocr.py`, `reread_*.py` are the machine readings of page
  images (Tesseract 5; some need `numpy` and `cv2`). Their output is kept in
  `raw/`, so a table can be rebuilt without them.
- `fetch_*.py` downloads.
- A name with `UNFINISHED` is a draft that produced nothing.
- `north-italy-tools/` is shared: page download from archive.org, and a
  Tesseract wrapper.
