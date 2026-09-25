use std::collections::HashMap;

use rand::SeedableRng;
use serde_json::json;
use vulgultra_cli::{
    compute_energy, format_output, init_genome, mutate_in_place, CandidateData,
    EndingCatalog, PipelineInput,
};

fn tiny_catalog() -> EndingCatalog {
    let noun_slots = vec![
        "m_nom_sg", "m_acc_sg", "m_gen_sg", "m_nom_pl", "m_acc_pl", "m_gen_pl",
        "f_nom_sg", "f_acc_sg", "f_gen_sg", "f_nom_pl", "f_acc_pl", "f_gen_pl",
    ].into_iter().map(String::from).collect::<Vec<_>>();
    let verb_slots = vulgultra_cli::verb_slots();
    let noun = vec![vec!["a".to_string()]; 12];
    let verb = vec![vec!["a".to_string()]; 41];
    EndingCatalog {
        noun_slots,
        verb_slots,
        noun_blocks: HashMap::from([(String::from("fixture"), noun)]),
        verb_blocks: HashMap::from([(String::from("fixture"), verb)]),
        vowels: vec!["a".into(), "e".into(), "i".into(), "o".into(), "u".into()],
    }
}

fn candidate(concept: &str, word: &str, phones: &[&str], syllables: u32, evidence: &str) -> CandidateData {
    CandidateData {
        concept: concept.into(),
        source_lang: "es".into(),
        source_word: word.into(),
        ipa: word.into(),
        vulgultra_phonemes: phones.iter().map(|p| (*p).into()).collect(),
        orthography: word.into(),
        syllables,
        violations: 0,
        evidence: evidence.into(),
        relation: "direct".into(),
        pos: "noun".into(),
    }
}

fn fixture_input() -> PipelineInput {
    PipelineInput {
        concepts: HashMap::from([(
            "water".into(),
            vec![
                candidate("water", "a", &["a"], 1, "fixture-a"),
                candidate("water", "baba", &["b", "a", "b", "a"], 2, "fixture-long"),
            ],
        )]),
        ending_catalog: Some(tiny_catalog()),
    }
}

#[test]
fn json_schema_and_evidence_are_accepted() {
    let input = json!({
        "schema": "vulgultra.candidates.v2",
        "concepts": {"water": [candidate("water", "a", &["a"], 1, "fixture")]},
        "ending_catalog": tiny_catalog(),
    });
    let parsed: PipelineInput = serde_json::from_value(input).expect("candidate JSON schema");
    assert_eq!(parsed.concepts["water"][0].evidence, "fixture");
}

#[test]
fn initialization_respects_shortest_legal_slice_and_retains_evidence() {
    let input = fixture_input();
    let (genome, db) = init_genome(&input).expect("tiny fixture");
    assert_eq!(genome.get_root(0, &db).syllables, 1);
    assert_eq!(genome.get_root(0, &db).evidence, "fixture-a");
    let output = format_output(&genome, &db, &compute_energy(&genome, &db), 0, 0, 0.0);
    assert_eq!(output.roots["water"].evidence, "fixture-a");
}

#[test]
fn seeded_mutation_is_deterministic() {
    let input = fixture_input();
    let (mut left, left_db) = init_genome(&input).expect("left fixture");
    let (mut right, right_db) = init_genome(&input).expect("right fixture");
    let mut left_cache = vulgultra_cli::EnergyCache::from_genome(&left, &left_db);
    let mut right_cache = vulgultra_cli::EnergyCache::from_genome(&right, &right_db);
    let mut left_rng = rand::rngs::StdRng::seed_from_u64(17);
    let mut right_rng = rand::rngs::StdRng::seed_from_u64(17);
    for _ in 0..20 {
        mutate_in_place(&mut left, &left_db, &mut left_cache, &mut left_rng);
        mutate_in_place(&mut right, &right_db, &mut right_cache, &mut right_rng);
        assert_eq!(left.selections, right.selections);
    }
}
