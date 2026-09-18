#!/usr/bin/env python3
"""Entry point for the 4FQM configuration-driven figure workflow."""

from __future__ import annotations

import sys
from pathlib import Path


STRUCTURE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from pymol_common.structure_workflow import main  # noqa: E402


if __name__ == "__main__":
    main(STRUCTURE_ROOT)
