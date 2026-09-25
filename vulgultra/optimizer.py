"""
vulgultra.optimizer — Simulated Annealing engine for Vulgultra language generation.

Root candidates are hard-filtered to each concept's shortest legal forms.
Annealing then chooses among those ties to maximize the observed root-segment
union. Inflection tables may also use productive combinations of segments
observed in the shortlisted grid.
"""

from __future__ import annotations

import math
import random
import copy
from dataclasses import dataclass, field
from typing import Optional

from vulgultra.phonology import (
    VOWELS, CONSONANTS, LEGAL_CODAS,
    count_syllables, count_violations, extract_phonemes,
    phonemic_edit_distance, is_phonotactically_legal,
    to_orthography, syllabify,
)
from vulgultra.paradigms import (
    NOUN_TEMPLATES, VERB_TEMPLATES, closed_noun_blocks,
    productive_grid_blocks,
    ADJ_SLOT_NAMES, NOUN_SLOT_NAMES,
)
from vulgultra.optimizer_constants import (
    DIST_THRESHOLD, VERB_NONFINITE, VERB_SLOTS, VERB_SLOTS_IND,
    VERB_SLOTS_SUBJ, W_COLL, W_DIST, W_END, W_PHON, W_TACT,
)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Candidate:
    """A candidate root for a concept."""
    concept: str
    source_lang: str
    source_word: str
    ipa: str
    vulgultra_phonemes: list[str]
    orthography: str
    syllables: int
    violations: int
    evidence: str = ""
    relation: str = "direct"
    pos: str = ""

    @property
    def is_legal(self) -> bool:
        return self.violations == 0


@dataclass
class Genome:
    """Complete state of a Vulgultra lexicon."""
    # concept_id → index into candidates list
    selections: dict[str, int]
    # All candidates grouped by concept
    candidates: dict[str, list[Candidate]]
    # Noun endings: class_id → {slot_name → phoneme_seq}
    noun_endings: dict[str, dict[str, list[str]]]
    # Verb endings: class_id → {slot_name → phoneme_seq}
    verb_endings: dict[str, dict[str, list[str]]]
    # Adjective endings: {slot_name → phoneme_seq}
    adj_endings: dict[str, list[str]]

    def get_root(self, concept: str) -> Candidate:
        idx = self.selections[concept]
        return self.candidates[concept][idx]

    def all_roots(self) -> list[Candidate]:
        return [self.get_root(c) for c in self.selections]

    def all_endings(self) -> list[list[str]]:
        """Collect all ending phoneme sequences."""
        endings: list[list[str]] = []
        for cls in self.noun_endings.values():
            endings.extend(cls.values())
        for cls in self.verb_endings.values():
            endings.extend(cls.values())
        endings.extend(self.adj_endings.values())
        return endings


# ---------------------------------------------------------------------------
# Ending paradigm slots (grammar.tex Ch.3)
# ---------------------------------------------------------------------------

NOUN_SLOTS = list(NOUN_SLOT_NAMES)

ADJ_SLOTS = list(ADJ_SLOT_NAMES)


# ---------------------------------------------------------------------------
# Generate legal 1-syllable endings
# ---------------------------------------------------------------------------

def generate_legal_endings() -> list[list[str]]:
    """
    Legacy helper: generate legal 1σ shapes from the current grid inventory.
    The active catalog uses `productive_grid_blocks` to build structured
    noun and verb tables from the same unrestricted observed segment set.
    """
    endings: list[list[str]] = []
    vowels = sorted(VOWELS)
    codas = sorted(LEGAL_CODAS)
    # Simple onsets (single consonant, not clusters for endings)
    onsets = sorted(CONSONANTS)

    # V
    for v in vowels:
        endings.append([v])

    # CV
    for c in onsets:
        for v in vowels:
            endings.append([c, v])

    # VC
    for v in vowels:
        for cd in codas:
            endings.append([v, cd])

    # CVC
    for c in onsets:
        for v in vowels:
            for cd in codas:
                endings.append([c, v, cd])

    return endings


# Cache it
_LEGAL_ENDINGS: list[list[str]] | None = None
_LEGAL_ENDINGS_INVENTORY: tuple[tuple[str, ...], ...] | None = None

def get_legal_endings() -> list[list[str]]:
    global _LEGAL_ENDINGS, _LEGAL_ENDINGS_INVENTORY
    inventory = (
        tuple(sorted(VOWELS)),
        tuple(sorted(CONSONANTS)),
        tuple(sorted(LEGAL_CODAS)),
    )
    if _LEGAL_ENDINGS is None or inventory != _LEGAL_ENDINGS_INVENTORY:
        _LEGAL_ENDINGS = generate_legal_endings()
        _LEGAL_ENDINGS_INVENTORY = inventory
    return _LEGAL_ENDINGS


def random_ending() -> list[str]:
    """Pick a random legal 1-syllable ending."""
    endings = get_legal_endings()
    return list(random.choice(endings))


# ---------------------------------------------------------------------------
# Energy computation
# ---------------------------------------------------------------------------

def _pairs_equal(seqs: list[tuple]) -> int:
    n = 0
    for i in range(len(seqs)):
        for j in range(i + 1, len(seqs)):
            if seqs[i] == seqs[j]:
                n += 1
    return n


def _scored_endings(genome: Genome) -> list[list[str]]:
    """Noun table once, then the verb table. Adjectives copy the noun table."""
    seqs: list[list[str]] = []
    for cls in genome.noun_endings.values():
        for slot in NOUN_SLOTS:
            if slot in cls:
                seqs.append(cls[slot])
    for cls in genome.verb_endings.values():
        for slot in VERB_SLOTS:
            if slot in cls:
                seqs.append(cls[slot])
    return seqs


def _collision_count(genome: Genome) -> int:
    """Noun cells distinct. Verb collisions inside each 6-person row, and among non-finite cells."""
    collisions = 0
    for cls in genome.noun_endings.values():
        seqs = [tuple(cls[s]) for s in NOUN_SLOTS if s in cls]
        collisions += _pairs_equal(seqs)
    for cls in genome.verb_endings.values():
        seqs = [tuple(cls[s]) for s in VERB_SLOTS if s in cls]
        finite = seqs[:36]
        for start in range(0, len(finite), 6):
            collisions += _pairs_equal(finite[start:start + 6])
        collisions += _pairs_equal(seqs[36:])
    return collisions


def _dist_penalty(genome: Genome) -> float:
    """d ≥ 2 inside each finite 6-person row. Noun minimal pairs are not taxed."""
    penalty = 0.0
    for cls in genome.verb_endings.values():
        seqs = [cls[s] for s in VERB_SLOTS if s in cls]
        finite = seqs[:36]
        for start in range(0, len(finite), 6):
            row = finite[start:start + 6]
            for i in range(len(row)):
                for j in range(i + 1, len(row)):
                    d = phonemic_edit_distance(row[i], row[j])
                    if d < DIST_THRESHOLD:
                        penalty += DIST_THRESHOLD - d
    return penalty


def compute_energy(genome: Genome) -> tuple[float, dict[str, float]]:
    """
    Compute total energy and per-term breakdown.
    Returns (total_energy, breakdown_dict).
    """
    roots = genome.all_roots()
    endings = _scored_endings(genome)

    root_phonemes: set[str] = set()
    for r in roots:
        root_phonemes.update(extract_phonemes(r.vulgultra_phonemes))
    # Endings are selected once against the root inventory. Keeping them out
    # of the root SA term prevents a productive template from pre-filling the
    # very inventory the lexical annealing is meant to optimize.
    e_phon = W_PHON * len(root_phonemes)

    e_end = W_END * sum(count_syllables(e) for e in endings)
    e_coll = W_COLL * _collision_count(genome)

    total_viols = sum(r.violations for r in roots)
    for e in endings:
        total_viols += count_violations(e)
    e_tact = W_TACT * total_viols
    e_dist = W_DIST * _dist_penalty(genome)

    total = e_phon + e_end + e_coll + e_tact + e_dist
    breakdown = {
        "E_phon": e_phon,
        "E_end": e_end,
        "E_coll": e_coll,
        "E_tact": e_tact,
        "E_dist": e_dist,
    }
    return total, breakdown


# ---------------------------------------------------------------------------
# Genome initialization
# ---------------------------------------------------------------------------

def _sigma_slice(cands: list[Candidate]) -> list[tuple[int, Candidate]]:
    """Candidates that already win on legality then syllables."""
    best = min((c.violations, c.syllables) for c in cands)
    return [(i, c) for i, c in enumerate(cands) if (c.violations, c.syllables) == best]


def greedy_root_selections(candidates: dict[str, list[Candidate]]) -> dict[str, int]:
    """Choose the shortest legal forms, preferring segments not yet selected."""
    items: list[tuple[int, str, list[tuple[int, Candidate]]]] = []
    for concept, cands in candidates.items():
        sl = _sigma_slice(cands)
        items.append((len(sl), concept, sl))
    items.sort(key=lambda t: (t[0], t[1]))

    used_ph: set[str] = set()
    selections: dict[str, int] = {}
    for _, concept, sl in items:
        def key(ic: tuple[int, Candidate]) -> tuple:
            _i, c = ic
            new_ph = sum(1 for p in extract_phonemes(c.vulgultra_phonemes) if p not in used_ph)
            return (-new_ph, c.source_lang, c.source_word)

        idx, c = min(sl, key=key)
        selections[concept] = idx
        used_ph |= extract_phonemes(c.vulgultra_phonemes)
    return selections


def _slot_map(slots: list[str], cells: list[list[str]]) -> dict[str, list[str]]:
    if len(slots) != len(cells):
        raise ValueError(f"ending block length {len(cells)} != {len(slots)} slots")
    return {slot: [p for p in seq] for slot, seq in zip(slots, cells)}


# One lect owns a whole 6-person row. Tenses are chosen separately.
FINITE_ROW_NAMES = ("prs", "pst", "fut", "subj", "theme_i", "theme_a")


def _row_score(row: list[list[str]], phonemes: set[str], lang: str) -> tuple:
    """Choose legal short rows, then maximize new segment diversity.

    The explicit order is collision/phonotactics, distance, shortest cells,
    then maximum new-phone coverage. It makes the conjugation heuristic
    inspectable instead of letting a long exotic ending win by accident.
    """
    seqs = [tuple(cell) for cell in row]
    collisions = _pairs_equal(seqs)
    violations = sum(count_violations(cell) for cell in row)
    dist = 0
    for i in range(len(row)):
        for j in range(i + 1, len(row)):
            d = phonemic_edit_distance(row[i], row[j])
            if d < DIST_THRESHOLD:
                dist += DIST_THRESHOLD - d
    fresh: set[str] = set()
    for cell in row:
        fresh.update(extract_phonemes(cell))
    new_ph = len(fresh - phonemes)
    length = sum(len(cell) for cell in row)
    return (collisions, violations, dist, length, -new_ph, lang)


def assemble_verb_rows(
    phonemes: set[str],
    templates: dict[str, list[list[str]]] | None = None,
) -> tuple[list[list[str]], str]:
    """Pick each finite tense from the lect that wins that row alone.

    Slots inside the row stay one lect. Non-finite cells are the shared tail.
    """
    used = set(phonemes)
    labels: list[str] = []
    cells: list[list[str]] = []
    templates = templates or VERB_TEMPLATES
    langs = sorted(templates)
    for r, name in enumerate(FINITE_ROW_NAMES):
        start = r * 6
        best: tuple | None = None
        best_row: list[list[str]] | None = None
        best_ph: set[str] = set()
        for lang in langs:
            row = [list(cell) for cell in templates[lang][start:start + 6]]
            key = _row_score(row, used, lang)
            if best is None or key < best:
                best = key
                best_row = row
                best_ph = set()
                for cell in row:
                    best_ph.update(extract_phonemes(cell))
        assert best_row is not None and best is not None
        cells.extend(best_row)
        labels.append(f"{name}={best[5]}")
        used |= best_ph
    tail_lang = langs[0]
    cells.extend(list(cell) for cell in templates[tail_lang][36:])
    return cells, ",".join(labels)


def enumerate_endings(
    candidates: dict[str, list[Candidate]],
    selections: dict[str, int],
) -> tuple[dict, dict, dict, str, str]:
    """Noun theme is global. Each verb tense is its own row. Roots stay pinned."""
    observed = {
        phone
        for candidate_list in candidates.values()
        for candidate in candidate_list
        for phone in candidate.vulgultra_phonemes
    }
    productive_nouns, productive_verbs = productive_grid_blocks(observed)
    nouns: dict[str, list[list[str]]] = {
        f"theme:{name}": cells
        for name, cells in closed_noun_blocks().items()
    }
    nouns.update({f"lect:{lang}": cells for lang, cells in NOUN_TEMPLATES.items()})
    if productive_nouns:
        nouns["grid-inventory"] = productive_nouns
    verb_templates = {lang: cells for lang, cells in VERB_TEMPLATES.items()}
    if productive_verbs:
        verb_templates["grid-inventory"] = productive_verbs
    root_ph: set[str] = set()
    for concept, idx in selections.items():
        root_ph.update(extract_phonemes(candidates[concept][idx].vulgultra_phonemes))

    best_key: tuple | None = None
    best: tuple | None = None
    for nname in sorted(nouns):
        noun_map = {"class_1": _slot_map(NOUN_SLOTS, nouns[nname])}
        noun_ph = set(root_ph)
        for cell in noun_map["class_1"].values():
            noun_ph.update(extract_phonemes(cell))
        verb_cells, verb_label = assemble_verb_rows(noun_ph, verb_templates)
        verb_map = {"class_1": _slot_map(VERB_SLOTS, verb_cells)}
        adj_map = {slot: seq[:] for slot, seq in noun_map["class_1"].items()}
        trial = Genome(
            selections=selections,
            candidates=candidates,
            noun_endings=noun_map,
            verb_endings=verb_map,
            adj_endings=adj_map,
        )
        energy, _bd = compute_energy(trial)
        ending_ph: set[str] = set()
        for cell in trial.all_endings():
            ending_ph.update(cell)
        # Morphology is chosen after roots: prefer valid paradigms that add
        # the most distinct segments to the final root+ending inventory.
        ending_bonus = len(ending_ph - root_ph)
        # This is exactly the morphology objective in grammar.tex §4:
        # reward the final root+ending union, then use stable names only to
        # make equal-energy runs deterministic.
        key = (energy - ending_bonus, nname, verb_label)
        if best_key is None or key < best_key:
            best_key = key
            best = (noun_map, verb_map, adj_map, nname, verb_label)
    assert best is not None
    return best


def init_genome(candidates: dict[str, list[Candidate]]) -> Genome:
    """Shortest-slice, segment-greedy roots, then the ending pair at those roots."""
    selections = greedy_root_selections(candidates)
    noun_endings, verb_endings, adj_endings, _theme, _lect = enumerate_endings(
        candidates, selections,
    )
    return Genome(
        selections=selections,
        candidates=candidates,
        noun_endings=noun_endings,
        verb_endings=verb_endings,
        adj_endings=adj_endings,
    )


# ---------------------------------------------------------------------------
# SA mutations
# ---------------------------------------------------------------------------

def _slice_indices(cands: list[Candidate]) -> list[int]:
    best = min((c.violations, c.syllables) for c in cands)
    return [i for i, c in enumerate(cands) if (c.violations, c.syllables) == best]


def mutate_root(genome: Genome) -> Genome:
    """Swap one concept to another stem in its minimum-(violations, σ) slice."""
    g = copy.deepcopy(genome)
    movable = [c for c, cands in g.candidates.items() if len(_slice_indices(cands)) > 1]
    if not movable:
        return g
    concept = random.choice(movable)
    options = [i for i in _slice_indices(g.candidates[concept]) if i != g.selections[concept]]
    g.selections[concept] = random.choice(options)
    return g


def mutate(genome: Genome) -> Genome:
    """Root move inside the σ-slice. Endings are enumerated, not annealed."""
    return mutate_root(genome)


# ---------------------------------------------------------------------------
# Simulated Annealing
# ---------------------------------------------------------------------------

@dataclass
class SAResult:
    genome: Genome
    energy: float
    breakdown: dict[str, float]
    iterations: int
    acceptance_rate: float


def anneal(
    candidates: dict[str, list[Candidate]],
    initial_temp: float = 80.0,
    cooling_rate: float = 0.9999852445,
    min_temp: float = 0.05,
    max_iterations: int = 500_000,
    seed: int = 42,
    progress_interval: int = 10_000,
) -> SAResult:
    """
    Run simulated annealing to find optimal Vulgultra lexicon.
    """
    random.seed(seed)

    genome = init_genome(candidates)
    energy, breakdown = compute_energy(genome)

    best_genome = copy.deepcopy(genome)
    best_energy = energy
    best_breakdown = breakdown.copy()

    temp = initial_temp
    accepted = 0

    for it in range(max_iterations):
        new_genome = mutate(genome)
        new_energy, new_breakdown = compute_energy(new_genome)

        delta = new_energy - energy

        if delta < 0 or random.random() < math.exp(-delta / max(temp, 1e-10)):
            genome = new_genome
            energy = new_energy
            breakdown = new_breakdown
            accepted += 1

            if energy < best_energy:
                best_genome = copy.deepcopy(genome)
                best_energy = energy
                best_breakdown = breakdown.copy()

        temp *= cooling_rate

        if temp < min_temp:
            break

        if progress_interval and (it + 1) % progress_interval == 0:
            print(f"  iter {it+1:>7d} | temp {temp:>10.2f} | energy {energy:>12.0f} | best {best_energy:>12.0f} | accept {accepted/(it+1):.2%}")

    final_iters = it + 1
    # Re-enumerate the ending pair against the final annealed roots. Endings
    # stay fixed during root moves so they cannot pre-fill the root score.
    noun_endings, verb_endings, adj_endings, _theme, _lect = enumerate_endings(
        candidates, best_genome.selections,
    )
    best_genome.noun_endings = noun_endings
    best_genome.verb_endings = verb_endings
    best_genome.adj_endings = adj_endings
    best_energy, best_breakdown = compute_energy(best_genome)
    return SAResult(
        genome=best_genome,
        energy=best_energy,
        breakdown=best_breakdown,
        iterations=final_iters,
        acceptance_rate=accepted / max(final_iters, 1),
    )
