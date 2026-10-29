#!/usr/bin/env python3
"""Re-OCR a scanned PDF from raw/ with Tesseract (French model), page by page.

The archive.org OCR of some Norman scans was run without a French model and
lost every accent, or misreads the bold headwords. This renders each page of
the PDF at 300 dpi and runs `tesseract -l fra --psm N` (6 = one column, the
default; 3 = automatic layout, for two-column pages), writing one text file
with a form feed and a `### page N` line before each page (N = 0-based PDF
page index). An optional fourth argument sets the resolution: the parsers
keep a headword only when a 300 dpi and a 400 dpi reading agree on it.

Needs PyMuPDF (`fitz`) and the `tesseract` binary with the `fra` model.

    python3 ocr_tesseract.py raw/Dictionnaire_franco_normand.pdf raw/metivier-1870_tesseract-fra.txt
    python3 ocr_tesseract.py raw/Dictionnaire_franco_normand.pdf raw/metivier-1870_tesseract-fra-400dpi.txt 6 400
    python3 ocr_tesseract.py raw/normand_centre.pdf raw/moisy-1887_tesseract-fra.txt 3
    python3 ocr_tesseract.py raw/essaisurlepatois00joreuoft.pdf raw/joret-1881_tesseract-fra.txt
    python3 ocr_tesseract.py raw/essisurlepatoisn00fleuuoft.pdf raw/fleury-1886_tesseract-fra.txt
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import fitz

DPI = 300
WORKERS = 5
PSM = "6"


def ocr_page(args: tuple[str, int, str]) -> tuple[int, str]:
    pdf, index, workdir = args
    image = Path(workdir) / f"p{index:04d}.png"
    with fitz.open(pdf) as document:
        document[index].get_pixmap(dpi=DPI).save(image)
    done = subprocess.run(["tesseract", str(image), "stdout", "-l", "fra", "--psm", PSM],
                          capture_output=True, text=True, env={**os.environ, "OMP_THREAD_LIMIT": "1"})
    image.unlink(missing_ok=True)
    return index, done.stdout


def main() -> None:
    global PSM
    pdf, out = sys.argv[1], Path(sys.argv[2])
    global DPI
    if len(sys.argv) > 3:
        PSM = sys.argv[3]
    if len(sys.argv) > 4:
        DPI = int(sys.argv[4])
    with fitz.open(pdf) as document:
        count = len(document)
    with tempfile.TemporaryDirectory() as workdir, ThreadPoolExecutor(WORKERS) as pool:
        pages = dict(pool.map(ocr_page, [(pdf, i, workdir) for i in range(count)]))
    with out.open("w", encoding="utf-8") as handle:
        for index in range(count):
            handle.write(f"\f### page {index}\n{pages[index]}\n")
    print(f"{out}: {count} pages")


if __name__ == "__main__":
    main()
