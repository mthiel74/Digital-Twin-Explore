"""Lightweight Ensemble Kalman Filter for pipeline state and parameter estimation."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .config import EnKFConfig, TwinConfig
from .physics import PipelineState, step, BoundaryInputs


@dataclass
class EnKFState:
    ensemble: np.ndarray


def initialize_ensemble(cfg: TwinConfig) -> EnKFState:
    """Initialize ensembles around zero states with parameter perturbations."""
    n = cfg.enkf.ensemble_size
    n_cells = cfg.domain.n_cells
    state_dim = 2 * n_cells - 1 + 2  # pressure, flow, friction_scale, pump_gain
    rng = np.random.default_rng(cfg.sensors.seed)
    ens = rng.normal(0.0, 0.05, size=(n, state_dim))
    ens[:, :n_cells] = np.abs(ens[:, :n_cells])
    ens[:, -2] = np.abs(1.0 + ens[:, -2])
    ens[:, -1] = np.abs(1.0 + ens[:, -1])
    return EnKFState(ensemble=ens)


def propagate(enkf_state: EnKFState, inputs: BoundaryInputs, cfg: TwinConfig) -> EnKFState:
    """Propagate each ensemble member deterministically."""
    n_cells = cfg.domain.n_cells
    for i in range(enkf_state.ensemble.shape[0]):
        member = enkf_state.ensemble[i]
        pressure = member[:n_cells]
        flow = member[n_cells:-2]
        pipeline_state = PipelineState(pressure=pressure, flow=flow, friction_scale=member[-2], pump_gain=member[-1])
        new_state = step(pipeline_state, inputs, cfg.domain)
        enkf_state.ensemble[i, :n_cells] = new_state.pressure
        enkf_state.ensemble[i, n_cells:-2] = new_state.flow
    return enkf_state


def update(enkf_state: EnKFState, measurement: dict, cfg: TwinConfig, rng: np.random.Generator | None = None) -> EnKFState:
    """Basic stochastic EnKF update using pressure and flow observations."""
    if not measurement:
        return enkf_state
    rng = rng or np.random.default_rng(cfg.sensors.seed)

    obs_keys = []
    obs_values = []
    for key in ("pressure", "flow"):
        if key in measurement:
            obs_keys.append(key)
            obs_values.append(np.asarray(measurement[key]).ravel())
    if not obs_keys:
        return enkf_state

    y = np.concatenate(obs_values)
    ensemble = enkf_state.ensemble
    mean = ensemble.mean(axis=0)
    anomalies = ensemble - mean

    # simple observation operator: picks state entries by slicing
    n_cells = cfg.domain.n_cells
    obs_indices = []
    if "pressure" in obs_keys:
        obs_indices.extend(range(n_cells))
    if "flow" in obs_keys:
        obs_indices.extend(range(n_cells, n_cells + (n_cells - 1)))
    H = np.eye(ensemble.shape[1])[obs_indices]

    R = np.eye(len(obs_indices)) * cfg.sensors.pressure_noise * cfg.enkf.obs_noise_scale

    Y = ensemble @ H.T
    y_mean = Y.mean(axis=0)
    Y_anom = Y - y_mean

    C_xy = anomalies.T @ Y_anom / (ensemble.shape[0] - 1)
    jitter = np.eye(len(obs_indices)) * 1e-6
    C_yy = Y_anom.T @ Y_anom / (ensemble.shape[0] - 1) + R + jitter

    K = C_xy @ np.linalg.pinv(C_yy)
    innovation = y - y_mean
    ensemble += (innovation @ K.T)
    if cfg.enkf.parameter_drift > 0.0:
        ensemble += rng.normal(0.0, cfg.enkf.parameter_drift, size=ensemble.shape)

    enkf_state.ensemble = ensemble * cfg.enkf.inflation
    return enkf_state
