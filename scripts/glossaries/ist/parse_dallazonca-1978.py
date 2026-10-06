#!/usr/bin/env python3
"""Dalla Zonca, Vocabolario dignanese-italiano (ms. before 1857; ed. Debeljuh, 1978)
-> dallazonca-1978.tsv  (+ dallazonca-1978.doubtful.tsv)

Input (in raw/):
  dallazonca_1978_reocr_ita_words.tsv.gz   word boxes from our own re-OCR of the
        archive.org page images (tesseract 5, tessdata_best `ita`), each word with
        stroke-thickness figures; made by ocr_dallazonca.py.
  dallazonca_1978_reread_tokens.tsv        (optional) second readings of single
        head tokens, made by reread_dallazonca.py; used only for the d/ò repair.

The printed page is two columns of entries `headword - gloss`: headword in bold,
gloss in roman, notes in italic.  An entry starts on a line that opens in bold;
its headword runs up to the first dash that is followed by non-bold type.

Python 3, standard library only.   python3 parse_dallazonca-1978.py [--stats]
"""
import csv, gzip, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS = os.path.join(HERE, "raw", "dallazonca_1978_reocr_ita_words.tsv.gz")
REREAD = os.path.join(HERE, "raw", "dallazonca_1978_reread_tokens.tsv")
CHECKED = os.path.join(HERE, "raw", "dallazonca_1978_reread_checked.tsv")
OUT = os.path.join(HERE, "dallazonca-1978.tsv")
OUT_DOUBT = os.path.join(HERE, "dallazonca-1978.doubtful.tsv")
FIRST_LEAF, LAST_LEAF = 32, 335          # printed pp. 1-304; the rest is the editor's

DASHES = {"-", "–", "—", "―", "_", "--", "=", "~", "—-", "-—"}
ACC = "àèìòùáéíóú"
LETTER = re.compile(r"[a-zàèìòùáéíóúäëïöüâêîôûç]", re.I)


def letters(s):
    return len(LETTER.findall(s))


# ---------------------------------------------------------------- page layout
def read_pages(path):
    pages = collections.OrderedDict()
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            p = int(r["page"])
            if FIRST_LEAF <= p <= LAST_LEAF:
                pages.setdefault(p, []).append(r)
    return pages


def two_means(vals):
    vals = sorted(vals)
    if len(vals) < 8:
        return None
    lo, hi = vals[len(vals) // 4], vals[-max(1, len(vals) // 10)]
    for _ in range(30):
        a = [v for v in vals if abs(v - lo) <= abs(v - hi)]
        b = [v for v in vals if abs(v - lo) > abs(v - hi)]
        if not a or not b:
            return None
        nlo, nhi = sum(a) / len(a), sum(b) / len(b)
        if abs(nlo - lo) < 1e-4 and abs(nhi - hi) < 1e-4:
            break
        lo, hi = nlo, nhi
    return lo, hi


class W:
    __slots__ = ("t", "x", "y", "w", "h", "b", "raw", "page", "eol", "full")

    def __init__(self, t, x, y, w, h, b, raw, page):
        self.t, self.x, self.y, self.w, self.h, self.b, self.page = t, x, y, w, h, b, page
        self.raw = raw                      # dtmean; b = bold score, > 0 means bold
        self.eol = False
        self.full = True                    # set on the first word of a line


def page_lines(page, rows, stats):
    """-> list of lines (each a list of W) in reading order: left column, then right."""
    vals = [float(r["dtmean"]) for r in rows if letters(r["text"]) >= 3]
    tm = two_means(vals)
    if tm and tm[1] - tm[0] > 0.2:
        lo, hi = tm
    else:                                   # page with (almost) one kind of type
        lo, hi = 1.75, 2.2
        stats["pages_default_threshold"] += 1
    thr, span = (lo + hi) / 2, (hi - lo)
    groups = collections.OrderedDict()
    for r in rows:
        w = W(r["text"], int(r["left"]), int(r["top"]), int(r["width"]), int(r["height"]),
              (float(r["dtmean"]) - thr) / span, float(r["dtmean"]), page)
        groups.setdefault((r["block"], r["par"], r["line"]), []).append(w)
    lines = [sorted(ws, key=lambda w: w.x) for ws in groups.values()]
    # column starts: median left edge of the lines in each half of the page
    lefts = sorted(ln[0].x for ln in lines if len(ln) >= 2)
    if not lefts:
        return []
    cm = two_means(lefts)
    if cm and cm[1] - cm[0] > 500:
        mid = (cm[0] + cm[1]) / 2
        right = [x for x in lefts if x > mid]
        c1 = right[len(right) // 2]
    else:                                   # a one-column page (never expected)
        c1 = lefts[0] + 776
        stats["pages_one_column"] += 1
    out = []
    for ln in lines:
        a = [w for w in ln if w.x < c1 - 40]
        b = [w for w in ln if w.x >= c1 - 40]
        if a and b:                         # tesseract ran a line across the gutter
            stats["lines_split_at_gutter"] += 1
            out.append((0, a)); out.append((1, b))
        else:
            out.append((1 if b else 0, ln))
    # tesseract sometimes cuts one printed line into two pieces: put them back
    out.sort(key=lambda z: (z[0], sorted(w.y + w.h / 2 for w in z[1])[len(z[1]) // 2]))
    merged = []
    for col, ln in out:
        yc = sorted(w.y + w.h / 2 for w in ln)[len(ln) // 2]
        if merged and merged[-1][0] == col and abs(merged[-1][1] - yc) < 16:
            merged[-1][2].extend(ln)
            merged[-1][2].sort(key=lambda w: w.x)
            stats["line_pieces_rejoined"] += 1
        else:
            merged.append([col, yc, ln])
    out = [(col, ln) for col, yc, ln in merged]
    # A new letter starts under a centred capital in mid-page: the entries above
    # it (end of the old letter, in two columns) come before those below it.
    cuts = []
    for col, ln in out:
        txt = "".join(w.t for w in ln)
        xc = (ln[0].x + ln[-1].x + ln[-1].w) / 2
        if re.fullmatch(r"[A-Z]", txt) and abs(xc - (c1 - 35)) < 160:
            cuts.append(min(w.y for w in ln))
            stats["letter_headings"] += 1
    # The capital itself is often missing from the OCR: then the white band it
    # stands in shows as a gap of several lines across both columns.
    tops = {0: [], 1: []}
    for col, ln in out:
        if len(ln) >= 2 or letters(ln[0].t) >= 3:
            tops[col].append(min(w.y for w in ln))
    lt = sorted(tops[0])
    for a_, b_ in zip(lt, lt[1:]):
        if b_ - a_ > 170 and a_ > lt[0] + 60 and not any(a_ + 40 < y < b_ - 20 for y in tops[1]):
            if not any(a_ < c <= b_ for c in cuts):
                cuts.append((a_ + b_) / 2)
                stats["letter_breaks_from_gap"] += 1
    # Running head ("CAG"), page number and signature number stand apart from
    # the text block: a short line at the top or foot of a column with more than
    # a line of white between it and the text.
    drop = set()
    for col in (0, 1):
        cl = sorted((min(w.y for w in ln), id(ln), ln) for c, ln in out if c == col)
        for seq in (cl, cl[::-1]):
            for n, (y, _, ln) in enumerate(seq[:2]):
                txt = "".join(w.t for w in ln)
                if letters(txt) > 6 or len(txt) > 9:
                    break
                if n + 1 < len(seq) and abs(seq[n + 1][0] - y) > 75:
                    drop.add(id(ln))
                else:
                    break
    body = []
    for col, ln in out:
        txt = " ".join(w.t for w in ln)
        y = min(w.y for w in ln)
        if id(ln) in drop or re.fullmatch(r"[A-Z]", txt):
            stats["lines_dropped_head_foot"] += 1
            continue
        band = sum(1 for c in cuts if y > c)
        body.append((band * 2 + col, y, ln))
    body.sort(key=lambda z: (z[0], z[1]))
    # The ink gets heavier or lighter across a page, so roman type is measured
    # locally: the 20th percentile of the longer words within +-320 px in the
    # same column (most words are gloss words, i.e. roman).
    for col in sorted(set(c for c, _, _ in body)):
        colws = [(y, w) for c, y, ln in body if c == col for w in ln if letters(w.t) >= 4]
        if len(colws) < 12:
            continue
        for c, y, ln in body:
            if c != col:
                continue
            near = sorted(w.raw for yy, w in colws if abs(yy - y) <= 320)
            if len(near) >= 10:
                base = near[len(near) // 5] + 0.03
                for w in ln:
                    w.b = (w.raw - base) / span - 0.5
    # right margin of each column: a line that stops short of it ends a paragraph
    res = []
    for col in sorted(set(c for c, _, _ in body)):
        ends = sorted(ln[-1].x + ln[-1].w for c, y, ln in body if c % 2 == col % 2 and len(ln) >= 3)
        margin = ends[int(len(ends) * 0.9)] if ends else 0
        for c, y, ln in body:
            if c != col:
                continue
            ln[-1].eol = True
            ln[0].full = (ln[-1].x + ln[-1].w) >= margin - 110
            res.append(ln)
    return res


# ------------------------------------------------------------ entry assembly
def wmean_bold(ws):
    num = den = 0.0
    for w in ws:
        k = letters(w.t)
        if k == 0:
            continue
        k = min(k, 6)
        num += k * w.b; den += k
    return (num / den) if den else None


def find_sep(ln, depth, nxt_line=None):
    """index of the head/gloss dash in this line, or None.  `depth` = parentheses
    still open from earlier head lines.  The dash is the first one followed by
    roman type (the dash inside "(al — se màgna)" is followed by bold)."""
    for i, w in enumerate(ln):
        if w.t in DASHES:
            closes_later = any(")" in x.t and "(" not in x.t for x in ln[i + 1:])
            if depth > 0 and (w.t in ("—", "―", "–") or closes_later):
                continue                    # the lemma sign in "(al — se màgna)"
            rest = [x for x in ln[i + 1:] if letters(x.t)]
            nxt = rest[:4]
            after = wmean_bold(nxt)
            before = wmean_bold(ln[max(0, i - 4):i])
            if after is None:               # dash ends the line
                if depth <= 0:
                    return i
            elif after < -0.15 or (before is not None and before - after > 0.4 and after < 0.15):
                return i
            elif sum(letters(x.t) for x in rest) <= 7 and nxt_line is not None and ln[0].full:
                # one or two short words after the dash: too little ink to judge,
                # so look at the line below (the gloss runs on in roman)
                below = wmean_bold(nxt_line[:4])
                if below is not None and below < -0.15 and find_sep(nxt_line, 0) is None:
                    return i
        depth += w.t.count("(") - w.t.count(")")
    return None


def wide_gap(ws):
    """True if two neighbouring words stand more than 58 px apart.  Word spaces
    in this book are 19 px (median), 42 px at the 99.9th percentile even in
    stretched lines; a wider hole means tesseract returned no text for some ink
    ("cuv        - coprirsi" for "cuvaèrzisse - coprirsi")."""
    return any(b.x - (a.x + a.w) > 58 for a, b in zip(ws, ws[1:]))


def entries(pages, stats):
    lines = []
    for page, rows in pages.items():
        for ln in page_lines(page, rows, stats):
            lines.append((page, ln))
    cur = None
    for n, (page, ln) in enumerate(lines):
        nxt_line = lines[n + 1][1] if n + 1 < len(lines) else None
        in_head = cur is not None and not cur["sep"]
        depth = 0
        if in_head:
            s = " ".join(w.t for w in cur["head"])
            depth = s.count("(") - s.count(")")
        i = find_sep(ln, depth, nxt_line)
        pre = ln if i is None else ln[:i]
        b = wmean_bold(pre)
        first_bold = bool(pre) and (wmean_bold(pre[:2]) or -1) > 0
        if i is not None and pre and letters(pre[0].t) >= 3 and pre[0].b > 0.1:
            b = max(b, pre[0].b)            # "càldo (sost.) - caldo": bold word, italic label
        if in_head:
            if i is not None:
                cur["head"] += pre; cur["gloss"] += ln[i + 1:]; cur["sep"] = True
                cur["gap"] = cur["gap"] or wide_gap(ln[:i + 1])
            elif b is not None and b > 0 and cur["full"]:
                cur["head"] += ln; cur["full"] = ln[0].full
                cur["gap"] = cur["gap"] or wide_gap(ln)
            else:                           # roman line while still waiting for the dash
                cur["sep"] = True; cur["nosep"] = True; cur["gloss"] += ln
            continue
        if i == 0 and ln[0].x > min(w_.x for _, l_ in lines[max(0, n - 3):n + 4] for w_ in l_[:1]
                                    if abs(l_[0].x - ln[0].x) < 500) + 45:
            # the line begins with the dash, well inside the column: tesseract gave
            # no text for the bold head before it
            if cur: yield cur
            cur = dict(head=[], gloss=list(ln[1:]), sep=True, page=page, nosep=False, full=True,
                       x=ln[0].x, y=ln[0].y, orphan=True, gap=False, sepx=ln[0].x, sepy=ln[0].y,
                       colx=None, lines=1)
            continue
        if i is not None and (b is None or b > 0) and (pre or cur is None):
            if cur: yield cur
            cur = dict(head=list(pre), gloss=list(ln[i + 1:]), sep=True, page=page, nosep=False, full=True,
                       x=ln[0].x, y=ln[0].y, orphan=False, gap=wide_gap(ln[:i + 1]),
                       sepx=ln[i].x, sepy=ln[i].y, colx=ln[0].x, lines=1)
        elif i is None and b is not None and b > 0.1 and first_bold and ln[0].full:
            # a headword too long for one line: it must fill the line it starts on
            if cur: yield cur
            cur = dict(head=list(ln), gloss=[], sep=False, page=page, nosep=False, full=True,
                       x=ln[0].x, y=ln[0].y, orphan=False, gap=wide_gap(ln), sepx=None, sepy=None,
                       colx=ln[0].x, lines=2)
        elif cur is not None:
            cur["gloss"] += ln
        else:
            stats["lines_before_first_entry"] += 1
    if cur:
        yield cur


# ------------------------------------------------------------------ cleaning
def join_words(ws):
    """join OCR words; undo end-of-line hyphenation."""
    out = []
    glue = False
    for w in ws:
        t = w.t
        if glue and out:
            out[-1] = out[-1][:-1] + t
        else:
            out.append(t)
        glue = w.eol and len(t) > 1 and t.endswith("-") and LETTER.match(t[-2] or "")
    return " ".join(out)


# "(v. l'it.)" = vedi l'italiano: a pointer to the Italian dictionary, printed in
# italic and read by the OCR in many shapes ("(». l'it.)", "(vw. lit.)", "(v. l'iz.)",
# "(di tutti v. l'it.)", "(v. l'it. di ambo)").  The "l'it." itself is the mark.
VITCORE = r"(?:\bV?l\s?['’`‘]\s?i[tzfl]\b|\blit\.|\bnell?\s?['’`‘]?\s?i[tzf]\.)"
RE_VITSEG = re.compile(VITCORE)
RE_XREF = re.compile(r"^[vo»]{1,2}\.\s")          # "(v. fragiòtto)": see another entry


POS_LABELS = [
    (re.compile(r"^\(?\s*(sost|sostantivo|s)\s*\.?\s*(masch|femm|m|f)?\.?\s*\)?$", re.I), "noun"),
    (re.compile(r"^\(?\s*(agg|add|aggettivo)\s*\.?\s*\)?$", re.I), "adj"),
    (re.compile(r"^\(?\s*(verbo|verb|v\. ?(att|n|neutro|rifl)?)\s*\.?\s*\)?$", re.I), "verb"),
    (re.compile(r"^\(?\s*(avv|avverbio)\s*\.?\s*\)?$", re.I), "adv"),
    (re.compile(r"^\(?\s*(prep|preposizione)\s*\.?\s*\)?$", re.I), "prep"),
    (re.compile(r"^\(?\s*(cong|congiunzione)\s*\.?\s*\)?$", re.I), "conj"),
    (re.compile(r"^\(?\s*(pron|pronome)\s*\.?\s*\)?$", re.I), "pron"),
    (re.compile(r"^\(?\s*(inter|interiez|esclam|interiezione)\s*\.?\s*\)?$", re.I), "other"),
    # "(nome)": Dalla Zonca's word for the nominal form beside a homograph verb,
    # in practice the past participle used as adjective ("baendà (nome) - bendato")
    # but also plain nouns; too mixed to map, so pos stays empty.
    (re.compile(r"^\(?\s*(nome|more|mome|nomo|none)\s*\.?\s*\)?$", re.I), ""),
]


def split_label(head_ws):
    """strip a trailing parenthetical in italic (a grammatical label) from the head.
    -> (head words, None | (label text, pos or None))"""
    ws = list(head_ws)
    if len(ws) < 2 or not ws[-1].t.rstrip(".,;:").endswith(")"):
        return ws, None
    k = None
    for a in range(len(ws) - 1, 0, -1):
        if ws[a].t.startswith("("):
            k = a
            break
        if ")" in ws[a].t and a != len(ws) - 1:
            break
    if k is None:
        return ws, None
    tail = ws[k:]
    lab = " ".join(w.t for w in tail)
    for rx, pos in POS_LABELS:
        if rx.match(lab):
            return ws[:k], (lab, pos)
    b = wmean_bold(tail)
    if b is not None and b < -0.15 and not any(w.t in DASHES for w in tail):
        return ws[:k], (lab, None)          # an italic note we cannot map: text kept
    return ws, None


def clean_gloss(g):
    def par(m):
        segs = [x.strip() for x in m.group(1).split(",")]
        keep = [x for x in segs if x and not RE_VITSEG.search(x) and not RE_XREF.match(x)]
        return "(" + ", ".join(keep) + ")" if keep else ""
    g = re.sub(r"\(([^()]*)\)", par, g)
    g = re.sub(r"\([^()]*" + VITCORE + r"[^()]*$", "", g)      # "(v. l'it." cut off at the line end
    g = re.sub(r"\s+([,;.:!?)])", r"\1", g)
    g = re.sub(r"\(\s+", "(", g)
    g = re.sub(r"\s{2,}", " ", g).strip(" ,;")
    m = re.fullmatch(r"[vo»]\.\s+(.+?)\s+nell?\s?['’]?\s?i[tf]\.?", g)
    if m:                                    # "v. petto nell'it." -> petto
        g = m.group(1)
    return g


HEAD_OK = re.compile(r"[a-zàèìòùáéíóúâêîôûäëïöüçA-ZÀÈÌÒÙ’'`\s,;.!?()—\-/]+")


def load_reread():
    """second readings made by reread_dallazonca.py, keyed by (kind, leaf, left, top);
    then the rows settled by eye on the scan (decision *-checked), which win."""
    d = {}
    for path in (REREAD, CHECKED):
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                    d[(r["kind"], int(r["page"]), int(r["left"]), int(r["top"]))] = r
    return d


def dgrave_candidate(tok):
    """bold ò before u is often read as d ("dun" for "òun", "aiduto" for "aiòuto").
    Dalla Zonca writes one grave accent per stressed word, so a token with "du"
    and no accent at all is the suspect shape."""
    t = tok.lower()
    return "du" in t and not any(c in t for c in ACC)


def prepared_entries(stats, words=None):
    pages = read_pages(words or WORDS)
    ents = list(entries(pages, stats))
    for e in ents:
        e["head_ws"], e["label"] = split_label(e["head"]) if e["head"] else ([], None)
    stats["pages"] = len(pages)
    return ents


def main():
    stats = collections.Counter()
    reread = load_reread()
    good, doubt, qa = [], [], []
    ents = prepared_entries(stats)
    kept = []
    for e in ents:
        stats["entries"] += 1
        head_ws, label = e["head_ws"], e["label"]
        why = []
        if e["orphan"] or e["gap"]:
            # part of the head came back empty from the OCR: take the second
            # reading of that line if there is one
            rr = reread.get(("head", e["page"], e["sepx"] or 0, e["sepy"] or 0))
            if rr and rr["decision"] in ("read", "read-checked"):
                head_ws = [W(t, e["x"], e["y"], 0, 0, 1.0, 0.0, e["page"]) for t in rr["repaired"].split()]
                head_ws, label = split_label(head_ws)
                stats["entries_head_from_second_reading"] += 1
                if rr["decision"] == "read" and any(dgrave_candidate(w.t) for w in head_ws):
                    why.append("d-or-ograve")
            elif e["orphan"]:
                stats["entries_head_not_read_dropped"] += 1
                continue
            else:
                why.append("gap")
        # d/ò repair of single head tokens, only where a second reading says so
        for w in head_ws:
            rr = reread.get(("token", w.page, w.x, w.y))
            if rr and rr["decision"] in ("repair", "repair-rule", "repair-checked"):
                w.t = rr["repaired"]; stats["tokens_" + rr["decision"].replace("-", "_") + "_d_to_ograve"] += 1
            elif rr and rr["decision"] == "unsure":
                why.append("d-or-ograve")
            elif not rr and reread and dgrave_candidate(w.t) and w.w:
                why.append("d-or-ograve")
        for w in head_ws:                   # glyph confusions that cannot be anything else
            t = w.t
            t2 = re.sub(r"(?<=[a-zàèìòù])[\]|](?=$|[,;.!?)])", "l", t)   # campagnò] -> campagnòl
            if t2 == "0":
                t2 = "o"                    # the word "o" (or) read as zero
            if t2 != t:
                w.t = t2; stats["tokens_repaired_glyph"] += 1
        head = join_words(head_ws)
        head = re.sub(r"\s+([,;.:!?)])", r"\1", head)
        head = re.sub(r"\(\s+", "(", head).strip()
        head = head.replace("’", "'").replace("‘", "'").replace("`", "'")
        gloss = clean_gloss(join_words(e["gloss"]))
        gloss = gloss.replace("’", "'").replace("‘", "'")
        pos = ""
        if label:
            lab, p = label
            if p is None:
                gloss = (gloss + " " + lab).strip()
                stats["head_notes_kept_in_gloss"] += 1
            else:
                pos = p
                stats["pos_from_label"] += 1
        else:
            m = re.match(r"^([^,;(]+?)\s*\((avv|agg|sost|verbo)\.?\)", gloss)
            if m:
                pos = {"avv": "adv", "agg": "adj", "sost": "noun", "verbo": "verb"}[m.group(2)]
                stats["pos_from_gloss_label"] += 1
        if e["nosep"]:
            why.append("no-dash")
        if not head or not gloss:
            why.append("empty")
        if head and not HEAD_OK.fullmatch(head):
            why.append("odd-char")
        if head.count("(") != head.count(")"):
            why.append("paren")
        if any(w.t in DASHES for w in e["gloss"]):
            why.append("second-dash")       # most often two entries run together
        if "(?)" in head or "(?)" in " ".join(w.t for w in e["head"]):
            why.append("editor-query")      # the editor's own doubt about the manuscript reading
        if re.search(r"[àèìòù][àèìòù]", head):
            why.append("two-accents")       # "bràùdi": two stress marks side by side is an OCR slip
        e.update(head=head, gloss=gloss, pos=pos, why=sorted(set(why)))
        kept.append(e)
    ents = kept
    # Alphabetical check.  The book runs A-Z by first word, and phrases are filed
    # under their key word ("in bànda" under B), so every head must hold a word
    # beginning with the letter of the stretch it stands in.  A head with none has
    # lost its first letters in the OCR ("roustulà" for "broustulà").
    def ini(tok):
        m = LETTER.search(tok)
        c = m.group(0).lower() if m else ""
        return {"à": "a", "è": "e", "ì": "i", "ò": "o", "ù": "u"}.get(c, c)
    firsts = [ini(e["head"]) for e in ents]
    sect = []                               # letters allowed at entry k (one, or two at a change of letter)
    for k in range(len(ents)):
        ok = set()
        for win in (firsts[max(0, k - 9):k], firsts[k + 1:k + 10]):
            c = collections.Counter(x for x in win if x)
            if c and c.most_common(1)[0][1] >= 5:
                ok.add(c.most_common(1)[0][0])
        sect.append(ok)
    for k, e in enumerate(ents):
        toks = re.findall(r"[^\s,;()]+", e["head"])
        if sect[k] and not any(ini(t) in sect[k] for t in toks):
            e["why"].append("alpha-order")
    for k, e in enumerate(ents):
        rows = []
        parts = [p.strip() for p in e["head"].split(",")]
        if len(parts) > 1 and all(p and " " not in p and "(" not in p and ")" not in p for p in parts):
            stats["entries_split_variants"] += 1
            if sect[k] and ini(parts[0]) not in sect[k] and not e["why"]:
                e["why"].append("alpha-order")   # first variant must carry the letter
            for p in parts:
                rows.append((p, e["gloss"], "it", e["pos"]))
        else:
            rows.append((e["head"], e["gloss"], "it", e["pos"]))
        for r_ in rows:
            qa.append(r_ + (str(e["page"]), str(e["x"]), str(e["y"]), ",".join(e["why"])))
        if e["why"]:
            stats["entries_doubtful"] += 1
            for w in e["why"]:
                stats["doubt_" + w] += 1
            if "--debug" in sys.argv:
                print("DOUBT p.%d %s | %s" % (e["page"] - 31, ",".join(e["why"]), e["head"][:90]), file=sys.stderr)
            doubt += rows
        else:
            good += rows
    for path, rows in ((OUT, good), (OUT_DOUBT, doubt)):
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write("headword\tgloss\tgloss_lang\tpos\n")
            for r in rows:
                f.write("\t".join(x.replace("\t", " ") for x in r) + "\n")
    if "--qa" in sys.argv:                   # rows with leaf and position, for checking against the scan
        with open(sys.argv[sys.argv.index("--qa") + 1], "w", encoding="utf-8") as f:
            f.write("headword\tgloss\tgloss_lang\tpos\tleaf\tx\ty\tdoubt\n")
            for r in qa:
                f.write("\t".join(r) + "\n")
    stats["rows_good"] = len(good); stats["rows_doubtful"] = len(doubt)
    if "--stats" in sys.argv:
        for k in sorted(stats):
            print("%-34s %d" % (k, stats[k]), file=sys.stderr)


if __name__ == "__main__":
    if "--words" in sys.argv:                # test run on another word table
        WORDS = sys.argv[sys.argv.index("--words") + 1]
    if "--reread" in sys.argv:
        REREAD = sys.argv[sys.argv.index("--reread") + 1]
    if "--checked" in sys.argv:
        CHECKED = sys.argv[sys.argv.index("--checked") + 1]
    main()
