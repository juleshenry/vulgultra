
This Database is an open source and downloadable version of the [Oxford  Database of the Inflectional Morphology of the Romance Verb](http://romverbmorph.clp.ox.ac.uk/), as a [CLDF](https://cldf.clld.org/) WordList module. It is intended to facilitate quantitative analysis.

This version was created in the following way:

- We scraped the online database to reconstruct an image of the original database,
- We then reorganized, cleaned up, and normalized the resulting tables into a CLDF WordList, adding metadata when needed.
- We added latin entries from [LatInfLexi 1.1](https://github.com/matteo-pellegrini/LatInfLexi)

The scripts used for that purpose can be found in the [scraping and formatting the ODRVM](https://gitlab.com/sbeniamine/scraping_and_formatting_the_ODRVM) repository.

The original documentation can be found online at [http://romverbmorph.clp.ox.ac.uk/](http://romverbmorph.clp.ox.ac.uk/).

Tables
-------

- `languages.csv` is a [LanguageTable](http://cldf.clld.org/v1.0/terms.rdf#LanguageTable) with information on each variety:

| ID                                                      |   Latitude |   Longitude | Closest_Glottocode   | Town          |   Comment | Variety                          | Linguistic_Date                 | Sources        | Country   | Family    | Region          | Variety_in_ODRVM                                           |
|:--------------------------------------------------------|-----------:|------------:|:---------------------|:--------------|----------:|:---------------------------------|:--------------------------------|:---------------|:----------|:----------|:----------------|:-----------------------------------------------------------|
| Sardinian_Sassarese                                     |    40.7267 |     8.55917 | sass1235             |           |       | Sassarese                        | late 20th to early 21st century | Camilli1929    | Italy     | Sardinian | Sardinia        | Sardinian - Sassarese                                      |
| French_Norman_from_Jersey                               |    49.1833 |    -2.10694 | norm1245             | Jersey        |       | Norman                           | mid to late 20th century        | Liddicoat1994  | Jersey    | French    | Channel Islands | French - Norman - Jersey                                   |
| Italian_Northern_I_Piedmontese_Basso_from_Cascinagrossa |    44.8786 |     8.72028 | lowp1238             | Cascinagrossa |       | Northern I > Piedmontese > Basso | late 20th to early 21st century | Castellani2002 | Italy     | Italian   | Piedmont        | Italian - Northern I - Piedmontese - Basso - Cascinagrossa |




- The table `parameters.csv` is a [ParameterTable](http://cldf.clld.org/v1.0/terms.rdf#ParameterTable) which describes the morphosyntactic cells of the paradigm. It was made manually following the online documentation, which is quoted in the "description" field. The IDs are used in the forms table. The 'Continuants' column links latin paradigm cells to their continuant labels.

| ID          | Name                        | Description         | Continuants          |
|:------------|:----------------------------|:--------------------|:---------------------|
| PLUP-IND    | Latin pluperfect indicative |                     | CONT_LAT_PLUP-IND    |
| IMPERF-SBJV | Latin imperfect subjunctive |                     | CONT_LAT_IMPERF-SBJV |
| 3PL         | 3pl                         | third person plural |                      |


- The table `cognatesets.csv` is a [CognateSetTable](http://cldf.clld.org/v1.0/terms.rdf#CognatesetTable). It provides information for each unique etymon. The IDs are used in the form and lexeme tables. The LemLat_ID links back latin etymons to LatInFlexi identifiers.

| ID        | LemLat_ID   | Language_of_the_etymon   | Etymon     | Latin_Conjugation   | Part_Of_Speech   | Derived_from   |
|:----------|:------------|:-------------------------|:-----------|:--------------------|:-----------------|:---------------|
| pascere   | pasco/-or   | Latin                    |  pascere
   | III                 | V                |         |
| akkattare |             | Romance                  |  *akkattare
|                     | V                |                |
| cubare    | cubo        | Latin                    |   cubare
  | I                   | V                |          |


- The `lexemes.csv` table is a custom table which provides a meaning and a potential comment for each lexeme, that is each instance of an etymon in a given variety.

| ID       | Etymon_in_ODRVM         | Meaning   | Comment   | Cognateset_ID       | Language_ID                                                    |
|:---------|:------------------------|:----------|:----------|:--------------------|:---------------------------------------------------------------|
| lex_1340 | PLACERE                 | please    |           | placere             | French_Wallon_from_Namur                                       |
| lex_2039 | UENIRE                  | come      |           | uenire              | Italian_Northern_I_Emilian_from_Travo                          |
| lex_127  | AMBULARE / IRE / UADERE | go        |           | ambulare~ire~uadere | French_Acadian_South-East_New_Brunswick_from_Moncton__environs |


- `form.csv` is a [FormTable](http://cldf.clld.org/v1.0/terms.rdf#FormTable) representing a paradigm in long form, where each row corresponds to a specific form in one variety. The table refers to the languages, cognatesets and parameter tables through respectively the Language_ID, CognateSet_ID and Cell columns.

| ID           | Language_ID                               | Cell         | Form      | Cognateset_ID   |
|:-------------|:------------------------------------------|:-------------|:----------|:----------------|
| form_723896  | Romanian_Modern_Standard                  | PRS-SBJV~1PL | ˈnaʃtem   | nasci           |
| form_2203100 | Galego-Portuguese_Portuguese              | INFL_INF~3PL | pɾɐˈzeɾɐ̃ĩ | placere         |
| form_2262553 | Italian_Central_Marchigiano_from_Macerata | ROM_FUT~3PL  | aˈvra     | habere          |

Character Inventory
-------------------

Forms are entered in IPA notation, using the following characters. 

|                     | bilabial   | labio-dental   | dental   | alveolar   | post-alveolar   | retroflex   | palatal   | labio-palatal   | labio-velar   | velar   | uvular   | glottal   |
|:--------------------|:-----------|:---------------|:---------|:-----------|:----------------|:------------|:----------|:----------------|:--------------|:--------|:---------|:----------|
| stop                | b p        |                |          | d t        |                 | ɖ           | ɟ c       |                 |               | g k     |          |           |
| nasal               | m          |                |          | n          |                 |             | ɲ         |                 |               | ŋ       |          |           |
| trill               |            |                |          | r          |                 |             |           |                 |               |         | ʀ        |           |
| tap                 |            |                |          | ɾ          |                 |             |           |                 |               |         |          |           |
| fricative           | β ɸ        | v f            | ð θ      | z s        | ʒ ʃ             |             | ʝ ç       |                 |               | ɣ x     | ʁ χ      | h         |
| affricate           |            |                |          | ʣ ʦ        | ʤ ʧ             |             |           |                 |               |         |          |           |
| approximant         |            |                |          | ɹ          |                 |             | j         | ɥ               | w             |         |          |           |
| lateral approximant |            |                |          | l          |                 |             | ʎ         |                 |               |         |          |           |


|            | front   | near-front   | central   | near-back   | back   |
|:-----------|:--------|:-------------|:----------|:------------|:-------|
| close      | i y     |              | ɨ         |             | u      |
| near-close |         | ɪ            |           | ʊ           |        |
| close-mid  | e ø     |              | ɘ         |             | o      |
| mid        |         |              | ə         |             |        |
| open-mid   | ɛ œ     |              |           |             | ʌ ɔ    |
| near-open  | æ       |              | ɐ         |             |        |
| open       | a ɶ     |              |           |             | ɑ ɒ    |

| category   | diacritic   | value        |
|:-----------|:------------|:-------------|
| syllable   | ◌ˈ          | stressed  |
| consonant  | ◌̩           | syllabic     |
| consonant  | ◌ʲ          | palatalized  |
| vowel      | ◌̝           | raised       |
| vowel      | ◌̯           | non-syllabic |
| vowel      | ◌̃           | nasalized    |
| vowel      | ◌ː          | long         |
| vowel      | ◌̞           | lowered      |



In addition:

-  parenthesis mark elements which are only optionally or variably present in pronunciation
-  brackets mark clitics when either we do not have an example of that form without the clitic and, or when it is possible that without the clitic the form of the verb would be slightly different.


People and contacts 
-------------------

The following have contributed to building the Database:

-   Silvio Cruschina
-   Maria Goldbach
-   Marc-Olivier Hinzelin
-   Martin Maiden
-   John Charles Smith

We are grateful also to Chiara Cappellaro, Louise Esher, Paul O'Neill,
Stephen Parkinson, Mair Parry, Nicolae Saramandu, Andrew Swearingen,
Francisco Dubert García and Tania Paciaroni for their assistance.

The CLDF version was created and cleaned by Sacha Beniamine and Erich Round.

Any queries or suggestions regarding the Database should be directed to:
<martin.maiden@mod-langs.ox.ac.uk> and / or
<johncharles.smith@mod-langs.ox.ac.uk>
