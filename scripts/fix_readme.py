import json
import os

INCUBATOR_LANGS = [
    ('pms', 'Piedmontese'),
    ('pcd', 'Picard'),
    ('mwl', 'Mirandese'),
    ('lij', 'Ligurian'),
    ('lad', 'Ladino'),
    ('frp', 'Franco-Provençal'),
    ('fur', 'Friulian'),
    ('nrm', 'Norman'),
    ('ext', 'Extremaduran'),
    ('eml', 'Emiliano-Romagnolo'),
    ('lld', 'Ladin'),
    ('gsc', 'Gascon'),
    ('dlm', 'Dalmatian'),
    ('ist', 'Istriot'),
    ('ruo', 'Istro-Romanian'),
    ('glw', 'Gallo')
]

with open('README.md', 'r') as f:
    lines = f.read().split('\n')

# Find the start of our appended list (line 20. pms)
start_idx = -1
for i, line in enumerate(lines):
    if line.strip().startswith('19. wa  — Walloon'):
        start_idx = i + 1
        break

# Find the end of our appended list (where ``` is)
end_idx = start_idx
for i in range(start_idx, len(lines)):
    if lines[i].startswith('```'):
        end_idx = i
        break

new_lines = []
current_num = 20
for code, name in INCUBATOR_LANGS:
    json_file = f"data/words/{code}_words.json"
    word_count = 0
    if os.path.exists(json_file):
        with open(json_file, 'r') as jf:
            data = json.load(jf)
            word_count = len(data)
    
    spacing = " " * (3 - len(code))
    new_lines.append(f"  {current_num}. {code}{spacing} — {name} ({word_count} words extracted from incubator)")
    current_num += 1

new_lines.append("")
new_lines.append("  *(If you'd like to contribute to these low-resource Romance languages, head over to the [Wikimedia Incubator](https://incubator.wikimedia.org/) and start adding entries!)*")

lines = lines[:start_idx] + new_lines + lines[end_idx:]

with open('README.md', 'w') as f:
    f.write('\n'.join(lines))
print("README.md updated with 0-word langs and contribution note!")
