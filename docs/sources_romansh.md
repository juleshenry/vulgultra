# Romansh (`rm`) source ladder

Ordered by how well they fit **lexical ingestion** for Lacyo (not by prestige).

| Priority | Source | Format | Ingest? | Status in this repo |
|---|---|---|---|---|
| 1 | **Kaikki / Wiktextract** | JSONL | **Yes** — structured lemmas + EN glosses | `kaikki.org-dictionary-Romansh.jsonl` → `data/words/rm_words.json` (~2.3k lemmas) |
| 2 | **DRG digitization (Trier / IDRG)** | TEI / XML | **Only if bulk public dump exists** | TEI used internally; **no verified bulk public download**. Online UI: [online.drg.ch](https://online.drg.ch/). Do not scrape. |
| 3 | **DRG volumes** | PDF / scans | **No** (human reference only) | Per-article/volume PDFs exist (e.g. `online.drg.ch/pdf/DRG_01.pdf`); poor for bulk lexicon |
| 4 | **Pledari Grond** (via dicziunari pipeline) | JSON exports | **Yes, if you obtain exports legally** | [farscrl/dicziunari](https://github.com/farscrl/dicziunari) ships **scripts only**. Full data **must not** be redistributed from GitHub. Drop publisher exports into `vendor/dicziunari/db/data/` as `pledarigrond_export_json_{idiom}.json` |

## Also open / already pulled

- `xmls/wiki/rmwiki-latest-pages-articles.xml.bz2` — Romansh Wikipedia (types / running text)
- Swadesh `rm` row in `lacyo/swadesh_rest.py`

## Idioms (Pledari / dicziunari)

When exports arrive, convert separately:

- rumantschgrischun  
- sursilvan  
- sutsilvan  
- surmiran  
- puter (udg.ch on request)  
- vallader (udg.ch on request)  

## Policy

1. Prefer **Kaikki JSONL** for anything we can ingest today.  
2. Treat **DRG** as research gold — wait for a clear TEI dump or licensed export; PDFs are for reading.  
3. Treat **Pledari / dicziunari data** as rights-gated; never scrape pledarigrond.ch.  
4. Keep provenance tags on every lemma (`kaikki` / `drg` / `pledarigrond` / `rmwiki`).
