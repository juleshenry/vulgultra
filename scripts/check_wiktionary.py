import urllib.request
import urllib.error
languages = ['ext', 'lad', 'mwl', 'eml', 'lij', 'pms', 'fur', 'lld', 'frp', 'gsc', 'dlm', 'ist', 'ruo', 'nrm', 'pcd', 'gallo']
for lang in languages:
    url = f"https://dumps.wikimedia.org/{lang}wiktionary/latest/{lang}wiktionary-latest-pages-articles.xml.bz2"
    try:
        req = urllib.request.Request(url, method='HEAD')
        urllib.request.urlopen(req)
        print(f"Exists: {lang}")
    except urllib.error.URLError as e:
        print(f"Missing: {lang} ({e.reason})")
