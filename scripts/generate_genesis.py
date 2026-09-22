import msgpack
import argparse
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def create_genesis_state() -> Dict[str, Any]:
    """
    Creates the genesis.clatin file using a mock initial lexicon.
    """
    # Define our mock concepts with grammatical classes and phonetic candidates
    concepts = {
        "concept_water": {
            "id": "concept_water",
            "grammatical_class": "noun",
            "candidates": [
                {"word": "eau", "syllables": 1, "phonemes": ["o"]},
                {"word": "agua", "syllables": 2, "phonemes": ["a", "g", "w", "a"]},
                {"word": "acqua", "syllables": 2, "phonemes": ["a", "k", "k", "w", "a"]},
            ]
        },
        "concept_fire": {
            "id": "concept_fire",
            "grammatical_class": "noun",
            "candidates": [
                {"word": "feu", "syllables": 1, "phonemes": ["f", "ø"]},
                {"word": "fuego", "syllables": 2, "phonemes": ["f", "w", "e", "g", "o"]},
                {"word": "fuoco", "syllables": 2, "phonemes": ["f", "w", "o", "k", "o"]},
            ]
        },
        "concept_speak": {
            "id": "concept_speak",
            "grammatical_class": "verb-ar",
            "candidates": [
                {"word": "parler", "syllables": 2, "phonemes": ["p", "a", "ʁ", "l", "e"]},
                {"word": "hablar", "syllables": 2, "phonemes": ["a", "b", "l", "a", "ɾ"]},
                {"word": "parlare", "syllables": 3, "phonemes": ["p", "a", "r", "l", "a", "r", "e"]},
            ]
        },
        "concept_love": {
            "id": "concept_love",
            "grammatical_class": "verb-ar",
            "candidates": [
                {"word": "aimer", "syllables": 2, "phonemes": ["ɛ", "m", "e"]},
                {"word": "amar", "syllables": 2, "phonemes": ["a", "m", "a", "ɾ"]},
                {"word": "amare", "syllables": 3, "phonemes": ["a", "m", "a", "r", "e"]},
            ]
        }
    }

    # Set initial random choices (e.g., all 0 index)
    choices = {concept_id: 0 for concept_id in concepts}

    state = {
        "concepts": concepts,
        "choices": choices,
        "energy_score": 0  # Will be recalculated by Rust
    }
    
    return state

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vulgultra Genesis Generator")
    parser.add_argument('--out', default='genesis.clatin', help='Output file path')
    args = parser.parse_args()
    
    state = create_genesis_state()
    
    with open(args.out, 'wb') as f:
        packed = msgpack.packb(state, use_bin_type=True)
        f.write(packed)
        
    logging.info(f"Successfully generated genesis block: {args.out}")
