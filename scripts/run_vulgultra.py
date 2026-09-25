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
    parser.add_argument("--bible-input-dir", type=Path, default=None,
                        help="Directory containing fr.tsv, es.tsv, pt.tsv, it.tsv, ro.tsv; compile before prep")
    parser.add_argument("--bible-grid-output", type=Path,
                        default=Path("data/bible/concept_grid.json"),
                        help="Compiled Bible grid path when --bible-input-dir is used")
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

    if args.bible_grid and args.bible_input_dir:
        parser.error("use --bible-grid or --bible-input-dir, not both")

    bible_grid = Path(absolute(args.bible_grid)) if args.bible_grid else None
    if args.bible_input_dir:
        bible_input_dir = Path(absolute(args.bible_input_dir))
        bible_grid = Path(absolute(args.bible_grid_output))
        compile_bible = [
            sys.executable, str(ROOT / "scripts" / "build_bible_grid.py"),
            "--input-dir", str(bible_input_dir),
            "--output", str(bible_grid),
        ]
        subprocess.run(compile_bible, cwd=ROOT, check=True)

    prep = [
        sys.executable, "-m", "vulgultra.pipeline", "prep",
        "--output", str(candidates), "--grid-output", str(grid),
    ]
    if args.langs:
        prep.extend(["--langs", args.langs])
    if bible_grid:
        prep.extend(["--bible-grid", str(bible_grid)])
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
