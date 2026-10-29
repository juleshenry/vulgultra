# Contributing

Most of what Vulgultra is built from is in git: every glossary table, the OCR
and page readings it was parsed from, the parsers, the Wiktionary and Wikipedia
extracts, the Bible texts. What is not in git is listed, with a pinned URL and
a checksum, in [`data/sources/sources.toml`](data/sources/sources.toml), and
one command downloads it.

## Setting up

```bash
git clone https://github.com/juleshenry/vulgultra.git && cd vulgultra
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python3 scripts/fetch_sources.py status
```

One corpus is not in git: two thirds of `data/words/ext_words.json` comes
from a dictionary whose rights are reserved. Build it before the first run:

```bash
.venv/bin/python3 scripts/fetch_sources.py fetch data/sources/pdf/oscec xmls/extwiki vendor/recursos_es-ext
.venv/bin/python3 scripts/build_ext_corpus.py
```

You need the downloads only to redo a step from its raw input. Rebuilding a
glossary table from its scan needs that scan; re-extracting the translation
tables needs the Wiktionary dumps. Fetch only the part you are working on:

```bash
.venv/bin/python3 scripts/fetch_sources.py fetch data/sources/glossaries/gsc/   # one lect's scans
.venv/bin/python3 scripts/fetch_sources.py fetch xmls/frwiktionary-latest-pages-articles.xml
.venv/bin/python3 scripts/fetch_sources.py fetch                                # all of it: 15 GB once unpacked
```

The Wiktionary dumps of June 2025 that the extracts were made from have left
dumps.wikimedia.org. A fetch then takes the latest dump and says so: the
extracts in git stay the record of what was read.

## Adding a source

1. **Folder.** A dictionary or glossary goes under
   `data/sources/glossaries/{lect}/`: the download, untouched, in `raw/`; a
   `parse_{author}-{year}-{short-title}.py` beside it; and the table it writes,
   `{author}-{year}-{short-title}.tsv`, with the header
   `headword	gloss	gloss_lang	pos`. A table whose rows you do not trust
   ends in `.doubtful.tsv`.
2. **Note.** Add the source to the `SOURCES-*.md` of its region: full
   reference, URL, the licence as the source states it, and a sample: 50
   random rows read against the source, with the count that were right.
3. **Licence.** The repository is public, so a file in git is republished.
   It may go in when the work is in the public domain or under a licence that
   allows redistribution: CC0, CC BY, CC BY-SA, CC BY-NC (the project is
   non-commercial), GPL, the Unicode licence, Licence Ouverte. A table drawn
   from a share-alike source carries that licence. "All rights reserved", no
   licence at all, or a dictionary still in copyright stays out of git: add it
   to `sources.toml` as `[[local]]`, with the reason and where it came from.
4. **Git or download.** Decide for each file:

   | File | Where |
   |---|---|
   | Your own work: tables, OCR output, page readings, parsers, notes | git |
   | A download under 5 MB that may be redistributed | git |
   | A download of 5 MB or more, with a URL that will keep serving the same file | `[[file]]` in `sources.toml` |
   | Page images archive.org renders one by one | `[[pages]]` |
   | A git repository | `[[git]]`, at a commit |
   | A file a script rebuilds from another download | `[[derived]]`, with the command |

   Pin the URL: a dated Wikimedia dump, not `latest`; a commit, not a branch;
   the archive.org file, not the item page. Then:

   ```bash
   .venv/bin/python3 scripts/fetch_sources.py stub data/sources/glossaries/xx/raw/scan.pdf   # size and checksum to paste
   .venv/bin/python3 scripts/fetch_sources.py gitignore   # ignore exactly what sources.toml lists
   git status                                              # what is left is what you commit
   ```

## Licences of what is in git

[`data/sources/LICENSES.md`](data/sources/LICENSES.md) gives the licence of
each folder. The table-by-table detail is in the `SOURCES-*.md` notes, in
[`docs/sources_manifest.md`](docs/sources_manifest.md) and in
[`docs/sources_bible_lexicon.md`](docs/sources_bible_lexicon.md).

## Commits

Conventional Commits prefixes: `feat(scope): ...`, `chore(scope): ...`,
`bugfix(scope): ...`.
