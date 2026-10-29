#!/usr/bin/env python3
"""Second readings for Dalla Zonca 1978, for two OCR faults the parser cannot
settle from the first reading alone:

 token  a bold head token with "du" and no accent ("dun", "aiduto"): bold "ò"
        before "u" is often read as "d".  The word box is cut out, enlarged x2
        and read again twice (tessdata_best `ita`, and the script model `Latin`).
          repair  a second reading has "òu" exactly where the first has "du"
                  (44 of 44 such repairs checked on the scan were right)
          repair-rule  the token is dun / duna / duno and no reading says òu:
                  set to òun / òuna / òuno.  The book has no word "dun": on the
                  scan all 5 such cases checked were òun, òuna, òuno.
          keep    both second readings agree with the first (a real d: "dui",
                  "cagadura"; 6 of 6 checked on the scan were right)
          unsure  anything else -> the parser sends the entry to the doubtful file
 head   a line that begins with the dash: tesseract returned no text for the
        bold head word.  The line from the column edge to a little past the
        dash is read again on its own (x2, `ita`, single-line mode).
          read    one or more words came back
          none    nothing usable -> the parser drops the entry (counted)

Output: raw/dallazonca_1978_reread_tokens.tsv
        kind  page  left  top  ocr  read_ita  read_latin  decision  repaired
Not needed to rebuild the TSV (the output is kept in raw/); kept so the step
can be repeated.  Needs tesseract 5, tessdata_best ita + script/Latin, numpy, cv2.

  python3 reread_dallazonca.py --tessdata DIR --work DIR_WITH_JP2 [--words FILE] [--out FILE]
"""
import argparse, collections, csv, importlib.util, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("dzparse", os.path.join(HERE, "parse_dallazonca-1978.py"))
dz = importlib.util.module_from_spec(spec); spec.loader.exec_module(dz)


def ocr_strips(strips, lang, tessdata, tmp, psm="6"):
    """strips: list of small grayscale images.  They are stacked into one tall
    page, one per row, read in a single tesseract call; -> list of strings."""
    import numpy as np, cv2
    res = [""] * len(strips)
    B = 30
    for start in range(0, len(strips), B):
        batch = strips[start:start + B]
        W = max(im.shape[1] for im in batch) + 80
        rows, ypos, y = [], [], 40
        for im in batch:
            ypos.append((y, y + im.shape[0]))
            y += im.shape[0] + 60
        page = np.full((y + 40, W), 255, np.uint8)
        for im, (y0, y1) in zip(batch, ypos):
            page[y0:y1, 40:40 + im.shape[1]] = im
        png = os.path.join(tmp, "strip_%s_%d.png" % (lang, start))
        cv2.imwrite(png, page)
        env = dict(os.environ, OMP_THREAD_LIMIT="1")
        subprocess.run(["tesseract", png, png[:-4], "--tessdata-dir", tessdata, "-l", lang, "--psm", psm,
                        "-c", "tessedit_create_tsv=1"], env=env, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, check=False)
        got = collections.defaultdict(list)
        if os.path.exists(png[:-4] + ".tsv"):
            with open(png[:-4] + ".tsv", encoding="utf-8") as f:
                for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                    if r["level"] != "5" or not r["text"].strip():
                        continue
                    yc = int(r["top"]) + int(r["height"]) / 2
                    for k, (y0, y1) in enumerate(ypos):
                        if y0 - 25 <= yc <= y1 + 25:
                            got[k].append((int(r["left"]), r["text"]))
                            break
        for k in range(len(batch)):
            res[start + k] = " ".join(t for _, t in sorted(got[k]))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tessdata", required=True)
    ap.add_argument("--work", required=True, help="directory holding RovignoAtti-02-1978_jp2/*.jp2")
    ap.add_argument("--words", default=dz.WORDS)
    ap.add_argument("--out", default=dz.REREAD)
    a = ap.parse_args()
    import numpy as np, cv2
    stats = collections.Counter()
    ents = dz.prepared_entries(stats, a.words)
    jobs = []                                # (kind, page, x, y, w, h, ocr)
    lines_x0 = {}
    for e in ents:
        if (e["orphan"] or e["gap"]) and e["sepx"] is not None and e["lines"] == 1:
            jobs.append(("head", e["page"], e["sepx"], e["sepy"], e["colx"] or 0, 0,
                         " ".join(w.t for w in e["head"])))
            if e["orphan"]:
                continue
        for w in e["head_ws"]:
            if dz.dgrave_candidate(w.t):
                jobs.append(("token", w.page, w.x, w.y, w.w, w.h, w.t))
    # column start for the orphan heads: commonest line start left of the dash
    starts = collections.defaultdict(collections.Counter)
    for e in ents:
        if not e["orphan"]:
            starts[e["page"]][e["x"] // 8 * 8] += 1
    strips, cache = [], {}
    for kind, page, x, y, w, h, t in jobs:
        if page not in cache:
            cache.clear()
            jp2 = os.path.join(a.work, "RovignoAtti-02-1978_jp2", "RovignoAtti-02-1978_%04d.jp2" % page)
            cache[page] = cv2.imread(jp2, cv2.IMREAD_GRAYSCALE)
        img = cache[page]
        if kind == "head":                   # here w = x of the line start, 0 if unknown
            cands = [s for s, n in starts[page].items() if s < x - 40 and x - s < 760 and n >= 3]
            x0 = w if w else (max(cands) if cands else max(0, x - 300))
            crop = img[max(0, y - 34):y + 30, max(0, x0 - 12):x + 260]
            cv2.imwrite(os.path.join(a.work, "reread_head_%d_%d_%d.png" % (page, x, y)) , crop)
        else:
            crop = img[max(0, y - 8):y + h + 8, max(0, x - 10):x + w + 10]
        crop = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        strips.append(crop)
    os.makedirs(os.path.join(a.work, "reread"), exist_ok=True)
    tmp = os.path.join(a.work, "reread")

    def single(im, lang, psm):
        png = os.path.join(tmp, "one.png")
        cv2.imwrite(png, cv2.copyMakeBorder(im, 30, 30, 30, 30, cv2.BORDER_CONSTANT, value=255))
        env = dict(os.environ, OMP_THREAD_LIMIT="1")
        r = subprocess.run(["tesseract", png, "stdout", "--tessdata-dir", a.tessdata, "-l", lang, "--psm", psm],
                           env=env, capture_output=True, text=True, check=False)
        return " ".join(r.stdout.split())

    tok_idx = [k for k, j in enumerate(jobs) if j[0] == "token"]
    r_ita = [""] * len(jobs); r_lat = [""] * len(jobs)
    for lang, res in (("ita", r_ita), ("Latin", r_lat)):
        got = ocr_strips([strips[k] for k in tok_idx], lang, a.tessdata, tmp)
        for k, g in zip(tok_idx, got):
            res[k] = g if g.strip() else single(strips[k], lang, "8")   # nothing in the batch: read it alone
    for k, j in enumerate(jobs):
        if j[0] == "head":
            r_ita[k] = single(strips[k], "ita", "7")
    def norm(s):
        return re.sub(r"[^\w]", "", s.lower())
    with open(a.out, "w", encoding="utf-8", newline="") as f:
        f.write("kind\tpage\tleft\ttop\tocr\tread_ita\tread_latin\tdecision\trepaired\n")
        for (kind, page, x, y, w, h, t), ra, rb in zip(jobs, r_ita, r_lat):
            if kind == "head":
                m = re.match(r"^(.*?)\s+[-–—]\s", ra.strip() + " ")
                txt = m.group(1).strip() if m else ""
                ok = bool(re.fullmatch(r"[a-zàèìòùA-Z’' ,().]+", txt)) and dz.letters(txt) >= 2
                dec, rep = ("read", txt) if ok else ("none", "")
            else:
                first = norm(t)
                opts = set()
                for m in re.finditer("du", t.lower()):
                    opts.add(t[:m.start()] + "òu" + t[m.end():])
                hit = [o for o in opts if norm(o) in (norm(ra), norm(rb))]
                if len(hit) == 1:
                    dec, rep = "repair", hit[0]
                elif first in ("dun", "duna", "duno"):
                    dec, rep = "repair-rule", re.sub("du", "òu", t, count=1)
                elif norm(ra) == first and norm(rb) == first:
                    dec, rep = "keep", t
                else:
                    dec, rep = "unsure", ""
            stats[kind + "_" + dec] += 1
            f.write("\t".join([kind, str(page), str(x), str(y), t, ra, rb, dec, rep]) + "\n")
    for k in sorted(stats):
        if "_" in k and k.split("_")[0] in ("token", "head"):
            print(k, stats[k])


if __name__ == "__main__":
    main()
