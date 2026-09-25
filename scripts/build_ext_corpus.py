#!/usr/bin/env python3
"""Build Extremaduran lexicon from:

1. https://github.com/juanro49/recursos_es-ext  (line-aligned ES↔EXT)
2. OSCEC Diccionario castellano–estremeñu (Ismael Carmona García, 2017) PDF
3. ext.wikipedia.org dump titles
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "vendor" / "recursos_es-ext"
PDF_SRC = ROOT / "data" / "sources" / "pdf" / "oscec-diccionario-castellano-extremec3b1o-ismael-carmona-garcc3ada.pdf"
PDF_TXT = Path("/tmp/ext_dict.txt")
WIKI = ROOT / "xmls" / "extwiki-latest-pages-articles.xml"
OUT = ROOT / "data" / "words" / "ext_words.json"

WORD_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñÇç][A-Za-zÁÉÍÓÚÜÑáéíóúüñÇç\-']{1,}")

POS = {
    "act", "med", "adv", "adj", "m", "f", "com", "loc", "fr", "prep", "interj",
    "pron", "det", "num", "fam",
}
DOMAINS = {
    "AGR", "ALB", "ANAT", "ANTR", "APIC", "ARQ", "BOT", "CINEG", "COST", "CUL",
    "DEP", "DER", "DIV", "ECON", "ENO", "ENT", "GAN", "GENT", "GEO", "GEOM",
    "INFORM", "HIPOC", "MAT", "MATAN", "MED", "METEOR", "MIC", "MIL", "MOL",
    "MÚS", "PESC", "QUÍM", "REL", "TEC", "ZOOL", "ART",
}
SKIP_TOK = POS | {d.lower() for d in DOMAINS} | {
    "dicho", "de", "un", "una", "el", "la", "los", "las", "alguien", "algo",
    "persona", "animal", "cosa", "tipo", "hacia", "sitio", "donde", "hace",
    "mucho", "calor", "poco", "claro", "ac", "discont", "cont",
}

# Spanish headword at start of an entry chunk
ENTRY_RE = re.compile(
    r"(?:^|\n|\s{2,})"
    r"([A-Za-záéíóúüñÁÉÍÓÚÜÑçÇ][A-Za-záéíóúüñÁÉÍÓÚÜÑçÇ\-']{1,}(?:, -a)?)"
    r"\.\s+",
)


def norm(w: str) -> str:
    return w.strip().strip(".,;:¡!¿?\"'«»()[]")


def tokens(text: str) -> list[str]:
    return [m.group(0) for m in WORD_RE.finditer(text)]


def add_pair(store: dict, es: str, ext: str, source: str, quality: str) -> None:
    es, ext = norm(es), norm(ext)
    if len(es) < 2 or len(ext) < 2:
        return
    key = es.lower()
    rec = store.setdefault(
        key,
        {"es": es.split(",")[0], "ext": [], "ext_quality": {}, "sources": []},
    )
    if ext not in rec["ext"]:
        rec["ext"].append(ext)
    # keep best quality tag per surface
    prev = rec["ext_quality"].get(ext)
    rank = {"gold": 4, "dict": 3, "conj": 2, "wiki": 1, "text": 0}
    if prev is None or rank.get(quality, 0) > rank.get(prev, 0):
        rec["ext_quality"][ext] = quality
    if source not in rec["sources"]:
        rec["sources"].append(source)


def from_palabras(store: dict) -> None:
    pal = REPO / "Palabras"
    for ext_path in sorted(pal.glob("*.ext.txt")):
        es_path = ext_path.with_name(ext_path.name.replace(".ext.txt", ".es.txt"))
        if not es_path.exists():
            continue
        es_lines = es_path.read_text(encoding="utf-8", errors="replace").splitlines()
        ext_lines = ext_path.read_text(encoding="utf-8", errors="replace").splitlines()
        for es, ex in zip(es_lines, ext_lines):
            if not es.strip() or not ex.strip():
                continue
            for e in re.split(r"[/;]", ex):
                e = e.strip()
                if e:
                    add_pair(store, es, e, "recursos_es-ext/Palabras", "gold")


def from_conjugations(store: dict) -> None:
    conj = REPO / "Conjugacion verbos"
    headers = {
        "enfinitivu", "simplí", "simpli", "compuestu", "gerundi", "participiu",
        "indicativu", "suhuntivu", "imperativu", "condicional", "presenti",
        "pretéritu", "imperfectu", "futuru", "perfectu", "pluscuamperfectu",
    }
    for ext_path in sorted(conj.glob("*.ext.txt")):
        stem = ext_path.name.replace(".ext.txt", "")
        for line in ext_path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            low_line = line.lower()
            if any(h in low_line for h in headers) and " " in line:
                continue
            for tok in tokens(line):
                low = tok.lower()
                if low in SKIP_TOK or low in headers or len(low) < 4:
                    continue
                add_pair(store, stem, low, "recursos_es-ext/Conjugacion", "conj")


def from_parallel_text(store: dict) -> None:
    es_all = (REPO / "contenido-completo.es.txt").read_text(encoding="utf-8", errors="replace").splitlines()
    ext_all = (REPO / "contenido-completo.ext.txt").read_text(encoding="utf-8", errors="replace").splitlines()
    for es_line, ext_line in zip(es_all, ext_all):
        es_toks = [t.lower() for t in tokens(es_line)]
        ext_toks = [t.lower() for t in tokens(ext_line)]
        if not es_toks or not ext_toks:
            continue
        if abs(len(es_toks) - len(ext_toks)) > 1:
            continue
        for a, b in zip(es_toks, ext_toks):
            if a == b or len(b) < 3 or b in SKIP_TOK:
                continue
            # require some orthographic difference typical of EXT
            add_pair(store, a, b, "recursos_es-ext/contenido-completo", "text")


def from_pdf(store: dict) -> None:
    # Raw (single-flow) text — two-column -layout merges entries badly.
    raw = Path("/tmp/ext_dict_raw.txt")
    if not raw.exists() or raw.stat().st_size < 1000:
        subprocess.check_call(["pdftotext", str(PDF_SRC), str(raw)])
    text = raw.read_text(encoding="utf-8", errors="replace")
    start = text.find("\na. f (letra)")
    if start < 0:
        start = text.find("\nabajo.")
    body = text[max(0, start) :]

    matches = list(ENTRY_RE.finditer(body))
    for i, m in enumerate(matches):
        head = m.group(1)
        end = matches[i + 1].start() if i + 1 < len(matches) else min(len(body), m.end() + 500)
        chunk = body[m.end() : end]
        # drop parenthetical sense glosses in Spanish
        chunk = re.sub(r"\([^)]*\)", " ", chunk)
        got = []
        for tok in tokens(chunk):
            if tok.upper() in DOMAINS or tok.lower() in SKIP_TOK:
                continue
            if tok.lower() == head.lower().split(",")[0]:
                # same orthography in both languages — still valid EXT citation
                got.append(tok)
                continue
            if len(tok) < 2:
                continue
            got.append(tok)
            if len(got) >= 8:
                break
        for g in got:
            add_pair(store, head, g, "carmona_oscec_2017", "dict")


def from_wiki(store: dict) -> None:
    if not WIKI.exists():
        return
    import xml.etree.ElementTree as ET

    for _ev, elem in ET.iterparse(WIKI, events=("end",)):
        if elem.tag.rsplit("}", 1)[-1] != "title":
            continue
        title = (elem.text or "").strip()
        elem.clear()
        if not title or ":" in title or title.startswith("Wikipedia"):
            continue
        add_pair(store, title, title, "extwiki", "wiki")


def preferred_ext(rec: dict) -> list[str]:
    """Quality first; within a quality, keep discovery order (primary gloss first)."""
    rank = {"gold": 4, "dict": 3, "conj": 2, "wiki": 1, "text": 0}
    order = {w: i for i, w in enumerate(rec["ext"])}
    return sorted(
        rec["ext"],
        key=lambda w: (
            -rank.get(rec["ext_quality"].get(w, "text"), 0),
            order[w],
        ),
    )


def main() -> None:
    if not REPO.exists():
        raise SystemExit(f"missing {REPO}; clone juanro49/recursos_es-ext first")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    store: dict = {}
    print("1/4 Palabras…")
    from_palabras(store)
    print(f"   {len(store)} keys")
    print("2/4 Conjugaciones…")
    from_conjugations(store)
    print(f"   {len(store)} keys")
    print("3/4 Carmona PDF…")
    from_pdf(store)
    print(f"   {len(store)} keys")
    print("4/4 extwiki titles…")
    from_wiki(store)
    print(f"   {len(store)} keys")

    # compact export: preferred EXT forms first
    entries = {}
    surfaces = set()
    gold_surfaces = set()
    for key, rec in store.items():
        prefs = preferred_ext(rec)
        surfaces.update(prefs)
        for w in prefs:
            if rec["ext_quality"].get(w) in {"gold", "dict"}:
                gold_surfaces.add(w)
        entries[key] = {
            "es": rec["es"],
            "ext": prefs[:12],
            "best": prefs[0] if prefs else None,
            "sources": rec["sources"],
        }

    out = {
        "meta": {
            "lang": "ext",
            "sources": [
                "https://github.com/juanro49/recursos_es-ext",
                str(PDF_SRC.name),
                "https://dumps.wikimedia.org/extwiki/latest/",
            ],
            "n_es_keys": len(entries),
            "n_ext_surfaces": len(surfaces),
            "n_ext_surfaces_gold_or_dict": len(gold_surfaces),
        },
        "entries": entries,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {OUT}")
    print(json.dumps(out["meta"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
