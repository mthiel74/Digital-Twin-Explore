"""Command-line entrypoint for the pipeline digital twin prototype."""
from __future__ import annotations

import argparse
from .config import load_config
from .plots import plot_pressure_heatmap
from .simulate import run_simulation


def main() -> None:
    parser = argparse.ArgumentParser(description="Run pipeline digital twin simulation")
    parser.add_argument("--config", type=str, default="configs/default.yaml", help="Path to YAML config")
    parser.add_argument("--outdir", type=str, default="outputs", help="Directory for plots")
    parser.add_argument("--no-plots", action="store_true", help="Disable plot generation")
    args = parser.parse_args()

    cfg = load_config(args.config)
    result = run_simulation(cfg)

    if not args.no_plots:
        path = plot_pressure_heatmap(result.time, pressure=_stack_pressures(result), outdir=args.outdir)
        print(f"Saved pressure heatmap to {path}")


def _stack_pressures(result):
    import numpy as np

    return np.stack([state.pressure for state in result.states])


if __name__ == "__main__":
    main()
