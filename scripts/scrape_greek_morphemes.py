#!/usr/bin/env python3
"""
Scrapes Greek morphemes (prefixes and suffixes) from Wiktionary.

Output: data/morphemes/greek_morphemes.json with structure:
{
  "prefixes": [{"form": "anti-", "meaning": "...", "etymology": "...", "examples": [...]}],
  "suffixes": [{"form": "-logy", "meaning": "...", "etymology": "...", "examples": [...]}]
}
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
# "Ancient_Greek" is usually the source for classical prefixes/suffixes in English
PREFIXES_URL = f"{WIKTIONARY_BASE}/wiki/Category:Ancient_Greek_prefixes"
SUFFIXES_URL = f"{WIKTIONARY_BASE}/wiki/Category:Ancient_Greek_suffixes"

USER_AGENT = "CyberLatinBot/1.0 (Educational morpheme research; mailto:research@example.com)"
HEADERS = {"User-Agent": USER_AGENT}

def fetch_category_pages(category_url: str, max_pages: int = 10) -> List[str]:
    """
    Fetches all morpheme entry URLs from a Wiktionary category page.
    Handles pagination if the category spans multiple pages.
    """
    morpheme_urls = []
    current_url = category_url
    pages_fetched = 0
    
    while current_url and pages_fetched < max_pages:
        logging.info(f"Fetching category page: {current_url}")
        
        try:
            response = requests.get(current_url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the category member list (morpheme entries)
            category_div = soup.find('div', {'id': 'mw-pages'})
            if not category_div:
                logging.warning(f"No category members found at {current_url}")
                break
            
            for link in category_div.find_all('a', href=True):
                href = link['href']
                if href.startswith('/wiki/') and ':' not in href:
                    morpheme_urls.append(href)
            
            next_link = soup.find('a', string=re.compile(r'next page', re.IGNORECASE))
            if next_link and 'href' in next_link.attrs:
                current_url = urljoin(WIKTIONARY_BASE, next_link['href'])
                pages_fetched += 1
                time.sleep(1)
            else:
                break
                
        except requests.RequestException as e:
            logging.error(f"Error fetching {current_url}: {e}")
            break
    
    logging.info(f"Found {len(morpheme_urls)} morpheme entries")
    return morpheme_urls

def extract_morpheme_data(morpheme_url: str) -> Optional[Dict]:
    """
    Scrapes a single morpheme page and extracts form, meaning, etymology, examples.
    """
    full_url = urljoin(WIKTIONARY_BASE, morpheme_url)
    morpheme_form = unquote(morpheme_url.split('/')[-1])
    
    logging.info(f"Scraping morpheme: {morpheme_form}")
    
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
            logging.warning(f"No parser-output div found for {morpheme_form}")
            return None
        
        # Check for Greek etymology
        for p in parser_output.find_all('p', limit=10):
            p_text = p.get_text(strip=True)
            if 'Greek' in p_text or 'From' in p_text:
                morpheme_data["etymology"] = p_text[:300]
                break
        
        first_ol = parser_output.find('ol')
        if first_ol:
            list_items = first_ol.find_all('li', recursive=False)
            if list_items:
                definitions = []
                for li in list_items[:3]:
                    def_text = li.get_text(strip=True)
                    def_text = ' '.join(def_text.split())
                    if def_text and len(def_text) > 5:
                        definitions.append(def_text)
                if definitions:
                    morpheme_data["meaning"] = "; ".join(definitions)
        
        for ul in parser_output.find_all('ul', limit=5):
            links = ul.find_all('a', href=lambda h: h and h.startswith('/wiki/') and ':' not in h, limit=15)
            if links:
                examples = [link.get_text(strip=True) for link in links if link.get_text(strip=True)]
                examples = [ex for ex in examples if len(ex) > 2 and any(c.isalpha() for c in ex)]
                if examples:
                    morpheme_data["examples"] = examples[:10]
                    break
        
        return morpheme_data if morpheme_data["meaning"] else None
        
    except requests.RequestException as e:
        logging.error(f"Error fetching {full_url}: {e}")
        return None

def scrape_all_morphemes(prefixes_url: str, suffixes_url: str) -> Dict:
    morpheme_database = {
        "prefixes": [],
        "suffixes": [],
        "metadata": {
            "source": "Wiktionary",
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_prefixes": 0,
            "total_suffixes": 0
        }
    }
    
    # Prefix
    logging.info("=" * 60)
    logging.info("SCRAPING GREEK PREFIXES")
    logging.info("=" * 60)
    prefix_urls = fetch_category_pages(prefixes_url)
    
    for url in prefix_urls:
        morpheme_data = extract_morpheme_data(url)
        if morpheme_data:
            morpheme_database["prefixes"].append(morpheme_data)
        time.sleep(0.5)
    
    # Suffix
    logging.info("=" * 60)
    logging.info("SCRAPING GREEK SUFFIXES")
    logging.info("=" * 60)
    suffix_urls = fetch_category_pages(suffixes_url, max_pages=15)
    
    for url in suffix_urls:
        morpheme_data = extract_morpheme_data(url)
        if morpheme_data:
            morpheme_database["suffixes"].append(morpheme_data)
        time.sleep(0.5)
    
    morpheme_database["metadata"]["total_prefixes"] = len(morpheme_database["prefixes"])
    morpheme_database["metadata"]["total_suffixes"] = len(morpheme_database["suffixes"])
    
    return morpheme_database

def save_to_json(data: Dict, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logging.info(f"Saved morpheme database to {output_path}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape Greek morphemes from Wiktionary")
    parser.add_argument('--output', default='data/morphemes/greek_morphemes.json', 
                        help='Output JSON file path')
    parser.add_argument('--test', action='store_true',
                        help='Test mode: only scrape first 5 morphemes of each type')
    args = parser.parse_args()
    
    if args.test:
        logging.info("TEST MODE: Scraping only first 5 morphemes of each type")
        PREFIXES_URL = f"{WIKTIONARY_BASE}/wiki/Category:Ancient_Greek_prefixes"
        SUFFIXES_URL = f"{WIKTIONARY_BASE}/wiki/Category:Ancient_Greek_suffixes"
        
        prefix_urls = fetch_category_pages(PREFIXES_URL, max_pages=1)[:5]
        suffix_urls = fetch_category_pages(SUFFIXES_URL, max_pages=1)[:5]
        
        morpheme_database = {
            "prefixes": [],
            "suffixes": [],
            "metadata": {
                "source": "Wiktionary",
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "mode": "test"
            }
        }
        
        for url in prefix_urls:
            morpheme_data = extract_morpheme_data(url)
            if morpheme_data:
                morpheme_database["prefixes"].append(morpheme_data)
            time.sleep(0.5)
        
        for url in suffix_urls:
            morpheme_data = extract_morpheme_data(url)
            if morpheme_data:
                morpheme_database["suffixes"].append(morpheme_data)
            time.sleep(0.5)
        
        morpheme_database["metadata"]["total_prefixes"] = len(morpheme_database["prefixes"])
        morpheme_database["metadata"]["total_suffixes"] = len(morpheme_database["suffixes"])
        
        save_to_json(morpheme_database, args.output)
    else:
        morpheme_database = scrape_all_morphemes(PREFIXES_URL, SUFFIXES_URL)
        save_to_json(morpheme_database, args.output)