//! Optimization domain facade: root SA state, energy, and mutations.

pub use super::{
    compute_energy, enumerate_endings, init_genome, mutate_in_place, undo_mutation,
    CandidateDB, EnergyBreakdown, EnergyCache, Genome, MutationUndo,
    DIST_THRESHOLD, W_COLL, W_DIST, W_END, W_PHON, W_TACT,
};
