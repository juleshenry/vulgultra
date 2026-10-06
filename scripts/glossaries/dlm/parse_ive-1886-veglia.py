#!/usr/bin/env python3
"""Ive 1886, L'antico dialetto di Veglia, § VIII b "Indice lessicale" (pp. 168-186)
   raw/ive_1886_indice_lessicale_ocr.jsonl  ->  ive-1886-veglia.tsv, ive-1886-veglia.doubtful.tsv

The JSONL is our own OCR of the page images (ocr_ive-1886-veglia.py): one object per printed
line; each word has t = text, i = 1 if italic, c = OCR confidence, f = flags, x/x2 = edges.

Shape of an entry (first line indented, the rest flush left; ends with a full stop):

    acáid 6, 57, 62, aceto.
    agniál, pl. gniál, 9, 24, agnello.
    chenúr kenúr (prtc. kenút) 1, 57, cenare.
    a lic a lics, cfr. 3, a lato, vicino.
    che che 79, pron. rel. interr. e congiunz., che; cfr. que.
    aláin 126-127.                                  (no gloss: not written)

  head   = the Vegliote form or forms before the first number / "p." / bracket / label.
           Ive prints forms from Cubich's manuscripts letter-spaced upright and the others
           in italics; where the type changes inside the head, a new variant begins.
  refs   = numbers of the paragraphs of the phonetic survey, italic numbers = lines of the
           texts, "p. 117" = page of the vocabulary
  gloss  = what follows the last reference, up to ";" or the final full stop (Italian)

Rows: each head variant with the entry's gloss.  Forms given inside brackets or after
"pl.", "f.", "prtc." (inflected forms without a gloss of their own) are not written.
A form goes to the .doubtful.tsv file when it holds a character outside a-z + acute/grave
vowels, when the OCR confidence of the form or of the gloss is low, when a "d" in it looks
like a misread accented vowel, or when a headword breaks the alphabetical order.
"""
import json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "raw", "ive_1886_indice_lessicale_ocr.jsonl")
OUT = os.path.join(HERE, "ive-1886-veglia.tsv")
OUT_D = os.path.join(HERE, "ive-1886-veglia.doubtful.tsv")
MIN_CONF = 60

LABEL = {"pl", "plur", "plurale", "sng", "sing", "f", "m", "fem", "masc", "cfr", "v", "s", "p", "n", "prtc", "partic",
         "part", "pres", "prs", "imperf", "prf", "perf", "fut", "inf", "imper", "cong", "congiunz", "pron", "rel",
         "interr", "interrog", "prep", "avv", "agg", "sost", "num", "art", "indecl", "ib", "ibid", "ecc", "sg",
         "lett", "nl", "ni", "pers", "poss", "dim", "interjez", "interj", "determ", "indeterm", "neutr", "srb", "slov",
         "vnt", "venez", "it", "ital", "friul", "rum", "istr", "lat", "ted", "cr", "e", "ed", "o", "con", "senza"}
POS = {"pron": "pron", "prep": "prep", "avv": "adv", "agg": "adj", "sost": "noun", "num": "num", "cong": "conj",
       "congiunz": "conj", "interjez": "other", "interj": "other", "art": "other", "m": "noun", "f": "noun"}
VOWEL_ACC = {"́", "̀"}


def norm_key(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if "a" <= c <= "z")


def clean_charset(form):
    prev = ""
    for ch in unicodedata.normalize("NFD", form):
        if "a" <= ch <= "z" or ch == " ":
            prev = ch
        elif ch in VOWEL_ACC and prev in "aeiou":
            pass
        else:
            return False
    return True


def entries():
    pages = {}
    for raw in open(SRC, encoding="utf-8"):
        d = json.loads(raw)
        pages.setdefault(d["page"], []).append(d)
    cur = None
    stop = False
    for pno in sorted(pages):
        lines = pages[pno]
        mid = lines[0]["page_w"] / 2
        # the centre rule: use the widest empty band near the middle, taken from word positions
        xs_right = sorted(w["x"] for l in lines for w in l["words"] if abs(w["x"] - mid) < 0.12 * lines[0]["page_w"])
        halves = []
        for l in lines:
            text = " ".join(w["t"] for w in l["words"])
            # split a line at the largest gap between words if it straddles the middle
            ws = l["words"]
            cut = None
            if ws and ws[0]["x"] < mid < ws[-1]["x2"]:
                gaps = [(ws[k + 1]["x"] - ws[k]["x2"], k) for k in range(len(ws) - 1)
                        if ws[k]["x2"] < mid + 0.08 * l["page_w"] and ws[k + 1]["x"] > mid - 0.08 * l["page_w"]]
                if gaps:
                    g, k = max(gaps)
                    if g > 0.02 * l["page_w"]:
                        cut = k + 1
            parts = [ws[:cut], ws[cut:]] if cut else [ws]
            for part in parts:
                if part:
                    col = 0 if (part[0]["x"] + part[-1]["x2"]) / 2 < mid else 1
                    halves.append(dict(page=pno, col=col, y=l["y0"], x=part[0]["x"], words=part))
        for col in (0, 1):
            cl = sorted((h for h in halves if h["col"] == col), key=lambda h: h["y"])
            cl = [h for h in cl if not re.fullmatch(r"[\d\s.,]+", " ".join(w["t"] for w in h["words"]))]
            cl = [h for h in cl if "Indice lessicale" not in " ".join(w["t"] for w in h["words"])
                  and "dial. veglioto" not in " ".join(w["t"] for w in h["words"])]
            if not cl:
                continue
            xs = sorted(h["x"] for h in cl)
            margin = xs[max(0, len(xs) // 12)]
            for h in cl:
                text = " ".join(w["t"] for w in h["words"])
                if re.search(r"C[1Il]MELJ|Cimelj rumeni|ultimo riordinamento", text, re.I):
                    stop = True
                if stop:
                    break
                indent = h["x"] - margin
                if indent > 0.012 * lines[0]["page_w"]:          # first line of an entry is indented
                    if cur:
                        yield cur
                    cur = dict(page=pno, words=[])
                if cur is None:
                    continue
                ws = [dict(w) for w in h["words"]]
                if cur["words"] and re.search(r"[^\W\d_][-¬]$", cur["words"][-1]["t"]) and ws and re.match(r"[^\W\d_]", ws[0]["t"]):
                    prev = cur["words"][-1]
                    prev["t"] = prev["t"][:-1] + ws[0]["t"]
                    prev["c"] = min(prev["c"], ws[0]["c"]); prev["f"] = prev["f"] + ws[0]["f"]
                    ws = ws[1:]
                cur["words"].extend(ws)
            if stop:
                break
        if stop:
            break
    if cur:
        yield cur


def is_num(t):
    return bool(re.search(r"\d", t))


def core(t):
    return t.strip("()[],;:.?!'‘’\"")


def is_label(t):
    c = core(t).lower()
    return c in LABEL and (t.rstrip(",;:)").endswith(".") or c in ("e", "ed", "o", "con", "senza", "plurale"))


def parse(e):
    ws = e["words"]
    # ---- head: tokens up to the first number, label, bracket or comma
    head = []
    k = 0
    while k < len(ws):
        t = ws[k]["t"]
        if is_num(t) or is_label(t) or t.startswith("(") or t.startswith("[") or not re.search(r"[^\W\d_]", t):
            break
        head.append(ws[k]); k += 1
        if t.endswith(",") or t.endswith(";") or t.endswith(":"):
            break
    if not head:
        return None
    # variants: split where italic/upright changes
    variants, cur = [], [head[0]]
    for w in head[1:]:
        if w["i"] != cur[-1]["i"]:
            variants.append(cur); cur = [w]
        else:
            cur.append(w)
    variants.append(cur)
    rest = ws[k:]
    # ---- gloss: after the last reference, up to ';' or the final '.'
    last = -1
    depth = 0
    pos = ""
    for j, w in enumerate(rest):
        t = w["t"]
        if depth == 0 and (is_num(t) or is_label(t)):
            last = j
            c = core(t).lower()
            if not pos and c in POS and not is_num(t):
                pos = POS[c]
        depth = max(0, depth + t.count("(") - t.count(")"))
        if depth > 0 or t.endswith(")"):
            last = max(last, j)
        if depth == 0 and t.endswith(";"):
            break
    gl = []
    for w in rest[last + 1:]:
        gl.append(w)
        if w["t"].endswith(";") or w["t"].endswith("."):
            break
    # a head that already ended the entry: "acqua p. 120, v. jácqua."  -> cross-reference, no gloss
    if any(core(w["t"]).lower() in ("v", "cfr") and w["t"].endswith(".") for w in rest[max(0, last - 1):last + 1]):
        gl = []
    g = " ".join(w["t"] for w in gl)
    g = re.sub(r"\s+([,;:.)])", r"\1", g).strip().rstrip(";.,:").strip()
    return variants, g, gl, pos


def main():
    rows, drows = [], []
    ents = list(entries())
    parsed = []
    stats = dict(entries=len(ents), no_gloss=0)
    for e in ents:
        r = parse(e)
        if not r:
            continue
        variants, g, gl, pos = r
        e["head"] = " ".join(w["t"] for w in variants[0]).strip(" ,;:.")
        e["rows"] = []
        if len(re.sub(r"[^A-Za-zÀ-ÿ]", "", g)) < 2:
            stats["no_gloss"] += 1
            parsed.append(e); continue
        gd = ["gloss-conf"] if any(w["c"] < 50 for w in gl) else []
        for v in variants:
            ft = " ".join(w["t"] for w in v).strip(" ,;:.")
            why = list(gd)
            for w in v:
                why += w["f"]
                if w["c"] < MIN_CONF:
                    why.append("conf%d" % w["c"])
            if not clean_charset(ft):
                why.append("charset")
            if not norm_key(ft):
                continue
            e["rows"].append(dict(form=ft, gloss=g, pos=pos, why=why, head=v is variants[0]))
        parsed.append(e)
    keys = [norm_key(e.get("head", "")) for e in parsed]
    for i, e in enumerate(parsed):
        k = keys[i]
        if not k:
            continue
        prev = next((keys[j] for j in range(i - 1, -1, -1) if keys[j]), "")
        nxt = next((keys[j] for j in range(i + 1, len(keys)) if keys[j]), "￿")
        if (prev and k[:2] < prev[:2] and prev[:2] <= nxt[:2]) or (nxt != "￿" and k[:2] > nxt[:2] and prev[:2] <= nxt[:2]):
            for r in e["rows"]:
                if r["head"]:
                    r["why"].append("order")
    seen = set()
    for e in parsed:
        for r in e["rows"]:
            row = (r["form"], r["gloss"], "it", r["pos"])
            if r["why"]:
                drows.append(row + (",".join(sorted(set(r["why"]))), e["page"]))
            elif row not in seen:
                seen.add(row); rows.append(row + (e["page"],))
    for path, rr in ((OUT, rows), (OUT_D, drows)):
        with open(path, "w", encoding="utf-8") as f:
            f.write("headword\tgloss\tgloss_lang\tpos\n")
            for r in rr:
                f.write("\t".join(r[:4]) + "\n")
    with open(os.path.join(HERE, "raw", "ive-1886-veglia.rows-with-pages.tsv"), "w", encoding="utf-8") as f:
        f.write("file\theadword\tgloss\tpage\twhy\n")
        for r in rows:
            f.write("main\t%s\t%s\t%d\t\n" % (r[0], r[1], r[4]))
        for r in drows:
            f.write("doubtful\t%s\t%s\t%d\t%s\n" % (r[0], r[1], r[5], r[4]))
    stats.update(rows=len(rows), doubtful=len(drows))
    print(stats, file=sys.stderr)


if __name__ == "__main__":
    main()
