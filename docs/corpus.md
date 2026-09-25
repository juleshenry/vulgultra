# Corpus status

Bibliography and counts. Remaining *work* is in [`TODO.md`](../TODO.md).
Hole-lect notes: [`sources_romansh.md`](sources_romansh.md),
[`sources_istriot.md`](sources_istriot.md),
[`sources_ruo.md`](sources_ruo.md).

Bar: ≥10k lemmas in `{code}_words.json` **or** ≥10k Wikipedia running-text
types (`meta.n_wiki_types`). Wiki titles are not lemmas.

Scripts: `scripts/collect_10k.py`, `scripts/harvest_dump_types.py`,
`scripts/build_kaikki_corpus.py`, `scripts/extract_incubator_wt.py`.

Do not scrape Pledari, DRG, TalkBank, Verbix site-wide, or vlaski-zejanski.

## By branch (SOURCE_LANGS)

| Branch | code | lect | lemmas | wiki types | 10k |
|---|---|---|---:|---:|---|
| Ibero | es | Spanish | 39396 | 0 | lemmas |
| Ibero | pt | Portuguese | 25000 | 0 | lemmas |
| Ibero | gl | Galician | 48775 | 0 | lemmas |
| Ibero | an | Aragonese | 58746 | 488318 | both |
| Ibero | ast | Asturian | 59792 | 0 | lemmas |
| Ibero | ext | Extremaduran | book | 0 | lemmas (Carmona / GitHub) |
| Ibero | lad | Ladino | 2612 | 97202 | wiki |
| Ibero | mwl | Mirandese | 60207 | 177906 | both |
| Occitano | oc | Occitan | 235721 | 0 | lemmas |
| Occitano | ca | Catalan | 60501 | 0 | lemmas |
| Occitano | gsc | Gascon | 66615 | 0 | lemmas (`oci@gascon`) |
| Oil | fr | French | 61007 | 0 | lemmas |
| Oil | wa | Walloon | 42716 | 0 | lemmas |
| Oil | pcd | Picard | 765 | 126753 | wiki |
| Oil | nrf | Norman | 11244 | 0 | lemmas |
| Oil | glw | Gallo | 11566 | 0 | lemmas (frwiktionary) |
| Arpitan | frp | Franco-Provençal | 82 | 77352 | wiki |
| Gallo-Italian | lmo | Lombard | 35741 | 0 | lemmas |
| Gallo-Italian | pms | Piedmontese | 4053 | 205321 | wiki |
| Gallo-Italian | lij | Ligurian | 1896 | 238624 | wiki |
| Gallo-Italian | eml | Emilian | 3286 | 193327 | wiki |
| Gallo-Italian | rgn | Romagnol | 1422 | 0 | **thin** |
| Italo-Dalmatian | it | Italian | 25000 | 0 | lemmas |
| Italo-Dalmatian | scn | Sicilian | 59909 | 0 | lemmas |
| Italo-Dalmatian | vec | Venetan | 9205 | 335220 | wiki |
| Italo-Dalmatian | co | Corsican | 3046 | 139569 | wiki |
| Italo-Dalmatian | ist | Istriot | 1034 | 0 | **thin** |
| Italo-Dalmatian | dlm | Dalmatian | 1179 | 0 | **thin** |
| Rhaeto | rm | Romansh | 2325 | 138265 | wiki |
| Rhaeto | fur | Friulian | 2028 | 102924 | wiki |
| Rhaeto | lld | Ladin | 5991 | 208097 | wiki |
| Sardinian | sc | Sardinian | 103702 | 183635 | both |
| Eastern | ro | Romanian | 25000 | 0 | lemmas |
| Eastern | rup | Aromanian | 5337 | 65489 | wiki |
| Eastern | ruo | Istro-Romanian | ~519 | 0 | **thin** |
| Eastern | ruq | Megleno-Romanian | ~212 | 0 | **thin** |

Reserved (not sources): `la` Latin, `en` English.

## Thin lects (open-source ceiling)

| code | why it stops |
|---|---|
| `ist` | Kaikki max. TalkBank CHA zip is auth-gated. |
| `dlm` | Kaikki max. No Wikipedia. [`data/sources/pdf/Il Dalmatico.pdf`](../data/sources/pdf/Il%20Dalmatico.pdf) has no text layer. |
| `rgn` | Kaikki max. No Wikipedia. |
| `ruo` | Cantemir 2020 appendix. No Kaikki/wiki. Do not scrape vlaski-zejanski. |
| `ruq` | Swadesh appendix + category. No Kaikki/wiki. |

## Incubator `Wt/` (extracted 2026-09-20)

`scripts/extract_incubator_wt.py` → `xmls/incubator/{code}wiktionary-incubator-pages-articles.xml`

pms 3023, nrf 1526, pcd 768, mwl 590, egl/eml 152, lij 141, lad 107, frp 83, fur 37.

## Pulls already on disk

- Wikipedia dumps `xmls/wiki/`: an fur frp lad lij lld mwl nap pcd pms rm sc vec eml roa_rup co
- Apertium `vendor/`: arg, spa-arg, ast, spa-ast, oci, oci-spa, srd, ita-srd, scn, mwl, glg, nap, fra-cat (no official fur/lld/vec)
- Kaikki JSONL `data/words/kaikki-*.jsonl` (gitignored), with legacy-name
  snapshots in `data/sources/jsonl/` (also ignored; see the source manifest)
