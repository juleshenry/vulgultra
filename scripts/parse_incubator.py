import xml.etree.ElementTree as ET
import logging
import re
import json
import os

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def parse_incubator_wiktionary(xml_file: str, language_code: str):
    logging.info(f"Parsing {xml_file} (Lang: {language_code})...")
    
    extracted_data = {}

    if not os.path.exists(xml_file):
        logging.warning(f"File {xml_file} does not exist. Skipping.")
        return extracted_data

    # Parse full file since incubator xmls are small
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # In the extracted XMLs, we manually wrapped them with <mediawiki> and then put original <ns0:page> elements
        # Since namespaces can be tricky with ElementTree if not perfectly declared at the root, 
        # let's just use string operations as a fallback if ET misses them
        
    except ET.ParseError as e:
        logging.error(f"XML parsing error in {xml_file}: {e}")

    # Fallback to regex text parsing which is 100% robust against namespace issues in these extracted snippets
    with open(xml_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Split by page
    pages = re.split(r'</(?:ns0:)?page>', content)
    for page in pages:
        title_match = re.search(r'<(?:ns0:)?title>([^<]+)</(?:ns0:)?title>', page)
        text_match = re.search(r'<(?:ns0:)?text[^>]*>([\s\S]*?)</(?:ns0:)?text>', page)
        
        if title_match and text_match:
            title = title_match.group(1)
            text_content = text_match.group(1)
            
            prefix = f"Wt/{language_code}/"
            if title.startswith(prefix):
                word = title[len(prefix):]
                
                if ":" not in word:
                    ipa_match = None
                    
                    # Try standard templates like {{IPA|...}} or {{pron|...}}
                    template_match = re.search(r'\{\{(?:IPA|pron)\|([^}]+)\}\}', text_content)
                    if template_match:
                        ipa_match = template_match.group(1).split('|')[0]
                    else:
                        # Try to find /a.ba'zʊr/ style IPA
                        slash_matches = re.findall(r'/([^/]+)/', text_content)
                        # Filter to likely IPA (has phonetic chars or punctuation, no spaces/newlines usually)
                        valid_slashes = [m for m in slash_matches if len(m) > 1 and "http" not in m and "<" not in m and " " not in m and "\n" not in m]
                        if valid_slashes:
                            ipa_match = valid_slashes[0]
                    
                    extracted_data[word] = ipa_match if ipa_match else ""

    with_ipa = sum(1 for v in extracted_data.values() if v)
    logging.info(f"Finished {language_code}. Extracted {len(extracted_data)} words ({with_ipa} with phonetics).")
    
    return extracted_data

if __name__ == "__main__":
    LANGUAGES = ['lad', 'mwl', 'lij', 'pms', 'fur', 'frp', 'nrm', 'pcd']
    os.makedirs('data', exist_ok=True)
    
    total_words = 0
    total_ipa = 0
    
    for lang in LANGUAGES:
        xml_path = f"xmls/{lang}wiktionary-latest-pages-articles.xml"
        if os.path.exists(xml_path):
            data = parse_incubator_wiktionary(xml_path, lang)
            if data:
                out_path = f"data/words/{lang}_words.json"
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                total_words += len(data)
                total_ipa += sum(1 for v in data.values() if v)

    logging.info(f"DONE! Total words: {total_words} ({total_ipa} with IPA).")

