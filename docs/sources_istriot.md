# Istriot (`ist`) sources

| Source | Status | Ingest |
|---|---|---|
| **Kaikki / Wiktextract** [dictionary/Istriot](https://kaikki.org/dictionary/Istriot/) | Confirmed JSONL | **Done:** `data/words/kaikki-ist.jsonl` → `ist_words.json` (~1034 lemmas). Swadesh overlays in `IST_KAIKKI_OVERRIDES`. |
| **CABank / TalkBank** [talkbank.org/ca/access/Istriot.html](https://talkbank.org/ca/access/Istriot.html) | Live; 13 bilingual speakers | Transcripts behind **TalkBank auth** (`?f=zip` returns login). Do not scrape. User can download CHA zip after agreeing to terms → drop in `vendor/istriot/`. |
| **Verbix** [docs.verbix.com/Languages/Istriot](https://docs.verbix.com/Languages/Istriot) | Public docs page with `avì` tables + infinitive list | **One-page capture only** (no site-wide scrape): `vendor/istriot/verbix_infinitives.txt` (~135 verbs), `verbix_avi_tables.txt`. |
| **PanLex** ISO `ist` | Indexed | Snapshot/API not pulled (no convenient small dump). Optional later. |

Still far from 10k lemmas. Kaikki is the open structured stock; TalkBank is the spoken corpus once you log in.
