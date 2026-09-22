#!/usr/bin/env python3
"""
Scrapes modern Romance morphemes (prefixes and suffixes) from Wiktionary
for the core languages Vulgultra is built on: French, Spanish, Italian, and Portuguese.

Output: data/morphemes/romance_morphemes.json
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import logging
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin, unquote
import os

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

WIKTIONARY_BASE = "https://en.wiktionary.org"
USER_AGENT = "VulgultraBot/1.0 (Educational morpheme research; mailto:research@example.com)"
HEADERS = {"User-Agent": USER_AGENT}

LANGUAGES = {
    "french": {
        "prefix_url": f"{WIKTIONARY_BASE}/wiki/Category:French_prefixes",
        "suffix_url": f"{WIKTIONARY_BASE}/wiki/Category:French_suffixes",
        "keywords": ["French", "Latin", "From"]
    },
    "spanish": {
        "prefix_url": f"{WIKTIONARY_BASE}/wiki/Category:Spanish_prefixes",
        "suffix_url": f"{WIKTIONARY_BASE}/wiki/Category:Spanish_suffixes",
        "keywords": ["Spanish", "Latin", "From"]
    },
    "italian": {
        "prefix_url": f"{WIKTIONARY_BASE}/wiki/Category:Italian_prefixes",
        "suffix_url": f"{WIKTIONARY_BASE}/wiki/Category:Italian_suffixes",
        "keywords": ["Italian", "Latin", "From"]
    },
    "portuguese": {
        "prefix_url": f"{WIKTIONARY_BASE}/wiki/Category:Portuguese_prefixes",
        "suffix_url": f"{WIKTIONARY_BASE}/wiki/Category:Portuguese_suffixes",
        "keywords": ["Portuguese", "Latin", "From"]
    }
}

def fetch_category_pages(category_url: str, max_pages: int = 15) -> List[str]:
    """Fetches all morpheme entry URLs from a Wiktionary category page."""
    morpheme_urls = []
    current_url = category_url
    pages_fetched = 0
    
    while current_url and pages_fetched < max_pages:
        logging.info(f"Fetching category page: {unquote(current_url)}")
        
        try:
            response = requests.get(current_url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            category_div = soup.find('div', {'id': 'mw-pages'})
            if not category_div:
                logging.warning(f"No category members found at {unquote(current_url)}")
                break
            
            for link in category_div.find_all('a', href=True):
                href = link['href']
                if href.startswith('/wiki/') and ':' not in href:
                    morpheme_urls.append(href)
            
            next_link = soup.find('a', string=re.compile(r'next page', re.IGNORECASE))
            if next_link and 'href' in next_link.attrs:
                current_url = urljoin(WIKTIONARY_BASE, next_link['href'])
                pages_fetched += 1
                time.sleep(0.5)
            else:
                break
                
        except requests.RequestException as e:
            logging.error(f"Error fetching {current_url}: {e}")
            break
    
    return morpheme_urls

def extract_morpheme_data(morpheme_url: str, keywords: List[str]) -> Optional[Dict]:
    """Scrapes a single morpheme page."""
    full_url = urljoin(WIKTIONARY_BASE, morpheme_url)
    morpheme_form = unquote(morpheme_url.split('/')[-1])
    
    try:
        response = requests.get(full_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        morpheme_data = {
            "form": morpheme_form,
            "meaning": "",
            "etymology": "",
            "examples": []
        }
        
        parser_output = soup.find('div', {'class': 'mw-parser-output'})
        if not parser_output:
            return None
        
        # Etymology: Find the first paragraph containing target keywords
        for p in parser_output.find_all('p', limit=15):
            p_text = p.get_text(strip=True)
            if any(k in p_text for k in keywords) and len(p_text) > 10:
                morpheme_data["etymology"] = p_text[:300]
                break
        
        # Meaning: First ordered list definitions
        first_ol = parser_output.find('ol')
        if first_ol:
            list_items = first_ol.find_all('li', recursive=False)
            if list_items:
                definitions = []
                for li in list_items[:3]:
                    def_text = ' '.join(li.get_text(strip=True).split())
                    if def_text and len(def_text) > 5:
                        definitions.append(def_text)
                if definitions:
                    morpheme_data["meaning"] = "; ".join(definitions)
        
        # Examples
        for ul in parser_output.find_all('ul', limit=8):
            links = ul.find_all('a', href=lambda h: h and h.startswith('/wiki/') and ':' not in h, limit=15)
            if links:
                examples = [link.get_text(strip=True) for link in links if link.get_text(strip=True)]
                examples = [ex for ex in examples if len(ex) > 2 and any(c.isalpha() for c in ex)]
                if examples:
                    morpheme_data["examples"] = examples[:10]
                    break
        
        return morpheme_data if morpheme_data["meaning"] else None
        
    except requests.RequestException:
        return None

def scrape_all():
    morpheme_database = {
        "metadata": {
            "source": "Wiktionary",
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    }
    
    for lang, urls in LANGUAGES.items():
        logging.info("=" * 60)
        logging.info(f"SCRAPING {lang.upper()} MORPHEMES")
        logging.info("=" * 60)
        
        morpheme_database[lang] = {"prefixes": [], "suffixes": []}
        
        # Prefixes
        logging.info(f"Fetching prefixes for {lang}...")
        prefix_urls = fetch_category_pages(urls["prefix_url"])
        for url in prefix_urls:
            data = extract_morpheme_data(url, urls["keywords"])
            if data:
                morpheme_database[lang]["prefixes"].append(data)
            time.sleep(0.05)
            
        # Suffixes
        logging.info(f"Fetching suffixes for {lang}...")
        suffix_urls = fetch_category_pages(urls["suffix_url"])
        for url in suffix_urls:
            data = extract_morpheme_data(url, urls["keywords"])
            if data:
                morpheme_database[lang]["suffixes"].append(data)
            time.sleep(0.05)
            
        logging.info(f"{lang.capitalize()} totals - Prefixes: {len(morpheme_database[lang]['prefixes'])}, Suffixes: {len(morpheme_database[lang]['suffixes'])}")

        # Save incremental progress
        with open('data/morphemes/romance_morphemes.json', 'w', encoding='utf-8') as f:
            json.dump(morpheme_database, f, indent=2, ensure_ascii=False)

    return morpheme_database

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='data/morphemes/romance_morphemes.json')
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()
    
    if args.test:
        logging.info("TEST MODE")
        # Overwrite with test parameters
        for lang in LANGUAGES:
            LANGUAGES[lang]["prefix_url"] = LANGUAGES[lang]["prefix_url"]
            # Just relying on the fetch limiting
            
        db = {"metadata": {"mode": "test"}}
        for lang, urls in LANGUAGES.items():
            db[lang] = {"prefixes": [], "suffixes": []}
            p_urls = fetch_category_pages(urls["prefix_url"], max_pages=1)[:5]
            for u in p_urls:
                d = extract_morpheme_data(u, urls["keywords"])
                if d: db[lang]["prefixes"].append(d)
                
            s_urls = fetch_category_pages(urls["suffix_url"], max_pages=1)[:5]
            for u in s_urls:
                d = extract_morpheme_data(u, urls["keywords"])
                if d: db[lang]["suffixes"].append(d)
                
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
            
    else:
        db = scrape_all()
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        logging.info(f"Saved database to {args.output}")