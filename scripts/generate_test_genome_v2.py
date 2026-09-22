#!/usr/bin/env python3
"""
Generate a test .clatin genome file for Vulgultra v2.0 with concept classifications.

This script converts the test_concepts.json file into a msgpack-serialized .clatin file
that includes concept classifications (LOCAL vs GLOBAL) for the Rust CLI to use.
"""

import json
import msgpack
from pathlib import Path
from morpheme_detector import MorphemeDetector


def count_syllables(word: str) -> int:
    """Heuristic syllable counting."""
    vowels = "aeiouyáéíóúàèìòùâêîôûäëïöü"
    count = 0
    prev_is_vowel = False
    for char in word.lower():
        is_vowel = char in vowels
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel
    return max(1, count)


def extract_phonemes(word: str) -> list:
    """Mock phoneme extraction - returns list of unique characters."""
    return list(set(list(word.lower())))


def generate_genome_v2(input_json: str, output_clatin: str):
    """
    Generate a v2.0 genome with concept classifications.
    
    Args:
        input_json: Path to test_concepts.json
        output_clatin: Output path for .clatin file
    """
    # Load test concepts
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    test_concepts = data["concepts"]
    
    # Initialize morpheme detector
    detector = MorphemeDetector()
    
    # Build genome structure
    concepts = {}
    choices = {}
    
    for concept_id, concept_data in test_concepts.items():
        grammatical_class = concept_data.get("grammatical_class", "noun")
        
        # Classify concept using morpheme detector
        candidates_by_lang = concept_data["candidates"]
        all_candidates = []
        for lang, words in candidates_by_lang.items():
            for word in words:
                all_candidates.append({"word": word, "language": lang})
        
        # Use detector to classify
        classification = detector.classify_concept(candidates_by_lang)
        
        # Build candidate list with full metadata
        candidates = []
        for cand in all_candidates:
            word = cand["word"]
            lang = cand["language"]
            
            candidates.append({
                "word": word,
                "syllables": count_syllables(word),
                "phonemes": extract_phonemes(word),
                "language": lang
            })
        
        # Create concept entry
        concepts[concept_id] = {
            "id": concept_id,
            "grammatical_class": grammatical_class,
            "candidates": candidates,
            "classification": classification
        }
        
        # Initialize with first candidate
        choices[concept_id] = 0
    
    # Build state object
    state = {
        "concepts": concepts,
        "choices": choices,
        "energy_score": 0,
        "morpheme_inventory": []  # Will be calculated by Rust
    }
    
    # Serialize to msgpack
    packed = msgpack.packb(state, use_bin_type=True)
    
    # Write to file
    output_path = Path(output_clatin)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(packed)
    
    print(f"✓ Generated {output_clatin}")
    print(f"  - {len(concepts)} concepts")
    print(f"  - {sum(1 for c in concepts.values() if c['classification'] == 'LOCAL')} LOCAL concepts")
    print(f"  - {sum(1 for c in concepts.values() if c['classification'] == 'GLOBAL')} GLOBAL concepts")
    print(f"  - {sum(len(c['candidates']) for c in concepts.values())} total candidates")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        # Auto-generate output filename based on input
        if input_file.endswith('.json'):
            output_file = input_file.replace('.json', '.clatin')
        else:
            output_file = input_file + '.clatin'
    else:
        input_file = "data/test_concepts.json"
        output_file = "data/test_genome_v2.clatin"
    
    generate_genome_v2(input_file, output_file)
    print(f"\nTest genome ready for Rust CLI:")
    print(f"  cargo run --release -- start -f {output_file}")
