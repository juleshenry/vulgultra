#!/usr/bin/env python3
"""Lespy & Raymond, Dictionnaire béarnais ancien et moderne (1887) -> headword/gloss tables.

Source: raw/dictionnaireba01lesp_djvu.txt and raw/dictionnaireba02lesp_djvu.txt,
the archive.org OCR text (ABBYY FineReader) of the two volumes.

The book prints MODERN Béarnais headwords in bold capitals and OLD Béarnais
ones (charters, fors, 14th-17th c. texts) in bold lower case (preface,
section VII: "ABOUGAT, DISE sont modernes; Abocat, Diser sont anciens").
An entry may open with a capital headword and go on with lower-case forms
(`ABERTI, Adbertir, avertir: ...`); those are mostly the old form of the word
(Abocat, Adbertir, Aberoo) but sometimes a present-day local variant
(`SAUTE-HEE, Saude-hee (Aspe)`), and the book does not say which. So three
files, by that typographic mark:

    lespy-raymond-1887-bearnais.tsv              headwords in capitals (modern)
    lespy-raymond-1887-bearnais-old.tsv          entries that open with a lower-case
                                                 headword (old Béarnais)
    lespy-raymond-1887-bearnais-other-forms.tsv  lower-case forms listed after a
                                                 capital headword (old form or
                                                 local variant, not told apart)

An entry is `HEAD[, HEAD...][ (Place)], [masc.,] gloss[: example. SOURCE.
Translation.][ —, further sense: ...]`. The gloss is the text up to the first
colon, full stop or dash; `—,` opens a further sense, which gets its own row.
Examples, quotations, etymologies and cross-references ("voy. X", "même
signif. que X") are cut; entries that are only a cross-reference are skipped.

Headwords are written in lower case (the capitals of the modern ones, the
initial capital of the others); nothing else is changed and no spelling is
repaired. Because the text is OCR, headwords are filtered rather than fixed:
  * a headword must consist of letters and hyphens only (no space, digit,
    apostrophe, stray punctuation, no capital inside a lower-case word,
    no "IJ", which is how the OCR misreads the bold U), and may carry no
    accented letter other than è, é and ç: the book's spelling uses no
    others, and in the OCR à, â, ë, ê, î, ï, ô, û, ù are specks read as accents;
  * the first headwords of successive entries must run alphabetically (the
    longest non-decreasing run is kept), which drops most misread headwords
    and most continuation lines mistaken for entries.
  * the book itself is the second witness: headwords recur in ordinary type
    in its examples and cross-references. A headword that never occurs
    there, while a spelling one confusable letter away does (C/G, é/è/e
    for capitals; n/u, f/t, c/e, i/l for lower case) and is not simply a
    French word, is dropped (BADENCE read "BADENGE", GAUCHÈRE read
    "GAUCHÉRE").
A gloss is kept only if every word of it is a known French word form (the
word list of Tesseract's French model, ocr/french-wordlist_tessdata-fra.txt,
plus data/sources/kaikki_full/fr_forms.tsv when present): this drops glosses
with OCR damage, at the price of some glosses that use rare French words.
Entries of the Supplément and Additions (end of vol. 2) are included.

    python3 parse_lespy-raymond-1887-bearnais.py
"""
from __future__ import annotations

import bisect
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT_MODERN = HERE / "lespy-raymond-1887-bearnais.tsv"
OUT_OLD = HERE / "lespy-raymond-1887-bearnais-old.tsv"
OUT_OTHER = HERE / "lespy-raymond-1887-bearnais-other-forms.tsv"

UP = "A-ZÀ-ÖØ-Þ"
LOW = "a-zà-öø-ÿ"
MODERN = rf"[{UP}][{UP}'’-]*"
OLD = rf"[{UP}][{LOW}'’-]+"
PAREN = r"(?:\s*\([^()]{1,60}\))?"
GENDER = r"(?:\s*,?\s*(?:masc|f[ée]m|plur|sing|subst|adj|adv)\s*(?:\.|(?=\s*,)))*"
# (volume file, first line of the dictionary, [section starts...], end)
VOLUMES = [
    ("dictionnaireba01lesp_djvu.txt", r"^A,\s+pronom", [], None),
    ("dictionnaireba02lesp_djvu.txt", r"^L,\s", [r"^SUPPLÉMENT\s*$", r"^ADDITIONS\s*$"], r"^FIN\s+DU\s+DEUXI"),
]
POS = [
    (r"\b(?:masc|f[ée]m|subst)\b\.?", "noun"), (r"\badj\b\.?", "adj"), (r"\badv\b\.?|\badverbe\b", "adv"),
    (r"\br[ée]f\b\.?|\bverbe\b|\bv\. ?(?:a|n)\b\.?", "verb"), (r"\bpr[ée]p\b\.?|\bpréposition\b", "prep"),
    (r"\bpron\b\.?|\bpronom\b", "pron"), (r"\bconj\b\.?|\bconjonction\b", "conj"), (r"\binterj", "other"),
]
SKIP_GLOSS = re.compile(
    r"(?i)^(?:voy\b|vov\b|v\.\s|m[êôe]me|au (?:f[ée]minin|masculin|plur|sing)|dim\b|aug\b|superdim|plur\.? de|f[ée]m\.? de|part\b|passé|prés\b|imparf|futur|"
    r"subj|impér|terminaison|ne s['’]emploie|se dit|s['’]emploie|dans\b|locution|cf\b|pour\b.*\bvoy|nom propre|"
    r"comme\b|ainsi|on dit|usité|employé|est |sont |c['’]est)")
ABBREV = r"(?:\b(?:masc|f[ée]m|plur|sing|subst|adj|adv|r[ée]f|fig|dim|aug|fr|esp|lat|cat|port|it|prov|v|p|etc|St|Ste|M|MM)|\b[A-Z])$"


# French word forms, to tell a clean French gloss from OCR debris: the word list inside Tesseract's
# French model (saved next to the OCR text) and, when the repository has it, its French forms table.
FRENCH_LISTS = [HERE / "ocr" / "french-wordlist_tessdata-fra.txt", HERE.parents[1] / "kaikki_full" / "fr_forms.tsv"]
ELIDED = {"quelqu", "lorsqu", "jusqu", "puisqu", "presqu", "aujourd", "quoiqu"}


def french_words() -> set[str]:
    words: set[str] = set()
    for path in FRENCH_LISTS:
        if path.is_file():
            with path.open(encoding="utf-8") as lines:
                for line in lines:
                    words.update(part.lower() for part in line.rstrip("\n").split("\t"))
    if not words:
        print("warning: no French word list found; glosses are not checked against one")
    return words


def is_french(gloss: str, words: set[str]) -> bool:
    """Every word of three letters or more is a known French form (capitalised names are let through)."""
    if not words:
        return True
    for token in re.findall(r"[A-Za-zÀ-ÿœŒ]+(?:-[A-Za-zÀ-ÿœŒ]+)*", gloss):
        low = token.lower()
        if len(low) < 3 or token[0].isupper() or low in words or low in ELIDED:
            continue
        if low.endswith(("s", "x")) and low[:-1] in words:
            continue
        if low.endswith("ment") and (low[:-4] in words or low[:-4] + "e" in words or low[:-5] in words):
            continue
        if "-" in low and all(len(part) < 3 or part in words for part in low.split("-")):
            continue
        return False
    return True


CONFUSABLE_CAPITALS = [("c", "g"), ("g", "c"), ("é", "è"), ("è", "é"), ("e", "é"), ("e", "è"), ("é", "e"), ("è", "e")]
CONFUSABLE_LOWER = CONFUSABLE_CAPITALS[2:] + [("n", "u"), ("u", "n"), ("f", "t"), ("t", "f"), ("c", "e"), ("e", "c"),
                                              ("i", "l"), ("l", "i")]


def running_text() -> dict[str, int]:
    """How often each word occurs in the book outside the capital headwords."""
    counts: dict[str, int] = {}
    for name, _, _, _ in VOLUMES:
        text = re.sub(r"-\s*\n\s*", "", (RAW / name).read_text(encoding="utf-8"))
        for token in re.findall(rf"[{UP}{LOW}]+(?:-[{UP}{LOW}]+)*", text):
            if not token.isupper():
                key = unicodedata.normalize("NFC", token.lower())
                counts[key] = counts.get(key, 0) + 1
    return counts


def contradicted(word: str, modern: bool, counts: dict[str, int], french: set[str]) -> bool:
    """The word never occurs in running text, but a spelling one confusable letter away does."""
    key = unicodedata.normalize("NFC", word.lower())
    if counts.get(key, 0) > (0 if modern else 1):     # a lower-case headword counts itself once
        return False
    for index, letter in enumerate(key):
        for seen, printed in (CONFUSABLE_CAPITALS if modern else CONFUSABLE_LOWER):
            if letter == seen:
                other = key[:index] + printed + key[index + 1:]
                if counts.get(other, 0) > 0 and other not in french:
                    return True
    return False


def fold(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    return re.sub(r"[^a-z]", "", "".join(c for c in text if not unicodedata.combining(c)))


def sections():
    """Lists of lines, one list per alphabetical run (main dictionary, Supplément, Additions)."""
    for name, start, marks, end in VOLUMES:
        lines = (RAW / name).read_text(encoding="utf-8").split("\n")
        lines = [re.sub(r"\s+", " ", line).strip() for line in lines]
        first = next(i for i, line in enumerate(lines) if re.match(start, line))
        last = next((i for i, line in enumerate(lines) if end and re.match(end, line)), len(lines))
        cuts = [first]
        for mark in marks:   # the last occurrence of each heading (the first may be a half-title)
            hits = [i for i in range(cuts[-1], last) if re.match(mark, lines[i])]
            if hits:
                cuts.append(hits[-1] + 1)
        cuts.append(last)
        for a, b in zip(cuts, cuts[1:]):
            yield lines[a:b]


HEAD_LINE = re.compile(rf"^(?:{MODERN}(?:-{MODERN})*){PAREN}\s*[,;.:!]")
OLD_LINE = re.compile(rf"^{OLD}(?: {OLD}| [{LOW}]+)?{PAREN}\s*[,;]")
RUNNING_HEAD = re.compile(rf"^(?:[{UP}.\s]{{1,7}}|\d{{1,3}}|[ivxlc]+)$")


def entries(lines: list[str]):
    """Entry texts: a headword line (capitals anywhere; lower case only after a blank line) to the next one."""
    current: list[str] = []
    blank = True
    for line in lines:
        if not line:
            blank = True
            continue
        if RUNNING_HEAD.match(line):
            continue
        starts = (HEAD_LINE.match(line) and not re.match(rf"^[{UP}]\.\s", line)) or (blank and OLD_LINE.match(line))
        if starts:
            if current:
                yield join(current)
            current = [line]
        elif current:
            current.append(line)
        blank = False
    if current:
        yield join(current)


def join(lines: list[str]) -> str:
    text = ""
    for line in lines:
        if text.endswith("-") and not text.endswith(" -"):
            text = text[:-1] + line          # line-break hyphen
        else:
            text = (text + " " + line).strip()
    return text


def split_heads(text: str):
    """([(headword, is_modern)], rest of the entry) or None."""
    heads: list[tuple[str, bool]] = []
    position = 0
    while True:
        found = re.match(rf"\s*({MODERN}|{OLD})({PAREN}){GENDER}\s*([,.;:!])\s*", text[position:])
        if not found:
            break
        word, separator = found.group(1), found.group(3)
        after = text[position + found.end():]
        if separator == "." and not found.group(0).endswith(" ") and after[:1].isalpha():
            return None                         # NOUBL.ETAT: a full stop inside a misread word
        modern = not re.search(rf"[{LOW}]", word)
        if heads and not modern and separator == "." and not re.match(rf"\s*[{LOW}(]", after):
            break                               # a capitalised French sentence, not a further headword
        heads.append((word, modern))
        position += found.end()
        if separator in ";:!" or not re.match(rf"[{UP}]", after):
            break
    if not heads:
        return None
    return heads, text[position:]


def first_clause(body: str) -> str:
    position = 0
    while True:
        found = re.search(r":|[—–]|\.(?=\s|$)|;\s*(?=[A-ZÀ-Þ«]|vo[yv]\b|m[êôe]me\b|cf\b)", body[position:])
        if not found:
            return body
        end = position + found.start()
        if found.group(0) == "." and re.search(ABBREV, body[:end]):
            position = end + 1
            continue
        return body[:end]


def clean_gloss(text: str) -> tuple[str, str]:
    """(gloss, pos) with leading grammatical and place marks removed."""
    pos = ""
    while True:
        found = re.match(r"\s*(?:\([^()]{1,60}\)|(?:masc|f[ée]m|plur|sing|subst|adj|adv|r[ée]f|fig|prép|pron|conj|interj)\s*(?:\.|(?=\s*,)))\s*[,;.]?\s*", text)
        if not found:
            break
        for pattern, name in POS:
            if not pos and re.search(pattern, found.group(0)):
                pos = name
        text = text[found.end():]
    text = re.sub(r",?\s*dans\s+\S{0,6}$", "", text)            # "..., dans F. B." cut at the siglum
    text = re.sub(r"\s*\([^()]*\)?\s*$", "", text)               # a closing parenthesis: Latin name, remark
    text = re.sub(r"\s+([,;])", r"\1", text).strip(" .,;:—–-«»\"")
    return text, pos


def sound_gloss(text: str) -> bool:
    """A short French definition, not OCR debris or a remark."""
    if not text or SKIP_GLOSS.match(text) or len(text) > 110 or not re.match(rf"[{LOW}]", text):
        return False
    if re.search(rf"[^{LOW}{UP} ,'’()\-]", text) or text.count("(") != text.count(")"):
        return False
    if re.search(rf"[{LOW}][{UP}]|\b[{LOW}]\b(?<![aàyôó])", text):   # bdMif; stray single letters
        return False
    return True


def valid_head(word: str, modern: bool) -> bool:
    if len(word) < 2 and word not in ("A", "E", "I", "O", "U", "Y"):
        return False
    if "IJ" in word or re.search(r"['’-]$|^['’-]|--", word):
        return False
    if re.search(r"[^A-Za-zèéçÈÉÇ-]", word):      # apostrophes in headwords are OCR specks (FRA'YROU)
        return False
    if modern:
        return re.fullmatch(rf"[{UP}]+(?:['’-][{UP}]+)*", word) is not None
    return re.fullmatch(rf"[{UP}][{LOW}]+(?:['’-][{LOW}]+)*", word) is not None


def longest_run(keys: list[str]) -> set[int]:
    """Indices of a longest non-decreasing subsequence."""
    tails: list[str] = []
    tail_index: list[int] = []
    previous = [-1] * len(keys)
    for i, key in enumerate(keys):
        slot = bisect.bisect_right(tails, key)
        if slot == len(tails):
            tails.append(key)
            tail_index.append(i)
        else:
            tails[slot] = key
            tail_index[slot] = i
        previous[i] = tail_index[slot - 1] if slot else -1
    keep, i = set(), tail_index[-1] if tail_index else -1
    while i >= 0:
        keep.add(i)
        i = previous[i]
    return keep


def main() -> None:
    modern_rows, old_rows, other_rows = [], [], []
    seen: set[tuple] = set()
    stats = {"entries": 0, "no_head": 0, "out_of_order": 0, "bad_head": 0, "contradicted": 0, "no_gloss": 0}
    words = french_words()
    counts = running_text()
    for lines in sections():
        parsed = []
        for text in entries(lines):
            stats["entries"] += 1
            split = split_heads(text)
            if not split:
                stats["no_head"] += 1
                continue
            parsed.append(split)
        keep = longest_run([fold(heads[0][0]) for heads, _ in parsed])
        for index, (heads, body) in enumerate(parsed):
            if index not in keep:
                stats["out_of_order"] += 1
                continue
            senses = []
            for number, segment in enumerate(re.split(r"\s*[—–]\s*,\s*", body)):
                gloss, pos = clean_gloss(first_clause(segment))
                if number == 0 and (not gloss or SKIP_GLOSS.match(gloss)):
                    break                       # a cross-reference or a remark, not a definition
                for part in gloss.split(";"):
                    part = part.strip(" ,.")
                    if sound_gloss(part) and is_french(part, words):
                        senses.append((part, pos))
            if not senses:
                stats["no_gloss"] += 1
                continue
            opens_modern = heads[0][1]
            if not valid_head(*heads[0]):
                stats["bad_head"] += 1
                continue                        # a misread first headword discredits the entry
            if contradicted(*heads[0], counts, words):
                stats["contradicted"] += 1
                continue
            for word, modern in heads:
                if not valid_head(word, modern):
                    stats["bad_head"] += 1
                    continue
                if contradicted(word, modern, counts, words):
                    stats["contradicted"] += 1
                    continue
                head = unicodedata.normalize("NFC", word.lower())
                target = modern_rows if modern else (other_rows if opens_modern else old_rows)
                for gloss, pos in senses:
                    key = (head, gloss, id(target))
                    if key not in seen:
                        seen.add(key)
                        target.append((head, gloss, pos))
    for path, rows in ((OUT_MODERN, modern_rows), (OUT_OLD, old_rows), (OUT_OTHER, other_rows)):
        with path.open("w", encoding="utf-8") as out:
            out.write("headword\tgloss\tgloss_lang\tpos\n")
            for head, gloss, pos in rows:
                out.write(f"{head}\t{gloss}\tfr\t{pos}\n")
        print(f"{path.name}: {len(rows)} rows, {len({r[0] for r in rows})} headwords")
    print(stats)


if __name__ == "__main__":
    main()
