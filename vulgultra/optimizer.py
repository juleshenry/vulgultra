"""
vulgultra.optimizer — Simulated Annealing engine for Vulgultra language generation.

Two-stage optimization per grammar.tex Ch.7:
  Stage 1: Root selection (pick best candidate per concept)
  Stage 2: Ending generation (assign fusional endings to paradigm slots)

Energy function per grammar.tex: knapsack roots + 1σ endings.
"""

from __future__ import annotations

import math
import random
import copy
from dataclasses import dataclass, field
from typing import Optional

from vulgultra.phonology import (
    PHONEME_INVENTORY, VOWELS, CONSONANTS, LEGAL_CODAS, OBSTRUENTS, ONSET2,
    count_syllables, count_violations, extract_phonemes,
    phonemic_edit_distance, is_phonotactically_legal,
    to_orthography, syllabify,
)
from vulgultra.romance_swadesh import SOURCE_LANGS
from vulgultra.paradigms import (
    VERB_TEMPLATES, closed_noun_blocks,
    ADJ_SLOT_NAMES, NOUN_SLOT_NAMES,
)


# ---------------------------------------------------------------------------
# Energy weights (grammar.tex Table 4.1)
# ---------------------------------------------------------------------------

# Root syllable minima are applied as a hard shortlist before annealing.
# Inside that slice the objective maximizes attested phoneme contrasts, then
# source-lect coverage, then cross-lect cognate-morpheme support.
W_SYL  = 1000
W_PHON = -40       # maximize |Φ|, bounded by the attested 23-phoneme inventory
W_DIV  = 1          # after |Φ|: maximize distinct source lects; |L| < 40
W_NORM = 0.02       # after lect coverage: minimize mean cognate-morpheme support gap
W_END  = 200
W_COLL = 100_000
W_TACT = 2000
W_DIST = 500
DIST_THRESHOLD = 2
N_SOURCES = len(SOURCE_LANGS)
if W_DIV * N_SOURCES >= abs(W_PHON):
    raise ValueError(f"|L|={N_SOURCES} breaks |L|*W_DIV < W_PHON")


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
    support: int = 1  # how many source forms this stem covers
    evidence: str = ""
    relation: str = "direct"
    morpheme_key: str = ""

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

VERB_SLOTS_IND = [
    f"{tense}_{person}{number}"
    for tense in ["prs", "pst", "fut"]
    for person in ["1", "2", "3"]
    for number in ["sg", "pl"]
]

VERB_SLOTS_SUBJ = [
    f"{tense}_subj_{person}{number}"
    for tense in ["prs", "pst", "fut"]
    for person in ["1", "2", "3"]
    for number in ["sg", "pl"]
]

VERB_NONFINITE = ["inf", "ptcp_act", "ptcp_pas", "imp_2sg", "imp_2pl"]

VERB_SLOTS = VERB_SLOTS_IND + VERB_SLOTS_SUBJ + VERB_NONFINITE

ADJ_SLOTS = list(ADJ_SLOT_NAMES)


# ---------------------------------------------------------------------------
# Generate legal 1-syllable endings
# ---------------------------------------------------------------------------

def generate_legal_endings() -> list[list[str]]:
    """
    Generate all phonotactically legal 1-syllable forms from Vulgultra inventory.
    Templates: V, CV, VC, CVC (most common/useful for endings).
    We limit to the most useful subset for speed.
    """
    endings: list[list[str]] = []
    vowels = sorted(VOWELS)
    codas = sorted(LEGAL_CODAS)
    # Simple onsets (single consonant, not clusters for endings)
    onsets = sorted(CONSONANTS - {"w"})  # w is rare in endings

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

def get_legal_endings() -> list[list[str]]:
    global _LEGAL_ENDINGS
    if _LEGAL_ENDINGS is None:
        _LEGAL_ENDINGS = generate_legal_endings()
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

    e_root = W_SYL * sum(r.syllables for r in roots)

    all_phonemes: set[str] = set()
    for r in roots:
        all_phonemes.update(extract_phonemes(r.vulgultra_phonemes))
    for e in endings:
        all_phonemes.update(extract_phonemes(e))
    e_phon = W_PHON * len(all_phonemes)

    n_roots = max(len(roots), 1)
    support_gap = sum(max(0, N_SOURCES - getattr(r, "support", 1)) for r in roots)
    e_norm = W_NORM * (support_gap / n_roots)
    n_lects = len({r.source_lang for r in roots})
    e_div = W_DIV * max(0, N_SOURCES - n_lects)

    e_end = W_END * sum(count_syllables(e) for e in endings)
    e_coll = W_COLL * _collision_count(genome)

    total_viols = sum(r.violations for r in roots)
    for e in endings:
        total_viols += count_violations(e)
    e_tact = W_TACT * total_viols
    e_dist = W_DIST * _dist_penalty(genome)

    total = e_root + e_phon + e_div + e_norm + e_end + e_coll + e_tact + e_dist
    breakdown = {
        "E_root": e_root,
        "E_phon": e_phon,
        "E_div": e_div,
        "E_norm": e_norm,
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
    """Min σ shortlist, then most new phonemes, a new lect, then morpheme support.

    Inventory and diversity couple concepts, so this is a set-cover heuristic;
    SA can still improve phoneme inventory, lect coverage, and support globally.
    """
    items: list[tuple[int, str, list[tuple[int, Candidate]]]] = []
    for concept, cands in candidates.items():
        sl = _sigma_slice(cands)
        items.append((len(sl), concept, sl))
    items.sort(key=lambda t: (t[0], t[1]))

    used_ph: set[str] = set()
    used_lang: set[str] = set()
    selections: dict[str, int] = {}
    for _, concept, sl in items:
        def key(ic: tuple[int, Candidate]) -> tuple:
            _i, c = ic
            new_ph = sum(1 for p in extract_phonemes(c.vulgultra_phonemes) if p not in used_ph)
            new_lang = 1 if c.source_lang in used_lang else 0
            return (-new_ph, new_lang, -c.support, len(c.vulgultra_phonemes), c.source_lang)

        idx, c = min(sl, key=key)
        selections[concept] = idx
        used_ph |= extract_phonemes(c.vulgultra_phonemes)
        used_lang.add(c.source_lang)
    return selections


def _slot_map(slots: list[str], cells: list[list[str]]) -> dict[str, list[str]]:
    if len(slots) != len(cells):
        raise ValueError(f"ending block length {len(cells)} != {len(slots)} slots")
    return {slot: [p for p in seq] for slot, seq in zip(slots, cells)}


# One lect owns a whole 6-person row. Tenses are chosen separately.
FINITE_ROW_NAMES = ("prs", "pst", "fut", "subj", "theme_i", "theme_a")


def _row_score(row: list[list[str]], phonemes: set[str], used_lects: list[str], lang: str) -> tuple:
    """Collisions, violations, distance, new phonemes (max), then unused lect."""
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
    already = 1 if lang in used_lects else 0
    return (collisions, violations, dist, -new_ph, already, lang)


def assemble_verb_rows(phonemes: set[str]) -> tuple[list[list[str]], str]:
    """Pick each finite tense from the lect that wins that row alone.

    Slots inside the row stay one lect. Non-finite cells are the shared tail.
    """
    used = set(phonemes)
    used_lects: list[str] = []
    labels: list[str] = []
    cells: list[list[str]] = []
    langs = sorted(VERB_TEMPLATES)
    for r, name in enumerate(FINITE_ROW_NAMES):
        start = r * 6
        best: tuple | None = None
        best_row: list[list[str]] | None = None
        best_ph: set[str] = set()
        for lang in langs:
            row = [list(cell) for cell in VERB_TEMPLATES[lang][start:start + 6]]
            key = _row_score(row, used, used_lects, lang)
            if best is None or key < best:
                best = key
                best_row = row
                best_ph = set()
                for cell in row:
                    best_ph.update(extract_phonemes(cell))
        assert best_row is not None and best is not None
        cells.extend(best_row)
        used_lects.append(best[5])
        labels.append(f"{name}={best[5]}")
        used |= best_ph
    tail_lang = langs[0]
    cells.extend(list(cell) for cell in VERB_TEMPLATES[tail_lang][36:])
    return cells, ",".join(labels)


def enumerate_endings(
    candidates: dict[str, list[Candidate]],
    selections: dict[str, int],
) -> tuple[dict, dict, dict, str, str]:
    """Noun theme is global. Each verb tense is its own row. Roots stay pinned."""
    nouns = closed_noun_blocks()
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
        verb_cells, verb_label = assemble_verb_rows(noun_ph)
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
        key = (energy, nname, verb_label)
        if best_key is None or key < best_key:
            best_key = key
            best = (noun_map, verb_map, adj_map, nname, verb_label)
    assert best is not None
    return best


def init_genome(candidates: dict[str, list[Candidate]]) -> Genome:
    """Min-σ set-cover roots, then the exact ending pair at those roots."""
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
    return SAResult(
        genome=best_genome,
        energy=best_energy,
        breakdown=best_breakdown,
        iterations=final_iters,
        acceptance_rate=accepted / max(final_iters, 1),
    )
