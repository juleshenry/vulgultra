import json
import os
import re

NEW_LANGS = {
    'pms': 'Piedmontese',
    'pcd': 'Picard',
    'mwl': 'Mirandese',
    'lij': 'Ligurian',
    'lad': 'Ladino',
    'frp': 'Franco-Provençal',
    'fur': 'Friulian',
    'nrm': 'Norman'
}

with open('README.md', 'r') as f:
    readme_content = f.read()

# Find where to append the new languages
lines = readme_content.split('\n')
xmls_idx = -1
for i, line in enumerate(lines):
    if line.strip().startswith('19. wa  — Walloon'):
        xmls_idx = i
        break

if xmls_idx != -1:
    new_lines = []
    current_num = 20
    for code, name in NEW_LANGS.items():
        json_file = f"data/words/{code}_words.json"
        word_count = 0
        if os.path.exists(json_file):
            with open(json_file, 'r') as jf:
                data = json.load(jf)
                word_count = len(data)
        
        spacing = " " * (3 - len(code))
        new_lines.append(f"  {current_num}. {code}{spacing} — {name} ({word_count} words extracted from incubator)")
        current_num += 1

    lines = lines[:xmls_idx+1] + new_lines + lines[xmls_idx+1:]
    
    with open('README.md', 'w') as f:
        f.write('\n'.join(lines))
    print("README.md updated successfully!")
else:
    print("Could not find insertion point in README.md")

