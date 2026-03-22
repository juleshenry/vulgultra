import json, time, logging
from scrape_romance_morphemes import LANGUAGES, fetch_category_pages, extract_morpheme_data
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

with open('data/morphemes/romance_morphemes.json', 'r') as f:
    db = json.load(f)

for lang in ["italian", "portuguese"]:
    if lang not in db:
        db[lang] = {"prefixes": [], "suffixes": []}
        
    urls = LANGUAGES[lang]
    logging.info(f"Resuming {lang}...")
    
    if len(db[lang]["prefixes"]) == 0:
        prefix_urls = fetch_category_pages(urls["prefix_url"])
        for u in prefix_urls:
            d = extract_morpheme_data(u, urls["keywords"])
            if d: db[lang]["prefixes"].append(d)
            time.sleep(0.05)
            
    if len(db[lang]["suffixes"]) == 0:
        suffix_urls = fetch_category_pages(urls["suffix_url"])
        for u in suffix_urls:
            d = extract_morpheme_data(u, urls["keywords"])
            if d: db[lang]["suffixes"].append(d)
            time.sleep(0.05)

    with open('data/morphemes/romance_morphemes.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
