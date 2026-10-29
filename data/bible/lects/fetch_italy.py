#!/usr/bin/env python3
"""Verse-keyed Bible text for the lects of Italy, the Alps and the Adriatic.

Downloads (once) into `raw/italy/` and rebuilds `{lect}[-{variety}].tsv` beside this file:
`book<TAB>chapter<TAB>verse<TAB>text`, one verse per row, USFM book codes as in
`data/bible/texts/la.tsv`, the source's own chapter and verse numbers. What each text is,
where it comes from and on what basis it is free to use is in `SOURCES-italy.md`.

    python3 data/bible/lects/fetch_italy.py              # fetch what is missing, build everything
    python3 data/bible/lects/fetch_italy.py vec pms      # only these outputs (prefix match)
    python3 data/bible/lects/fetch_italy.py --fetch-only # download, do not build
    python3 data/bible/lects/fetch_italy.py --check      # also compare verses per chapter with the Latin

Raw files are HTTP response bodies, untouched: MediaWiki `api.php` JSON (the wikitext of
the pages, with revision ids and timestamps) and Commons `imageinfo` JSON (which carries a
DjVu file's text layer). Nothing is fetched twice; delete a folder under `raw/italy/` to
fetch it again. `raw/italy/rejected/` holds OCR that was examined and not used.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw" / "italy"
LATIN = HERE.parent / "texts" / "la.tsv"
USER_AGENT = "vulgultra-research/0.1 (+noncommercial; lexical sourcing)"
PAUSE = 1.5  # seconds between requests, any host
_last_request = [0.0]

MUL, IT, VEC, LIJ, PMS, COMMONS = ("wikisource.org", "it.wikisource.org", "vec.wikisource.org",
                                   "lij.wikisource.org", "pms.wikisource.org", "commons.wikimedia.org")
FUR_DJVU = "File:Pietro dal Pozzo - Il Vangelo di S. Matteo volgarizzato in dialetto friulano.djvu"
RGN_DJVU = "File:É-vangëli-ṡgönd-s.-Matí.djvu"
CHRESTOMATHIE_I = "Pagina:Decurtins - Rätoromanische chrestomathie, I.djvu/"
CHRESTOMATHIE_VI = "Pagina:Decurtins - Rätoromanische chrestomathie, VI.djvu/"

# ---------------------------------------------------------------------------------------
# What is downloaded. kind "prefix": every page of a namespace whose title starts with
# `prefix`; "titles": the pages named; "imageinfo": file metadata (holds the DjVu text layer).
# ---------------------------------------------------------------------------------------
FETCH = {
    "vecws_veneziano": dict(kind="prefix", host=VEC, ns=102,
        prefix="Il Vangelo di S. Matteo volgarizzato in dialetto veneziano dal sig. Gianjacopo Fontana, Londra 1859.pdf/"),
    "itws_milanese": dict(kind="prefix", host=IT, ns=108,
        prefix="Antonio Picozzi - Il Vangelo di S. Matteo volgarizzato in dialetto milanese.djvu/"),
    "itws_bergamasco": dict(kind="prefix", host=IT, ns=108,
        prefix="Pasino Locatelli - Il Vangelo di S. Matteo volgarizzato in dialetto bergamasco.djvu/"),
    "lijws_genovese": dict(kind="prefix", host=LIJ, ns=250, prefix="U santu Evangeliu segundu Mattè.pdf/"),
    "mulws_romagnol": dict(kind="prefix", host=MUL, ns=104, prefix="É-vangëli-ṡgönd-s.-Matí.djvu/"),
    "mulws_giona_spano1861": dict(kind="prefix", host=MUL, ns=104, prefix="La profezia di Giona (Spano, 1861).djvu/"),
    "mulws_giona_abis1861": dict(kind="prefix", host=MUL, ns=104, prefix="La profezia di Giona (Abis, 1861).djvu/"),
    "mulws_cantico_siciliano": dict(kind="prefix", host=MUL, ns=104,
        prefix="Il Cantico de' Cantici di Salomone, volgarizzato in dialetto siciliano.djvu/"),
    "mulws_parabola_biondelli": dict(kind="prefix", host=MUL, ns=0, prefix="La parobola del Figliol Prodigo LMO"),
    "mulws_parabola": dict(kind="titles", host=MUL, titles=[
        "Parabola del Figliol Prodigo BAD", "Parabola del Figliol Prodigo MAR", "Parabola del Figliol Prodigo GRD",
        "Parabola del Figliol Prodigo CAZ", "Parabola del Figliol Prodigo BRA", "Parabola del Figliol Prodigo FOD",
        "Parabola del Figliol Prodigo AMP", "Parabola del Figliol Prodigo BAD (Flatscher)",
        "La Parabola del Figliol Prodigo BAD", "La Parabola del Figliol Prodigo MAR", "La Parabola del Figliol Prodigo GRD",
        "La Parabola del Figliol Prodigo CAZ", "La Parabola del Figliol Prodigo BRA", "La Parabola del Figliol Prodigo FOD",
        "La parabola del Figliol Prodigo DLM", "Pez dla parabula dl fi prodigo", "L figliuol prodigo"]),
    "itws_chrestomathie_vi": dict(kind="titles", host=IT,
        titles=[f"{CHRESTOMATHIE_VI}{page}" for page in range(545, 565)]),
    "itws_chrestomathie_i": dict(kind="titles", host=IT,
        titles=[f"{CHRESTOMATHIE_I}{page}" for page in range(117, 123)]),
    "pmsws_bibia": dict(kind="prefix", host=PMS, ns=0, prefix="La Bibia piemontèisa/"),
    "commons_djvu_text": dict(kind="imageinfo", host=COMMONS, titles=[FUR_DJVU, RGN_DJVU]),
    # Not text: the licence pms.wikisource states for its pages, and who wrote the Bible's presentation page.
    "pmsws_rights": dict(kind="query", host=PMS, params={
        "meta": "siteinfo", "siprop": "rightsinfo|general", "prop": "revisions", "rvprop": "ids|timestamp|user",
        "rvlimit": "50", "rvdir": "newer", "titles": "La Bibia piemontèisa/Presentassion"}),
}


def http_get(url: str) -> bytes:
    """One polite GET: fixed pause, the project's User-Agent, back off on 429/503."""
    for attempt in range(8):
        wait = PAUSE - (time.time() - _last_request[0])
        if wait > 0:
            time.sleep(wait)
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                body = response.read()
            _last_request[0] = time.time()
            return body
        except urllib.error.HTTPError as error:
            _last_request[0] = time.time()
            if error.code not in (429, 503) or attempt == 7:
                raise
            retry = error.headers.get("Retry-After", "")
            delay = min(int(retry), 180) if retry.isdigit() else 20 * (attempt + 1)
            print(f"  HTTP {error.code}, waiting {delay}s", file=sys.stderr, flush=True)
            time.sleep(delay)
    raise RuntimeError("unreachable")


def api_pages(host: str, folder: Path, params: dict) -> None:
    """Run a MediaWiki query to the end of its continuation, one raw JSON file per response."""
    base = {"action": "query", "format": "json", "formatversion": "2"}
    cont: dict = {}
    part = 0
    partial = folder.with_name(folder.name + ".part")
    partial.mkdir(parents=True, exist_ok=True)
    for stale in partial.glob("*.json"):
        stale.unlink()
    while True:
        body = http_get(f"https://{host}/w/api.php?" + urllib.parse.urlencode({**base, **params, **cont}))
        (partial / f"{part:03d}.json").write_bytes(body)
        part += 1
        reply = json.loads(body)
        if "error" in reply:
            raise RuntimeError(f"{host}: {reply['error']}")
        if "continue" not in reply:
            break
        cont = reply["continue"]
    partial.rename(folder)


def fetch(key: str) -> None:
    spec, folder = FETCH[key], RAW / key
    if folder.is_dir() and any(folder.iterdir()):
        return
    print(f"fetching {key} from {spec['host']}", flush=True)
    content = {"prop": "revisions", "rvprop": "ids|timestamp|content", "rvslots": "main"}
    if spec["kind"] == "prefix":
        api_pages(spec["host"], folder, {"generator": "allpages", "gapnamespace": spec["ns"],
                                         "gapprefix": spec["prefix"], "gaplimit": "50", **content})
    elif spec["kind"] == "titles":
        api_pages(spec["host"], folder, {"titles": "|".join(spec["titles"]), **content})
    elif spec["kind"] == "query":
        api_pages(spec["host"], folder, spec["params"])
    elif spec["kind"] == "imageinfo":
        api_pages(spec["host"], folder, {"titles": "|".join(spec["titles"]), "prop": "imageinfo",
                                         "iiprop": "url|size|mime|metadata|extmetadata"})


def wiki_pages(key: str) -> dict[str, str]:
    """title -> wikitext, from the raw API responses of one source."""
    pages: dict[str, str] = {}
    for path in sorted((RAW / key).glob("*.json")):
        for page in json.loads(path.read_bytes()).get("query", {}).get("pages", []):
            for revision in page.get("revisions", []):
                pages[page["title"]] = revision["slots"]["main"]["content"]
    return pages


def djvu_layer(file_title: str) -> list[str]:
    """Text layer of a DjVu file on Commons, page by page, as MediaWiki's imageinfo gives it."""
    for path in sorted((RAW / "commons_djvu_text").glob("*.json")):
        for page in json.loads(path.read_bytes())["query"]["pages"]:
            if page["title"] == file_title:
                metadata = {item["name"]: item["value"] for item in page["imageinfo"][0]["metadata"]}
                return [item["value"] for item in sorted(metadata["text"], key=lambda item: item["name"])]
    raise KeyError(file_title)


# ---------------------------------------------------------------------------------------
# Wikitext to plain text
# ---------------------------------------------------------------------------------------
NOINCLUDE = re.compile(r"<noinclude>.*?</noinclude>", re.S)
TEMPLATE = re.compile(r"\{\{([^{}]*)\}\}")
NAMED_ARG = re.compile(r"\s*[\w-]+\s*=")
# Templates whose last positional argument is the text they show.
SHOWS_TEXT = {"capolettera", "sc", "larger", "x-larger", "xx-larger", "xxx-larger", "smaller", "x-smaller",
              "letter-spacing", "indentatura", "big", "ec"}  # ec: misprint|correction, the correction is kept
ON_ITS_OWN_LINE = {"ct", "centra", "center", "centrato"}
VERSE_MARK = re.compile(r"\x01(\d+):(\d+)\x02\s*")
# Cyrillic letters that OCR put where Latin ones are printed (Ligurian pages, not proofread).
HOMOGLYPHS = str.maketrans("АВЕКМНОРСТХІЈЅаеорсухіјѕ", "ABEKMHOPCTXIJSaeopcyxijs")
ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
CHAPTER_HEAD = re.compile(r"^\W*(?:CAPP?O?|[CÇ]HAP|PSALM)\s*\.?\s*([IVXLC]+)\s*\.*\W*$", re.I)
PAGE_NUMBER = re.compile(r"^(?:\d{1,3}|[ivxlc]+)$")
RUNNING_TITLE = re.compile(r"^S\.\s*MAT\w*\s*\.?$", re.I)
SIGNATURE = re.compile(r"^[A-Z]\s?\d?$")
STRAY_TITLE = re.compile(r"S\s?\.\s?M\s?A\s?T\s?[IÍ]\s?E?\s?\.")
COLOPHON = re.compile(r"^(?:I|We) certify\b")


def roman(numeral: str) -> int:
    values = [ROMAN[letter] for letter in numeral.upper()]
    return sum(-v if i + 1 < len(values) and v < values[i + 1] else v for i, v in enumerate(values))


def _template(match: re.Match) -> str:
    name, *args = match.group(1).split("|")
    name = name.strip().lower()
    positional = [arg for arg in args if arg.strip() and not NAMED_ARG.match(arg)]
    if name == "v" and len(positional) >= 2:  # {{v|chapter|verse}}
        return f"\n\x01{positional[0].strip()}:{positional[1].strip()}\x02 "
    if name in SHOWS_TEXT:
        return positional[-1] if positional else ""
    if name == "rigaintestazione":  # in a page body: a heading set as a header line
        return "\n" + "\n".join(positional) + "\n"
    if name in ON_ITS_OWN_LINE:
        return "\n" + (positional[-1] if positional else "") + "\n"
    if name == "hyphenate":  # {{Hyphenate|s'ani-|s'anima}} … {{Hyphenate|ma|}}: the whole word, once
        return positional[1] if len(positional) > 1 else ""
    return ""


def plain(wikitext: str) -> str:
    """Page body as text: no page furniture, footnotes, tags or templates; a verse template
    becomes \\x01chapter:verse\\x02, centred lines stand alone."""
    text = NOINCLUDE.sub("", wikitext)
    text = re.sub(r"<ref[^>/]*/>|<ref[^>]*>.*?</ref>", "", text, flags=re.S)
    text = re.sub(r"<sup>.*?</sup>", "", text, flags=re.S)  # "[sic]" marks, folio letters
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    previous = None
    while previous != text:
        previous, text = text, TEMPLATE.sub(_template, text)
    text = re.sub(r"\[\[\s*(?:category|categorîa|categoria|file|figura|image|immagine)\s*:[^\]]*\]\]", "", text, flags=re.I)
    text = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</?(?:center|div|p|poem)\b[^>]*>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"'{2,}", "", text)
    return html.unescape(text).replace(" ", " ")


def tidy(text: str) -> str:
    """One verse: line-end hyphenation undone, whitespace collapsed, NFC."""
    text = re.sub(r"(?<=\w)[-¬]\s*\n\s*(?=[^\W\d_])", "", text)
    return " ".join(unicodedata.normalize("NFC", text.replace("\ufeff", "")).split())


def page_number(title: str) -> int:
    return int(title.rsplit("/", 1)[1])


def book_lines(pages: dict[str, str], *, homoglyphs: bool = False) -> list[str]:
    """The pages of a transcribed volume, in order, as lines of plain text."""
    lines: list[str] = []
    for title in sorted(pages, key=page_number):
        body = plain(pages[title])
        if homoglyphs:
            body = body.translate(HOMOGLYPHS)
        lines.extend(line.strip() for line in body.split("\n"))
    return lines


def layer_lines(pages: list[str]) -> list[str]:
    """Lines of an OCR text layer without page numbers, running heads and signature marks.
    A chapter line is a running head when it is the first line and the page number follows."""
    lines: list[str] = []
    for page in pages:
        body = [line.strip() for line in page.split("\n") if line.strip()]
        drop = {index for index, line in enumerate(body[:2]) if PAGE_NUMBER.match(line) or RUNNING_TITLE.match(line)}
        if len(body) > 1 and CHAPTER_HEAD.match(body[0].translate(HOMOGLYPHS)) and PAGE_NUMBER.match(body[1]):
            drop.add(0)  # recto: "CHAP. VI." over the page number
        body = [line for index, line in enumerate(body) if index not in drop]
        if body and SIGNATURE.match(body[-1]):
            body.pop()
        lines.extend(body)
    return lines


# ---------------------------------------------------------------------------------------
# Lines to verses
# ---------------------------------------------------------------------------------------
STRICT_NUMBER = re.compile(r"(\d{1,3})(?![\d°])\.?\s*(?=\S)")
# OCR gives O for 0 and l or I for 1 ("2O", "3l", "l7"); such a token must be followed by a space.
LOOKALIKE_NUMBER = re.compile(r"((?=[OlI]*\d)[\dOlI]{2,3})\.?\s+(?=\S)")
Row = list  # [book, chapter, verse, text]


def leading_numbers(line: str) -> list[tuple[int, int]]:
    """(number, where the text starts) for each way of reading a number at the start of the line."""
    found = []
    strict = STRICT_NUMBER.match(line)
    if strict:
        found.append((int(strict.group(1)), strict.end()))
    lookalike = LOOKALIKE_NUMBER.match(line)
    if lookalike:
        found.append((int(lookalike.group(1).translate(str.maketrans("OlI", "011"))), lookalike.end()))
    return found


def opens_in_capitals(line: str) -> bool:
    """A chapter's first verse is printed with its first word in capitals: "VIODIND po Jesu", "É LÍVAR dla"."""
    words = re.findall(r"[^\W\d_]+", line)[:2]
    if not words:
        return False
    if len(words[0]) >= 3:
        return words[0].isupper()
    return len(words) > 1 and words[0].isupper() and words[1].isupper() and len(words[1]) >= 2


def verses_from_lines(lines: list[str], book: str, *, last_chapter: int, notes: list[str], first_chapter: int = 1,
                      numbered_first: bool = False, headings_in_order: bool = False) -> list[Row]:
    """Split a book into verses.

    A chapter opens at a heading line ("CAP. V."). Its first verse is unnumbered, unless
    `numbered_first` (then what stands between the heading and "1" is a summary and is
    dropped). Later verses open at a {{v|c|n}} mark or at a line that starts with a number
    one to three above the current verse. Where OCR lost a heading, the chapter opens at a
    line whose first word is in capitals and which is followed by verse 2. With
    `headings_in_order` every heading opens the next chapter, whatever its numeral says.
    The colophon after the last chapter ends the book."""
    rows: list[list] = []
    chapter, verse = first_chapter - 1, 0

    def next_number(start: int) -> int | None:
        for later in lines[start:start + 15]:
            if CHAPTER_HEAD.match(later.translate(HOMOGLYPHS)):
                return None
            numbers = leading_numbers(later)
            if numbers:
                return numbers[0][0]
        return None

    for index, line in enumerate(lines):
        head = CHAPTER_HEAD.match(line.translate(HOMOGLYPHS))
        if head:
            number = roman(head.group(1))
            if number == chapter + 1 or headings_in_order:
                if number != chapter + 1:
                    notes.append(f"{book}: heading '{line}' taken as chapter {chapter + 1}")
                chapter, verse = chapter + 1, 0 if numbered_first else 1
                if not numbered_first:
                    rows.append([book, chapter, verse, []])
            elif number != chapter:  # a running head repeats the chapter; anything else is odd
                notes.append(f"{book}: heading '{line}' while in chapter {chapter}")
            continue
        if chapter < first_chapter:
            continue
        if chapter == last_chapter and COLOPHON.match(line):
            break
        mark = VERSE_MARK.match(line)
        if mark:
            if int(mark.group(1)) != chapter:
                notes.append(f"{book} {chapter}: verse template says {mark.group(1)}:{mark.group(2)}")
            verse = int(mark.group(2))
            rows.append([book, chapter, verse, [line[mark.end():]]])
            continue
        numbered = next(((n, end) for n, end in leading_numbers(line) if verse < n <= verse + 3), None)
        if numbered and not (numbered_first and verse == 0 and numbered[0] != 1):
            verse = numbered[0]
            rows.append([book, chapter, verse, [line[numbered[1]:]]])
            continue
        if numbered_first and verse == 0 and re.match(r"[^\W\d_]{2}", line) and line[:2].isupper() \
                and next_number(index + 1) == 2:  # "CAntà a Iehova …": a first verse printed without its number
            verse = 1
            rows.append([book, chapter, verse, [line]])
            continue
        if not numbered_first and verse >= 3 and opens_in_capitals(line) and next_number(index + 1) == 2:
            notes.append(f"{book} {chapter + 1}: chapter heading missing, opened at '{line[:30]}'")
            chapter, verse = chapter + 1, 1
            rows.append([book, chapter, verse, [line]])
            continue
        if line and verse:
            rows[-1][3].append(line)
    out = [[b, c, v, tidy("\n".join(parts))] for b, c, v, parts in rows if c <= last_chapter]
    return [row for row in out if row[3]]


def mend(rows: list[Row], anchors: dict[tuple[int, int], str], notes: list[str]) -> list[Row]:
    """Restore a verse that the source runs into the one before it: split at its number when
    the number stands inside the text ("… camina? 6 Perchèmo …"), else at the given first
    words (`anchors`, regular expressions keyed by chapter and verse). Other gaps are noted."""
    out: list[Row] = []
    for row in rows:
        if out and out[-1][:2] == row[:2] and row[2] == out[-1][2] + 2:
            before, missing = out[-1], out[-1][2] + 1
            cut = re.search(rf"(?<=\s){missing}\.?\s+(?=\S)", before[3])
            start = None
            if cut:
                start = (cut.start(), cut.end())
            elif (row[1], missing) in anchors:
                found = re.search(anchors[(row[1], missing)], before[3])
                if found:
                    start = (found.start(), found.start())
                    notes.append(f"{row[0]} {row[1]}:{missing} has no number in the source; split by hand at its first words")
            if start and before[3][:start[0]].strip():
                out.append([row[0], row[1], missing, before[3][start[1]:].strip()])
                before[3] = re.sub(r"\s+\.$", "", before[3][:start[0]].strip())  # the dot of a lost "6."
        out.append(row)
    for before, row in zip(out, out[1:]):
        if before[:2] == row[:2] and row[2] != before[2] + 1:
            notes.append(f"{row[0]} {row[1]}: verse {row[2]} follows {before[2]} "
                         f"(the text of the verses between is inside {row[1]}:{before[2]})")
    return out


def matthew(lines: list[str], notes: list[str], anchors: dict | None = None) -> list[Row]:
    return mend(verses_from_lines(lines, "MAT", last_chapter=28, notes=notes), anchors or {}, notes)


# ---------------------------------------------------------------------------------------
# The texts
# ---------------------------------------------------------------------------------------
def build_vec(notes):
    return matthew(book_lines(wiki_pages("vecws_veneziano")), notes)


def build_lmo_milanese(notes):
    return matthew(book_lines(wiki_pages("itws_milanese")), notes, {(22, 6): r"Gh.è staa di alter pœu"})


def build_lmo_bergamasco(notes):
    return matthew(book_lines(wiki_pages("itws_bergamasco")), notes,
                   {(5, 30): r"E se la tò mà drecia", (9, 29): r"Inalura lü al gh.à tocat"})


def build_lij(notes):
    return matthew(book_lines(wiki_pages("lijws_genovese"), homoglyphs=True), notes)


def clean_layer(rows: list[Row]) -> list[Row]:
    """What an OCR layer leaves inside the verses: the running title and page number of a
    page that begins mid-verse, stray figures (no verse of these editions has a figure in
    it, so a token of digits alone is not text), and after the last verse the marks of the
    printer's ornament ("! + 1 C")."""
    for row in rows:
        row[3] = " ".join(re.sub(r"(?<!\S)\d+(?!\S)", " ", STRAY_TITLE.sub(" ", row[3])).split())
    if rows:
        rows[-1][3] = re.sub(r"(?:\s+(?:[^\w\s]+|\w))+$", "", rows[-1][3])
    return rows


def build_fur(notes):
    return clean_layer(matthew(layer_lines(djvu_layer(FUR_DJVU)), notes))


def build_rgn(notes):
    """Morri's Matthew: the OCR layer of the scan, replaced verse by verse by the proofread
    transcription where there is one (chapters 1 to 6 and the start of 7)."""
    rows = clean_layer(matthew(layer_lines(djvu_layer(RGN_DJVU)), notes))
    proofread = matthew(book_lines(wiki_pages("mulws_romagnol")), notes)[:-1]  # its last verse may stop at a page end
    better = {(chapter, verse): text for _, chapter, verse, text in proofread}
    for row in rows:
        row[3] = better.get((row[1], row[2]), row[3])
    notes.append(f"MAT: {len(better)} verses (1:1 to {proofread[-1][1]}:{proofread[-1][2]}) are the proofread "
                 f"transcription, the rest is the scan's OCR layer")
    return rows


def jonah(key: str, notes: list[str]) -> list[Row]:
    return mend(verses_from_lines(book_lines(wiki_pages(key)), "JON", last_chapter=4, notes=notes), {}, notes)


def build_sc_logudorese(notes):
    return jonah("mulws_giona_spano1861", notes)


def build_sc_campidanese(notes):
    return jonah("mulws_giona_abis1861", notes)


# Only three pages of the Sicilian Song of Songs are transcribed; none of them has a chapter heading.
CANTICO_PAGES = {10: 1, 12: 2, 15: 4}


def build_scn(notes):
    rows: list[Row] = []
    pages = wiki_pages("mulws_cantico_siciliano")
    for title in sorted(pages, key=page_number):
        chapter = CANTICO_PAGES.get(page_number(title))
        if not chapter:
            notes.append(f"SNG: page {page_number(title)} has no chapter assigned; left out")
            continue
        verse = None
        for line in (line.strip() for line in plain(pages[title]).split("\n")):
            number = STRICT_NUMBER.match(line)
            if number and (verse is None or int(number.group(1)) == verse + 1):
                verse = int(number.group(1))
                rows.append(["SNG", chapter, verse, line[number.end():]])
            elif line and verse is not None:
                rows[-1][3] += "\n" + line
    return [[b, c, v, tidy(text)] for b, c, v, text in rows]


def prodigal(pieces: list[str], notes: list[str], label: str) -> list[Row]:
    """Luke 15:11-32 from 22 pieces of text, one per verse."""
    if len(pieces) != 22:
        notes.append(f"LUK 15: {label} has {len(pieces)} pieces, not 22; left out")
        return []
    return [["LUK", 15, 11 + index, tidy(piece)] for index, piece in enumerate(pieces)]


def split_at(pieces: list[str], starts: list[str]) -> list[str]:
    """Split the piece that contains each of `starts` in front of it."""
    for start in starts:
        for index, piece in enumerate(pieces):
            at = piece.find(start)
            if at > 0:
                pieces[index:index + 1] = [piece[:at], piece[at:]]
                break
    return pieces


# Haller 1832 prints one verse per line; where the transcription runs verses together they
# are split in front of these words.
HALLER = {
    "lld-badiot": ("Parabola del Figliol Prodigo BAD", []),
    "lld-mareo": ("Parabola del Figliol Prodigo MAR", []),
    "lld-gherdeina": ("Parabola del Figliol Prodigo GRD",
                      ["Chest li ha dit: Ti frá", "Ma el se ha desená", "Ma dopoché cest ti fí", "Ma ad el al dit"]),
    "lld-fascian-cazet": ("Parabola del Figliol Prodigo CAZ", ["Ma fer nozza"]),
    "lld-fascian-brach": ("Parabola del Figliol Prodigo BRA", []),
    # Haller's Fodom version is on Wikisource only in the editors' modern spelling.
    "lld-fodom": ("La Parabola del Figliol Prodigo FOD", ["L clama un dei servidous", "E chëst i disc: To fradel"]),
}


def build_haller(name: str):
    def build(notes):
        title, starts = HALLER[name]
        body = wiki_pages("mulws_parabola")[title].split('margin:0 auto">', 1)[-1]
        lines = [line.strip() for line in plain(body).split("\n") if line.strip()]
        lines = [line for line in lines if not re.match(r":|La Parabola del Figliol Prodigo", line)]
        return prodigal(split_at(lines, starts), notes, title)
    return build


# Biondelli 1853 as retyped on Wikisource, one verse per line; the number is the subpage.
BIONDELLI = {"eml-bolognese": 3, "eml-ferrarese": 9, "eml-mirandolese": 13, "eml-modenese": 14,
             "eml-parmigiano": 16, "eml-reggiano": 17}


def build_biondelli(name: str):
    def build(notes):
        title = f"La parobola del Figliol Prodigo LMO/{BIONDELLI[name]}"
        lines = [line.strip() for line in plain(wiki_pages("mulws_parabola_biondelli")[title]).split("\n")]
        lines = [line for line in lines if line and not re.match(r"=|\d+\s*-|\(?\[?http|\(?Bernardino Biondelli", line)]
        return prodigal(lines, notes, title)
    return build


def build_dlm(notes):
    body = wiki_pages("mulws_parabola")["La parabola del Figliol Prodigo DLM"].split('margin:0 auto">', 1)[-1]
    pieces = re.split(r"(?:^|\s)(\d\d)\.\s", plain(body))
    numbers = [int(number) for number in pieces[1::2]]
    if numbers != list(range(11, 33)):
        notes.append(f"LUK 15: verse numbers found are {numbers}")
    return [["LUK", 15, number, tidy(text)] for number, text in zip(numbers, pieces[2::2])]


def build_rm_vallader(notes):
    """Psalms 90-106 of the Vulpius "Biblia pitschna" (1666) as reprinted by Decurtins. The
    reprint's page and folio marks and its marginal line numbers (multiples of five) go."""
    pages = wiki_pages("itws_chrestomathie_vi")
    lines: list[str] = []
    for line in book_lines(pages):
        if line.startswith("JACOBUS ANTHONIUS VULPIUS"):  # the next piece of the anthology
            break
        line = re.sub(r"\[[pf]\.[^\]]*\]|\[\d+\]", "", line)
        line = re.sub(r"(?<=\S) (?:5|[1-4][05]) (?=[^\W\d_])", " ", line)
        lines.append(line.strip())
    rows = verses_from_lines(lines, "PSA", first_chapter=90, last_chapter=106, notes=notes,
                             numbered_first=True, headings_in_order=True)
    return mend(rows, {(92, 6): r"Un narr nu sâ quai", (93, 3): r"O Jehova, ils flüms han aduzâ",
                       (104, 34): r"Meis plæd il völg esser accept"}, notes)


# The cross-references at the foot of a page of the reprint: "(i) Matt. 26, 69; Marc. 14, 66 — (k) Joh. 7, 14".
RM_FOOTNOTES = re.compile(r"\([a-z]\) (?:\d\. ?)?(?:Matt|Marc|Luc|Joh|Act|Jer|Psal|Ps|Esa|Jes|Zach|Exod|Gen|Num|Deut|Lev|"
                          r"Rom|Cor|Sam|Reg|Hebr|Mich|Prov|Dan|Hos|Apoc)\w*\.? \d+")


# Where each chapter's first verse begins, after the summary that follows the heading.
RM_OPENINGS = {18: "CUR ", 19: "Lura parnet"}


def build_rm_sursilvan(notes):
    """John 18-19 from Luci Gabriel's New Testament (1648) as reprinted by Decurtins. The pages
    are raw OCR, each one paragraph: running head, text with verse numbers ("16."), the
    reprint's marginal line numbers (no dot), reference letters "(i)", page marks, and the
    cross-references at the foot. Verse 1 of a chapter follows a summary (RM_OPENINGS)."""
    pages = wiki_pages("itws_chrestomathie_i")
    text = ""
    for title in sorted(pages, key=page_number):
        body = " ".join(plain(pages[title]).split())
        body = re.sub(r"^(?:Ilg Nief Testament \d+|\d+ Luci Gabriel)\s*", "", body)
        foot = RM_FOOTNOTES.search(body)
        if "DECLARATIUN." in body:  # Gabriel's note after 19:42, then the next piece of the anthology
            body = body[:body.index("DECLARATIUN.")]
        elif foot:
            body = body[:foot.start()]
        text += " " + body
    text = re.sub(r"\[[pf]\.[^\]]*\]|\([a-z]\)|…", " ", text)
    rows: list[Row] = []
    parts = re.split(r"Cap\. ([IVXLC]+)\.", text)
    for numeral, content in zip(parts[1::2], parts[2::2]):
        chapter = roman(numeral)
        opening = content.find(RM_OPENINGS.get(chapter, "\x00"))
        if opening < 0:
            notes.append(f"JHN {chapter}: the first words of its first verse are not known; left out")
            continue
        content = re.sub(r"(?<!\S)\d{1,2}(?!\S)", " ", content[opening:])
        pieces = re.split(r"(?<!\S)(\d{1,2})\.\s", content)
        rows.append(["JHN", chapter, 1, pieces[0]])
        for number, piece in zip(pieces[1::2], pieces[2::2]):
            if int(number) == rows[-1][2] + 1:
                rows.append(["JHN", chapter, int(number), piece])
            else:
                rows[-1][3] += f" {number}. {piece}"
    return mend([[b, c, v, tidy(t)] for b, c, v, t in rows], {}, notes)


# ---------------------------------------------------------------------------------------
# Piedmontese: "La Bibia piemontèisa" on pms.wikisource (one page per chapter, {{verse|chapter=|verse=}})
# ---------------------------------------------------------------------------------------
PMS_BOOKS = {
    "Genesi": "GEN", "Surtia": "EXO", "Levitich": "LEV", "Numeri": "NUM", "Deuteronomi": "DEU", "Giosue": "JOS",
    "Giudes": "JDG", "Rut": "RUT", "Samuel": ("1SA", "2SA"), "Re": ("1KI", "2KI"), "Cronache": ("1CH", "2CH"),
    "Esdra": "EZR", "Neemia": "NEH", "Ester": "EST", "Giob": "JOB", "Salm": "PSA", "Proverbi": "PRO",
    "Coelet": "ECC", "Cantich": "SNG", "Isaia": "ISA", "Geremia": "JER", "Complente": "LAM", "Esechiel": "EZK",
    "Daniel": "DAN", "Osea": "HOS", "Gioel": "JOL", "Amos": "AMO", "Abdìa": "OBA", "Abdia": "OBA", "Giona": "JON",
    "Michea": "MIC", "Naum": "NAM", "Abacuc": "HAB", "Sofonia": "ZEP", "Age": "HAG", "Sacaria": "ZEC",
    "Malachia": "MAL",
    "Maté": "MAT", "March": "MRK", "Luca": "LUK", "Gioann": "JHN", "At": "ACT", "Roman": "ROM",
    "Corint": ("1CO", "2CO"), "Galat": "GAL", "Efesin": "EPH", "Filipeis": "PHP", "Colosseis": "COL",
    "Tessaloniceis": ("1TH", "2TH"), "Timot": ("1TI", "2TI"), "Tito": "TIT", "Filemon": "PHM", "Ebreo": "HEB",
    "Giaco": "JAS", "Pero": ("1PE", "2PE"), "Gioann Litre": ("1JN", "2JN", "3JN"), "Giuda": "JUD",
    "Arvelassion": "REV",
}
# Deuterocanonical books are one page each. The last five are not separate books in the
# Vulgate (they sit inside Baruch, Esther and Daniel); they keep their own USFM codes.
PMS_DEUTERO = {
    "Tobia": "TOB", "Giudita": "JDT", "Sapiensa": "WIS", "Sirach": "SIR", "Baruch": "BAR", "Prim Macabé": "1MA",
    "Scond Macabé": "2MA", "Letra 'd Geremìa": "LJE", "Ester (version greca)": "ESG", "Stòria 'd Susan-a": "SUS",
    "Bel e 'l Dragon": "BEL", "Preghiera d'Azaria e Cantich ant la fornasa": "S3Y",
}
# "2Cronache 11" (with a space) is a stray copy of 1 Chronicles 11; the chapter itself is "2Cronache11".
PMS_SKIP = {"La Bibia piemontèisa/Testament Vej/Cronache/2Cronache 11"}
PMS_END = re.compile(r"^=+\s*'*\s*(?:N[òo]t[ea]|Version|Contnù)", re.I)
PMS_VERSE = re.compile(r"\{\{\s*verse\s*\|([^{}]*)\}\}", re.I)
# Editorial labels in square brackets: speakers in the Song of Songs, oracle titles in Amos.
PMS_LABEL = re.compile(r"\[(?:[^\[\]]*:|''[^\[\]]*''|Contra [^\[\]]*|A Giuda|Ch[^\[\]]*|Le fi[^\[\]]*)\]")
PMS_DECALOGUE = re.compile("'''[IVX]+\\.'''")  # the commandments, numbered in a table in Exodus 20


def pms_book(parts: list[str]) -> str | None:
    """USFM code of a page of the Piedmontese Bible, from its title path; None for what is not Bible text."""
    if len(parts) < 3 or not parts[1].startswith("Testament"):
        return None
    if any(re.match(r"(?i)introd", part) or "Coment" in part for part in parts[2:]):
        return None
    if parts[2] == "Deuterocanonich":
        return PMS_DEUTERO.get(parts[3]) if len(parts) == 4 else None
    code = PMS_BOOKS.get(parts[2])
    if isinstance(code, tuple):
        number = re.match(r"\s*([123])", parts[3]) if len(parts) > 3 else None
        return code[int(number.group(1)) - 1] if number and int(number.group(1)) <= len(code) else None
    return code if len(parts) <= 4 else None


def build_pms(notes):
    verses: dict[tuple[str, int, int], str] = {}
    for title, text in wiki_pages("pmsws_bibia").items():
        parts = title.split("/")
        code = pms_book(parts)
        if not code or title in PMS_SKIP or text.lstrip().startswith("#") or not PMS_VERSE.search(text):
            continue
        titled = re.search(r"(\d+)\s*$", parts[-1]) if len(parts) > 3 and parts[2] != "Deuterocanonich" else None
        text = re.sub(r"<ref[^>/]*/>|<ref[^>]*>.*?</ref>", "", text, flags=re.S)
        text = re.sub(r"</?(?:nowiki|sup|poem|blockquote|div|nowini)\b[^>]*>", "", text, flags=re.I)
        text = PMS_VERSE.sub(lambda match: "\x01" + match.group(1) + "\x02", text)
        text = re.sub(r"\{\{[^{}]*\}\}", "", text)
        text = re.sub(r"\[\[\s*(?:category|file|figura|image)\s*:[^\]]*\]\]", "", text, flags=re.I)
        text = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", text)
        text = PMS_LABEL.sub("", PMS_DECALOGUE.sub("", text))
        text = re.sub(r"'{2,}", "", text)
        body: list[str] = []
        for line in text.split("\n"):
            if PMS_END.match(line):
                break
            if re.match(r"\s*(?:=|\{\||\|[-}]|!|----|<references)", line):
                continue
            body.append(re.sub(r"^[|*#:;\s]+", "", line))
        pieces = re.split(r"\x01([^\x02]*)\x02", "\n".join(body))
        # A chapter page is its chapter, whatever `chapter=` says (it is often left over from the
        # page the editor copied); "31:55" in the verse field is the one way to say otherwise.
        home = int(titled.group(1)) if titled else None
        chapter, verse = home or 1, 0
        found: list[list] = []
        for index in range(1, len(pieces), 2):
            fields = dict(part.split("=", 1) for part in pieces[index].split("|") if "=" in part)
            given = fields.get("verse", "").strip()
            both = re.match(r"(\d+):(\d+)", given)
            if both:
                new_chapter = int(both.group(1))
            elif home:
                new_chapter = home
            elif fields.get("chapter", "").strip().isdigit():
                new_chapter = int(fields["chapter"])
            else:
                new_chapter = chapter
            if new_chapter != chapter:
                chapter, verse = new_chapter, 0
            number = re.match(r"\d+", given)
            if both:
                verse = int(both.group(2))
            elif number:
                verse = int(number.group())
            else:
                verse += 1
                notes.append(f"{code} {chapter}: a verse template without a number, taken as verse {verse}")
            content = re.sub(r"^\s*\(\d+:\d+\)", "", pieces[index + 1])
            content = tidy(html.unescape(content).replace(" ", " "))
            if content:
                found.append([chapter, verse, content])
        # A mistyped verse number ("5:4" between 5:39 and 5:41, "1:23" after 1:24) takes the
        # number its neighbours leave free.
        for index in range(1, len(found)):
            (before_chapter, before), (chapter, verse) = found[index - 1][:2], found[index][:2]
            after = found[index + 1][:2] if index + 1 < len(found) else None
            if chapter != before_chapter or verse == before + 1:
                continue
            if (after == [chapter, before + 2]) or (verse <= before and (after is None or after[0] != chapter)):
                notes.append(f"{code} {chapter}: verse numbered {verse} between {before} and "
                             f"{after[1] if after and after[0] == chapter else 'the end'}, taken as {before + 1}")
                found[index][1] = before + 1
        for chapter, verse, content in found:
            key = (code, chapter, verse)
            if key in verses:
                notes.append(f"{code} {chapter}:{verse} occurs twice; texts joined")
                verses[key] += " " + content
            else:
                verses[key] = content
    return [[*key, content] for key, content in verses.items()]


OUTPUTS = {
    "vec": build_vec,
    "lmo-milanese": build_lmo_milanese,
    "lmo-bergamasco": build_lmo_bergamasco,
    "pms": build_pms,
    "lij": build_lij,
    **{name: build_biondelli(name) for name in BIONDELLI},
    "rgn": build_rgn,
    "fur": build_fur,
    **{name: build_haller(name) for name in HALLER},
    "rm-sursilvan": build_rm_sursilvan,
    "rm-vallader": build_rm_vallader,
    "sc-logudorese": build_sc_logudorese,
    "sc-campidanese": build_sc_campidanese,
    "scn": build_scn,
    "dlm": build_dlm,
}


# ---------------------------------------------------------------------------------------
# Writing and checking
# ---------------------------------------------------------------------------------------
def latin() -> tuple[list[str], Counter]:
    """Book order and verses per (book, chapter) of the Vulgate file."""
    order: list[str] = []
    per_chapter: Counter = Counter()
    with LATIN.open(encoding="utf-8") as stream:
        next(stream)
        for line in stream:
            book, chapter, _ = line.split("\t", 2)
            if book not in order:
                order.append(book)
            per_chapter[(book, int(chapter))] += 1
    return order, per_chapter


def write(name: str, rows: list[Row], order: list[str]) -> None:
    rank = {book: index for index, book in enumerate(order)}
    rows.sort(key=lambda row: (rank.get(row[0], len(rank)), row[0], row[1], row[2]))
    with (HERE / f"{name}.tsv").open("w", encoding="utf-8", newline="") as out:
        out.write("book\tchapter\tverse\ttext\n")
        out.writelines(f"{book}\t{chapter}\t{verse}\t{text}\n" for book, chapter, verse, text in rows)


def compare(rows: list[Row], per_chapter: Counter) -> list[str]:
    """Chapters whose verse count differs from the Latin by more than two, book by book.
    Chapters the text does not have at all are not listed when it holds only part of a book."""
    mine = Counter((row[0], row[1]) for row in rows)
    lines = []
    for book in dict.fromkeys(row[0] for row in rows):
        theirs = {c for b, c in per_chapter if b == book}
        if not theirs:
            lines.append(f"{book}: not a book of la.tsv")
            continue
        held = {c for b, c in mine if b == book}
        whole = len(held) >= len(theirs)
        starts = {c: min(row[2] for row in rows if row[0] == book and row[1] == c) for c in held}
        off = [f"{c} ({mine[(book, c)]} vs {per_chapter[(book, c)]})" for c in sorted(held | theirs)
               if abs(mine[(book, c)] - per_chapter[(book, c)]) > 2 and (whole or starts.get(c) == 1)]
        if off:
            lines.append(f"{book}: " + ", ".join(off))
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("outputs", nargs="*", help="output names or prefixes (vec, lmo, pms, …); default: all")
    parser.add_argument("--fetch-only", action="store_true")
    parser.add_argument("--check", action="store_true", help="compare verses per chapter with the Latin")
    parser.add_argument("--notes", action="store_true", help="print every note, not the first eight per text")
    args = parser.parse_args()
    for key in FETCH:
        fetch(key)
    if args.fetch_only:
        return
    names = [name for name in OUTPUTS if not args.outputs or any(name.startswith(prefix) for prefix in args.outputs)]
    order, per_chapter = latin()
    for name in names:
        notes: list[str] = []
        rows = OUTPUTS[name](notes)
        if not rows:
            print(f"{name}: nothing built; {'; '.join(notes)}")
            continue
        write(name, rows, order)
        books = Counter(row[0] for row in rows)
        summary = ", ".join(f"{book} {count}" for book, count in books.items()) if len(books) < 6 else f"{len(books)} books"
        print(f"{name}: {len(rows)} verses ({summary}) -> {name}.tsv")
        for note in notes if args.notes else notes[:8]:
            print(f"    note: {note}")
        if len(notes) > 8 and not args.notes:
            print(f"    … {len(notes) - 8} more notes (--notes)")
        if args.check:
            for line in compare(rows, per_chapter):
                print(f"    differs from la.tsv by more than two verses: {line}")


if __name__ == "__main__":
    main()
