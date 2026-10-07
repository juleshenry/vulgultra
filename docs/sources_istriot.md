# Istriot (`ist`) sources

| Source | Status | Ingest |
|---|---|---|
| **Kaikki / Wiktextract** [dictionary/Istriot](https://kaikki.org/dictionary/Istriot/) | Confirmed JSONL | **Done:** `data/words/kaikki-ist.jsonl` → `ist_words.json` (1034 lemmas). The grid column is `_IST` in `vulgultra/swadesh_rest.py`: Wiktionary's Istriot Swadesh list plus forms its Istriot entries gloss with the concept, cell by cell in `docs/eval/grid_sources.md`. |
| **CABank / TalkBank** [talkbank.org/ca/access/Istriot.html](https://talkbank.org/ca/access/Istriot.html) | Live; 13 bilingual speakers | Transcripts behind **TalkBank auth** (`?f=zip` returns login). Do not scrape. User can download CHA zip after agreeing to terms → drop in `vendor/istriot/`. |
| **Verbix** [docs.verbix.com/Languages/Istriot](https://docs.verbix.com/Languages/Istriot) | Public docs page with `avì` tables + infinitive list | **One-page capture only** (no site-wide scrape): `vendor/istriot/verbix_infinitives.txt` (~135 verbs), `verbix_avi_tables.txt`. |
| **PanLex** ISO `ist` | Indexed | Snapshot/API not pulled (no convenient small dump). Optional later. |

Still far from 10k lemmas. Kaikki is the open structured stock; TalkBank is the spoken corpus once you log in.

Dalla Zonca's *Vocabolario dignanese-italiano* (15,527 rows) was read for the
Bible lexicon and is recorded in
[`sources_bible_lexicon.md`](sources_bible_lexicon.md). It sits under
`data/sources/glossaries/ist/` and does not feed `ist_words.json`.
