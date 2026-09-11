import os
import subprocess
import json

ALL_LANGS = {
    'an': ('Aragonese', 'anwiktionary-latest-pages-articles.xml', False),
    'ast': ('Asturian', 'astwiktionary-latest-stub-articles.xml', False),
    'ca': ('Catalan', 'cawiktionary-latest-pages-articles.xml', False),
    # Reserved: not a Lacyo source. Kept so the dump can be used later.
    'en': ('English (reserved, not a source)', 'enwiktionary-latest-pages-articles.xml', False),
    'es': ('Spanish', 'eswiktionary-latest-pages-articles.xml', False),
    'fr': ('French', 'frwiktionary-latest-pages-articles.xml', False),
    'gl': ('Galician', 'glwiktionary-latest-pages-articles.xml', False),
    'it': ('Italian', 'itwiktionary-latest-pages-articles.xml', False),
    'la': ('Latin', 'lawiktionary-latest-pages-articles.xml', False),
    'lmo': ('Lombard', 'lmowiktionary-latest-pages-articles.xml', False),
    'oc': ('Occitan', 'ocwiktionary-latest-pages-articles.xml', False),
    'pt': ('Portuguese', 'ptwiktionary-latest-pages-articles.xml', False),
    'rm': ('Romansh', 'rmwiktionary-latest-pages-articles.xml', False),
    'ro': ('Romanian', 'rowiktionary-latest-pages-articles.xml', False),
    'roa-rup': ('Aromanian', 'roa_rupwiktionary-latest-pages-articles.xml', False),
    'sc': ('Sardinian', 'scwiktionary-latest-pages-articles.xml', False),
    'scn': ('Sicilian', 'scnwiktionary-latest-pages-articles.xml', False),
    'vec': ('Venetian', 'vecwiktionary-latest-pages-articles.xml', False),
    'wa': ('Walloon', 'wawiktionary-latest-pages-articles.xml', False),
    
    'pms': ('Piedmontese', 'data/words/pms_words.json', True),
    'pcd': ('Picard', 'data/words/pcd_words.json', True),
    'mwl': ('Mirandese', 'data/words/mwl_words.json', True),
    'lij': ('Ligurian', 'data/words/lij_words.json', True),
    'lad': ('Ladino', 'data/words/lad_words.json', True),
    'frp': ('Franco-Provençal', 'data/words/frp_words.json', True),
    'fur': ('Friulian', 'data/words/fur_words.json', True),
    'nrm': ('Norman', 'data/words/nrm_words.json', True),
    'ext': ('Extremaduran', 'data/words/ext_words.json', True),
    'eml': ('Emiliano-Romagnolo', 'data/words/eml_words.json', True),
    'lld': ('Ladin', 'data/words/lld_words.json', True),
    'gsc': ('Gascon', 'data/words/gsc_words.json', True),
    'dlm': ('Dalmatian', 'data/words/dlm_words.json', True),
    'ist': ('Istriot', 'data/words/ist_words.json', True),
    'ruo': ('Istro-Romanian', 'data/words/ruo_words.json', True),
    'glw': ('Gallo', 'data/words/glw_words.json', True)
}

counts = {}

def get_count_fast(filepath):
    # Pure python line by line is usually quite fast enough, avoiding grep memory issues and pipes
    count = 0
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if '<title>' in line and ':' not in line:
                count += 1
    return count

print("Counting words...")
for code, (name, path, is_incubator) in ALL_LANGS.items():
    if is_incubator:
        count = 0
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                count = len(data)
        counts[code] = (name, count, True)
        print(f"{code}: {count}")
    else:
        full_path = os.path.join('xmls', path)
        if os.path.exists(full_path):
            print(f"Counting {code}...", flush=True)
            c = get_count_fast(full_path)
            counts[code] = (name, c, False)
            print(f"{code}: {c}")
        else:
            counts[code] = (name, 0, False)
            print(f"{code}: missing")

# Update README
sorted_codes = sorted(counts.keys())
new_lines = []

def format_number(num):
    return f"{num:,}"

for i, code in enumerate(sorted_codes, 1):
    name, count, is_incubator = counts[code]
    
    if is_incubator:
        suffix = f" ({format_number(count)} words extracted from incubator)"
    else:
        suffix = f" ({format_number(count)} words)"
        
    spacing = " " * (7 - len(code))
    num_str = f"{i}."
    num_spacing = " " if i < 10 else ""
    
    new_lines.append(f"  {num_spacing}{num_str} {code}{spacing} — {name}{suffix}")

new_lines.append("")
new_lines.append("  *(If you'd like to contribute to these low-resource Romance languages, head over to the [Wikimedia Incubator](https://incubator.wikimedia.org/) and start adding entries!)*")

with open('README.md', 'r') as f:
    lines = f.read().split('\n')

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if '1. an' in line and 'Aragonese' in line:
        start_idx = i
        break

if start_idx != -1:
    for i in range(start_idx, len(lines)):
        if lines[i].startswith('```'):
            end_idx = i
            break

if start_idx != -1 and end_idx != -1:
    lines = lines[:start_idx] + new_lines + lines[end_idx:]
    with open('README.md', 'w') as f:
        f.write('\n'.join(lines))
    print("README.md updated with all counts!")

