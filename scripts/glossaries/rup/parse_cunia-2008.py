#!/usr/bin/env python3
"""Parse Tiberius Cunia, Dictsiunar a Limbãljei Armãneascã (early edition,
Dec 2008) into headword-gloss tables.

Input : raw/cunia_dictsiunar_2008.pdf  (born-digital, 1,134 pp, two columns)
Output: cunia-2008.tsv           English glosses   ({en: ...})
        cunia-2008-ro.tsv        Romanian glosses  ({ro: ...})
        cunia-2008-fr.tsv        French glosses    ({fr: ...})
        cunia-2008.doubtful.tsv  rows whose headword could not be trusted
        (all four: headword <TAB> gloss <TAB> gloss_lang <TAB> pos)

How it reads the PDF.  pdftotext's plain reading order interleaves the two
columns, and its de-hyphenation glues real hyphens, so this script takes the
word boxes (pdftotext -bbox-layout) and rebuilds the text itself:
  * a word belongs to the left column when its xMin < 303 pt;
  * words are grouped into lines by their top edge; superscript homonym
    numbers (box height ~5 pt) are attached to the word before them as ^n;
  * a line that starts at the column margin (65 pt / 310 pt) opens an entry,
    lines with the 5 pt hanging indent continue it;
  * a hyphen at a line end is kept as the marker "¬" and resolved later:
    inside a headword it is decided by the same headword printed unbroken
    elsewhere in the dictionary (every derived word also has its own
    alphabetical pointer entry); inside a gloss it is dropped (Word's
    automatic hyphenation) except after Romanian/French clitics.

Entry grammar (the source's own):
  headword[/variant] (pro-nun-ci-á-tion) [(mi)] POS forms – Aromanian
  definition {ro: …} {fr: …} {en: …} ex: … § derived headword (…) POS …
A sub-entry "– (unã cu X)" (= "one with X", a spelling or word-formation
variant of X) carries no gloss of its own; it gets X's glosses, looked up
among the sub-entries of the same entry first, then among all headwords
(only when unambiguous).  "– vedz tu X" pointers are skipped.

Usage: python3 parse_cunia-2008.py [--dump-entries FILE]
       (stdlib only; needs pdftotext on PATH)
"""
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
from collections import Counter, defaultdict
from html import unescape

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(HERE, "raw", "cunia_dictsiunar_2008.pdf")
FIRST_DICT_PAGE = 7          # the heading "A" is in the left column of PDF p. 7
SPLIT_X = 303.0              # left-column words start left of this
HDR_Y = 45.0                 # running head / page number sit above this
MARGIN = (65.04, 309.84)     # x of an entry's first line, per column
MARK = "¬"                   # line-end hyphen marker

POS_TOKENS = (r"(?:sm|sf|sn|smf|simf|adg|adgf|adj|adv|vb|prip|cong|pron|pr|num|"
              r"inter|articul|art|invar|expr|prifixu|sufixu)")

WORD_RE = re.compile(
    r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>')


# ---------------------------------------------------------------- text layer
def page_columns(page_html):
    """-> [left_lines, right_lines]; each line = (x_first_word, text)."""
    cols = ([], [])
    for x0, y0, x1, y1, w in WORD_RE.findall(page_html):
        x0, y0, x1, y1 = float(x0), float(y0), float(x1), float(y1)
        if y0 < HDR_Y:
            continue
        cols[0 if x0 < SPLIT_X else 1].append([x0, y0, x1, y1, unescape(w)])
    out = []
    for words in cols:
        normal = [w for w in words if (w[3] - w[1]) > 8]
        small = [w for w in words if (w[3] - w[1]) <= 8]
        lines = defaultdict(list)
        for w in normal:
            lines[round(w[1], 0)].append(w)
        merged = []
        for k in sorted(lines):
            if merged and k - merged[-1][0] < 3:
                merged[-1][1].extend(lines[k])
            else:
                merged.append([k, lines[k]])
        for s in small:                       # superscript -> ^n on the word before
            best = None
            for k, ws in merged:
                if abs(s[1] - k) < 4:
                    for w in ws:
                        if abs(s[0] - w[2]) < 1.5:
                            best = w
            if best is not None:
                best[4] = best[4] + "^" + s[4]
        col_lines = []
        for k, ws in merged:
            ws.sort(key=lambda w: w[0])
            col_lines.append((ws[0][0], " ".join(w[4] for w in ws)))
        out.append(col_lines)
    return out


def read_entries(bbox_path):
    """Yield entry strings (lines joined; line-end hyphens become MARK)."""
    data = open(bbox_path, encoding="utf-8").read()
    pages = data.split("<page ")[1:]
    cur = None
    started = False
    for pno, pg in enumerate(pages, 1):
        if pno < FIRST_DICT_PAGE:
            continue
        for ci, col in enumerate(page_columns(pg)):
            margin = MARGIN[ci]
            for x, text in col:
                if not started:
                    if text.strip() == "A":
                        started = True
                    continue
                if x > margin + 25 and len(text) <= 3:        # centred letter heading
                    continue
                if x < margin + 2.5:
                    if cur is not None:
                        yield cur
                    cur = text
                elif cur is None:
                    cur = text
                elif cur.endswith("-"):
                    cur = cur[:-1] + MARK + text
                else:
                    cur = cur + " " + text
    if cur is not None:
        yield cur


# ---------------------------------------------------------------- entry parsing
# headword (pro-nun-ci-a-tion) rest
SUB_RE = re.compile(r"^(?P<hw>[^(){}–§=;:,]+?)\s*\((?P<pron>[^()]*)\)\s*(?P<rest>.*)$", re.S)
# headword POS ... / headword – ...   (no pronunciation given)
SUB2_RE = re.compile(
    r"^(?P<hw>[^(){}–§=;:,]+?)\s+(?P<rest>(?:\(\w+\)\s+)?" + POS_TOKENS + r"\b.*|–.*)$", re.S)
BRACE_RE = re.compile(r"\{([^{}]*)\}")
LABEL_RE = {l: re.compile(r"^\s*" + l + r"\s*[:;]?\s*") for l in ("ro", "fr", "en")}
SAMEAS_RE = re.compile(r"(?:–\s*|\(\s*)un[ãă]\s+cu\s+([^(){};,]+?)\s*(?:\)|$|\bex:)")
HW_OK_RE = re.compile(r"[^\W\d_]+(?:[-’' ][^\W\d_]+)*[!?]?")

RO_CLITIC_L = {"dintr", "într", "printr", "s", "l", "n", "m", "i", "c", "d", "ţi", "şi",
               "ş", "mi", "ne", "te", "le", "v", "ce", "de", "nu", "să", "se"}
RO_CLITIC_R = {"o", "un", "una", "i", "l", "le", "mi", "ţi", "şi", "au", "a", "am", "ai",
               "aţi", "ar", "aş"}
FR_HYPH_L = {"c’est", "peut", "est", "dit", "vis", "au", "là", "ci", "demi", "sous", "non",
             "grand", "arc", "après", "avant", "chef", "porte", "contre", "entre", "quelqu’un",
             "petit", "belle", "beau", "sans", "pêle", "tête", "moi", "toi", "lui", "nous",
             "vous", "eux", "elle", "soi", "celui", "celle", "ceux", "jusque"}
EN_HYPH_L = {"self", "well", "ill", "half", "two", "three", "four", "good", "so", "non"}


def unbreak_gloss(g, lang):
    def rep(m):
        left, right = m.group(1), m.group(2)
        l, r = left.lower(), right.lower()
        keep = ((lang == "ro" and (l in RO_CLITIC_L or r in RO_CLITIC_R))
                or (lang == "fr" and l in FR_HYPH_L)
                or (lang == "en" and l in EN_HYPH_L))
        return left + ("-" if keep else "") + right
    g = re.sub(r"([^\s" + MARK + r"(]*)" + MARK + r"([^\s" + MARK + r"),;]*)", rep, g)
    return g.replace(MARK, "")


def clean_gloss(g, lang):
    g = unbreak_gloss(g, lang)
    return re.sub(r"\s+", " ", g).strip(" ;,")


CONT_RE = {"en": re.compile(r"^(of|to)\s"), "fr": re.compile(r"^(de\s|d’|du\s|des\s)"),
           "ro": re.compile(r"^(de\s|a\s)")}


def split_senses(g, lang):
    """Split a gloss on ';' outside parentheses.  A part that only continues
    the one before ("action of X; of Y") stays attached; a bare "etc." goes."""
    parts, depth, cur = [], 0, ""
    for ch in g:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == ";" and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    out = []
    for p in parts:
        p = p.strip(" ,")
        if not p or re.fullmatch(r"etc\.?", p):
            continue
        if out and CONT_RE[lang].match(p):
            out[-1] = out[-1] + "; " + p
        else:
            out.append(p)
    return out


def skeleton(s):
    """Consonant skeleton used to compare a headword with its pronunciation
    (the pronunciation writes x as cs and d/t/g as dh/th/gh)."""
    s = s.lower().replace(MARK, "").replace("x", "cs")
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^bcdfghjklmnpqrstvwz]", "", s)
    return re.sub(r"([dtg])h", r"\1", s)


def pron_agrees(headword, pron):
    if not pron:
        return True
    alts = re.split(r"\s+shi\s+|\s*,\s*|\s+i\s+", pron)
    return any(skeleton(headword) == skeleton(a) for a in alts)


def pos_of(label):
    lab = label.strip()
    lab = re.sub(r"^\(\w+\)\s*", "", lab)           # (mi) vb …
    m = re.match(r"^(" + POS_TOKENS + r")\b", lab)
    if not m:
        return ""
    t = m.group(1)
    if t in ("sm", "sf", "sn", "smf", "simf"):
        return "noun"
    if t == "vb":
        return "verb"
    if t in ("adg", "adgf", "adj"):
        return "adj"
    if t == "adv":
        return "adv"
    if t == "prip":
        return "prep"
    if t == "cong":
        return "conj"
    if t in ("pron", "pr"):
        return "pron"
    if t == "num":
        return "num"
    return "other"


def glosses_of(rest):
    """{ro,fr,en} from the brace groups; the source's order is ro, fr, en."""
    groups = BRACE_RE.findall(rest)
    gl = {}
    if not groups:
        return gl
    labelled = []
    for g in groups:
        lang = None
        for l in ("ro", "fr", "en"):
            if re.match(r"^\s*" + l + r"\s*[:;]", g):
                lang = l
        labelled.append(lang)
    order = ("ro", "fr", "en")
    for i, (g, lang) in enumerate(zip(groups[:3], labelled[:3])):
        if lang is None and len(groups) >= 3:
            lang = order[i]                      # label dropped by the author
            if lang in [x for x in labelled[:3] if x]:
                continue
        if lang is None or lang in gl:
            continue
        txt = LABEL_RE[lang].sub("", g, count=1)
        txt = clean_gloss(txt, lang)
        if txt and txt != "?":
            gl[lang] = txt
    return gl


def parse_sub(sub):
    """One sub-entry -> dict or None."""
    sub = sub.strip()
    m = SUB_RE.match(sub)
    if m and re.search(r"(^|\s)" + POS_TOKENS + r"(\s|$)", m.group("hw")):
        m = None                       # that parenthesis was not a pronunciation
    if m:
        hw, pron, rest = m.group("hw").strip(), m.group("pron"), m.group("rest")
    else:
        m2 = SUB2_RE.match(sub)
        if not m2:
            return None
        hw, pron, rest = m2.group("hw").strip(), "", m2.group("rest")
    label = rest.split("–", 1)[0] if "–" in rest else rest[:40]
    body = (rest.split("–", 1)[1] if "–" in rest else "").strip()
    d = {"hw_raw": hw, "pron": pron or "", "pos": pos_of(label), "gl": glosses_of(rest),
         "sameas": None, "pointer": False}
    if re.match(r"^\(?\s*vedz\s+(tu\s+)?", body) or re.match(r"^\(?\s*scriari\s+neapru", body):
        d["pointer"] = True
    if not d["gl"]:
        head = re.split(r"\{|\bex:", rest, maxsplit=1)[0]
        ms = SAMEAS_RE.search(head)
        if ms:
            d["sameas"] = ms.group(1).strip()
        elif re.search(r"\bvedz\b", head):
            d["pointer"] = True
    return d


def split_headword(hw_raw):
    """'abatiri^1 /abatire' -> (['abatiri', 'abatire'], '1')."""
    hom = re.search(r"\^(\d+)", hw_raw)
    hw = re.sub(r"\^\S*", "", hw_raw)
    hw = re.sub(r"\s+", " ", hw).strip()
    hw = re.sub(r"\s*/\s*", "/", hw)
    return [v.strip() for v in hw.split("/") if v.strip()], (hom.group(1) if hom else "")


def main():
    dump = None
    if "--dump-entries" in sys.argv:
        dump = sys.argv[sys.argv.index("--dump-entries") + 1]
    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
    tmp.close()
    try:
        subprocess.run(["pdftotext", "-bbox-layout", PDF, tmp.name], check=True)
        entries = list(read_entries(tmp.name))
    finally:
        os.unlink(tmp.name)
    if dump:
        with open(dump, "w", encoding="utf-8") as f:
            f.write("\n".join(entries))

    stats = Counter()
    stats["entries"] = len(entries)
    recs = []
    unbroken = set()          # every headword variant printed without a line break
    first_variants = set()    # ... and those standing first before a slash
    for eno, ent in enumerate(entries):
        for sub in re.split(r"\s*§\s*", ent):
            if not sub.strip():
                continue
            stats["subentries"] += 1
            d = parse_sub(sub)
            if d is None:
                stats["skip_unparsed"] += 1
                continue
            raw = d["hw_raw"]
            if "*" in raw:                     # x^* = inflected-form pointer
                stats["skip_inflected_form_pointer"] += 1
                continue
            if MARK not in raw:
                vs, _ = split_headword(raw)
                unbroken.update(vs)
                first_variants.update(vs[:1])
            d["eno"] = eno
            recs.append(d)

    def first(hw):
        v = split_headword(hw)[0]
        return v[0] if v else None

    kept = []
    for d in recs:
        raw = d["hw_raw"]
        trusted = True
        if MARK in raw:
            stats["headword_broken_at_line_end"] += 1
            fixed = []
            for part in raw.split("/"):
                if MARK not in part:
                    fixed.append(part)
                    continue
                glued = part.replace(MARK, "")
                hyph = part.replace(MARK, "-")
                g_ok = first(glued) in unbroken
                h_ok = first(hyph) in unbroken
                if g_ok and not h_ok:
                    fixed.append(glued)
                elif h_ok and not g_ok:
                    fixed.append(hyph)
                else:
                    fixed.append(glued)
                    trusted = False
            raw = "/".join(fixed)
            stats["headword_break_resolved" if trusted else "headword_break_unresolved"] += 1
        variants, hom = split_headword(raw)
        if not variants or any(not HW_OK_RE.fullmatch(v) or len(v) > 40 for v in variants):
            stats["skip_odd_headword"] += 1
            continue
        # "x/y": y is normally the same word with the other final vowel
        # (-i/-e).  Anything else in second place is kept only if that
        # spelling also heads a line of its own somewhere.
        keep = [variants[0]]
        for v in variants[1:]:
            if v[:-1] == variants[0][:-1] or v in first_variants:
                keep.append(v)
            else:
                stats["second_variant_dropped"] += 1
        variants = keep
        if trusted and not pron_agrees(variants[0], d["pron"]):
            trusted = False
            stats["headword_disagrees_with_pronunciation"] += 1
        if d["pointer"] and not d["gl"] and not d["sameas"]:
            stats["skip_pointer_vedz"] += 1
            continue
        d.update(variants=variants, hom=hom, trusted=trusted)
        kept.append(d)

    by_hw = defaultdict(list)
    fam = defaultdict(dict)
    for d in kept:
        for v in d["variants"]:
            by_hw[v].append(d)
            fam[d["eno"]].setdefault((v, d["hom"]), d)
            fam[d["eno"]].setdefault((v, ""), d)

    def lookup(d, depth=0):
        """Glosses of the word that d is 'unã cu'."""
        if d["gl"] or not d["sameas"] or depth > 3:
            return d["gl"]
        tgt_raw = d["sameas"]
        for t in dict.fromkeys([tgt_raw.replace(MARK, ""), tgt_raw.replace(MARK, "-")]):
            tv, th = split_headword(t)
            if not tv:
                continue
            t0 = tv[0]
            x = fam[d["eno"]].get((t0, th))
            if x is not None and x is not d:
                g = lookup(x, depth + 1)
                if g:
                    return g
            cands = [c for c in by_hw.get(t0, []) if c is not d and (not th or c["hom"] == th)]
            gls = []
            for c in cands:
                g = lookup(c, depth + 1)
                if g:
                    gls.append(g)
            if gls and len({tuple(sorted(g.items())) for g in gls}) == 1:
                return gls[0]
        return {}

    outs = {"en": "cunia-2008.tsv", "ro": "cunia-2008-ro.tsv", "fr": "cunia-2008-fr.tsv"}
    rows = {k: [] for k in outs}
    seen = {k: set() for k in outs}
    doubtful = []
    for d in kept:
        gl = d["gl"]
        if gl:
            stats["sub_with_own_gloss"] += 1
        elif d["sameas"]:
            gl = lookup(d)
            stats["sub_sameas_resolved" if gl else "sub_sameas_unresolved"] += 1
        else:
            stats["sub_no_gloss"] += 1
        if not gl:
            continue
        for lang in ("ro", "fr", "en"):
            if lang not in gl:
                continue
            for sense in split_senses(gl[lang], lang):
                for v in d["variants"]:
                    row = (v, sense, lang, d["pos"])
                    if not d["trusted"]:
                        doubtful.append(row)
                    elif row not in seen[lang]:
                        seen[lang].add(row)
                        rows[lang].append(row)
    header = "headword\tgloss\tgloss_lang\tpos\n"
    for lang, fn in outs.items():
        with open(os.path.join(HERE, fn), "w", encoding="utf-8") as f:
            f.write(header)
            for row in rows[lang]:
                f.write("\t".join(row) + "\n")
        stats["rows_" + lang] = len(rows[lang])
        stats["headwords_" + lang] = len({r[0] for r in rows[lang]})
    with open(os.path.join(HERE, "cunia-2008.doubtful.tsv"), "w", encoding="utf-8") as f:
        f.write(header)
        for row in doubtful:
            f.write("\t".join(row) + "\n")
    stats["rows_doubtful"] = len(doubtful)
    for k in sorted(stats):
        print(f"{k}\t{stats[k]}", file=sys.stderr)


if __name__ == "__main__":
    main()
