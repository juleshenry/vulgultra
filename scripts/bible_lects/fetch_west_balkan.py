#!/usr/bin/env python3
"""Rebuild the verse-keyed Bible TSVs for the western and Balkan thin lects.

    python3 data/bible/lects/fetch_west_balkan.py            # build every text
    python3 data/bible/lects/fetch_west_balkan.py wa rup     # build only these
    python3 data/bible/lects/fetch_west_balkan.py --check    # build, then compare with la.tsv
    python3 data/bible/lects/fetch_west_balkan.py --offline  # build from raw/ only

Everything downloaded is kept untouched under raw/; a file already there is
never fetched again, so a rebuild with --offline needs no network.  Sources:
MediaWiki api.php (wa.wikisource, fr.wikisource), eBible.org zips, archive.org
download URLs, the Gallica document API, one PDF each from Wikimedia Commons
and CIEL d'Oc.  One request every 1.5 s at most, Retry-After honoured.

Needs poppler (pdftotext, pdftoppm) for oc and mwl, and tesseract for mwl only
when raw/ocr_mwl_revista1894/ is empty.  See SOURCES-west-balkan.md for what
each file is worth: pcd and mwl are unproofread OCR.
"""
from __future__ import annotations

import csv
import html
import io
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import subprocess
import zipfile
from collections import Counter, OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
LATIN = HERE.parent / "texts" / "la.tsv"
UA = "vulgultra-research/0.1 (+noncommercial; lexical sourcing)"
PAUSE = 1.5  # seconds between requests (the brief asks for <= 1 request/s)

_last = [0.0]


# --------------------------------------------------------------------------
# fetching
# --------------------------------------------------------------------------
def http_get(url: str, tries: int = 8) -> bytes:
    """GET with the project User-Agent, a polite pause, and Retry-After."""
    for attempt in range(tries):
        wait = PAUSE - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
            _last[0] = time.time()
            return data
        except urllib.error.HTTPError as err:
            _last[0] = time.time()
            if err.code in (429, 503):
                ra = err.headers.get("Retry-After", "")
                pause = int(ra) + 3 if ra.isdigit() else 30 * (attempt + 1)
                sys.stderr.write(f"  [{err.code}] {url[:70]}… waiting {pause}s\n")
                time.sleep(pause)
                continue
            raise
    raise RuntimeError(f"gave up on {url}")


OFFLINE = False  # --offline: never touch the network, build from what raw/ holds


def fetch(url: str, name: str, optional: bool = False) -> "Path | None":
    """Download url to raw/name unless it is already there."""
    dest = RAW / name
    if not dest.exists() or dest.stat().st_size == 0:
        if OFFLINE:
            if optional:
                return None
            raise FileNotFoundError(f"{dest} is missing and --offline was given")
        dest.parent.mkdir(parents=True, exist_ok=True)
        sys.stderr.write(f"  fetching {url}\n")
        dest.write_bytes(http_get(url))
    return dest


def mw_pages(host: str, titles: list[str], name: str) -> "OrderedDict[str, str]":
    """Wikitext of several pages through api.php; the JSON answers are kept
    as raw/name (one JSON array of API responses).  Returns title -> wikitext
    in the order asked."""
    dest = RAW / name
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        answers = []
        for i in range(0, len(titles), 40):
            q = urllib.parse.urlencode({
                "action": "query", "prop": "revisions", "rvprop": "content|timestamp|ids",
                "rvslots": "main", "titles": "|".join(titles[i:i + 40]),
                "format": "json", "formatversion": "2",
            })
            sys.stderr.write(f"  fetching {host} pages {i + 1}-{min(i + 40, len(titles))} of {len(titles)}\n")
            answers.append(json.loads(http_get(f"https://{host}/w/api.php?{q}")))
        dest.write_text(json.dumps(answers, ensure_ascii=False, indent=1), encoding="utf-8")
    answers = json.loads(dest.read_text(encoding="utf-8"))
    got = {}
    for ans in answers:
        norm = {n["to"]: n["from"] for n in ans.get("query", {}).get("normalized", [])}
        for page in ans["query"]["pages"]:
            if page.get("missing") or "revisions" not in page:
                continue
            text = page["revisions"][0]["slots"]["main"]["content"]
            got[page["title"]] = text
            if page["title"] in norm:
                got[norm[page["title"]]] = text
    return OrderedDict((t, got[t]) for t in titles if t in got)


# --------------------------------------------------------------------------
# cleaning
# --------------------------------------------------------------------------
ROMAN = {s: i for i, s in enumerate(
    "I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI XVII XVIII XIX XX XXI XXII "
    "XXIII XXIV XXV XXVI XXVII XXVIII XXIX XXX".split(), 1)}


KEEP_TEMPLATES = {"c", "center", "centré", "sc", "smaller", "larger", "right", "left", "lang",
                  "tab", "g", "d", "i", "b", "x-larger", "xx-larger", "small", "big", "alinea"}


def _template(m: "re.Match") -> str:
    """Formatting templates keep their text ({{c|…}}, {{sc|…}}); others vanish."""
    parts = m.group(1).split("|")
    name = parts[0].strip().lower()
    if name in KEEP_TEMPLATES:
        args = [a for a in parts[1:] if not re.match(r"\s*[\w-]+\s*=", a)]
        if name == "lang" and len(args) > 1:
            args = args[1:]
        return args[0] if args else ""
    if name in ("alignmint", "poem"):
        return parts[-1]
    return ""


def strip_wiki(text: str) -> str:
    """Wikitext -> plain text: no refs, templates, links, tags or emphasis."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"<ref[^>]*/>", "", text)
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.S)
    text = re.sub(r"<noinclude>.*?</noinclude>", "", text, flags=re.S)
    text = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", text)
    for _ in range(5):  # nested templates, innermost first
        text = re.sub(r"\{\{([^{}]*)\}\}", _template, text)
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"'{2,}", "", text)
    return html.unescape(text)


def tidy(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = text.replace(" ", " ").replace(" ", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", text).strip()


_LINE_NUM = re.compile(r"^[ \t]*[\[(]?(\d{1,3})[\])]?[ \t]*[.,:]?[ \t]*(?=\S)", re.M)


def fix_typed_digits(text: str) -> str:
    """Verse numbers typed with letters: "I0." -> "10.", "l4." -> "14.", "4l." -> "41."."""
    def repair(m):
        return m.group(1) + m.group(2).translate(str.maketrans("IlO", "110")) + m.group(3)
    text = re.sub(r"(?m)^([ \t]*)((?=[IlO]*\d)[0-9IlO]{2,3})([.,][ \t])", repair, text)
    return re.sub(r"((?<=[.!?»”\"] )|(?<=[.!?»”\"]  ))((?=[Il]?\d[Il]?\.)[0-9Il]{2,3})(\. )", repair, text)


def split_numbered(text: str, notes: list[str] | None = None, label: str = "",
                   max_gap: int = 3, start: int = 1) -> "OrderedDict[int, str]":
    """Cut a chapter into verses on its own verse numbers.

    Numbers that open a line are trusted first; they must run 1, 2, 3 …  A
    number that is skipped at line starts is then looked for inside the
    preceding verse (printers and transcribers often run two verses into one
    paragraph).  A line-opening number that breaks the run while its neighbours
    agree is taken for a misprint of the expected number.  Whatever stays
    unfound is left merged in the verse before it and reported in notes."""
    notes = notes if notes is not None else []
    text = fix_typed_digits(text)
    marks = [(m.start(), m.end(), int(m.group(1))) for m in _LINE_NUM.finditer(text)]
    accepted: list[tuple[int, int, int]] = []  # (start, end, verse)
    cur = start - 1
    for i, (st, en, n) in enumerate(marks):
        nxt = marks[i + 1][2] if i + 1 < len(marks) else None
        if n == cur + 1:
            accepted.append((st, en, n)); cur = n
        elif cur + 1 < n <= cur + 1 + max_gap and (nxt is None or nxt in (n + 1, n + 2) or not accepted):
            accepted.append((st, en, n)); cur = n
        elif nxt == cur + 2 and accepted:
            notes.append(f"{label}: line number {n} read as {cur + 1}")
            accepted.append((st, en, cur + 1)); cur += 1
        # anything else is a number belonging to the text
    verses: "OrderedDict[int, str]" = OrderedDict()
    prev = 0
    for j, (st, en, n) in enumerate(accepted):
        end = accepted[j + 1][0] if j + 1 < len(accepted) else len(text)
        body = text[en:end]
        if j == 0 and n > start and text[:st].strip():
            _inline(text[:st], start, n - 1, verses, notes, label)   # unnumbered opening verse
        verses[n] = body
        if n > prev + 1 and prev:
            _inline(verses[prev], prev, n - 1, verses, notes, label)
        prev = n
    return verses


def _inline(body: str, first: int, last: int, verses, notes, label) -> None:
    """Look inside body (verse `first`) for the numbers first+1 … last."""
    want = list(range(first + 1, last + 1))
    pieces = []
    rest = body
    cur_no = first
    for k in want:
        m = re.search(rf"(?:(?<=[\s.,;:!?»”\"'’)])|^)[\[(]?{k}[\])]?[.,]?(?=\s|[A-ZÀ-ÝŒ«“\"])", rest)
        if not m:
            notes.append(f"{label}: verse {k} has no number of its own (left inside verse {cur_no or '?'})")
            continue
        pieces.append((cur_no, rest[:m.start()]))
        rest = rest[m.end():]
        cur_no = k
    pieces.append((cur_no, rest))
    for no, txt in pieces:
        if no is None:
            continue
        verses[no] = txt


def write_tsv(name: str, rows: list[tuple[str, int, int, str]]) -> Path:
    dest = HERE / name
    with dest.open("w", encoding="utf-8", newline="") as fh:
        fh.write("book\tchapter\tverse\ttext\n")
        for book, chap, verse, text in rows:
            text = tidy(text)
            if not text:
                continue
            assert "\t" not in text and "\n" not in text
            fh.write(f"{book}\t{chap}\t{verse}\t{text}\n")
    return dest


# --------------------------------------------------------------------------
# checking against the Vulgate
# --------------------------------------------------------------------------
def latin_counts() -> dict[tuple[str, int], int]:
    counts: Counter = Counter()
    with LATIN.open(encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            book, chap, _verse, _ = line.split("\t", 3)
            counts[(book, int(chap))] += 1
    return counts


def check(tsv: Path) -> str:
    """Verses per chapter against la.tsv; chapters off by more than two."""
    la = latin_counts()
    mine: Counter = Counter()
    seen = set()
    dup = 0
    with tsv.open(encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            book, chap, verse, _ = line.rstrip("\n").split("\t", 3)
            key = (book, int(chap), verse)
            dup += key in seen
            seen.add(key)
            mine[(book, int(chap))] += 1
    books = OrderedDict()
    for (book, chap), n in mine.items():
        books.setdefault(book, []).append((chap, n))
    out = [f"{tsv.name}: {sum(mine.values())} verses" + (f", {dup} duplicate keys" if dup else "")]
    for book, chaps in books.items():
        la_chaps = sorted(c for (b, c) in la if b == book)
        total_la = sum(la[(book, c)] for c in la_chaps)
        have = sum(n for _, n in chaps)
        first = {c: min(int(v) for (b, cc, v) in seen if b == book and cc == c) for c, _ in chaps}
        whole = [(c, n) for c, n in chaps if first[c] <= 2]
        off = [f"{c}: {n} vs la {la.get((book, c), 0)}" for c, n in sorted(whole)
               if abs(n - la.get((book, c), 0)) > 2]
        line = f"  {book}: {have} verses in {len(chaps)} chapters (la {total_la} in {len(la_chaps)})"
        part = [f"{c}:{first[c]}-{first[c] + n - 1}" for c, n in sorted(chaps) if first[c] > 2]
        if part:
            line += "; passage only: " + ", ".join(part)
        if off:
            line += "; chapters off by >2: " + ", ".join(off)
        missing = [c for c in la_chaps if (book, c) not in mine]
        if missing and len(chaps) > len(la_chaps) / 2:
            line += "; chapters absent: " + ",".join(map(str, missing))
        out.append(line)
    return "\n".join(out)


# --------------------------------------------------------------------------
# the texts (filled in below)
# --------------------------------------------------------------------------
BUILDERS: "OrderedDict[str, callable]" = OrderedDict()


def builder(key: str):
    def deco(fn):
        BUILDERS[key] = fn
        return fn
    return deco


# ---- wa · Walloon ---------------------------------------------------------
WA_HOST = "wa.wikisource.org"
WA_MAT = "Évangile selon saint Mathieu SLLW 1862/{}"
WA_MRK = "Evandjîle sorlon Marc/{}"
# Slips in the transcription, put right before the verses are cut (chapter ->
# list of (found, replacement)).  Each one was checked against the Vulgate.
WA_MAT_FIXES = {
    9: [("\n26. Comme Jèsus sortève", "\n27. Comme Jèsus sortève")],   # v. 26 is absent, "26." is v. 27
    13: [("\n30. El'sy raconta ine aute parabole", "\n31. El'sy raconta ine aute parabole")],
    14: [("l' fi di Diu.\" Estant oute", "l' fi di Diu.\"\n34. Estant oute")],
}


def _wiki_chapters(host, pattern, n_chapters, raw_name, book, fixes=None, label=""):
    romans = list(ROMAN)[:n_chapters]
    pages = mw_pages(host, [pattern.format(r) for r in romans], raw_name)
    rows, notes = [], []
    for chap, roman in enumerate(romans, 1):
        text = pages[pattern.format(roman)]
        for old, new in (fixes or {}).get(chap, []):
            assert old in text, (book, chap, old)
            text = text.replace(old, new)
        text = re.sub(r"(?m)^[ \t]*'''[^'\n]+'''[ \t]*$", "", text)   # bold section titles
        text = strip_wiki(text)
        text = re.sub(r"(?m)^\s*(Categoreye|Category|Catégorie):.*$", "", text)
        text = re.sub(r"(?m)^\s*[IVXL]+\.\s*$", "", text)          # chapter number line
        verses = split_numbered(text, notes, f"{book} {chap}")
        rows += [(book, chap, v, t) for v, t in sorted(verses.items())]
    for note in notes:
        sys.stderr.write(f"  note {label}{note}\n")
    return rows


@builder("wa-liege1862")
def build_wa_matthew():
    rows = _wiki_chapters(WA_HOST, WA_MAT, 28, "wa_wikisource_matthieu_sllw1862.json", "MAT", WA_MAT_FIXES)
    return [write_tsv("wa-liege1862.tsv", rows)]


@builder("wa-liege-rochefort")
def build_wa_mark():
    rows = _wiki_chapters(WA_HOST, WA_MRK, 16, "wa_wikisource_marc.json", "MRK")
    return [write_tsv("wa-liege-rochefort.tsv", rows)]


# ---- rup · Aromanian (Farsherot, Albania) ---------------------------------
VPL_CODES = {"MAR": "MRK", "JOH": "JHN", "1JO": "1JN", "2JO": "2JN", "3JO": "3JN", "PHI": "PHP",
             "JAM": "JAS", "EZE": "EZK", "JOE": "JOL", "NAH": "NAM", "SOL": "SNG"}


@builder("rup-farsherot")
def build_rup():
    fetch("https://ebible.org/Scriptures/translations.csv", "ebible_translations.csv")
    fetch("https://ebible.org/Scriptures/details.php?id=rup", "ebible_rup_details.html")
    fetch("https://ebible.org/rup/copr.htm", "ebible_rup_copr.htm")
    fetch("https://ebible.org/Scriptures/rup_usfm.zip", "ebible_rup_usfm.zip")
    vpl = fetch("https://ebible.org/Scriptures/rup_vpl.zip", "ebible_rup_vpl.zip")
    rows = []
    with zipfile.ZipFile(vpl) as zf:
        for line in zf.read("rup_vpl.txt").decode("utf-8-sig").splitlines():
            m = re.match(r"(\w{3}) (\d+):(\d+)\s+(.*)", line)
            if m:
                book = VPL_CODES.get(m.group(1), m.group(1))
                rows.append((book, int(m.group(2)), int(m.group(3)), m.group(4)))
    return [write_tsv("rup-farsherot.tsv", rows)]


# ---- oc · Occitan, Provençal (Mistral's Genesis) ---------------------------
def pdf_text(pdf: Path) -> str:
    """Text of a born-digital PDF (needs poppler's pdftotext on the PATH)."""
    return subprocess.run(["pdftotext", "-layout", str(pdf), "-"], check=True,
                          capture_output=True).stdout.decode("utf-8")


# Slips of the e-text (chapter -> (found, replacement)), checked against the Vulgate.
OC_GEN_FIXES = {
    1: [("E’mé lou vèspre e lou matin, acò faguè lou jour quatren.",
         "\n19. E’mé lou vèspre e lou matin, acò faguè lou jour quatren.")],
    5: [("\n5. Malaleèl, à seissanto-cinq an", "\n15. Malaleèl, à seissanto-cinq an"),
        ("\n6. E après la neissènço de Jarèd", "\n16. E après la neissènço de Jarèd")],
    18: [("\n3I - “D’abord", "\n31. - “D’abord")],
}


@builder("oc-provencal")
def build_oc_genesis():
    # NB: the work is public domain (Mistral died 1914; Paris, Champion, 1910),
    # but this e-text closes with "© CIEL d'Oc 1997 … Còpi interdicho" over its
    # typing and layout.  An image-only scan of the 1910 printing under the
    # Licence Ouverte is https://www.occitanica.eu/items/show/214.
    pdf = fetch("https://biblio.cieldoc.com/libre/integral/libr0066.pdf",
                "cieldoc_libr0066_mistral_genesi.pdf")
    text = pdf_text(pdf).replace("\f", "\n")
    text = text[text.index("CHAPITRE I\n"):text.rindex("__________\n\n           La Genèsi")]
    chapters = re.split(r"(?m)^\s*CHAPITRE\s+[IVXLl]+\s*$", text)[1:]
    assert len(chapters) == 50, len(chapters)
    rows, notes = [], []
    for chap, body in enumerate(chapters, 1):
        for old, new in OC_GEN_FIXES.get(chap, []):
            assert old in body, (chap, old)
            body = body.replace(old, new)
        body = re.sub(r"\(\d\)", "", body)                       # footnote calls
        body = re.sub(r"\b(?:[^\W\d_] ){4,}[^\W\d_]\b",          # "S e g n o u r" (letter-spaced)
                      lambda m: m.group(0).replace(" ", ""), body)
        body = re.sub(r"(?m)^\s*\*\s*$", "", body)
        verses = split_numbered(body, notes, f"GEN {chap}")
        rows += [("GEN", chap, v, t) for v, t in sorted(verses.items())]
    for note in notes:
        sys.stderr.write(f"  note {note}\n")
    return [write_tsv("oc-provencal.tsv", rows)]


# ---- frp · Franco-Provençal: the Prodigal Son at Vionnaz (Valais) ----------
FRP_INDEX = "Page:Gilliéron - Patois de la commune de Vionnaz (Bas-Valais), 1880.djvu/{}"


@builder("frp-vionnaz")
def build_frp_vionnaz():
    """Gilliéron prints the parable in his phonetic notation with a French gloss
    under each line and no verse numbers; every indented paragraph is one verse
    of Luke 15, except that verse 12 takes two (speech-frame, then the rest)."""
    titles = [FRP_INDEX.format(n) for n in range(132, 151)]
    pages = mw_pages("fr.wikisource.org", titles, "frws_gillieron_vionnaz_pages132-150.json")
    paragraphs: list[str] = []
    for n in (146, 147, 148):
        for cell in re.findall(r"(?m)^\|(?!-)(.*)$", pages[FRP_INDEX.format(n)]):
            cell = re.sub(r'^\s*style="[^"]*"\s*\|', "", cell)
            if "''" not in cell:
                continue                                    # the French gloss line
            new = "{{em|2}}" in cell
            line = tidy(strip_wiki(cell))
            if new or not paragraphs:
                paragraphs.append(line)
            elif paragraphs[-1].endswith("-"):               # word broken at the line end
                paragraphs[-1] = paragraphs[-1][:-1] + line
            else:
                paragraphs[-1] += " " + line
    assert len(paragraphs) == 23, len(paragraphs)
    verses = [paragraphs[0], paragraphs[1] + " " + paragraphs[2]] + paragraphs[3:]
    rows = [("LUK", 15, 11 + i, t) for i, t in enumerate(verses)]
    return [write_tsv("frp-vionnaz.tsv", rows)]


# ---- pcd · Picard of Amiens (É. Paris, 1863) -- Gallica OCR -----------------
PCD_ARK = "bd6t5346572x"
PCD_DIR = f"gallica_{PCD_ARK}_pcd_matthieu"
PCD_VIEWS = range(41, 171)        # views that carry the Gospel (preface before, appendix after)


def alto_lines(path: Path) -> list[tuple[float, float, str]]:
    """(HPOS, VPOS, text) for every OCR line of a Gallica ALTO page."""
    xml = path.read_text(encoding="utf-8", errors="replace")
    out = []
    for line in re.findall(r"<TextLine\b.*?</TextLine>", xml, flags=re.S):
        head = line[:line.index(">")]
        hpos = float(re.search(r'HPOS="([\d.]+)"', head).group(1))
        vpos = float(re.search(r'VPOS="([\d.]+)"', head).group(1))
        words = []
        for attrs in re.findall(r"<String\b([^>]*)>", line):
            kind = re.search(r'SUBS_TYPE="(\w+)"', attrs)
            if kind and kind.group(1) == "HypPart2":
                continue                                    # second half of a word cut at the line end
            key = "SUBS_CONTENT" if kind else "CONTENT"
            m = re.search(rf'(?<![A-Z_]){key}="([^"]*)"', attrs)
            if m:
                words.append(html.unescape(m.group(1)))
        if words:
            out.append((hpos, vpos, " ".join(words)))
    return out


@builder("pcd-amienois")
def build_pcd():
    """Raw OCR, not proofread.  Each scan shows a strip of the facing page, so
    lines are kept only inside the text block; verse 1 of a chapter has a drop
    capital and no number; chapters are counted from the CHAPIT headings that
    are not running heads."""
    fetch(f"https://gallica.bnf.fr/services/OAIRecord?ark={PCD_ARK}", f"{PCD_DIR}/OAIRecord.xml")
    fetch(f"https://gallica.bnf.fr/services/Pagination?ark={PCD_ARK}", f"{PCD_DIR}/Pagination.xml")
    GAP = "\x00GAP"
    chapters: list[tuple[str, list[str]]] = []          # (numeral as read, lines)
    missing = []
    for view in PCD_VIEWS:
        path = fetch(f"https://gallica.bnf.fr/RequestDigitalElement?O={PCD_ARK}&E=ALTO&Deb={view}",
                     f"{PCD_DIR}/alto_{view:03d}.xml", optional=True)
        if path is None:
            missing.append(view)
            if chapters and (not chapters[-1][1] or chapters[-1][1][-1] != GAP):
                chapters[-1][1].append(GAP)
            continue
        block = [l for l in alto_lines(path) if 150 < l[0] < 1500]   # drop the strip of the facing page
        for hpos, vpos, text in block:
            if re.fullmatch(r"[\divxlIVXL .]{1,6}", text) or re.match(r"SIN MAT", text):
                continue                                    # page number, running head
            head = re.match(r"(?i)[cog(]?h[aàâ]pi\w{0,2}\s+(\S+)", text)
            if head and len(text) < 18:
                if vpos > 580:                              # below the head line: a real chapter heading
                    chapters.append((head.group(1).upper().strip(".,"), []))
                continue
            if re.match(r"S.SINT .VANJIL|SLON$", text) or text.startswith("* L’italique") or text.startswith("de De Sacy"):
                continue
            if not chapters:
                continue
            if text.endswith("-") or text.endswith("- "):
                text = text.rstrip("- ") + "­"          # joined to the next line below
            chapters[-1][1].append(text)
    rows, notes = [], []
    chap = 0
    for numeral, lines in chapters:
        chap = ROMAN[numeral] if ROMAN.get(numeral) in (chap + 1, chap + 2) else chap + 1
        segments = "\n".join(lines).replace("­\n", "").split(GAP)
        last = 0
        for i, seg in enumerate(segments):
            if not seg.strip():
                continue
            if i == 0:
                verses = split_numbered(seg, notes, f"MAT {chap}")
            else:                                           # text after a page that is not in raw/ yet
                m = re.search(r"(?m)^\s*(\d{1,2})\s", seg)
                if not m:
                    notes.append(f"MAT {chap}: text after a missing page could not be keyed")
                    continue
                first = int(m.group(1))
                if first <= last:                           # the numbers start again: a chapter began unseen
                    chap, last = chap + 1, 0
                    notes.append(f"MAT {chap}: heading on a missing page, chapter number inferred")
                verses = split_numbered(seg[m.start():], notes, f"MAT {chap}", start=first)
            rows += [("MAT", chap, v, t) for v, t in sorted(verses.items())]
            last = max(list(verses) + [last])
    for note in notes:
        sys.stderr.write(f"  note {note}\n")
    if missing:
        sys.stderr.write(f"  pcd: {len(missing)} page views not downloaded yet ({missing[0]}–{missing[-1]}); "
                         "run again without --offline to fetch them\n")
    return [write_tsv("pcd-amienois.tsv", rows)]


# ---- nrf, gsc · the Prodigal Son from Favre's 1879 collection ---------------
FAVRE = "paraboledelenfan00favr"
# Luke 15:11-32.  archive.org's OCR of this book is too rough to trust word by
# word ("père" for the printed "pére", "1'" for "l'", …), so the two versions
# kept here were read against the page images saved under raw/ (leaves given
# below); the OCR text is only used to check that the right passage is cut out.
FAVRE_PROOFREAD = {
    "nrf-centre-normandie": ((157, 158), "en  patois  du  centre", """
11. Un homme avait deux éfants ;
12. Le pu jeune dit à sen pére : Men pére, qu'i fît, baillez-mei c'qui deit m'erveni d'votte bien. Et l'bonhomme lui fît dé lots d' sen bien.
13. Eune escousse apreux, l' pu jeune d' sé deux éfants ramâssit tout sen mâgot et s'n allit valeter ava lé pais lointains, ioù qu'i mangit tout sé quibus en bamboches.
14. Drès qu'il eut tout supai, v'là-t-i pas qu'eunne grand disette consommit tout çu pais-là, c' qui fît qu'i c'menchit à debinai.
15. Pour lors, i s'n allit et s' mint en condition cheux z'un particuyer du pais, qui l'envyit à eunne maison qu'il avait és camps, pour à celle fin qu'il y gardît lé cochons.
16. Quand qu'il y fut, il airait ben voulu s'rempli l' vente aveuques la grouée dé cochons, mais personne ne li en bailleit.
17. A la fin i s'mordit lé pouces et s' dit en li-même : Comben qu'i a d' domestiques cheux men pére qu'ont du pain en veux tu en v'là, et mei j' crève de faim landré.
18. Faut, tout d' sieutte, que j' voige trouvai men pére et que j' li dise : Papa, j'ons manquai au bon Gieu et à vous aussite ;
19. Je n' mérite pus qu'i m'appellent votte fieu, mettez-mei d' pére aveuques vos domestiques.
20. Là d'sus, i partit et s'n allit trouvai sen pére. Il'tait co loin, l' bonhomme l'aperchut, cha li fit piquiet, i courut à li, li saôtit au co et l'embranchit :
21. Et l' gâs li fît : Papa, qui dît, j'ons manquai au bon Gieu et à vous itou, dit i ; je n' méritons pus qu'i m'appellent votte fieu.
22. Pour lors l' pére fît à sé gens : Allais v's-en vitement qu'ri la pu belle blaôde et mettais-li su l' dos, coulais-li itou eunne bague au deigt et passais-li dé souyers és pieds.
23. Am'nais un viau gras et tuais-lei, faisons bombanche et rions notte content.
24. L' motif en est qu'notte garçon que v'là était défunt et il est r'ssucitait ; j' l'aviomes perdu et il est r'trouvai. Là d'sus, i c'menchirent à noçai.
25. Pour lors, sen garçon l'ainsnei qu'était és camps, ervint, et quand qu'i fut preuche la maison, il entendit lé musiqueux et lé danseux.
26. I huchit un d' sé gens et li d'mandit qu'i qu' c'était qu' cha.
27. L' domestique li réponit : Ch'est votte frére qu'est r'venu et votte pére a tuai un viau gras, pace qu'i l'a r'trouvai ben portant.
28. Cha l' fâchit-i pas, si ben qu'i n' voulait brin entrai ; sen pére sortit à celle fin d' li decidai.
29. L' gâs li fît : V'là deujà tant d'annaies que j' sieux à votte service et j' peux m' vantai, qu'i dît, qu'au grand jamais j' nons r'fusai d' faire que qu' ce seit qu' vos m'ayais c'mendai ; vos n' m'avais pas tant seulement bailli un cabri po m' diverti d'aveuques m's amis.
30. Mais sitôt qu' votte aôte fieu qu'a mangi sen bién aveuques un tas d' criatures est r'venu, v's avais tuai pou li l' viau gras.
31. Men garçon, qu' fît l' bonhomme, t'es tajoûs d'aveuques mei et tout c' que j'ons est à tei.
32. Fallais-i pas ben noçai et s' mette d' belle himeur, pisque ten frére que v'là qu'était défunt est r'ssucitai ; j' l'aviomes perdu et le v'là r'trouvai.
"""),
    "gsc-gers": ((81, 82, 83), "en  patois  gascon", """
11. Un home qu'aougouc dus hils.
12. Lou caddet qu'eou digouc : Pay baillats me la pourtioun qui'em rebencq s'eou ben : é lou pay eous partagec lou ben.
13. Quaouques jours aprés, é aprés aoüe ramassat tout soun deque, aquet maynat que partiscouc, é s'enangouc louylouy, deguens un païs oun s'aougouc leou tout couhounut en bioue dins lou derégloment.
14. Quand n'aougouc pas mes arre, üo gran' famino que se boutec en acquet païs, é lou maynat que coumencec à senti lou besouy.
15. Que s'en anec, é s'estaquec a un home d'aquet païs : aqueste que l'enbouyec à sa maysoun de campagno ouyata lous porcs.
16. Que s'aoure plëat lou bente dambe gran gay de las telos é peladuros que lous porcs minjaoüon é degun n'eou ne daüo.
17. Que rentrec en et-madich, é que digouc : Quantis journaliés n'an pas ets pan a-raguero deguens la maysoun de mon pay, é jou que mourichi aci de hame.
18. Qu'em lëouerey, qu'anirey enta moun pay, é qu'eou direy : Pay, qu'ey peccat cost'oou ceou é daounant bous.
19. Nou souy pas mes digne deou noum de boste hil : Traittas me coum'un d'eous bostes journaliés.
20. Que se lëouec, é que bengouc enta soun pay. Soun pay que l'apercebouc de louy, qu'en aougouc piatat, qu'eou courrouc aou daouant, que caijouc entre sous brassis, é que l'embrassec.
21. É soun hil qu'eouc digouc : Moun pay, qu'ey peccat cost'oou ceou é daouant bous : nou souy pas mes digne deou noum de boste hil.
22. Lou pay que digouc a sous baylets : Biste, biste, pourtat sa pruméro raoubo é boutats l'oc ; boutats lou la bago aou dit, é caoussats lou.
23. Amiats lou bedet gras, é tuats lou : minjen é hascan uo gran' hesto.
24. Pramou que moun hil ey tournat de mort en bito, que s'ero esgarat é que l'ey tournat trouba é la hesto que coumencec.
25. Sur aquet demey, lou hil aynat, qui ero aou camp, que s'en tournaoüo à l'oustaou, é quand n'estec proche, é entenouc lou brut d'eous instruments é de las dansos.
26. É apperec un baylet, el qu'eou demandec ço qu'ero que tout aco.
27. Aquet baylet qu'eou digouc : Boste fray qu'ey tournat, é de plaze de l'aoüe counserbat, boste pay qu'a heyt tua lou bedet gras.
28. L'aynat indignat nou boulëo pas entra, lou pay dounc que sourtiscouc, el se boutec aou prega.
29. Mes et digouc a soun pay : Que bous serbichi dempuch tant d'annados ; qu'ey toutjour heyt en tout bosto boulentat, et james nou m'aouëts dat un crabot ent'aou minja dampe mous amics.
30. É que tuats lou bedet gras à l'arribado de boste hil qui benc de se fricassa tou ço qu'aouëo dambe las putos.
31. Moun hil, s'aou digouc lou pay, tu qu'es toutjour dambe jou, é tou ço-de-men qu'ey ço de toun.
32. Mes be caléoüo hé hésto et s'arregaougi quand toun fray ey tournat de mort en bito, é s'ey tournat trouba aprés s'este esgarat.
"""),
}


def _favre(key: str) -> list[Path]:
    import difflib
    leaves, marker, proofread = FAVRE_PROOFREAD[key]
    ocr = fetch(f"https://archive.org/download/{FAVRE}/{FAVRE}_djvu.txt", f"ia_{FAVRE}_djvu.txt")
    for leaf in leaves:
        fetch(f"https://archive.org/download/{FAVRE}/page/n{leaf}.jpg", f"ia_{FAVRE}_pages/leaf_{leaf}.jpg")
    text = ocr.read_text(encoding="utf-8")
    start = text.index(marker)
    start = text.index("11.", start)
    end = re.search(r"\n32\..*?\n\s*\n\s*\n", text[start:], flags=re.S).end() + start
    slice_ = re.sub(r"\s+", " ", text[start:end])
    mine = re.sub(r"\s+", " ", proofread)
    ratio = difflib.SequenceMatcher(None, slice_, mine, autojunk=False).ratio()
    assert ratio > 0.85, (key, ratio)                  # same passage as the OCR, give or take its slips
    verses = split_numbered(proofread, start=11)
    assert sorted(verses) == list(range(11, 33)), sorted(verses)
    return [write_tsv(f"{key}.tsv", [("LUK", 15, v, t) for v, t in sorted(verses.items())])]


@builder("nrf-centre-normandie")
def build_nrf():
    return _favre("nrf-centre-normandie")


@builder("gsc-gers")
def build_gsc():
    return _favre("gsc-gers")


# ---- OCR of a scan whose text layer is not good enough (mwl) ----------------
TESSDATA = "https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/main/{}.traineddata"


def ocr_page(image_cmd: list[str], image: Path, out: Path, lang: str) -> None:
    """Run image_cmd (which must write `image`), then tesseract -> out.txt.
    Needs poppler, ImageMagick and tesseract; the language model is fetched
    into raw/tessdata."""
    import os
    fetch(TESSDATA.format(lang), f"tessdata/{lang}.traineddata")
    subprocess.run(image_cmd, check=True, capture_output=True)
    subprocess.run(["tesseract", str(image), str(out.with_suffix("")), "--tessdata-dir",
                    str(RAW / "tessdata"), "-l", lang, "--psm", "3"],
                   check=True, capture_output=True, env={**os.environ, "OMP_THREAD_LIMIT": "1"})
    image.unlink(missing_ok=True)


# ---- mwl · Mirandese (B. Fernandes Monteiro, 1894) -- own OCR ---------------
MWL_PDF = "commons_Revista_de_educacao_e_ensino_Vol_9.pdf"
MWL_URL = ("https://upload.wikimedia.org/wikipedia/commons/f/f8/"
           "Revista_de_educa%C3%A7%C3%A3o_e_ensino_%28Vol._9%29.pdf")
# (book, PDF pages) of the four instalments in the Revista de Educação e Ensino, vol. 9
MWL_PARTS = [("LUK", 1, range(155, 170)), ("1CO", 7, range(186, 189)),
             ("LUK", 5, range(256, 270)), ("LUK", 9, range(504, 512))]
MWL_CLITICS = r"(?:les?|l[oa]s?|me|te|se|nos|bos|mos)\b"


@builder("mwl-monteiro1894")
def build_mwl():
    """Luke 1-10 and 1 Corinthians 7.  NOT proofread: the printed nasal vowels
    ã ẽ ĩ õ ũ are beyond the Portuguese OCR model and come out as â/ê/î/ô/û, à,
    ã or bare vowels ("ũ filho" is read "à filho", "relaciõ" "relaciô"), so no
    ending with a nasal vowel can be trusted without the scan."""
    pdf = fetch(MWL_URL, MWL_PDF)
    ocr_dir = RAW / "ocr_mwl_revista1894"
    ocr_dir.mkdir(exist_ok=True)
    rows, notes = [], []
    for book, first_chapter, pages in MWL_PARTS:
        text = ""
        for n in pages:
            out = ocr_dir / f"p{n}.txt"
            if not out.exists():
                png = ocr_dir / f"q{n}-{n:03d}.png"
                ocr_page(["pdftoppm", "-r", "300", "-gray", "-f", str(n), "-l", str(n), "-png", str(pdf),
                          str(ocr_dir / f"q{n}")], png, out, "por")
            lines = out.read_text(encoding="utf-8").split("\n")
            while lines and (not lines[0].strip() or re.search(r"REVISTA DE EDUCA|EBANGELHO DE J|EVANGELHO DE S|"
                                                               r"EP[IÍ]STOLA DE S|BOLETIM", lines[0])):
                lines.pop(0)                                 # running head
            body = "\n".join(lines)
            body = re.split(r"(?m)^[ \t]*1 O som com que termina", body)[0]   # the one footnote
            text += body + "\n"
        text = re.split(r"\n[^\n]*BERNARDO[^\n]*MONTEIRO", text)[0]
        text = re.sub(r"[¹²³]", "", text)
        text = re.sub(r"(?m)^[^\w\n]{1,5}(?=\d{1,2}\. )", "", text)        # specks before a verse number
        text = re.sub(rf"-\n+(?={MWL_CLITICS})", "-", text)           # dixo-\nle keeps its hyphen
        text = re.sub(r"(?<=[^\W\d_])-\n+(?=[^\W\d_])", "", text)     # a word cut at the line end
        bodies = re.split(r"(?m)^\s*CAP[IÍ]TULO\b.*$", text)[1:]
        for chap, body in enumerate(bodies, first_chapter):
            verses = split_numbered(body, notes, f"{book} {chap}")
            rows += [(book, chap, v, t) for v, t in sorted(verses.items())]
    for note in notes:
        sys.stderr.write(f"  note {note}\n")
    order = {"LUK": 0, "1CO": 1}
    rows.sort(key=lambda r: (order[r[0]], r[1], r[2]))
    return [write_tsv("mwl-monteiro1894.tsv", rows)]


# @@BUILDERS@@


def main(argv: list[str]) -> None:
    global OFFLINE
    want = [a for a in argv if not a.startswith("--")]
    do_check = "--check" in argv
    OFFLINE = "--offline" in argv
    RAW.mkdir(parents=True, exist_ok=True)
    for key, fn in BUILDERS.items():
        if want and key not in want and key.split("-")[0] not in want:
            continue
        sys.stderr.write(f"{key}\n")
        for tsv in fn():
            print(check(tsv) if do_check else f"wrote {tsv.name}")


if __name__ == "__main__":
    main(sys.argv[1:])
