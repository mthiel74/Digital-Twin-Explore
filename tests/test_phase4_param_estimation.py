import numpy as np

from pipeline_twin.config import load_config
from pipeline_twin.enkf import initialize_ensemble, update


def test_parameter_drift_and_inflation_apply():
    cfg = load_config("configs/default.yaml")
    cfg.enkf.parameter_drift = 0.05
    cfg.enkf.inflation = 1.05

    enkf_state = initialize_ensemble(cfg)
    rng = np.random.default_rng(123)
    ensemble_before = enkf_state.ensemble.copy()

    measurement = {
        "pressure": np.zeros(cfg.domain.n_cells),
        "flow": np.zeros(cfg.domain.n_cells - 1),
    }
    enkf_state = update(enkf_state, measurement, cfg, rng=rng)

    params_before = ensemble_before[:, -2:]
    params_after = enkf_state.ensemble[:, -2:]
    assert np.all(params_after >= 0.0)
    assert np.mean(params_after) > np.mean(params_before)
