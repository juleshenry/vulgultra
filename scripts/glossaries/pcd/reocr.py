#!/usr/bin/env python3
"""Re-OCR an archive.org scan with Tesseract 5 (the 2008 OCR text on archive.org is too noisy).

    python3 reocr.py IDENTIFIER [FIRST_LEAF LAST_LEAF]

Downloads https://archive.org/download/IDENTIFIER/IDENTIFIER_jp2.zip (the
page images, 150-250 MB) to a temporary folder unless it is already there,
runs `tesseract -l fra --psm 3` on every leaf (optionally only FIRST..LAST),
and writes raw/IDENTIFIER_tesseract.txt: the pages in order, each preceded by
a line `=== leaf NNNN ===`. Needs tesseract with the `fra` model.

The page images are not kept in raw/ (size); the text this script writes is
what the parse_*.py scripts read.
"""
from __future__ import annotations

import concurrent.futures
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
UA = "vulgultra-research/0.1 (+noncommercial; lexical sourcing)"
WORK = Path(os.environ.get("REOCR_WORK", tempfile.gettempdir())) / "vulgultra-reocr"


def ocr(path: Path) -> tuple[int, str]:
    leaf = int(re.search(r"_(\d{4})\.jp2$", path.name).group(1))
    done = subprocess.run(["tesseract", str(path), "stdout", "-l", "fra", "--psm", "3"],
                          capture_output=True, text=True, env={**os.environ, "OMP_THREAD_LIMIT": "1"})
    return leaf, done.stdout


def main() -> None:
    ident = sys.argv[1]
    first, last = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 10 ** 6)
    WORK.mkdir(parents=True, exist_ok=True)
    archive = WORK / f"{ident}_jp2.zip"
    if not archive.exists():
        request = urllib.request.Request(f"https://archive.org/download/{ident}/{ident}_jp2.zip",
                                         headers={"User-Agent": UA})
        with urllib.request.urlopen(request, timeout=1800) as response, archive.open("wb") as out:
            while chunk := response.read(1 << 20):
                out.write(chunk)
    pages = WORK / ident
    if not pages.exists():
        with zipfile.ZipFile(archive) as bundle:
            bundle.extractall(pages)
    leaves = sorted(p for p in pages.rglob("*.jp2")
                    if first <= int(re.search(r"_(\d{4})\.jp2$", p.name).group(1)) <= last)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) - 1)) as pool:
        results = dict(pool.map(ocr, leaves))
    target = HERE / "raw" / f"{ident}_tesseract.txt"
    with target.open("w", encoding="utf-8") as out:
        for leaf in sorted(results):
            out.write(f"=== leaf {leaf:04d} ===\n{results[leaf]}\n")
    print(f"{target.name}: {len(results)} leaves")


if __name__ == "__main__":
    main()
