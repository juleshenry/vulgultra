#!/usr/bin/env python3
"""Fetch page images of an archive.org scan, one a second, as `{out}/{page:04d}.jpg`.

Some archive.org PDFs (the Google Books ones, `bub_gb_…`) hold the pages at
only ~700 px wide, too coarse for OCR; the full-size page images are served
one by one at `https://archive.org/download/{id}/page/n{N}.jpg`.

    python3 fetch_ia_pages.py IDENTIFIER out_dir --first 40 --last 1230 [--step 30]
"""

from __future__ import annotations

import argparse
import time
import urllib.request
from pathlib import Path

AGENT = "vulgultra-research/0.1 (+noncommercial; lexical sourcing)"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("identifier")
    parser.add_argument("out")
    parser.add_argument("--first", type=int, required=True)
    parser.add_argument("--last", type=int, required=True)
    parser.add_argument("--step", type=int, default=1)
    arguments = parser.parse_args()
    out = Path(arguments.out)
    out.mkdir(parents=True, exist_ok=True)
    for number in range(arguments.first, arguments.last + 1, arguments.step):
        target = out / f"{number:04d}.jpg"
        if target.is_file() and target.stat().st_size > 10_000:
            continue
        url = f"https://archive.org/download/{arguments.identifier}/page/n{number}.jpg"
        request = urllib.request.Request(url, headers={"User-Agent": AGENT})
        started = time.time()
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                target.write_bytes(response.read())
        except Exception as error:      # noqa: BLE001 - report and go on
            print(f"page {number}: {error}", flush=True)
        time.sleep(max(0.0, 1.1 - (time.time() - started)))
    print("done", flush=True)


if __name__ == "__main__":
    main()
