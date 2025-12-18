import numpy as np

from pipeline_twin.config import load_config
from pipeline_twin.enkf import initialize_ensemble, propagate, update
from pipeline_twin.physics import BoundaryInputs


def _innovation_norm(ensemble_mean, measurement, n_cells):
    obs_indices = list(range(n_cells)) + list(range(n_cells, n_cells + (n_cells - 1)))
    H = np.eye(ensemble_mean.shape[0])[obs_indices]
    y_pred = H @ ensemble_mean
    y = np.concatenate([measurement["pressure"], measurement["flow"]])
    return np.linalg.norm(y - y_pred)


def test_update_reduces_innovation():
    cfg = load_config("configs/default.yaml")
    cfg.enkf.inflation = 1.0
    enkf_state = initialize_ensemble(cfg)

    rng = np.random.default_rng(0)
    enkf_state.ensemble += rng.normal(0.0, 0.1, size=enkf_state.ensemble.shape)

    inputs = BoundaryInputs(pump_command=0.5, valve_command=0.5)
    enkf_state = propagate(enkf_state, inputs, cfg)

    measurement = {
        "pressure": np.full(cfg.domain.n_cells, 0.3),
        "flow": np.full(cfg.domain.n_cells - 1, 0.1),
    }
    pre_innov = _innovation_norm(enkf_state.ensemble.mean(axis=0), measurement, cfg.domain.n_cells)
    enkf_state = update(enkf_state, measurement, cfg, rng=np.random.default_rng(1))
    post_innov = _innovation_norm(enkf_state.ensemble.mean(axis=0), measurement, cfg.domain.n_cells)
    assert post_innov < pre_innov
