"""
lacyo.optimizer — Simulated Annealing engine for Lacyo language generation.

Two-stage optimization per grammar.tex Ch.7:
  Stage 1: Root selection (pick best candidate per concept)
  Stage 2: Ending generation (assign fusional endings to paradigm slots)

Energy function per grammar.tex Ch.4:
  E_total = E_root + E_phon + E_end + E_coll + E_tact + E_dist
"""

from __future__ import annotations

import math
import random
import copy
from dataclasses import dataclass, field
from typing import Optional

from lacyo.phonology import (
    PHONEME_INVENTORY, VOWELS, CONSONANTS, LEGAL_CODAS, OBSTRUENTS, ONSET2,
    count_syllables, count_violations, extract_phonemes,
    phonemic_edit_distance, is_phonotactically_legal,
    to_orthography, syllabify,
)
from lacyo.romance_swadesh import SOURCE_LANGS
from lacyo.paradigms import (
    ADJ_TEMPLATES, NOUN_TEMPLATES, VERB_TEMPLATES,
    ADJ_SLOT_NAMES, NOUN_SLOT_NAMES,
)


# ---------------------------------------------------------------------------
# Energy weights (grammar.tex Table 4.1)
# ---------------------------------------------------------------------------

W_SYL  = 1000      # root syllable cost — primary objective
W_PHON = 0         # inventory is not an objective
W_NORM = 10        # prefer stems that cover more source forms (syllable ties)
W_END  = 200       # ending syllable cost
W_COLL = 100_000   # collision penalty
W_TACT = 500_000   # phonotactic violation penalty
W_DIST = 500       # distinctiveness penalty
DIST_THRESHOLD = 2  # minimum phonemic edit distance between endings
N_SOURCES = len(SOURCE_LANGS)  # fr, es, it, pt, ca


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
    lacyo_phonemes: list[str]
    orthography: str
    syllables: int
    violations: int
    support: int = 1  # how many source forms this stem covers

    @property
    def is_legal(self) -> bool:
        return self.violations == 0


@dataclass
class Genome:
    """Complete state of a Lacyo lexicon."""
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
    Generate all phonotactically legal 1-syllable forms from Lacyo inventory.
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

def compute_energy(genome: Genome) -> tuple[float, dict[str, float]]:
    """
    Compute total energy and per-term breakdown.
    Returns (total_energy, breakdown_dict).
    """
    roots = genome.all_roots()
    all_endings = genome.all_endings()

    # E_root: sum of root syllable counts
    e_root = W_SYL * sum(r.syllables for r in roots)

    # E_phon: size of phoneme inventory across entire lexicon
    all_phonemes: set[str] = set()
    for r in roots:
        all_phonemes.update(extract_phonemes(r.lacyo_phonemes))
    for e in all_endings:
        all_phonemes.update(extract_phonemes(e))
    e_phon = W_PHON * len(all_phonemes)

    e_norm = W_NORM * sum(max(0, N_SOURCES - getattr(r, "support", 1)) for r in roots)

    # E_end: sum of ending syllable counts
    e_end = W_END * sum(count_syllables(e) for e in all_endings)

    # E_coll: collision count within each paradigm
    collisions = 0
    # Noun paradigm collisions
    for cls_endings in genome.noun_endings.values():
        seqs = [tuple(v) for v in cls_endings.values()]
        for i in range(len(seqs)):
            for j in range(i + 1, len(seqs)):
                if seqs[i] == seqs[j]:
                    collisions += 1
    # Verb paradigm collisions
    for cls_endings in genome.verb_endings.values():
        seqs = [tuple(v) for v in cls_endings.values()]
        for i in range(len(seqs)):
            for j in range(i + 1, len(seqs)):
                if seqs[i] == seqs[j]:
                    collisions += 1
    # Adj paradigm collisions
    adj_seqs = [tuple(v) for v in genome.adj_endings.values()]
    for i in range(len(adj_seqs)):
        for j in range(i + 1, len(adj_seqs)):
            if adj_seqs[i] == adj_seqs[j]:
                collisions += 1
    e_coll = W_COLL * collisions

    # E_tact: phonotactic violations in all morphemes
    total_viols = 0
    for r in roots:
        total_viols += r.violations
    for e in all_endings:
        total_viols += count_violations(e)
    e_tact = W_TACT * total_viols

    # E_dist: ending distinctiveness within paradigms
    dist_penalty = 0.0
    for cls_endings in genome.noun_endings.values():
        seqs = list(cls_endings.values())
        for i in range(len(seqs)):
            for j in range(i + 1, len(seqs)):
                d = phonemic_edit_distance(seqs[i], seqs[j])
                if d < DIST_THRESHOLD:
                    dist_penalty += DIST_THRESHOLD - d
    for cls_endings in genome.verb_endings.values():
        seqs = list(cls_endings.values())
        # For verb paradigms, only check within same tense group to keep O(n^2) manageable
        for i in range(len(seqs)):
            for j in range(i + 1, min(i + 7, len(seqs))):  # nearby slots
                d = phonemic_edit_distance(seqs[i], seqs[j])
                if d < DIST_THRESHOLD:
                    dist_penalty += DIST_THRESHOLD - d
    e_dist = W_DIST * dist_penalty

    total = e_root + e_norm + e_phon + e_end + e_coll + e_tact + e_dist
    breakdown = {
        "E_root": e_root,
        "E_norm": e_norm,
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

def init_genome(candidates: dict[str, list[Candidate]]) -> Genome:
    """
    Create initial genome: pick shortest legal candidate per concept,
    generate random endings.
    """
    selections: dict[str, int] = {}
    for concept, cands in candidates.items():
        # Prefer legal candidates, then shortest
        legal = [(i, c) for i, c in enumerate(cands) if c.is_legal]
        if legal:
            best_idx = min(
                legal,
                key=lambda x: (x[1].syllables, -x[1].support, len(x[1].lacyo_phonemes), x[1].source_lang),
            )[0]
        else:
            best_idx = min(
                range(len(cands)),
                key=lambda i: (
                    cands[i].violations,
                    cands[i].syllables,
                    -cands[i].support,
                    cands[i].source_lang,
                ),
            )
        selections[concept] = best_idx

    noun_name = random.choice(list(NOUN_TEMPLATES))
    noun_endings = {
        "class_1": {slot: seq[:] for slot, seq in zip(NOUN_SLOTS, NOUN_TEMPLATES[noun_name])}
    }

    verb_name = random.choice(list(VERB_TEMPLATES))
    verb_endings = {
        "class_1": {slot: seq[:] for slot, seq in zip(VERB_SLOTS, VERB_TEMPLATES[verb_name])}
    }

    adj_name = random.choice(list(ADJ_TEMPLATES))
    adj_endings = {slot: seq[:] for slot, seq in zip(ADJ_SLOTS, ADJ_TEMPLATES[adj_name])}

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

def mutate_root(genome: Genome) -> Genome:
    """Swap one concept's root to a different candidate."""
    g = copy.deepcopy(genome)
    concept = random.choice(list(g.selections.keys()))
    n_cands = len(g.candidates[concept])
    if n_cands <= 1:
        return g  # nothing to swap
    old_idx = g.selections[concept]
    new_idx = old_idx
    while new_idx == old_idx:
        new_idx = random.randint(0, n_cands - 1)
    g.selections[concept] = new_idx
    return g


def mutate_ending(genome: Genome) -> Genome:
    """Replace a whole declension/conjugation template (never mix slots)."""
    g = copy.deepcopy(genome)
    r = random.random()
    if r < 0.2:
        name = random.choice(list(NOUN_TEMPLATES))
        cls = random.choice(list(g.noun_endings.keys()))
        g.noun_endings[cls] = {
            slot: seq[:] for slot, seq in zip(NOUN_SLOTS, NOUN_TEMPLATES[name])
        }
    elif r < 0.9:
        name = random.choice(list(VERB_TEMPLATES))
        cls = random.choice(list(g.verb_endings.keys()))
        g.verb_endings[cls] = {
            slot: seq[:] for slot, seq in zip(VERB_SLOTS, VERB_TEMPLATES[name])
        }
    else:
        name = random.choice(list(ADJ_TEMPLATES))
        g.adj_endings = {
            slot: seq[:] for slot, seq in zip(ADJ_SLOTS, ADJ_TEMPLATES[name])
        }
    return g


def mutate(genome: Genome) -> Genome:
    """Apply a random mutation."""
    if random.random() < 0.5:
        return mutate_root(genome)
    else:
        return mutate_ending(genome)


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
    initial_temp: float = 10_000,
    cooling_rate: float = 0.9999,
    min_temp: float = 0.01,
    max_iterations: int = 200_000,
    seed: int = 42,
    progress_interval: int = 10_000,
) -> SAResult:
    """
    Run simulated annealing to find optimal Lacyo lexicon.
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
