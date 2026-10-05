#!/usr/bin/env python3
"""Harvest the building-block words of each lect, and how its nouns form the plural.

Pronouns, numerals, prepositions, conjunctions, determiners and the small
adverbs come before any lexicon: every sentence needs them, and they are
picked by hand from what the daughters attest. This script gathers the
evidence for that pick from the dictionary extracts on disk and writes

    docs/building_blocks/{lect}.md          what one lect attests
    docs/eval/building_block_candidates.md  each meaning's shortest forms across lects
    docs/eval/plural_formation.md           plural patterns, lect by lect
    data/building_blocks/options.json       the top forms per meaning, for the pick

A lect's extract is, in this order: `data/sources/kaikki_full/{lect}.jsonl`
(scripts/fetch_kaikki_full.py), `data/sources/frwikt_blocks/{lect}.jsonl`
(scripts/extract_frwikt_blocks.py, French glosses), or
`data/words/kaikki-{lect}.jsonl`. A form is listed only where a dictionary
entry of that lect glosses it with the meaning. Nothing is filled in from a
sister lect; a lect with no extract on disk is named as missing.

    python3 scripts/build_building_blocks.py
"""

from __future__ import annotations

import collections
import functools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import audit_grid_sources as audit  # noqa: E402
from vulgultra.g2p import transcribe_and_repair  # noqa: E402
from vulgultra.phonology import count_syllables  # noqa: E402
from vulgultra.romance_swadesh import LECT_NAMES, SOURCE_LANGS  # noqa: E402

WORDS = ROOT / "data" / "words"
FULL = ROOT / "data" / "sources" / "kaikki_full"      # scripts/fetch_kaikki_full.py
FRWIKT = ROOT / "data" / "sources" / "frwikt_blocks"  # scripts/extract_frwikt_blocks.py
PAGES = ROOT / "docs" / "building_blocks"
SHORTLIST = ROOT / "docs" / "eval" / "building_block_candidates.md"
PLURALS = ROOT / "docs" / "eval" / "plural_formation.md"
OPTIONS = ROOT / "data" / "building_blocks" / "options.json"
# The extract of a lect, where its file is not named by the lect's code.
EXTRACT = {"eml": "egl"}
# Extracts beside the word lists whose glosses are French.
FRENCH_GLOSSED = ("gallo",)

# class → (the parts of speech an entry of that class may carry, its meanings).
# A meaning is the English word a dictionary glosses the form with.
CLASSES: dict[str, tuple[frozenset[str], tuple[str, ...]]] = {
    "Personal pronouns": (frozenset({"pron", "det"}), (
        "I", "me", "you", "thou", "thee", "he", "him", "she", "her", "it", "we", "us", "they", "them",
        "oneself", "himself", "myself", "yourself")),
    "Possessives": (frozenset({"det", "pron", "adj"}), (
        "my", "mine", "your", "yours", "his", "its", "our", "ours", "their", "theirs")),
    "Articles and demonstratives": (frozenset({"det", "article", "pron", "adj"}), (
        "the", "a", "an", "this", "that", "these", "those")),
    "Interrogatives and relatives": (frozenset({"pron", "det", "adv", "conj"}), (
        "who", "whom", "what", "which", "whose", "where", "when", "how", "why", "how much", "how many")),
    "Quantifiers and indefinites": (frozenset({"det", "pron", "adj", "adv"}), (
        "all", "every", "each", "some", "any", "no", "none", "nobody", "no one", "nothing", "something",
        "someone", "somebody", "everything", "everyone", "many", "much", "few", "little", "more", "less",
        "other", "same", "both", "enough", "too much")),
    "Numerals": (frozenset({"num", "adj", "noun", "det"}), (
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven",
        "twelve", "twenty", "thirty", "forty", "fifty", "hundred", "thousand", "first", "second", "third",
        "half")),
    "Prepositions": (frozenset({"prep", "postp", "adv", "contraction"}), (
        "of", "to", "in", "into", "on", "at", "with", "without", "for", "from", "by", "between", "among",
        "under", "over", "above", "before", "after", "until", "against", "through", "towards", "toward",
        "near", "behind", "during", "about", "since", "inside", "outside")),
    "Conjunctions": (frozenset({"conj", "particle", "adv"}), (
        "and", "or", "but", "if", "because", "that", "while", "as", "than", "nor", "although", "so",
        "then", "therefore")),
    "Adverbs and particles": (frozenset({"adv", "particle", "intj"}), (
        "yes", "no", "not", "also", "too", "only", "very", "already", "still", "yet", "now", "here",
        "there", "never", "always", "again", "well", "today", "yesterday", "tomorrow", "perhaps",
        "maybe", "almost")),
}
# The French words a French-glossed extract uses for each meaning.
FRENCH: dict[str, tuple[str, ...]] = {
    "I": ("je",), "me": ("me", "moi"), "you": ("tu", "vous", "toi"), "thou": ("tu",), "thee": ("te", "toi"),
    "he": ("il", "lui"), "him": ("le", "lui"), "she": ("elle",), "her": ("la",), "it": ("cela", "ça", "ce"),
    "we": ("nous", "on"), "us": ("nous",), "they": ("ils", "elles", "eux"), "them": ("les", "leur", "eux"),
    "oneself": ("se", "soi"), "himself": ("lui-même",), "myself": ("moi-même",), "yourself": ("toi-même",),
    "my": ("mon", "ma", "mes"), "mine": ("mien", "le mien"), "your": ("ton", "ta", "tes", "votre", "vos"),
    "yours": ("tien", "vôtre"), "his": ("son", "sa", "ses"), "its": ("son",), "our": ("notre", "nos"),
    "ours": ("nôtre",), "their": ("leur", "leurs"), "theirs": ("le leur",),
    "the": ("le", "la", "les", "l’", "l'"), "a": ("un", "une"), "an": (),
    "this": ("ce", "cet", "cette", "ceci", "celui-ci"), "that": ("cela", "ça", "celui-là", "celui"),
    "these": ("ces", "ceux-ci"), "those": ("ceux-là", "ceux"),
    "who": ("qui",), "whom": (), "what": ("que", "quoi", "quel"), "which": ("quel", "lequel"), "whose": ("dont",),
    "where": ("où",), "when": ("quand",), "how": ("comment",), "why": ("pourquoi",), "how much": ("combien",),
    "how many": ("combien",),
    "all": ("tout", "tous"), "every": ("chaque",), "each": ("chacun", "chaque"), "some": ("quelque", "quelques"),
    "any": ("n’importe quel", "aucun"), "no": ("aucun", "nul", "non"), "none": ("aucun",), "nobody": ("personne",),
    "no one": ("personne",), "nothing": ("rien",), "something": ("quelque chose",),
    "someone": ("quelqu’un", "quelqu'un"), "somebody": ("quelqu’un", "quelqu'un"), "everything": ("tout",),
    "everyone": ("tout le monde",), "many": ("beaucoup", "plusieurs"), "much": ("beaucoup",), "few": ("peu",),
    "little": ("peu",), "more": ("plus", "davantage"), "less": ("moins",), "other": ("autre",), "same": ("même",),
    "both": ("tous les deux", "les deux"), "enough": ("assez",), "too much": ("trop",),
    "zero": ("zéro",), "one": ("un",), "two": ("deux",), "three": ("trois",), "four": ("quatre",), "five": ("cinq",),
    "six": ("six",), "seven": ("sept",), "eight": ("huit",), "nine": ("neuf",), "ten": ("dix",), "eleven": ("onze",),
    "twelve": ("douze",), "twenty": ("vingt",), "thirty": ("trente",), "forty": ("quarante",),
    "fifty": ("cinquante",), "hundred": ("cent",), "thousand": ("mille",), "first": ("premier",),
    "second": ("deuxième", "second"), "third": ("troisième",), "half": ("demi", "moitié"),
    "of": ("de",), "to": ("à",), "in": ("dans", "en"), "into": ("dans",), "on": ("sur",), "at": ("à", "chez"),
    "with": ("avec",), "without": ("sans",), "for": ("pour",), "from": ("de", "depuis"), "by": ("par",),
    "between": ("entre",), "among": ("parmi",), "under": ("sous",), "over": ("par-dessus",),
    "above": ("au-dessus",), "before": ("avant", "devant"), "after": ("après",),
    "until": ("jusque", "jusqu’à", "jusqu'à"), "against": ("contre",), "through": ("à travers",),
    "towards": ("vers",), "toward": ("vers",), "near": ("près", "près de"), "behind": ("derrière",),
    "during": ("pendant", "durant"), "about": ("environ", "à propos de"), "since": ("depuis",),
    "inside": ("dedans",), "outside": ("dehors", "hors"),
    "and": ("et",), "or": ("ou",), "but": ("mais",), "if": ("si",), "because": ("parce que", "car"),
    "that": ("que",), "while": ("pendant que", "tandis que"), "as": ("comme",), "than": ("que",), "nor": ("ni",),
    "although": ("bien que", "quoique"), "so": ("donc", "alors"), "then": ("puis", "alors", "ensuite"),
    "therefore": ("donc",),
    "yes": ("oui",), "not": ("ne", "pas", "ne pas", "point"), "also": ("aussi",), "too": ("aussi", "trop"),
    "only": ("seulement",), "very": ("très",), "already": ("déjà",), "still": ("encore", "toujours"),
    "yet": ("encore",), "now": ("maintenant",), "here": ("ici",), "there": ("là",), "never": ("jamais",),
    "always": ("toujours",), "again": ("encore", "de nouveau"), "well": ("bien",),
    "today": ("aujourd’hui", "aujourd'hui"), "yesterday": ("hier",), "tomorrow": ("demain",),
    "perhaps": ("peut-être",), "maybe": ("peut-être",), "almost": ("presque",),
}

# A personal pronoun's cell: gloss word → (person, role), per gloss language.
ROLES = ("subject", "object", "indirect", "stressed", "reflexive")
PERSONS = ("1sg", "2sg", "2", "3sg m", "3sg f", "3sg n", "1pl", "2pl", "3pl", "3pl m", "3pl f", "3 reflexive")
PRONOUN_CELL: dict[str, dict[str, tuple[str, str]]] = {
    "en": {"i": ("1sg", "subject"), "me": ("1sg", "object"), "myself": ("1sg", "reflexive"),
           "thou": ("2sg", "subject"), "thee": ("2sg", "object"), "yourself": ("2sg", "reflexive"),
           "you": ("2", "subject"), "ye": ("2pl", "subject"), "you all": ("2pl", "subject"),
           "he": ("3sg m", "subject"), "him": ("3sg m", "object"), "himself": ("3sg m", "reflexive"),
           "she": ("3sg f", "subject"), "her": ("3sg f", "object"), "herself": ("3sg f", "reflexive"),
           "it": ("3sg n", "subject"), "we": ("1pl", "subject"), "us": ("1pl", "object"),
           "ourselves": ("1pl", "reflexive"), "they": ("3pl", "subject"), "them": ("3pl", "object"),
           "themselves": ("3pl", "reflexive"), "oneself": ("3 reflexive", "reflexive")},
    "fr": {"je": ("1sg", "subject"), "me": ("1sg", "object"), "moi": ("1sg", "stressed"),
           "tu": ("2sg", "subject"), "te": ("2sg", "object"), "toi": ("2sg", "stressed"),
           "il": ("3sg m", "subject"), "le": ("3sg m", "object"), "lui": ("3sg m", "stressed"),
           "elle": ("3sg f", "subject"), "la": ("3sg f", "object"), "nous": ("1pl", "subject"),
           "vous": ("2pl", "subject"), "ils": ("3pl m", "subject"), "elles": ("3pl f", "subject"),
           "les": ("3pl", "object"), "leur": ("3pl", "indirect"), "eux": ("3pl m", "stressed"),
           "se": ("3 reflexive", "reflexive"), "soi": ("3 reflexive", "stressed"), "on": ("3sg n", "subject")},
}
# Words in a gloss or its tags that move a pronoun to another role.
ROLE_WORDS = (
    ("reflexive", ("reflexive", "réfléchi")),
    ("indirect", ("dative", "indirect", "to me", "to you", "to him", "to her", "to us", "to them", "datif")),
    ("stressed", ("disjunctive", "stressed", "emphatic", "tonic", "prepositional", "oblique", "tonique", "disjoint")),
    ("object", ("accusative", "direct object", "objective", "object pronoun", "complément d’objet direct")),
)
# An article's kind: gloss word → kind, per gloss language.
ARTICLE_KIND = {"en": {"the": "definite", "a": "indefinite", "an": "indefinite"},
                "fr": {"le": "definite", "la": "definite", "les": "definite", "l’": "definite", "l'": "definite",
                       "un": "indefinite", "une": "indefinite", "des": "indefinite"}}
ARTICLE_CELLS = ("m sg", "f sg", "n sg", "m pl", "f pl", "n pl", "pl", "not given")
FRENCH_SHAPE = {"la": "f sg", "une": "f sg", "le": "m sg", "un": "m sg", "les": "pl", "des": "pl"}
# Forms of a noun that are a plain plural: nothing but number and gender.
PLAIN = {"plural", "masculine", "feminine", "neuter", "indefinite", "nominative", "accusative", "canonical"}
GENDERS = ("masculine", "feminine", "neuter")
CLOSED = {"pron", "det", "article", "prep", "postp", "conj", "particle", "contraction", "num"}
# Senses that are not the lect's plain current word.
SKIPPED = {"misspelling", "obsolete", "archaic", "dated", "rare", "neologism", "nonstandard", "proscribed",
           "humorous", "gender-neutral"}
EXAMPLES: dict[tuple[str, str, str], str] = {}


def extract_of(lect: str) -> Path:
    """The lect's extract: the full one, the French Wiktionary's, else the one beside the word lists."""
    for path in (FULL / f"{lect}.jsonl", FRWIKT / f"{lect}.jsonl"):
        if path.is_file():
            return path
    return WORDS / f"kaikki-{EXTRACT.get(lect, lect)}.jsonl"


def gloss_language(lect: str) -> str:
    return "fr" if lect in FRENCH_GLOSSED or extract_of(lect).parent == FRWIKT else "en"


@functools.cache
def entries(lect: str) -> tuple[dict, ...]:
    path = extract_of(lect)
    if not path.is_file():
        return ()
    with path.open(encoding="utf-8") as stream:
        return tuple(json.loads(line) for line in stream if line.strip())


@functools.cache
def reading(form: str, lect: str, pos: str) -> tuple[str, int] | None:
    """The form's sounds and syllable count, or None if the reader rejects it."""
    try:
        _, seq = transcribe_and_repair(form, lect, pos)
    except Exception:
        return None
    return "".join(seq), count_syllables(seq)


def senses(lect: str):
    """Every (form, part of speech, gloss, gloss parts, gloss and tags as one lowercase text, entry)."""
    for entry in entries(lect):
        form, pos = audit.nfc(entry.get("word", "")), entry.get("pos", "")
        if not form or " " in form or form[:1].isupper() and form != "I":
            continue
        for sense in entry.get("senses") or []:
            tags = list(sense.get("tags") or []) + list(entry.get("tags") or [])
            # me is entered as "accusative of yo": a closed-class word keeps such a sense.
            if SKIPPED & set(tags) or pos not in CLOSED and {"form-of", "alt-of"} & set(tags):
                continue
            for gloss in sense.get("glosses") or []:
                yield form, pos, gloss, audit.gloss_parts(gloss), f"{gloss} {' '.join(tags)}".lower(), entry


def keys(meaning: str, language: str) -> tuple[str, ...]:
    return (meaning.lower(),) if language == "en" else FRENCH.get(meaning, ())


def harvest(lect: str) -> dict[str, dict[str, list[tuple[str, str, str]]]]:
    """class → meaning → [(form, part of speech, the gloss as the dictionary gives it)]."""
    language = gloss_language(lect)
    found: dict[str, dict[str, list[tuple[str, str, str]]]] = {name: {} for name in CLASSES}
    for form, pos, gloss, parts, _, _ in senses(lect):
        for name, (allowed, meanings) in CLASSES.items():
            if pos not in allowed:
                continue
            for meaning in meanings:
                if any(key in parts for key in keys(meaning, language)):
                    rows = found[name].setdefault(meaning, [])
                    if not any(row[0] == form for row in rows):
                        rows.append((form, pos, gloss[:90]))
    return found


@functools.cache
def pronouns(lect: str) -> dict[tuple[str, str], list[str]]:
    """(person, role) → the lect's personal pronouns for that cell."""
    language = gloss_language(lect)
    table: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    for form, pos, _, parts, text, _ in senses(lect):
        if pos != "pron":
            continue
        for word, (person, role) in PRONOUN_CELL[language].items():
            if word not in parts:
                continue
            role = next((name for name, words in ROLE_WORDS if any(w in text for w in words)), role)
            if person == "2":
                person = "2pl" if any(w in text for w in ("plural", "pluriel", "you all")) else (
                    "2sg" if any(w in text for w in ("singular", "singulier")) else "2")
            if person == "3pl" and ("feminine" in text or "masculine" in text):
                person = "3pl f" if "feminine" in text else "3pl m"
            if form not in table[(person, role)]:
                table[(person, role)].append(form)
    return dict(table)


def shape(text: str, default: str = "not given") -> str:
    """Gender and number named in a gloss or a list of tags: m sg, f pl, pl."""
    gender = next((g[0] for g in GENDERS if g in text or g[:7] in text), "")
    number = "pl" if "plural" in text or "pluriel" in text else ("sg" if gender else "")
    return f"{gender} {number}".strip() or default


@functools.cache
def articles(lect: str) -> dict[tuple[str, str], list[str]]:
    """(definite or indefinite, gender and number) → the lect's articles for that cell."""
    language = gloss_language(lect)
    table: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    for form, pos, _, parts, text, entry in senses(lect):
        if pos not in ("article", "det"):
            continue
        for word, kind in ARTICLE_KIND[language].items():
            if word not in parts:
                continue
            cell = shape(text, FRENCH_SHAPE.get(word, "not given") if language == "fr" else "not given")
            if form not in table[(kind, cell)]:
                table[(kind, cell)].append(form)
            for other in entry.get("forms") or []:  # the feminine and plural an entry records for its headword
                tags = " ".join(other.get("tags") or [])
                inflected = audit.nfc(other.get("form", ""))
                if inflected and " " not in inflected and ("plural" in tags or "feminine" in tags):
                    gendered = any(g in tags for g in GENDERS)
                    other_cell = shape(tags if gendered else f"{'masculine' if cell.startswith('m') else ''} {tags}")
                    if inflected not in table[(kind, other_cell)]:
                        table[(kind, other_cell)].append(inflected)
    return dict(table)


def plural_pattern(singular: str, plural: str) -> str:
    """What turns the singular into the plural: an ending added, an ending replaced, nothing."""
    if singular == plural:
        return "no change"
    shared = 0
    while shared < min(len(singular), len(plural)) and singular[shared] == plural[shared]:
        shared += 1
    dropped, added = singular[shared:], plural[shared:]
    if not dropped:
        return f"+{added}" if len(added) <= 3 else "other"
    if len(dropped) <= 2 and len(added) <= 3:
        return f"-{dropped} +{added}" if added else f"-{dropped}"
    return "other"


def plurals(lect: str) -> dict[str, collections.Counter]:
    """gender → pattern → count, with one stored example per pattern in EXAMPLES."""
    table: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for entry in entries(lect):
        if entry.get("pos") != "noun" or " " in entry.get("word", ""):
            continue
        tags = {tag for sense in entry.get("senses") or [] for tag in sense.get("tags") or []} | set(entry.get("tags") or [])
        tags |= {arg for head in entry.get("head_templates") or [] for arg in (head.get("args") or {}).values()
                 if isinstance(arg, str)}
        gender = next((g for g in GENDERS if g in tags or g[0] in tags or f"{g[0]}-p" in tags), "gender not given")
        plural = next((audit.nfc(form["form"]) for form in entry.get("forms") or []
                       if "plural" in (form.get("tags") or []) and set(form.get("tags") or []) <= PLAIN
                       and form.get("form") and " " not in form["form"]), None)
        if plural:
            singular = audit.nfc(entry["word"])
            pattern = plural_pattern(singular, plural)
            table[gender][pattern] += 1
            EXAMPLES.setdefault((lect, gender, pattern), f"{singular} → {plural}")
    return table


def shown(form: str, lect: str, pos: str) -> str:
    read = reading(form, lect, pos)
    return f"*{form}* {read[0]} ({read[1]})" if read else f"*{form}* (not read)"


def grid(title: str, rows: tuple[str, ...], columns: tuple[str, ...], table: dict, lect: str, pos: str) -> list[str]:
    """A paradigm table: one row per first key, one column per second, forms with sounds and syllables."""
    used = [row for row in rows if any(table.get((row, column)) for column in columns)]
    if not used:
        return [f"## {title}", "", "Nothing on disk sorts into this table.", ""]
    lines = [f"## {title}", "", "| | " + " | ".join(columns) + " |", "|---|" + "---|" * len(columns)]
    for row in used:
        cells = [", ".join(shown(form, lect, pos) for form in table.get((row, column), [])) for column in columns]
        lines.append(f"| {row} | " + " | ".join(cells) + " |")
    return lines + [""]


def page(lect: str, found: dict, plural_table: dict) -> str:
    source = "French" if gloss_language(lect) == "fr" else "English"
    lines = [f"# {LECT_NAMES.get(lect, lect)} ({lect}): building blocks", "",
             "Generated by `scripts/build_building_blocks.py`. Do not edit by hand.", "",
             f"Each form is a dictionary headword of this lect that the {source} Wiktionary glosses with the "
             "meaning. **Sounds** is the pipeline's reading of the spelling, **σ** its syllable count; in the "
             "two paradigm tables a form is followed by its sounds and, in brackets, its syllable count. "
             "An empty row means no entry on disk has that gloss, not that the lect lacks the word.", ""]
    lines += grid("Personal pronouns, by person and role", PERSONS, ROLES, pronouns(lect), lect, "pron")
    lines += ["A pronoun glossed only *you*, with no number, is in row 2. The role is taken from the gloss "
              "(*me* is object, *to him* indirect, *disjunctive* stressed); where the dictionary does not say, "
              "the form sits in the column of its gloss word.", ""]
    lines += grid("Articles, by gender and number", ("definite", "indefinite"), ARTICLE_CELLS, articles(lect), lect, "det")
    for name, (_, meanings) in CLASSES.items():
        lines += [f"## {name}", "", "| meaning | form | sounds | σ | glossed as |", "|---|---|---|---:|---|"]
        for meaning in meanings:
            rows = found[name].get(meaning, [])
            if not rows:
                lines.append(f"| {meaning} | | | | |")
            for form, pos, gloss in rows:
                read = reading(form, lect, pos)
                sounds, sigma = read if read else ("not read", "")
                lines.append(f"| {meaning} | *{form}* | {sounds} | {sigma} | {gloss.replace('|', '/')} |")
        lines.append("")
    lines += ["## How nouns form the plural", ""]
    if not plural_table:
        lines += ["No noun on disk has a plural form recorded.", ""]
    for gender in (*GENDERS, "gender not given"):
        counts = plural_table.get(gender)
        if not counts:
            continue
        total = sum(counts.values())
        lines += [f"**{gender}** ({total} nouns)", "", "| singular → plural | nouns | share | example |", "|---|---:|---:|---|"]
        for pattern, n in counts.most_common(8):
            lines.append(f"| {pattern} | {n} | {100 * n // total}% | {EXAMPLES[(lect, gender, pattern)]} |")
        lines.append("")
    return "\n".join(lines)


def candidates(all_found: dict[str, dict]) -> list[tuple[str, str, int, list]]:
    """(section, meaning or cell, lects with a form, ranked sound shapes) for every row of the shortlist."""
    tables: list[tuple[str, str, int, list]] = []

    def add(section: str, label: str, attested: list[tuple[str, str, str]]) -> None:
        shapes: dict[tuple[int, str], list[str]] = collections.defaultdict(list)
        for lect, form, pos in attested:
            read = reading(form, lect, pos)
            if read:
                shapes[(read[1], read[0])].append(f"{lect} *{form}*")
        ranked = sorted(shapes.items(), key=lambda item: (item[0][0], -len({a.split()[0] for a in item[1]}), item[0][1]))
        tables.append((section, label, len({lect for lect, _, _ in attested}), ranked))

    for person in PERSONS:
        for role in ROLES:
            attested = [(lect, form, "pron") for lect in all_found for form in pronouns(lect).get((person, role), [])]
            if attested:
                add("Personal pronouns, by person and role", f"{person}, {role}", attested)
    for kind in ("definite", "indefinite"):
        for cell in ARTICLE_CELLS:
            attested = [(lect, form, "det") for lect in all_found for form in articles(lect).get((kind, cell), [])]
            if attested:
                add("Articles, by gender and number", f"{kind}, {cell}", attested)
    for name, (_, meanings) in CLASSES.items():
        for meaning in meanings:
            add(name, meaning, [(lect, form, pos) for lect, found in all_found.items()
                                for form, pos, _ in found[name].get(meaning, [])])
    return tables


def shortlist(tables: list, harvested: int) -> tuple[str, dict]:
    """The cross-lect page, and the same top rows as data for the pick."""
    meanings_of: dict[str, set[str]] = collections.defaultdict(set)
    for _, label, _, ranked in tables:
        for (_, sounds), _ in ranked:
            meanings_of[sounds].add(label)
    lines = ["# Building blocks: the shortest attested forms, meaning by meaning", "",
             "Generated by `scripts/build_building_blocks.py`. Do not edit by hand.", "",
             "For each meaning, every lect's forms are read and grouped by their sounds. A row is one sound "
             "shape, with the lects and spellings that attest it; rows are ordered by syllable count, then by "
             "the number of lects. Up to eight rows are shown. **Also** lists other meanings on this page that "
             "some lect expresses with the same sounds: picking both would make a homophone. **Lects with a "
             f"form** counts the lects whose extract has the gloss at all, out of {harvested} harvested. This "
             "is evidence for a pick by hand, not a pick.", ""]
    options: dict[str, dict[str, list[dict]]] = collections.defaultdict(dict)
    section = None
    for name, label, lects_with, ranked in tables:
        if name != section:
            lines += [f"## {name}", ""]
            section = name
        if not ranked:
            lines += [f"**{label}**: no form on disk.", ""]
            continue
        lines += [f"**{label}** (lects with a form: {lects_with})", "", "| σ | sounds | lects | attested as | also |",
                  "|---:|---|---:|---|---|"]
        options[name][label] = []
        for (sigma, sounds), attested in ranked[:8]:
            lects = len({a.split()[0] for a in attested})
            also = sorted(meanings_of[sounds] - {label})[:4]
            lines.append(f"| {sigma} | {sounds} | {lects} | {', '.join(attested[:8])} | {', '.join(also)} |")
            options[name][label].append({"sigma": sigma, "sounds": sounds, "lects": lects,
                                         "attested": attested[:8], "also": also})
        lines.append("")
    return "\n".join(lines), options


def plural_overview(tables: dict[str, dict]) -> str:
    lines = ["# How the daughters form the plural of a noun", "",
             "Generated by `scripts/build_building_blocks.py`. Do not edit by hand.", "",
             "For every noun whose dictionary entry records a plural, the plural is compared with the singular "
             "spelling: an ending added (`+s`), an ending replaced (`-o +i`), no change, or something else "
             "(a stem change, a suppletive plural). The three commonest patterns per gender are shown with "
             "their share of that gender's nouns. Counts follow what Wiktionary's editors entered, so a small "
             "lect's shares are rough.", "",
             "| lect | gender | nouns | commonest | second | third |", "|---|---|---:|---|---|---|"]
    for lect, table in tables.items():
        for gender in (*GENDERS, "gender not given"):
            counts = table.get(gender)
            if not counts or sum(counts.values()) < 5:
                continue
            total = sum(counts.values())
            top = [f"{pattern} {100 * n // total}% ({EXAMPLES[(lect, gender, pattern)]})" for pattern, n in counts.most_common(3)]
            lines.append(f"| {lect} | {gender} | {total} | " + " | ".join(top + [""] * (3 - len(top))) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    PAGES.mkdir(parents=True, exist_ok=True)
    harvested: dict[str, dict] = {}
    plural_tables: dict[str, dict] = {}
    missing = []
    for lect in SOURCE_LANGS:
        if not any(entry.get("pos") not in ("verb", None) for entry in entries(lect)):
            missing.append(lect)
            continue
        harvested[lect] = harvest(lect)
        plural_tables[lect] = plurals(lect)
        (PAGES / f"{lect}.md").write_text(page(lect, harvested[lect], plural_tables[lect]), encoding="utf-8")
    index = ["# Building blocks", "",
             "Generated by `scripts/build_building_blocks.py`. Do not edit by hand.", "",
             "Pronouns, possessives, articles, demonstratives, interrogatives, quantifiers, numerals, "
             "prepositions, conjunctions and the small adverbs, as each lect's dictionary entries attest "
             "them, and how its nouns form the plural. Cross-lect views: "
             "[shortest forms per meaning](../eval/building_block_candidates.md), "
             "[plural formation](../eval/plural_formation.md).", "",
             "| lect | glossed in | meanings with a form | forms | pronoun cells | nouns with a plural |",
             "|---|---|---:|---:|---:|---:|"]
    wanted = sum(len(meanings) for _, meanings in CLASSES.values())
    for lect, found in harvested.items():
        filled = sum(1 for by_meaning in found.values() for rows in by_meaning.values() if rows)
        forms = sum(len(rows) for by_meaning in found.values() for rows in by_meaning.values())
        nouns = sum(sum(counts.values()) for counts in plural_tables[lect].values())
        index.append(f"| [{LECT_NAMES.get(lect, lect)}]({lect}.md) | {'French' if gloss_language(lect) == 'fr' else 'English'} "
                     f"| {filled} of {wanted} | {forms} | {len(pronouns(lect))} | {nouns} |")
    index += ["", f"**No page.** No extract on disk for: {', '.join(missing) or 'none'}.", ""]
    (PAGES / "README.md").write_text("\n".join(index), encoding="utf-8")
    text, options = shortlist(candidates(harvested), len(harvested))
    SHORTLIST.write_text(text, encoding="utf-8")
    OPTIONS.parent.mkdir(parents=True, exist_ok=True)
    OPTIONS.write_text(json.dumps(options, ensure_ascii=False, indent=1), encoding="utf-8")
    PLURALS.write_text(plural_overview(plural_tables), encoding="utf-8")
    print("\n".join(index[6:]))
    print(f"Wrote {PAGES}/, {SHORTLIST.name}, {PLURALS.name}, {OPTIONS.name}")


if __name__ == "__main__":
    main()
