# Decisions waiting on you, in order

Hand-written; updated as you answer. Each entry says what is being decided, why it comes at this
point, and where the evidence is. Nothing here is picked yet. Where I have a view it is marked
*Suggestion* and is only that.

The order follows the Bible: the Latin text was counted word by word
([`eval/bible_lexicon.md`](eval/bible_lexicon.md)), and its commonest words are the building blocks.
*Et* is 1 word in 12 of the text; the 100 commonest words are 55% of it.

## A. How the Bible is used

1. **Latin as the word list, the five modern Bibles as the guide.** The Vulgate gives the list of
   words a Bible needs and how often each occurs. Each Latin word names a family of daughter words
   (Wiktionary lists 15,600 Latin words with their reflexes); the daughters supply every form, Latin
   none. The modern French, Spanish, Portuguese, Italian and Romanian Bibles show, verse by verse,
   what the daughters say where no Latin word survived (*autem, enim, ut, sed, is*) and give the
   model for word order. *Suggestion: yes.* Limits: a reflex may have drifted in meaning (*dominus*
   gives Portuguese *Dom*, a title), and the Vulgate numbers the Psalms one behind the others, so
   verse alignment needs a mapping table that is not built yet.
2. **The Romanian text.** No public-domain Romanian Bible in Latin script could be verified. The one
   on disk is Cornilescu from a repository that calls it public domain; another source says the 1924
   copyright still holds. It stays on your machine and is never committed. Keep it as a working
   text, or leave Romanian out until a clean edition turns up?
   ([`bible_sources.md`](bible_sources.md))

## B. The shape of the grammar

These three decide how many forms the building blocks need, so they come before the forms.

3. **How a noun forms its plural.** Seventeen lects add *-s* to a masculine noun (Spanish,
   Portuguese, Catalan, French, Occitan, Sardinian, Romansh...); nine change the final vowel
   (Italian, Romanian, Sicilian, Venetan, Corsican...); three leave it unchanged (Lombard,
   Piedmontese, Emilian). For feminines it is sixteen against thirteen.
   ([`eval/plural_formation.md`](eval/plural_formation.md))
4. **Gender and case.** Two genders or three (Romanian and Aromanian have a neuter)? Does a noun or
   pronoun change by role? Every daughter keeps subject, object and indirect forms in the pronouns;
   only the Eastern lects keep any case on nouns. The spec today has nominative, accusative and
   genitive on every noun, which no daughter has.
5. **Articles.** Latin had none; every daughter has a definite and an indefinite one, agreeing in
   gender and number. Have both, one, or none?
   (*Articles, by gender and number* in [`eval/building_block_candidates.md`](eval/building_block_candidates.md))

## C. The words themselves

One at a time, from the shortest attested forms across the 36 lects
([`eval/building_block_candidates.md`](eval/building_block_candidates.md); one page per lect under
[`building_blocks/`](building_blocks/README.md)). In the order the Bible uses them, with the Latin
word's rank in the text:

6. **Words that never change**: *and* (1), *in* (2), *to* (7), *not* (8), *of, from* (17), *with*
   (23), *on* (24), then *or, but, if, because, for, by, without, yes, no*.
7. **Personal pronouns**, by person and role, once 4 is settled: *I* (16), *he, she, it* (4),
   *you* plural (27), *me* (28), and the rest of the table.
8. **Possessives**: *his, her* (10), *your* (11), *my* (21), *our, their*.
9. **Demonstratives and the relative**: *who, which* (5), *that* (15), *this* (18).
10. **To be** (3) belongs to your verb work; it is listed here only because the Bible uses it more
    than any word but *et* and *in*.
11. **Numerals** one to ten, the tens, hundred, thousand.
12. **Question words and the small adverbs**: *who, what, where, when, how, why; now, here, there,
    also, already, still, never, always*.

## D. Carried over from the foundations

13. **A letter for each sound that has none** (39 of 62).
    ([`eval/orthography_gaps.md`](eval/orthography_gaps.md))
14. **How to choose among equally short forms.** Today the choice is random: another random seed
    changes 138 of 213 roots. Whatever rule you pick for the building blocks in C (most lects?
    fewest sounds? no homophones?) is probably the rule here too.

## Picked so far

Nothing yet.
