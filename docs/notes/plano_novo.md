# Three classes, one function

Lemmas are the base. The language then branches. There are three classes of word, and the same energy covers all of them. A cultismo is not sheltered, and it is not thrown out for being learned. It competes when a contest exists.

| class | what it is | what happens |
|---|---|---|
| **lemma** | a headword in `{code}_words.json` | the base. Families, then the anneal |
| **cultismo** | a learned word with a rival somewhere: another lect's cultismo, or a popular twin in the same skeleton | competes. Shorter clause wins. `ópera` may lose to `obra` |
| **cultismo único** | a learned word one lect has and nobody else does | no contest. Spelled once and kept. `meteoropatico` → `meteyoropatiko` |

The class is not a label we assign by taste. It falls out of the inputs. A skeleton with two or more lects is a contest, whether the forms are popular or learned. A skeleton with one lect is único. A later feeding can move a word from único to cultismo the moment a second lect shows up with the same skeleton. Then it competes.

## The function

Families join on a reverse-Vulgar-Latin consonant skeleton of the source spelling, before G2P. `ch`/`c`/`qu`/`k` collapse, voiced with voiceless, vowels drop. A skeleton shorter than two consonants merges nothing. English never creates a family. If both sides have glosses and the glosses differ, the bucket splits. Sister epitran never decides membership.

Multiword citations are split before the skeleton. `de`/`di`/`da` mark a genitive object. `se`/`si` mark the one clitic `se`. A separated light verb marks HAVE plus a noun. The particle is not a stem and does not enter the inventory.

Where a family has two or more lects, anneal: fewest clause syllables, then a smaller inventory, then a lect not yet used, then support.

- direct or oblique verb: stem plus one person cell; accusative and genitive are both one syllable
- reflexive: stem plus person cell plus `se`
- light noun: HAVE (`a`/`o`) plus the noun plus its case cell

Grammar is priced once: noun theme `o`/`u`/`e`, each verb tense its own lect, adjectives copy the noun's cell. Gender is the gender on the stem that won. Non-cognates meet only when the inputs say so: matching glosses after the frame is stripped, or the hand list `like` and `need`.

## How the base branches

**1. Lemmas.** `{code}_words.json`. Build families. Anneal every family with a rival. Spell every one-lect lemma once. Write `data/eval/families_lexicon.json`. Swadesh is the regression check, not the search. This layer already contains ordinary cultismos that made the frequency cut (`democrazia`, `fotografia`). They compete here if their skeleton is shared.

**2. Cultismos.** The long tail: Kaikki JSONL and headwords past the cap. A line whose skeleton already exists joins that family and the family is re-sliced. The learned form can win or lose. A line that shares a skeleton only with other tail forms becomes its own contest and is annealed. Nothing in this pass is marked "keep because it is learned."

**3. Cultismos únicos.** A tail line with a new skeleton, one lect. No anneal. Frame-split, then one pass of the spelling rules, then append. `meteoropatico` is this class for as long as no other lect has it. If a later line matches it, it leaves this class and enters the contest in 2.

**4. Predicates, beside the three.** `aimer`, `gostar de`, and `necesitar` are different skeletons. They compete only as one predicate, on the clause price above. The audit line keeps the source construction.

**5. Running text, last.** A Wikipedia token that parses as a known stem plus a known cell confirms the paradigm. A token that does not parse is a new input and takes step 2 or 3. It waits until 1–3 have a written lexicon.

Thin lects add only lines they have. No step copies a Spanish stem into a hole.

## First slice, when building starts

Run step 1 to a written lexicon. Then run the tail far enough to show one cultismo change a family's winner and one único spelled as `meteyoropatiko`, or the nearest real one-lect learned word the Kaikki files contain. `like` and `need` come after that. Wiki types wait.
