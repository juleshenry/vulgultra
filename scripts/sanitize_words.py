import json
import glob
import os
import re

def is_clean(key, value, lang_code):
    v = str(value).strip()
    k = str(key).strip()
    
    # Must have both key and value
    if not v or not k: 
        return False
        
    # Filter out HTML tags and common entities
    if re.search(r'<[^>]+>|&[a-z]+;|&#[0-9]+;', v): 
        return False
    if re.search(r'<[^>]+>|&[a-z]+;|&#[0-9]+;', k): 
        return False
        
    # Filter out URLs and domains (very rudimentary but effective for these dumps)
    if re.search(r'http[s]?://|www\.|[a-zA-Z0-9-]+\.(com|org|net|edu|fr|it|es|pt)(/|$)', v, re.IGNORECASE): 
        return False
        
    # Filter out definitions that are just the language code (e.g. "pcd")
    if v.lower() == lang_code.lower(): 
        return False
        
    # Filter out Wiktionary meta-text
    if "wiktionary" in v.lower() or "wikipedia" in v.lower(): 
        return False

    # Filter out single character definitions (unlikely to be a real definition)
    if len(v) < 2:
        return False

    return True

def main():
    files = glob.glob('data/words/*_words.json')
    total_removed = 0
    
    for fpath in files:
        filename = os.path.basename(fpath)
        lang_code = filename.split('_')[0]
        
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading {fpath}: {e}")
            continue
            
        clean_data = {}
        for k, v in data.items():
            if is_clean(k, v, lang_code):
                clean_data[k] = str(v).strip()
                
        removed = len(data) - len(clean_data)
        total_removed += removed
        
        if removed > 0:
            print(f"Sanitized {filename}: {len(data)} -> {len(clean_data)} (removed {removed})")
            with open(fpath, 'w', encoding='utf-8') as f:
                json.dump(clean_data, f, indent=2, ensure_ascii=False)
        else:
            print(f"Sanitized {filename}: {len(data)} -> {len(clean_data)} (clean)")

    print(f"\nTotal junk entries removed across all files: {total_removed}")

if __name__ == '__main__':
    main()
