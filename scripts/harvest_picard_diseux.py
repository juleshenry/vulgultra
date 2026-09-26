#!/usr/bin/env python3
"""Harvest Picard conjugations from Chés Diseux d'Achteure.

Source: http://ches.diseux.free.fr/conj/ (Amiénois / Vimeu Picard).
Also records North/South auxiliary variants supplied for ète, avoèr, s'in aler.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "conjugation" / "sources" / "pcd_diseux.json"
CACHE = ROOT / "data" / "sources" / "picard_diseux"

PAGES = {
    "verbaux.htm": "http://ches.diseux.free.fr/conj/verbaux.htm",
    "verb1g.htm": "http://ches.diseux.free.fr/conj/verb1g.htm",
    "verb2g.htm": "http://ches.diseux.free.fr/conj/verb2g.htm",
    "verb3g.htm": "http://ches.diseux.free.fr/conj/verb3g.htm",
    "verb4g.htm": "http://ches.diseux.free.fr/conj/verb4g.htm",
}

FEATURES = (
    "indicative.present",
    "indicative.imperfect",
    "indicative.future",
    "conditional",
    "subjunctive.present",
    "imperative",
)
SLOTS = ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")
USER_AGENT = "vulgultra-research/0.1 (+noncommercial Picard morphology)"


_OIL_COMPL = re.compile(r"^(?:qu['’]|q['’]|équ?|eq)\s*", re.I)
_OIL_WORD = re.compile(
    r"^(?:éj|ej|jé|je|tu|té|te|vous|il|is|ale|al|in|os|vos|i)\s+",
    re.I,
)
_OIL_ELIDE = re.compile(r"^[jtimsv]['’]", re.I)
_OIL_REFL = re.compile(r"^(?:m['’]in|t['’]in|s['’]in|nos in|vos in)\s+", re.I)


def strip_subject(form: str) -> str:
    """Drop pedagogical subject clitics so inventories can strip endings."""
    text = form.strip()
    for _ in range(3):
        nxt = _OIL_COMPL.sub("", text).strip()
        nxt = _OIL_WORD.sub("", nxt).strip()
        nxt = _OIL_ELIDE.sub("", nxt).strip()
        nxt = _OIL_REFL.sub("", nxt).strip()
        if nxt == text:
            break
        text = nxt
    return text.strip("-").strip()


def clean_cell(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\xa0", " ").replace("\u00ad", "").replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    text = text.strip("-").strip()
    return strip_subject(text)


def fetch(url: str, dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 0:
        return dest.read_text(encoding="utf-8", errors="replace")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as response:
        data = response.read().decode("utf-8", errors="replace")
    dest.write_text(data, encoding="utf-8")
    return data


def nearest_verb_label(html: str, offset: int) -> tuple[str, str]:
    """Find the closest Verbe/verbe label before a conjugation table."""
    window = html[max(0, offset - 1200):offset]
    patterns = [
        re.compile(
            r"Verbe\s*:\s*<span class=\"b\">([^<]+)</span>\s*(?:\(([^)]*)\))?",
            re.I,
        ),
        re.compile(
            r"verbe\s*<span class=\"b\">([^<]+)</span>\s*(?:\(([^)]*)\))?",
            re.I,
        ),
        re.compile(
            r"Verbe\s*:\s*([A-Za-zÀ-ÿ’'\-]+)\s*(?:\(([^)]*)\))?",
            re.I,
        ),
    ]
    best = None
    for pattern in patterns:
        for match in pattern.finditer(window):
            best = match
    if not best:
        return "", ""
    return clean_cell(best.group(1)), clean_cell(best.group(2) or "")


def parse_model_tables(html: str, page_url: str) -> list[dict]:
    """Pull verb header + 6×6 conjugation tables from a Diseux page."""
    table_re = re.compile(r"<TABLE class\s*=\s*\"conj\"[^>]*>(.*?)</TABLE>", re.I | re.S)
    paradigms: list[dict] = []
    for match in table_re.finditer(html):
        table = match.group(1)
        rows = re.findall(r"<TR[^>]*>(.*?)</TR>", table, re.I | re.S)
        if len(rows) < 7:
            continue
        header_cells = [
            clean_cell(cell).lower()
            for cell in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", rows[0], re.I | re.S)
        ]
        if not any("présent" in cell or "present" in cell for cell in header_cells):
            continue
        lemma, gloss = nearest_verb_label(html, match.start())
        if not lemma:
            continue

        cells: dict[str, dict[str, dict]] = {feature: {} for feature in FEATURES}
        for slot_index, row in enumerate(rows[1:7]):
            slot = SLOTS[slot_index]
            values = [
                clean_cell(cell)
                for cell in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, re.I | re.S)
            ]
            while len(values) < len(FEATURES):
                values.append("")
            for feature, form in zip(FEATURES, values):
                if not form or form == "-":
                    continue
                cells[feature][slot] = {
                    "form": form,
                    "phonemes": [],
                    "source_label": feature,
                    "source_url": page_url,
                }
        cells = {feature: row for feature, row in cells.items() if row}
        if not cells:
            continue
        ending = class_from_lemma(lemma)
        paradigms.append({
            "lect": "pcd",
            "lemma": lemma,
            "class_source": ending,
            "regularity": "model" if lemma in {"warder", "finir"} else "irregular",
            "source": {
                "attested": True,
                "title": f"Chés Diseux:{lemma}",
                "url": page_url,
                "gloss_fr": gloss,
                "provider": "ches.diseux.free.fr",
            },
            "cells": cells,
        })
    return paradigms


def class_from_lemma(lemma: str) -> str:
    low = lemma.lower().strip()
    irregulars = {
        "ête": "ête", "ete": "ête", "avoér": "avoér", "avoer": "avoér",
        "aller": "aller", "foaire": "foaire", "dvoér": "dvoér", "dvoer": "dvoér",
        "s'in aler": "s'in aler", "sin aler": "s'in aler",
    }
    if low in irregulars:
        return irregulars[low]
    for ending in ("ier", "tcher", "djer", "uer", "yer", "eler", "eter", "er", "ir", "re", "te"):
        if low.endswith(ending):
            return f"-{ending}"
    return "other"


def add_form(cells: dict, feature: str, slot: str, form: str, *, url: str, note: str) -> None:
    form = strip_subject(form.strip())
    if not form or form == "-":
        return
    row = cells.setdefault(feature, {})
    existing = row.get(slot)
    if existing and existing.get("form") == form:
        return
    if existing:
        # Keep first as primary; stash alternate under notes list on the cell.
        alts = existing.setdefault("notes", [])
        if isinstance(alts, list) and form not in alts and form != existing.get("form"):
            alts.append(f"{note}: {form}")
        return
    row[slot] = {
        "form": form,
        "phonemes": [],
        "source_label": note,
        "source_url": url,
    }


def north_south_overlays() -> list[dict]:
    """User-supplied North/South auxiliary grids (Amiénois/Vimeu style)."""
    url = "http://ches.diseux.free.fr/conj/verb1g.htm"
    # Mapped to standard 6 slots. SHE/ONE folded into 3sg alternates.
    # Present/Imperfect North vs South stored as primary + notes.
    data = []

    def pack(lemma: str, class_source: str, rows: dict) -> dict:
        cells: dict[str, dict] = {}
        for feature, slot_map in rows.items():
            for slot, forms in slot_map.items():
                if isinstance(forms, str):
                    forms = [forms]
                primary, *rest = forms
                add_form(cells, feature, slot, primary, url=url, note="picard")
                for alt in rest:
                    add_form(cells, feature, slot, alt, url=url, note="variant")
        return {
            "lect": "pcd",
            "lemma": lemma,
            "class_source": class_source,
            "regularity": "irregular",
            "source": {
                "attested": True,
                "title": f"Picard auxiliaries:{lemma}",
                "url": url,
                "provider": "user+ches.diseux",
                "dialect_note": "North/South and variable forms retained as alternates",
            },
            "cells": cells,
        }

    # ète / être — prefer North present; keep South/imperfect/future/conditional/subj variants
    data.append(pack("ête", "ête", {
        "indicative.present": {
            "1sg": ["ej su", "j'su"],
            "2sg": ["t'es"],
            "3sg": ["il est", "al est", "in est"],
            "1pl": ["os sonmes"],
            "2pl": ["os ètes"],
            "3pl": ["is sont"],
        },
        "indicative.imperfect": {
            "1sg": ["j'éto(s)", "j'étoé", "étoais"],
            "2sg": ["t'étos", "t'étoés", "étoais"],
            "3sg": ["i'étot", "il étoét", "étoait", "al étot", "in étot"],
            "1pl": ["os étonmes", "os étoinmes"],
            "2pl": ["os étotes", "os étoétes"],
            "3pl": ["is étotte", "is étoétte", "étoaitte"],
        },
        "indicative.future": {
            "1sg": ["ej srai"],
            "2sg": ["tu sros", "té séros"],
            "3sg": ["i sro", "ale sro", "in sro"],
            "1pl": ["os srons"],
            "2pl": ["os srez"],
            "3pl": ["is sront"],
        },
        "conditional": {
            "1sg": ["ej séro(s)", "ej sroé"],
            "2sg": ["té séros", "tu sroés"],
            "3sg": ["i sérot", "i sroét", "ale sérot", "in sérot"],
            "1pl": ["os séronmes", "os sroinmes"],
            "2pl": ["os sérotes", "os sroétes"],
            "3pl": ["is sérotte", "is sroétte"],
        },
        "subjunctive.present": {
            "1sg": ["qu'ej soéche", "qu'ej fuche", "seuche"],
            "2sg": ["eq tu soéches", "eq tu fuches", "seuches"],
            "3sg": ["qu'i soéche", "qu'i fuche", "seuche"],
            "1pl": ["qu'os soéïonches", "qu'os fuchonches", "seuchonches", "sonches"],
            "2pl": ["qu'os soéïèches", "qu'os fuchèches", "seuchèches"],
            "3pl": ["qu'is soéchtte", "qu'is fuchtte", "seuchtte"],
        },
        "imperative": {
            "2sg": ["soéche", "fus", "fuche"],
            "1pl": ["soéïons", "fuchons"],
            "2pl": ["soéïez", "fuchez"],
        },
    }))

    data.append(pack("avoèr", "avoér", {
        "indicative.present": {
            "1sg": ["j'ai"],
            "2sg": ["t'as", "t'os"],
            "3sg": ["i'a", "il o", "al a", "al o", "in a", "in o"],
            "1pl": ["os avons"],
            "2pl": ["os avez"],
            "3pl": ["is ont", "il ont"],
        },
        "indicative.imperfect": {
            "1sg": ["j'avo(s)", "j'avoés", "avoais"],
            "2sg": ["t'avos", "t'avoés"],
            "3sg": ["i'avot", "il avoét", "al avot", "in avot"],
            "1pl": ["os avonmes", "os avoinmes"],
            "2pl": ["os avotes", "os avoétes"],
            "3pl": ["is avotte", "is avoétte"],
        },
        "indicative.future": {
            "1sg": ["j'arai", "j'érai"],
            "2sg": ["t'aras", "t'éros"],
            "3sg": ["i'ara", "il éro", "al ara", "in ara"],
            "1pl": ["os arons", "os érons"],
            "2pl": ["os arez", "os érez"],
            "3pl": ["is aront", "is éront"],
        },
        "conditional": {
            "1sg": ["j'aros", "j'éroé"],
            "2sg": ["t'aros", "t'éroés"],
            "3sg": ["i'arot", "il éroét", "al arot", "in arot"],
            "1pl": ["os aronmes", "os éroinmes"],
            "2pl": ["os arotes", "os éroétes"],
            "3pl": ["is arotte", "is éroétte"],
        },
        "subjunctive.present": {
            "1sg": ["eq j'euche"],
            "2sg": ["eq t'euches"],
            "3sg": ["qu'il euche", "qu'al euche", "qu'in euche"],
            "1pl": ["qu'os euchonches", "aïonches"],
            "2pl": ["qu'os euchèches", "aïèches"],
            "3pl": ["qu'is euhtte"],
        },
        "imperative": {
            "2sg": ["aïe"],
            "1pl": ["aïons"],
            "2pl": ["aïez"],
        },
    }))

    data.append(pack("s'in aler", "s'in aler", {
        "indicative.present": {
            "1sg": ["j'm'in vas", "ej m'in vos"],
            "2sg": ["té t'in vas", "tu t'in vos"],
            "3sg": ["i s'in va", "i s'in vo", "ale s'in va", "in s'in va"],
            "1pl": ["os nos in alons"],
            "2pl": ["os vos in alez"],
            "3pl": ["is s'in vont"],
        },
        "indicative.imperfect": {
            "1sg": ["j'm'in alos", "ej m'in aloés", "aloais"],
            "2sg": ["té t'in alos", "tu t'in aloés"],
            "3sg": ["i s'in a lot", "i s'in aloét", "ale s'in a lot", "in s'in a lot"],
            "1pl": ["os nos in alonmes", "os nos in aloinmes"],
            "2pl": ["os vos in alotes", "os vos in aloétes"],
            "3pl": ["is s'in alotte", "is s'in aloétte"],
        },
        "indicative.future": {
            "1sg": ["j'm'in irai"],
            "2sg": ["tu t'in iros", "té t'in iros"],
            "3sg": ["i s'in iro", "ale s'in iro", "in s'in ira"],
            "1pl": ["os nos in irons"],
            "2pl": ["vos vos in irez", "os vos in irotes"],
            "3pl": ["is s'in iront"],
        },
        "conditional": {
            "1sg": ["j'm'in iros", "ej m'in iroé"],
            "2sg": ["té t'in iros", "tu t'in iroés"],
            "3sg": ["i s'in irot", "i s'in iroét", "ale s'in irot", "in s'in irot"],
            "1pl": ["os nos in ironmes", "os nos in iroinmes"],
            "2pl": ["os vos in irotes", "os vos in iroétes"],
            "3pl": ["is s'in irotte", "is s'in iroétte"],
        },
        "subjunctive.present": {
            "1sg": ["qu'ej m'in ale", "qu'ej m'in voaiche"],
            "2sg": ["qu'té t'in ale", "qu'tu t'in voaiches"],
            "3sg": ["qu'i s'in ale", "qu'i s'in voaiche", "qu'ale s'in ale", "qu'in s'in ale"],
            "1pl": ["qu'os nos in allotte", "qu'os nos in alonches"],
            "2pl": ["qu'os vos in allotte", "qu'os vos in alèches"],
            "3pl": ["qu'is s'in allote", "qu'is s'in voaichtte"],
        },
    }))
    return data


def merge_paradigms(items: list[dict]) -> list[dict]:
    by_lemma: dict[str, dict] = {}
    for item in items:
        lemma = item["lemma"]
        key = lemma.lower()
        # Normalize spelling variants onto one lemma key where obvious.
        if key in {"ete", "ête"}:
            key = "ête"
            item["lemma"] = "ête"
        if key in {"avoer", "avoér", "avoèr"}:
            key = "avoér"
            item["lemma"] = "avoér"
        existing = by_lemma.get(key)
        if not existing:
            by_lemma[key] = item
            continue
        # Merge cells / alternates into the first record.
        for feature, row in item.get("cells", {}).items():
            for slot, cell in row.items():
                add_form(
                    existing["cells"],
                    feature,
                    slot,
                    cell.get("form", ""),
                    url=str(cell.get("source_url") or item["source"].get("url") or ""),
                    note="merged",
                )
                for note in cell.get("notes") or []:
                    # notes already encoded
                    pass
    return list(by_lemma.values())


def main() -> int:
    paradigms: list[dict] = []
    for name, url in PAGES.items():
        html = fetch(url, CACHE / name)
        got = parse_model_tables(html, url)
        print(f"{name}: {len(got)} paradigms")
        paradigms.extend(got)
    paradigms.extend(north_south_overlays())
    merged = merge_paradigms(paradigms)
    # Ending inventories lightweight
    inventories: dict[str, dict] = {}
    document = {
        "schema": "vulgultra.conjugation.v1",
        "metadata": {
            "lect": "pcd",
            "purpose": "Picard conjugations from Chés Diseux + North/South auxiliaries",
            "provider": "ches.diseux.free.fr",
            "attribution": "Chés Diseux d'Achteure (http://ches.diseux.free.fr/conj/)",
            "ending_inventories": inventories,
            "optimizer_involved": False,
        },
        "paradigms": sorted(merged, key=lambda item: item["lemma"]),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT} paradigms={len(merged)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
