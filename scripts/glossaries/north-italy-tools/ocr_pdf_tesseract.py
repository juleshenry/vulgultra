#!/usr/bin/env python3
"""Re-OCR a scanned book (an archive.org image PDF) with Tesseract, page by page.

The OCR text archive.org ships for the 19th-century dialect dictionaries was
made around 2008 with ABBYY FineReader 8/9 and mangles the bold headwords
(`Argcnt.` for `Argent.`). Tesseract 5 with the `tessdata_best` Italian and
French models (French for ë, ê, ç, œ) reads them far better.

Each page is rendered from the PDF at its native image resolution, read with
`--psm 3` (automatic layout, so two-column pages come out column by column)
and written as `{out}/{page:04d}.tsv`: Tesseract's word table, one word per
row with block / paragraph / line numbers, box and confidence. Pages already
done are skipped, so the run can be resumed. About 8 CPU-seconds a page.

    python3 ocr_pdf_tesseract.py book.pdf out_dir [--first N] [--last N] [--step N] [--jobs 3] [--langs ita+fra]

Instead of a PDF the first argument may be a folder of page images named
`{page:04d}.jpg` (see `fetch_ia_pages.py`): the Google Books PDFs on
archive.org (`bub_gb_…`) hold the pages at only ~700 px wide.

`--step 30` reads every thirtieth page: a pilot to judge a book before the full run.

Needs: tesseract on PATH, PyMuPDF (`fitz`), and `tessdata/{ita,fra}.traineddata`
next to this script (from github.com/tesseract-ocr/tessdata_best, Apache-2.0).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import fitz

HERE = Path(__file__).resolve().parent
TESSDATA = HERE / "tessdata"
MAX_SIDE = 4200   # px: cap for very large page images


def page_image(page: "fitz.Page") -> "fitz.Pixmap":
    """The page at the resolution of its largest embedded image (the scan itself)."""
    widest = max((image[2] for image in page.get_images(full=True)), default=0)
    zoom = widest / page.rect.width if widest else 300 / 72
    zoom = max(min(zoom, MAX_SIDE / max(page.rect.width, page.rect.height)), 200 / 72)
    return page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csGRAY)


def ocr_page(job: tuple[str, int, str, str]) -> int:
    pdf, number, out, langs = job
    target = Path(out) / f"{number:04d}.tsv"
    if target.is_file() and target.stat().st_size > 200:      # more than the header line
        return number
    with tempfile.TemporaryDirectory() as scratch:
        if Path(pdf).is_dir():                                # a folder of page images, `{page:04d}.jpg`
            image = Path(pdf) / f"{number:04d}.jpg"
            if not image.is_file():
                return -1
        else:
            image = Path(scratch) / "page.png"
            page_image(fitz.open(pdf)[number]).save(image)
        environment = dict(os.environ, OMP_THREAD_LIMIT="1")
        result = subprocess.run(
            ["tesseract", str(image), str(Path(scratch) / "page"), "--tessdata-dir", str(TESSDATA),
             "-l", langs, "--psm", "3", "-c", "tessedit_create_tsv=1", "-c", "tessedit_create_txt=0"],
            check=False, env=environment, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        produced = Path(scratch) / "page.tsv"
        if result.returncode != 0 or not produced.is_file():
            print(f"page {number}: tesseract failed: {result.stderr.strip()[:200]}", file=sys.stderr, flush=True)
            return -1
        text = produced.read_text(encoding="utf-8")
    partial = target.with_suffix(".part")
    partial.write_text(text or "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n",
                       encoding="utf-8")
    partial.replace(target)
    return number


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("pdf")
    parser.add_argument("out")
    parser.add_argument("--first", type=int, default=0)
    parser.add_argument("--last", type=int, default=-1)
    parser.add_argument("--step", type=int, default=1)
    parser.add_argument("--jobs", type=int, default=3)
    parser.add_argument("--langs", default="ita+fra")
    arguments = parser.parse_args()
    Path(arguments.out).mkdir(parents=True, exist_ok=True)
    if Path(arguments.pdf).is_dir():
        total = max((int(path.stem) for path in Path(arguments.pdf).glob("[0-9]*.jpg")), default=-1) + 1
    else:
        total = len(fitz.open(arguments.pdf))
    last = total - 1 if arguments.last < 0 else min(arguments.last, total - 1)
    jobs = [(arguments.pdf, number, arguments.out, arguments.langs) for number in range(arguments.first, last + 1, arguments.step)]
    done = 0
    with ProcessPoolExecutor(max_workers=arguments.jobs) as pool:
        for number in pool.map(ocr_page, jobs, chunksize=1):
            done += number >= 0
            if done % 50 == 0:
                print(f"{done}/{len(jobs)} pages", file=sys.stderr, flush=True)
    print(f"done: {len(jobs)} pages -> {arguments.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
