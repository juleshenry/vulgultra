# Orthography sources

Where each reading in `BACKEND_LEFTOVERS` (`vulgultra/phonology_constants.py`)
comes from. A reading is the IPA value a letter has in that lect's own
spelling, for letters the borrowed G2P backend does not know. Checked
5 October 2026.

| Lect | Letter → reading | Source |
|---|---|---|
| ruo | ľ → ʎ, ń → ɲ | Same article, tables 3 and 4: the Romanian-based and mixed spellings write /ʎ/ ‹l'›/‹ľ› and /ɲ/ ‹n'›/‹ń› |
| ruo | j → j, ž → ʒ, š → ʃ, č → tʃ, lj → ʎ, nj → ɲ, å → ɒ, ę → æ | Vrzić, "Orthographic practices and social meanings: writing Istro-Romanian", *Sociolinguistica* 39(2), 2025, table 5 (Croatian-based orthography, after Vrzić 2010): /ʒ/ ‹ž›, glide ‹j›, /ɲ/ ‹nj›, /ʎ/ ‹lj›, /æ/ ‹ę›, /ɒ/ ‹å›. <https://d-nb.info/1381267149/34> |
| rgn | ẓ → ð | Wiktionary *alẓir* /al.ˈðir/ (local Kaikki dump); Wikipedia "Romagnol": z is [θ] or [ð], never an affricate |
| rgn | ș → z, ọ → o, ë → ɛ, ö → ɔ | Wiktionary *radìșa* [ɾɐˈdiːzɐ], *calurôș* [kɐluˈɾoə̯z], *fọmm* [ˈfomm], *pël* [ˈpɛːl], *öv* [ˈɔːv] (local Kaikki dump). Wikipedia "Romagnol" (Vitali 2008) gives ë [ɛə̯], ö [ɔə̯]: one syllable either way |
| rgn | ã → ə̃ | Wikipedia "Romagnol", vowel table (Vitali 2008): ã/â [ə̃] |
| rgn | ş → z | Inferred: cedilla form of ș. *uşël* is not in the dump |
| eml | ṡ → z, å → ʌ, ä → æ, final c' → ts, final g' → dz | Wikipedia "Bolognese dialect", orthography table: ṡ /z/, å /ʌ/, ä /æ/, c' /ts/, g' /dz/. The column now follows Wiktionary's Emilian Swadesh list, which is in this spelling |
| eml | ṅ → ŋ, ć → tʃ | Italian Wikipedia "Dialetto mirandolese": ‹ṅ ń› [ŋ], ‹ć c'› [tʃ]. Wikipedia "Bolognese dialect": ṅ is the velar nasal |
| lld | ë → ɐ, ö → ø, ü → y | Wikipedia "Ladin language", Vowels: "[ɐ] vowel, spelled ⟨ë⟩, as in Urtijëi"; front rounded [ø y] spelled ⟨ö, ü⟩ |
| pms | ë → ə, o → u, u → y, eu → ø | Wikipedia "Piedmontese language", alphabet table: Ë ë /ə/, O o /u/, U u /y/, eu /ø/, Ò ò /ɔ/ |
| wa | å → ɔ | Wikipedia "Walloon orthography": Feller å [ɔː], rifondou [ɔː/oː/ɑː]; Wiktionary *åbe* /ɔːp/ (local Kaikki dump) |
| wa pcd fr frp nrf gallo | è, ê → ɛ | Wikipedia "Walloon orthography": è [ɛ], ê [ɛː]. Wikiversité "Graphie picarde/Feller-Carton": è /ɛ/, ê /eː, ɛː/. Standard French for the rest |
| pcd | oé → we | Wikiversité "Graphie picarde/Feller-Carton" lists *oé* as a diphthong; the glide is how the pipeline keeps a diphthong to one syllable |
| fur | ç → tʃ | Wiktionary *glaç* /ˈɡlat͡ʃ/ (local Kaikki dump) |
| lmo | ö → ø, ü → y | Standard Lombard orthographies; not re-checked |
| ca lad | ç → s | Standard Catalan; Ladino in the grid's Spanish-style spelling. Not re-checked |
| oc gsc gl | acute or grave left on a vowel → plain vowel | The accent marks stress; the backend has already transcribed quality (è → ɛ, ó → u). Not re-checked |
| rup ruq | sh → ʃ, ts → ts, dz → dz, lj → ʎ | Standard Aromanian digraphs; not re-checked |

## A second reader for four lects

`scripts/reader_check.py` sets the pipeline's reading of each grid form beside IE-CoR's and Saenko's
transcription of the same spelling ([`eval/readers.md`](eval/readers.md)). Syllable counts agree for
97% of 1,345 cells. The sounds agree far less often for the two big lects on a borrowed Epitran map:
Epitran read 56% of French words and 13% of Portuguese words with the right sounds (*grand* with a
final d, *femme* in two syllables, *aile* as a bare e, *glace* with z; *chuva* with k, *olho* with l,
*peixe* with ks, *poucos* in three syllables).

French, Picard, Portuguese and Mirandese are therefore read by espeak-ng (`ESPEAK_VOICES`), with the
French voice for Picard and the Portuguese voice for Mirandese. Against IE-CoR it reads 92% of French
and 73% of Portuguese words with the right sounds, and 97% with the right syllable count. Where
espeak-ng is not installed the Epitran map still reads these lects, as before.

| lect | spelling | rewritten for the voice | why |
|---|---|---|---|
| Picard | *grain.ne* | *grainne* | the dot of the Chés Diseux spelling marks a nasal vowel before n |
| Picard | *oé, oè* | *oué, ouè* | [we], [wɛ], the reflex of French *oi* |
| Picard | *-tcher* | *-tché* | an infinitive, read by the voice as an English loan |
| Mirandese | *ch* | *tch* | Mirandese keeps the affricate [tʃ] |
| Mirandese | *x* | *ch* | [ʃ]; the voice reads x in an unknown word as [ks] |

Readings added to the Epitran maps the same day, each a sound the map read as two:

| lect | spelling | reading | source |
|---|---|---|---|
| Walloon, Norman, Gallo, Franco-Provençal | *dj, tch* | d͡ʒ, t͡ʃ | IE-CoR Walloon: *djambe* [d͡ʒãb] |
| Gallo | *ao* | aw | fr.wiktionary: *aotr* [awt], *iao* [jaw], *jaone* [ʒawn] |
| Gallo | *oé, ouè* | we, wɛ | fr.wiktionary: *savouèr*; the same reflex as Picard *oé* |
| Romanian | *oa, ea* | wa, ja | IE-CoR: *soare* [so̯are], *stea* [ste̯a] |

Why the scholarly transcriptions are a yardstick and not the reader: they cover 110 to 170 concepts
of 213 and only two thirds of the lects, each in its own notation (affricates untied, long consonants
doubled, Portuguese diphthongs as two vowels), and for several lects they record another valley than
the column's.

## Not encoded, needs a ruling

| Lect | Letter | Why |
|---|---|---|
| wa | xh | Wikipedia "Walloon orthography": [h/ʃ/ç/x] depending on dialect. The backend reads it /ks/, which no dialect has |
| ruo | c | Croatian-based spelling has ‹c› for /ts/ and ‹k› for /k/ (Vrzić, table 5); the mixed spelling has ‹c/k› for /k/. The backend reads Romanian values. *gljåcę* comes out with tʃ |
| ruo | â, ă | Vrzić writes one central vowel /ɘ/ (‹â› in Croatian-based, ‹ă› in Romanian-based). The backend gives ɨ and ə |
| rup | nj | *njic* should be ɲ, but *înjunghii* in the same column is Romanian-spelled |
| eml | z, ż | Wikipedia "Bolognese dialect": z /θ/, ż /ð/. The Italian backend reads an affricate |
| eml | ź | *źnòć* in Wiktionary's list; no source for the letter. The form is rejected |
| ist | ſ | *buſia*; no source for the letter. The form is rejected |
| oc gsc | qu | /k/ before e, i; the backend gives /ky/ (*aquí*) |

The Istro-Romanian column still mixes spellings (Croatian-based from the
Swadesh appendix, mixed and Romanian-based from other Wiktionary pages). A
form with ă, î, ș or ț is read with Romanian values for *j*. The Romanian
padding that used to sit in this column was removed; see `sources_ruo.md`.
- **Romansh *tg, gl, ch***: the Italian map reads *tg* as t + g and final *gl* as g + l, so *notg, fegl,
  sulegl* gain a syllable (9 of 47 checked cells). They are [tɕ] and [ʎ]. Needs a respelling step
  before the map, which the Epitran path does not have.
- **Romanian final *-i***: non-syllabic after a consonant in *cinci, ochi, vechi*, a full stressed
  vowel in the infinitives *muri, veni*. The spelling does not tell them apart.
- **Final schwa after a nasal vowel and a consonant** in the lects still on the French map (Walloon
  *djambe* read in two syllables). French itself no longer goes through that map.
- **Gallo ELG spellings** (*saun, plum, naijae*): not read correctly by either reader, which is why
  the Gallo column avoids them.

