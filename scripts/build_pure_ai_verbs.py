#!/usr/bin/env python3
"""Pure AI build: the verb system chosen by rule, next to the hand picks.

Hermetic: no usage counts. Every cell is a form a daughter has for that very
cell (an ending after the stem for the four regular themes, the whole word for
esse, stare and habere), so nothing is invented. Every form is counted in
Vulgultra phonemes, read with each lect's own pronunciation: French chantent
is /ʃɑ̃t/, so its ending is no phoneme at all.

Each tense is taken whole from one daughter: its row of six persons, so a
tense never mixes lects. Over those rows the system is base plus variation.
Six person endings serve every tense and verb. Each tense of each verb has one
base, which at least half the persons of its row are built on (a theme marker,
or an irregular verb's stem). A form that is not its base + its person ending
is a variation asset: an own ending on the base, or an own form off it. The rules are hard constraints;
what passes is ranked by

1. the phonemes of the distinct pieces (the person endings, the bases, and
   each own ending or own form), plus one per variation asset;
2. then the phonemes of all the forms;
3. then the number of lects that have each form.

The whole system is one exact model, solved with OR-Tools CP-SAT; the page says
whether the result is proven optimal. Writes docs/eval/pure-ai-build.html.
Needs OR-Tools: .venv/bin/python3 -m pip install ortools
"""

from __future__ import annotations

import argparse
import html
import json
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations, islice, product
from pathlib import Path

from ortools.sat.python import cp_model

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import build_verb_picks as picks  # noqa: E402
import verb_ending_candidates as vec  # noqa: E402
from vulgultra.phonology import (  # noqa: E402
    from_orthography,
    ipa_to_vulgultra,
    is_phonotactically_legal,
    overlay_spelling_contrasts,
    repair,
    unknown_segments,
    word_to_ipa,
)

DEFAULT_OUTPUT = ROOT / "docs" / "eval" / "pure-ai-build.html"
# The lects' readings of the forms, kept between runs (data/ is not committed).
SOUNDS_CACHE = ROOT / "data" / "eval" / "pure_ai_sounds.json"
SLOTS = vec.PERSON_SLOTS
THEMES = vec.THEMES
TAMS = vec.TAMS
IRREGULAR = ("esse", "stare", "habere")
NAMES = THEMES + IRREGULAR
SAMPLE_STEM = {"a": "kant", "e": "tem", "i": "dorm", "re": "vend"}
# Every regular ending is checked on two stems, one ending in one consonant and
# one in two, so that no ending leaves a cluster bare (respond-t).
CHECK_STEMS = {"a": ("kant", "lav"), "e": ("tem", "respond"), "i": ("dorm", "fin"), "re": ("vend", "kred")}
# The stem every lect's endings are read on (see harvest).
READING_STEM = "tip"
# No false friends: a person cannot take an ending that the daughters give the
# other persons, together, at least this many times as often.
FALSE_FRIEND = 2
BUDGET = 2
# Ranks of the objective, each far above the most the next can add up to.
PIECE, FORM, LECT = 10**9, 10**5, 1


# ---------------------------------------------------------------------------
# Sounds
# ---------------------------------------------------------------------------

class Sounds:
    """A word as Vulgultra phonemes, read with its lect's own pronunciation."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.known: dict = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        self.added = 0

    def __call__(self, word: str, lect: str) -> tuple | None:
        key = f"{lect}\t{word}"
        if key not in self.known:
            try:
                phonemes = repair(overlay_spelling_contrasts(word, ipa_to_vulgultra(word_to_ipa(word, lect), lect)))
                self.known[key] = phonemes if phonemes and not unknown_segments(phonemes) else None
            except Exception:
                self.known[key] = None
            self.added += 1
        found = self.known[key]
        return None if found is None else tuple(found)

    def save(self) -> None:
        if self.added:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.known, ensure_ascii=False), encoding="utf-8")


@lru_cache(maxsize=None)
def legal(phonemes: tuple) -> bool:
    return bool(phonemes) and is_phonotactically_legal(list(phonemes))


@lru_cache(maxsize=None)
def stem_sounds(stem: str) -> tuple:
    return tuple(from_orthography(stem))


def cut(row: dict) -> tuple:
    """The longest front at least four endings of a row share, and the rest of
    each ending (None where it does not share it)."""
    ends = list(row.values())
    marker: tuple = ()
    for size in range(max(map(len, ends), default=0), 0, -1):
        top = Counter(e[:size] for e in ends if len(e) >= size).most_common(1)
        if top and top[0][1] >= 4:
            marker = top[0][0]
            break
    return marker, {s: (e[len(marker):] if e[:len(marker)] == marker else None) for s, e in row.items()}


def show(phonemes: tuple) -> str:
    return "".join(phonemes) or "∅"


# ---------------------------------------------------------------------------
# The daughters' forms
# ---------------------------------------------------------------------------

def cut_per_tense() -> set:
    """(lect, class) whose endings the harvest cut after each tense's own stem
    (Gascon future -ai, not -arai): not comparable with the others'."""
    out = set()
    for lect in vec.SOURCE_LANGS:
        path = vec.SOURCES / f"{lect}.json"
        if path.is_file():
            inventories = json.loads(path.read_text(encoding="utf-8"))["metadata"].get("ending_inventories") or {}
            out |= {(lect, cls) for cls, features in inventories.items()
                    if any(payload.get("stem_mode") == "lcp" for payload in features.values())}
    return out


def misnamed(regular: dict) -> dict:
    """(lect, class, tense) → the tense it repeats. A lect's table that repeats
    another of its tenses ending for ending (Occitan's -re preterite is its
    future, -rai, -ràs…) is kept under the tense whose other daughters share more
    of its endings, and dropped from the other. Where they share as many
    (Asturian -are is both pluperfect and subjunctive imperfect), it stays in both."""
    tables: dict = defaultdict(lambda: defaultdict(dict))
    having: dict = defaultdict(set)
    for theme, tams in regular.items():
        for tam, slots in tams.items():
            for slot, endings in slots.items():
                for ending, sources in endings.items():
                    for lect, cls, _support in sources:
                        tables[(theme, lect, cls)][tam][slot] = ending
                        having[(theme, tam, slot, ending)].add(lect)
    out = {}
    for (theme, lect, cls), tams in tables.items():
        for t1, t2 in combinations(sorted(tams), 2):
            common = [s for s in tams[t1] if s in tams[t2]]
            if len(common) < 4 or any(tams[t1][s] != tams[t2][s] for s in common):
                continue
            share = {t: sum(len(having[(theme, t, s, tams[t][s])] - {lect}) for s in common) for t in (t1, t2)}
            if share[t1] != share[t2]:
                keep, drop = sorted((t1, t2), key=share.get, reverse=True)
                out[(lect, cls, drop)] = keep
    return out


def harvest(sounds: Sounds) -> dict:
    regular, _ = vec.load_regular()
    named, _ = vec.load_named()
    per_tense = cut_per_tense()
    copies = misnamed(regular)
    # Read every ending inside a word, on the stem tip-, and take the stem's
    # phonemes off the front. Every lect spells and reads tip- alike, and no
    # ending starts with p; a word that does not start with the stem as the
    # lect reads it before a vowel (Romanian tipi is /tipʲ/) is not read.
    ending_sounds: dict = {}
    for tams in regular.values():
        for slots in tams.values():
            for endings in slots.values():
                for ending, sources in endings.items():
                    letters = unicodedata.normalize("NFC", ending.lower().strip("-"))
                    letters = "" if letters == "∅" else letters
                    for lect, cls, support in sources:
                        if support < vec.THIN or (lect, cls) in per_tense or (lect, letters) in ending_sounds:
                            continue
                        front = (sounds(READING_STEM + "a", lect) or ())[:len(READING_STEM)]
                        p = sounds(READING_STEM + letters, lect)
                        ending_sounds[(lect, letters)] = p[len(front):] if p and p[:len(front)] == front else None
    # Each lect's rows, in phonemes.
    rows: dict = defaultdict(dict)
    heard: dict = defaultdict(dict)  # (theme or verb, lect, class) → cell → phonemes
    cells: dict = defaultdict(lambda: defaultdict(lambda: {"lects": set(), "spell": set()}))
    for theme, tams in regular.items():
        for tam, slots in tams.items():
            for slot, endings in slots.items():
                for ending, sources in endings.items():
                    letters = unicodedata.normalize("NFC", ending.lower().strip("-"))
                    letters = "" if letters == "∅" else letters
                    for lect, cls, support in sources:
                        if support < vec.THIN or (lect, cls) in per_tense or (lect, cls, tam) in copies:
                            continue
                        p = ending_sounds.get((lect, letters))
                        if p is None:
                            continue
                        rows[(theme, tam, lect, cls)][slot] = p
                        heard[(theme, lect, cls)][(tam, slot)] = p
                        if all(legal(stem_sounds(st) + p) for st in CHECK_STEMS[theme]):
                            cell = cells[(theme, tam, slot)][p]
                            cell["lects"].add(lect)
                            cell["spell"].add("-" + letters if letters else "∅")
    # Which persons a tense has: those in at least half the daughters' rows.
    # No Romance imperative has a first person singular, whatever the tables fill in.
    count: dict = defaultdict(Counter)
    for (_theme, tam, _lect, _cls), row in rows.items():
        count[tam].update(list(row))
        count[tam][None] += 1
    slots_of = {tam: [s for s in SLOTS if 2 * count[tam][s] >= count[tam][None]
                      and (tam, s) != ("imperative", "1sg")] for tam in TAMS}
    # Each tense is taken whole from one daughter: its row, every person there
    # and legal. Lects with the same row in phonemes share it.
    whole: dict = defaultdict(lambda: defaultdict(set))
    for (theme, tam, lect, _cls), row in rows.items():
        need = slots_of[tam]
        if all(s in row and all(legal(stem_sounds(st) + row[s]) for st in CHECK_STEMS[theme]) for s in need):
            whole[(theme, tam)][tuple(row[s] for s in need)].add(lect)
    for verb in IRREGULAR:
        for tam, slots in named.get(verb, {}).items():
            by_lect: dict = defaultdict(lambda: defaultdict(list))
            for slot, forms in slots.items():
                for form, lects in forms.items():
                    for lect in lects:
                        p = sounds(unicodedata.normalize("NFC", form.lower()), lect)
                        if p:
                            heard[(verb, lect, "")].setdefault((tam, slot), p)
                        if p and legal(p):
                            cell = cells[(verb, tam, slot)][p]
                            cell["lects"].add(lect)
                            cell["spell"].add(form)
                            if p not in by_lect[lect][slot]:
                                by_lect[lect][slot].append(p)
            need = slots_of.get(tam, [])
            for lect, own in by_lect.items():
                if need and all(own.get(s) for s in need):
                    for row in islice(product(*(own[s] for s in need)), 8):
                        whole[(verb, tam)][row].add(lect)
    cells = {k: dict(v) for k, v in cells.items() if k[1] in slots_of and k[2] in slots_of[k[1]] and v}
    # Person endings: what follows a row's shared front, and only if its lect
    # uses it for that person in at least two tenses.
    person_tenses: dict = defaultdict(set)
    for (_theme, tam, lect, _cls), row in rows.items():
        if len(row) >= 4:
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
    # For each theme and verb, the pairs of cells that more than half of its
    # own rows having both have alike, in phonemes (French -ais and -ait are
    # both /ɛ/).
    same: Counter = Counter()
    both: Counter = Counter()
    for (name, _lect, _cls), row in heard.items():
        for k1, k2 in combinations(sorted(row), 2):
            both[(name, k1, k2)] += 1
            same[(name, k1, k2)] += row[k1] == row[k2]
    allowed: dict = defaultdict(dict)
    for (name, k1, k2), n in both.items():
        if 2 * same[(name, k1, k2)] > n:
            allowed[name][frozenset({k1, k2})] = (same[(name, k1, k2)], n)
    sounds.save()
    return {"cells": cells, "rows": {key: dict(by) for key, by in whole.items()}, "person": person,
            "barred": barred, "allowed": allowed, "slots_of": slots_of, "named": named,
            "per_tense": sorted(per_tense), "copies": copies}


# ---------------------------------------------------------------------------
# The model
# ---------------------------------------------------------------------------

class Build:
    def __init__(self, data: dict, budget: int) -> None:
        self.data = data
        self.budget = budget
        self.budgets = {name: budget for name in NAMES}
        self.cells = data["cells"]
        self.rows = {key: by for key, by in data["rows"].items() if by}
        self.allowed = data["allowed"]
        self.agree_tams = {name: {t for t in TAMS if frozenset({(t, "1sg"), (t, "3sg")}) in self.allowed[name]}
                           for name in NAMES}
        self.tenses = {key: [(*key, s) for s in data["slots_of"][key[1]]] for key in self.rows}
        # The forms a cell can take: those of the rows its tense can take.
        self.forms: dict = defaultdict(set)
        for key, by in self.rows.items():
            for row in by:
                for k, w in zip(self.tenses[key], row):
                    self.forms[k].add(w)
        self.bases = {key: self.base_options(key) for key in self.rows}

    def base_options(self, key) -> list[tuple]:
        """What at least half the persons of one of the tense's rows are built
        on. An irregular verb's base is never empty: it is the verb's stem for
        that tense."""
        found = set()
        for row in self.rows[key]:
            on: Counter = Counter()
            for w in row:
                on.update({w[:i] for i in range(len(w) + 1)})
            found |= {b for b, n in on.items() if 2 * n >= len(row)}
        if key[0] not in THEMES and found - {()}:
            found.discard(())
        return sorted(found)

    def may_agree(self, k1, k2) -> bool:
        """Two cells of one paradigm may be alike where most of its daughters'
        rows have them alike."""
        return k1[0] == k2[0] and frozenset({k1[1:], k2[1:]}) in self.allowed[k1[0]]

    def person_slots(self, name: str, tam: str, slot: str) -> list[str]:
        """A 1sg may take the 3sg's ending where the two may agree."""
        return [slot, "3sg"] if slot == "1sg" and tam in self.agree_tams[name] else [slot]

    def least_budgets(self, seconds: float = 60.0) -> None:
        """A paradigm that no choice of rows keeps within the budget gets the
        fewest pairs alike it can manage. The irregular verbs go together,
        since they must differ from one another."""
        for group in [[t] for t in THEMES] + [list(IRREGULAR)]:
            part = Build({**self.data, "rows": {k: v for k, v in self.data["rows"].items() if k[0] in group}},
                         self.budget)
            while part.solve(seconds) is None and part.budgets[group[0]] < 6 * len(TAMS):
                for name in group:
                    part.budgets[name] += 1
            for name in group:
                self.budgets[name] = part.budgets[name]

    def solve(self, seconds: float) -> dict | None:
        cells, person = self.forms, self.data["person"]
        m = cp_model.CpModel()
        q = {(s, p): m.NewBoolVar("") for s in SLOTS for p in person[s]}
        for s in SLOTS:
            m.AddExactlyOne(q[(s, p)] for p in person[s])
        for p in {p for s in SLOTS for p in person[s]}:
            m.AddAtMostOne(q[(s, p)] for s in SLOTS if p in person[s])
        # One daughter's row per tense; a cell's form is that row's.
        y = {(key, row): m.NewBoolVar("") for key, by in self.rows.items() for row in by}
        for key, by in self.rows.items():
            m.AddExactlyOne(y[(key, row)] for row in by)
        x = {(k, w): m.NewBoolVar("") for k, forms in cells.items() for w in forms}
        for key, by in self.rows.items():
            for i, k in enumerate(self.tenses[key]):
                for w in cells[k]:
                    m.Add(x[(k, w)] == sum(y[(key, row)] for row in by if row[i] == w))
        z = {(key, b): m.NewBoolVar("") for key, bs in self.bases.items() for b in bs}
        for key, bs in self.bases.items():
            m.AddExactlyOne(z[(key, b)] for b in bs)
        used: dict = {}
        for (key, b), v in z.items():
            if b:
                m.AddImplication(v, used.setdefault((key[0], b), m.NewBoolVar("")))
        # c: this cell takes this form with this base, on it or off it; r: and
        # it is base + its person ending.
        cost = []
        self._c = {}
        for key, ks in self.tenses.items():
            for k in ks:
                options = []
                for b in self.bases[key]:
                    for w in cells[k]:
                        c = m.NewBoolVar("")
                        m.AddImplication(c, x[(k, w)])
                        m.AddImplication(c, z[(key, b)])
                        options.append(c)
                        if w[:len(b)] != b:
                            cost.append(PIECE * (len(w) + 1) * c)
                            self._c[(k, w, b)] = (c, "off", [])
                            continue
                        ending = w[len(b):]
                        rs = []
                        for ps in self.person_slots(*k):
                            if ending in person[ps]:
                                r = m.NewBoolVar("")
                                m.AddImplication(r, c)
                                m.AddImplication(r, q[(ps, ending)])
                                rs.append(r)
                        if rs:
                            m.AddAtMostOne(rs)
                        cost.append(PIECE * (len(ending) + 1) * (c - sum(rs)))
                        self._c[(k, w, b)] = (c, "on", rs)
                m.AddExactlyOne(options)
        # Rules
        by_name: dict = defaultdict(list)
        for k in cells:
            by_name[k[0]].append(k)
        alike: dict = defaultdict(list)
        for name, ks in by_name.items():
            for k1, k2 in combinations(ks, 2):
                shared = cells[k1] & cells[k2]
                if not shared or self.may_agree(k1, k2):
                    continue
                for w in shared:
                    if k1[1] == k2[1]:
                        m.AddBoolOr([x[(k1, w)].Not(), x[(k2, w)].Not()])
                    else:
                        a = m.NewBoolVar("")
                        m.AddBoolOr([x[(k1, w)].Not(), x[(k2, w)].Not(), a])
                        alike[name].append(a)
        for name, vs in alike.items():
            m.Add(sum(vs) <= self.budgets[name])
        for v1, v2 in combinations(IRREGULAR, 2):
            for k1 in by_name[v1]:
                k2 = (v2, *k1[1:])
                for w in cells[k1] & cells.get(k2, set()):
                    m.AddBoolOr([x[(k1, w)].Not(), x[(k2, w)].Not()])
        # Objective
        cost += [PIECE * len(p) * v for (s, p), v in q.items()]
        cost += [PIECE * len(b) * u for (_n, b), u in used.items()]
        cost += [(FORM * len(w) - LECT * len(self.cells[k][w]["lects"])) * v for (k, w), v in x.items()]
        m.Minimize(sum(cost))
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = seconds
        solver.parameters.num_workers = 8
        solver.parameters.random_seed = 0
        started = time.time()
        status = solver.Solve(m)
        self.status = solver.StatusName(status)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None
        kind = {}
        for (k, w, b), (c, where, rs) in self._c.items():
            if solver.Value(c):
                kind[k] = "off" if where == "off" else ("base" if any(solver.Value(r) for r in rs) else "own")
        return {
            "status": solver.StatusName(status),
            "seconds": time.time() - started,
            "pieces": round(solver.ObjectiveValue()) // PIECE,
            "bound": round(solver.BestObjectiveBound()) // PIECE,
            "endings": {s: p for (s, p), v in q.items() if solver.Value(v)},
            "bases": {key: b for (key, b), v in z.items() if solver.Value(v)},
            "forms": {k: next(w for w in forms if solver.Value(x[(k, w)])) for k, forms in cells.items()},
            "row": {key: self.rows[key][row] for (key, row), v in y.items() if solver.Value(v)},
            "kind": kind,
        }

    # Checks, on the result alone --------------------------------------------

    def paradigm(self, sol: dict, name: str) -> dict:
        return {k[1:]: w for k, w in sol["forms"].items() if k[0] == name}

    def extra_alike(self, name: str, forms: dict) -> int:
        groups = defaultdict(list)
        for k, w in forms.items():
            groups[w].append(k)
        return sum(1 for ks in groups.values() for a, b in combinations(ks, 2)
                   if frozenset({a, b}) not in self.allowed[name])

    def checks(self, sol: dict) -> list[tuple[str, bool]]:
        forms, bases, endings = sol["forms"], sol["bases"], sol["endings"]
        attested = all(w in self.cells[k] for k, w in forms.items())
        legal_all = all(
            all(legal(stem_sounds(st) + w) for st in CHECK_STEMS[k[0]]) if k[0] in THEMES else legal(w)
            for k, w in forms.items())
        apart = all(forms[a] != forms[b] or self.may_agree(a, b)
                    for a, b in combinations(forms, 2) if a[:2] == b[:2])
        budget = all(self.extra_alike(n, self.paradigm(sol, n)) <= self.budgets[n] for n in NAMES)
        aux = all(forms[(a, *k[1:])] != forms.get((b, *k[1:]))
                  for a, b in combinations(IRREGULAR, 2) for k in forms if k[0] == a)
        persons = len(set(endings.values())) == 6 and all(e in self.data["person"][s] for s, e in endings.items())
        whole = all(tuple(forms[k] for k in ks) in self.rows[key] for key, ks in self.tenses.items())
        regular = all(
            sol["kind"][k] != "base" or any(w == bases[k[:2]] + endings[ps] for ps in self.person_slots(*k))
            for k, w in forms.items())
        return [
            ("every form is a daughter's own form for that cell", attested),
            ("every form legal (regular endings on both test stems)", legal_all),
            ("six different person endings, none a false friend", persons),
            ("every tense is one daughter's own row", whole),
            ("every form marked regular is base + person ending", regular),
            ("the persons of every tense differ, but for 1sg and 3sg where the daughters allow", apart),
            (f"at most {self.budget} pairs alike in any paradigm beyond the daughters' own, or the fewest it "
             "can manage", budget),
            ("esse, stare and habere never alike", aux),
        ]


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

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


def worded(lead: tuple, rest: tuple) -> str:
    """The word in phonemes, its lead highlighted (the sample stem, or an
    irregular verb's base) and the rest in brackets."""
    return f'<span class="stem">{html.escape(show(lead))}</span>[{html.escape("".join(rest))}]'


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
        base = sol["bases"].get((name, tam), ())
        tds = []
        for slot in SLOTS:
            k = (name, tam, slot)
            if (tam, slot) not in forms:
                tds.append('<td class="na"><span class="none">n/a</span></td>')
                continue
            w = forms[(tam, slot)]
            kind = sol["kind"][k]
            if name in THEMES:
                word = worded(stem_sounds(SAMPLE_STEM[name]), w)
            elif kind != "off":
                word = worded(base, w[len(base):])
            else:
                word = html.escape(show(w))
            info = build.cells[k][w]
            spell = ", ".join(f"‹{html.escape(s)}›" for s in sorted(info["spell"], key=len)[:2])
            parts = [f'<div class="pick">{word}</div>', f'<div class="src">{chips(info["lects"], 4)}</div>',
                     f'<div class="mine">{spell}</div>']
            if kind == "own":
                parts.append('<div class="src"><span class="flag var">own ending</span></div>')
            elif kind == "off":
                parts.append('<div class="src"><span class="flag var">own form</span></div>')
            others = [o for o in groups[w] if o != (tam, slot)]
            if others:
                parts.append('<div class="mine">alike: ' + ", ".join(
                    f"{picks.SHORT[t]} {s}" + (" (daughters')" if build.may_agree(k, (name, t, s)) else "")
                    for t, s in others) + "</div>")
            if (tam, slot) in mine:
                theirs = mine[(tam, slot)]
                parts.append(f'<div class="mine">yours: {html.escape(theirs)}</div>')
            tds.append(f'<td{" class=alike" if others else ""}>{"".join(parts)}</td>')
        rows.append((tam, tds))
    return picks.table(rows)


def agree(build: Build, name: str) -> str:
    return "; ".join(
        f"{picks.SHORT[a[0]]} {a[1]} = {picks.SHORT[b[0]]} {b[1]} ({n_same} of {n})"
        for pair, (n_same, n) in sorted(build.allowed[name].items(), key=lambda kv: sorted(kv[0]))
        for a, b in [sorted(pair)] if ("imperative", "1sg") not in pair and a[1] in SLOTS)


def render(build: Build, sol: dict) -> str:
    data, endings, forms = build.data, sol["endings"], sol["forms"]
    kinds = Counter(sol["kind"].values())
    phonemes = sum(len(w) for w in forms.values())
    persons = "".join(
        f'<tr><th scope="row">{s}</th><td><span class="pick">{html.escape(show(endings[s]))}</span></td>'
        f'<td>{chips(data["person"][s].get(endings[s], ()))}</td></tr>'
        for s in SLOTS)
    barred = "; ".join(
        f'{s} <span class="pick">{html.escape(show(e))}</span> (other persons {n_other}, {s} {n_own})'
        for s in SLOTS
        for e, (n_other, n_own) in sorted(data["barred"][s].items(), key=lambda kv: (len(kv[0]), kv[0]))
    ) or "none"
    base_rows = []
    for tam in TAMS:
        tds = []
        for name in NAMES:
            if (name, tam) not in build.tenses:
                tds.append('<td><span class="none">—</span></td>')
                continue
            ks = build.tenses[(name, tam)]
            own = sum(1 for k in ks if sol["kind"][k] != "base")
            tds.append(f'<td><span class="pick">{html.escape(show(sol["bases"][(name, tam)]))}</span>'
                       + (f'<div class="mine">{own} not base + ending</div>' if own else "") + "</td>")
        base_rows.append(f'<tr><th scope="row">{tam.replace(".", " · ")}</th>{"".join(tds)}</tr>')
    mine = manual_stare(data["named"])
    sections = []
    for name in NAMES:
        title = vec.THEME_TITLE.get(name) or vec.NAMED_TITLE[name]
        para = build.paradigm(sol, name)
        n_var = sum(1 for k, v in sol["kind"].items() if k[0] == name and v != "base")
        note = (f"In phonemes, on the sample stem <i>{SAMPLE_STEM[name]}</i> (highlighted), the daughters' ending "
                "in brackets, and below it the lects that have it and how they spell it." if name in THEMES else
                "In phonemes; where a form is on its tense's base, the base is highlighted and the rest is in "
                "brackets.")
        sections.append(
            f'<section class="verb"><h2>{html.escape(title)}</h2>'
            f'<p class="tally">{len(para)} forms, {n_var} not base + person ending, '
            f"{build.extra_alike(name, para)} pairs alike beyond the daughters' own (at most {build.budgets[name]}"
            + ("" if build.budgets[name] == build.budget else
               f": no choice of the daughters' rows gets it down to {build.budget}") + "). "
            f"{note}</p>"
            + '<p class="tally">May be alike, as most of its daughters\' rows have them: ' + (agree(build, name) or "none")
            + ".</p>"
            + paradigm_table(build, sol, name, mine if name == "stare" else {})
            + '<p class="tally">Whose row each tense is: ' + "; ".join(
                f"{picks.SHORT[tam]} {chips(sol['row'][(name, tam)], 6)}"
                for tam in TAMS if (name, tam) in sol["row"]) + "</p>"
            + "</section>")
    checks = "".join(f'<li>{"✓" if ok else "✗"} {html.escape(label)}</li>' for label, ok in build.checks(sol))
    proof = ("proven optimal" if sol["status"] == "OPTIMAL" else
             f"the best found in {sol['seconds']:.0f} s; no system can cost less than {sol['bound']:,}")
    return PAGE.format(
        style=picks.STYLE + EXTRA_STYLE,
        budget=build.budget,
        thin=vec.THIN,
        per_tense=", ".join(f"{lect} {cls}" for lect, cls in data["per_tense"]) or "none",
        copies="; ".join(f"{lect} {cls} {picks.SHORT[tam]} (kept as {picks.SHORT[keep]})"
                         for (lect, cls, tam), keep in sorted(data["copies"].items())) or "none",
        pieces=f"{sol['pieces']:,}",
        proof=proof,
        seconds=f"{sol['seconds']:.0f}",
        base=kinds["base"],
        own=kinds["own"],
        off=kinds["off"],
        cells=len(forms),
        mean=f"{phonemes / len(forms):.2f}",
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
esse, stare and habere, the whole word. No form is new. A lect's table that repeats another of its tenses
ending for ending is taken to be filed under the wrong tense as well: it is kept under the tense whose other
daughters share more of its endings and dropped from the other, or kept in both where they share as many
(dropped: {copies}).</li>
<li><b>In phonemes.</b> Every form is read with its lect's own pronunciation and turned into Vulgultra
phonemes, as the roots are. A regular ending is read on the stem <i>tip-</i>, which every lect spells and
reads alike, and the stem's phonemes are taken off: French <i>tipent</i> is /tip/, so its ending is no
phoneme at all. Forms are compared, counted and checked as phonemes.</li>
<li><b>Legal.</b> Every form passes the spec's syllable rules; a regular ending is checked on a stem ending in
one consonant and on one ending in two (<i>kant-</i>, <i>lav-</i>; <i>tem-</i>, <i>respond-</i>; …).</li>
<li><b>Each tense is one daughter's row.</b> The six persons of a tense are taken together from one lect, as
that lect has them (lects with the same row in phonemes share it), so a tense never mixes daughters. Lects whose
endings the harvest cut after each tense's own stem are left out ({per_tense}).</li>
<li><b>Base plus variation.</b> Six person endings serve every tense and every verb. Each tense of each verb has
one base, which at least half the persons of its row are built on: a theme marker (possibly none), or an
irregular verb's stem (never none). A form that is not its base + its person ending is a variation asset: an
<span class="flag var">own ending</span> on the base, or an <span class="flag var">own form</span> off it. A
person ending must be one its lect uses for that person in at least two tenses, and never a false friend: an
ending the daughters give the other persons, together, at least twice as often.</li>
<li><b>Unique, with minor overloading.</b> The persons of a tense differ. Two cells may be alike where more than
half of the theme's or verb's own rows in the daughters that have both have them alike (listed with each
paradigm). Beyond that, at most {budget} pairs of forms in a paradigm may be alike, or, where no choice of the
daughters' rows gets a paradigm down to that, the fewest it can manage. Esse, stare and habere never share a form.</li>
<li><b>Minimal.</b> Of what passes, the system whose distinct pieces have the fewest phonemes: the six person
endings, each base once, and each own ending or own form, plus one for each of those. Then the fewest phonemes
over all the forms; then the forms more daughters have.</li>
</ol>

<h2>Result</h2>
<ul class="facts">
<li><b>{pieces}</b> phonemes of pieces: {proof} (CP-SAT, {seconds} s).</li>
<li>Of the {cells} cells, <b>{base}</b> are base + person ending, <b>{own}</b> have an own ending, and
<b>{off}</b> are own forms.</li>
<li><b>{mean}</b> phonemes per form on average (after the stem, for the regular themes).</li>
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
not base + person ending.</p>
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

    started = time.time()
    build = Build(harvest(Sounds(SOUNDS_CACHE)), args.budget)
    build.least_budgets()
    print(f"harvest {time.time() - started:.0f} s, {len(build.cells)} cells, "
          f"{sum(map(len, build.cells.values()))} forms", flush=True)
    sol = build.solve(args.seconds)
    if sol is None:
        print("no system passes the rules", file=sys.stderr)
        return 1
    args.output.write_text(render(build, sol), encoding="utf-8")
    kinds = Counter(sol["kind"].values())
    print("endings", {s: show(p) for s, p in sol["endings"].items()})
    print(f"{sol['pieces']} phonemes of pieces, {sol['status'].lower()} (bound {sol['bound']}), "
          f"{kinds['base']} base + ending, {kinds['own']} own endings, {kinds['off']} own forms, "
          f"{sol['seconds']:.0f} s")
    for label, ok in build.checks(sol):
        print(f"  {'ok ' if ok else 'FAIL'} {label}")
    having = Counter(lect for k, w in sol["forms"].items() for lect in build.cells[k][w]["lects"])
    print("cells each lect has:", ", ".join(f"{lect} {n}" for lect, n in having.most_common(12)))
    mark = {"base": "", "own": "*", "off": "!"}
    for name in NAMES:
        print(name)
        for tam in TAMS:
            row = [sol["forms"].get((name, tam, s)) for s in SLOTS]
            if any(w is not None for w in row):
                print(f"  {picks.SHORT[tam]:>10} [{show(sol['bases'][(name, tam)])}] " + " ".join(
                    "-" if w is None else show(w) + mark[sol["kind"][(name, tam, s)]]
                    for s, w in zip(SLOTS, row)))
    print(args.output.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
