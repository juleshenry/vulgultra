#!/usr/bin/env python3
"""Second OCR of Coulabin 1891 from the archive.org page scans, with Tesseract.

archive.org's own text layer (raw/dictionnairedesl00couluoft_djvu.txt, ABBYY FineReader) misreads part of
the bold headwords (Haldabou -> "HaldabOD", Achaison -> "Achaîson"). The parser therefore accepts a headword
only when a second, independent OCR engine reads it the same way. This
script makes that second reading: it rasterises pages 14-404 of
raw/dictionnairedesl00couluoft.pdf at 300 dpi and runs Tesseract 5 with the French model
(--psm 6, the pages are single-column), writing one text file with a form
feed and a "=== page N ===" line per PDF page.

Needs `pdftoppm` (poppler) and `tesseract` with the `fra` traineddata.

    python3 ocr_coulabin-1891-rennes.py      # writes ocr/coulabin-1891_tesseract-fra.txt
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
PDF = HERE / "raw" / "dictionnairedesl00couluoft.pdf"
OUT = HERE / "ocr" / "coulabin-1891_tesseract-fra.txt"
FIRST, LAST, DPI, WORKERS = 14, 404, 300, 4


def ocr_page(page: int, tmp: str) -> str:
    stem = Path(tmp) / f"p{page:04d}"
    subprocess.run(["pdftoppm", "-r", str(DPI), "-gray", "-png", "-f", str(page), "-l", str(page),
                    "-singlefile", str(PDF), str(stem)], check=True)
    text = subprocess.run(["tesseract", f"{stem}.png", "stdout", "-l", "fra", "--psm", "6"],
                          capture_output=True, text=True, env=dict(os.environ, OMP_THREAD_LIMIT="1")).stdout
    Path(f"{stem}.png").unlink(missing_ok=True)
    return text


def main() -> None:
    OUT.parent.mkdir(exist_ok=True)
    pages = list(range(FIRST, LAST + 1))
    with tempfile.TemporaryDirectory() as tmp, ThreadPoolExecutor(WORKERS) as pool:
        texts = list(pool.map(lambda page: ocr_page(page, tmp), pages))
    with OUT.open("w", encoding="utf-8") as out:
        for page, text in zip(pages, texts):
            out.write(f"\f=== page {page} ===\n{text}\n")
    print(f"{OUT.relative_to(HERE)}: {len(pages)} pages")


if __name__ == "__main__":
    main()
