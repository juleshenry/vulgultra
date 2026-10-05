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

## Three kinds of reader

`scripts/reader_check.py` sets the pipeline's reading of each grid form beside a scholarly
transcription of the same spelling ([`eval/readers.md`](eval/readers.md)): IE-CoR, Saenko 2015 and,
for Walloon, the standard pronunciation in the Walloon Wiktionary. The first run found Epitran's
borrowed maps reading 56% of French and 13% of Portuguese words with the right sounds, and the same
kind of fault in every map. Each lect is now read by whichever of three readers measures best:

| reader | lects | sounds right, before → after |
|---|---|---|
| espeak-ng voice of the language (`ESPEAK_VOICES`) | French, Spanish, Italian, Portuguese, Catalan, Aragonese | fr 56 → 94%, es 79 → 95%, it 62 → 87%, pt 13 → 74%, ca 28 → 92% |
| espeak-ng voice of the big sister, after respelling (`RESPELL`) | Picard (French voice), Mirandese (Portuguese voice) | no transcription to check against |
| the lect's own rules (`RULES`) | Walloon | 94% of 184 cells, and 91% of 10,900 Walloon Wiktionary headwords (the French map: 37% of the 37 cells checkable then) |
| Epitran map, with the lect's letters read first (`RESPELL`) and the map's faults mended (`BACKEND_RESPELL`) | the other 27 | rm 36 → 55%, fur 52 → 61%, sc 69 → 71% |

Over all 1,492 checked cells the syllable count now agrees in 99% (97% before) and every sound in
79% (62%). Without espeak-ng installed, the Epitran map reads the voice lects as before. Romanian
keeps its Epitran map: the Romanian voice gets fewer syllable counts right (106 of 125) than the
map does with one rule added (124).

The reader receives the concept's part of speech, because one rule needs it (Romanian below).

### Variety decisions

- **Spanish is read as Castilian**: *c, z* are θ and *ll* is ʎ, as in IE-CoR's Spanish and as its
  spelling distinguishes them. Epitran's map read them as s and ʝ. Asturian and Extremaduran, which
  stay on that map, get the same three readings by rule; Ladino keeps s.
- **Catalan is read as Central Catalan** (the voice, and IE-CoR's variety): unstressed *a, e* are ə,
  unstressed *o* is u, the *r* of an infinitive is silent.
- **Walloon is read in the "prononçaedje zero-cnoxhou"** of the Walloon Wiktionary, the reading its
  editors mark as standard for the unified spelling: *ea* [ja], *oe* [wɛ], *ae* [ɛ], *xh* [ʃ], *jh*
  [ʒ], final obstruents devoiced. Counted over the dictionary: *ae* is ɛ in 803 of 808 words, *oe* is
  wɛ in 173 of 178, *ô* is õ in 238 of 364, a final voiced obstruent is devoiced in 1,101 of 1,108. A
  final *xh* is written [ç] there; the rules give ʃ, the same phoneme.

### Letters read before the reader sees them

| lect | spelling | reading | source |
|---|---|---|---|
| Picard | *grain.ne*; *oé, oè*; *-tcher* | *grainne*; *oué, ouè*; *-tché* | Chés Diseux spelling: the dot marks a nasal vowel before n; [we], [wɛ]; an infinitive |
| Mirandese | *ch*; *x* | *tch*; *ch* | Mirandese keeps [tʃ]; x is [ʃ] |
| Romansh | *tg*, *ch* before a o u | t͡ɕ | IE-CoR: *tgi* [t͡ɕi], *betg* [bet͡ɕ], *chaun* [t͡ɕawn] |
| Romansh | *gl* before i or word-final, *gli* + vowel | ʎ | IE-CoR: *fegl* [feʎ], *sulegl* [suleʎ], *glina* [ʎinə] |
| Romansh, Ladin | *s* before a consonant | ʃ, ʒ | IE-CoR: *star* [ʃtar], *scorsa* [ʃkɔrsə]; Ladin *baston* [baʃtoŋ], *streda* [ʃtrɛda] |
| Romansh | *tsch*; *sch*; *c* before e i, *z*; *s* between vowels | t͡ʃ; ʃ; t͡s; z | IE-CoR: *cotschen* [kot͡ʃən], *pesch* [peʃ], *culiez* [kuljet͡s], *vesair* [vəzajr] |
| Ladin | *z, tz*; *sc* before e i and word-final | t͡s; ʃ | IE-CoR: *scorza* [ʃkort͡sa], *mazé* [mat͡sɛ], *pësc* [pəʃ] |
| Friulian | *cj, gj*; initial *z*; other *z*; final *sc* | c, ɟ; d͡ʒ; t͡s; sk | IE-CoR: *cjan* [can], *mangjâ* [manɟa], *zâl* [d͡ʒal], *panze* [pant͡se], *bosc* [bɔsk] |
| Bolognese; Romagnol | *z*, *ż*; *z* | θ, ð; θ | Wikipedia "Bolognese dialect", "Romagnol": z /θ/, ż and ẓ /ð/ |
| Sicilian, Corsican | *z, zz* | t͡s | Saenko's Sicilian: *panza* [pant͡sa], *ammazzari* [amat͡sari] |
| Milanese; Istriot | *z, zz*; *z* | s; z | classical Milanese z is a plain sibilant today; Istriot *zalo* |
| Piedmontese | *u* after a, o | w | Saenko: *giàun* [d͡ʒawŋ] |
| Asturian | *x*; *ḥ*; *c, z*; *ll* | ʃ; h; θ; ʎ | Academia de la Llingua Asturiana, *Normes ortográfiques* |
| Extremaduran | *h, j*, *g* before e i; *c, z*; *ll* | h; θ; ʎ | Carmona García's dictionary, whose spelling the column follows |
| Ladino | *sh, x*; *dj*; *j*; *z*; *ny*; *h*; *g* before e i | ʃ; d͡ʒ; ʒ; z; ɲ; x; ɡ | Aki Yerushalayim spelling |
| Occitan, Gascon | *qu* | k | [k] before every vowel; the map gave [ky] (*aquí*) |
| Aromanian, Megleno-Romanian | *nj* | ɲ | as *lj* is ʎ |
| Romanian | final *-i* after a consonant | ʲ on the consonant; nothing after *c, g* | IE-CoR: *ochi* [okʲ], *vechi* [vekʲ], *cinci* [t͡ʃint͡ʃ]. Not in a verb (*muri, veni* end in a stressed i), not when it is the only vowel (*zi*), not after consonant + l, r |
| Jèrriais | *th*; *aun* | ð; ɑ̃ | *méthe, péthe, téthe* for French *mère, père, terre* |
| Franco-Provençal | *en*; *ue*, *oa*; the *-r* of an infinitive | ɛ̃; wɛ, wa; silent | Stich 2001 on ORB: *en* is "une fréquente réalisation [ẽ] et non [ã]"; *ue* is [ɥ/w] + vowel; in *-ar* "le r est très rarement prononcé" |
| Walloon | the *-er* of an infinitive | e | Walloon Wiktionary: [e] in 1,285 of 1,308 longer words in *-er*; *mer, vier, noer* keep r |

### Faults of a borrowed map, mended for every lect on it

| map | fault | example |
|---|---|---|
| Italian | *sc* read ʃ before a, o, u; s + t͡ʃ before e, i | *scorza* [ʃorsa], *sce* [st͡ʃe] |
| Italian | *z* read s (left to each lect's table above, since its value differs) | *culiez* [kulies] |
| Spanish | *gu* before a consonant or word-final read ɡw; *hi* + consonant read as a glide | *gusanu* [ɡewsanu], *llagu* [jaɡew], *hígado* [ʝɡado] |
| Sardinian | the *i* of *gi, ci* dropped before a consonant | *girare* [d͡ʒrare] |
| French | *c* before e, i read z between vowels; a final consonant sounded after a nasal vowel; a schwa left after nasal vowel + consonant; *-er* read əʀ; *ail, eil, euil, ouil* misread | *racena* [ʀazəna], *grant* [ɡʀɑ̃t], *crendre* [kʀɑ̃dʀə], *aile* [e], *faille* [fel] |

Earlier the same day, each a sound the map read as two:

| lect | spelling | reading | source |
|---|---|---|---|
| Norman, Gallo, Franco-Provençal | *dj, tch* | d͡ʒ, t͡ʃ | IE-CoR Walloon: *djambe* [d͡ʒãb] |
| Gallo | *ao* | aw | fr.wiktionary: *aotr* [awt], *iao* [jaw], *jaone* [ʒawn] |
| Gallo, Franco-Provençal | *oé, ouè* | we, wɛ | fr.wiktionary: *savouèr*; the same reflex as Picard *oé* |
| Romanian | *oa, ea* | wa, ja | IE-CoR: *soare* [so̯are], *stea* [ste̯a] |

Why the scholarly transcriptions are a yardstick and not the reader: they cover 110 to 170 concepts
of 213 and only two thirds of the lects, each in its own notation (affricates untied, long consonants
doubled, Portuguese diphthongs as two vowels), and for several lects they record another valley than
the column's.

## Still read wrongly

| Lect | Letter | Why |
|---|---|---|
| ruo | c | Croatian-based spelling has ‹c› for /ts/ and ‹k› for /k/ (Vrzić, table 5); the mixed spelling has ‹c/k› for /k/. The backend reads Romanian values. *gljåcę* comes out with tʃ |
| ruo | â, ă | Vrzić writes one central vowel /ɘ/ (‹â› in Croatian-based, ‹ă› in Romanian-based). The backend gives ɨ and ə |
| eml | ź | *źnòć* in Wiktionary's list; no source for the letter. The form is rejected |
| ist | ſ | *buſia*; no source for the letter. The form is rejected |
| vec | z | [z] in *zalo, zugàr*, [s] in *scorza, panza*: the column mixes two spellings, so the map's s stays |
| dlm | z | Bartoli's *z* is not documented in the sources on disk; the map's s stays |
| ext | x | *páxaru, enxugal*: Carmona García's spelling has no x; the two cells are not his forms |
| nrf | ' | *p'tit, t'nin, g'ler, ch'la*: an apostrophe form is rejected, not read |
| gallo | ELG spellings | *saun, plum, naijae*: the column avoids them |
| all | stress | No reader's stress reaches the pipeline, although espeak-ng and the Walloon Wiktionary mark it |
| all | three-consonant onsets | *trois, troes, droet, plievgia* gain a syllable in `repair` (t + ʀ + w is not a legal onset in `grammar.tex` §2.2), in the scholarly transcription and in the pipeline's alike |

The Istro-Romanian column still mixes spellings (Croatian-based from the
Swadesh appendix, mixed and Romanian-based from other Wiktionary pages). A
form with ă, î, ș or ț is read with Romanian values for *j*. The Romanian
padding that used to sit in this column was removed; see `sources_ruo.md`.
