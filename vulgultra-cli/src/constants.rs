//! Cross-language constants mirrored by the Python `*_constants.py` modules.
//! The rationale for each family is recorded in docs/architecture.md and the
//! corresponding grammar chapter.

// grammar.tex §2: defaults used by standalone Rust phonology helpers. The
// runtime root inventory is still derived from the candidate grid.
pub const VOWELS: &[&str] = &["a", "e", "i", "o", "u"];
pub const CONSONANTS: &[&str] = &[
    "p", "b", "t", "d", "k", "ɡ", "m", "n", "f", "v", "s", "z", "ʃ",
    "t͡ʃ", "l", "r", "j", "w",
];
pub const LEGAL_CODAS: &[&str] = CONSONANTS;
pub const SONORANTS: &[&str] = &["m", "n", "l", "r"];
pub const OBSTRUENTS: &[&str] = &["p", "b", "t", "d", "k", "ɡ", "f", "v", "s", "z", "ʃ", "t͡ʃ"];
pub const S_LIKE: &[&str] = &["s", "z", "ʃ"];
pub const ONSET2: &[&str] = &["l", "r", "j", "w"];

// grammar.tex §4: morphology terms. Root σ minimization is hard-filtered
// before annealing, so there is no root syllable weight here.
pub const W_PHON: f64 = -1.0;
pub const W_END: f64 = 200.0;
pub const W_COLL: f64 = 100_000.0;
pub const W_TACT: f64 = 2_000.0;
pub const W_DIST: f64 = 500.0;
pub const DIST_THRESHOLD: u32 = 2;

pub const NOUN_SLOTS: &[&str] = &[
    "m_nom_sg", "m_acc_sg", "m_gen_sg", "m_nom_pl", "m_acc_pl", "m_gen_pl",
    "f_nom_sg", "f_acc_sg", "f_gen_sg", "f_nom_pl", "f_acc_pl", "f_gen_pl",
];
pub const ADJ_SLOTS: &[&str] = NOUN_SLOTS;
