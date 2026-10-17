#!/usr/bin/env python3
"""Pure AI build: the verb system chosen by rule, next to the hand picks.

Hermetic: no usage counts. Every form is stem + marker(theme, tense) + person
ending, and every piece is cut from the daughters' harvested endings. The
goals, in rank order:

1. every form legal, on a stem ending in one consonant and on one ending in
   two; no person ending that the daughters give mostly to another person;
   the persons of each tense distinct; at most BUDGET pairs of forms alike in
   a paradigm; esse, stare and habere never alike;
2. as few variation assets as possible (a tense's own person ending, an
   irregular verb's second stem);
3. the shortest forms: fewest letters after the stem, every cell counted once.

For a given set of person endings, each theme's markers are found exactly (a
bounded search). The person endings themselves are found by local search from
fixed starting sets; the page says whether the starts agree. The irregular
verbs are fitted to the base afterwards. Writes docs/eval/pure-ai-build.html.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import product
from pathlib import Path

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
IRREGULAR_THEME = {"esse": "re", "stare": "a", "habere": "e"}
SAMPLE_STEM = {"a": "kant", "e": "tem", "i": "dorm", "re": "vend"}
# Every regular form is also checked on a second stem, so that each theme is
# tried with a stem ending in one consonant and with one ending in two: a
# piece that leaves -nd- or -rm- bare before a consonant fails (respond-t).
CHECK_STEMS = {"a": ("kant", "lav"), "e": ("tem", "respond"), "i": ("dorm", "fin"), "re": ("vend", "kred")}
# No false friends: a person cannot take an ending that the daughters give
# another person at least this many times as often (-s is 2sg in 17 lects and
# 1sg in 3, so it cannot be the 1sg).
FALSE_FRIEND = 2
BUDGET = 2
TIE = 1e-4  # per attesting lect: ties in length go to the better-attested pieces
# A variation asset (a marker a theme borrows from another theme for the same
# tense) costs as much as 20 letters: it is taken where it makes a tense legal or
# saves more than about three letters on each of the tense's six forms.
BORROW = 20.0
VOWELS = frozenset("aeiou")
LETTERS = {"ț": "ts", "ţ": "ts", "ș": "x", "ş": "x", "ç": "s", "ñ": "ny", "ă": "e", "ß": "ss"}


# ---------------------------------------------------------------------------
# Pieces from the harvest
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
    """Marker = the longest prefix at least four endings share; the rest of
    each ending is its person ending (None where it does not share it)."""
    ends = list(row.values())
    marker = ""
    for size in range(max(map(len, ends), default=0), 0, -1):
        top = Counter(e[:size] for e in ends if len(e) >= size).most_common(1)
        if top and top[0][1] >= 4:
            marker = top[0][0]
            break
    return marker, {s: (e[len(marker):] if e.startswith(marker) else None) for s, e in row.items()}


def harvest() -> dict:
    """Candidate pieces, each mapped to the lects that attest it."""
    regular, _ = vec.load_regular()
    named, _ = vec.load_named()
    rows: dict = defaultdict(dict)
    by_lect: dict = defaultdict(lambda: defaultdict(set))
    for theme, tams in regular.items():
        for tam, slots in tams.items():
            for slot, endings in slots.items():
                for ending, sources in endings.items():
                    e = norm(ending)
                    if e is None:
                        continue
                    for lect, cls, support in sources:
                        if support >= vec.THIN:
                            rows[(theme, tam, lect, cls)][slot] = e
                            by_lect[(lect, tam)][slot].add(e)
    marker: dict = defaultdict(lambda: defaultdict(set))
    slots_of: dict = defaultdict(Counter)
    person_tenses: dict = defaultdict(set)
    for (theme, tam, lect, _cls), row in rows.items():
        for slot in row:
            slots_of[tam][slot] += 1
        slots_of[tam][None] += 1
        if len(row) < 4:
            continue
        m, persons = cut(row)
        marker[(theme, tam)][m].add(lect)
        for slot, p in persons.items():
            if p is not None:
                person_tenses[(slot, p, lect)].add(tam)
    # A person ending must be one in its lect: the same ending for the same
    # person in at least two tenses (Emilian conditional -are-v is not).
    person = {s: defaultdict(set) for s in SLOTS}
    for (slot, p, lect), tenses in person_tenses.items():
        if len(tenses) >= 2:
            person[slot][p].add(lect)
    barred: dict = {s: {} for s in SLOTS}
    for s in SLOTS:
        for p, lects in person[s].items():
            rival = max((o for o in SLOTS if o != s), key=lambda o: len(person[o].get(p, ())))
            if len(person[rival].get(p, ())) >= FALSE_FRIEND * len(lects):
                barred[s][p] = (rival, len(person[rival][p]), len(lects))
    for s in SLOTS:
        for p in barred[s]:
            del person[s][p]
    seen: dict = defaultdict(lambda: defaultdict(set))
    for verb in IRREGULAR_THEME:
        for tam, slots in named.get(verb, {}).items():
            for slot, forms in slots.items():
                for form, lects in forms.items():
                    f = norm(form)
                    if not f:
                        continue
                    for lect in lects:
                        for e in by_lect.get((lect, tam), {}).get(slot, ()):
                            if f.endswith(e):
                                seen[verb][f[: len(f) - len(e)]].add((lect, tam))
    # A stem must recur: in two lects, or in two tenses of one.
    stems = {
        verb: {s: {lect for lect, _t in where} for s, where in by.items() if len(where) >= 2}
        for verb, by in seen.items()
    }
    return {
        "person": person, "barred": barred, "marker": marker, "stems": stems, "named": named,
        # A person a tense has in at least half the daughters' rows. No Romance
        # imperative has a first person singular, whatever the tables fill in.
        "slots_of": {
            tam: [s for s in SLOTS if 2 * slots_of[tam][s] >= slots_of[tam][None]
                  and (tam, s) != ("imperative", "1sg")]
            for tam in TAMS
        },
    }


def ranked(pool: dict) -> list[str]:
    return sorted(pool, key=lambda p: (len(p), -len(pool[p]), p))


# ---------------------------------------------------------------------------
# Forms
# ---------------------------------------------------------------------------

def join(left: str, right: str) -> str:
    """Where two pieces meet vowel to vowel, the first one's vowel drops."""
    if left and right and left[-1] in VOWELS and right[0] in VOWELS:
        left = left[:-1]
    return left + right


@lru_cache(maxsize=None)
def compose(stem: str, marker: str, ending: str) -> str:
    return join(join(stem, marker), ending)


@lru_cache(maxsize=None)
def legal(form: str) -> bool:
    if not form:
        return False
    try:
        return is_phonotactically_legal(from_orthography(form))
    except Exception:
        return False


def alike_pairs(forms) -> int:
    return sum(n * (n - 1) // 2 for n in Counter(forms).values())


# ---------------------------------------------------------------------------
# The search
# ---------------------------------------------------------------------------

class System:
    def __init__(self, pools: dict, budget: int) -> None:
        self.pools = pools
        self.budget = budget
        self.slots_of = pools["slots_of"]
        # Every theme needs every tense; where its own rows give no marker, it
        # can only borrow one.
        self.markers = {(t, tam): ranked(pools["marker"].get((t, tam), {})) for t in THEMES for tam in TAMS}
        self.tams_of = {t: list(TAMS) for t in THEMES}
        # Markers a theme may borrow: another theme's, for the same tense.
        self.borrowable = {
            (t, tam): [m for m in ranked(self.lects_of_marker(tam)) if m not in self.markers[(t, tam)]]
            for (t, tam) in self.markers
        }
        self.tried = 0
        self._themes: dict = {}

    def lects_of_marker(self, tam: str) -> dict[str, set[str]]:
        """marker → lects, over every theme's rows for this tense."""
        out: dict = defaultdict(set)
        for t in THEMES:
            for m, lects in self.pools["marker"].get((t, tam), {}).items():
                out[m] |= lects
        return out

    def marker_lects(self, theme: str, tam: str, m: str) -> set[str]:
        own = self.pools["marker"].get((theme, tam), {})
        return own[m] if m in own else self.lects_of_marker(tam).get(m, set())

    def support(self, kind: str, key, value: str) -> int:
        if kind == "M":
            return len(self.marker_lects(key[0], key[1], value))
        pool = {"E": self.pools["person"], "S": self.pools["stems"]}[kind]
        return len(pool[key].get(value, ()))

    # The base -------------------------------------------------------------

    def row(self, stem: str, marker: str, endings: dict, tam: str, also: tuple = ()) -> list[str] | None:
        """The forms of one tense, or None if one is illegal (on `stem` or on any
        of the stems `also`) or two persons meet."""
        forms = [compose(stem, marker, endings[s]) for s in self.slots_of[tam]]
        if not all(legal(f) for f in forms) or len(set(forms)) < len(forms):
            return None
        if not all(legal(compose(other, marker, endings[s])) for other in also for s in self.slots_of[tam]):
            return None
        return forms

    def solve_theme(self, theme: str, endings: dict):
        """The theme's markers with the least cost (letters after the stem, plus
        BORROW per borrowed marker), at most `budget` pairs alike:
        (cost, {tam: marker}) or None."""
        key = (theme, tuple(endings[s] for s in SLOTS))
        if key in self._themes:
            return self._themes[key]
        stem = SAMPLE_STEM[theme]
        ids: dict = {}
        opts = {}
        for tam in TAMS:
            found = []
            for borrowed, pool in ((False, self.markers[(theme, tam)]), (True, self.borrowable[(theme, tam)])):
                for m in pool:
                    forms = self.row(stem, m, endings, tam, CHECK_STEMS[theme])
                    if forms is not None:
                        cost = sum(len(f) - len(stem) for f in forms) + (BORROW if borrowed else 0)
                        cost -= TIE * self.support("M", (theme, tam), m)
                        found.append((cost, m, tuple(ids.setdefault(f, len(ids)) for f in forms)))
            if not found:
                self._themes[key] = None
                return None
            opts[tam] = sorted(found)
        order = sorted(opts, key=lambda t: len(opts[t]))
        rest = [0.0] * (len(order) + 1)
        for i in range(len(order) - 1, -1, -1):
            rest[i] = rest[i + 1] + opts[order[i]][0][0]
        used = [0] * len(ids)

        # A first answer, greedily, so the exact search has something to beat.
        best: list = [float("inf"), None]
        chosen: dict = {}
        pairs = cost = 0
        for tam in order:
            for c, m, forms in opts[tam]:
                add = sum(used[f] for f in forms)
                if pairs + add <= self.budget:
                    for f in forms:
                        used[f] += 1
                    chosen[tam], pairs, cost = m, pairs + add, cost + c
                    break
            else:
                break
        else:
            best = [cost + 1e-9, dict(chosen)]
        used = [0] * len(ids)
        chosen = {}

        def dfs(i: int, pairs: int, cost: float) -> None:
            if cost + rest[i] >= best[0] - 1e-9:
                return
            if i == len(order):
                best[0], best[1] = cost, dict(chosen)
                return
            tam = order[i]
            for c, m, forms in opts[tam]:
                if cost + c + rest[i + 1] >= best[0] - 1e-9:
                    break
                add = sum(used[f] for f in forms)
                if pairs + add > self.budget:
                    continue
                for f in forms:
                    used[f] += 1
                chosen[tam] = m
                dfs(i + 1, pairs + add, cost + c)
                for f in forms:
                    used[f] -= 1
                del chosen[tam]

        dfs(0, 0, 0.0)
        result = None if best[1] is None else (best[0], best[1])
        self._themes[key] = result
        return result

    def evaluate(self, endings: dict):
        """(cost, markers) of a person-ending set, or None if it cannot pass."""
        if len(set(endings.values())) < len(endings):
            return None
        self.tried += 1
        cost = -TIE * sum(self.support("E", s, e) for s, e in endings.items())
        markers = {}
        for theme in THEMES:
            solved = self.solve_theme(theme, endings)
            if solved is None:
                return None
            cost += solved[0]
            markers.update({(theme, tam): m for tam, m in solved[1].items()})
        return cost, markers

    def candidates(self) -> dict[str, list[str]]:
        """Per person, the endings that some marker can make legal in every
        theme and tense, by how cheaply they can be."""
        out = {}
        for s in SLOTS:
            weight = {}
            for e in self.pools["person"][s]:
                total = 0
                for theme in THEMES:
                    stem = SAMPLE_STEM[theme]
                    for tam in TAMS:
                        if s not in self.slots_of[tam]:
                            continue
                        lens = [len(compose(stem, m, e)) - len(stem)
                                for m in self.markers[(theme, tam)] + self.borrowable[(theme, tam)]
                                if all(legal(compose(st, m, e)) for st in CHECK_STEMS[theme])]
                        if not lens:
                            total = None
                            break
                        total += min(lens)
                    if total is None:
                        break
                if total is not None:
                    weight[e] = (total, -self.support("E", s, e), e)
            out[s] = sorted(weight, key=weight.get)
        return out

    def climb(self, endings: dict, cands: dict):
        """Best-improvement local search: change one person's ending, or swap
        two persons' endings, while that lowers the cost. A start that cannot
        pass moves first to its cheapest neighbour that can."""
        current = self.evaluate(endings)
        while True:
            best = (current[0] if current else float("inf"), None)
            moves = [{s: e} for s in SLOTS for e in cands[s] if e != endings[s]]
            moves += [{a: endings[b], b: endings[a]} for i, a in enumerate(SLOTS) for b in SLOTS[i + 1:]
                      if endings[b] in cands[a] and endings[a] in cands[b]]
            for move in moves:
                trial = {**endings, **move}
                got = self.evaluate(trial)
                if got is not None and got[0] < best[0] - 1e-9:
                    best = (got[0], trial, got[1])
            if best[1] is None:
                return None if current is None else (current[0], endings, current[1])
            endings, current = best[1], (best[0], best[2])

    def starts(self, cands: dict) -> list[dict]:
        """Fixed starting sets, made distinct: each person's cheapest endings
        (and rotations of that order), its best-attested ones, and its
        consonant-initial or vowel-initial ones first, so both families of
        endings are explored."""
        def distinct(pick) -> dict | None:
            out, taken = {}, set()
            for s in SLOTS:
                options = [e for e in pick(s) if e not in taken]
                if not options:
                    return None
                out[s] = options[0]
                taken.add(out[s])
            return out

        by_support = {s: sorted(cands[s], key=lambda e: -self.support("E", s, e)) for s in SLOTS}
        found = [distinct(lambda s, k=k: cands[s][k:] + cands[s][:k]) for k in range(4)]
        found += [distinct(lambda s, k=k: by_support[s][k:] + by_support[s][:k]) for k in range(2)]
        found += [distinct(lambda s, v=v: sorted(cands[s], key=lambda e: (e[:1] in VOWELS) == v)) for v in (False, True)]
        return [f for i, f in enumerate(found) if f is not None and f not in found[:i]]

    def kick(self, best: tuple, cands: dict, top: int = 8) -> tuple:
        """From the best base, try changing two persons at once (each to one of
        its `top` cheapest endings); take any improvement and climb again."""
        self.kicked = 0
        while True:
            cost, endings, _markers = best
            found = None
            for i, a in enumerate(SLOTS):
                for b in SLOTS[i + 1:]:
                    for ea in cands[a][:top]:
                        for eb in cands[b][:top]:
                            if ea == endings[a] or eb == endings[b]:
                                continue
                            got = self.evaluate({**endings, a: ea, b: eb})
                            if got is not None and got[0] < (found or best)[0] - 1e-9:
                                found = (got[0], {**endings, a: ea, b: eb}, got[1])
            if found is None:
                return best
            self.kicked += 1
            best = self.climb(found[1], cands) or found

    def solve_base(self):
        """(cost, endings, markers) for the best base found, or None."""
        cands = self.candidates()
        results = [r for r in (self.climb(start, cands) for start in self.starts(cands)) if r is not None]
        if not results:
            self.agree = False
            return None
        best = self.kick(min(results, key=lambda r: r[0]), cands)
        self.starts_run = len(results)
        self.reached = sum(1 for r in results if r[1] == best[1])
        self.agree = self.reached == len(results)
        optima: dict = {}
        for cost, endings, markers in results:
            key = tuple(endings[s] for s in SLOTS)
            optima.setdefault(key, [cost, endings, markers, 0])[3] += 1
        self.optima = sorted(optima.values(), key=lambda o: o[0])
        return best

    # The irregular verbs ---------------------------------------------------

    def verb_forms(self, theme: str, stems: dict, endings: dict, markers: dict):
        """(tam, slot) → form, or None if a tense breaks the rules."""
        cells = {}
        for tam in self.tams_of[theme]:
            forms = self.row(stems[tam], markers[(theme, tam)], endings, tam)
            if forms is None:
                return None
            cells.update({(tam, s): f for s, f in zip(self.slots_of[tam], forms)})
        if alike_pairs(cells.values()) > self.budget:
            return None
        return cells

    def fit_irregulars(self, endings: dict, markers: dict):
        """A theme and one stem per verb, all three verbs apart in every cell;
        where one stem cannot do it, a second stem for the clashing tenses."""
        full = [t for t in THEMES if len(self.tams_of[t]) == len(TAMS)]
        options = {}
        for verb in IRREGULAR_THEME:
            found = []
            for theme in full:
                for stem in ranked(self.pools["stems"].get(verb, {})):
                    cells = self.verb_forms(theme, defaultdict(lambda s=stem: s), endings, markers)
                    if cells is not None:
                        cost = sum(len(f) for f in cells.values()) - TIE * self.support("S", verb, stem)
                        found.append((cost, theme, stem, cells))
            options[verb] = sorted(found, key=lambda o: o[0])[:40]
        verbs = list(IRREGULAR_THEME)
        best = None
        for combo in product(*(options[v] for v in verbs)):
            cost = sum(o[0] for o in combo)
            if best is not None and cost >= best[0]:
                continue
            if any(combo[i][3].get(k) == combo[j][3].get(k) and k in combo[i][3]
                   for i in range(3) for j in range(i + 1, 3) for k in combo[i][3]):
                continue
            best = (cost, combo)
        if best is None:
            return None
        return {v: {"theme": o[1], "stems": {tam: o[2] for tam in TAMS}} for v, o in zip(verbs, best[1])}

    def solve(self):
        base = self.solve_base()
        if base is None:
            return None
        _cost, endings, markers = base
        irregular = self.fit_irregulars(endings, markers)
        return {"endings": endings, "markers": markers, "irregular": irregular}

    # Reading a solution ----------------------------------------------------

    def paradigms(self, sol: dict) -> dict[str, dict[tuple[str, str], str]]:
        out = {}
        for theme in THEMES:
            out[theme] = {
                (tam, s): compose(SAMPLE_STEM[theme], sol["markers"][(theme, tam)], sol["endings"][s])
                for tam in self.tams_of[theme] for s in self.slots_of[tam]
            }
        for verb, fit in (sol["irregular"] or {}).items():
            out[verb] = {
                (tam, s): compose(fit["stems"][tam], sol["markers"][(fit["theme"], tam)], sol["endings"][s])
                for tam in self.tams_of[fit["theme"]] for s in self.slots_of[tam]
            }
        return out

    def letters(self, paras: dict) -> tuple[int, int]:
        """(letters after the stem over all forms, number of forms)."""
        total = cells = 0
        for name, forms in paras.items():
            cut_at = len(SAMPLE_STEM.get(name, ""))
            total += sum(len(f) - cut_at for f in forms.values())
            cells += len(forms)
        return total, cells

    def checks(self, sol: dict, paras: dict) -> list[tuple[str, bool]]:
        attested = all(self.support("E", s, e) for s, e in sol["endings"].items()) and all(
            self.support("M", k, m) for k, m in sol["markers"].items()) and all(
            self.support("S", v, s) for v, fit in (sol["irregular"] or {}).items() for s in fit["stems"].values())
        legal_all = all(legal(f) for forms in paras.values() for f in forms.values()) and all(
            legal(compose(st, sol["markers"][(t, tam)], sol["endings"][sl]))
            for t in THEMES for st in CHECK_STEMS[t] for tam in TAMS for sl in self.slots_of[tam])
        distinct = all(
            len({forms[(tam, s)] for s in self.slots_of[tam] if (tam, s) in forms}) ==
            sum(1 for s in self.slots_of[tam] if (tam, s) in forms)
            for forms in paras.values() for tam in TAMS
        )
        budget = all(alike_pairs(forms.values()) <= self.budget for forms in paras.values())
        verbs = [v for v in IRREGULAR_THEME if v in paras]
        apart = all(
            paras[a][k] != paras[b][k]
            for i, a in enumerate(verbs) for b in verbs[i + 1:] for k in paras[a] if k in paras[b]
        )
        return [
            ("every piece attested in a daughter", attested),
            ("every form legal, on both test stems", legal_all),
            ("the persons of every tense distinct", distinct),
            (f"at most {self.budget} pairs alike in any paradigm", budget),
            ("esse, stare and habere never alike", apart and sol["irregular"] is not None),
        ]


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

def piece(text: str | None) -> str:
    return "∅" if text == "" else html.escape(text or "")


def chips(lects) -> str:
    order = {lect: i for i, lect in enumerate(vec.SOURCE_LANGS)}
    return picks.chips(sorted(lects, key=lambda lect: order.get(lect, 99)))


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


def paradigm_table(name: str, forms: dict, mine: dict) -> str:
    groups: dict = defaultdict(list)
    for k, f in forms.items():
        groups[f].append(k)
    stem = SAMPLE_STEM.get(name)
    rows = []
    for tam in TAMS:
        if not any((tam, s) in forms for s in SLOTS):
            continue
        tds = []
        for slot in SLOTS:
            if (tam, slot) not in forms:
                tds.append('<td class="na"><span class="none">n/a</span></td>')
                continue
            form = forms[(tam, slot)]
            parts = [f'<div class="pick">{html.escape("-" + form[len(stem):] if stem else form)}</div>']
            others = [k for k in groups[form] if k != (tam, slot)]
            if others:
                parts.append('<div class="mine">alike: ' + ", ".join(
                    f"{picks.SHORT[t]} {s}" for t, s in others) + "</div>")
            if (tam, slot) in mine:
                theirs = mine[(tam, slot)]
                parts.append(f'<div class="mine">yours: {html.escape(theirs)}'
                             f'{" ✓" if norm(theirs) == form else ""}</div>')
            tds.append(f'<td{" class=alike" if others else ""}>{"".join(parts)}</td>')
        rows.append((tam, tds))
    return picks.table(rows)


def render(system: System, sol: dict, strict: str) -> str:
    paras = system.paradigms(sol)
    letters, cells = system.letters(paras)
    endings, markers = sol["endings"], sol["markers"]
    persons = "".join(
        f'<tr><th scope="row">{s}</th><td><span class="pick">{piece(endings[s])}</span></td>'
        f'<td>{chips(system.pools["person"][s].get(endings[s], ()))}</td></tr>'
        for s in SLOTS
    )
    barred = system.pools["barred"]
    barred_line = "; ".join(
        f"{s} <span class=\"pick\">{piece(e)}</span> ({rival} in {n_rival} lects, {s} in {n_own})"
        for s in SLOTS for e, (rival, n_rival, n_own) in sorted(barred[s].items(), key=lambda kv: (len(kv[0]), kv[0]))
    ) or "none"
    marker_rows = []
    for tam in TAMS:
        tds = []
        for theme in THEMES:
            m = markers.get((theme, tam))
            borrowed = m not in system.markers[(theme, tam)]
            tds.append(
                f'<td><span class="pick">{piece(m)}</span>'
                + (' <span class="flag var">borrowed</span>' if borrowed else "")
                + f'<div class="src">{chips(system.marker_lects(theme, tam, m))}</div></td>'
            )
        marker_rows.append(f'<tr><th scope="row">{tam.replace(".", " · ")}</th>{"".join(tds)}</tr>')
    irregular = sol["irregular"] or {}
    stem_lines = []
    for verb, fit in irregular.items():
        by_stem: dict = defaultdict(list)
        for tam in system.tams_of[fit["theme"]]:
            by_stem[fit["stems"][tam]].append(tam)
        stem_lines.append(
            f'<li><b>{verb}</b> takes the markers of the {vec.THEME_TITLE[fit["theme"]]}; stem '
            + "; ".join(
                f'<span class="pick">{piece(s)}</span>'
                + ("" if len(by_stem) == 1 else " (" + ", ".join(picks.SHORT[t] for t in tams) + ")")
                + f' {chips(system.pools["stems"][verb].get(s, ()))}'
                for s, tams in by_stem.items()
            ) + "</li>"
        )
    extra_stems = sum(max(0, len(set(fit["stems"].values())) - 1) for fit in irregular.values())
    borrowed = sorted(k for k, m in markers.items() if m not in system.markers[k])
    assets = (f"<b>{len(borrowed) + extra_stems}</b>: "
              + ("borrowed markers for " + ", ".join(f"the {t} theme's {picks.SHORT[tam]}" for t, tam in borrowed)
                 if borrowed else "no borrowed markers")
              + f"; {extra_stems} extra stem{'s' if extra_stems != 1 else ''} for the irregular verbs.")
    mine = manual_stare(system.pools["named"])
    sections = []
    for name in list(THEMES) + list(irregular):
        title = vec.THEME_TITLE.get(name) or vec.NAMED_TITLE[name]
        forms = paras[name]
        n_alike = alike_pairs(forms.values())
        note = (f"Shown after the sample stem <i>{SAMPLE_STEM[name]}-</i>; every form is also checked on "
                f"<i>{CHECK_STEMS[name][1]}-</i>." if name in SAMPLE_STEM else "Full forms.")
        extra = ""
        if name == "stare" and mine:
            agree = sum(1 for k, form in mine.items() if k in forms and norm(form) == forms[k])
            extra = f" {agree} of your {len(mine)} stare forms are the same as the build's."
        missing = [picks.SHORT[t] for t in TAMS if t not in system.tams_of.get(name, TAMS)]
        if missing:
            extra += " No daughter's row gives this theme a marker for: " + ", ".join(missing) + "."
        sections.append(
            f'<section class="verb"><h2>{html.escape(title)}</h2>'
            f'<p class="tally">{len(forms)} forms, {n_alike} pair{"s" if n_alike != 1 else ""} alike '
            f"(at most {system.budget} allowed). {note}{extra}</p>"
            + paradigm_table(name, forms, mine if name == "stare" else {})
            + "</section>"
        )
    checks = "".join(f'<li>{"✓" if ok else "✗"} {html.escape(label)}</li>' for label, ok in system.checks(sol, paras))
    optima_rows = []
    for cost, ends, marks, starts in system.optima:
        regular = {t: {(tam, sl): compose(SAMPLE_STEM[t], marks[(t, tam)], ends[sl])
                       for tam in TAMS for sl in system.slots_of[tam]} for t in THEMES}
        reg_letters, reg_cells = system.letters(regular)
        n_borrowed = sum(1 for k, m in marks.items() if m not in system.markers[k])
        mark = " (this build)" if ends == endings else ""
        optima_rows.append(
            "<tr>" + "".join(f'<td><span class="pick">{piece(ends[sl])}</span></td>' for sl in SLOTS)
            + f"<td>{reg_letters / reg_cells:.2f}</td><td>{n_borrowed}</td><td>{starts}{mark}</td></tr>"
        )
    optima = (
        '<h2>Other bases the search stopped on</h2>'
        '<p class="tally">Each start climbs until no single change of one person\'s ending (or swap of two) helps. '
        "Where starts stop on different sets, those are real alternatives: to get from one to another, several "
        "persons have to change at once. Letters are averaged over the four regular themes' forms.</p>"
        '<div class="wrap"><table class="pieces"><thead><tr>'
        + "".join(f"<th>{sl}</th>" for sl in SLOTS)
        + "<th>Letters per form</th><th>Borrowed markers</th><th>Starts that end here</th></tr></thead><tbody>"
        + "".join(optima_rows) + "</tbody></table></div>"
    ) if len(system.optima) > 1 else ""
    search = (
        f"Person endings found by local search from {system.starts_run} fixed starting sets "
        f"({system.tried:,} sets weighed, each with its best markers found exactly). "
        + ("All of them end on the same base. "
           if system.agree else
           f"{system.reached} of them end on this base; the others stop on costlier ones. ")
        + ("No change of two persons' endings at once improves on it either. " if not system.kicked else
           f"Changing two persons' endings at once then improved it {system.kicked} time(s). ")
        + "Nothing random is involved: the same result on every run."
    )
    return PAGE.format(
        style=picks.STYLE + EXTRA_STYLE,
        budget=system.budget,
        mean=f"{letters / cells:.2f}",
        letters=f"{letters:,}",
        cells=f"{cells:,}",
        assets=assets,
        strict=strict,
        search=search,
        checks=checks,
        optima=optima,
        persons=persons,
        barred=barred_line,
        theme_head="".join(f"<th>{vec.THEME_TITLE[t]}</th>" for t in THEMES),
        markers="".join(marker_rows),
        stems="".join(stem_lines) or "<li>No fit found.</li>",
        sections="".join(sections),
    )


EXTRA_STYLE = """
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
<li><b>Built from pieces.</b> Every form is stem + marker (one per theme and tense) + person ending.
Where two pieces meet vowel to vowel, the first one's vowel drops (<i>kant-a-o</i> → <i>kanto</i>).</li>
<li><b>Attested only.</b> Every piece is cut from a daughter's endings. A marker is what at least four
of a row's six endings share at the front; a person ending is what follows it, and counts only if its
lect uses it for that person in two tenses or more; an irregular stem is the verb's form minus that
lect's own ending, found at least twice.</li>
<li><b>Legal, and no false friends.</b> Every form passes the spec's syllable rules, checked for each
theme on a stem ending in one consonant and on one ending in two (<i>tem-</i> and <i>respond-</i>), so no
piece leaves a cluster bare. A person never takes an ending the daughters give another person at least
twice as often: <i>-s</i> is the 2sg in most lects, so it cannot be the 1sg.</li>
<li><b>Unique, with minor overloading.</b> The persons of a tense always differ; at most {budget} pairs
of forms in a paradigm may be alike; esse, stare and habere never share a form.</li>
<li><b>Base plus variation.</b> One set of person endings serves every tense and every theme. A theme may
borrow another theme's marker for a tense (as Spanish folded <i>-ere</i> into <i>-er</i>), and must where
its own rows give none or none that works; an irregular verb may take a second stem. Each such variation
costs as much as 20 letters, so it is taken only where it makes a tense possible or saves more than about
three letters on each of its forms.</li>
<li><b>Minimal.</b> Of what passes, the forms with the fewest letters after the stem, every cell counted
once, plus the cost of the variations. Ties go to the pieces more daughters use.</li>
</ol>

<h2>Result</h2>
<ul class="facts">
<li><b>{mean}</b> letters after the stem per form, on average ({letters} letters over {cells} forms).</li>
<li>Variation assets: {assets}</li>
<li>{strict}</li>
<li>{search}</li>
{checks}
</ul>

<h2>Person endings</h2>
<p class="tally">The same six in every tense and every theme.</p>
<div class="wrap"><table class="pieces"><thead><tr><th>Person</th><th>Ending</th><th>Attested in</th></tr></thead>
<tbody>{persons}</tbody></table></div>
<p class="tally">Barred as false friends: {barred}.</p>

{optima}

<h2>Markers, by tense and theme</h2>
<div class="wrap"><table class="pieces"><thead><tr><th>Tense</th>{theme_head}</tr></thead>
<tbody>{markers}</tbody></table></div>

<h2>The irregular verbs</h2>
<ul class="facts">{stems}</ul>

{sections}
</main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--budget", type=int, default=BUDGET)
    args = parser.parse_args()

    pools = harvest()
    system = System(pools, args.budget)
    sol = system.solve()
    if sol is None:
        print("no base passes the rules", file=sys.stderr)
        return 1
    strict_system = System(pools, 0)
    strict_base = strict_system.evaluate(sol["endings"])
    strict_irregular = strict_base and strict_system.fit_irregulars(sol["endings"], strict_base[1])
    if not strict_irregular:
        strict = "With these person endings and no pairs alike at all, no set of markers passes."
    else:
        strict_sol = {"endings": sol["endings"], "markers": strict_base[1], "irregular": strict_irregular}
        s_letters, s_cells = strict_system.letters(strict_system.paradigms(strict_sol))
        strict = (f"With these person endings and no pairs alike at all, the forms would average "
                  f"<b>{s_letters / s_cells:.2f}</b> letters after the stem.")
    args.output.write_text(render(system, sol, strict), encoding="utf-8")
    paras = system.paradigms(sol)
    letters, cells = system.letters(paras)
    print(f"endings {sol['endings']}")
    print(f"{letters / cells:.2f} letters per form over {cells} forms; {system.tried:,} sets weighed; "
          f"{system.reached} of {system.starts_run} starts reach it")
    for label, ok in system.checks(sol, paras):
        print(f"  {'ok ' if ok else 'FAIL'} {label}")
    print(args.output.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
