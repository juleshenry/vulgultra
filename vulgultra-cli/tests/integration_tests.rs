use std::collections::{HashMap, HashSet};

#[test]
fn test_load_tiny_genome() {
    // Test loading the tiny test genome file
    let genome_path = "../data/test_concepts_tiny.clatin";
    
    // This test assumes the file exists - skip if it doesn't
    if !std::path::Path::new(genome_path).exists() {
        eprintln!("Skipping test - genome file not found: {}", genome_path);
        return;
    }
    
    // We can't directly call load_state from main.rs without refactoring,
    // so we'll manually deserialize here for testing
    use std::fs::File;
    use std::io::Read;
    
    let mut file = File::open(genome_path).expect("Failed to open genome file");
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer).expect("Failed to read file");
    
    // Try to deserialize as msgpack
    let result: Result<serde_json::Value, _> = rmp_serde::from_slice(&buffer);
    
    match result {
        Ok(data) => {
            println!("Successfully loaded tiny genome");
            println!("Data structure: {}", serde_json::to_string_pretty(&data).unwrap_or_default());
            
            // Verify it has the expected structure
            assert!(data.get("concepts").is_some(), "Should have 'concepts' field");
            assert!(data.get("choices").is_some(), "Should have 'choices' field");
        }
        Err(e) => {
            panic!("Failed to deserialize genome: {:?}", e);
        }
    }
}

#[test]
fn test_load_small_genome() {
    // Test loading the small test genome file
    let genome_path = "../data/test_concepts_small.clatin";
    
    if !std::path::Path::new(genome_path).exists() {
        eprintln!("Skipping test - genome file not found: {}", genome_path);
        return;
    }
    
    use std::fs::File;
    use std::io::Read;
    
    let mut file = File::open(genome_path).expect("Failed to open genome file");
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer).expect("Failed to read file");
    
    let result: Result<serde_json::Value, _> = rmp_serde::from_slice(&buffer);
    
    match result {
        Ok(data) => {
            println!("Successfully loaded small genome");
            
            // Count concepts
            if let Some(concepts) = data.get("concepts").and_then(|c| c.as_object()) {
                println!("Number of concepts: {}", concepts.len());
                assert!(concepts.len() >= 5, "Small genome should have at least 5 concepts");
            }
        }
        Err(e) => {
            panic!("Failed to deserialize genome: {:?}", e);
        }
    }
}

#[test]
fn test_genome_has_classifications() {
    // Verify that generated genomes include concept classifications
    let genome_path = "../data/test_concepts_tiny.clatin";
    
    if !std::path::Path::new(genome_path).exists() {
        eprintln!("Skipping test - genome file not found: {}", genome_path);
        return;
    }
    
    use std::fs::File;
    use std::io::Read;
    
    let mut file = File::open(genome_path).expect("Failed to open genome file");
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer).expect("Failed to read file");
    
    let data: serde_json::Value = rmp_serde::from_slice(&buffer).expect("Failed to deserialize");
    
    // Check that at least one concept has a classification
    if let Some(concepts) = data.get("concepts").and_then(|c| c.as_object()) {
        let mut has_local = false;
        let mut has_global = false;
        
        for (concept_id, concept_data) in concepts {
            if let Some(classification) = concept_data.get("classification").and_then(|c| c.as_str()) {
                println!("Concept {} classification: {}", concept_id, classification);
                
                if classification == "LOCAL" {
                    has_local = true;
                }
                if classification == "GLOBAL" {
                    has_global = true;
                }
            }
        }
        
        // Tiny genome should have both LOCAL and GLOBAL concepts
        assert!(has_local, "Tiny genome should have at least one LOCAL concept");
        assert!(has_global, "Tiny genome should have at least one GLOBAL concept");
    }
}
