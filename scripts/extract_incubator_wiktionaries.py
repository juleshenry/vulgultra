import bz2
import xml.etree.ElementTree as ET
import re
import os

LANGUAGES = ['ext', 'lad', 'mwl', 'eml', 'lij', 'pms', 'fur', 'lld', 'frp', 'gsc', 'dlm', 'ist', 'ruo', 'nrm', 'pcd', 'gallo']
DUMP_FILE = 'incubatorwiki-latest-pages-articles.xml.bz2'
OUTPUT_DIR = 'xmls'

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Pre-compile regexes for fast matching
# We look for titles starting with Wt/LANG/
lang_regexes = {lang: re.compile(f'^Wt/{lang}/') for lang in LANGUAGES}

# Open output files
output_files = {}
for lang in LANGUAGES:
    file_path = os.path.join(OUTPUT_DIR, f"{lang}wiktionary-latest-pages-articles.xml")
    f = open(file_path, 'w', encoding='utf-8')
    f.write('<?xml version="1.0" encoding="utf-8"?>\n')
    f.write('<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd" version="0.10" xml:lang="en">\n')
    f.write(f'  <siteinfo>\n    <sitename>Wiktionary</sitename>\n    <dbname>{lang}wiktionary</dbname>\n    <base>https://incubator.wikimedia.org/wiki/Wt/{lang}/</base>\n    <generator>MediaWiki 1.43.0-wmf.19</generator>\n    <case>first-letter</case>\n    <namespaces>\n      <namespace key="0" case="first-letter" />\n    </namespaces>\n  </siteinfo>\n')
    output_files[lang] = f

def get_namespace(tag):
    m = re.match(r'\{.*\}', tag)
    return m.group(0) if m else ''

print(f"Opening {DUMP_FILE} for extraction...")
count_found = {lang: 0 for lang in LANGUAGES}

try:
    with bz2.BZ2File(DUMP_FILE, 'r') as bz2_file:
        context = ET.iterparse(bz2_file, events=('start', 'end'))
        
        _, root = next(context) # get root element
        ns = get_namespace(root.tag)
        
        for event, elem in context:
            if event == 'end' and elem.tag == f'{ns}page':
                title_elem = elem.find(f'{ns}title')
                if title_elem is not None and title_elem.text:
                    title = title_elem.text
                    
                    # Check which language it belongs to
                    for lang, regex in lang_regexes.items():
                        if regex.match(title):
                            # Convert element back to XML string and write
                            xml_str = ET.tostring(elem, encoding='unicode', method='xml')
                            # The string will have namespace prefixes, which is fine for parsing later
                            output_files[lang].write(xml_str)
                            output_files[lang].write('\n')
                            count_found[lang] += 1
                            break
                            
                # Clear the element to save memory
                root.clear()
except FileNotFoundError:
    print(f"Error: {DUMP_FILE} not found. Please download it first.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    for lang, f in output_files.items():
        f.write('</mediawiki>\n')
        f.close()

print("\nExtraction complete! Stats:")
for lang, count in count_found.items():
    print(f"  {lang}: {count} pages")

