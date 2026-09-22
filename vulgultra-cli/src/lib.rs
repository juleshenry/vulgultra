//! vulgultra phonology & energy function — core types and optimizer logic.
//!
//! Implements the grammar.tex Ch.2 phonotactics and Ch.4 energy function
//! operating on IPA phoneme sequences (not orthographic characters).
//!
//! Performance-critical: the SA hot loop runs millions of iterations.
//! Key optimizations:
//!   - Genome stores only mutable state (selections + endings), not candidates.
//!     Cloning/undo is O(1) per mutation.
//!   - In-place mutation with undo: mutate → evaluate → accept or revert.
//!   - Cached phoneme reference counts: E_phon recomputed in O(phonemes_in_changed_root)
//!     instead of O(all_roots × all_phonemes).
//!   - Cached aggregate sums: total_root_syls, total_root_viols updated incrementally.

use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};

// ── Vulgultra phoneme inventory ceiling (grammar.tex Ch.2) ──────────────────
// These define the *search space*. The actual inventory is emergent:
// whichever phonemes the optimizer's selected roots use = the inventory.

pub const VOWELS: &[&str] = &["a", "e", "i", "o", "u"];

pub const CONSONANTS: &[&str] = &[
    "p", "b", "t", "d", "k", "ɡ",
    "m", "n",
    "f", "v", "s", "z", "ʃ",
    "t͡ʃ",
    "l", "r",
    "j", "w",
];

pub const LEGAL_CODAS: &[&str] = &[
    "p", "b", "t", "d", "k", "ɡ",
    "m", "n",
    "f", "v", "s", "z", "ʃ",
    "t͡ʃ",
    "l", "r",
    "j", "w",
];  // any consonant — naturalistic, respects Romance sources
pub const SONORANTS: &[&str] = &["m", "n", "l", "r"];
pub const OBSTRUENTS: &[&str] = &["p", "b", "t", "d", "k", "ɡ", "f", "v", "s", "z", "ʃ", "t͡ʃ"];
pub const S_LIKE: &[&str] = &["s", "z", "ʃ"];
pub const ONSET2: &[&str] = &["l", "r", "j", "w"];

// ── IPA → orthography ───────────────────────────────────────────────────

pub fn ipa_to_ortho(phoneme: &str) -> &str {
    match phoneme {
        "p" => "p", "b" => "b", "t" => "t", "d" => "d", "k" => "k", "ɡ" => "g",
        "m" => "m", "n" => "n",
        "f" => "f", "v" => "v", "s" => "s", "z" => "z",
        "ʃ" => "x", "t͡ʃ" => "c",
        "l" => "l", "r" => "r",
        "j" => "y", "w" => "w",
        "a" => "a", "e" => "e", "i" => "i", "o" => "o", "u" => "u",
        _ => "?",
    }
}

pub fn phonemes_to_ortho(seq: &[String]) -> String {
    seq.iter().map(|p| ipa_to_ortho(p)).collect()
}

// ── Helper predicates ───────────────────────────────────────────────────

#[inline]
pub fn is_vowel(p: &str) -> bool {
    VOWELS.contains(&p)
}

#[inline]
pub fn is_consonant(p: &str) -> bool {
    !is_vowel(p)
}

#[inline]
pub fn is_legal_coda(p: &str) -> bool {
    LEGAL_CODAS.contains(&p)
}

#[inline]
pub fn is_obstruent(p: &str) -> bool {
    OBSTRUENTS.contains(&p)
}

#[inline]
pub fn is_onset2(p: &str) -> bool {
    ONSET2.contains(&p)
}

#[inline]
pub fn is_s_like(p: &str) -> bool {
    S_LIKE.contains(&p)
}

pub fn legal_onset_cluster(c1: &str, c2: &str) -> bool {
    if is_onset2(c2) && (is_obstruent(c1) || is_sonorant(c1) || is_s_like(c1)) {
        return true;
    }
    is_s_like(c1) && c1 != c2
}

pub fn legal_onset_triple(c1: &str, c2: &str, c3: &str) -> bool {
    is_s_like(c1) && legal_onset_cluster(c2, c3)
}

pub fn legal_coda_cluster(c1: &str, c2: &str) -> bool {
    if is_sonorant(c1) {
        return true;
    }
    is_s_like(c1) && is_obstruent(c2)
}

#[inline]
pub fn is_sonorant(p: &str) -> bool {
    SONORANTS.contains(&p)
}

// ── Syllable counting (IPA-based) ───────────────────────────────────────

pub fn count_syllables(seq: &[String]) -> u32 {
    let c = seq.iter().filter(|p| is_vowel(p)).count() as u32;
    c.max(1)
}

// ── Phonotactic violation counting ──────────────────────────────────────

fn syllabify(seq: &[String]) -> Vec<Vec<usize>> {
    if seq.is_empty() {
        return vec![];
    }

    let vowel_positions: Vec<usize> = seq.iter()
        .enumerate()
        .filter(|(_, p)| is_vowel(p))
        .map(|(i, _)| i)
        .collect();

    if vowel_positions.is_empty() {
        return vec![(0..seq.len()).collect()];
    }

    let mut syllables: Vec<Vec<usize>> = Vec::new();

    for (si, &vi) in vowel_positions.iter().enumerate() {
        let start;
        if si == 0 {
            start = 0;
        } else {
            let prev_vi = vowel_positions[si - 1];
            let inter_start = prev_vi + 1;
            let inter_len = vi - inter_start;

            if inter_len == 0 {
                start = vi;
            } else if inter_len == 1 {
                start = inter_start;
            } else if inter_len == 2 {
                let c1 = &seq[inter_start];
                let c2 = &seq[inter_start + 1];
                if legal_onset_cluster(c1, c2) {
                    start = inter_start;
                } else {
                    syllables.last_mut().unwrap().push(inter_start);
                    start = inter_start + 1;
                }
            } else {
                let take3 = inter_len >= 3
                    && legal_onset_triple(&seq[vi - 3], &seq[vi - 2], &seq[vi - 1]);
                if take3 {
                    for idx in inter_start..(vi - 3) {
                        syllables.last_mut().unwrap().push(idx);
                    }
                    start = vi - 3;
                } else if legal_onset_cluster(&seq[vi - 2], &seq[vi - 1]) {
                    for idx in inter_start..(vi - 2) {
                        syllables.last_mut().unwrap().push(idx);
                    }
                    start = vi - 2;
                } else {
                    for idx in inter_start..(vi - 1) {
                        syllables.last_mut().unwrap().push(idx);
                    }
                    start = vi - 1;
                }
            }
        }

        let end = vi + 1;
        let syl: Vec<usize> = (start..end).collect();
        syllables.push(syl);
    }

    let last_vi = *vowel_positions.last().unwrap();
    if last_vi + 1 < seq.len() {
        for idx in (last_vi + 1)..seq.len() {
            syllables.last_mut().unwrap().push(idx);
        }
    }

    syllables
}

pub fn count_violations(seq: &[String]) -> u32 {
    let mut violations = 0u32;
    let syls = syllabify(seq);

    for syl_indices in &syls {
        let syl: Vec<&str> = syl_indices.iter().map(|&i| seq[i].as_str()).collect();

        let nuc_pos = syl.iter().position(|p| is_vowel(p));
        let nuc_idx = match nuc_pos {
            Some(i) => i,
            None => { violations += 1; continue; }
        };

        let onset = &syl[..nuc_idx];
        let coda = &syl[nuc_idx + 1..];

        if coda.len() > 2 {
            violations += (coda.len() - 2) as u32;
        }
        if coda.len() == 2 && !legal_coda_cluster(coda[0], coda[1]) {
            violations += 1;
        }
        if onset.len() > 3 {
            violations += (onset.len() - 3) as u32;
        } else if onset.len() == 3 {
            if !legal_onset_triple(onset[0], onset[1], onset[2]) {
                violations += 1;
            }
        } else if onset.len() == 2 {
            if !legal_onset_cluster(onset[0], onset[1]) {
                violations += 1;
            }
        }
    }

    violations
}

// ── Phonemic edit distance ──────────────────────────────────────────────

pub fn phonemic_edit_distance(a: &[String], b: &[String]) -> u32 {
    let m = a.len();
    let n = b.len();
    let mut dp = vec![0u32; n + 1];
    for j in 0..=n { dp[j] = j as u32; }

    for i in 1..=m {
        let mut prev = dp[0];
        dp[0] = i as u32;
        for j in 1..=n {
            let tmp = dp[j];
            if a[i - 1] == b[j - 1] {
                dp[j] = prev;
            } else {
                dp[j] = 1 + prev.min(dp[j]).min(dp[j - 1]);
            }
            prev = tmp;
        }
    }
    dp[n]
}

// ── Data structures (JSON interchange with Python) ──────────────────────

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct CandidateData {
    pub concept: String,
    pub source_lang: String,
    pub source_word: String,
    pub ipa: String,
    #[serde(alias = "lacyo_phonemes")]
    pub vulgultra_phonemes: Vec<String>,
    pub orthography: String,
    pub syllables: u32,
    pub violations: u32,
    #[serde(default = "default_support")]
    pub support: u32,
}

fn default_support() -> u32 {
    1
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct EndingCatalog {
    pub noun_slots: Vec<String>,
    pub verb_slots: Vec<String>,
    pub noun_blocks: HashMap<String, Vec<Vec<String>>>,
    pub verb_blocks: HashMap<String, Vec<Vec<String>>>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct PipelineInput {
    pub concepts: HashMap<String, Vec<CandidateData>>,
    #[serde(default)]
    pub ending_catalog: Option<EndingCatalog>,
}

// ── Ending paradigm slots ───────────────────────────────────────────────

pub const NOUN_SLOTS: &[&str] = &[
    "m_nom_sg", "m_acc_sg", "m_gen_sg", "m_nom_pl", "m_acc_pl", "m_gen_pl",
    "f_nom_sg", "f_acc_sg", "f_gen_sg", "f_nom_pl", "f_acc_pl", "f_gen_pl",
];

pub fn verb_slots() -> Vec<String> {
    let mut slots = Vec::new();
    for tense in &["prs", "pst", "fut"] {
        for person in &["1", "2", "3"] {
            for number in &["sg", "pl"] {
                slots.push(format!("{}_{}{}", tense, person, number));
            }
        }
    }
    for tense in &["prs", "pst", "fut"] {
        for person in &["1", "2", "3"] {
            for number in &["sg", "pl"] {
                slots.push(format!("{}_subj_{}{}", tense, person, number));
            }
        }
    }
    slots.extend(["inf", "ptcp_act", "ptcp_pas", "imp_2sg", "imp_2pl"]
        .iter().map(|s| s.to_string()));
    slots
}

pub const ADJ_SLOTS: &[&str] = NOUN_SLOTS;

fn parse_ortho(s: &str) -> Vec<String> {
    s.chars().map(|ch| match ch {
        'x' => "ʃ".to_string(),
        'c' => "t͡ʃ".to_string(),
        'g' => "ɡ".to_string(),
        other => other.to_string(),
    }).collect()
}

fn clip_one_sigma(seq: Vec<String>) -> Vec<String> {
    let syls = syllabify(&seq);
    match syls.last() {
        Some(idxs) if !idxs.is_empty() => idxs.iter().map(|&i| seq[i].clone()).collect(),
        _ => seq,
    }
}

fn fuse_cell(theme: &str, person: &str) -> Vec<String> {
    let raw = if theme.is_empty() {
        parse_ortho(person)
    } else {
        let cell = if person.chars().count() > 1 {
            format!("{}{}", theme, person.chars().last().unwrap())
        } else {
            format!("{}{}", theme, person)
        };
        parse_ortho(&cell)
    };
    clip_one_sigma(raw)
}

fn verb_block(persons: &[&str], pst: &str, fut: &str, subj: &str) -> Vec<Vec<String>> {
    let mut out = Vec::new();
    for theme in ["", pst, fut] {
        for p in persons {
            out.push(fuse_cell(theme, p));
        }
    }
    for p in persons { out.push(fuse_cell(subj, p)); }
    for p in persons { out.push(fuse_cell("i", p)); }
    for p in persons { out.push(fuse_cell("a", p)); }
    for nf in ["r", "nt", "t", "a", "e"] {
        out.push(parse_ortho(nf));
    }
    out
}

/// Whole-language conjugation tables. Never mix slots across sources.
pub fn verb_templates() -> Vec<Vec<Vec<String>>> {
    // person order: 1sg 1pl 2sg 2pl 3sg 3pl (matches verb_slots)
    vec![
        verb_block(&["o", "mos", "as", "is", "a", "an"], "i", "ra", "e"), // es
        verb_block(&["o", "mos", "as", "is", "a", "am"], "i", "ra", "e"), // pt
        verb_block(&["o", "am", "i", "at", "a", "an"], "e", "re", "i"),   // it
        verb_block(&["o", "em", "es", "ew", "a", "en"], "i", "re", "i"),  // ca
        verb_block(&["e", "on", "es", "e", "e", "et"], "e", "ra", "i"),   // fr
    ]
}

fn case_block(m: &str, f: &str, m_acc_pl: &str, f_acc_pl: &str) -> Vec<Vec<String>> {
    let with_vowel = |cell: &str, theme: &str| -> String {
        if cell.chars().any(|ch| "aeiou".contains(ch)) {
            cell.to_string()
        } else {
            format!("{}{}", theme, cell)
        }
    };
    let acc_sg = |theme: &str| -> String {
        let last = theme.chars().last().unwrap_or('x');
        if !"aeiou".contains(last) {
            let mut cs: String = theme.chars().collect();
            cs.pop();
            cs.push('n');
            cs
        } else {
            format!("{theme}n")
        }
    };
    let mpl = with_vowel(m_acc_pl, m);
    let fpl = with_vowel(f_acc_pl, f);
    let cells = [
        m.to_string(), acc_sg(m), "is".into(), "i".into(), mpl, "or".into(),
        f.to_string(), acc_sg(f), "es".into(), "e".into(), fpl, "ar".into(),
    ];
    cells.into_iter().map(|c| clip_one_sigma(parse_ortho(&c))).collect()
}

/// Reverse-VL case on a lect theme: 12 slots (gender × case × number).
pub fn noun_templates() -> Vec<Vec<Vec<String>>> {
    vec![
        case_block("o", "a", "os", "as"), // es/pt/it
        case_block("u", "a", "os", "as"), // ast/sc/ro
        case_block("e", "a", "s", "es"),  // ca/oc
        case_block("e", "a", "s", "s"),   // fr/oil
    ]
}

pub fn adj_templates() -> Vec<Vec<Vec<String>>> {
    noun_templates()
}

// ── Legal endings pool ──────────────────────────────────────────────────

pub fn generate_legal_endings() -> Vec<Vec<String>> {
    let mut endings: Vec<Vec<String>> = Vec::new();
    let vowels = VOWELS;
    let codas = LEGAL_CODAS;
    let onsets: Vec<&str> = CONSONANTS.iter()
        .filter(|&&c| c != "w")
        .copied()
        .collect();

    // V
    for &v in vowels {
        endings.push(vec![v.to_string()]);
    }
    // CV
    for &c in &onsets {
        for &v in vowels {
            endings.push(vec![c.to_string(), v.to_string()]);
        }
    }
    // VC
    for &v in vowels {
        for &cd in codas {
            endings.push(vec![v.to_string(), cd.to_string()]);
        }
    }
    // CVC
    for &c in &onsets {
        for &v in vowels {
            for &cd in codas {
                endings.push(vec![c.to_string(), v.to_string(), cd.to_string()]);
            }
        }
    }

    endings
}

// ── Genome state (mutable only — candidates stored separately) ──────────

#[derive(Clone)]
pub struct Genome {
    /// concept index → index into candidate list for that concept
    pub selections: Vec<usize>,
    /// concept_ids in order (parallel to selections)
    pub concept_ids: Vec<String>,
    /// Noun endings: class → slot → phoneme seq
    pub noun_endings: Vec<Vec<Vec<String>>>,   // [class][slot][phonemes]
    /// Verb endings: class → slot → phoneme seq
    pub verb_endings: Vec<Vec<Vec<String>>>,
    /// Adj endings: slot → phoneme seq. Copy of the noun table; not scored twice.
    pub adj_endings: Vec<Vec<String>>,
    pub noun_theme: String,
    pub verb_lect: String,
}

/// Immutable candidate database (never cloned during SA)
pub struct CandidateDB {
    /// concept_id → candidates list (same order as genome.concept_ids)
    pub by_index: Vec<Vec<CandidateData>>,
}

impl CandidateDB {
    pub fn from_input(input: &PipelineInput, concept_ids: &[String]) -> Self {
        let by_index: Vec<Vec<CandidateData>> = concept_ids.iter()
            .map(|cid| input.concepts[cid].clone())
            .collect();
        CandidateDB { by_index }
    }

    #[inline]
    pub fn get(&self, concept_idx: usize, selection: usize) -> &CandidateData {
        &self.by_index[concept_idx][selection]
    }

    #[inline]
    pub fn n_candidates(&self, concept_idx: usize) -> usize {
        self.by_index[concept_idx].len()
    }
}

impl Genome {
    pub fn get_root<'a>(&self, idx: usize, db: &'a CandidateDB) -> &'a CandidateData {
        db.get(idx, self.selections[idx])
    }

    pub fn n_concepts(&self) -> usize {
        self.concept_ids.len()
    }
}

// ── Energy weights (grammar.tex Ch.4) ───────────────────────────────────

// Lexicographic: 23*W_PHON < W_SYL, |L|*W_DIV < W_PHON, mean-support*W_NORM < W_DIV.
// |L| = SOURCE_LANGS (daughters only). Keep in lockstep with romance_swadesh.py.
pub const W_SYL: f64  = 1000.0;
pub const W_PHON: f64 = 40.0;     // global min |Φ|; 40*23 = 920 < 1000
pub const W_DIV: f64  = 1.0;      // σ-and-Φ tie: max distinct source lects
pub const W_NORM: f64 = 0.02;     // *mean* support gap (finer than one lect)
pub const N_SOURCES: f64 = 36.0;
pub const W_END: f64  = 200.0;
pub const W_COLL: f64 = 100_000.0;
pub const W_TACT: f64 = 2000.0; // leftover after repair; not a donor-glitch death
pub const W_DIST: f64 = 500.0;
pub const DIST_THRESHOLD: u32 = 2;

#[derive(Clone, Debug, Serialize)]
pub struct EnergyBreakdown {
    pub e_root: f64,
    pub e_phon: f64,
    pub e_div: f64,
    pub e_norm: f64,
    pub e_end: f64,
    pub e_coll: f64,
    pub e_tact: f64,
    pub e_dist: f64,
    pub total: f64,
}

/// Full energy computation (used once at init and for final output).
pub fn compute_energy(genome: &Genome, db: &CandidateDB) -> EnergyBreakdown {
    let mut root_syls = 0u64;
    let mut all_phonemes: HashSet<String> = HashSet::new();
    let mut root_viols = 0u64;

    let mut support_gap = 0u64;
    let mut lects: HashSet<String> = HashSet::new();
    let n = genome.n_concepts().max(1);
    for i in 0..genome.n_concepts() {
        let r = genome.get_root(i, db);
        root_syls += r.syllables as u64;
        root_viols += r.violations as u64;
        let s = r.support.max(1);
        if (s as f64) < N_SOURCES {
            support_gap += (N_SOURCES as u64) - s as u64;
        }
        lects.insert(r.source_lang.clone());
        for p in &r.vulgultra_phonemes {
            all_phonemes.insert(p.clone());
        }
    }
    let e_root = W_SYL * root_syls as f64;
    let e_div = W_DIV * (N_SOURCES - lects.len() as f64).max(0.0);
    let e_norm = W_NORM * (support_gap as f64) / (n as f64);

    let mut end_syls = 0u64;
    let mut end_viols = 0u64;

    let all_ending_seqs = collect_all_endings(genome);
    for seq in &all_ending_seqs {
        end_syls += count_syllables(seq) as u64;
        end_viols += count_violations(seq) as u64;
        for p in *seq {
            all_phonemes.insert(p.clone());
        }
    }

    let e_phon = W_PHON * all_phonemes.len() as f64;
    let e_end = W_END * end_syls as f64;
    let e_tact = W_TACT * (root_viols + end_viols) as f64;

    let e_coll = W_COLL * count_ending_collisions(genome) as f64;
    let e_dist = W_DIST * count_dist_penalty(genome);

    let total = e_root + e_phon + e_div + e_norm + e_end + e_coll + e_tact + e_dist;

    EnergyBreakdown { e_root, e_phon, e_div, e_norm, e_end, e_coll, e_tact, e_dist, total }
}

fn count_ending_collisions(genome: &Genome) -> u64 {
    let mut collisions = 0u64;
    for cls in &genome.noun_endings {
        for i in 0..cls.len() {
            for j in (i + 1)..cls.len() {
                if cls[i] == cls[j] { collisions += 1; }
            }
        }
    }
    // Verbs: collision only inside a 6-person row (cross-tense syncretism is legal).
    for cls in &genome.verb_endings {
        let finite = cls.len().min(36);
        for start in (0..finite).step_by(6) {
            let end = (start + 6).min(finite);
            for i in start..end {
                for j in (i + 1)..end {
                    if cls[i] == cls[j] { collisions += 1; }
                }
            }
        }
        for i in finite..cls.len() {
            for j in (i + 1)..cls.len() {
                if cls[i] == cls[j] { collisions += 1; }
            }
        }
    }
    collisions
}

fn count_dist_penalty(genome: &Genome) -> f64 {
    // d ≥ 2 inside each finite 6-person row. Noun minimal pairs (-o/-on/-os) are not taxed.
    let mut penalty = 0.0f64;
    for cls in &genome.verb_endings {
        let finite = cls.len().min(36);
        let mut start = 0;
        while start < finite {
            let end = (start + 6).min(finite);
            for i in start..end {
                for j in (i + 1)..end {
                    let d = phonemic_edit_distance(&cls[i], &cls[j]);
                    if d < DIST_THRESHOLD { penalty += (DIST_THRESHOLD - d) as f64; }
                }
            }
            start += 6;
        }
    }
    penalty
}

fn collect_all_endings(genome: &Genome) -> Vec<&Vec<String>> {
    // Noun table once. Adjectives are a copy and must not double E_end or |Φ| counts
    // of ending tokens (the set is unchanged, the syllable sum is not).
    let mut out: Vec<&Vec<String>> = Vec::new();
    for cls in &genome.noun_endings {
        for seq in cls { out.push(seq); }
    }
    for cls in &genome.verb_endings {
        for seq in cls { out.push(seq); }
    }
    out
}

// ── Cached energy state for incremental updates ─────────────────────────

/// Maintains running totals so we can do O(1) delta updates per mutation.
pub struct EnergyCache {
    pub total_root_syls: u64,
    pub total_root_viols: u64,
    pub total_support_gap: u64,
    pub n_roots: usize,
    /// phoneme → count of roots+endings using it
    pub phoneme_counts: HashMap<String, u32>,
    pub n_phonemes: usize,
    /// source lect → how many selected roots
    pub lang_counts: HashMap<String, u32>,
    pub n_lects: usize,
    pub total_end_syls: u64,
    pub total_end_viols: u64,
    pub ending_collisions: u64,
    pub ending_dist_penalty: f64,
}

impl EnergyCache {
    pub fn from_genome(genome: &Genome, db: &CandidateDB) -> Self {
        let mut total_root_syls = 0u64;
        let mut total_root_viols = 0u64;
        let mut total_support_gap = 0u64;
        let mut phoneme_counts: HashMap<String, u32> = HashMap::new();
        let mut lang_counts: HashMap<String, u32> = HashMap::new();

        for i in 0..genome.n_concepts() {
            let r = genome.get_root(i, db);
            total_root_syls += r.syllables as u64;
            total_root_viols += r.violations as u64;
            let s = r.support.max(1);
            if (s as f64) < N_SOURCES {
                total_support_gap += (N_SOURCES as u64) - s as u64;
            }
            *lang_counts.entry(r.source_lang.clone()).or_insert(0) += 1;
            for p in &r.vulgultra_phonemes {
                *phoneme_counts.entry(p.clone()).or_insert(0) += 1;
            }
        }

        // Add ending phonemes
        let all_endings = collect_all_endings(genome);
        let mut total_end_syls = 0u64;
        let mut total_end_viols = 0u64;
        for seq in &all_endings {
            total_end_syls += count_syllables(seq) as u64;
            total_end_viols += count_violations(seq) as u64;
            for p in *seq {
                *phoneme_counts.entry(p.clone()).or_insert(0) += 1;
            }
        }

        let n_phonemes = phoneme_counts.values().filter(|&&c| c > 0).count();
        let n_lects = lang_counts.values().filter(|&&c| c > 0).count();

        EnergyCache {
            total_root_syls,
            total_root_viols,
            total_support_gap,
            n_roots: genome.n_concepts(),
            phoneme_counts,
            n_phonemes,
            lang_counts,
            n_lects,
            total_end_syls,
            total_end_viols,
            ending_collisions: count_ending_collisions(genome),
            ending_dist_penalty: count_dist_penalty(genome),
        }
    }

    pub fn tiers(&self) -> (u64, usize, usize, f64, f64) {
        let n = self.n_roots.max(1) as f64;
        let gap = self.total_support_gap as f64 / n;
        (self.total_root_syls, self.n_phonemes, self.n_lects, gap, self.energy())
    }

    pub fn energy(&self) -> f64 {
        let e_root = W_SYL * self.total_root_syls as f64;
        let e_phon = W_PHON * self.n_phonemes as f64;
        let e_div = W_DIV * (N_SOURCES - self.n_lects as f64).max(0.0);
        let n = self.n_roots.max(1) as f64;
        let e_norm = W_NORM * (self.total_support_gap as f64) / n;
        let e_end = W_END * self.total_end_syls as f64;
        let e_tact = W_TACT * (self.total_root_viols + self.total_end_viols) as f64;
        let e_coll = W_COLL * self.ending_collisions as f64;
        let e_dist = W_DIST * self.ending_dist_penalty;
        e_root + e_phon + e_div + e_norm + e_end + e_coll + e_tact + e_dist
    }

    fn add_phonemes(&mut self, phonemes: &[String]) {
        for p in phonemes {
            let count = self.phoneme_counts.entry(p.clone()).or_insert(0);
            if *count == 0 { self.n_phonemes += 1; }
            *count += 1;
        }
    }

    fn remove_phonemes(&mut self, phonemes: &[String]) {
        for p in phonemes {
            if let Some(count) = self.phoneme_counts.get_mut(p) {
                *count -= 1;
                if *count == 0 { self.n_phonemes -= 1; }
            }
        }
    }

    /// Update cache after a root selection change.
    /// `old_root` / `new_root` are the candidate data before/after.
    fn support_gap(root: &CandidateData) -> u64 {
        let s = root.support.max(1);
        if (s as f64) < N_SOURCES {
            (N_SOURCES as u64) - s as u64
        } else {
            0
        }
    }

    fn add_lang(&mut self, lang: &str) {
        let count = self.lang_counts.entry(lang.to_string()).or_insert(0);
        if *count == 0 { self.n_lects += 1; }
        *count += 1;
    }

    fn remove_lang(&mut self, lang: &str) {
        if let Some(count) = self.lang_counts.get_mut(lang) {
            *count -= 1;
            if *count == 0 { self.n_lects -= 1; }
        }
    }

    pub fn update_root(&mut self, old_root: &CandidateData, new_root: &CandidateData) {
        self.total_root_syls = self.total_root_syls - old_root.syllables as u64 + new_root.syllables as u64;
        self.total_root_viols = self.total_root_viols - old_root.violations as u64 + new_root.violations as u64;
        self.total_support_gap = self.total_support_gap - Self::support_gap(old_root) + Self::support_gap(new_root);
        self.remove_phonemes(&old_root.vulgultra_phonemes);
        self.add_phonemes(&new_root.vulgultra_phonemes);
        self.remove_lang(&old_root.source_lang);
        self.add_lang(&new_root.source_lang);
    }

    /// Undo a root change (just call update_root with args swapped)
    pub fn undo_root(&mut self, old_root: &CandidateData, new_root: &CandidateData) {
        self.update_root(new_root, old_root);
    }

    /// Update cache after an ending change. We just recompute all ending
    /// metrics since endings are small (< 50 slots total).
    pub fn update_endings(&mut self, genome: &Genome, old_ending: &[String], new_ending: &[String]) {
        // Update phoneme counts
        self.remove_phonemes(old_ending);
        self.add_phonemes(new_ending);

        // Recompute end syls/viols (fast: ~50 endings)
        let all_endings = collect_all_endings(genome);
        self.total_end_syls = 0;
        self.total_end_viols = 0;
        for seq in &all_endings {
            self.total_end_syls += count_syllables(seq) as u64;
            self.total_end_viols += count_violations(seq) as u64;
        }

        // Recompute collisions and dist (fast: ~50 endings)
        self.ending_collisions = count_ending_collisions(genome);
        self.ending_dist_penalty = count_dist_penalty(genome);
    }

    /// Undo an ending change
    pub fn undo_endings(&mut self, genome: &Genome, old_ending: &[String], new_ending: &[String]) {
        self.remove_phonemes(new_ending);
        self.add_phonemes(old_ending);

        let all_endings = collect_all_endings(genome);
        self.total_end_syls = 0;
        self.total_end_viols = 0;
        for seq in &all_endings {
            self.total_end_syls += count_syllables(seq) as u64;
            self.total_end_viols += count_violations(seq) as u64;
        }
        self.ending_collisions = count_ending_collisions(genome);
        self.ending_dist_penalty = count_dist_penalty(genome);
    }
}

fn greedy_root_selections(db: &CandidateDB) -> Vec<usize> {
    let n = db.by_index.len();
    if n == 0 {
        return vec![];
    }
    let mut slice: Vec<Vec<usize>> = Vec::with_capacity(n);
    for i in 0..n {
        let cands = &db.by_index[i];
        let best = cands.iter()
            .map(|c| (c.violations, c.syllables))
            .min()
            .unwrap_or((0, 0));
        let idxs: Vec<usize> = cands.iter().enumerate()
            .filter(|(_, c)| (c.violations, c.syllables) == best)
            .map(|(j, _)| j)
            .collect();
        slice.push(if idxs.is_empty() { vec![0] } else { idxs });
    }
    let mut order: Vec<usize> = (0..n).collect();
    order.sort_by(|&a, &b| {
        slice[a].len().cmp(&slice[b].len()).then_with(|| {
            let ca = db.by_index[a].first().map(|c| c.concept.as_str()).unwrap_or("");
            let cb = db.by_index[b].first().map(|c| c.concept.as_str()).unwrap_or("");
            ca.cmp(cb)
        })
    });

    let mut used_phon: HashSet<String> = HashSet::new();
    let mut used_lang: HashSet<String> = HashSet::new();
    let mut selections = vec![0usize; n];

    for i in order {
        let best_j = slice[i].iter().copied().min_by_key(|j| {
            let c = &db.by_index[i][*j];
            let new_ph = c.vulgultra_phonemes.iter().filter(|p| !used_phon.contains(*p)).count();
            let new_lang: u8 = if used_lang.contains(&c.source_lang) { 1 } else { 0 };
            (new_ph, new_lang, std::cmp::Reverse(c.support), c.vulgultra_phonemes.len(), c.source_lang.clone())
        }).unwrap_or(0);
        selections[i] = best_j;
        let c = &db.by_index[i][best_j];
        for p in &c.vulgultra_phonemes {
            used_phon.insert(p.clone());
        }
        used_lang.insert(c.source_lang.clone());
    }
    selections
}

fn slice_indices(cands: &[CandidateData]) -> Vec<usize> {
    let Some(best) = cands.iter().map(|c| (c.violations, c.syllables)).min() else {
        return vec![];
    };
    cands.iter().enumerate()
        .filter(|(_, c)| (c.violations, c.syllables) == best)
        .map(|(i, _)| i)
        .collect()
}

const FINITE_ROW_NAMES: [&str; 6] = ["prs", "pst", "fut", "subj", "theme_i", "theme_a"];

fn row_pair_collisions(row: &[Vec<String>]) -> u64 {
    let mut n = 0u64;
    for i in 0..row.len() {
        for j in (i + 1)..row.len() {
            if row[i] == row[j] { n += 1; }
        }
    }
    n
}

/// Score one 6-person row. Lower is better. Matches Python `_row_score` key order.
fn row_score(
    row: &[Vec<String>],
    phonemes: &HashSet<String>,
    used_lects: &[String],
    lang: &str,
) -> (u64, u64, u32, usize, u8, String) {
    let collisions = row_pair_collisions(row);
    let violations: u64 = row.iter().map(|cell| count_violations(cell) as u64).sum();
    let mut dist = 0u32;
    for i in 0..row.len() {
        for j in (i + 1)..row.len() {
            let d = phonemic_edit_distance(&row[i], &row[j]);
            if d < DIST_THRESHOLD {
                dist += DIST_THRESHOLD - d;
            }
        }
    }
    let mut fresh: HashSet<String> = HashSet::new();
    for cell in row {
        for p in cell {
            fresh.insert(p.clone());
        }
    }
    let new_ph = fresh.iter().filter(|p| !phonemes.contains(*p)).count();
    let already: u8 = if used_lects.iter().any(|l| l == lang) { 1 } else { 0 };
    (collisions, violations, dist, new_ph, already, lang.to_string())
}

/// Each finite tense is the lect that wins that row. Non-finite tail is shared.
fn assemble_verb_rows(
    catalog: &EndingCatalog,
    phonemes: &HashSet<String>,
) -> Result<(Vec<Vec<String>>, String), String> {
    let mut langs: Vec<&String> = catalog.verb_blocks.keys().collect();
    langs.sort();
    if langs.is_empty() {
        return Err("ending catalog has no verb blocks".into());
    }
    let mut used = phonemes.clone();
    let mut used_lects: Vec<String> = Vec::new();
    let mut labels: Vec<String> = Vec::new();
    let mut cells: Vec<Vec<String>> = Vec::new();
    for (r, name) in FINITE_ROW_NAMES.iter().enumerate() {
        let start = r * 6;
        let mut best: Option<(u64, u64, u32, usize, u8, String)> = None;
        let mut best_row: Vec<Vec<String>> = Vec::new();
        for lang in &langs {
            let block = &catalog.verb_blocks[*lang];
            if block.len() < start + 6 {
                return Err(format!("verb block {lang} has {} cells, need {}", block.len(), start + 6));
            }
            let row = &block[start..start + 6];
            let key = row_score(row, &used, &used_lects, lang);
            if best.as_ref().map(|b| key < *b).unwrap_or(true) {
                best = Some(key);
                best_row = row.to_vec();
            }
        }
        let winner = best.ok_or("no verb row")?;
        for cell in &best_row {
            for p in cell {
                used.insert(p.clone());
            }
        }
        used_lects.push(winner.5.clone());
        labels.push(format!("{name}={}", winner.5));
        cells.extend(best_row);
    }
    let tail_lang = langs[0];
    let tail = &catalog.verb_blocks[tail_lang];
    if tail.len() < 41 {
        return Err(format!("verb block {tail_lang} has {} cells, expected 41", tail.len()));
    }
    cells.extend(tail[36..].iter().cloned());
    Ok((cells, labels.join(",")))
}

/// Noun theme is global. Each verb tense is its own row. Roots stay pinned.
pub fn enumerate_endings(
    catalog: &EndingCatalog,
    selections: &[usize],
    concept_ids: &[String],
    db: &CandidateDB,
) -> Result<(Vec<Vec<String>>, Vec<Vec<String>>, String, String), String> {
    let mut noun_names: Vec<&String> = catalog.noun_blocks.keys().collect();
    noun_names.sort();
    if noun_names.is_empty() {
        return Err("ending catalog has no noun blocks".into());
    }

    let mut root_ph: HashSet<String> = HashSet::new();
    for (i, &sel) in selections.iter().enumerate() {
        for p in &db.get(i, sel).vulgultra_phonemes {
            root_ph.insert(p.clone());
        }
    }

    let mut best_key: Option<(i64, String, String)> = None;
    let mut best_noun: Vec<Vec<String>> = Vec::new();
    let mut best_verb: Vec<Vec<String>> = Vec::new();
    let mut best_nname = String::new();
    let mut best_vname = String::new();

    for nname in noun_names {
        let ncells = &catalog.noun_blocks[nname];
        if ncells.len() != catalog.noun_slots.len() {
            return Err(format!(
                "noun block {nname} has {} cells, expected {}",
                ncells.len(),
                catalog.noun_slots.len()
            ));
        }
        let mut noun_ph = root_ph.clone();
        for cell in ncells {
            for p in cell {
                noun_ph.insert(p.clone());
            }
        }
        let (vcells, verb_label) = assemble_verb_rows(catalog, &noun_ph)?;
        let trial = Genome {
            selections: selections.to_vec(),
            concept_ids: concept_ids.to_vec(),
            noun_endings: vec![ncells.clone()],
            verb_endings: vec![vcells.clone()],
            adj_endings: ncells.clone(),
            noun_theme: nname.clone(),
            verb_lect: verb_label.clone(),
        };
        let energy = compute_energy(&trial, db).total;
        let energy_key = (energy * 1000.0).round() as i64;
        let key = (energy_key, nname.clone(), verb_label.clone());
        if best_key.as_ref().map(|b| key < *b).unwrap_or(true) {
            best_key = Some(key);
            best_noun = ncells.clone();
            best_verb = vcells;
            best_nname = nname.clone();
            best_vname = verb_label;
        }
    }

    Ok((best_noun, best_verb, best_nname, best_vname))
}

// ── Genome initialization ───────────────────────────────────────────────

pub fn init_genome(input: &PipelineInput) -> Result<(Genome, CandidateDB), String> {
    let catalog = input.ending_catalog.as_ref()
        .ok_or("candidates JSON has no ending_catalog; re-run prep")?;
    let mut concept_ids: Vec<String> = input.concepts.keys().cloned().collect();
    concept_ids.sort();
    let db = CandidateDB::from_input(input, &concept_ids);
    let selections = greedy_root_selections(&db);
    let (noun, verb, noun_theme, verb_lect) = enumerate_endings(catalog, &selections, &concept_ids, &db)?;
    let genome = Genome {
        selections,
        concept_ids,
        adj_endings: noun.clone(),
        noun_endings: vec![noun],
        verb_endings: vec![verb],
        noun_theme,
        verb_lect,
    };
    Ok((genome, db))
}

// ── Mutation with undo ──────────────────────────────────────────────────

/// Describes what was mutated so it can be undone.
pub enum MutationUndo {
    Root { concept_idx: usize, old_selection: usize },
}

/// Swap one concept to another stem in its minimum-(violations, σ) slice.
pub fn mutate_in_place(
    genome: &mut Genome,
    db: &CandidateDB,
    cache: &mut EnergyCache,
    rng: &mut impl rand::Rng,
) -> MutationUndo {
    let n = genome.n_concepts();
    let movable: Vec<usize> = (0..n)
        .filter(|&i| slice_indices(&db.by_index[i]).len() > 1)
        .collect();
    if movable.is_empty() || n == 0 {
        return MutationUndo::Root { concept_idx: 0, old_selection: genome.selections.first().copied().unwrap_or(0) };
    }
    let idx = movable[rng.gen_range(0..movable.len())];
    let old_sel = genome.selections[idx];
    let options: Vec<usize> = slice_indices(&db.by_index[idx])
        .into_iter()
        .filter(|&j| j != old_sel)
        .collect();
    let new_sel = options[rng.gen_range(0..options.len())];
    let old_root = db.get(idx, old_sel);
    let new_root = db.get(idx, new_sel);
    genome.selections[idx] = new_sel;
    cache.update_root(old_root, new_root);
    MutationUndo::Root { concept_idx: idx, old_selection: old_sel }
}

/// Revert a mutation using undo info.
pub fn undo_mutation(
    genome: &mut Genome,
    db: &CandidateDB,
    cache: &mut EnergyCache,
    undo: MutationUndo,
) {
    match undo {
        MutationUndo::Root { concept_idx, old_selection } => {
            if genome.selections.is_empty() {
                return;
            }
            let current_sel = genome.selections[concept_idx];
            if current_sel == old_selection {
                return;
            }
            let current_root = db.get(concept_idx, current_sel);
            let old_root = db.get(concept_idx, old_selection);
            cache.undo_root(old_root, current_root);
            genome.selections[concept_idx] = old_selection;
        }
    }
}

// ── Output format ───────────────────────────────────────────────────────

#[derive(Serialize)]
pub struct LexiconOutput {
    pub version: String,
    pub metadata: OutputMetadata,
    pub energy_breakdown: EnergyBreakdown,
    pub phoneme_inventory: Vec<String>,
    pub phoneme_count: usize,
    pub roots: HashMap<String, RootOutput>,
    pub noun_endings: HashMap<String, HashMap<String, String>>,
    pub verb_endings: HashMap<String, HashMap<String, String>>,
    pub adj_endings: HashMap<String, String>,
}

#[derive(Serialize)]
pub struct OutputMetadata {
    pub total_concepts: usize,
    pub total_energy: f64,
    pub initial_energy: f64,
    pub iterations: u64,
    pub acceptance_rate: f64,
    pub noun_theme: String,
    pub verb_lect: String,
}

#[derive(Serialize)]
pub struct RootOutput {
    pub ipa: Vec<String>,
    pub orthography: String,
    pub source_lang: String,
    pub source_word: String,
    pub syllables: u32,
    pub violations: u32,
}

pub fn format_output(
    genome: &Genome,
    db: &CandidateDB,
    breakdown: &EnergyBreakdown,
    iterations: u64,
    accepted: u64,
    initial_energy: f64,
) -> LexiconOutput {
    let mut all_phonemes: HashSet<String> = HashSet::new();
    let mut roots: HashMap<String, RootOutput> = HashMap::new();

    for i in 0..genome.n_concepts() {
        let r = genome.get_root(i, db);
        for p in &r.vulgultra_phonemes {
            all_phonemes.insert(p.clone());
        }
        roots.insert(genome.concept_ids[i].clone(), RootOutput {
            ipa: r.vulgultra_phonemes.clone(),
            orthography: r.orthography.clone(),
            source_lang: r.source_lang.clone(),
            source_word: r.source_word.clone(),
            syllables: r.syllables,
            violations: r.violations,
        });
    }

    let mut noun_out: HashMap<String, HashMap<String, String>> = HashMap::new();
    for (ci, cls) in genome.noun_endings.iter().enumerate() {
        let mut m = HashMap::new();
        for (si, seq) in cls.iter().enumerate() {
            for p in seq { all_phonemes.insert(p.clone()); }
            let slot_name = NOUN_SLOTS.get(si).unwrap_or(&"?");
            m.insert(slot_name.to_string(), phonemes_to_ortho(seq));
        }
        noun_out.insert(format!("class_{}", ci + 1), m);
    }

    let v_slots = verb_slots();
    let mut verb_out: HashMap<String, HashMap<String, String>> = HashMap::new();
    for (ci, cls) in genome.verb_endings.iter().enumerate() {
        let mut m = HashMap::new();
        for (si, seq) in cls.iter().enumerate() {
            for p in seq { all_phonemes.insert(p.clone()); }
            let slot_name = v_slots.get(si).map(|s| s.as_str()).unwrap_or("?");
            m.insert(slot_name.to_string(), phonemes_to_ortho(seq));
        }
        verb_out.insert(format!("class_{}", ci + 1), m);
    }

    let mut adj_out: HashMap<String, String> = HashMap::new();
    for (si, seq) in genome.adj_endings.iter().enumerate() {
        for p in seq { all_phonemes.insert(p.clone()); }
        let slot_name = ADJ_SLOTS.get(si).unwrap_or(&"?");
        adj_out.insert(slot_name.to_string(), phonemes_to_ortho(seq));
    }

    let mut phon_sorted: Vec<String> = all_phonemes.into_iter().collect();
    phon_sorted.sort();

    LexiconOutput {
        version: "2.0".to_string(),
        metadata: OutputMetadata {
            total_concepts: genome.n_concepts(),
            total_energy: breakdown.total,
            initial_energy,
            iterations,
            acceptance_rate: if iterations > 0 { accepted as f64 / iterations as f64 } else { 0.0 },
            noun_theme: genome.noun_theme.clone(),
            verb_lect: genome.verb_lect.clone(),
        },
        energy_breakdown: breakdown.clone(),
        phoneme_inventory: phon_sorted.clone(),
        phoneme_count: phon_sorted.len(),
        roots,
        noun_endings: noun_out,
        verb_endings: verb_out,
        adj_endings: adj_out,
    }
}

// ── Tests ───────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use rand::SeedableRng;

    #[test]
    fn test_lexicographic_weights() {
        assert!(W_PHON * 23.0 < W_SYL);
        assert!(W_DIV * N_SOURCES < W_PHON);
        assert!(W_NORM * 33.0 < W_DIV);
    }

    #[test]
    fn test_count_syllables_ipa() {
        let seq: Vec<String> = vec!["r", "u", "ʃ"].into_iter().map(String::from).collect();
        assert_eq!(count_syllables(&seq), 1);

        let seq: Vec<String> = vec!["a", "k", "w", "a"].into_iter().map(String::from).collect();
        assert_eq!(count_syllables(&seq), 2);
    }

    #[test]
    fn test_violations_clean() {
        let seq: Vec<String> = vec!["t", "a", "r", "e"].into_iter().map(String::from).collect();
        assert_eq!(count_violations(&seq), 0);
    }

    #[test]
    fn test_legal_coda_and_sc_onset() {
        let ak: Vec<String> = vec!["a", "k"].into_iter().map(String::from).collect();
        assert_eq!(count_violations(&ak), 0);

        let sta: Vec<String> = vec!["s", "t", "a"].into_iter().map(String::from).collect();
        assert_eq!(count_violations(&sta), 0);

        let nja: Vec<String> = vec!["n", "j", "a"].into_iter().map(String::from).collect();
        assert_eq!(count_violations(&nja), 0);

        let gem: Vec<String> = ["a", "k", "k", "w", "a"].into_iter().map(String::from).collect();
        assert_eq!(count_violations(&gem), 0);
        assert_eq!(count_syllables(&gem), 2);
    }

    #[test]
    fn test_illegal_onset() {
        let seq: Vec<String> = vec!["p", "t", "a"].into_iter().map(String::from).collect();
        assert!(count_violations(&seq) > 0);
    }

    #[test]
    fn test_edit_distance() {
        let a: Vec<String> = vec!["a", "s"].into_iter().map(String::from).collect();
        let b: Vec<String> = vec!["a", "n"].into_iter().map(String::from).collect();
        assert_eq!(phonemic_edit_distance(&a, &b), 1);
    }

    #[test]
    fn test_ortho() {
        let seq: Vec<String> = vec!["t͡ʃ", "a"].into_iter().map(String::from).collect();
        assert_eq!(phonemes_to_ortho(&seq), "ca");
    }

    fn phon(xs: &[&str]) -> Vec<String> {
        xs.iter().map(|s| (*s).to_string()).collect()
    }

    fn cand(concept: &str, lang: &str, word: &str, phones: &[&str], syl: u32) -> CandidateData {
        CandidateData {
            concept: concept.into(),
            source_lang: lang.into(),
            source_word: word.into(),
            ipa: phones.join(""),
            vulgultra_phonemes: phon(phones),
            orthography: phones.join(""),
            syllables: syl,
            violations: 0,
            support: 1,
        }
    }

    fn fixture_genome() -> (Genome, CandidateDB) {
        let row = [
            phon(&["p", "a"]), phon(&["b", "e"]), phon(&["t", "i"]),
            phon(&["d", "o"]), phon(&["k", "u"]), phon(&["m", "a", "n"]),
        ];
        let mut verb = Vec::new();
        for _ in 0..6 {
            verb.extend(row.iter().cloned());
        }
        verb.extend([
            phon(&["r", "a"]), phon(&["n", "e"]), phon(&["t", "o"]),
            phon(&["a"]), phon(&["e"]),
        ]);
        let noun = vec![
            phon(&["o"]), phon(&["o", "n"]), phon(&["i", "s"]), phon(&["i"]),
            phon(&["o", "s"]), phon(&["o", "r"]), phon(&["a"]), phon(&["a", "n"]),
            phon(&["e", "s"]), phon(&["e"]), phon(&["a", "s"]), phon(&["a", "r"]),
        ];
        let db = CandidateDB {
            by_index: vec![
                vec![cand("c1", "es", "gat", &["ɡ", "a", "t"], 1)],
                vec![cand("c2", "it", "kan", &["k", "a", "n"], 1)],
                vec![cand("c3", "pt", "a", &["a"], 1)],
            ],
        };
        let genome = Genome {
            selections: vec![0, 0, 0],
            concept_ids: vec!["c1".into(), "c2".into(), "c3".into()],
            noun_endings: vec![noun.clone()],
            verb_endings: vec![verb],
            adj_endings: noun,
            noun_theme: "o".into(),
            verb_lect: "fixture".into(),
        };
        (genome, db)
    }

    #[test]
    fn test_energy_fixture_matches_hand_total() {
        let (genome, db) = fixture_genome();
        let bd = compute_energy(&genome, &db);
        assert_eq!(bd.e_root, 3000.0);
        assert_eq!(bd.e_phon, 600.0);
        assert_eq!(bd.e_div, 33.0);
        assert!((bd.e_norm - 0.7).abs() < 1e-9, "e_norm {}", bd.e_norm);
        assert_eq!(bd.e_end, 10600.0);
        assert_eq!(bd.e_coll, 0.0);
        assert_eq!(bd.e_tact, 0.0, "tact {}", bd.e_tact);
        assert_eq!(bd.e_dist, 0.0, "dist {}", bd.e_dist);
        assert!((bd.total - 14233.7).abs() < 1e-6, "total {}", bd.total);
    }

    #[test]
    fn test_mutation_stays_on_sigma_slice() {
        let (mut genome, _) = fixture_genome();
        genome.concept_ids = vec!["c".into()];
        genome.selections = vec![0];
        let db = CandidateDB {
            by_index: vec![vec![
                cand("c", "es", "a", &["a"], 1),
                cand("c", "fr", "ba", &["b", "a"], 2),
                cand("c", "it", "ka", &["k", "a"], 1),
            ]],
        };
        let mut cache = EnergyCache::from_genome(&genome, &db);
        let mut rng = rand::rngs::StdRng::seed_from_u64(7);
        for _ in 0..40 {
            mutate_in_place(&mut genome, &db, &mut cache, &mut rng);
            assert_eq!(genome.get_root(0, &db).syllables, 1);
        }
    }
}
