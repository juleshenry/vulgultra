#!/usr/bin/env python3
"""OCR stage for Bartoli 1906, "Anhang: Vegliotisches Wortverzeichnis" (vol. II, cols. 169-240).

Input : raw/bartoli_1906_das_dalmatische.pdf  (archive.org item `das-dalmatische`, Google scan,
        600 dpi bitonal page images; the word list is on the odd PDF pages 537-607).
Output: raw/bartoli_1906_wortverzeichnis_ocr.jsonl  (one JSON object per printed line)

Not stdlib: needs `pdfimages` (poppler), `tesseract` 5 with the tessdata_best `script/Latin`
model (pass its directory with --tessdata), and the python packages cv2 + numpy.
The TSV is made from the JSONL by parse_bartoli-1906-vegliote.py (stdlib only).

Why two OCR passes.  Bartoli prints three things no stock OCR model reads:
  * i/u with an inverted breve below (non-syllabic i, u)        -> written here  i + U+032F, u + U+032F
  * o/e/a with a dot below (closed vowel)                        -> letter + U+0323
  * two vowels under a tie, usually with one acute over the tie  -> first vowel (+ U+0301) + U+0361 + second vowel
Pass 1 finds the text lines.  The marks are then located in the page image by shape
(ink below the baseline that is closed on top and open below = breve; a small round
blob under a letter = dot; a long horizontal stroke above the x-height = tie), blanked,
and the cleaned page is read again (pass 2).  Each blanked mark is put back on the
pass-2 letter that stood under/over it.  Words get flags when a mark lands on an
implausible letter, when the strokes above the x-height or the blobs below the baseline
do not match the letters read, when a "d" looks like an accented vowel, or when an "l"
carries a hook (palatal l); the parser sends flagged forms to the .doubtful.tsv file.
Italic (= Vegliote forms) versus upright (= Italian gloss, German labels, numbers) is
decided per word by a shear test on the image.
"""
import argparse, hashlib, json, os, re, subprocess, sys, tempfile, unicodedata
from html.parser import HTMLParser
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(HERE, "raw", "bartoli_1906_das_dalmatische.pdf")
OUT = os.path.join(HERE, "raw", "bartoli_1906_wortverzeichnis_ocr.jsonl")
PAGES = list(range(537, 608, 2))          # odd PDF pages; even pages are blank versos

ARC, DOTB, TIE, ACUTE = "̯", "̣", "͡", "́"
ALPHA = re.compile(r"[^\W\d_]")


# ---------------------------------------------------------------- hOCR
class HOCR(HTMLParser):
    LINE = ("ocr_line", "ocr_header", "ocr_textfloat", "ocr_caption")

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines, self.line, self.word, self.char, self.stack = [], None, None, None, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs); cls = a.get("class", ""); t = a.get("title", "")
        self.stack.append(cls)
        if cls in self.LINE:
            bb = [int(v) for v in re.search(r"bbox (\d+) (\d+) (\d+) (\d+)", t).groups()]
            m = re.search(r"baseline (-?[\d.]+) (-?[\d.]+)", t)
            g = lambda k: (float(re.search(k + r" ([\d.]+)", t).group(1)) if re.search(k + r" ([\d.]+)", t) else None)
            self.line = dict(bbox=bb, baseline=(float(m.group(1)), float(m.group(2))) if m else (0.0, 0.0),
                             x_size=g("x_size"), x_asc=g("x_ascenders"), x_desc=g("x_descenders"), words=[])
            self.lines.append(self.line)
        elif cls == "ocrx_word" and self.line is not None:
            bb = [int(v) for v in re.search(r"bbox (\d+) (\d+) (\d+) (\d+)", t).groups()]
            c = re.search(r"x_wconf (\d+)", t)
            self.word = dict(bbox=bb, conf=int(c.group(1)) if c else -1, chars=[])
            self.line["words"].append(self.word)
        elif cls == "ocrx_cinfo" and self.word is not None:
            bb = [int(v) for v in re.search(r"x_bboxes (\d+) (\d+) (\d+) (\d+)", t).groups()]
            self.char = dict(bbox=bb, text="")
            self.word["chars"].append(self.char)

    def handle_endtag(self, tag):
        cls = self.stack.pop() if self.stack else ""
        if cls == "ocrx_cinfo":
            self.char = None
        elif cls == "ocrx_word":
            self.word = None
        elif cls in self.LINE:
            self.line = None

    def handle_data(self, data):
        if self.char is not None:
            self.char["text"] += data


def read_hocr(path):
    p = HOCR(); p.feed(open(path, encoding="utf-8").read())
    lines = [l for l in p.lines if l["words"]]
    for l in lines:
        for w in l["words"]:
            w["text"] = "".join(c["text"] for c in w["chars"])
        l["words"] = [w for w in l["words"] if w["text"].strip()]
    return [l for l in lines if l["words"]]


def ocr(png, tessdata, cache, key):
    """tesseract -> hOCR with character boxes; `cache` (optional dir) keeps the hOCR while developing"""
    target = os.path.join(cache, key + ".hocr") if cache else png[:-4] + ".hocr"
    if not (cache and os.path.exists(target)):
        env = dict(os.environ, OMP_THREAD_LIMIT="1")
        subprocess.run(["tesseract", png, png[:-4], "--tessdata-dir", tessdata, "-l", "Latin", "--psm", "3", "--dpi", "600",
                        "-c", "tessedit_create_hocr=1", "-c", "hocr_char_boxes=1"],
                       check=True, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if cache:
            os.replace(png[:-4] + ".hocr", target)
    return read_hocr(target)


# ---------------------------------------------------------------- geometry
def xheight(line, page_xh):
    try:
        xh = line["x_size"] - line["x_asc"] - line["x_desc"]
    except TypeError:
        return page_xh
    return xh if 33 <= xh <= 50 else page_xh


def base_y(line, x):
    x0, y0, x1, y1 = line["bbox"]; a, b = line["baseline"]
    return y1 + b + a * (x - x0)


def runs(row):
    """(start, end) ink runs of a 0/1 row"""
    out = []; s = None
    for i, v in enumerate(row):
        if v and s is None:
            s = i
        elif not v and s is not None:
            out.append((s, i)); s = None
    if s is not None:
        out.append((s, len(row)))
    return out


def is_italic(bw, line, w, xh):
    """shear test: an italic word gives sharper column sums when sheared back by 4-20 degrees"""
    x0, y0, x1, y1 = w["bbox"]
    by = int(round(base_y(line, (x0 + x1) / 2)))
    ya, yb = max(0, int(by - 1.6 * xh)), by
    pad = 40
    sub = bw[ya:yb, max(0, x0 - pad):x1 + pad].astype(np.float32)
    if sub.size == 0 or sub.sum() < 30:
        return False, 1.0
    h = sub.shape[0]; res = {}
    for deg in (0, 4, 8, 12, 16, 20):
        t = float(np.tan(np.radians(deg)))
        M = np.float32([[1, t, -t * h], [0, 1, 0]])
        sh = cv2.warpAffine(sub, M, (sub.shape[1], h), flags=cv2.INTER_NEAREST)
        res[deg] = float((sh.sum(axis=0) ** 2).sum())
    best = max(res, key=res.get)
    ratio = res[0] / res[best] if res[best] else 1.0
    return (best >= 8 or (best == 4 and ratio <= 0.993)), round(ratio, 3)


def find_marks(bw, line, w, xh, want_tie=True):
    """Marks in one word: inverted breve below ("arc"), dot below ("dot"), tie above two vowels ("tie").
    Each mark carries its x-range and the box to blank before the second OCR pass."""
    x0, y0, x1, y1 = w["bbox"]
    X0, X1 = max(0, x0 - 3), min(bw.shape[1], x1 + 3)
    by = int(round(base_y(line, (x0 + x1) / 2)))
    marks = []
    ya, yb = by + int(round(0.06 * xh)), by + int(round(0.66 * xh))
    band = np.ascontiguousarray(bw[ya:yb, X0:X1])
    if band.size:
        n, lab, st, _ = cv2.connectedComponentsWithStats(band, 8)
        for i in range(1, n):
            bx, byy, bwid, bh, area = [int(v) for v in st[i]]
            if area < 60 or byy > 0.3 * xh:
                continue
            blob = (lab[byy:byy + bh, bx:bx + bwid] == i).astype(np.uint8)
            kind = None
            # arc: closed on top, open at the bottom (two legs; one may be shorter)
            if 17 <= bwid <= 36 and 0.25 * xh <= bh <= 0.5 * xh and byy <= 2:
                gap = None
                for r in range(bh):
                    rr = runs(blob[r])
                    if len(rr) >= 2 and rr[1][0] - rr[0][1] >= 4 and r >= 0.4 * bh:
                        gap = (r, (rr[0][1] + rr[1][0]) // 2)
                if gap is not None:
                    r0, gc = gap
                    closed_top = bool(blob[:max(1, int(0.3 * bh)), gc].any())
                    open_bottom = not blob[r0:, gc].any()
                    rt = int(0.3 * bh)
                    wide_top = len(runs(blob[rt])) == 1 and blob[rt].sum() >= 0.55 * bwid
                    if closed_top and open_bottom and wide_top:
                        kind = "arc"
            # dot: small, compact, round, with a letter body right above it
            if kind is None and 9 <= bwid <= 21 and 8 <= bh <= 17 and abs(bwid - bh) <= 6 and area >= 0.72 * bwid * bh:
                body = bw[by - int(round(0.9 * xh)):by - int(round(0.15 * xh)), X0 + bx:X0 + bx + bwid]
                if body.sum() >= 40:
                    kind = "dot"
            if kind:
                marks.append(dict(kind=kind, x0=X0 + bx, x1=X0 + bx + bwid,
                                  erase=(by + int(round(0.03 * xh)), ya + byy + bh + 1, X0 + bx - 1, X0 + bx + bwid + 1)))
    if want_tie:
        ta, tb = by - int(round(1.42 * xh)), by - int(round(1.12 * xh))
        band = bw[ta:tb, X0:X1]
        best = None
        for r in range(band.shape[0]):
            for s_, e_ in runs(band[r]):
                if e_ - s_ >= 0.85 * xh and (best is None or e_ - s_ > best[1] - best[0]):
                    best = (s_, e_)
        if best is not None:
            tx0, tx1 = X0 + best[0], X0 + best[1]
            hi = bw[by - int(round(1.95 * xh)):by - int(round(1.66 * xh)), tx0:tx1]
            marks.append(dict(kind="tie", x0=tx0, x1=tx1, acute=bool(hi.sum() >= 20),
                              erase=(by - int(round(1.98 * xh)), by - int(round(1.08 * xh)), tx0 - 3, tx1 + 3)))
    return marks


DESC = set("gjpqyfçşţ,;()[]ǧ")
def sub_blobs(bw, line, w, xh):
    """number of ink blobs hanging below the baseline (descenders, comma tails, unread marks)"""
    x0, y0, x1, y1 = w["bbox"]
    by = int(round(base_y(line, (x0 + x1) / 2)))
    ya, yb = by + int(round(0.06 * xh)), by + int(round(0.66 * xh))
    band = np.ascontiguousarray(bw[ya:yb, max(0, x0 - 3):x1 + 3])
    if not band.size:
        return 0
    n, lab, st, _ = cv2.connectedComponentsWithStats(band, 8)
    return len([1 for i in range(1, n) if st[i][4] >= 60 and st[i][1] <= 0.3 * xh])


def scan_above(bw, line, w, xh):
    """ink runs on a scan line 1.38 x-heights above the baseline: one per ascender, dot of i/j, accent"""
    x0, y0, x1, y1 = w["bbox"]
    by = int(round(base_y(line, (x0 + x1) / 2)))
    r = by - int(round(1.38 * xh))
    row = bw[r - 1:r + 2, x0:x1 + 6].max(axis=0)
    return len([1 for s_, e_ in runs(row) if e_ - s_ >= 3])


ASC = set("bdfhklſ")
def expected_scan(text):
    k = 0
    for ch in text:
        d = unicodedata.normalize("NFD", ch)
        base, comb = d[0], [c for c in d[1:] if unicodedata.combining(c) == 230]
        if base in ASC or base.isupper() or base.isdigit() or base in "()[]?!":
            k += 1
        if comb:
            k += 2 if "̈" in comb else 1
        elif base in "ij":
            k += 1
    return k


def stroke_profile(bw, line, c, xh, rels, left=6, right=10):
    """(runs, ink width) of the strokes above the x-height around one character, at given heights"""
    x0, y0, x1, y1 = c["bbox"]
    by = int(round(base_y(line, (x0 + x1) / 2)))
    out = []
    for rel in rels:
        r = by + int(round(rel * xh))
        rr = runs(bw[r - 1:r + 2, max(0, x0 - left):x1 + right].max(axis=0))
        out.append((len(rr), sum(e_ - s_ for s_, e_ in rr)))
    return out


def d_is_stem(bw, line, c, xh):
    """A real italic d has an unbroken stem with a wide head (>=16 px at 1.5 x-heights).
    An acute or grave accent misread as the stem of d is short and thin at the top."""
    prof = stroke_profile(bw, line, c, xh, (-1.5, -1.4, -1.3, -1.2, -1.1))
    return all(n >= 1 for n, wd in prof) and prof[0][1] >= 16


def l_has_hook(bw, line, c, xh):
    """Bartoli's palatal l carries a small hook at the top right of the stem: two strokes instead of one"""
    prof = stroke_profile(bw, line, c, xh, (-1.34, -1.26), left=8, right=14)
    return any(n >= 2 for n, wd in prof)


# ---------------------------------------------------------------- page
def process_page(pno, tessdata, tmp, cache=None):
    subprocess.run(["pdfimages", "-f", str(pno), "-l", str(pno), "-png", PDF, os.path.join(tmp, f"p{pno}")], check=True)
    png = os.path.join(tmp, f"p{pno}-000.png")
    gray = cv2.imread(png, cv2.IMREAD_GRAYSCALE)
    bw = (gray < 128).astype(np.uint8)
    lines1 = ocr(png, tessdata, cache, f"p{pno}-pass1")
    xhs = [l["x_size"] - l["x_asc"] - l["x_desc"] for l in lines1
           if l["x_size"] and l["x_asc"] is not None and l["x_desc"] is not None]
    xhs = [v for v in xhs if 33 <= v <= 50]
    page_xh = float(np.median(xhs)) if xhs else 41.0
    clean = gray.copy()
    marks = []
    for l in lines1:
        xh = xheight(l, page_xh)
        for k, w in enumerate(l["words"]):
            if not ALPHA.search(w["text"]) or re.search(r"\d", w["text"]):
                continue
            ital, _ = is_italic(bw, l, w, xh)
            for m in find_marks(bw, l, w, xh, want_tie=(ital or k == 0)):
                m["by"] = int(round(base_y(l, (m["x0"] + m["x1"]) / 2)))
                marks.append(m)
                ya, yb, xa, xb = m["erase"]
                clean[max(0, ya):yb, max(0, xa):xb] = 255
    cpng = os.path.join(tmp, f"p{pno}-clean.png")
    cv2.imwrite(cpng, clean)
    key = hashlib.sha1(clean.tobytes()).hexdigest()[:12]
    lines2 = ocr(cpng, tessdata, cache, f"p{pno}-pass2-{key}")
    cbw = (clean < 128).astype(np.uint8)
    for l in lines2:
        for w in l["words"]:
            w["marks"] = []; w["flags"] = []
    for m in marks:                                  # which pass-2 word does each mark belong to
        cx = (m["x0"] + m["x1"]) / 2
        cand = None
        for l in lines2:
            x0, y0, x1, y1 = l["bbox"]
            if not (y0 - 25 <= m["by"] <= y1 + 25):
                continue
            for w in l["words"]:
                if w["bbox"][0] - 4 <= cx <= w["bbox"][2] + 4 and abs(base_y(l, cx) - m["by"]) <= 18:
                    cand = w
        if cand is None:                             # never drop a mark silently: flag the nearest word
            best = None
            for l in lines2:
                for w in l["words"]:
                    d = abs((w["bbox"][0] + w["bbox"][2]) / 2 - cx) + 4 * abs(base_y(l, cx) - m["by"])
                    if best is None or d < best[0]:
                        best = (d, w)
            if best is not None:
                best[1]["flags"].append("mark-unplaced")
        else:
            cand["marks"].append(m)
    out = []
    for l in lines2:
        xh = xheight(l, page_xh)
        toks = []
        for k, w in enumerate(l["words"]):
            ital, ratio = is_italic(bw, l, w, xh)
            chars = [dict(c) for c in w["chars"]]
            alpha = bool(ALPHA.search(w["text"])) and not re.search(r"\d", w["text"])
            for m in sorted(w["marks"], key=lambda m: m["x0"]):
                def overlap(c):
                    return max(0, min(c["bbox"][2], m["x1"]) - max(c["bbox"][0], m["x0"]))
                if not chars:
                    w["flags"].append("mark-unplaced"); continue
                if m["kind"] in ("arc", "dot"):
                    c = max(chars, key=overlap)
                    base = unicodedata.normalize("NFD", c["text"])[:1].lower()
                    ok = (base in "iu") if m["kind"] == "arc" else (base in "aeiou")
                    if overlap(c) <= 0 or not ok:
                        w["flags"].append(m["kind"] + "-on-" + (c["text"] or "?"))
                    c["text"] += ARC if m["kind"] == "arc" else DOTB
                else:
                    under = [c for c in chars if overlap(c) >= 0.35 * (c["bbox"][2] - c["bbox"][0])]
                    if len(under) != 2 or any(unicodedata.normalize("NFD", c["text"])[:1].lower() not in "aeiou" for c in under):
                        w["flags"].append("tie-over-" + "".join(c["text"] for c in under))
                    if under:
                        t = under[0]["text"]
                        if m.get("acute") and not any(unicodedata.combining(ch) == 230 for ch in unicodedata.normalize("NFD", t)):
                            t += ACUTE
                        under[0]["text"] = t + TIE
            text = unicodedata.normalize("NFC", "".join(c["text"] for c in chars))
            if alpha and (ital or k == 0):
                plain = "".join(c["text"] for c in w["chars"])
                na, ne = scan_above(cbw, l, w, xh), expected_scan(plain)
                if na != ne:
                    w["flags"].append(f"scan-{na}-vs-{ne}")
                nb, nd = sub_blobs(cbw, l, w, xh), len([ch for ch in plain if ch in DESC])
                if nb != nd:
                    w["flags"].append(f"sub-{nb}-vs-{nd}")
                for c in w["chars"]:
                    if c["text"] == "d" and not d_is_stem(cbw, l, c, xh):
                        w["flags"].append("d-like-accent")
                    if c["text"] == "l" and l_has_hook(cbw, l, c, xh):
                        w["flags"].append("l-hook")
            toks.append(dict(t=text, i=int(ital), c=w["conf"], f=w["flags"], x=w["bbox"][0], x2=w["bbox"][2]))
        out.append(dict(page=pno, x0=l["bbox"][0], y0=l["bbox"][1], x1=l["bbox"][2], y1=l["bbox"][3], words=toks))
    return out, gray.shape


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tessdata", required=True, help="directory holding Latin.traineddata (tessdata_best/script)")
    ap.add_argument("--pages", default="", help="comma list, default = all word-list pages")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--cache", default="", help="optional directory for cached hOCR while developing")
    a = ap.parse_args()
    pages = [int(p) for p in a.pages.split(",")] if a.pages else PAGES
    with tempfile.TemporaryDirectory() as tmp, open(a.out, "w", encoding="utf-8") as fo:
        for p in pages:
            lines, shape = process_page(p, a.tessdata, tmp, a.cache or None)
            for l in lines:
                l["page_w"], l["page_h"] = shape[1], shape[0]
                fo.write(json.dumps(l, ensure_ascii=False) + "\n")
            print("page", p, "lines", len(lines), file=sys.stderr); fo.flush()


if __name__ == "__main__":
    main()
