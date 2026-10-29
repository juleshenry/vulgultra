#!/usr/bin/env python3
"""Re-OCR of Dalla Zonca, Vocabolario dignanese-italiano (1978) from the
archive.org page images, with a per-word stroke-thickness figure so that the
parser can tell bold (headword) type from roman/italic (gloss) type.

Not needed to rebuild the TSV: its output, raw/dallazonca_1978_reocr_ita_words.tsv.gz,
is kept in raw/ and parse_dallazonca-1978.py reads that. Kept so the OCR step
is reproducible.

Needs: tesseract 5 with the tessdata_best `ita` model (pass its directory with
--tessdata), python3 with numpy and opencv (cv2).

  python3 ocr_dallazonca.py --tessdata /path/to/tessdata_best --work /tmp/dz [--jobs 2]

Only the dictionary proper is read: leaves 32-335 = printed pp. 1-304. The
editor's front matter (leaves 0-31) and Debeljuh's own Supplemento, appendix
and index (leaves 336-395) are left out on purpose: they are not Dalla Zonca's
text.

Input : raw/dallazonca_1978_RovignoAtti-02_jp2.zip  (archive.org RovignoAtti-02-1978)
Output: raw/dallazonca_1978_reocr_ita_words.tsv.gz
        columns: page  block  par  line  word  left  top  width  height  conf  dtmean  er2  sw  text
        page = 0-based leaf number of the scan (printed page = leaf - 31 in the
        dictionary proper). Three stroke-thickness figures for the ink inside
        the word box, all higher for bold type: dtmean = mean of the distance
        transform over ink pixels (roman ~1.75, bold ~2.2 at this scan's
        resolution, 1918x3038; it drifts from page to page, so the parser
        clusters per page); er2 = share of ink surviving two 3x3 erosions;
        sw = 2*area/perimeter.
"""
import argparse, csv, gzip, os, subprocess, sys, zipfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ZIP = os.path.join(HERE, "raw", "dallazonca_1978_RovignoAtti-02_jp2.zip")
OUT = os.path.join(HERE, "raw", "dallazonca_1978_reocr_ita_words.tsv.gz")


def ocr_page(args):
    jp2, base, tessdata = args
    if os.path.exists(base + ".tsv") and os.path.getsize(base + ".tsv") > 0:
        return
    env = dict(os.environ, OMP_THREAD_LIMIT="1")
    subprocess.run(["tesseract", jp2, base, "--tessdata-dir", tessdata, "-l", "ita",
                    "--psm", "1", "-c", "tessedit_create_tsv=1"],
                   env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tessdata", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--first", type=int, default=32, help="first leaf (32 = printed p. 1)")
    ap.add_argument("--last", type=int, default=335, help="last leaf (335 = printed p. 304)")
    a = ap.parse_args()
    import numpy as np, cv2
    K3 = np.ones((3, 3), np.uint8)
    os.makedirs(a.work, exist_ok=True)
    with zipfile.ZipFile(ZIP) as z:
        names = sorted(n for n in z.namelist() if n.endswith(".jp2")
                       and a.first <= int(n[-8:-4]) <= a.last)
        z.extractall(a.work, names)
    jobs = []
    for n in names:
        jp2 = os.path.join(a.work, n)
        jobs.append((jp2, jp2[:-4], a.tessdata))
    with ThreadPoolExecutor(a.jobs) as ex:
        list(ex.map(ocr_page, jobs))
    with gzip.open(OUT, "wt", encoding="utf-8", newline="") as fo:
        fo.write("page\tblock\tpar\tline\tword\tleft\ttop\twidth\theight\tconf\tdtmean\ter2\tsw\ttext\n")
        for jp2, base, _ in jobs:
            page = int(base[-4:])
            if not os.path.exists(base + ".tsv"):
                continue
            img = cv2.imread(jp2, cv2.IMREAD_GRAYSCALE)
            _, bw = cv2.threshold(img, 0, 1, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            with open(base + ".tsv", encoding="utf-8") as f:
                for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                    if r["level"] != "5" or not r["text"].strip():
                        continue
                    x, y, w, h = int(r["left"]), int(r["top"]), int(r["width"]), int(r["height"])
                    sub = np.ascontiguousarray(bw[y:y + h, x:x + w])
                    dtmean = er2 = sw = 0.0
                    if sub.size and sub.sum():
                        area = float(sub.sum())
                        dt = cv2.distanceTransform(sub, cv2.DIST_L2, 5)
                        dtmean = float(dt[dt > 0].mean())
                        er2 = float(cv2.erode(sub, K3, iterations=2).sum()) / area
                        cnts, _ = cv2.findContours(sub, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
                        per = sum(len(c) for c in cnts)
                        sw = 2 * area / per if per else 0.0
                    fo.write("\t".join([str(page), r["block_num"], r["par_num"], r["line_num"],
                                        r["word_num"], str(x), str(y), str(w), str(h),
                                        r["conf"], "%.3f" % dtmean, "%.3f" % er2, "%.2f" % sw,
                                        r["text"]]) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
