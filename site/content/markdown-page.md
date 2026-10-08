---
description: Everything a lesson can be written with.
---

This page shows what a lesson can be written with. Its source is `site/content/markdown-page.md`.

## Text

A paragraph is one or more lines of text. A blank line starts a new one. Text can be **bold**, *italic* or `code`, and a backslash at the end of a line\
breaks the line.

A link to another page of the site starts with a slash: [the alphabet](/lessons/pronunciation/alphabet), or [a heading on this page](#tables). A link to another site is written in full: [Wikipedia](https://www.wikipedia.org/).

A sentence can carry a footnote.[^1]

## Headings

A lesson's title comes from `site/sidebar.yml`, so its text starts at the second level (`##`). In a numbered lesson the second-level headings are numbered for you.

### A Third-Level Heading

Second and third-level headings appear in the list on the right.

## Lists

- An item
- Another item
  - An item inside it
  - And another
- A last item

1. First
2. Second
3. Third

## Tables

| Form | Meaning |
|---|---|
| `a` | first |
| `b` | second |

An empty first row leaves the heading out, for a plain list of examples:

| | |
|---|---|
| An example | Its translation |
| Another example | Its translation |

Colons in the second row set the alignment of a column:

| Left | Centre | Right |
|:---|:---:|---:|
| a | b | 1 |
| aa | bb | 10 |

## Notes

:::note
A note.
:::

:::tip A tip with a title of its own
A tip.
:::

:::info
Information.
:::

:::warning
A warning.
:::

:::danger
A danger.
:::

## Quotations and Code

> A quotation.

```
A block of text kept exactly
    as it is typed.
```

## Images

An image in `site/static/` is linked with a slash, like a page:

![The site's icon](/img/favicon.svg)

---

[^1]: The note's text is written anywhere in the file, on a line of its own.
