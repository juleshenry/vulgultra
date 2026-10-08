# Decisions waiting on you, in order

Hand-written; updated as you answer. Each entry says what is being decided, why it comes at this
point, and where the evidence is. Nothing here is picked yet. Where I have a view it is marked
*Suggestion* and is only that.

The order is the roadmap's ([`../TODO.md`](../TODO.md), set on 7 October 2026), and a
decision is numbered by its step. Within the small words the order follows the Bible: the Latin
text was counted word by word ([`eval/bible_lexicon.md`](eval/bible_lexicon.md)), and its commonest
words are the small ones. *Et* is 1 word in 12 of the text; the 100 commonest words are 56% of it.

## Step 0. Spelling, and choosing among equally short forms

Nothing picked later can be written down, or stay picked, until these two are settled.

- **0.1 A letter for each sound that has none** (39 of 62).
  ([`eval/orthography_gaps.md`](eval/orthography_gaps.md), with a proposal per sound)
- **0.2 How to choose among equally short forms.** Today the choice is random: another random seed
  changes 138 of 213 roots. Three parts: what ranks equals (most lects? fewest sounds?), whether a
  homophone costs anything, and whether a root you approve is pinned so that adding words cannot
  change it. Whatever rule you pick here is probably the rule for the small words too.

## Step 1. Verbs

Yours; nothing is queued here. *To be* is the Bible's third commonest word, after *et* and *in*.

## Step 2. Small words

One at a time, from the shortest attested forms across the 36 lects
([`eval/building_block_candidates.md`](eval/building_block_candidates.md); one page per lect under
[`building_blocks/`](building_blocks/README.md)). The first two decide how many forms the rest
need, so they come before the forms. The number after a word is its Latin word's rank in the text.

- **2.1 Case.** Does a noun or pronoun change by role? Every daughter keeps subject, object and
  indirect forms in the pronouns; only the Eastern lects keep any case on nouns. The spec today has
  nominative, accusative and genitive on every noun, which no daughter has. If nouns have no case,
  prepositions carry the roles; if they keep one, each preposition needs a case to govern.
- **2.2 Articles.** Latin had none; every daughter has a definite and an indefinite one, agreeing
  in gender and number. Have both, one, or none?
  (*Articles, by gender and number* in [`eval/building_block_candidates.md`](eval/building_block_candidates.md))
- **2.3 Words that never change**: *and* (1), *in* (2), *to* (7), *not* (8), *of, from* (17),
  *with* (23), *on* (24), then *or, but, if, because, for, by, without, yes, no*.
- **2.4 Personal pronouns**, by person and role, once 2.1 is settled: *I* (16), *he, she, it* (4),
  *you* plural (27), *me* (28), and the rest of the table.
- **2.5 Possessives**: *his, her* (10), *your* (11), *my* (21), *our, their*.
- **2.6 Demonstratives and the relative**: *who, which* (5), *that* (15), *this* (18).
- **2.7 Question words and the small adverbs**: *who, what, where, when, how, why; now, here,
  there, also, already, still, never, always*.

## Step 3. Nouns and adjectives

- **3.1 How a noun forms its plural.** By each lect's commonest pattern, in the 31 lects whose
  nouns record a plural: eighteen form the masculine plural in *-s* (Spanish, Portuguese, Catalan,
  French, Occitan, Sardinian, Romansh...); nine change or add a vowel (Italian, Romanian, Sicilian,
  Venetan, Corsican...); three leave it unchanged (Lombard, Piedmontese, Emilian); Romagnol has no
  one pattern. For feminines it is eighteen in *-s* against twelve with a vowel, and Aromanian has
  no one pattern.
  ([`eval/plural_formation.md`](eval/plural_formation.md))
- **3.2 Gender.** Two genders or three (Romanian and Aromanian have a neuter)?

The endings themselves, the junction of root and ending, and whether adjectives share the nouns'
table come once the harvest and its shortlist exist.

## Step 4. Numerals

- **4.1 The numerals.** One to ten, the tens, hundred, thousand; how the numbers between are built
  (a fused word, or ten-and-one); whether an ordinal is a word of its own or built from its
  cardinal. (*Numerals* in [`eval/building_block_candidates.md`](eval/building_block_candidates.md))

## Step 5. Proper nouns

New on 7 October. The Vulgate has about 4,000 name forms that are no dictionary word (*Israel*,
*David*, *Ierusalem*, *Iesus*): one word in twenty of the text. Nothing is harvested yet.

- **5.1 Where a name's form comes from.** The daughters, like any other word: each name as the
  modern Bibles and the lects' own Bible texts write it (*Jésus, Jesús, Gesù, Isus*), and the pick
  made the same way as for a common word. Or one fixed source, adapted to Vulgultra's sounds by a
  rule. *Suggestion: the daughters. The axiom has no exception for names, and the Bibles already on
  disk give the forms. The cost is that the shortest attested form of a name may be an odd one, so
  you may want names picked by how many lects agree rather than by length.*
- **5.2 Whether a name inflects**, once 2.1 and 3.1 are settled: a plural, a case, a gender.

## Step 6. Lexicon, the Bible first

- **6.1 Latin as the word list, the five modern Bibles as the guide.** The Vulgate gives the list
  of words a Bible needs and how often each occurs. Each Latin word names a family of daughter
  words (Wiktionary lists 15,600 Latin words with their reflexes); the daughters supply every form,
  Latin none. The modern French, Spanish, Portuguese, Italian and Romanian Bibles show, verse by
  verse, what the daughters say where no Latin word survived (*autem, enim, ut, sed, is*) and give
  the model for word order. *Suggestion: yes.* Limits: a reflex may have drifted in meaning
  (*dominus* gives Portuguese *Dom*, a title). The five are lined up with the Latin verse by verse,
  so each Latin word shows the word every Bible uses for it
  ([`eval/bible_anchor_words.md`](eval/bible_anchor_words.md)).
- **6.2 The Romanian text.** No public-domain Romanian Bible in Latin script could be verified. The
  one on disk is Cornilescu from a repository that calls it public domain; another source says the
  1924 copyright still holds. It stays on your machine and is never committed. Keep it as a working
  text, or leave Romanian out until a clean edition turns up?
  ([`bible_sources.md`](bible_sources.md))
- **6.3 What counts as a daughter's form.** Sourcing the thin lects turned up four kinds of
  material I have set aside rather than count, pending your word
  ([`sources_bible_lexicon.md`](sources_bible_lexicon.md)):
  - *an earlier stage of a lect*: medieval Béarnais, Gascon charters (and, from 5 October, Old
    French, Old Occitan, Old Spanish);
  - *a written standard that is nobody's speech*: Ladin Dolomitan, Micurà de Rü's common Ladin of
    1833; Rumantsch Grischun raises the same question and is counted today;
  - *forms from an unproofread scan*: counted apart as "scan", never as firm;
  - *"shared" Occitan* from Apertium, which I count for Gascon as the earlier audit did.

  *Suggestion: keep all four out of root-picking; the first two are yours to rule on.*
- **6.4 Soft licence footing.** Six sources are used locally and rest on an argument rather than a
  stated licence: Cunia's Aromanian dictionary, Dalla Zonca's Istriot dictionary, the Piedmontese
  Bible's Old Testament, the Walloon Matthew and Mark, the e-text of Mistral's Genesis, and
  Capidan's Megleno-Romanian dictionary. Nothing is committed or published. Use them, or drop any?
  A seventh, the Société Jersiaise's Jèrriais vocabulary, states no licence at all and is not read.
- **6.5 Paying for page readings.** Istro-Romanian and Megleno-Romanian are the two lects whose
  dictionaries exist only as printed pages that a machine misreads. Reading them from the page
  images works (Pușcariu's glossary is read in full, and was right on the column I compared) and
  costs usage: ten pages took about 240,000 tokens. Popovici is 72 pages, Byhan 224, and Capidan
  has 951 entries to re-read. Say how far to go.

## Picked so far

Nothing yet.
