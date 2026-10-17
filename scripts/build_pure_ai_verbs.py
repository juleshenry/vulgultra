#!/usr/bin/env python3
"""Pure AI build: the verb system chosen by rule, next to the hand picks.

Hermetic: no usage counts. Every cell is a form a daughter has for that very
cell (an ending after the stem for the four regular themes, the whole word for
esse, stare and habere), so nothing is invented. Over those forms the system is
base plus variation: six person endings serve every tense and verb, each tense
of each verb has one base (a theme marker, or an irregular verb's stem), and a
cell that is not base + person ending is the verb's own form, a variation
asset. The rules are hard constraints; what passes is ranked by

1. the letters of the distinct pieces (the person endings, the bases, and each
   own form whole), plus one per own form;
2. then the letters of all the forms;
3. then the number of lects that have each form.

The whole system is one exact model, solved with OR-Tools CP-SAT; the page says
whether the result is proven optimal. Writes docs/eval/pure-ai-build.html.
Needs OR-Tools: .venv/bin/python3 -m pip install ortools
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations
from pathlib import Path

from ortools.sat.python import cp_model

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import build_verb_picks as picks  # noqa: E402
import verb_ending_candidates as vec  # noqa: E402
from vulgultra.phonology import from_orthography, is_phonotactically_legal  # noqa: E402

DEFAULT_OUTPUT = ROOT / "docs" / "eval" / "pure-ai-build.html"
SLOTS = vec.PERSON_SLOTS
THEMES = vec.THEMES
TAMS = vec.TAMS
IRREGULAR = ("esse", "stare", "habere")
NAMES = THEMES + IRREGULAR
SAMPLE_STEM = {"a": "kant", "e": "tem", "i": "dorm", "re": "vend"}
# Every regular ending is checked on two stems, one ending in one consonant and
# one in two, so that no ending leaves a cluster bare (respond-t).
CHECK_STEMS = {"a": ("kant", "lav"), "e": ("tem", "respond"), "i": ("dorm", "fin"), "re": ("vend", "kred")}
# No false friends: a person cannot take an ending that the daughters give the
# other persons, together, at least this many times as often.
FALSE_FRIEND = 2
BUDGET = 2
# Ranks of the objective, each far above the most the next can add up to.
PIECE, FORM, LECT = 10**9, 10**5, 1
LETTERS = {"ț": "ts", "ţ": "ts", "ș": "x", "ş": "x", "ç": "s", "ñ": "ny", "ă": "e", "ß": "ss"}


# ---------------------------------------------------------------------------
# The daughters' forms
# ---------------------------------------------------------------------------

def norm(text: str) -> str | None:
    """A harvested ending or form as plain letters, or None if it has others.
    An h that is not part of a digraph is dropped: it is silent in most of
    the lects that write it (it ho, es he, pt hei)."""
    if text.strip() in {"∅", ""}:
        return ""
    text = "".join(LETTERS.get(c, c) for c in unicodedata.normalize("NFC", text.lower().strip("-")))
    text = "".join(c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c))
    text = re.sub(r"(?<![cstpglnr])h", "", text)
    return text if all("a" <= c <= "z" for c in text) else None


def cut(row: dict[str, str]) -> tuple[str, dict[str, str | None]]:
    """The longest prefix at least four endings of a row share, and the rest of
    each ending (None where it does not share it)."""
    ends = list(row.values())
    marker = ""
    for size in range(max(map(len, ends), default=0), 0, -1):
        top = Counter(e[:size] for e in ends if len(e) >= size).most_common(1)
        if top and top[0][1] >= 4:
            marker = top[0][0]
            break
    return marker, {s: (e[len(marker):] if e.startswith(marker) else None) for s, e in row.items()}


@lru_cache(maxsize=None)
def legal(form: str) -> bool:
    if not form:
        return False
    try:
        return is_phonotactically_legal(from_orthography(form))
    except Exception:
        return False


def is_subjunctive(tam: str) -> bool:
    return tam.startswith("subjunctive.")


def harvest() -> dict:
    regular, _ = vec.load_regular()
    named, _ = vec.load_named()
    # Each lect's rows: plain letters for the pieces, accents kept for the
    # daughters' own syncretism (pt cantará is not cantara).
    rows: dict = defaultdict(dict)
    accented: dict = defaultdict(dict)
    for theme, tams in regular.items():
        for tam, slots in tams.items():
            for slot, endings in slots.items():
                for ending, sources in endings.items():
                    e = norm(ending)
                    for lect, cls, support in sources:
                        if support < vec.THIN:
                            continue
                        accented[(theme, lect, cls)][(tam, slot)] = unicodedata.normalize(
                            "NFC", ending.lower().strip("-"))
                        if e is not None:
                            rows[(theme, tam, lect, cls)][slot] = e
    # Which persons a tense has: those in at least half the daughters' rows.
    # No Romance imperative has a first person singular, whatever the tables fill in.
    slots_of: dict = defaultdict(Counter)
    for (_theme, tam, _lect, _cls), row in rows.items():
        slots_of[tam].update(list(row))
        slots_of[tam][None] += 1
    slots_of = {tam: [s for s in SLOTS if 2 * slots_of[tam][s] >= slots_of[tam][None]
                      and (tam, s) != ("imperative", "1sg")] for tam in TAMS}
    # Person endings: what follows a row's shared front, and only if its lect
    # uses it for that person in at least two tenses.
    person_tenses: dict = defaultdict(set)
    for (_theme, tam, lect, _cls), row in rows.items():
        if len(row) < 4:
            continue
        for slot, p in cut(row)[1].items():
            if p is not None:
                person_tenses[(slot, p, lect)].add(tam)
    person = {s: defaultdict(set) for s in SLOTS}
    for (slot, p, lect), tenses in person_tenses.items():
        if len(tenses) >= 2:
            person[slot][p].add(lect)
    barred: dict = {s: {} for s in SLOTS}
    for s in SLOTS:
        for p, lects in person[s].items():
            elsewhere = sum(len(person[o].get(p, ())) for o in SLOTS if o != s)
            if elsewhere >= FALSE_FRIEND * len(lects):
                barred[s][p] = (elsewhere, len(lects))
    for s in SLOTS:
        for p in barred[s]:
            del person[s][p]
    # Pairs of cells that more than half the daughters' rows having both have alike.
    same: Counter = Counter()
    both: Counter = Counter()
    for row in accented.values():
        for k1, k2 in combinations(sorted(row), 2):
            both[(k1, k2)] += 1
            same[(k1, k2)] += row[k1] == row[k2]
    allowed = {frozenset(k): (same[k], both[k]) for k in both if 2 * same[k] > both[k]}
    # The cells: every form a daughter has for it, legal, with its lects.
    cells: dict = {}
    for name in NAMES:
        for tam in TAMS:
            for slot in slots_of[tam]:
                forms: dict = defaultdict(set)
                if name in THEMES:
                    for ending, sources in regular.get(name, {}).get(tam, {}).get(slot, {}).items():
                        w = norm(ending)
                        lects = {lect for lect, _c, n in sources if n >= vec.THIN}
                        if w is not None and lects and all(legal(st + w) for st in CHECK_STEMS[name]):
                            forms[w] |= lects
                else:
                    for form, lects in named.get(name, {}).get(tam, {}).get(slot, {}).items():
                        w = norm(form)
                        if w and legal(w):
                            forms[w] |= set(lects)
                if forms:
                    cells[(name, tam, slot)] = dict(forms)
    return {"cells": cells, "person": person, "barred": barred, "allowed": allowed,
            "slots_of": slots_of, "named": named}


# ---------------------------------------------------------------------------
# The model
# ---------------------------------------------------------------------------

class Build:
    def __init__(self, data: dict, budget: int) -> None:
        self.data = data
        self.budget = budget
        self.cells = data["cells"]
        self.allowed = data["allowed"]
        self.agree_tams = {t for t in TAMS if frozenset({(t, "1sg"), (t, "3sg")}) in self.allowed}

    def may_agree(self, k1, k2) -> bool:
        return frozenset({k1[1:], k2[1:]}) in self.allowed

    def person_slots(self, tam: str, slot: str) -> list[str]:
        """A 1sg may take the 3sg's ending where the two may agree."""
        return [slot, "3sg"] if slot == "1sg" and tam in self.agree_tams else [slot]

    def solve(self, seconds: float) -> dict | None:
        cells, person = self.cells, self.data["person"]
        m = cp_model.CpModel()
        q = {(s, p): m.NewBoolVar(f"p{s}{p}") for s in SLOTS for p in person[s]}
        for s in SLOTS:
            m.AddExactlyOne(q[(s, p)] for p in person[s])
        for p in {p for s in SLOTS for p in person[s]}:
            m.AddAtMostOne(q[(s, p)] for s in SLOTS if p in person[s])
        x = {(k, w): m.NewBoolVar("") for k, forms in cells.items() for w in forms}
        for k, forms in cells.items():
            m.AddExactlyOne(x[(k, w)] for w in forms)
        # Base + person ending: y says this form is that, for this base.
        z: dict = {}
        y: dict = defaultdict(list)
        for k, forms in cells.items():
            name, tam, slot = k
            for w in forms:
                for i in range(len(w) + 1):
                    base, p = w[:i], w[i:]
                    for ps in self.person_slots(tam, slot):
                        if p in person[ps]:
                            zb = z.setdefault((name, tam, base), m.NewBoolVar(""))
                            v = m.NewBoolVar("")
                            m.AddImplication(v, zb)
                            m.AddImplication(v, q[(ps, p)])
                            m.AddImplication(v, x[(k, w)])
                            y[(k, w)].append(v)
        by_tense: dict = defaultdict(list)
        for (name, tam, _b), v in z.items():
            by_tense[(name, tam)].append(v)
        for vs in by_tense.values():
            m.AddExactlyOne(vs)
        used: dict = {}
        for (name, tam, base), v in z.items():
            u = used.setdefault((name, base), m.NewBoolVar(""))
            m.AddImplication(v, u)
        own = {}
        for (k, w), xv in x.items():
            e = m.NewBoolVar("")
            m.Add(e >= xv - sum(y[(k, w)]))
            own[(k, w)] = e
        # Rules
        by_name: dict = defaultdict(list)
        for k in cells:
            by_name[k[0]].append(k)
        alike: dict = defaultdict(list)
        for name, ks in by_name.items():
            for k1, k2 in combinations(ks, 2):
                shared = cells[k1].keys() & cells[k2].keys()
                if not shared or self.may_agree(k1, k2):
                    continue
                forbidden = k1[1] == k2[1] or any(
                    k[2] == "1sg" and is_subjunctive(k[1]) for k in (k1, k2))
                for w in shared:
                    if forbidden:
                        m.AddBoolOr([x[(k1, w)].Not(), x[(k2, w)].Not()])
                    else:
                        a = m.NewBoolVar("")
                        m.AddBoolOr([x[(k1, w)].Not(), x[(k2, w)].Not(), a])
                        alike[name].append(a)
        for vs in alike.values():
            m.Add(sum(vs) <= self.budget)
        for v1, v2 in combinations(IRREGULAR, 2):
            for k1 in by_name[v1]:
                k2 = (v2, *k1[1:])
                for w in cells[k1].keys() & cells.get(k2, {}).keys():
                    m.AddBoolOr([x[(k1, w)].Not(), x[(k2, w)].Not()])
        # Objective
        terms = [PIECE * len(p) * v for (s, p), v in q.items()]
        terms += [PIECE * len(base) * u for (_n, base), u in used.items() if base]
        for (k, w), xv in x.items():
            terms.append(PIECE * (len(w) + 1) * own[(k, w)])
            terms.append((FORM * len(w) - LECT * len(cells[k][w])) * xv)
        m.Minimize(sum(terms))
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = seconds
        solver.parameters.num_workers = 8
        solver.parameters.random_seed = 0
        started = time.time()
        status = solver.Solve(m)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None
        return {
            "status": solver.StatusName(status),
            "seconds": time.time() - started,
            "pieces": round(solver.ObjectiveValue()) // PIECE,
            "bound": round(solver.BestObjectiveBound()) // PIECE,
            "endings": {s: p for (s, p), v in q.items() if solver.Value(v)},
            "bases": {(n, t): b for (n, t, b), v in z.items() if solver.Value(v)},
            "forms": {k: next(w for w in forms if solver.Value(x[(k, w)])) for k, forms in cells.items()},
            "own": {k: bool(solver.Value(own[(k, w)])) for (k, w), xv in x.items() if solver.Value(xv)},
        }

    # Checks, on the result alone --------------------------------------------

    def paradigm(self, sol: dict, name: str) -> dict:
        return {k[1:]: w for k, w in sol["forms"].items() if k[0] == name}

    def extra_alike(self, forms: dict) -> int:
        groups = defaultdict(list)
        for k, w in forms.items():
            groups[w].append(k)
        return sum(1 for ks in groups.values() for a, b in combinations(ks, 2)
                   if frozenset({a, b}) not in self.allowed)

    def checks(self, sol: dict) -> list[tuple[str, bool]]:
        forms = sol["forms"]
        attested = all(w in self.cells[k] for k, w in forms.items())
        legal_all = all(
            all(legal(st + w) for st in CHECK_STEMS[k[0]]) if k[0] in THEMES else legal(w)
            for k, w in forms.items())
        apart = all(
            forms[a] != forms[b] or self.may_agree(a, b)
            for a, b in combinations(forms, 2) if a[:2] == b[:2])
        subj = all(
            forms[a] != forms[b]
            for a in forms if a[2] == "1sg" and is_subjunctive(a[1])
            for b in forms if b[0] == a[0] and b[1] != a[1] and not self.may_agree(a, b))
        budget = all(self.extra_alike(self.paradigm(sol, n)) <= self.budget for n in NAMES)
        aux = all(forms[(a, *k[1:])] != forms.get((b, *k[1:]))
                  for a, b in combinations(IRREGULAR, 2) for k in forms if k[0] == a)
        endings = sol["endings"]
        persons = len(set(endings.values())) == 6 and all(
            e in self.data["person"][s] for s, e in endings.items())
        base = all(
            sol["own"][k] or any(w == sol["bases"].get(k[:2], "") + endings[ps]
                                 for ps in self.person_slots(k[1], k[2]))
            for k, w in forms.items())
        return [
            ("every form is a daughter's own form for that cell", attested),
            ("every form legal (regular endings on both test stems)", legal_all),
            ("six different person endings, none a false friend", persons),
            ("every cell not marked as an own form is base + person ending", base),
            ("the persons of every tense differ, but for 1sg and 3sg where the daughters allow", apart),
            ("no subjunctive 1sg alike with a form of another tense, but where the daughters allow", subj),
            (f"at most {self.budget} pairs alike in any paradigm beyond the daughters' own", budget),
            ("esse, stare and habere never alike", aux),
        ]


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

def piece(text: str | None) -> str:
    return "∅" if text == "" else html.escape(text or "")


def chips(lects, limit: int = 5) -> str:
    order = {lect: i for i, lect in enumerate(vec.SOURCE_LANGS)}
    lects = sorted(lects, key=lambda lect: order.get(lect, 99))
    more = f'<span class="mine">+{len(lects) - limit}</span>' if len(lects) > limit else ""
    return "".join(vec._lect(lect) for lect in lects[:limit]) + more


def manual_stare(named: dict) -> dict:
    """(tam, slot) → the user's form for stare, from verb_ending_notes.txt."""
    out = {}
    if not picks.DEFAULT_NOTES.is_file():
        return out
    for verb in picks.parse(picks.DEFAULT_NOTES):
        if picks.verb_key(verb["title"]) != "stare":
            continue
        for tam, items in verb["rows"]:
            for slot, item in zip(SLOTS, picks.place(items, "word", named.get("stare", {}).get(tam) or {})):
                if item not in (None, picks.MISSING):
                    out[(tam, slot)] = item[0]
    return out


def worded(lead: str, rest: str) -> str:
    """The word with its lead highlighted (the sample stem, or an irregular
    verb's base) and the rest in brackets."""
    return f'<span class="stem">{html.escape(lead) or "∅"}</span>[{html.escape(rest)}]'


def paradigm_table(build: Build, sol: dict, name: str, mine: dict) -> str:
    forms = build.paradigm(sol, name)
    groups: dict = defaultdict(list)
    for k, w in forms.items():
        groups[w].append(k)
    rows = []
    for tam in TAMS:
        if not any((tam, s) in forms for s in SLOTS):
            if name in THEMES:
                rows.append((tam, ['<td class="na"><span class="none">no daughter has it</span></td>'] * 6))
            continue
        base = sol["bases"].get((name, tam))
        tds = []
        for slot in SLOTS:
            k = (name, tam, slot)
            if (tam, slot) not in forms:
                tds.append('<td class="na"><span class="none">n/a</span></td>')
                continue
            w = forms[(tam, slot)]
            own = sol["own"][k]
            if name in THEMES:
                word = worded(SAMPLE_STEM[name], w)
            elif not own and base is not None and w.startswith(base):
                word = worded(base, w[len(base):])
            else:
                word = html.escape(w)
            parts = [f'<div class="pick">{word}</div>', f'<div class="src">{chips(build.cells[k][w], 4)}</div>']
            if own:
                parts.append('<div class="src"><span class="flag var">own form</span></div>')
            others = [o for o in groups[w] if o != (tam, slot)]
            if others:
                parts.append('<div class="mine">alike: ' + ", ".join(
                    f"{picks.SHORT[t]} {s}" + (" (daughters')" if build.may_agree((name, tam, slot), (name, t, s))
                                               else "")
                    for t, s in others) + "</div>")
            if (tam, slot) in mine:
                theirs = mine[(tam, slot)]
                parts.append(f'<div class="mine">yours: {html.escape(theirs)}'
                             f'{" ✓" if norm(theirs) == w else ""}</div>')
            tds.append(f'<td{" class=alike" if others else ""}>{"".join(parts)}</td>')
        rows.append((tam, tds))
    return picks.table(rows)


def render(build: Build, sol: dict) -> str:
    data, endings = build.data, sol["endings"]
    forms = sol["forms"]
    n_forms = len(forms)
    n_own = sum(sol["own"].values())
    letters = sum(len(w) for w in forms.values())
    persons = "".join(
        f'<tr><th scope="row">{s}</th><td><span class="pick">{piece(endings[s])}</span></td>'
        f'<td>{chips(data["person"][s].get(endings[s], ()))}</td></tr>'
        for s in SLOTS)
    barred = "; ".join(
        f'{s} <span class="pick">{piece(e)}</span> (other persons {n_other}, {s} {n_own_})'
        for s in SLOTS
        for e, (n_other, n_own_) in sorted(data["barred"][s].items(), key=lambda kv: (len(kv[0]), kv[0]))
    ) or "none"
    base_rows = []
    for tam in TAMS:
        tds = []
        for name in NAMES:
            b = sol["bases"].get((name, tam))
            own = sum(1 for k, v in sol["own"].items() if k[:2] == (name, tam) and v)
            total = sum(1 for k in forms if k[:2] == (name, tam))
            if b is None and not total:
                tds.append('<td><span class="none">—</span></td>')
                continue
            tds.append(f'<td><span class="pick">{piece(b)}</span>'
                       + (f'<div class="mine">{own} own</div>' if own else "") + "</td>")
        base_rows.append(f'<tr><th scope="row">{tam.replace(".", " · ")}</th>{"".join(tds)}</tr>')
    agree = "; ".join(
        f"{picks.SHORT[a[0]]} {a[1]} = {picks.SHORT[b[0]]} {b[1]} ({s} of {n})"
        for pair, (s, n) in sorted(build.allowed.items(), key=lambda kv: sorted(kv[0]))
        for a, b in [sorted(pair)] if ("imperative", "1sg") not in pair)
    mine = manual_stare(data["named"])
    sections = []
    for name in NAMES:
        title = vec.THEME_TITLE.get(name) or vec.NAMED_TITLE[name]
        para = build.paradigm(sol, name)
        own = sum(1 for k, v in sol["own"].items() if k[0] == name and v)
        note = (f"Shown on the sample stem <i>{SAMPLE_STEM[name]}</i> (highlighted), the daughters' ending in "
                "brackets." if name in THEMES else
                "Where a form is base + person ending, the base is highlighted and the ending is in brackets.")
        extra = ""
        if name == "stare" and mine:
            same = sum(1 for k, form in mine.items() if k in para and norm(form) == para[k])
            extra = f" {same} of your {len(mine)} stare forms are the same as the build's."
        sections.append(
            f'<section class="verb"><h2>{html.escape(title)}</h2>'
            f'<p class="tally">{len(para)} forms, {own} own forms, {build.extra_alike(para)} pairs alike beyond '
            f"the daughters' own (at most {build.budget}). {note}{extra}</p>"
            + paradigm_table(build, sol, name, mine if name == "stare" else {})
            + "</section>")
    checks = "".join(f'<li>{"✓" if ok else "✗"} {html.escape(label)}</li>' for label, ok in build.checks(sol))
    proof = ("proven optimal" if sol["status"] == "OPTIMAL" else
             f"the best found in {sol['seconds']:.0f} s; no system can cost less than {sol['bound']:,} letters of "
             "pieces")
    return PAGE.format(
        style=picks.STYLE + EXTRA_STYLE,
        budget=build.budget,
        thin=vec.THIN,
        agree=agree,
        pieces=f"{sol['pieces']:,}",
        proof=proof,
        seconds=f"{sol['seconds']:.0f}",
        own=n_own,
        regular=n_forms - n_own,
        cells=n_forms,
        mean=f"{letters / n_forms:.2f}",
        checks=checks,
        persons=persons,
        barred=barred,
        name_head="".join(f"<th>{html.escape(vec.THEME_TITLE.get(n) or n)}</th>" for n in NAMES),
        bases="".join(base_rows),
        sections="".join(sections),
    )


EXTRA_STYLE = """
.stem { background: var(--line); border-radius: 3px; padding: 0 2px; font-weight: 400; }
table.pieces { width: 100%; border-collapse: collapse; }
table.pieces th, table.pieces td { padding: 6px 8px; border-bottom: 1px solid var(--line); text-align: left;
  vertical-align: top; }
table.pieces thead th { color: var(--muted); font-size: .8rem; font-weight: 600; }
table.pieces tbody th { color: var(--ink); font-weight: 600; white-space: nowrap; text-transform: capitalize; }
table.pieces tr:last-child th, table.pieces tr:last-child td { border-bottom: 0; }
ul.facts { margin: 6px 0; padding-left: 20px; }
ul.facts li { margin: 3px 0; }
ol.rules { margin: 6px 0; padding-left: 22px; }
ol.rules li { margin: 3px 0; }
"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pure AI Build</title>
<style>{style}</style>
</head>
<body>
<main>
<h1>Verb system, built by rule</h1>
<p class="lede">The counterpart to the hand picks in <code>verb_picks.html</code>. Nothing here is picked
by hand, and no usage counts are used. Rebuild with
<code>.venv/bin/python3 scripts/build_pure_ai_verbs.py</code>.</p>

<h2>The rules</h2>
<ol class="rules">
<li><b>Only the daughters' own forms.</b> Every cell is a form some daughter has for that very cell: for the
four regular themes, an ending after the stem that the lect uses on at least {thin} verbs of the class; for
esse, stare and habere, the whole word. Nothing is cut and glued: no form is new. Letters are compared without
accents.</li>
<li><b>Legal.</b> Every form passes the spec's syllable rules; a regular ending is checked on a stem ending in
one consonant and on one ending in two (<i>kant-</i>, <i>lav-</i>; <i>tem-</i>, <i>respond-</i>; …).</li>
<li><b>Base plus variation.</b> Six person endings serve every tense and every verb. Each tense of each verb has
one base: a theme marker, or an irregular verb's stem. A cell that is not its base + its person ending is the
verb's <span class="flag var">own form</span>, a variation asset. A person ending must be one its lect uses
for that person in at least two tenses, and never a false friend: an ending the daughters give the other
persons, together, at least twice as often.</li>
<li><b>Unique, with minor overloading.</b> The persons of a tense differ. Two cells may be alike where more than
half of the daughters' rows that have both have them alike: {agree}. A subjunctive 1sg is never alike with a
form of another tense, but where the daughters allow it. Beyond that, at most {budget} pairs of forms in a
paradigm may be alike. Esse, stare and habere never share a form.</li>
<li><b>Minimal.</b> Of what passes, the system whose distinct pieces have the fewest letters: the six person
endings, each base once, and each own form whole plus one. Then the fewest letters over all the forms; then
the forms more daughters have.</li>
</ol>

<h2>Result</h2>
<ul class="facts">
<li><b>{pieces}</b> letters of pieces: {proof} (CP-SAT, {seconds} s).</li>
<li><b>{regular}</b> of the {cells} cells are base + person ending; <b>{own}</b> are own forms.</li>
<li><b>{mean}</b> letters per form on average (after the stem, for the regular themes).</li>
{checks}
</ul>

<h2>Person endings</h2>
<p class="tally">The same six in every tense and every verb.</p>
<div class="wrap"><table class="pieces"><thead><tr><th>Person</th><th>Ending</th><th>Attested in</th></tr></thead>
<tbody>{persons}</tbody></table></div>
<p class="tally">Barred as false friends (lects that give the ending to the other persons, against those that
give it to this one): {barred}.</p>

<h2>Bases, by tense</h2>
<p class="tally">The theme marker or the irregular stem each tense is built on, and how many of its cells are
own forms instead.</p>
<div class="wrap"><table class="pieces"><thead><tr><th>Tense</th>{name_head}</tr></thead>
<tbody>{bases}</tbody></table></div>

{sections}
</main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--budget", type=int, default=BUDGET)
    parser.add_argument("--seconds", type=float, default=300.0, help="time limit for the solver")
    args = parser.parse_args()

    build = Build(harvest(), args.budget)
    sol = build.solve(args.seconds)
    if sol is None:
        print("no system passes the rules", file=sys.stderr)
        return 1
    args.output.write_text(render(build, sol), encoding="utf-8")
    print(f"endings {sol['endings']}")
    print(f"{sol['pieces']} letters of pieces, {sol['status'].lower()} (bound {sol['bound']}), "
          f"{sum(sol['own'].values())} own forms of {len(sol['forms'])}, {sol['seconds']:.0f} s")
    for label, ok in build.checks(sol):
        print(f"  {'ok ' if ok else 'FAIL'} {label}")
    having = Counter(lect for k, w in sol["forms"].items() for lect in build.cells[k][w])
    print("cells each lect has:", ", ".join(f"{lect} {n}" for lect, n in having.most_common(12)))
    for name in NAMES:
        print(name)
        for tam in TAMS:
            row = [sol["forms"].get((name, tam, s)) for s in SLOTS]
            if any(w is not None for w in row):
                print(f"  {picks.SHORT[tam]:>10} [{piece(sol['bases'].get((name, tam)))}] " + " ".join(
                    "-" if w is None else (w or "∅") + ("*" if sol["own"][(name, tam, s)] else "")
                    for s, w in zip(SLOTS, row)))
    print(args.output.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
