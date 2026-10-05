# Orthography sources

Where each reading in `BACKEND_LEFTOVERS` (`vulgultra/phonology_constants.py`)
comes from. A reading is the IPA value a letter has in that lect's own
spelling, for letters the borrowed G2P backend does not know. Checked
5 October 2026.

| Lect | Letter → reading | Source |
|---|---|---|
| ruo | j → j, ž → ʒ, š → ʃ, č → tʃ, lj → ʎ, nj → ɲ, å → ɒ, ę → æ | Vrzić, "Orthographic practices and social meanings: writing Istro-Romanian", *Sociolinguistica* 39(2), 2025, table 5 (Croatian-based orthography, after Vrzić 2010): /ʒ/ ‹ž›, glide ‹j›, /ɲ/ ‹nj›, /ʎ/ ‹lj›, /æ/ ‹ę›, /ɒ/ ‹å›. <https://d-nb.info/1381267149/34> |
| rgn | ẓ → ð | Wiktionary *alẓir* /al.ˈðir/ (local Kaikki dump); Wikipedia "Romagnol": z is [θ] or [ð], never an affricate |
| rgn | ș → z, ọ → o, ë → ɛ, ö → ɔ | Wiktionary *radìșa* [ɾɐˈdiːzɐ], *calurôș* [kɐluˈɾoə̯z], *fọmm* [ˈfomm], *pël* [ˈpɛːl], *öv* [ˈɔːv] (local Kaikki dump). Wikipedia "Romagnol" (Vitali 2008) gives ë [ɛə̯], ö [ɔə̯]: one syllable either way |
| rgn | ã → ə̃ | Wikipedia "Romagnol", vowel table (Vitali 2008): ã/â [ə̃] |
| rgn | ş → z | Inferred: cedilla form of ș. *uşël* is not in the dump |
| eml | ṅ → ŋ, ć → tʃ | Italian Wikipedia "Dialetto mirandolese": ‹ṅ ń› [ŋ], ‹ć c'› [tʃ]. Wikipedia "Bolognese dialect": ṅ is the velar nasal |
| eml | ṣ → z | Inferred from the shared convention that a marked s is the voiced one: Mirandolese ‹ś ş› [z], Bolognese ṡ /z/, Romagnol ș [z]. No source found for this exact letter |
| eml | ū ī ō → u i o | Inferred: macron taken as length, which the pipeline drops. No source found |
| lld | ë → ɐ, ö → ø, ü → y | Wikipedia "Ladin language", Vowels: "[ɐ] vowel, spelled ⟨ë⟩, as in Urtijëi"; front rounded [ø y] spelled ⟨ö, ü⟩ |
| pms | ë → ə | Wikipedia "Piedmontese language", alphabet table: Ë ë /ə/ |
| wa | å → ɔ | Wikipedia "Walloon orthography": Feller å [ɔː], rifondou [ɔː/oː/ɑː]; Wiktionary *åbe* /ɔːp/ (local Kaikki dump) |
| wa pcd fr frp nrf gallo | è, ê → ɛ | Wikipedia "Walloon orthography": è [ɛ], ê [ɛː]. Wikiversité "Graphie picarde/Feller-Carton": è /ɛ/, ê /eː, ɛː/. Standard French for the rest |
| pcd | oé → we | Wikiversité "Graphie picarde/Feller-Carton" lists *oé* as a diphthong; the glide is how the pipeline keeps a diphthong to one syllable |
| fur | ç → tʃ | Wiktionary *glaç* /ˈɡlat͡ʃ/ (local Kaikki dump) |
| lmo | ö → ø, ü → y | Standard Lombard orthographies; not re-checked |
| ca lad | ç → s | Standard Catalan; Ladino in the grid's Spanish-style spelling. Not re-checked |
| oc gsc gl | acute or grave left on a vowel → plain vowel | The accent marks stress; the backend has already transcribed quality (è → ɛ, ó → u). Not re-checked |
| rup ruq | sh → ʃ, ts → ts, dz → dz, lj → ʎ | Standard Aromanian digraphs; not re-checked |

## Not encoded, needs a ruling

| Lect | Letter | Why |
|---|---|---|
| wa | xh | Wikipedia "Walloon orthography": [h/ʃ/ç/x] depending on dialect. The backend reads it /ks/, which no dialect has |
| ruo | c | Croatian-based spelling has ‹c› for /ts/ and ‹k› for /k/ (Vrzić, table 5); the mixed spelling has ‹c/k› for /k/. The backend reads Romanian values. *gljåcę* comes out with tʃ |
| ruo | â, ă | Vrzić writes one central vowel /ɘ/ (‹â› in Croatian-based, ‹ă› in Romanian-based). The backend gives ɨ and ə |
| rup | nj | *njic* should be ɲ, but *înjunghii* in the same column is Romanian-spelled |
| pms | o, u | Wikipedia "Piedmontese language": O o /u/, U u /y/. The Italian backend reads o, u |
| oc gsc | qu | /k/ before e, i; the backend gives /ky/ (*aquí*) |

About 50 forms in the Istro-Romanian column are in Romanian spelling and
look like Daco-Romanian words (*niște, respira, corect, zâmbi, animal*).
They are read with Romanian values. Whether they are attested
Istro-Romanian is a question for the grid, not for transcription.
