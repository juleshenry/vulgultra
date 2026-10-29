#!/usr/bin/env python3
"""Bartoli 1906, Das Dalmatische II, cols. 169-240: "Anhang: Vegliotisches Wortverzeichnis"
   raw/bartoli_1906_wortverzeichnis_ocr.jsonl  ->  bartoli-1906-vegliote.tsv
                                                    bartoli-1906-vegliote.doubtful.tsv

The JSONL is our own OCR of the scan (see ocr_bartoli-1906-vegliote.py): one object per
printed line, each word with  t = text, i = 1 if set in italics, c = OCR confidence,
f = flags raised by the image checks, x/x2 = left/right edge in pixels.

Shape of an entry in the source (hanging indent; headword letter-spaced italic):

    akái̯t 29, acait 4, 118, acaid 93, 115 (S. 137), 118, káit 51 aceto
    andure 31, 547, anduar 78, 88, 93 andare (camminare) — jonda 82, junda 47 va (vieni) — ...

  italic            = Vegliote forms (headword, then variants), each followed by the
                      numbers of the texts where it occurs
  upright words     = the Italian gloss (now and then a German word: "oder", "und")
  after ";" or "—"  = further forms of the same word (plural, feminine, verb forms),
                      some with a gloss of their own

Rows written: every form of the first group with the entry's gloss; every form of a
later group that has its own gloss, with that gloss.  Later groups without a gloss
(bare plurals, feminines) are not written: the source gives them no meaning of their own.
Nothing is normalised.  A form goes to the .doubtful.tsv file instead of the main file
when the OCR stage flagged it, when it holds a character outside the set the OCR reads
reliably (a-z, acute/grave vowels, and the three marks the OCR stage restores), when its
OCR confidence is low, or when a headword breaks the alphabetical order of the list.
"""
import json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "raw", "bartoli_1906_wortverzeichnis_ocr.jsonl")
OUT = os.path.join(HERE, "bartoli-1906-vegliote.tsv")
OUT_D = os.path.join(HERE, "bartoli-1906-vegliote.doubtful.tsv")
FIRST_PAGE, FIRST_PAGE_Y = 537, 2450      # the list starts under the heading in mid-page
MIN_CONF = 60

LABELS = {"fem", "masc", "plur", "pl", "sing", "sg", "präp", "adv", "conj", "conjunction", "ptc", "part", "inf",
          "imper", "imperat", "pres", "präs", "perf", "fut", "imperf", "impf", "mit", "d", "artik", "id", "idem",
          "vgl", "cfr", "cf", "s", "u", "ibid", "etc", "ecc", "ff", "f", "bis", "mehrm", "passim", "b", "ive",
          "wo", "neben", "auch", "nur", "sonst", "dazu", "aber", "bei", "aus", "von", "zu", "in", "subst", "adj",
          "pron", "interj", "zahlw", "num", "konj", "pers", "ger", "gerund", "cond", "kond", "refl", "dim", "n"}
POS = {"präp": "prep", "conj": "conj", "conjunction": "conj", "konj": "conj", "adv": "adv", "fem": "noun",
       "masc": "noun", "subst": "noun", "adj": "adj", "pron": "pron", "interj": "other", "zahlw": "num", "num": "num"}
OK_COMB = {"́", "̀", "̯", "̣", "͡"}


def norm_key(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if "a" <= c <= "z")


def clean_charset(form):
    """a-z; acute/grave on vowels; breve below on i/u; dot below and tie on vowels"""
    prev = ""
    for ch in unicodedata.normalize("NFD", form):
        if "a" <= ch <= "z" or ch == " ":
            prev = ch
        elif ch in OK_COMB and prev in "aeiou" and not (ch == "\u032f" and prev not in "iu"):
            pass
        else:
            return False
    return True


def scan_ok(flag, text):
    """scan-N-vs-M from the OCR stage: N strokes seen above the x-height, M expected from the letters.
    The top of t (and of the st ligature) sometimes reaches the scan line, so allow one extra per t."""
    m = re.fullmatch(r"scan-(\d+)-vs-(\d+)", flag)
    if not m:
        return False
    n, e = int(m.group(1)), int(m.group(2))
    return e <= n <= e + text.count("t")


def load_lines():
    pages = {}
    for raw in open(SRC, encoding="utf-8"):
        d = json.loads(raw)
        pages.setdefault(d["page"], []).append(d)
    for pno in sorted(pages):
        lines = pages[pno]
        mid = lines[0]["page_w"] / 2
        halves = []
        for l in lines:
            if pno == FIRST_PAGE and l["y0"] < FIRST_PAGE_Y:
                continue
            left = [w for w in l["words"] if w["x"] < mid]
            right = [w for w in l["words"] if w["x"] >= mid]
            for col, ws in ((0, left), (1, right)):
                if ws:
                    halves.append(dict(page=pno, col=col, y=l["y0"], x=ws[0]["x"], words=ws))
        for col in (0, 1):
            cl = sorted((h for h in halves if h["col"] == col), key=lambda h: h["y"])
            if not cl:
                continue
            xs = sorted(h["x"] for h in cl)
            margin = xs[max(0, len(xs) // 10)]          # robust left margin of the column
            for h in cl:
                h["indent"] = h["x"] - margin
                yield h


def entries():
    cur = None
    for h in load_lines():
        text = " ".join(w["t"] for w in h["words"])
        if re.fullmatch(r"[\d\s.,]+", text):                          # column numbers
            continue
        if re.fullmatch(r"[A-ZÀ-Ý]\.?", text.strip()) and h["indent"] > 250:   # letter heading
            continue
        if h["indent"] < 90:
            if cur:
                yield cur
            cur = dict(page=h["page"], col=h["col"], y=h["y"], words=[], nlines=0)
        if cur is None:
            continue
        cur["nlines"] += 1
        ws = [dict(w) for w in h["words"]]
        # join a word broken at the line end
        if cur["words"] and cur["words"][-1]["t"].endswith("-") and len(cur["words"][-1]["t"]) > 1 and ws \
                and re.match(r"[^\W\d_]", ws[0]["t"]) and ws[0]["t"][:1].islower():
            prev = cur["words"][-1]
            prev["t"] = prev["t"][:-1] + ws[0]["t"]
            prev["c"] = min(prev["c"], ws[0]["c"]); prev["f"] = prev["f"] + ws[0]["f"]
            prev["i"] = max(prev["i"], ws[0]["i"])
            ws = ws[1:]
        cur["words"].extend(ws)
    if cur:
        yield cur


def kind(tok, first):
    t = tok["t"]
    core = t.strip("()[],;:.?!„“”\"'’")
    if t in ("—", "–", "-", "=", "—-"):
        return "DASH"
    if re.search(r"\d", t) or core in ("S", "B", "D") or t in ("(?)", "?"):
        return "NUM"
    if not re.search(r"[^\W\d_]", t):
        return "PUNCT"
    if first:
        return "FORM"
    dotted = "." in t[len(t.rstrip(",;:)")) - 1:len(t.rstrip(",;:)"))] or t.rstrip(",;:)").endswith(".")
    if core.lower() in LABELS and (dotted or core.lower() in ("mit", "idem", "conjunction", "ive", "wo", "oder", "und")):
        return "LABEL"
    if len(core) == 1 and dotted:                       # "m.", "d." : a word of a phrase cut short
        return "ABBR"
    if core in ("Ive", "Cubich"):
        return "LABEL"
    if tok["i"]:
        return "FORM"
    return "WORD"


def segments(words):
    """split an entry at ';' , ':' and dashes"""
    seg = []
    for w in words:
        if w["t"] in ("—", "–", "-", "—-"):
            if seg:
                yield seg
            seg = []
            continue
        seg.append(w)
        if w["t"].endswith(";") or w["t"].endswith(":"):
            yield seg
            seg = []
    if seg:
        yield seg


def parse_segment(seg, is_head):
    """-> list of groups (forms, gloss tokens, label);  forms = list of [(token, kind), ...]"""
    kinds = [kind(w, is_head and k == 0) for k, w in enumerate(seg)]
    # an upright word directly followed by a number, right after a form or its numbers,
    # is a form whose italics the shear test missed
    for k, w in enumerate(seg):
        if kinds[k] == "WORD" and k + 1 < len(seg) and kinds[k + 1] == "NUM" and k > 0 \
                and kinds[k - 1] in ("NUM", "FORM", "FORM?", "LABEL") and "(" not in w["t"]:
            kinds[k] = "FORM?"
    groups = []
    forms, cur, gloss, label = [], [], [], ""
    depth = 0
    skip_next = False
    state = "forms"

    def close():
        nonlocal forms, cur, gloss, label, state
        if cur:
            forms.append(cur)
        if forms or gloss:
            groups.append((forms, gloss, label))
        forms, cur, gloss, label, state = [], [], [], "", "forms"

    for k, w in enumerate(seg):
        kd = kinds[k]; t = w["t"]
        opens, closes = t.count("(") + t.count("["), t.count(")") + t.count("]")
        if state == "gloss":
            joiner = kd == "LABEL" and t.strip("().,").lower() in ("oder", "und")
            if kd == "WORD" or joiner or (kd in ("PUNCT", "FORM", "FORM?") and depth > 0):
                gloss.append(w)
                depth = max(0, depth + opens - closes)
                continue
            close()
        if kd == "ABBR":                               # "dona m." = phrase with an abbreviated word: not a form
            cur = []; skip_next = True
        elif kd in ("FORM", "FORM?"):
            if depth > 0 or t.startswith("(") or t.startswith("[") or skip_next:
                skip_next = skip_next and not t.endswith(",")   # forms quoted in brackets are not taken
            else:
                cur.append((w, kd))
                if t.endswith(","):
                    forms.append(cur); cur = []
        elif kd == "LABEL":
            if cur:
                forms.append(cur); cur = []
            if not label and not forms:
                label = t.strip("().,;:").lower()
            elif not label:
                label = "+" + t.strip("().,;:").lower()   # label after the first form: fem., masc., Präp.
        elif kd in ("NUM", "PUNCT"):
            skip_next = False
            if cur:
                forms.append(cur); cur = []
        elif kd == "WORD":
            skip_next = False
            if cur:
                forms.append(cur); cur = []
            if forms and depth == 0 and not t.startswith("("):
                state = "gloss"; gloss.append(w)
        depth = max(0, depth + opens - closes)
    close()
    return groups


def form_text(toks):
    return " ".join(w["t"] for w, kd in toks).strip(" ,;:.")


def gloss_text(toks):
    g = " ".join(w["t"] for w in toks)
    g = re.sub(r"\s+([,;:.)])", r"\1", g).strip()
    g = g.rstrip(",;:").strip()
    if g.count("(") > g.count(")"):
        g = g[:g.rfind("(")].strip()
    if g.endswith(".") and not g.endswith("ecc.") and not g.endswith("etc."):
        g = g[:-1]
    return g.strip(" ,;:")


def doubts(toks, text):
    why = []
    for w, kd in toks:
        why += [f for f in w["f"] if not scan_ok(f, w["t"])]
        if w["c"] < MIN_CONF:
            why.append("conf%d" % w["c"])
        if kd == "FORM?":
            why.append("italic-unsure")
    if not clean_charset(text):
        why.append("charset")
    if len(norm_key(text)) < 1:
        why.append("empty")
    return why


def main():
    ents = list(entries())
    rows, drows = [], []
    stats = dict(entries=len(ents), no_gloss=0, head_rows=0, sub_rows=0)
    heads = []
    for e in ents:
        segs = list(segments(e["words"]))
        e["out"] = []
        if not segs:
            continue
        pending = []            # forms of the head group still waiting for a gloss (gloss after a ';')
        first_group = True
        for si, seg in enumerate(segs):
            for gi, (forms, gloss, label) in enumerate(parse_segment(seg, si == 0)):
                g = gloss_text(gloss)
                is_first = first_group
                if first_group:
                    e["head"] = form_text(forms[0]) if forms else ""
                    e["pos"] = POS.get(label.lstrip("+"), "")
                    first_group = False
                has_gloss = len(re.sub(r"[^A-Za-zÀ-ÿ]", "", g)) >= 2 and not g.startswith("-")
                if not has_gloss:
                    if is_first:
                        pending = forms
                    elif pending and gi == 0 and not label and seg[0]["t"] not in ("—", "–") and si <= 2:
                        pending = pending + forms
                    else:
                        pending = [] if (label and not label.startswith("+")) else pending
                    continue
                carried = bool(pending) and not is_first and not (label and not label.startswith("+")) and si <= 2
                use = (pending if carried else []) + forms
                head_like = is_first or carried
                pending = []
                gd = ["gloss-conf"] if any(w["c"] < 50 for w in gloss) else []
                for f in use:
                    ft = form_text(f)
                    if not ft or any(w["t"].rstrip(",;:").endswith(".") for w, kd in f):
                        continue
                    e["out"].append(dict(form=ft, gloss=g, pos=e.get("pos", "") if head_like else "",
                                         why=doubts(f, ft) + gd, head=(ft == e.get("head")), sub=not head_like))
        if not e["out"]:
            stats["no_gloss"] += 1
        heads.append(e)
    # alphabetical order of headwords: a headword out of order with both neighbours is suspect
    keys = [norm_key(e.get("head", "")) for e in heads]
    for i, e in enumerate(heads):
        k = keys[i]
        if not k:
            continue
        prev = next((keys[j] for j in range(i - 1, -1, -1) if keys[j]), "")
        nxt = next((keys[j] for j in range(i + 1, len(keys)) if keys[j]), "￿")
        bad = (prev and k[:3] < prev[:3] and prev[:3] <= nxt[:3]) or (nxt != "￿" and k[:3] > nxt[:3] and prev[:3] <= nxt[:3])
        if bad:
            for r in e["out"]:
                if r["head"]:
                    r["why"].append("order")
    seen = set()
    for e in heads:
        loc = (e["page"], e["col"], e["y"], e["nlines"])
        for r in e["out"]:
            row = (r["form"], r["gloss"], "it", r["pos"])
            if r["why"]:
                drows.append(row + (",".join(sorted(set(r["why"]))), loc))
            else:
                if row in seen:
                    continue
                seen.add(row); rows.append(row + ("", loc))
                stats["sub_rows" if r["sub"] else "head_rows"] += 1
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("headword\tgloss\tgloss_lang\tpos\n")
        for r in rows:
            f.write("\t".join(r[:4]) + "\n")
    with open(OUT_D, "w", encoding="utf-8") as f:
        f.write("headword\tgloss\tgloss_lang\tpos\n")
        for r in drows:
            f.write("\t".join(r[:4]) + "\n")
    # where each row stands in the scan (PDF page, column 0/1, y of the entry's first line in the
    # 600 dpi page image, number of lines): used to check samples against the page
    with open(os.path.join(HERE, "raw", "bartoli-1906-vegliote.rows-located.tsv"), "w", encoding="utf-8") as f:
        f.write("file\theadword\tgloss\tpdf_page\tcolumn\ty\tlines\twhy\n")
        for name, rr in (("main", rows), ("doubtful", drows)):
            for r in rr:
                f.write("%s\t%s\t%s\t%d\t%d\t%d\t%d\t%s\n" % ((name, r[0], r[1]) + r[5] + (r[4],)))
    stats.update(rows=len(rows), doubtful=len(drows))
    print(stats, file=sys.stderr)


if __name__ == "__main__":
    main()
