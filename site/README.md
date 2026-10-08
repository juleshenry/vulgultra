# Learn Vulgultra: the lesson site

A static site for learning Vulgultra, modelled on
[Apprènde Neolatino](https://www.apprendeneolatino.com/). It is a skeleton:
the navigation, the lesson tree and every page are in place, and the lessons
are still to be written.

## Build and look

```bash
.venv/bin/python3 scripts/build_site.py
open site/public/index.html
```

The build takes about two seconds and replaces `site/public/`, which git ignores. All
links are relative, so the pages open straight from disk; `python3 -m
http.server -d site/public` serves them if you prefer a URL. The build fails
with an error when a link in a page, the navigation bar or the footer names a
page that does not exist.

## What is where

| Path | Holds |
|---|---|
| `site.yml` | Site name, navigation bar, home page, footer, pages outside the lesson tree |
| `sidebar.yml` | The lesson tree: 29 categories and 138 lessons, in order |
| `content/` | Page bodies, in Markdown |
| `i18n/es.yml`, `i18n/es/` | Spanish wording, and Spanish page bodies |
| `static/` | Stylesheet, script and images, copied as they are |
| `public/` | The built site |

## Writing a lesson

Every lesson in `sidebar.yml` already has a page that says it is under
construction. To write one, create its Markdown file:

```
site/content/lessons/<dir>/<slug>.md
```

with `<dir>` and `<slug>` as `sidebar.yml` gives them, for example
`site/content/lessons/pronouns/subject-pronouns.md`. The title and its
number come from `sidebar.yml`, so the file starts with the text itself and
its headings start at `##`; in a numbered lesson those are numbered for you
(4.1.1, 4.1.2). Add `done: true` to the lesson's line in `sidebar.yml` to
put a check mark after its title.

What the Markdown can do is shown on the built page `markdown-page.html`,
whose source is `content/markdown-page.md`: text styles, links, lists,
tables, notes, footnotes, images.

Other pages work the same way: `content/lessons/faq.md`,
`content/resources/<slug>.md`, `content/tools/conjugator.md`, and a blog
post is `content/blog/YYYY-MM-DD-slug.md` with a `title:` in its front
matter.

To add, move or rename a lesson or a category, edit `sidebar.yml`; the
numbers follow.

## Spanish

The site is built twice: English at the root and Spanish under `es/`. A page
with no Spanish body shows the English one. A Spanish body goes in
`i18n/es/` under the same path as in `content/`; a Spanish title is the
`es:` key of the entry in `sidebar.yml`. The wording of menus and buttons is
in `i18n/es.yml`.

## What came from the model site

`scripts/scrape_apprendeneolatino.py` fetched all 187 pages of
apprendeneolatino.com with Scrapling on 7 October 2026 into
`data/sources/apprendeneolatino/`, which git ignores. Only the structure was
taken from it: which page types exist, how they are laid out, and the lesson
tree. None of its text, artwork or code is in this folder; the stylesheet,
the script and the images were written for this site.

The lesson tree follows the original category by category. Lessons are
numbered in order, so the original's gap at 10.5 is closed, and the titles
that named Neolatin's own words were made neutral:

| Original | Here |
|---|---|
| A History of Neolatin | A History of Vulgultra |
| 4.4. Other Pronouns (Hi and Ne) | Other Pronouns |
| 10.3. Per vs Por | Prepositions of Cause and Purpose |
| 13.1. Negation with "Non" | Simple Negation |
| 13.3. Omitting "Non" | Omitting the Negative Particle |
| 16.3. Type 1: Fully Irregular | Fully Irregular Verbs |
| 16.4. Type 2: Stem-Changing Verbs and Root Stress | Stem-Changing Verbs and Root Stress |
| 16.5. Type 3: Irregular in Èo | Irregular First Person Singular |
| 16.6. Type 4: Irregular in Èo and Stem-Changing | Irregular First Person Singular and Stem-Changing |
| 16.8. REGIONAL: Change In Stress | Change in Stress |
| 22.6. Imperatives With "Que" | Imperatives With a Complementizer |
| 24.5. Accidental Se | The Accidental Reflexive |
| 24.6. Special Construction: Se + Transitive Verb | Special Construction: Reflexive + Transitive Verb |
| 27. Èssere vs Estare | The Copula |
| 27.2. Uses of Èssere | Uses of the Copula |
| 27.3. Uses of Estare | Location and State |
| 28.3. Causative Verbs: Fàcere and Laxare | Causative Verbs |

The tree is the model's, not a ruling on Vulgultra's grammar: a lesson that
turns out not to apply (the specification has one copula and one past
tense, for instance) is removed or renamed in `sidebar.yml`.

The original links to an outside conjugator and dictionary. Here both are
pages of the site, `tools/conjugator` and `tools/dictionary`, and both are
empty.
