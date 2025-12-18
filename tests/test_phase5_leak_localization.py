import numpy as np

from pipeline_twin.config import load_config, TwinConfig, LeakConfig
from pipeline_twin.multihypothesis import evaluate_leak_hypotheses
from pipeline_twin.simulate import run_simulation


def test_leak_bank_scores_true_location_best():
    base_cfg = load_config("configs/default.yaml")
    leak_cfg = LeakConfig(coefficient=0.05, index=12, start_time=None)
    cfg = TwinConfig(domain=base_cfg.domain, boundaries=base_cfg.boundaries, leak=leak_cfg, sensors=base_cfg.sensors, enkf=base_cfg.enkf)
    result = run_simulation(cfg)

    measurements = [{k: v for k, v in m.items()} for m in result.measurements if m]
    commands = [c for m, c in zip(result.measurements, result.commands) if m]

    scores = evaluate_leak_hypotheses([5, 8, 12, 20], measurements, commands, cfg)
    best_index = min(scores, key=scores.get)
    assert best_index == leak_cfg.index
    assert all(np.isfinite(list(scores.values())))
