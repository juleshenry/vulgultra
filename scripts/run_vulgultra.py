#!/usr/bin/env python3
"""Run prep → Rust annealing → render the report from that exact lexicon."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--iterations", type=int, default=500_000)
    parser.add_argument("-s", "--seed", type=int, default=42)
    parser.add_argument("--langs", default=None,
                        help="Comma-separated daughter lect codes; defaults to all 36")
    parser.add_argument("--bible-grid", type=Path, default=None,
                        help="Optional compiled five-language Bible grid")
    parser.add_argument("--candidates", type=Path, default=Path("data/candidates.json"))
    parser.add_argument("--grid", type=Path, default=Path("data/concept_grid.json"))
    parser.add_argument("--lexicon", type=Path, default=Path("data/vulgultra_lexicon.json"))
    parser.add_argument("--report", type=Path,
                        default=Path("docs/eval/34_romance_scorecard.md"))
    args = parser.parse_args()

    def absolute(path: Path) -> str:
        return str((ROOT / path).resolve()) if not path.is_absolute() else str(path)

    candidates = Path(absolute(args.candidates))
    grid = Path(absolute(args.grid))
    lexicon = Path(absolute(args.lexicon))
    report = Path(absolute(args.report))

    prep = [
        sys.executable, "-m", "vulgultra.pipeline", "prep",
        "--output", str(candidates), "--grid-output", str(grid),
    ]
    if args.langs:
        prep.extend(["--langs", args.langs])
    if args.bible_grid:
        prep.extend(["--bible-grid", absolute(args.bible_grid)])
    subprocess.run(prep, cwd=ROOT, check=True)

    optimize = [
        "cargo", "run", "--release", "--",
        "--input", str(candidates), "--output", str(lexicon),
        "--iterations", str(args.iterations), "--seed", str(args.seed),
    ]
    subprocess.run(optimize, cwd=ROOT / "vulgultra-cli", check=True)

    render = [
        sys.executable, str(ROOT / "scripts" / "es_pt_beta.py"),
        "--candidates", str(candidates), "--lexicon", str(lexicon),
        "--output", str(report),
    ]
    subprocess.run(render, cwd=ROOT, check=True)
    print(f"Current phrase report refreshed from {lexicon}: {report}")


if __name__ == "__main__":
    main()
