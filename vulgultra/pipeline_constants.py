"""Paths and source metadata for the pipeline.

Keeping paths here makes the data boundary explicit: source evidence enters
through the grid, candidate JSON preserves its evidence, and Rust consumes
only that JSON.  See docs/architecture.md and docs/sources_manifest.md.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORDS_DIR = ROOT / "data" / "words"
BIBLE_GRID_PATH = ROOT / "data" / "bible" / "concept_grid.json"
BIBLE_LANGS = ("fr", "es", "pt", "it", "ro")
LANGUAGES = (
    "es", "pt", "gl", "an", "ast", "ext", "lad", "mwl", "oc", "ca", "gsc",
    "fr", "wa", "pcd", "nrf", "gallo", "frp", "lmo", "pms", "lij", "eml", "rgn",
    "it", "scn", "vec", "co", "ist", "dlm", "rm", "fur", "lld", "sc", "ro", "rup", "ruo", "ruq",
)

CONCEPT_GRID_SCHEMA = "vulgultra.concept-grid.v1"
BIBLE_GRID_SCHEMA = "vulgultra.bible-grid.v1"
CANDIDATE_SCHEMA = "vulgultra.candidates.v2"
