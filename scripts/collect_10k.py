#!/usr/bin/env python3
"""Merge open Apertium / Verbix / alias corpora into data/words/{code}_words.json.

Does not scrape gated sources (Pledari, DRG, TalkBank, Verbix site-wide).
Wikipedia / Wiktionary dumps are handled by harvest_dump_types.py.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORDS = ROOT / "data" / "words"
VENDOR = ROOT / "vendor"

WORD_OK = re.compile(r"^[^\W\d_][^\W_]{0,39}$", re.UNICODE)
LM_RE = re.compile(r'\blm="([^"]+)"')
I_RE = re.compile(r"<i>([^<]+)")
L_RE = re.compile(r"<l>([^<]+)")
E_OPEN_RE = re.compile(r"<e\b([^>]*)>", re.DOTALL)
LEXD_LEMMA_RE = re.compile(r"^([^\s#:]+):")


def is_lemma(w: str) -> bool:
    w = (w or "").strip()
    if not w or " " in w or "<" in w:
        return False
    return bool(WORD_OK.match(w))


def load_words(code: str) -> dict:
    dest = WORDS / f"{code}_words.json"
    if dest.exists():
        return json.loads(dest.read_text(encoding="utf-8"))
    return {"meta": {"lang": code, "n_entries": 0}, "entries": {}}


def save_words(code: str, data: dict) -> None:
    data["meta"]["lang"] = code
    data["meta"]["n_entries"] = len(data.get("entries") or {})
    dest = WORDS / f"{code}_words.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def add_lemmas(code: str, lemmas: set[str], source: str) -> tuple[int, int]:
    data = load_words(code)
    entries = data.setdefault("entries", {})
    added = 0
    for w in lemmas:
        if w not in entries:
            entries[w] = {
                code: w,
                "pos": [],
                "glosses_en": [],
                "sources": [source],
            }
            added += 1
        else:
            srcs = entries[w].setdefault("sources", [])
            if source not in srcs:
                srcs.append(source)
    save_words(code, data)
    return added, len(entries)


def lemmas_from_dix(path: Path, side: str = "lm") -> set[str]:
    """side: lm (monolingual lm=/i=), l (bilingual left), r (bilingual right)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    out: set[str] = set()
    if side == "lm":
        for w in LM_RE.findall(text):
            if is_lemma(w):
                out.add(w)
        for w in I_RE.findall(text):
            if is_lemma(w):
                out.add(w)
        return out
    tag = "l" if side == "l" else "r"
    for w in re.findall(rf"<{tag}>([^<]+)", text):
        if is_lemma(w):
            out.add(w)
    return out


def lemmas_from_lexd(path: Path) -> set[str]:
    out: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("LEXICON") or line.startswith("Pattern"):
            continue
        m = LEXD_LEMMA_RE.match(line)
        if not m:
            continue
        w = m.group(1)
        if is_lemma(w):
            out.add(w)
    return out


def lemmas_from_metadix_alt(path: Path, alt_substr: str) -> set[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    # main sections only — pardefs are inflection junk
    i = text.find("<section")
    body = text[i:] if i >= 0 else text
    out: set[str] = set()
    for m in E_OPEN_RE.finditer(body):
        attrs = m.group(1)
        if alt_substr not in attrs:
            continue
        lm = LM_RE.search(attrs)
        if lm and is_lemma(lm.group(1)):
            out.add(lm.group(1).strip())
    return out


def ingest_apertium() -> None:
    jobs: list[tuple[str, Path, str, str]] = [
        ("an", VENDOR / "apertium-arg/apertium-arg.arg.dix", "lm", "apertium"),
        ("an", VENDOR / "apertium-spa-arg/apertium-spa-arg.spa-arg.dix", "r", "apertium"),
        ("ast", VENDOR / "apertium-ast/apertium-ast.ast.dix", "lm", "apertium"),
        ("sc", VENDOR / "apertium-srd/apertium-srd.srd.dix", "lm", "apertium"),
        ("scn", VENDOR / "apertium-scn/apertium-scn.scn.dix", "lm", "apertium"),
        ("gl", VENDOR / "apertium-glg/apertium-glg.glg.dix", "lm", "apertium"),
        ("oc", VENDOR / "apertium-oci/apertium-oci.oci.metadix", "lm", "apertium"),
        ("oc", VENDOR / "apertium-oci-spa/apertium-oci-spa.oci-spa.dix", "l", "apertium"),
        ("ca", VENDOR / "apertium-fra-cat/apertium-fra-cat.fra-cat.dix", "r", "apertium"),
        ("fr", VENDOR / "apertium-fra-cat/apertium-fra-cat.fra-cat.dix", "l", "apertium"),
        ("es", VENDOR / "apertium-spa-arg/apertium-spa-arg.spa-arg.dix", "l", "apertium"),
        ("es", VENDOR / "apertium-spa-ast/apertium-spa-ast.spa-ast.dix", "l", "apertium"),
        ("ast", VENDOR / "apertium-spa-ast/apertium-spa-ast.ast.dix", "lm", "apertium"),
    ]
    for code, path, side, source in jobs:
        if not path.exists():
            print(f"  skip missing {path}")
            continue
        lemmas = lemmas_from_dix(path, side=side)
        added, total = add_lemmas(code, lemmas, source)
        print(f"  {code:4} +{added:6} from {path.name} ({side}) → {total}  [{len(lemmas)} parsed]")

    mwl = VENDOR / "apertium-mwl/apertium-mwl.mwl.lexd"
    if mwl.exists():
        lemmas = lemmas_from_lexd(mwl)
        added, total = add_lemmas("mwl", lemmas, "apertium")
        print(f"  mwl  +{added:6} from {mwl.name} → {total}  [{len(lemmas)} parsed]")

    metadix = VENDOR / "apertium-oci/apertium-oci.oci.metadix"
    if metadix.exists():
        gsc = lemmas_from_metadix_alt(metadix, "oci@gascon")
        aran = lemmas_from_metadix_alt(metadix, "oci@aran")
        gsc |= aran
        added, total = add_lemmas("gsc", gsc, "apertium")
        print(f"  gsc  +{added:6} oci@gascon/aran → {total}  [{len(gsc)} parsed]")


def ingest_verbix_ist() -> None:
    path = VENDOR / "istriot/verbix_infinitives.txt"
    if not path.exists():
        return
    lemmas: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        w = line.strip()
        if is_lemma(w):
            lemmas.add(w)
    added, total = add_lemmas("ist", lemmas, "verbix")
    print(f"  ist  +{added:6} verbix infinitives → {total}")


def copy_alias(src_code: str, dst_code: str, note: str) -> None:
    src = WORDS / f"{src_code}_words.json"
    if not src.exists():
        print(f"  skip alias {src_code}→{dst_code} (no {src.name})")
        return
    data = json.loads(src.read_text(encoding="utf-8"))
    entries_in = data.get("entries") or {}
    out = load_words(dst_code)
    entries = out.setdefault("entries", {})
    added = 0
    for word, rec in entries_in.items():
        if word in entries:
            continue
        new = dict(rec)
        if src_code in new:
            new[dst_code] = new.pop(src_code)
        else:
            new[dst_code] = word
        srcs = list(new.get("sources") or [])
        alias_tag = f"alias:{src_code}"
        if alias_tag not in srcs:
            srcs.append(alias_tag)
        new["sources"] = srcs
        entries[word] = new
        added += 1
    out["meta"]["alias_of"] = src_code
    out["meta"]["alias_note"] = note
    if data.get("meta", {}).get("n_wiki_types") and not out["meta"].get("n_wiki_types"):
        out["meta"]["n_wiki_types"] = data["meta"]["n_wiki_types"]
    save_words(dst_code, out)
    print(f"  {dst_code:4} +{added:6} aliased from {src_code} → {len(entries)}  ({note})")


def report() -> None:
    codes = [
        # Ibero
        "es", "pt", "gl", "an", "ast", "ext", "lad", "mwl",
        # Occitano
        "oc", "ca", "gsc",
        # Oil / Arpitan
        "fr", "wa", "pcd", "nrm", "nrf", "glw", "frp",
        # Gallo-Italian
        "lmo", "pms", "lij", "eml", "egl", "rgn",
        # Italo-Dalmatian
        "it", "scn", "vec", "co", "ist", "dlm", "nap",
        # Rhaeto / Sardinian
        "rm", "fur", "lld", "sc",
        # Eastern
        "ro", "rup", "ruo", "ruq",
        # reserved
        "la",
    ]
    print(f"\n{'code':6} {'entries':>8} {'wikiT':>8} {'ok':6}")
    for c in codes:
        p = WORDS / f"{c}_words.json"
        if not p.exists():
            print(f"{c:6} {'MISSING':>8} {'':>8} under")
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        m = d.get("meta") or {}
        n = m.get("n_entries") or len(d.get("entries") or {})
        wt = m.get("n_wiki_types") or 0
        ok = "CLEAR" if n >= 10_000 or wt >= 10_000 else "under"
        print(f"{c:6} {n:8} {wt:8} {ok}")


def main() -> None:
    WORDS.mkdir(parents=True, exist_ok=True)
    print("Apertium…")
    ingest_apertium()
    print("Verbix (one-page Istriot infinitives)…")
    ingest_verbix_ist()
    print("Aliases…")
    copy_alias("egl", "eml", "Emilian Kaikki/Wiktextract uses egl; SOURCE_LANGS is eml")
    copy_alias("nrf", "nrm", "legacy nrm file; SOURCE_LANGS code is nrf")
    report()


if __name__ == "__main__":
    main()
