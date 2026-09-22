#!/usr/bin/env python3
"""
Morpheme Detector for Vulgultra Hybrid Optimization System

Analyzes words to detect Latin morphemes (prefixes, roots, suffixes) and
classifies concepts as LOCAL (morpheme-free) or GLOBAL (morpheme-bearing)
based on majority rule.

Usage:
    from morpheme_detector import MorphemeDetector
    
    detector = MorphemeDetector()
    
    # Detect morphemes in a single word
    result = detector.detect_morphemes("transportation", "en")
    # Returns: {"prefixes": ["trans-"], "root": "port", "suffixes": ["-ation"]}
    
    # Classify a concept
    candidates = {"fr": "transport", "es": "transporte", "it": "trasporto", "pt": "transporte"}
    classification = detector.classify_concept(candidates)
    # Returns: "GLOBAL" (majority have morphemes)
"""

import json
import os
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class MorphemeDetector:
    def __init__(self, morpheme_db_path: str = "data/latin_morphemes.json",
                 variants_dir: str = "data/morpheme_variants"):
        """
        Initialize the morpheme detector with Latin morpheme database and
        language-specific variant mappings.
        
        Args:
            morpheme_db_path: Path to the canonical Latin morpheme JSON file
            variants_dir: Directory containing language-specific variant configs
        """
        self.morpheme_db = self._load_morpheme_db(morpheme_db_path)
        self.language_variants = self._load_language_variants(variants_dir)
        
        # Create reverse lookup: variant -> canonical form
        self.variant_to_canonical = self._build_variant_lookup()
        
        logging.info(f"Loaded {len(self.morpheme_db['prefixes'])} prefixes and "
                    f"{len(self.morpheme_db['suffixes'])} suffixes")
        logging.info(f"Loaded variant mappings for {len(self.language_variants)} languages")
    
    def _load_morpheme_db(self, path: str) -> Dict:
        """Load the canonical Latin morpheme database."""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_language_variants(self, variants_dir: str) -> Dict:
        """Load all language-specific morpheme variants."""
        variants = {}
        variants_path = Path(variants_dir)
        
        if not variants_path.exists():
            logging.warning(f"Variants directory not found: {variants_dir}")
            return variants
        
        for variant_file in variants_path.glob("*_variants.json"):
            lang_code = variant_file.stem.split('_')[0]  # e.g., "fr" from "fr_variants.json"
            with open(variant_file, 'r', encoding='utf-8') as f:
                variants[lang_code] = json.load(f)
        
        return variants
    
    def _build_variant_lookup(self) -> Dict[str, Tuple[str, str]]:
        """
        Build reverse lookup: morpheme variant -> (canonical form, morpheme type).
        
        Example: "tras-" (Spanish) -> ("trans-", "prefix")
                 "-ción" (Spanish) -> ("-tion", "suffix")
        """
        lookup = {}
        
        for lang_code, lang_data in self.language_variants.items():
            # Process prefixes
            for canonical, variants in lang_data.get("prefix_variants", {}).items():
                for variant in variants:
                    # Store: variant -> (canonical, type, language)
                    lookup[f"{lang_code}:{variant}"] = (canonical, "prefix")
            
            # Process suffixes
            for canonical, variants in lang_data.get("suffix_variants", {}).items():
                for variant in variants:
                    lookup[f"{lang_code}:{variant}"] = (canonical, "suffix")
        
        return lookup
    
    def detect_morphemes(self, word: str, language: str) -> Dict[str, List[str]]:
        """
        Detect Latin morphemes in a word for a given language.
        
        Args:
            word: The word to analyze (e.g., "transportation", "trasporto")
            language: ISO 639-1 language code (e.g., "en", "fr", "es", "it", "pt")
        
        Returns:
            Dictionary with detected morphemes:
            {
                "prefixes": ["trans-"],
                "root": "port",
                "suffixes": ["-ation"],
                "has_morphemes": True
            }
        """
        word_lower = word.lower()
        result = {
            "prefixes": [],
            "root": "",
            "suffixes": [],
            "has_morphemes": False
        }
        
        # Get language-specific variants
        if language not in self.language_variants:
            logging.debug(f"No variant mapping for language: {language}")
            return result
        
        lang_variants = self.language_variants[language]
        
        # Detect prefixes (check longest first to avoid partial matches)
        # Strip hyphens from morpheme forms for matching against actual words
        detected_prefix_len = 0
        for canonical, variants in sorted(lang_variants.get("prefix_variants", {}).items(),
                                          key=lambda x: -max(len(v.rstrip('-')) for v in x[1])):
            for variant in sorted(variants, key=lambda x: -len(x)):
                # Remove trailing hyphen for prefix matching
                variant_clean = variant.rstrip('-')
                if word_lower.startswith(variant_clean):
                    result["prefixes"].append(canonical)
                    detected_prefix_len = len(variant_clean)
                    break
            if detected_prefix_len > 0:
                break
        
        # Detect suffixes (check longest first)
        # Strip hyphens from morpheme forms for matching against actual words
        detected_suffix_len = 0
        for canonical, variants in sorted(lang_variants.get("suffix_variants", {}).items(),
                                          key=lambda x: -max(len(v.lstrip('-')) for v in x[1])):
            for variant in sorted(variants, key=lambda x: -len(x)):
                # Remove leading hyphen for suffix matching
                variant_clean = variant.lstrip('-')
                if word_lower.endswith(variant_clean):
                    result["suffixes"].append(canonical)
                    detected_suffix_len = len(variant_clean)
                    break
            if detected_suffix_len > 0:
                break
        
        # Extract root (what remains after removing prefix and suffix)
        # Require minimum root length of 3 characters to avoid false positives
        MIN_ROOT_LENGTH = 3
        
        if detected_prefix_len > 0 or detected_suffix_len > 0:
            root_start = detected_prefix_len
            root_end = len(word_lower) - detected_suffix_len if detected_suffix_len > 0 else len(word_lower)
            potential_root = word_lower[root_start:root_end]
            
            # Validate root length
            if len(potential_root) < MIN_ROOT_LENGTH:
                # Root too short - likely a false positive
                # Reset detection and treat entire word as root
                result["prefixes"] = []
                result["suffixes"] = []
                result["root"] = word_lower
                result["has_morphemes"] = False
            else:
                result["root"] = potential_root
                result["has_morphemes"] = True
        else:
            # No morphemes detected, entire word is the root
            result["root"] = word_lower
        
        return result
    
    def classify_concept(self, candidates: Dict[str, str], threshold: float = 0.5) -> str:
        """
        Classify a concept as LOCAL or GLOBAL based on morpheme detection.
        
        Uses majority rule: if >50% of candidates have morphemes -> GLOBAL,
        otherwise -> LOCAL.
        
        Args:
            candidates: Dict mapping language codes to candidate words
                       Example: {"fr": "transport", "es": "transporte", "it": "trasporto"}
            threshold: Minimum proportion of morphemic words for GLOBAL classification (default: 0.5)
        
        Returns:
            "GLOBAL" if majority have morphemes, "LOCAL" otherwise
        """
        if not candidates:
            return "LOCAL"
        
        morpheme_count = 0
        total_candidates = len(candidates)
        
        for lang_code, word in candidates.items():
            detection = self.detect_morphemes(word, lang_code)
            if detection["has_morphemes"]:
                morpheme_count += 1
                logging.debug(f"  {lang_code}:{word} -> {detection['prefixes']} + {detection['root']} + {detection['suffixes']}")
            else:
                logging.debug(f"  {lang_code}:{word} -> no morphemes")
        
        proportion = morpheme_count / total_candidates
        classification = "GLOBAL" if proportion > threshold else "LOCAL"
        
        logging.info(f"Concept classification: {morpheme_count}/{total_candidates} morphemic -> {classification}")
        
        return classification
    
    def get_morpheme_info(self, morpheme_form: str) -> Optional[Dict]:
        """
        Get detailed information about a specific morpheme.
        
        Args:
            morpheme_form: Canonical morpheme form (e.g., "trans-", "-tion")
        
        Returns:
            Dictionary with morpheme details (form, meaning, etymology, examples)
            or None if not found
        """
        # Check prefixes
        for prefix in self.morpheme_db["prefixes"]:
            if prefix["form"] == morpheme_form:
                return prefix
        
        # Check suffixes
        for suffix in self.morpheme_db["suffixes"]:
            if suffix["form"] == morpheme_form:
                return suffix
        
        return None
    
    def analyze_concept_morphology(self, candidates: Dict[str, str]) -> Dict:
        """
        Perform comprehensive morphological analysis of a concept.
        
        Args:
            candidates: Dict mapping language codes to candidate words
        
        Returns:
            Detailed analysis including:
            - classification: "LOCAL" or "GLOBAL"
            - morpheme_breakdown: Per-word morpheme detection
            - shared_morphemes: Morphemes found across multiple candidates
            - morpheme_inventory: Unique canonical morphemes detected
        """
        analysis = {
            "classification": self.classify_concept(candidates),
            "morpheme_breakdown": {},
            "shared_morphemes": {},
            "morpheme_inventory": set()
        }
        
        # Analyze each candidate
        for lang_code, word in candidates.items():
            detection = self.detect_morphemes(word, lang_code)
            analysis["morpheme_breakdown"][f"{lang_code}:{word}"] = detection
            
            # Track all detected morphemes
            for prefix in detection["prefixes"]:
                analysis["morpheme_inventory"].add(prefix)
                analysis["shared_morphemes"][prefix] = analysis["shared_morphemes"].get(prefix, 0) + 1
            
            for suffix in detection["suffixes"]:
                analysis["morpheme_inventory"].add(suffix)
                analysis["shared_morphemes"][suffix] = analysis["shared_morphemes"].get(suffix, 0) + 1
        
        # Convert set to list for JSON serialization
        analysis["morpheme_inventory"] = list(analysis["morpheme_inventory"])
        
        return analysis


def main():
    """CLI interface for testing the morpheme detector."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Detect Latin morphemes in words")
    parser.add_argument('--word', help='Single word to analyze')
    parser.add_argument('--lang', default='en', help='Language code (en, fr, es, it, pt)')
    parser.add_argument('--concept', help='Concept ID for multi-word analysis')
    parser.add_argument('--candidates', nargs='+', 
                       help='Candidate words in format lang:word (e.g., fr:transport es:transporte)')
    args = parser.parse_args()
    
    detector = MorphemeDetector()
    
    if args.word:
        # Single word analysis
        result = detector.detect_morphemes(args.word, args.lang)
        print(f"\nMorpheme analysis for '{args.word}' ({args.lang}):")
        print(f"  Prefixes: {result['prefixes']}")
        print(f"  Root: {result['root']}")
        print(f"  Suffixes: {result['suffixes']}")
        print(f"  Has morphemes: {result['has_morphemes']}")
        
    elif args.candidates:
        # Multi-word concept analysis
        candidates = {}
        for candidate in args.candidates:
            lang, word = candidate.split(':')
            candidates[lang] = word
        
        print(f"\nAnalyzing concept with {len(candidates)} candidates:")
        analysis = detector.analyze_concept_morphology(candidates)
        
        print(f"\nClassification: {analysis['classification']}")
        print(f"\nMorpheme inventory: {', '.join(analysis['morpheme_inventory'])}")
        print(f"\nPer-candidate breakdown:")
        for candidate, detection in analysis['morpheme_breakdown'].items():
            morphemes = " + ".join(detection['prefixes'] + [detection['root']] + detection['suffixes'])
            print(f"  {candidate}: {morphemes}")
    
    else:
        # Demo mode
        print("=== Morpheme Detector Demo ===\n")
        
        # Test case 1: Transportation (GLOBAL)
        print("Test 1: Transportation concept (GLOBAL expected)")
        candidates1 = {
            "en": "transportation",
            "fr": "transport",
            "es": "transporte",
            "it": "trasporto"
        }
        analysis1 = detector.analyze_concept_morphology(candidates1)
        print(f"Result: {analysis1['classification']}")
        print(f"Morphemes: {analysis1['morpheme_inventory']}\n")
        
        # Test case 2: Red (LOCAL)
        print("Test 2: Red concept (LOCAL expected)")
        candidates2 = {
            "fr": "rouge",
            "es": "rojo",
            "it": "rosso",
            "pt": "vermelho"
        }
        analysis2 = detector.analyze_concept_morphology(candidates2)
        print(f"Result: {analysis2['classification']}")
        print(f"Morphemes: {analysis2['morpheme_inventory']}\n")
        
        # Test case 3: Information (GLOBAL)
        print("Test 3: Information concept (GLOBAL expected)")
        candidates3 = {
            "en": "information",
            "fr": "information",
            "es": "información",
            "it": "informazione"
        }
        analysis3 = detector.analyze_concept_morphology(candidates3)
        print(f"Result: {analysis3['classification']}")
        print(f"Morphemes: {analysis3['morpheme_inventory']}\n")


if __name__ == "__main__":
    main()
