#!/usr/bin/env python3
"""Build the Learn Vulgultra site from site/ into site/public/.

The site is a skeleton modelled on apprendeneolatino.com (see
scripts/scrape_apprendeneolatino.py): the same navigation, lesson tree and
page types, with the lessons still to be written. A page gets a body when
its Markdown file exists under site/content/; until then it says it is
under construction. site/README.md describes the layout.

Standard library and PyYAML only. Every link in the output is relative, so
the site opens from disk or from any folder of a static host.
"""

from __future__ import annotations

import argparse
import datetime
import html
import json
import posixpath
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
CONTENT = SITE / "content"
OUT = SITE / "public"
FONTS = "https://fonts.googleapis.com/css2?family=Alegreya+Sans:ital,wght@0,400;0,700;1,400;1,700&display=swap"
SEARCH_TEXT_LIMIT = 1500

MONTHS = {
    "en": ("January", "February", "March", "April", "May", "June", "July", "August", "September",
           "October", "November", "December"),
    "es": ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
           "octubre", "noviembre", "diciembre"),
}

ICONS = {
    "menu": '<svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true"><path stroke="currentColor" stroke-linecap="round" stroke-width="2" d="M4 7h22M4 15h22M4 23h22"/></svg>',
    "globe": '<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/></svg>',
    "sun": '<svg class="icon-sun" width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
    "moon": '<svg class="icon-moon" width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4 8.5 8.5 0 1 0 20 14.5z"/></svg>',
    "search": '<svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="8.5" cy="8.5" r="6"/><path d="M13 13l5 5"/></svg>',
    "home": '<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3l9 8h-2.5v9h-5v-6h-3v6h-5v-9H3z"/></svg>',
    "caret": '<svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><path fill="currentColor" d="M2 4h8L6 9z"/></svg>',
    "collapse": '<svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 5l-5 5 5 5M16 5l-5 5 5 5"/></svg>',
}


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def attr(text: str) -> str:
    return html.escape(text, quote=True)


def plain(markup: str) -> str:
    """The text of a piece of HTML, on one line."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", markup))).strip()


def slugify(text: str) -> str:
    return re.sub(r"[^\w]+", "-", text.lower(), flags=re.UNICODE).strip("-")


# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------

ADMONITIONS = ("note", "tip", "info", "warning", "danger")
RAW_HTML = re.compile(r"\s*</?(div|table|details|summary|figure|iframe|audio|video|section|svg)\b")
_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
_HEADING = re.compile(r"^(#{1,6})\s+(.*?)(?:\s+\{#([\w-]+)\})?\s*$")
_ADMONITION = re.compile(r"^:::(\w+)[ \t]*(.*)$")
_RULE = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")
_TABLE_RULE = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")
_FOOTNOTE = re.compile(r"^\[\^([^\]]+)\]:\s*(.*)$")


class Markdown:
    """The subset of Markdown the pages are written in.

    site/content/markdown-page.md shows all of it: headings, paragraphs,
    emphasis, code, links, images, lists, tables, block quotes, admonitions
    (:::note ... :::), footnotes and raw HTML blocks.
    """

    def __init__(self, resolve, labels):
        self.resolve = resolve  # link target as written → href
        self.labels = labels    # English label → label in the page's locale

    def render(self, text: str, number: str = "") -> tuple[str, list[tuple[int, str, str]]]:
        """Returns the HTML and the table of contents as (level, id, text)."""
        self.toc: list[tuple[int, str, str]] = []
        self.ids: dict[str, int] = {}
        self.notes: dict[str, str] = {}
        self.cited: list[str] = []
        self.number, self.section = number, 0
        body = []
        for line in text.splitlines():
            note = _FOOTNOTE.match(line)
            if note:
                self.notes[note[1]] = note[2]
            else:
                body.append(line.rstrip())
        out = self.blocks(body)
        if self.cited:
            out += "\n" + self.footnotes()
        return out, self.toc

    # -- blocks --------------------------------------------------------------

    def blocks(self, lines: list[str]) -> str:
        out, i, n = [], 0, len(lines)
        while i < n:
            line = lines[i]
            if not line.strip():
                i += 1
            elif line.startswith("```"):
                j = i + 1
                while j < n and not lines[j].startswith("```"):
                    j += 1
                out.append("<pre><code>" + esc("\n".join(lines[i + 1:j])) + "</code></pre>")
                i = j + 1
            elif (m := _ADMONITION.match(line)) and m[1] in ADMONITIONS:
                j = i + 1
                while j < n and lines[j].strip() != ":::":
                    j += 1
                title = self.inline(m[2]) if m[2] else esc(m[1])
                out.append(f'<div class="admonition admonition-{m[1]}"><div class="admonition-heading">{title}</div>'
                           f'<div class="admonition-content">{self.blocks(lines[i + 1:j])}</div></div>')
                i = j + 1
            elif m := _HEADING.match(line):
                out.append(self.heading(len(m[1]), m[2], m[3]))
                i += 1
            elif _RULE.match(line):
                out.append("<hr>")
                i += 1
            elif "|" in line and i + 1 < n and "|" in lines[i + 1] and _TABLE_RULE.match(lines[i + 1]):
                j = i + 2
                while j < n and "|" in lines[j]:
                    j += 1
                out.append(self.table(lines[i:j]))
                i = j
            elif _ITEM.match(line):
                markup, i = self.list(lines, i)
                out.append(markup)
            elif line.startswith(">"):
                j = i
                while j < n and lines[j].startswith(">"):
                    j += 1
                quoted = [re.sub(r"^> ?", "", quote) for quote in lines[i:j]]
                out.append(f"<blockquote>{self.blocks(quoted)}</blockquote>")
                i = j
            elif RAW_HTML.match(line):
                j = i
                while j < n and lines[j].strip():
                    j += 1
                out.append("\n".join(lines[i:j]))
                i = j
            else:
                j = i + 1
                while j < n and lines[j].strip() and not self.opens_block(lines[j]):
                    j += 1
                text = " ".join(part.strip() for part in lines[i:j])
                out.append("<p>" + self.inline(text).replace("\\ ", "<br>") + "</p>")
                i = j
        return "\n".join(out)

    @staticmethod
    def opens_block(line: str) -> bool:
        return bool(line.startswith(("```", ">")) or _HEADING.match(line) or _ITEM.match(line)
                    or _ADMONITION.match(line))

    def heading(self, level: int, text: str, anchor: str | None) -> str:
        if level == 2 and self.number and not text[:1].isdigit():
            self.section += 1
            text = f"{self.number}{self.section}. {text}"
        markup = self.inline(text)
        anchor = anchor or slugify(plain(markup)) or "section"
        seen = self.ids.get(anchor, 0)
        self.ids[anchor] = seen + 1
        if seen:
            anchor = f"{anchor}-{seen}"
        if level in (2, 3):
            self.toc.append((level, anchor, plain(markup)))
        label = attr(self.labels("Direct link to this heading"))
        return (f'<h{level} id="{attr(anchor)}">{markup}'
                f'<a class="hash-link" href="#{attr(anchor)}" aria-label="{label}"></a></h{level}>')

    def table(self, rows: list[str]) -> str:
        def cells(row: str) -> list[str]:
            row = row.strip()
            row = row[1:] if row.startswith("|") else row
            row = row[:-1] if row.endswith("|") and not row.endswith("\\|") else row
            return [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", row)]

        head, rule, *body = (cells(row) for row in rows)
        aligns = []
        for mark in rule:
            side = "center" if mark.startswith(":") and mark.endswith(":") else \
                "right" if mark.endswith(":") else "left" if mark.startswith(":") else ""
            aligns.append(f' style="text-align:{side}"' if side else "")

        def tr(tag: str, row: list[str]) -> str:
            row = row + [""] * (len(aligns) - len(row))
            return "<tr>" + "".join(f"<{tag}{align}>{self.inline(cell)}</{tag}>"
                                    for cell, align in zip(row, aligns)) + "</tr>"

        # A table with an empty header row is a plain two-way list of examples.
        thead = f"<thead>{tr('th', head)}</thead>" if any(head) else ""
        tbody = "".join(tr("td", row) for row in body)
        return f'<div class="table-wrap"><table>{thead}<tbody>{tbody}</tbody></table></div>'

    def list(self, lines: list[str], i: int) -> tuple[str, int]:
        first = _ITEM.match(lines[i])
        indent, ordered = len(first[1]), first[2][0].isdigit()
        items: list[list[str]] = []
        n = len(lines)
        while i < n:
            line = lines[i]
            item = _ITEM.match(line)
            deeper = len(line) - len(line.lstrip()) > indent
            if item and len(item[1]) == indent and item[2][0].isdigit() == ordered:
                items.append([item[3]])
            elif line.strip() and deeper and items:
                items[-1].append(line)
            elif not line.strip() and items:
                # A blank line stays in the item only if indented text follows it.
                j = i
                while j < n and not lines[j].strip():
                    j += 1
                if j == n or len(lines[j]) - len(lines[j].lstrip()) <= indent:
                    break
                items[-1].append("")
            else:
                break
            i += 1
        rendered = []
        for head, *rest in items:
            inner = self.inline(head)
            if any(part.strip() for part in rest):
                margin = min(len(part) - len(part.lstrip()) for part in rest if part.strip())
                inner += "\n" + self.blocks([part[margin:] for part in rest])
            rendered.append(f"<li>{inner}</li>")
        tag = "ol" if ordered else "ul"
        return f"<{tag}>{''.join(rendered)}</{tag}>", i

    def footnotes(self) -> str:
        title = esc(self.labels("Footnotes"))
        self.toc.append((2, "footnotes", self.labels("Footnotes")))
        items = "".join(
            f'<li id="fn-{n}">{self.inline(self.notes[key])} <a href="#fnref-{n}" class="footnote-back">↩</a></li>'
            for n, key in enumerate(self.cited, 1))
        return f'<section class="footnotes"><h2 id="footnotes">{title}</h2><ol>{items}</ol></section>'

    # -- inline --------------------------------------------------------------

    def inline(self, text: str) -> str:
        kept: list[str] = []

        def keep(markup: str) -> str:
            kept.append(markup)
            return f"\x00{len(kept) - 1}\x00"

        text = re.sub(r"\\([\\`*\[\]|!#])", lambda m: keep(esc(m[1])), text)
        text = re.sub(r"`([^`]+)`", lambda m: keep(f"<code>{esc(m[1])}</code>"), text)
        text = re.sub(r"\[\^([^\]]+)\]", lambda m: keep(self.footnote_ref(m[1])), text)
        text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", lambda m: keep(
            f'<img src="{attr(self.resolve(m[2]))}" alt="{attr(m[1])}" loading="lazy">'), text)
        text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: keep(self.anchor(m[2], self.emphasis(esc(m[1])))), text)
        text = self.emphasis(esc(text))
        while "\x00" in text:
            text = re.sub(r"\x00(\d+)\x00", lambda m: kept[int(m[1])], text)
        return text

    @staticmethod
    def emphasis(text: str) -> str:
        text = re.sub(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", r"<strong>\1</strong>", text)
        return re.sub(r"(?<![\w*])\*(?=\S)(.+?)(?<=\S)\*(?![\w*])", r"<em>\1</em>", text)

    def anchor(self, target: str, text: str) -> str:
        if re.match(r"(https?:|mailto:)", target):
            return f'<a href="{attr(target)}" target="_blank" rel="noopener noreferrer" class="external">{text}</a>'
        return f'<a href="{attr(self.resolve(target))}">{text}</a>'

    def footnote_ref(self, key: str) -> str:
        if key not in self.notes:
            return esc(f"[^{key}]")
        if key not in self.cited:
            self.cited.append(key)
        n = self.cited.index(key) + 1
        return f'<sup class="footnote-ref"><a href="#fn-{n}" id="fnref-{n}">{n}</a></sup>'


def read_markdown(path: Path) -> tuple[dict, str]:
    """A Markdown file's front matter (YAML between --- lines) and its body."""
    text = path.read_text(encoding="utf-8")
    front = re.match(r"---\n(.*?)\n---\n?", text, flags=re.DOTALL)
    if not front:
        return {}, text
    return yaml.safe_load(front[1]) or {}, text[front.end():]


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@dataclass
class Page:
    route: str                     # path without .html: lessons/pronouns/subject-pronouns
    kind: str                      # home, category, doc, page, blog, post
    title: str = ""                # in the default locale, without its number
    titles: dict[str, str] = field(default_factory=dict)  # other locales: code → title
    number: str = ""               # "4." for a category, "4.1." for a lesson
    section: str = ""              # which sidebar: lessons, resources, blog
    source: str = ""               # body, as a path under content/ without .md
    done: bool = False
    parent: "Page | None" = None
    children: list["Page"] = field(default_factory=list)
    date: datetime.date | None = None


def load_pages(config: dict, sidebar: dict) -> dict[str, list[Page]]:
    """Every page of one locale, grouped: lessons (in sidebar order), resources, pages, posts."""
    def titles(entry: dict) -> dict[str, str]:
        # An entry of sidebar.yml or site.yml names a locale's title under its code (es: ...).
        return {code: entry[code] for code in config["locales"] if code in entry}

    lessons: list[Page] = []
    number = 0
    for entry in sidebar["lessons"]:
        numbered = entry.get("numbered", True)
        number += numbered
        prefix = f"{number}." if numbered else ""
        slug = slugify(f"{prefix} {entry['title']}")
        category = Page(f"category/{slug}", "category", entry["title"], titles(entry), prefix, "lessons")
        lessons.append(category)
        for position, lesson in enumerate(entry["lessons"], 1):
            path = f"lessons/{entry['dir']}/{lesson['slug']}"
            page = Page(path, "doc", lesson["title"], titles(lesson), f"{prefix}{position}." if numbered else "",
                        "lessons", path, bool(lesson.get("done")), category)
            category.children.append(page)
            lessons.append(page)
        category.done = bool(category.children) and all(child.done for child in category.children)
    for entry in sidebar.get("pages", []):
        path = f"lessons/{entry['slug']}"
        lessons.append(Page(path, "doc", entry["title"], titles(entry), "", "lessons", path,
                            bool(entry.get("done"))))
    resources = [Page(f"resources/{entry['slug']}", "doc", entry["title"], titles(entry), "", "resources",
                      f"resources/{entry['slug']}") for entry in sidebar.get("resources", [])]
    pages = [Page(entry["path"], "page", entry["title"], titles(entry), source=entry["path"])
             for entry in config.get("pages", [])]
    posts = []
    for path in sorted((CONTENT / "blog").glob("*.md"), reverse=True):
        stamp = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.+)", path.stem)
        if not stamp:
            raise SystemExit(f"{path}: a post is named YYYY-MM-DD-slug.md")
        title = str(read_markdown(path)[0].get("title", stamp[4]))
        # A translated post carries its own title, in i18n/<code>/blog/<same name>.
        other = {}
        for code in config["locales"]:
            translated = SITE / "i18n" / code / "blog" / path.name
            if translated.is_file():
                other[code] = str(read_markdown(translated)[0].get("title", title))
        posts.append(Page(f"blog/{stamp[4]}", "post", title, other,
                          section="blog", source=f"blog/{path.stem}",
                          date=datetime.date(int(stamp[1]), int(stamp[2]), int(stamp[3]))))
    return {"lessons": lessons, "resources": resources, "pages": pages, "posts": posts}


def merged(base, override):
    """`override` laid over `base`: mappings key by key, lists item by item."""
    if isinstance(base, dict) and isinstance(override, dict):
        return {**base, **{key: merged(base.get(key), value) for key, value in override.items()}}
    if isinstance(base, list) and isinstance(override, list):
        return [merged(old, new) for old, new in zip(base, override)] + base[len(override):]
    return base if override is None else override


class Locale:
    """One language edition of the site."""

    def __init__(self, code: str, config: dict, sidebar: dict, default: str):
        self.code, self.default = code, default
        self.prefix = "" if code == default else f"{code}/"
        wording = {}
        if code != default:
            wording = yaml.safe_load((SITE / "i18n" / f"{code}.yml").read_text(encoding="utf-8")) or {}
        self.strings: dict[str, str] = wording.get("strings", {})
        self.config = merged(config, wording.get("site", {}))
        self.locales: dict[str, str] = config["locales"]
        groups = load_pages(config, sidebar)
        self.lessons, self.resources = groups["lessons"], groups["resources"]
        self.posts = groups["posts"]
        self.home = Page("index", "home", self.config["title"])
        self.blog = Page("blog", "blog", "Blog", section="blog")
        self.pages = [self.home, *self.lessons, *self.resources, *groups["pages"], self.blog, *self.posts]
        self.routes = {page.route: page for page in self.pages}
        self.problems: list[str] = []
        self.search: list[dict] = []

    def t(self, label: str) -> str:
        return self.strings.get(label, label)

    def title(self, page: Page) -> str:
        """A page's title as shown: numbered, and checked once its lesson is done."""
        name = page.titles.get(self.code) or self.t(page.title)
        if page.number:
            name = f"{page.number} {name}"
        return name + (" ✅" if page.done else "")

    def date(self, day: datetime.date) -> str:
        month = MONTHS.get(self.code, MONTHS["en"])[day.month - 1]
        return f"{day.day} de {month} de {day.year}" if self.code == "es" else f"{month} {day.day}, {day.year}"

    # -- paths ---------------------------------------------------------------

    def file(self, route: str) -> str:
        return f"{self.prefix}{route}.html"

    def link(self, current: Page, route: str) -> str:
        """The relative URL of a page of this locale, seen from `current`."""
        return posixpath.relpath(self.file(route), posixpath.dirname(self.file(current.route)) or ".")

    def asset(self, current: Page, path: str) -> str:
        return posixpath.relpath(path, posixpath.dirname(self.file(current.route)) or ".")

    def resolver(self, current: Page):
        """How a link written in a Markdown body becomes an href on `current`."""
        def resolve(target: str) -> str:
            if not target.startswith("/"):
                return target
            path, _, fragment = target[1:].partition("#")
            path = re.sub(r"\.(html|md)$", "", path.strip("/")) or "index"
            if path in self.routes:
                url = self.link(current, path)
            elif (SITE / "static" / path).is_file():
                url = self.asset(current, path)
            else:
                self.problems.append(f"{current.source or current.route}: no page or file /{path}")
                url = target
            return url + (f"#{fragment}" if fragment else "")
        return resolve

    def body_file(self, page: Page) -> Path | None:
        """A page's Markdown: this locale's translation if there is one, else the default locale's."""
        if not page.source:
            return None
        candidates = [CONTENT / f"{page.source}.md"]
        if self.code != self.default:
            candidates.insert(0, SITE / "i18n" / self.code / f"{page.source}.md")
        return next((path for path in candidates if path.is_file()), None)

    # -- bodies --------------------------------------------------------------

    def body(self, page: Page) -> tuple[str, list, str]:
        """A page's HTML, its table of contents, and a one-line description."""
        path = self.body_file(page)
        if path is None:
            notice = esc(self.t("Under construction"))
            markup = (f'<p class="construction">🚧 <strong>{notice.upper()}</strong></p>'
                      f'<p>{esc(self.t("This page has not been written yet."))}</p>')
            return markup, [], f"🚧 {notice}"
        meta, text = read_markdown(path)
        markup, toc = Markdown(self.resolver(page), self.t).render(text, page.number)
        first = re.search(r"<(h[2-6]|p)\b[^>]*>(.*?)</\1>", markup, flags=re.DOTALL)
        return markup, toc, str(meta.get("description") or (plain(first[2]) if first else ""))

    # -- chrome --------------------------------------------------------------

    def navbar(self, page: Page) -> str:
        t, links = self.t, []
        for item in self.config["navbar"]:
            target = self.routes[item["to"]]
            active = page.route == target.route or bool(target.section and target.section == page.section)
            links.append(f'<a class="nav-link{" active" if active else ""}" href="{self.link(page, target.route)}">'
                         f'{esc(t(item["label"]))}</a>')
        languages = []
        for code, name in self.locales.items():
            prefix = "" if code == self.default else f"{code}/"
            url = posixpath.relpath(f"{prefix}{page.route}.html", posixpath.dirname(self.file(page.route)) or ".")
            languages.append(f'<li><a href="{url}" lang="{code}"{" class=\"active\"" if code == self.code else ""}>'
                             f'{esc(name)}</a></li>')
        name = self.config["language"].lower()
        brand = f"{esc(name[:-5])}<span>{esc(name[-5:])}</span>" if name.endswith("ultra") else esc(name)
        return f'''<nav class="navbar" aria-label="{attr(t("Main"))}">
<button class="navbar-toggle icon-button" type="button" aria-label="{attr(t("Toggle navigation bar"))}" aria-expanded="false">{ICONS["menu"]}</button>
<a class="brand" href="{self.link(page, "index")}" aria-label="{attr(t("Home page"))}"><img src="{self.asset(page, "img/logo.svg")}" alt="" width="44" height="32"><b>{brand}</b></a>
<div class="nav-links">{"".join(links)}</div>
<div class="navbar-right">
<div class="dropdown"><button class="dropdown-toggle" type="button" aria-haspopup="true" aria-expanded="false" aria-label="{attr(t("Languages"))}">{ICONS["globe"]}<span>{esc(self.locales[self.code])}</span>{ICONS["caret"]}</button><ul class="dropdown-menu">{"".join(languages)}</ul></div>
<button class="theme-toggle icon-button" type="button" title="{attr(t("Switch between dark and light mode"))}" aria-label="{attr(t("Switch between dark and light mode"))}">{ICONS["sun"]}{ICONS["moon"]}</button>
<button class="search-button" type="button" aria-label="{attr(t("Search"))}">{ICONS["search"]}<span>{esc(t("Search"))}</span><kbd>⌘</kbd><kbd>K</kbd></button>
</div>
</nav>'''

    def footer(self, page: Page) -> str:
        columns = []
        for column in self.config["footer"]:
            items = []
            for item in column["links"]:
                label = esc(self.t(item["label"]))
                if "href" in item:
                    items.append(f'<li><a href="{attr(item["href"])}" target="_blank" rel="noopener noreferrer" '
                                 f'class="external">{label}</a></li>')
                else:
                    items.append(f'<li><a href="{self.link(page, item["to"])}">{label}</a></li>')
            columns.append(f'<div class="footer-col"><div class="footer-title">{esc(self.t(column["title"]))}</div>'
                           f'<ul>{"".join(items)}</ul></div>')
        year = datetime.date.today().year
        return (f'<footer class="footer"><div class="footer-links">{"".join(columns)}</div>'
                f'<div class="footer-copyright">Copyright © {year} {esc(self.config["copyright"])}.</div></footer>')

    def menu(self, page: Page) -> str:
        """The sidebar of the section `page` is in."""
        if page.section == "resources":
            items = [self.menu_link(page, entry) for entry in self.resources]
        elif page.section == "blog":
            items = [self.menu_link(page, post) for post in self.posts]
            heading = f'<div class="menu-heading">{esc(self.t("Recent posts"))}</div>'
            return f'{heading}<ul class="menu-list">{"".join(items)}</ul>'
        else:
            items = []
            for entry in self.lessons:
                if entry.kind == "category":
                    is_open = page is entry or page.parent is entry
                    children = "".join(self.menu_link(page, child) for child in entry.children)
                    items.append(
                        f'<li class="menu-category{" open" if is_open else ""}">'
                        f'<div class="menu-row{" active" if page is entry else ""}">'
                        f'<a class="menu-link{" active" if is_open else ""}" href="{self.link(page, entry.route)}">'
                        f'{esc(self.title(entry))}</a><button class="menu-caret" type="button" '
                        f'aria-expanded="{str(is_open).lower()}" '
                        f'aria-label="{attr(self.t("Expand or collapse this category"))}"></button></div>'
                        f'<ul class="menu-list">{children}</ul></li>')
                elif entry.parent is None:
                    items.append(self.menu_link(page, entry))
        return f'<ul class="menu-list">{"".join(items)}</ul>'

    def menu_link(self, page: Page, target: Page) -> str:
        current = ' active" aria-current="page' if page is target else ""
        return (f'<li><a class="menu-link{current}" href="{self.link(page, target.route)}">'
                f'{esc(self.title(target))}</a></li>')

    def breadcrumbs(self, page: Page) -> str:
        crumbs = [f'<li><a class="crumb-home" href="{self.link(page, "index")}" '
                  f'aria-label="{attr(self.t("Home page"))}">{ICONS["home"]}</a></li>']
        if page.parent:
            crumbs.append(f'<li><a href="{self.link(page, page.parent.route)}">{esc(self.title(page.parent))}</a></li>')
        crumbs.append(f'<li class="active"><span>{esc(self.title(page))}</span></li>')
        return f'<nav class="breadcrumbs" aria-label="{attr(self.t("Breadcrumbs"))}"><ul>{"".join(crumbs)}</ul></nav>'

    def pagination(self, page: Page, order: list[Page], older_newer: bool = False) -> str:
        if page not in order:
            return ""
        at = order.index(page)
        labels = ("Newer post", "Older post") if older_newer else ("Previous", "Next")
        cells = []
        for step, side, label in ((-1, "prev", labels[0]), (1, "next", labels[1])):
            if 0 <= at + step < len(order):
                other = order[at + step]
                name = esc(self.title(other))
                name = f"« {name}" if side == "prev" else f"{name} »"
                cells.append(f'<a class="pagination-link pagination-{side}" href="{self.link(page, other.route)}">'
                             f'<div class="pagination-sublabel">{esc(self.t(label))}</div>'
                             f'<div class="pagination-label">{name}</div></a>')
            else:
                cells.append("<span></span>")
        return f'<nav class="pagination" aria-label="{attr(self.t("Docs pages"))}">{"".join(cells)}</nav>'

    @staticmethod
    def toc(entries: list, label: str) -> str:
        if not entries:
            return ""
        items = "".join(f'<li class="toc-level-{level}"><a href="#{attr(anchor)}">{esc(text)}</a></li>'
                        for level, anchor, text in entries)
        return f'<aside class="toc" aria-label="{attr(label)}"><ul>{items}</ul></aside>'

    def document(self, page: Page, main: str, description: str = "") -> str:
        """A whole HTML page around `main`."""
        t, config = self.t, self.config
        name = self.title(page) if page.kind != "home" else config["title"]
        heading = name if page.kind == "home" else f"{name} | {config['title']}"
        root = posixpath.relpath(".", posixpath.dirname(self.file(page.route)) or ".")
        here = posixpath.relpath(self.prefix or ".", posixpath.dirname(self.file(page.route)) or ".")
        labels = {key: t(key) for key in ("Search the lessons", "Type to search", "No results for", "to select",
                                           "to navigate", "to close", "Close navigation bar")}
        return f'''<!doctype html>
<html lang="{self.code}" data-root="{root}/" data-locale-root="{here}/" data-locale="{self.code}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(heading)}</title>
<meta name="description" content="{attr(description or config["description"])}">
<link rel="icon" href="{self.asset(page, "img/favicon.svg")}" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{self.asset(page, "assets/site.css")}">
<script>(function(){{var m;try{{m=localStorage.getItem("theme")}}catch(e){{}}if(m!=="dark"&&m!=="light")m=matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";document.documentElement.setAttribute("data-theme",m)}})()</script>
</head>
<body class="page-{page.kind}">
<a class="skip-link" href="#main">{esc(t("Skip to main content"))}</a>
{self.navbar(page)}
{main}
{self.footer(page)}
<script type="application/json" id="site-labels">{json.dumps(labels, ensure_ascii=False)}</script>
<script src="{self.asset(page, "assets/site.js")}" defer></script>
</body>
</html>
'''

    def with_sidebar(self, page: Page, article: str, toc: str = "") -> str:
        t = self.t
        return f'''<div class="docs">
<aside class="sidebar" aria-label="{attr(t("Docs sidebar"))}"><nav class="menu">{self.menu(page)}</nav>
<button class="sidebar-collapse" type="button" title="{attr(t("Collapse sidebar"))}" aria-label="{attr(t("Collapse sidebar"))}" data-expand="{attr(t("Expand sidebar"))}">{ICONS["collapse"]}</button></aside>
<main class="doc-main" id="main"><div class="doc-row"><article class="doc">{article}</article>{toc}</div></main>
</div>'''

    # -- page kinds ----------------------------------------------------------

    def render(self, page: Page) -> str:
        if page.kind == "home":
            return self.render_home(page)
        if page.kind == "category":
            return self.render_category(page)
        if page.kind == "blog":
            return self.render_blog(page)
        markup, toc, description = self.body(page)
        title = esc(self.title(page))
        # A page that is not written yet is found by its title only.
        self.index(page, markup if self.body_file(page) else "", toc)
        if page.kind == "post":
            article = (f'<div class="markdown"><h1>{title}</h1><p class="post-date">{esc(self.date(page.date))}</p>'
                       f'{markup}</div>{self.pagination(page, self.posts, older_newer=True)}')
            return self.document(page, self.with_sidebar(page, article, self.toc(toc, self.t("On this page"))),
                                 description)
        if page.kind == "page":
            main = f'<main class="plain-main" id="main"><article class="markdown"><h1>{title}</h1>{markup}</article></main>'
            return self.document(page, main, description)
        order = self.lessons if page.section == "lessons" else self.resources
        article = (f'{self.breadcrumbs(page)}<div class="markdown"><h1>{title}</h1>{markup}</div>'
                   f'{self.pagination(page, order)}')
        return self.document(page, self.with_sidebar(page, article, self.toc(toc, self.t("On this page"))), description)

    def render_home(self, page: Page) -> str:
        home = self.config["home"]
        features = "".join(
            f'<div class="feature"><img src="{self.asset(page, "img/" + feature["image"])}" alt="" width="200" '
            f'height="200"><h3>{esc(feature["title"])}</h3><p>{esc(feature["text"])}</p></div>'
            for feature in home["features"])
        button = home["button"]
        main = f'''<header class="hero"><div class="container"><h1 class="hero-title">{esc(home["title"])}</h1>
<p class="hero-subtitle">{esc(home["subtitle"])}</p>
<a class="button" href="{self.link(page, button["to"])}">{esc(button["label"])}</a></div></header>
<main id="main"><section class="features"><div class="container">{features}</div></section></main>'''
        self.index(page, f'<p>{esc(home["subtitle"])}</p>', [])
        return self.document(page, main)

    def render_category(self, page: Page) -> str:
        cards = []
        for child in page.children:
            description = self.body(child)[2]
            cards.append(f'<a class="card" href="{self.link(page, child.route)}"><h2 title="{attr(self.title(child))}">'
                         f'📄️ {esc(self.title(child))}</h2><p title="{attr(description)}">{esc(description)}</p></a>')
        article = (f'{self.breadcrumbs(page)}<div class="markdown"><h1>{esc(self.title(page))}</h1></div>'
                   f'<div class="cards">{"".join(cards)}</div>{self.pagination(page, self.lessons)}')
        self.index(page, "", [])
        return self.document(page, self.with_sidebar(page, article))

    def render_blog(self, page: Page) -> str:
        entries = []
        for post in self.posts:
            # Up to the post's first heading, with its links resolved from this page.
            _, text = read_markdown(self.body_file(post))
            markup, _ = Markdown(self.resolver(page), self.t).render(re.split(r"^## ", text, flags=re.M)[0])
            url = self.link(page, post.route)
            entries.append(f'<article class="post-summary"><h2><a href="{url}">{esc(self.title(post))}</a></h2>'
                           f'<p class="post-date">{esc(self.date(post.date))}</p><div class="markdown">{markup}</div>'
                           f'<a class="read-more" href="{url}">{esc(self.t("Read more"))} »</a></article>')
        if not entries:
            entries.append(f'<p>{esc(self.t("No posts yet."))}</p>')
        self.index(page, "", [])
        heading = f'<h1 class="visually-hidden">{esc(self.title(page))}</h1>'
        return self.document(page, self.with_sidebar(page, heading + "".join(entries)))

    def index(self, page: Page, markup: str, toc: list) -> None:
        """Add a page to this locale's search index."""
        group = self.title(page.parent) if page.parent else ""
        self.search.append({"u": f"{page.route}.html", "t": self.title(page) if page.kind != "home" else self.config["title"],
                            "g": group, "h": [text for _, _, text in toc], "x": plain(markup)[:SEARCH_TEXT_LIMIT]})


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build(out: Path) -> int:
    config = yaml.safe_load((SITE / "site.yml").read_text(encoding="utf-8"))
    sidebar = yaml.safe_load((SITE / "sidebar.yml").read_text(encoding="utf-8"))
    default = next(iter(config["locales"]))
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(SITE / "static", out)
    problems, written, unwritten = [], 0, 0
    for code in config["locales"]:
        locale = Locale(code, config, sidebar, default)
        known = {item["to"] for item in config["navbar"]} | {config["home"]["button"]["to"]} | {
            link["to"] for column in config["footer"] for link in column["links"] if "to" in link}
        problems += [f"site.yml: no page {route}" for route in sorted(known - set(locale.routes))]
        if problems:
            break
        for page in locale.pages:
            path = out / locale.file(page.route)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(locale.render(page), encoding="utf-8")
            written += 1
            if code == default and page.source and locale.body_file(page) is None:
                unwritten += 1
        index = json.dumps(locale.search, ensure_ascii=False, separators=(",", ":"))
        (out / "assets" / f"search-{code}.js").write_text(f"window.SEARCH_INDEX={index};\n", encoding="utf-8")
        problems += [f"[{code}] {problem}" for problem in dict.fromkeys(locale.problems)]
    for problem in problems:
        print(f"error: {problem}", file=sys.stderr)
    if problems:
        return 1
    print(f"{written} pages in {len(config['locales'])} locales → {out.relative_to(ROOT)}/ "
          f"({unwritten} pages still under construction)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=OUT, help="output folder (replaced on every build)")
    args = parser.parse_args()
    out = args.out.resolve()
    if not out.is_relative_to(ROOT) or out in (ROOT, SITE):
        parser.error("--out must be a folder of its own inside the repository")
    return build(out)


if __name__ == "__main__":
    sys.exit(main())
