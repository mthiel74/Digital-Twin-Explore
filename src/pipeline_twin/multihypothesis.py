"""Multi-hypothesis leak localization via a bank of filters."""
from __future__ import annotations

from dataclasses import replace
from typing import Dict, List
import numpy as np

from .config import TwinConfig
from .enkf import EnKFState, initialize_ensemble, propagate, update
from .physics import BoundaryInputs


def evaluate_leak_hypotheses(hypotheses: List[int], measurements: List[Dict], commands: List[BoundaryInputs], cfg: TwinConfig) -> Dict[int, float]:
    """Run a lightweight bank of filters to score each candidate leak index.

    Scores are normalized negative log-likelihood proxies derived from ensemble
    innovation magnitudes. Lower scores indicate better agreement with
    observations.
    """
    scores: Dict[int, float] = {}
    for idx in hypotheses:
        cfg_copy = replace(cfg, leak=replace(cfg.leak, index=idx))
        enkf_state = initialize_ensemble(cfg_copy)
        innovation_score = 0.0
        pressure_score_terms = []
        for meas, cmd in zip(measurements, commands):
            enkf_state = propagate(enkf_state, cmd, cfg_copy)
            prior = enkf_state.ensemble.mean(axis=0)
            enkf_state = update(enkf_state, meas, cfg_copy)
            post = enkf_state.ensemble.mean(axis=0)
            innovation_score += float(np.linalg.norm(post - prior))
            if "pressure" in meas:
                candidate = min(max(idx, 0), cfg_copy.domain.n_cells - 1)
                pressure_score_terms.append(float(np.mean(meas["pressure"][candidate])))
        mean_pressure = float(np.mean(pressure_score_terms)) if pressure_score_terms else 0.0
        innovation_score = innovation_score / max(len(measurements), 1)
        scores[idx] = 0.5 * innovation_score + 0.5 * mean_pressure
    return scores
