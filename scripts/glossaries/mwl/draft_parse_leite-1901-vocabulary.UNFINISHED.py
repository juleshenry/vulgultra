import re, glob, unicodedata, collections, sys
def nfc(s): return unicodedata.normalize('NFC', s)
pages = sorted(glob.glob('raw/leite-1901-vol2-vocabulary-pages/n*_por.txt'), key=lambda f: int(re.search(r'n(\d+)_', f).group(1)))
ENTRY = re.compile(r"^[:;|.,'‘’ ]*([^\s—–-][^—–]{0,60}?)\s*(?:[—–]|--)[—–\- ]*\s*(\S.*)$")
entries = []
for f in pages:
    cur = None
    for line in open(f, encoding='utf-8').read().split('\n'):
        line = nfc(line.strip())
        if not line: continue
        if re.match(r"^[:;|.,'‘’ ]*(H|F)[iIl1][sS][tTrR][.,:]", line):
            if cur is not None: cur['hist'].append(line)
            continue
        m = ENTRY.match(line)
        if m and cur is not None and cur['hist'] == [] and False: pass
        if m and not re.search(r'[.;:]\s', m.group(1)) and not m.group(1)[0].isupper() or (m and re.match(r'^[A-ZÀ-Ý][a-zà-ÿ]+(?: \(|$)', m.group(1) or '')):
            head = m.group(1).strip()
            cur = {'head': head, 'gloss': m.group(2), 'hist': [], 'page': f}
            entries.append(cur)
        elif cur is not None:
            (cur['hist'] if cur['hist'] else cur.setdefault('more', [])).append(line)
print(len(pages), len(entries))
import random; random.seed(1)
for e in random.sample(entries, 45): print(repr(e['head']), '|', e['gloss'][:60], '|', (e['hist'][:1] or [''])[0][:70])
