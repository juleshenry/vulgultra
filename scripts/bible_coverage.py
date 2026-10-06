#!/usr/bin/env python3
"""What the 36 lects have, and lack, of the Bible's vocabulary, and the forms themselves.

For every word of the Latin Bible (`scripts/build_bible_lexicon.py`) a lect
has a form by one of these routes, strongest first:

    reflex       Wiktionary lists the form under the Latin word as its descendant
    etymology    an entry of the lect says it comes from that Latin word
    cognate      an entry of a sister lect that comes from that Latin word
                 names the form as its cognate (`scripts/fetch_kaikki_cognates.py`)
    translation  the form and the Latin word stand in one translation table
                 of some Wiktionary: they translate the same sense; or the
                 form is the title of the lect's Wikipedia article on what
                 the Latin Wikipedia treats under the word
    bible        the lect's own Bible text has the form in the verses where
                 the Latin Bible has the word (`scripts/align_bible.py`)
    gloss        a dictionary entry of the lect is glossed with a key of the
                 Latin word in the gloss's language
    scan         as bible or gloss, but the text or the dictionary is a
                 machine reading of a printed page that nobody has proofread
                 and no other source has the form: the word is there, its
                 spelling may not be (a glossary table named *.scan.tsv)
    bridge       as gloss, but the key is a word of French (Spanish, ...) that
                 is itself only a gloss match for the Latin word: two steps

A **key** of a Latin word in English is one of its first senses in the Latin
dictionary; in any language, a headword whose translation table lists the
Latin word, or a sense that language's Wiktionary gives the Latin word; in French, Spanish, Portuguese, Italian, Catalan and Romanian,
also that language's reflex of the word and the word its Bible uses for it
(`scripts/align_bible_anchors.py`).

Dictionaries are everything `audit_grid_sources.dictionaries()` reads, the
extracts of the building-block harvest, the lects' own Wiktionaries
(`scripts/extract_native_wiktionaries.py`), the translation tables
(`scripts/extract_wikt_translations.py`, `scripts/fetch_kaikki_translations.py`),
the entries the German, Russian, Polish and other Wiktionaries have for
words of the lects, and the glossaries under `data/sources/glossaries/`. Where both sides name
a part of speech they must agree: a verb is not matched to a noun, nor the
numeral *decem* to a noun glossed with a word spelt like "ten".

Writes the candidate forms to `data/bible/lexicon/forms/{lect}.tsv`, each
with the routes and sources that give it, and the report
`docs/eval/bible_coverage.md`.

    python3 scripts/bible_coverage.py
"""

from __future__ import annotations

import collections
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import align_bible as align  # noqa: E402
import audit_grid_sources as audit  # noqa: E402
import build_bible_lexicon as bible  # noqa: E402
import build_building_blocks as blocks  # noqa: E402
from vulgultra.romance_swadesh import LECT_NAMES, SOURCE_LANGS  # noqa: E402

REPORT = ROOT / "docs" / "eval" / "bible_coverage.md"
POOL = ROOT / "data" / "bible" / "lexicon" / "forms"
TABLES = ROOT / "data" / "sources" / "wikt_translations"     # translation tables, one file per edition
NATIVE = ROOT / "data" / "sources" / "native_wikt"            # the lects' own Wiktionaries
ENTRIES = ROOT / "data" / "sources" / "wikt_entries"          # other editions' entries: code, word, pos, gloss
GLOSSARIES = ROOT / "data" / "sources" / "glossaries"         # {lect}/{source}.tsv: headword, gloss, gloss_lang, pos
ALIGNED = ROOT / "data" / "bible" / "lexicon" / "aligned"     # {lect}.tsv from the lects' Bible texts
ANCHOR_KEYS = ROOT / "data" / "bible" / "lexicon" / "anchor_keys.tsv"
COGNATES = ROOT / "data" / "sources" / "kaikki_full" / "cognates.tsv"
TITLES = ROOT / "data" / "sources" / "wikipedia" / "latin_titles.tsv"   # scripts/fetch_wikipedia_titles.py
TOP = 1000
TARGET = 2000
LATIN_CODES = {"la", "la-vul", "la-lat", "la-med", "la-ecc", "la-cla", "LL.", "VL.", "ML."}
ETYMOLOGY = {"inh", "inh+", "bor", "bor+", "der", "der+", "lbor", "slbor", "uder", "inh-lite"}
ROUTES = ("reflex", "etymology", "cognate", "translation", "bible", "gloss", "scan", "bridge")
# Bible texts that are a scan's text layer, not proofread (data/bible/lects/SOURCES-*.md). Where the reading
# is clean but for stray slips (Genoese and Friulian Matthew, Sursilvan John, Sicilian Song of Songs), a
# form read the same way in two verses is taken as read right. Where it goes wrong the same way every time
# (Romagnol Matthew after 7:2 loses the dots of ṡ ż ṅ, Mirandese Luke turns nasal vowels into other
# letters, Picard Matthew is a phonetic spelling the reader garbles), repetition proves nothing.
UNPROOFREAD = {"lij", "fur", "rm-sursilvan", "scn"}
MISREAD = {"rgn", "pcd-amienois", "mwl-monteiro1894"}
SCANNED = " (scan)"   # marks the source name of a glossary table read by machine and not proofread
# Glossary tables on disk that are not counted until their standing is decided (docs/decisions.md): an
# earlier stage of the lect (medieval Béarnais, Gascon charters), and written standards that are nobody's
# speech (Ladin Dolomitan, Micurà de Rü's common Ladin of 1833).
SET_ASIDE = ("-old.", "-charters.", ".ladin-dolomitan.", ".micura-de-ru.")
# One of these alone is a statement about the word; a gloss or a bridge wants a second witness.
STATED = ("reflex", "etymology", "cognate", "translation", "bible")
# The lects other dictionaries are glossed in; read first, so their forms can serve as keys.
ANCHORS = ("fr", "es", "pt", "it", "ca", "ro")
BRIDGE_KEYS = 6   # at most this many forms of an anchor lect stand in for a Latin word
# A form a gloss gives is also a witness to itself when it has the shape of the word's reflexes in the
# other lects (Romagnol sèmpar, glossed "always", beside sempre, siempre, semper): the dictionary speaks
# for the meaning and the shape for the descent. How alike two shapes must be, as `align_bible.resemblance`.
COGNATE_SHAPE = 0.55
ARTICLE = {
    "it": r"^(?:il|lo|la|i|gli|le|un|uno|una)\s+|^(?:l|un)'\s*", "es": r"^(?:el|la|los|las|un|una)\s+",
    "pt": r"^(?:o|a|os|as|um|uma)\s+", "ca": r"^(?:el|la|els|les|un|una)\s+|^l'\s*",
    "de": r"^(?:der|die|das|ein|eine|sich)\s+", "ro": r"^(?:a|un|o|se)\s+",
    "nl": r"^(?:de|het|een)\s+", "el": r"^(?:ο|η|το|οι|τα|ένας|μια|ένα)\s+",
}
# What a part of speech may be matched with: a name in one set matches a name in a set that shares a letter.
# V verb, N noun-like, D determiner-like (an adjective is both), Q numeral, F function word.
KIND = {
    **dict.fromkeys(("verb", "vblex", "vbser", "vbhaver", "vbmod", "v"), "V"),
    **dict.fromkeys(("noun", "n", "name", "np"), "N"), **dict.fromkeys(("adj", "adjective"), "ND"),
    **dict.fromkeys(("det", "pron", "prn", "article"), "DF"), "num": "QD",
    **dict.fromkeys(("adv", "prep", "pr", "conj", "cnjcoo", "cnjsub", "cnjadv", "particle", "intj", "ij", "postp",
                     "contraction"), "F"),
}
NOT_WORDS = {"character", "symbol", "suffix", "prefix", "interfix", "infix", "affix", "punct", "circumfix"}
# Editions whose translation tables were largely imported from the English one. A form and a Latin word
# in one of their tables still count; their headwords are not used as keys, since nobody here can tell
# two words spelt alike in Kurdish apart.
COPIES = {"zh", "ku", "ja"}


# Romanian as older books print it: a cedilla for the comma, and a grave accent on an infinitive (a apucà).
OLD_ROMANIAN = str.maketrans("şţŞŢàìèù", "șțȘȚaieu")


def parts(gloss: str, language: str) -> set[str]:
    """The senses a gloss names, without the article its language puts before a word."""
    if language == "ro":
        gloss = gloss.translate(OLD_ROMANIAN)
    article = ARTICLE.get(language)
    found = {re.sub(article, "", part).strip() if article else part for part in audit.gloss_parts(gloss)}
    return {part for part in found if part}


def word_class(pos) -> frozenset[str]:
    """The kinds a part of speech may be matched with; empty where the source does not say."""
    names = {pos} if isinstance(pos, str) else set(pos or ())
    return frozenset("".join(KIND.get(name, "") for name in names))


def agree(entry_class: frozenset[str], latin_classes: frozenset[str]) -> bool:
    return not entry_class or not latin_classes or bool(entry_class & latin_classes)


def witnesses(via: set[str]) -> int:
    """How many separate sources give a form: an edition's tables are one, a dictionary is one.

    A bridge is not counted: two sources that agree on the French word a form
    is glossed with say nothing about that French word and the Latin one.
    """
    names = set()
    for label in via:
        route, _, rest = label.partition(":")
        language, _, source = rest.partition(":")
        if route == "bridge":
            continue
        if route == "translation":
            edition = rest.removesuffix(".wiktionary")
            names.add("table:" + ("en" if edition in COPIES else edition))
        elif source == "table":
            names.add("table:" + ("en" if language in COPIES else language))
        elif source.removesuffix(".wiktionary") in COPIES:
            names.add("en.wiktionary")
        else:
            names.add(source or route)
    return len(names)


def extracts(lect: str) -> list[tuple[Path, str]]:
    """Every dictionary extract on disk for the lect, with the language of its glosses."""
    code = blocks.EXTRACT.get(lect, lect)
    found = [(blocks.FULL / f"{lect}.jsonl", "en"), (blocks.FRWIKT / f"{lect}.jsonl", "fr"),
             (blocks.WORDS / f"kaikki-{code}.jsonl", "fr" if lect in blocks.FRENCH_GLOSSED else "en")]
    return [(path, language) for path, language in found if path.is_file()]


def latin_words(form: str, forms: dict, words: dict) -> set[str]:
    """The Bible's words a cited Latin form stands for: itself, or the words it is a form of."""
    latin = bible.plain(form).strip("*- ")
    return ({latin} & words.keys()) or (forms.get(latin, set()) & words.keys())


class Tables:
    """The translation tables of every edition on disk."""

    def __init__(self, forms: dict, words: dict) -> None:
        self.same: dict[str, dict[str, dict[str, set[str]]]] = {}      # lect → Latin word → edition → forms
        self.keys: dict[str, dict[str, set[str]]] = {}                  # edition → Latin word → headwords
        self.listed: dict[str, dict[str, dict[str, set[str]]]] = {}    # edition → lect → headword → forms
        self.classes: dict[str, dict[str, frozenset[str]]] = {}         # edition → headword → kinds of its entries
        for path in sorted(TABLES.glob("*.tsv")):
            edition = path.stem
            groups: dict[tuple[str, str], dict[str, set[str]]] = collections.defaultdict(lambda: collections.defaultdict(set))
            with path.open(encoding="utf-8") as stream:
                next(stream)
                for line in stream:
                    fields = line.rstrip("\n").split("\t")
                    if len(fields) != 4 or " " in fields[3]:
                        continue
                    head, table, code, form = fields
                    # The Spanish edition numbers the senses a translation serves: 1, 1-2, 1,3.
                    number, _, served = table.partition(".")
                    for sense in (re.findall(r"\d+", served) or [""]) if edition == "es" else [served]:
                        groups[head, f"{number}.{sense}"][code].add(form)
                    pos = table.split(":")[0] if ":" in table else ""
                    if pos:
                        seen = self.classes.setdefault(edition, {})
                        seen[head.lower()] = seen.get(head.lower(), frozenset()) | word_class(pos)
            keys = self.keys.setdefault(edition, collections.defaultdict(set))
            listed = self.listed.setdefault(edition, collections.defaultdict(lambda: collections.defaultdict(set)))
            for (head, _), by_code in groups.items():
                latin = set().union(*(latin_words(form, {}, words) for form in by_code.get("la", ())))
                for word in latin:
                    keys[word].add(head.lower())
                for code, found in by_code.items():
                    if code == "la":
                        continue
                    listed[code][head.lower()] |= found
                    for word in latin:
                        self.same.setdefault(code, {}).setdefault(word, {}).setdefault(edition, set()).update(found)


def other_editions(words: dict):
    """(Edition → Latin word → the senses that edition gives it, lect → that edition's entries for its words)."""
    keys: dict[str, dict[str, set[str]]] = collections.defaultdict(lambda: collections.defaultdict(set))
    entries: dict[str, list[tuple[str, str, str, str]]] = collections.defaultdict(list)
    for path in sorted(ENTRIES.glob("*.tsv")):
        with path.open(encoding="utf-8") as stream:
            for row in csv.DictReader(stream, delimiter="\t", quoting=csv.QUOTE_NONE):
                if row["code"] == "la":
                    word = bible.plain(row["word"])
                    if word in words:
                        keys[path.stem][word] |= parts(row["gloss"], path.stem)
                else:
                    entries[row["code"]].append((path.stem, audit.nfc(row["word"]), row["pos"], row["gloss"]))
    return keys, entries


def anchor_bible_keys() -> dict[str, dict[str, set[str]]]:
    """Anchor language → Latin word → the words that language's Bible uses for it."""
    found: dict[str, dict[str, set[str]]] = collections.defaultdict(lambda: collections.defaultdict(set))
    if ANCHOR_KEYS.is_file():
        with ANCHOR_KEYS.open(encoding="utf-8") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                found[row["language"]][row["latin"]].add(row["word"].lower())
    return found


def glossary_source(stem: str, language: str) -> str:
    """The name a glossary table's rows are counted under: one per work, whatever its varieties and languages."""
    stem = stem.split(".")[0]
    if stem.startswith("wiktionary-kaikki"):   # other editions' entries, a second copy of data/sources/wikt_entries
        return f"{language}.wiktionary"
    for prefix, name in (("wiktionary-ro", "ro.wiktionary"), ("dewiktionary", "de.wiktionary"),
                         ("cowiktionary", "co.wiktionary"), ("kantoniko", "kantoniko")):
        if stem.startswith(prefix):
            return name
    dated = re.match(r".*?-(?:1[5-9]|20)\d\d", stem)   # author-year, then the variety: lespy-raymond-1887-bearnais-old
    if dated:
        return dated.group(0)
    return "-".join(stem.split("-")[:3]) if stem.startswith("apertium-") else stem


def named_cognates(forms: dict, words: dict) -> dict[str, dict[str, set[str]]]:
    """Lect → Latin word → the forms a sister lect's entry names as cognates."""
    found: dict[str, dict[str, set[str]]] = collections.defaultdict(lambda: collections.defaultdict(set))
    if COGNATES.is_file():
        with COGNATES.open(encoding="utf-8") as stream:
            for row in csv.DictReader(stream, delimiter="\t", quoting=csv.QUOTE_NONE):
                if " " not in row["form"]:
                    for word in latin_words(row["latin"], forms, words):
                        found[row["lect"]][word].add(audit.nfc(row["form"]))
    return found


def article_titles(words: dict) -> dict[str, dict[str, set[str]]]:
    """Lect → Latin word → the titles of the lect's Wikipedia articles on what the Latin one titles with the word."""
    found: dict[str, dict[str, set[str]]] = collections.defaultdict(lambda: collections.defaultdict(set))
    if TITLES.is_file():
        with TITLES.open(encoding="utf-8") as stream:
            for row in csv.DictReader(stream, delimiter="\t", quoting=csv.QUOTE_NONE):
                word = bible.plain(row["latin"])
                if word in words:
                    found[row["lect"]][word].add(audit.nfc(row["title"]))
    return found


def lect_evidence(lect: str, forms: dict, words: dict, foreign: list):
    """(Latin word → forms whose entry cites it, forms listed with a Latin translation,
    gloss language → sense → (form, word class, source)) for one lect."""
    cited: dict[str, set[str]] = collections.defaultdict(set)
    own_latin: dict[str, set[str]] = collections.defaultdict(set)
    senses: dict[str, dict[str, set[tuple[str, str, str]]]] = collections.defaultdict(lambda: collections.defaultdict(set))
    for path, language in extracts(lect):
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                entry = json.loads(line)
                head = audit.nfc(entry.get("word", ""))
                if not head or " " in head or entry.get("pos") in NOT_WORDS:
                    continue
                for template in entry.get("etymology_templates") or []:
                    args = template.get("args") or {}
                    if template.get("name") in ETYMOLOGY and args.get("2") in LATIN_CODES and args.get("3"):
                        for word in latin_words(args["3"], forms, words):
                            cited[word].add(head)
                for sense in entry.get("senses") or []:
                    for gloss in sense.get("glosses") or []:
                        for part in parts(gloss, language):
                            senses[language][part].add((head, word_class(entry.get("pos", "")), f"{language}.wiktionary"))
    for label, entries in audit.dictionaries(lect):
        for head, glossed, pos, language in entries:
            if " " not in head:
                for part in glossed:
                    for key in parts(part, language):
                        senses[language][key].add((head, word_class(pos), label))
    for edition, head, pos, gloss in foreign:
        for part in parts(gloss, edition):
            senses[edition][part].add((head, word_class(pos), f"{edition}.wiktionary"))
    native = NATIVE / f"{lect}.jsonl"
    if native.is_file():
        with native.open(encoding="utf-8") as stream:
            for line in stream:
                entry = json.loads(line)
                head = audit.nfc(entry["word"])
                if " " in head:
                    continue
                for latin in entry["latin"]:
                    for word in latin_words(latin, forms, words):
                        cited[word].add(head)
                for language, glosses in entry["glosses"].items():
                    for gloss in glosses:
                        if language == "la":
                            for word in latin_words(gloss, {}, words):
                                own_latin[word].add(head)
                        else:
                            senses[language][gloss.lower()].add((head, word_class(entry["pos"]), f"{lect}.wiktionary"))
    for path in sorted((GLOSSARIES / lect).glob("*.tsv")) if (GLOSSARIES / lect).is_dir() else ():
        if ".doubtful" in path.name or any(mark in path.name for mark in SET_ASIDE):
            continue    # rows their parser could not vouch for, or a table set aside
        with path.open(encoding="utf-8") as stream:
            for row in csv.DictReader(stream, delimiter="\t", quoting=csv.QUOTE_NONE):
                head = audit.nfc(row.get("headword") or "")
                if not head or " " in head:
                    continue
                for word in latin_words(row.get("latin_etymon") or "", forms, words) if row.get("latin_etymon") else ():
                    cited[word].add(head)
                language = row.get("gloss_lang") or ""
                source = glossary_source(path.stem, language) + (SCANNED if ".scan" in path.name else "")
                for part in parts(row.get("gloss") or "", language):
                    senses[language][part].add((head, word_class(row.get("pos") or ""), source))
    return cited, own_latin, senses


def aligned(lect: str) -> dict[str, dict[str, bool]]:
    """Latin word → the forms the lect's own Bible text has for it, each with whether its spelling can be trusted."""
    found: dict[str, dict[str, bool]] = collections.defaultdict(dict)
    path = ALIGNED / f"{lect}.tsv"
    if path.is_file():
        with path.open(encoding="utf-8") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                sound = (row["text"] not in UNPROOFREAD | MISREAD or row.get("proofread") == "1"
                         or row["text"] in UNPROOFREAD and int(row["links"]) >= 2)
                found[row["latin"]][row["form"]] = found[row["latin"]].get(row["form"], False) or sound
    return found


def main() -> None:
    words, forms = bible.dictionary(), bible.inflected()
    counts, _, _ = bible.count_words(words, forms)
    ranked = counts.most_common()
    explained = sum(counts.values())
    english = {word: {part for gloss in words[word]["glosses"][:2] for part in audit.gloss_parts(gloss)
                      if len(part.split()) <= 3} for word, _ in ranked}
    latin_class = {word: word_class(words[word]["pos"]) for word, _ in ranked}
    tables, bible_keys, cognates = Tables(forms, words), anchor_bible_keys(), named_cognates(forms, words)
    titles = article_titles(words)
    entry_keys, foreign_entries = other_editions(words)
    POOL.mkdir(parents=True, exist_ok=True)
    has: dict[str, dict[str, str]] = {}    # lect → Latin word → the strongest route that gives a form
    firm: dict[str, set[str]] = {}         # lect → Latin words with a stated form, or one two sources give
    anchor_forms: dict[str, dict[str, set[str]]] = {}   # anchor lect → Latin word → its forms, lowercased

    def keys_of(word: str, language: str) -> set[str]:
        found = set(tables.keys.get(language, {}).get(word, ())) | entry_keys.get(language, {}).get(word, set())
        if language == "en":
            return found | english[word]
        return found | {form.lower() for form in words[word]["reflexes"].get(language, ())} | bible_keys[language][word]

    for lect in (*ANCHORS, *(lect for lect in SOURCE_LANGS if lect not in ANCHORS)):
        cited, own_latin, senses = lect_evidence(lect, forms, words, foreign_entries.get(lect, []))
        from_text = aligned(lect)
        found: dict[str, str] = {}
        firm[lect] = set()
        with (POOL / f"{lect}.tsv").open("w", encoding="utf-8") as out:
            out.write("rank\tlatin\troute\tform\twitnesses\tvia\n")
            for rank, (word, _) in enumerate(ranked, 1):
                # form → the sources that give it, each named route:source
                given: dict[str, set[str]] = collections.defaultdict(set)
                for form in words[word]["reflexes"].get(lect, ()):
                    given[form].add("reflex:Latin entry")
                for form in cited.get(word, ()):
                    given[form].add("etymology:entry")
                for form in cognates.get(lect, {}).get(word, ()):
                    given[form].add("cognate:sister entry")
                for form in own_latin.get(word, ()):
                    given[form].add(f"translation:{lect}.wiktionary")
                for edition, listed in tables.same.get(lect, {}).get(word, {}).items():
                    for form in listed:
                        given[form].add(f"translation:{edition}.wiktionary")
                if "N" in latin_class[word]:   # an article is titled with a noun
                    for form in titles.get(lect, {}).get(word, ()):
                        given[form].add("translation:wikipedia")
                for language in (set(senses) | set(tables.listed)) - COPIES:
                    keys = keys_of(word, language)
                    stand_ins = set() if lect in ANCHORS else anchor_forms.get(language, {}).get(word, set()) - keys
                    for route, wanted in (("gloss", keys), ("bridge", stand_ins)):
                        for key in wanted:
                            for form, entry_class, source in senses.get(language, {}).get(key, ()):
                                if agree(entry_class, latin_class[word]):
                                    kind = "scan" if route == "gloss" and source.endswith(SCANNED) else route
                                    given[form].add(f"{kind}:{language}:{source}")
                            if agree(tables.classes.get(language, {}).get(key, frozenset()), latin_class[word]):
                                for form in tables.listed.get(language, {}).get(lect, {}).get(key, ()):
                                    given[form].add(f"{route}:{language}:table")
                # A candidate with one witness gets a second from its shape, if it looks like the family.
                family = None
                for form, via in given.items():
                    if any(label.startswith(STATED) for label in via) or witnesses(via) != 1:
                        continue
                    if family is None:
                        stem = word[:-2] if len(word) > 4 else word
                        family = [align.shape(stem)] + [align.shape(reflex) for reflexes in words[word]["reflexes"].values()
                                                        for reflex in reflexes[:2]]
                    if max(align.resemblance(align.shape(form), seen) for seen in family) >= COGNATE_SHAPE:
                        via.add("shape:family")
                # Last, so that a form read off an unproofread scan can be checked against the dictionaries.
                for form, proofread in from_text.get(word, {}).items():
                    label = "bible:text" if proofread or form in given else "scan:text"   # before given[form] makes the key
                    given[form].add(label)
                by_route = {route: {form for form, via in given.items() if any(v.startswith(route + ":") for v in via)}
                            for route in ROUTES}
                if lect in ANCHORS:   # the anchor's own forms, strongest first, as keys for the others
                    own = [form.lower() for route in ROUTES[:-1] for form in sorted(by_route[route])]
                    anchor_forms.setdefault(lect, {})[word] = set(list(dict.fromkeys(own))[:BRIDGE_KEYS])
                seen: set[str] = set()
                for route in ROUTES:
                    for form in sorted(by_route[route] - seen):
                        via = sorted(label.replace(" ", "_") for label in given[form])
                        out.write(f"{rank}\t{word}\t{route}\t{form}\t{witnesses(given[form])}\t{' '.join(via)}\n")
                        # Two witnesses make a form firm only if one of them is a dictionary's gloss in a
                        # trusted spelling: a scan and a family likeness do not add up to one.
                        if route in STATED or witnesses(given[form]) >= 2 and any(v.startswith("gloss:") for v in given[form]):
                            firm[lect].add(word)
                    seen |= by_route[route]
                    if by_route[route]:
                        found.setdefault(word, route)
        has[lect] = found
        print(f"{lect}: {len(found):,} words, {len(firm[lect]):,} firm", flush=True)
    lects_with = {word: sum(1 for lect in SOURCE_LANGS if word in has[lect]) for word, _ in ranked}
    top = [word for word, _ in ranked[:TOP]]
    reached = [lect for lect in SOURCE_LANGS if len(has[lect]) >= TARGET]
    firmly = [lect for lect in SOURCE_LANGS if len(firm[lect]) >= TARGET]
    lines = [
        "# What the lects have of the Bible's vocabulary", "",
        "Generated by `scripts/bible_coverage.py`. Do not edit by hand.", "",
        f"The Latin Bible has {len(ranked):,} distinct dictionary words "
        "([`bible_lexicon.md`](bible_lexicon.md)). A lect has a form for one of them by:", "",
        "- a **reflex**: Wiktionary lists the form under the Latin word;",
        "- an **etymology**: an entry of the lect says it comes from that Latin word;",
        "- a **cognate**: an entry of a sister lect that comes from that Latin word names the form as its cognate;",
        "- a **translation**: the form and the Latin word stand in one translation table of a Wiktionary, "
        "so they translate the same sense; or the form titles the lect's Wikipedia article on what the Latin "
        "Wikipedia treats under the word;",
        "- its **Bible**: the lect's own Bible text has the form in the verses where the Latin has the word "
        "(**scan**, counted apart: the text is an unproofread machine reading of a printed page and no "
        "dictionary has the form, so the word is there but its spelling needs checking against the page);",
        "- a **gloss**: a dictionary entry of the lect is glossed with a key of the Latin word (in English, "
        "one of the word's first senses; in any language, a headword whose translation table lists the Latin "
        "word, or a sense that language's Wiktionary gives it; in French, Spanish, Portuguese, Italian, Catalan and Romanian, also that language's reflex of "
        "the word and the word its Bible uses for it);",
        "- a **bridge**: the same in two steps, the key being a French or Spanish word that is itself only a "
        "gloss match for the Latin word.", "",
        "Each word is counted once, under the strongest route. A gloss or bridge match is a candidate to "
        "check, not a confirmed translation, so the table also counts the words that are **firm**: a form "
        "that a reflex, an etymology, a cognate note, a translation table or the lect's Bible gives; or that two separate "
        "sources give by a gloss; or that one source gives by a gloss and that has the shape of the word's reflexes "
        "in the other lects (a bridge alone never counts). **Share of the text** weighs each word by how often the Bible uses it. The forms, "
        "each with its sources, are in `data/bible/lexicon/forms/{lect}.tsv`.", "",
        f"{len(reached)} of {len(SOURCE_LANGS)} lects have a form for {TARGET:,} words or more; "
        f"{len(firmly)} have {TARGET:,} firm.", "",
        f"| lect | reflex | etymology | cognate | translation | Bible | gloss | scan | bridge | words with a form | firm "
        f"| of the {TOP:,} commonest | share of the text |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    table_start = len(lines) - 2
    order = sorted(SOURCE_LANGS, key=lambda lect: -len(has[lect]))
    for lect in order:
        found = has[lect]
        by = collections.Counter(found.values())
        text_share = 100 * sum(counts[word] for word in found) / explained
        mark = "" if len(found) >= TARGET else " ↓"
        lines.append(f"| {LECT_NAMES.get(lect, lect)} ({lect}) | " + " | ".join(f"{by[route]:,}" for route in ROUTES)
                     + f" | {len(found):,}{mark} | {len(firm[lect]):,} | {sum(1 for word in top if word in found)} "
                     f"| {text_share:.0f}% |")
    nowhere = [(word, n) for word, n in ranked if not lects_with[word]]
    thin = [(word, n) for word, n in ranked[:TOP] if 0 < lects_with[word] < 5]
    lines += [
        "", f"↓ marks a lect below {TARGET:,}.", "",
        "## What is missing", "",
        f"- **In no lect at all:** {len(nowhere):,} of the {len(ranked):,} words, "
        f"{100 * sum(n for _, n in nowhere) / explained:.0f}% of the text. "
        f"Among the {TOP:,} commonest: {sum(1 for word, _ in nowhere if word in set(top))}.",
        f"- **In fewer than five lects**, among the {TOP:,} commonest: {len(thin)}.",
        f"- **In thirty lects or more:** {sum(1 for word, _ in ranked if lects_with[word] >= 30):,} words; "
        f"in ten or more: {sum(1 for word, _ in ranked if lects_with[word] >= 10):,}.", "",
        "### The commonest words with a form in no lect", "",
        ", ".join(f"*{word}* ({n:,}; {words[word]['gloss'][:40]})" for word, n in nowhere[:80]), "",
        f"### Among the {TOP:,} commonest, in fewer than five lects", "",
        ", ".join(f"*{word}* ({words[word]['gloss'][:30]}; {lects_with[word]})" for word, _ in thin[:120]), "",
        f"### What each lect lacks among the {TOP:,} commonest", "",
        "| lect | missing | the commonest of them |", "|---|---:|---|",
    ]
    for lect in order:
        missing = [word for word in top if word not in has[lect]]
        lines.append(f"| {lect} | {len(missing)} | " + ", ".join(missing[:15]) + " |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[table_start - 2:table_start + 2 + len(order)]))


if __name__ == "__main__":
    main()
