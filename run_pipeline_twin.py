"""Convenience launcher that adds ``src/`` to ``sys.path`` before running the pipeline twin."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence


def _ensure_src_on_path(repo_root: Path) -> None:
    """Prepend the repository ``src/`` directory to ``sys.path`` if missing."""
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def main(argv: Sequence[str] | None = None) -> None:
    """Run the pipeline twin CLI with deterministic path setup."""
    repo_root = Path(__file__).resolve().parent
    _ensure_src_on_path(repo_root)

    from pipeline_twin.run import main as pipeline_main

    pipeline_main(argv)


if __name__ == "__main__":
    main(sys.argv[1:])
