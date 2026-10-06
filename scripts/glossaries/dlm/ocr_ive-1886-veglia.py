#!/usr/bin/env python3
"""OCR stage for Ive 1886, "L'antico dialetto di Veglia", § VIII b "Indice lessicale" (pp. 168-186).

Input : raw/ive_1886_antico_dialetto_di_veglia_jp2.zip  (archive.org item `iveanticodialettodiveglia`;
        page images _0055 .. _0073 are the printed pages 168-186)
Output: raw/ive_1886_indice_lessicale_ocr.jsonl  (one JSON object per printed line:
        page, x0, y0, x1, y1, page_w, words[{t text, i italic 0/1, c confidence, f flags, x, x2}])

Not stdlib: needs tesseract 5 with the tessdata_best `script/Latin` model (--tessdata DIR) and
the python packages cv2 + numpy.  Helper functions (hOCR reader, italic shear test, the test that
tells a real "d" from an accented vowel misread as "d") are imported from
ocr_bartoli-1906-vegliote.py in the same folder.  One OCR pass is enough here: Ive's spelling has
no marks below the line.
The TSV is made from the JSONL by parse_ive-1886-veglia.py (stdlib only).
"""
import argparse, importlib.util, json, os, re, sys, tempfile, zipfile
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZIP = os.path.join(HERE, "raw", "ive_1886_antico_dialetto_di_veglia_jp2.zip")
OUT = os.path.join(HERE, "raw", "ive_1886_indice_lessicale_ocr.jsonl")
IMAGES = list(range(55, 74))            # printed page = image number + 113

spec = importlib.util.spec_from_file_location("ob", os.path.join(HERE, "ocr_bartoli-1906-vegliote.py"))
ob = importlib.util.module_from_spec(spec); spec.loader.exec_module(ob)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tessdata", required=True)
    ap.add_argument("--images", default="")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--cache", default="")
    a = ap.parse_args()
    images = [int(p) for p in a.images.split(",")] if a.images else IMAGES
    zf = zipfile.ZipFile(ZIP)
    with tempfile.TemporaryDirectory() as tmp, open(a.out, "w", encoding="utf-8") as fo:
        for n in images:
            name = "IveAnticoDialettoDiVeglia_jp2/IveAnticoDialettoDiVeglia_%04d.jp2" % n
            jp2 = os.path.join(tmp, "p.jp2")
            open(jp2, "wb").write(zf.read(name))
            gray = cv2.imread(jp2, cv2.IMREAD_GRAYSCALE)
            png = os.path.join(tmp, "ive%04d.png" % n)
            cv2.imwrite(png, gray)
            thr, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            bw = (gray < thr).astype(np.uint8)
            lines = ob.ocr(png, a.tessdata, a.cache or None, "ive%04d" % n)
            xhs = [l["x_size"] - l["x_asc"] - l["x_desc"] for l in lines
                   if l["x_size"] and l["x_asc"] is not None and l["x_desc"] is not None]
            xhs = [v for v in xhs if 25 <= v <= 60]
            page_xh = float(np.median(xhs)) if xhs else 40.0
            for l in lines:
                try:
                    xh = l["x_size"] - l["x_asc"] - l["x_desc"]
                except TypeError:
                    xh = page_xh
                if not (0.75 * page_xh <= xh <= 1.3 * page_xh):
                    xh = page_xh
                toks = []
                for w in l["words"]:
                    ital, _ = ob.is_italic(bw, l, w, xh)
                    flags = []
                    if re.search(r"[^\W\d_]", w["text"]) and not re.search(r"\d", w["text"]):
                        scale = xh / 41.0
                        for c in w["chars"]:
                            if c["text"] == "d":
                                prof = ob.stroke_profile(bw, l, c, xh, (-1.5, -1.4, -1.3, -1.2, -1.1))
                                if not (all(k >= 1 for k, wd in prof) and prof[0][1] >= 9 * scale):
                                    flags.append("d-like-accent")
                    toks.append(dict(t=w["text"], i=int(ital), c=w["conf"], f=flags, x=w["bbox"][0], x2=w["bbox"][2]))
                fo.write(json.dumps(dict(page=n + 113, x0=l["bbox"][0], y0=l["bbox"][1], x1=l["bbox"][2], y1=l["bbox"][3],
                                         page_w=gray.shape[1], page_h=gray.shape[0], words=toks), ensure_ascii=False) + "\n")
            print("image", n, "lines", len(lines), file=sys.stderr); fo.flush()


if __name__ == "__main__":
    main()
