import json
import os

ALL_LANGS = {
    'an': ('Aragonese', False),
    'ast': ('Asturian', False),
    'ca': ('Catalan', False),
    # Reserved dump — not a Lacyo source.
    'en': ('English (reserved)', False),
    'es': ('Spanish', False),
    'fr': ('French', False),
    'gl': ('Galician', False),
    'it': ('Italian', False),
    'la': ('Latin', False),
    'lmo': ('Lombard', False),
    'oc': ('Occitan', False),
    'pt': ('Portuguese', False),
    'rm': ('Romansh', False),
    'ro': ('Romanian', False),
    'roa-rup': ('Aromanian', False),
    'sc': ('Sardinian', False),
    'scn': ('Sicilian', False),
    'vec': ('Venetian', False),
    'wa': ('Walloon', False),
    'pms': ('Piedmontese', True),
    'pcd': ('Picard', True),
    'mwl': ('Mirandese', True),
    'lij': ('Ligurian', True),
    'lad': ('Ladino', True),
    'frp': ('Franco-Provençal', True),
    'fur': ('Friulian', True),
    'nrm': ('Norman', True),
    'ext': ('Extremaduran', True),
    'eml': ('Emiliano-Romagnolo', True),
    'lld': ('Ladin', True),
    'gsc': ('Gascon', True),
    'dlm': ('Dalmatian', True),
    'ist': ('Istriot', True),
    'ruo': ('Istro-Romanian', True),
    'glw': ('Gallo', True)
}

sorted_codes = sorted(ALL_LANGS.keys())
new_lines = []

for i, code in enumerate(sorted_codes, 1):
    name, is_incubator = ALL_LANGS[code]
    
    suffix = ""
    if is_incubator:
        json_file = f"data/words/{code}_words.json"
        word_count = 0
        if os.path.exists(json_file):
            with open(json_file, 'r') as jf:
                data = json.load(jf)
                word_count = len(data)
        suffix = f" ({word_count} words extracted from incubator)"
        
    # Formatting spacing (roa-rup is 7 chars)
    spacing = " " * (7 - len(code))
    
    # Format the number to maintain alignment (1. vs 10.)
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
    print("README.md updated with alphabetical list!")
else:
    print("Could not find insertion bounds.")

