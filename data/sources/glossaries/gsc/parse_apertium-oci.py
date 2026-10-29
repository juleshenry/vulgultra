#!/usr/bin/env python3
"""Apertium Occitan-French and Occitan-Catalan dictionaries -> Gascon/Aranese tables.

Reads raw/apertium-oci-fra.oci-fra.dix, raw/apertium-oci-cat.oci-cat.dix and
Apertium's monolingual Occitan dictionary raw/apertium-oci.oci.metadix.

The bilingual dictionaries mark an entry alt="oci@gascon" (Gascon),
alt="oci@aran" (Aranese) or alt="oci" (Lengadocian: left out); an unmarked
entry serves every variety. An unmarked entry is not by itself a Gascon
word: its left side is a lemma key, and the monolingual dictionary decides
what each variety writes (lemma "nacional" + paradigm "principa/l_u" gives
Lengadocian "nacional" but Gascon "nacionau"). So for every pair the
headword is the citation form the monolingual dictionary GENERATES for the
variety (noun singular, adjective masculine singular, verb infinitive):

  - forms the monolingual dictionary only analyses for the variety (r="LR":
    accepted on input, never produced, e.g. Lengadocian "manjar" in Gascon
    text) are never used;
  - an unmarked pair goes to the "shared" file under its Gascon citation
    form, and is dropped when the monolingual dictionary has no generated
    Gascon form for it;
  - a pair marked for Gascon or Aranese keeps its own lemma when the
    monolingual dictionary does not know it at all (the mark is explicit).

Dropped besides: proper nouns (np), entries flagged i="yes", regex entries,
pure punctuation/digits, all-capital tokens (acronyms, Roman numerals) and
single letters. Direction restrictions (r="LR"/"RL") inside the
bilingual dictionaries are ignored: both sides are words either way.

    python3 parse_apertium-oci.py
"""
from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
MONODIX = RAW / "apertium-oci.oci.metadix"
JOBS = [
    ("apertium-oci-fra.oci-fra.dix", "fr",
     {"oci@gascon": "apertium-oci-fra-gascon.tsv", "oci@aran": "apertium-oci-fra-aranese.tsv",
      None: "apertium-oci-fra-shared.tsv"}),
    ("apertium-oci-cat.oci-cat.dix", "ca",
     {"oci@aran": "apertium-oci-cat-aranese.tsv", None: "apertium-oci-cat-shared.tsv"}),
]
CODES = ("oci@gascon", "oci@aran")
POS = {
    "n": "noun", "vblex": "verb", "vbser": "verb", "vbhaver": "verb", "vbmod": "verb", "vaux": "verb",
    "adj": "adj", "adv": "adv", "preadv": "adv", "prn": "pron", "rel": "pron", "num": "num",
    "pr": "prep", "cnjcoo": "conj", "cnjsub": "conj", "cnjadv": "conj",
    "det": "other", "predet": "other", "ij": "other", "abbr": "other", "acr": "other",
}
VERBS = ("vblex", "vbser", "vbhaver", "vbmod", "vaux")


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def plain(xml: str, prm: str = "") -> str:
    text = xml.replace("<prm/>", prm)
    text = re.sub(r"<b\s*/>", " ", text)
    return nfc(re.sub(r"\s+", " ", re.sub(r"<[^>]*>", "", text)).strip())


def tags_of(xml: str) -> list[str]:
    return re.findall(r'<s n="([^"]*)"\s*/>', xml)


def is_citation(tags: list[str]) -> int:
    """0 when the row is not a citation form, else a rank (lower is better)."""
    if not tags:
        return 0
    pos = tags[0]
    if pos in VERBS:
        return 1 if "inf" in tags and len(tags) == 2 else 0
    if pos in ("n", "adj", "num", "prn", "det", "predet", "rel"):
        if not ("sg" in tags or "sp" in tags or pos in ("num", "prn", "rel")):
            return 0
        if "sup" in tags or "pl" in tags:
            return 0
        return 1 if "m" in tags else 2 if "mf" in tags else 3
    return 0 if any(tag in POS and tag != pos for tag in tags[1:]) else 1


PART = re.compile(
    r"<i>(?P<i>.*?)</i>|<i\s*/>"
    r"|<p>\s*(?:<l>(?P<l>.*?)</l>|<l\s*/>)\s*(?:<r>(?P<r>.*?)</r>|<r\s*/>)\s*</p>"
    r'|<par n="(?P<par>[^"]*)"(?:\s+prm="(?P<prm>[^"]*)")?\s*/>', re.S)
MAX_PATHS = 4000


class Monodix:
    """Citation forms the monolingual dictionary generates for each variety."""

    def __init__(self) -> None:
        text = re.sub(r"<!--.*?-->", "", MONODIX.read_text(encoding="utf-8"), flags=re.S)
        self.pardefs: dict[str, list[tuple[dict, str]]] = {}
        for name, body in re.findall(r'<pardef n="([^"]*)"[^>]*>(.*?)</pardef>', text, re.S):
            self.pardefs[name] = [(dict(re.findall(r'(\w+)="([^"]*)"', attrs or "")), inner)
                                  for attrs, inner in re.findall(r"<e(\s[^>]*)?>(.*?)</e>", body, re.S)]
        # (lemma, first tag) -> citation forms, per variety; lemmas known at all; lemmas generated
        self.forms: dict[str, dict[tuple[str, str], set[str]]] = {code: defaultdict(set) for code in CODES}
        self.known: dict[str, set[str]] = {code: set() for code in CODES}
        self.generated: dict[str, set[str]] = {code: set() for code in CODES}
        section = text[text.index("<section"):]
        for attrs_xml, body in re.findall(r"<e(\s[^>]*)>(.*?)</e>", section, re.S):
            attrs = dict(re.findall(r'(\w+)="([^"]*)"', attrs_xml))
            if "lm" not in attrs or "<re>" in body:
                continue
            lemma = nfc(attrs["lm"])
            for code in CODES:
                if attrs.get("alt") not in (None, code):
                    continue
                self.known[code].add(lemma)
                if attrs.get("r") == "LR":
                    continue
                self.generated[code].add(lemma)
                if any(name.endswith(("__vblex", "__vbser", "__vbhaver", "__vbmod", "__vaux"))
                       for name in re.findall(r'<par n="([^"]*)"', body)):
                    continue            # verbs: the lemma is the infinitive, see citation()
                for pos, form in self.cite(lemma, body, code):
                    self.forms[code][(lemma, pos)].add(form)
        self.by_lemma: dict[str, dict[str, set[str]]] = {code: defaultdict(set) for code in CODES}
        for code in CODES:
            for (lemma, _), forms in self.forms[code].items():
                self.by_lemma[code][lemma] |= forms

    def expand(self, body: str, code: str, prm: str = "", depth: int = 0) -> list[tuple[str, str]] | None:
        """Every (surface, lemma-with-tags) the body generates for the variety; None when too large."""
        paths = [("", "")]
        for part in PART.finditer(body):
            if part.group("par") is not None:
                if depth > 3 or part.group("par") not in self.pardefs:
                    return None
                options: list[tuple[str, str]] = []
                for attrs, inner in self.pardefs[part.group("par")]:
                    if attrs.get("alt") not in (None, code) or attrs.get("r") == "LR" or "<re>" in inner:
                        continue
                    sub = self.expand(inner, code, part.group("prm") or prm, depth + 1)
                    if sub is None:
                        return None
                    options += sub
            elif part.group("i") is not None:
                options = [(part.group("i"), part.group("i"))]
            else:
                options = [(part.group("l") or "", part.group("r") or "")]
            if len(paths) * max(len(options), 1) > MAX_PATHS:
                return None
            paths = [(surface + left, lemma + right) for surface, lemma in paths for left, right in options]
        return [(surface.replace("<prm/>", prm), lemma.replace("<prm/>", prm)) for surface, lemma in paths]

    def cite(self, lemma: str, body: str, code: str):
        paths = self.expand(body, code)
        if not paths:
            return
        best: dict[str, tuple[int, set[str]]] = {}
        for surface, lemma_xml in paths:
            tags = tags_of(lemma_xml)
            rank = is_citation(tags)
            if not rank or plain(lemma_xml) != lemma:
                continue
            form = plain(surface)
            if "<a/>" in surface and form != lemma:
                continue                # a post-generation keyword ("<a/>detlo son"), not a spelling
            if tags[0] not in best or rank < best[tags[0]][0]:
                best[tags[0]] = (rank, {form})
            elif rank == best[tags[0]][0]:
                best[tags[0]][1].add(form)
        for pos, (_, forms) in best.items():
            for form in forms:
                yield pos, form

    def citation(self, lemma: str, tag: str, code: str) -> set[str] | None:
        """Forms to print for a bilingual-dictionary lemma, or None when the variety has none."""
        if tag in VERBS:
            return {lemma} if lemma in self.generated[code] else None
        forms = self.forms[code].get((lemma, tag)) or self.by_lemma[code].get(lemma)
        if not forms or len(forms) == 1:
            return forms or None
        if lemma in forms:
            return {lemma}

        def shared(form: str) -> int:
            return next((i for i, (a, b) in enumerate(zip(form, lemma)) if a != b), min(len(form), len(lemma)))
        longest = max(shared(form) for form in forms)
        return {form for form in forms if shared(form) == longest}


def bidix(path: Path):
    text = re.sub(r"<!--.*?-->", "", path.read_text(encoding="utf-8"), flags=re.S)
    for match in re.finditer(r"<e(\s[^>]*)?>(.*?)</e>", text, re.S):
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', match.group(1) or ""))
        body = match.group(2)
        if attrs.get("i") == "yes" or "<re>" in body:
            continue
        pair = re.search(r"<p>\s*<l>(.*?)</l>\s*<r>(.*?)</r>\s*</p>", body, re.S)
        if pair:
            left, right = pair.group(1), pair.group(2)
        else:
            same = re.search(r"<i>(.*?)</i>", body, re.S)
            if not same:
                continue
            left = right = same.group(1)
        head, gloss, tags, gloss_tags = plain(left), plain(right), tags_of(left), tags_of(right)
        if not head or not gloss or "np" in tags or "np" in gloss_tags:
            continue
        if not re.search(r"[^\W\d_]", head) or not re.search(r"[^\W\d_]", gloss):
            continue
        if head.isupper() or len(head) == 1:
            continue                    # acronyms, Roman numerals, letter names
        first = tags[0] if tags else (gloss_tags[0] if gloss_tags else "")
        yield head, gloss, first, attrs.get("alt")


def main() -> None:
    mono = Monodix()
    for raw, gloss_lang, outputs in JOBS:
        rows: dict[str | None, list[tuple[str, str, str]]] = {key: [] for key in outputs}
        seen: set[tuple] = set()
        notes: dict[str, int] = defaultdict(int)
        for lemma, gloss, tag, variety in bidix(RAW / raw):
            if variety not in outputs:
                notes[f"variety {variety!r} left out"] += 1
                continue
            code = variety or "oci@gascon"
            forms = mono.citation(lemma, tag, code)
            if forms is None:
                if variety is None or lemma in mono.known[code]:
                    notes["no generated form for the variety"] += 1
                    continue
                forms = {lemma}         # explicitly marked pair the monolingual dictionary does not know
                notes["marked pair kept on its own lemma"] += 1
            for head in sorted(forms):
                if head != lemma:
                    notes["headword is the variety's form, not the lemma key"] += 1
                key = (variety, head, gloss, POS.get(tag, "other" if tag else ""))
                if key not in seen:
                    seen.add(key)
                    rows[variety].append(key[1:])
        for variety, name in outputs.items():
            with (HERE / name).open("w", encoding="utf-8") as out:
                out.write("headword\tgloss\tgloss_lang\tpos\n")
                for head, gloss, pos in rows[variety]:
                    out.write(f"{head}\t{gloss}\t{gloss_lang}\t{pos}\n")
            print(f"{name}: {len(rows[variety])} rows, {len({r[0] for r in rows[variety]})} headwords")
        for note, count in sorted(notes.items()):
            print(f"  {note}: {count}")


if __name__ == "__main__":
    main()
