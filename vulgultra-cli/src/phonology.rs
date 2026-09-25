//! Phonology domain facade: IPA spelling, syllables, and legality.
//!
//! Root inventory remains observed-data-derived; these helpers only provide
//! feature and phonotactic operations specified in grammar chapter 2.

pub use super::{
    count_syllables, count_violations, ipa_to_ortho, is_consonant, is_legal_coda,
    is_obstruent, is_onset2, is_s_like, is_sonorant, is_vowel, legal_coda_cluster,
    legal_onset_cluster, legal_onset_triple, phonemic_edit_distance,
    phonemes_to_ortho, CONSONANTS, LEGAL_CODAS, OBSTRUENTS, ONSET2, S_LIKE,
    SONORANTS, VOWELS,
};
