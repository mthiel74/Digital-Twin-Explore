"""Command-line entrypoint for the pipeline digital twin prototype."""
from __future__ import annotations

import argparse

from .config import load_config
from .enkf import initialize_ensemble, propagate, update
from .multihypothesis import evaluate_leak_hypotheses
from .plots import (
    plot_boundary_commands,
    plot_flow_heatmap,
    plot_leak_scores,
    plot_pressure_heatmap,
    plot_pressure_sections,
    plot_residuals,
)
from .simulate import run_simulation


def main() -> None:
    parser = argparse.ArgumentParser(description="Run pipeline digital twin simulation")
    parser.add_argument("--config", type=str, default="configs/default.yaml", help="Path to YAML/JSON config")
    parser.add_argument("--outdir", type=str, default="outputs", help="Directory for plots")
    parser.add_argument("--image-format", type=str, default="png", choices=["png", "svg"], help="Image format for saved plots")
    parser.add_argument("--no-plots", action="store_true", help="Disable plot generation")
    args = parser.parse_args()

    cfg = load_config(args.config)
    result = run_simulation(cfg)

    if not args.no_plots:
        outputs = []
        pressure_true = _stack_pressures(result)
        commands = _stack_commands(result)
        flow_true = _stack_flows(result)
        ext = args.image_format

        path_heat = plot_pressure_heatmap(result.time, pressure=pressure_true, outdir=args.outdir, ext=ext)
        outputs.append(path_heat)

        flow_heat = plot_flow_heatmap(result.time, flow_true, outdir=args.outdir, ext=ext)
        outputs.append(flow_heat)

        pressure_meas = _collect_pressure_measurements(result)
        sections = plot_pressure_sections(result.time, pressure_true, pressure_meas, outdir=args.outdir, ext=ext)
        outputs.append(sections)

        bounds = plot_boundary_commands(result.time, commands, outdir=args.outdir, ext=ext)
        outputs.append(bounds)

        _, residuals = _run_enkf_analysis(result, cfg)
        resid_path = plot_residuals(result.time, residuals, outdir=args.outdir, ext=ext)
        outputs.append(resid_path)

        if cfg.hypotheses:
            scores = evaluate_leak_hypotheses(cfg.hypotheses, result.measurements, result.commands, cfg)
            leak_path = plot_leak_scores(scores, outdir=args.outdir, ext=ext)
            outputs.append(leak_path)

        print("Saved plots:")
        for p in outputs:
            print(f" - {p}")


def _stack_pressures(result):
    import numpy as np

    return np.stack([state.pressure for state in result.states])


def _stack_commands(result):
    import numpy as np

    return np.stack([[cmd.pump_command, cmd.valve_command] for cmd in result.commands])


def _stack_flows(result):
    import numpy as np

    return np.stack([state.flow for state in result.states])


def _collect_pressure_measurements(result):
    import numpy as np

    measurements = []
    for meas in result.measurements:
        if "pressure" in meas:
            measurements.append(meas["pressure"])
        else:
            measurements.append(np.full_like(result.states[0].pressure, np.nan))
    return np.stack(measurements)


def _run_enkf_analysis(result, cfg):
    import numpy as np

    enkf_state = initialize_ensemble(cfg)
    n_steps = len(result.time)
    n_cells = cfg.domain.n_cells
    rng = np.random.default_rng(cfg.sensors.seed)

    mean_pressure = np.zeros((n_steps, n_cells))
    residuals = np.zeros(n_steps)

    for k, (meas, cmd) in enumerate(zip(result.measurements, result.commands)):
        enkf_state = propagate(enkf_state, cmd, cfg)
        prior_mean = enkf_state.ensemble.mean(axis=0)
        if meas:
            enkf_state = update(enkf_state, meas, cfg, rng=rng)
        post_mean = enkf_state.ensemble.mean(axis=0)
        mean_pressure[k] = post_mean[:n_cells]
        residuals[k] = float(np.linalg.norm(post_mean[:n_cells] - prior_mean[:n_cells]))

    return mean_pressure, residuals


if __name__ == "__main__":
    main()
