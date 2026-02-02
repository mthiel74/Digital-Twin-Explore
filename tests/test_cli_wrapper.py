from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import run_pipeline_twin


def test_ensure_src_on_path(monkeypatch):
    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"
    monkeypatch.setattr(sys, "path", [p for p in sys.path if p != str(src_path)])

    run_pipeline_twin._ensure_src_on_path(repo_root)

    assert sys.path[0] == str(src_path)


def test_wrapper_main_forwards_arguments(monkeypatch):
    captured = {}

    def fake_main(argv):
        captured["argv"] = argv

    monkeypatch.setattr("pipeline_twin.run.main", fake_main)
    args = ["--config", "configs/default.yaml", "--no-plots"]

    run_pipeline_twin.main(args)

    assert captured["argv"] == args
