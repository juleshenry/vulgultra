#!/usr/bin/env python3
"""Verb picks: the hand-picked paradigms in verb_ending_notes.txt, as tables.

The notes stay where picks are written, in their own loose format: a heading
line per verb (``stare ❯``), free notes, and one line per tense,
``Indicative · Present -- toi, tas, ...`` with six forms from 1sg to 3pl. A
form may carry a note in brackets (``tié (an)``); ``n/a`` is a slot with no
form, and an empty slot (``am, ai, , , ajam``) is one still to fill.

Each pick is looked up in the harvest the shortlist reads, so every cell shows
the attested forms it comes from, or that no lect has it whole. A row with a
form too few and no empty slot gets its gap where the most forms line up with
the harvest.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import unicodedata
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import verb_ending_candidates as vec  # noqa: E402

DEFAULT_NOTES = ROOT / "docs" / "eval" / "verb_ending_notes.txt"
DEFAULT_OUTPUT = ROOT / "docs" / "eval" / "verb_picks.html"
SLOTS = vec.PERSON_SLOTS  # 1sg 2sg 3sg 1pl 2pl 3pl, the order the notes use
SHORT = {
    "indicative.present": "pres.", "indicative.imperfect": "impf.",
    "indicative.preterite": "pret.", "indicative.future": "fut.",
    "indicative.pluperfect": "plup.", "subjunctive.present": "subj. pres.",
    "subjunctive.imperfect": "subj. impf.", "subjunctive.future": "subj. fut.",
    "conditional": "cond.", "imperative": "imp.",
}
ALIASES = {"havere": "habere", "avere": "habere", "essere": "esse", "estar": "stare"}
TAM_LABEL = {
    tam: re.compile(r"^\s*" + r"\s*·\s*".join(map(re.escape, tam.split("."))) + r"(?=\s|-|$)(?P<rest>.*)$", re.I)
    for tam in vec.TAMS
}
ITEM = re.compile(r"^(?P<form>[^\s(\[]+)\s*(?P<note>[(\[].*)?$")
MISSING = object()


def bare(text: str) -> str:
    """Lowercase, accents off: the key forms are compared on."""
    return "".join(
        c for c in unicodedata.normalize("NFD", text.lower()) if not unicodedata.combining(c)
    )


def tam_of(label: str) -> str | None:
    tam = re.sub(r"\s*·\s*", ".", label.strip().lower())
    return tam if tam in vec.TAMS else None


def tense_line(line: str) -> tuple[str, str] | None:
    """(tam, forms text) for a line that starts with a tense name; ``--`` optional."""
    for tam, pattern in TAM_LABEL.items():
        m = pattern.match(line)
        if m:
            return tam, m["rest"].strip().removeprefix("--").strip()
    return None


def split_items(text: str) -> list:
    """'[toi, tié (an), n/a, , ]' → [(form, note) | None | MISSING]."""
    text = text.strip().rstrip("-").strip()
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]
    raws = [raw.strip() for raw in text.split(",")]
    if raws and not raws[-1]:
        raws.pop()  # a trailing comma is not a slot
    items: list = []
    for raw in raws:
        if not raw:
            items.append(MISSING)
        elif raw.lower() == "n/a":
            items.append(None)
        else:
            m = ITEM.match(raw)
            items.append((m["form"], (m["note"] or "").strip()) if m else (raw, ""))
    return items


def is_heading(line: str) -> bool:
    """``stare ❯``, or one word alone at the margin that is not a tense."""
    text = line.rstrip()
    if text.endswith("❯"):
        return True
    return not line[:1].isspace() and len(text.split()) == 1 and tam_of(text) is None


def parse(path: Path) -> list[dict]:
    """[{title, notes: [str], rows: [(tam, [items])]}] in file order."""
    verbs: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        if is_heading(line):
            verbs.append({"title": line.rstrip().rstrip("❯").strip(), "notes": [], "rows": []})
            continue
        if not verbs:
            verbs.append({"title": "", "notes": [], "rows": []})
        found = tense_line(line)
        if found is None:
            verbs[-1]["notes"].append(line.strip())
        elif found[1]:
            verbs[-1]["rows"].append((found[0], split_items(found[1])))
    return verbs


def verb_key(title: str) -> str:
    return ALIASES.get(title.lower(), title.lower())


def harvest_for(title: str, named: dict, regular: dict):
    """(kind, tam → slot → candidates) for a heading, or (None, {})."""
    key = verb_key(title)
    for verb in vec.NAMED_VERBS:
        if key.startswith(verb):
            return "word", named.get(verb, {})
    for theme in vec.THEMES:
        if key.startswith(f"{theme}-theme") or key == theme:
            return "ending", regular.get(theme, {})
    return None, {}


def sources(pick: str, kind: str | None, cands: dict) -> list[tuple[str, list[str]]]:
    """Harvested (form, lects) a pick comes from; exact spellings first.

    A word pick may drop up to two initial letters of its source (es-, s-);
    an ending pick must equal the ending.
    """
    p = bare(pick.lstrip("-"))
    exact, near = [], []
    for form, backers in cands.items():
        lects = [b[0] if isinstance(b, tuple) else b for b in backers]
        f = bare(form)
        if kind == "word":
            hit = f.endswith(p) and len(f) - len(p) <= 2
        else:
            hit = f == p
        if hit:
            same = form.lower().endswith(pick.lower().lstrip("-"))
            (exact if same else near).append((form, list(dict.fromkeys(lects))))
    return exact + near


def place(items: list, kind: str | None, slots: dict) -> list:
    """Six slots. A row with an empty slot is read as written; a short row
    without one gets its gaps where most forms match the harvest."""
    if len(items) >= len(SLOTS):
        return items[: len(SLOTS)]
    if any(item is MISSING for item in items):
        return items + [MISSING] * (len(SLOTS) - len(items))
    missing = len(SLOTS) - len(items)

    def laid(gaps: tuple[int, ...]) -> list:
        it = iter(items)
        return [MISSING if i in gaps else next(it) for i in range(len(SLOTS))]

    def score(gaps: tuple[int, ...]) -> int:
        return sum(
            1 for slot, item in zip(SLOTS, laid(gaps))
            if item not in (None, MISSING) and sources(item[0], kind, slots.get(slot) or {})
        )

    best = max(combinations(range(len(SLOTS)), missing), key=lambda g: (score(g), g))
    return laid(best)


def chips(lects) -> str:
    return "".join(vec._lect(lect) for lect in list(lects)[:5])


def cell(item, found) -> str:
    if item is MISSING:
        return '<td class="gap"><span class="flag miss">missing</span></td>'
    if item is None:
        return '<td class="na"><span class="none">n/a</span></td>'
    form, note = item
    parts = [f'<div class="pick">{html.escape(form)}</div>']
    if note:
        parts.append(f'<div class="mine">{html.escape(note)}</div>')
    if found:
        parts.extend(
            f'<div class="src"><i>{html.escape(src)}</i>{chips(lects)}</div>' for src, lects in found[:3]
        )
    else:
        parts.append('<div class="src"><span class="flag built">built</span></div>')
    return f"<td>{''.join(parts)}</td>"


def table(rows: list[tuple[str, list[str]]]) -> str:
    """rows of (tam, six <td> strings) → a tense × person table, moods as bands."""
    body, mood = [], None
    for tam, tds in rows:
        if "." in tam:
            head, tense = tam.split(".", 1)
            if head != mood:
                body.append(f'<tr class="mood"><th colspan="7">{head}</th></tr>')
                mood = head
        else:
            tense, mood = tam, None
        body.append(f'<tr><th scope="row">{tense}</th>{"".join(tds)}</tr>')
    head = "".join(f"<th>{s}</th>" for s in SLOTS)
    return (
        f'<div class="wrap"><table class="para"><thead><tr><th></th>{head}</tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table></div>'
    )


def render_verb(verb: dict, named: dict, regular: dict) -> str:
    kind, harvest = harvest_for(verb["title"], named, regular)
    rows, seen = [], {}
    counts = {"forms": 0, "attested": 0, "built": 0, "missing": 0}
    for tam, items in verb["rows"]:
        slots = harvest.get(tam) or {}
        tds = []
        for slot, item in zip(SLOTS, place(items, kind, slots)):
            found = []
            if item is MISSING:
                counts["missing"] += 1
            elif item is not None:
                found = sources(item[0], kind, slots.get(slot) or {})
                counts["forms"] += 1
                counts["attested" if found else "built"] += 1
                seen.setdefault(bare(item[0]), []).append(f"{SHORT[tam]} {slot}")
            tds.append(cell(item, found))
        rows.append((tam, tds))
    key = verb_key(verb["title"])
    title = vec.NAMED_TITLE.get(key, vec.THEME_TITLE.get(key, verb["title"]))
    notes = "".join(f'<p class="note">{html.escape(n)}</p>' for n in verb["notes"])
    tally = (
        f'{counts["forms"]} forms: {counts["attested"]} found in the harvest, '
        f'{counts["built"]} built' + (f', {counts["missing"]} missing' if counts["missing"] else "") + "."
    )
    alike = [(form, where) for form, where in seen.items() if len(where) > 1]
    alike_html = ""
    if alike:
        alike_html = '<p class="alike">Written alike, accents aside: ' + "; ".join(
            f"<b>{html.escape(form)}</b> ({', '.join(where)})" for form, where in alike
        ) + ".</p>"
    return (
        f'<section class="verb"><h2>{html.escape(title)}</h2>{notes}'
        f'<p class="tally">{tally}</p>{table(rows)}{alike_html}</section>'
    )


def render(verbs: list[dict], named: dict, regular: dict, notes_path: Path) -> str:
    sections = "".join(render_verb(v, named, regular) for v in verbs if v["rows"])
    return PAGE.format(style=STYLE, source=html.escape(notes_path.name), sections=sections)


STYLE = """
:root {
  --bg: #fbfaf7; --panel: #ffffff; --ink: #1d1c1a; --muted: #6b675f; --line: #e4e0d8;
  --accent: #8a3b12; --built: #b9770e; --miss: #c0392b; --var: #6c5ce7;
  --ibero: #c0392b; --occitano: #d68910; --oil: #2e6fb7; --arpitan: #6c5ce7;
  --gallo_italian: #16a085; --italo_dalmatian: #27ae60; --rhaeto: #8e44ad;
  --sardinian: #b9770e; --eastern: #34495e;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #161514; --panel: #1f1e1c; --ink: #ece9e2; --muted: #a39e94; --line: #34322e;
    --accent: #f0a36b; --built: #e0a84a; --miss: #ef7a6c; --var: #a99cf0;
    --eastern: #9fb3c8; --ibero: #ef7a6c; --oil: #74a7e8; --rhaeto: #c08be0;
  }
}
:root[data-theme="dark"] {
  --bg: #161514; --panel: #1f1e1c; --ink: #ece9e2; --muted: #a39e94; --line: #34322e;
  --accent: #f0a36b; --built: #e0a84a; --miss: #ef7a6c; --var: #a99cf0;
  --eastern: #9fb3c8; --ibero: #ef7a6c; --oil: #74a7e8; --rhaeto: #c08be0;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink);
  font: 15px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 1200px; margin: 0 auto; padding: 20px 16px 60px; }
h1 { font-size: 1.5rem; margin: 0 0 6px; }
h2 { font-size: 1.25rem; margin: 28px 0 6px; color: var(--accent); }
h3 { font-size: 1rem; margin: 18px 0 6px; }
.lede, p.note, .tally, .alike { color: var(--muted); margin: 4px 0; }
p.note { font-style: italic; }
.tally { margin: 8px 0; }
.wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; background: var(--panel); }
table.para { width: 100%; min-width: 760px; border-collapse: collapse; table-layout: fixed; }
table.para th { font-weight: 600; color: var(--muted); font-size: .8rem; padding: 6px 8px; text-align: left; }
table.para thead th { border-bottom: 1px solid var(--line); }
table.para thead th:first-child, table.para tbody th[scope=row] { width: 104px; }
table.para tbody th[scope=row] { position: sticky; left: 0; background: var(--panel); color: var(--ink);
  text-transform: capitalize; border-right: 1px solid var(--line); }
tr.mood th { background: var(--bg); color: var(--accent); text-transform: uppercase; letter-spacing: .06em;
  font-size: .72rem; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
table.para td { vertical-align: top; padding: 6px 8px; border-bottom: 1px solid var(--line); }
table.para td + td { border-left: 1px solid var(--line); }
table.para tr:last-child td, table.para tr:last-child th { border-bottom: 0; }
.pick { font-family: "Iowan Old Style", Georgia, serif; font-size: 1.15rem; font-weight: 600; }
.mine { font-size: .75rem; color: var(--muted); }
.src { display: flex; flex-wrap: wrap; gap: 3px; align-items: baseline; font-size: .78rem; margin-top: 2px; }
.src i { margin-right: 2px; }
.lect { font-size: .7rem; padding: 0 5px; border-radius: 4px; border-left: 3px solid var(--c);
  background: color-mix(in srgb, var(--c) 12%, transparent); }
.b-ibero { --c: var(--ibero); } .b-occitano { --c: var(--occitano); } .b-oil { --c: var(--oil); }
.b-arpitan { --c: var(--arpitan); } .b-gallo_italian { --c: var(--gallo_italian); }
.b-italo_dalmatian { --c: var(--italo_dalmatian); } .b-rhaeto { --c: var(--rhaeto); }
.b-sardinian { --c: var(--sardinian); } .b-eastern { --c: var(--eastern); }
.flag { font-size: .7rem; padding: 0 6px; border-radius: 4px; border: 1px solid currentColor; white-space: nowrap; }
.flag.built { color: var(--built); }
.flag.miss { color: var(--miss); }
.flag.var { color: var(--var); }
td.gap { background: color-mix(in srgb, var(--miss) 8%, transparent); }
td.alike { background: color-mix(in srgb, var(--built) 10%, transparent); }
.none { color: var(--muted); }
"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Verb Picks</title>
<style>{style}</style>
</head>
<body>
<main>
<h1>Verb picks</h1>
<p class="lede">Paradigms picked by hand, from <code>{source}</code>. Under each form: your note, then the
harvested forms it matches (a word may drop up to two initial letters, as <i>estié</i> → <i>tié</i>).
<span class="flag built">built</span> means no lect has the form whole.
Rebuild with <code>.venv/bin/python3 scripts/build_verb_picks.py</code>.</p>
{sections}
</main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--notes", type=Path, default=DEFAULT_NOTES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    named, _lemmas = vec.load_named()
    regular, _notes = vec.load_regular()
    verbs = parse(args.notes)
    args.output.write_text(render(verbs, named, regular, args.notes), encoding="utf-8")
    print(f"{args.output.relative_to(ROOT)}: {sum(1 for v in verbs if v['rows'])} verb(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
