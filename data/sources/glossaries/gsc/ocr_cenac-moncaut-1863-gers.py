#!/usr/bin/env python3
"""Re-OCR Cénac-Moncaut 1863 from the archive.org page scans with Tesseract.

archive.org's own text layer for this Google scan (raw/dictionnairegas00cngoog_djvu.txt)
misreads the bold small-capital headwords systematically (C as G, U as D:
ABACHA -> "Abagha", ABASTOUA -> "Abastoda"), so it cannot supply headwords.
This script rasterises raw/dictionnairegas00cngoog.pdf (600 ppi bitonal
scans) at 300 dpi and runs Tesseract 5 with the French model, one text file
for the whole book with a form feed and "=== page N ===" line per PDF page.

Needs `pdftoppm` (poppler) and `tesseract` with the `fra` traineddata.

    python3 ocr_cenac-moncaut-1863-gers.py      # writes ocr/cenac-moncaut-1863_tesseract-fra.txt
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PDF = HERE / "raw" / "dictionnairegas00cngoog.pdf"
OUT = HERE / "ocr" / "cenac-moncaut-1863_tesseract-fra.txt"


def main() -> None:
    OUT.parent.mkdir(exist_ok=True)
    pages = int(next(line.split()[1] for line in subprocess.run(
        ["pdfinfo", str(PDF)], capture_output=True, text=True, check=True).stdout.splitlines()
        if line.startswith("Pages:")))
    with tempfile.TemporaryDirectory() as tmp, OUT.open("w", encoding="utf-8") as out:
        for page in range(1, pages + 1):
            stem = Path(tmp) / f"p{page:04d}"
            subprocess.run(["pdftoppm", "-r", "300", "-gray", "-png", "-f", str(page), "-l", str(page),
                            "-singlefile", str(PDF), str(stem)], check=True)
            text = subprocess.run(["tesseract", f"{stem}.png", "stdout", "-l", "fra", "--psm", "1"],
                                  capture_output=True, text=True).stdout
            out.write(f"\f=== page {page} ===\n{text}\n")
            Path(f"{stem}.png").unlink(missing_ok=True)
    print(f"{OUT.relative_to(HERE)}: {pages} pages")


if __name__ == "__main__":
    main()
