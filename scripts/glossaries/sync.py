#!/usr/bin/env python3
"""Copy the per-source parsers to where they run: beside each lect's `raw/` folder.

    python3 scripts/glossaries/sync.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TARGETS = ((HERE, ROOT / "data" / "sources" / "glossaries"), (HERE.parent / "bible_lects", ROOT / "data" / "bible" / "lects"))


def main() -> None:
    copied = 0
    for source, target in TARGETS:
        for path in sorted(source.rglob("*")):
            if path.suffix in (".py", ".sh") and path != Path(__file__).resolve():
                destination = target / path.relative_to(source)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, destination)
                copied += 1
    print(f"{copied} scripts copied under {ROOT / 'data'}")


if __name__ == "__main__":
    main()
