"""Simplified 1D transient pipeline physics.

The implementation favors determinism and speed over fidelity while preserving
key behaviors (wave propagation, frictional damping) that are sufficient for
algorithm prototyping on a laptop.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .config import DomainConfig


@dataclass
class PipelineState:
    pressure: np.ndarray
    flow: np.ndarray
    friction_scale: float = 1.0
    pump_gain: float = 1.0


@dataclass
class BoundaryInputs:
    pump_command: float
    valve_command: float


def initialize_state(cfg: DomainConfig) -> PipelineState:
    """Create a zeroed pipeline state consistent with the discretization."""
    pressure = np.zeros(cfg.n_cells, dtype=float)
    flow = np.zeros(cfg.n_cells - 1, dtype=float)
    return PipelineState(pressure=pressure, flow=flow)


def step(state: PipelineState, inputs: BoundaryInputs, cfg: DomainConfig) -> PipelineState:
    """Advance the pipeline state one step using a linearized transient update.

    The scheme updates flow from pressure gradients and friction, then updates
    cell pressures from flow divergence. It is unconditionally deterministic and
    uses clipping to avoid numerical artifacts in small-scale demos.
    """
    p = state.pressure.copy()
    q = state.flow.copy()

    dx = cfg.length / (cfg.n_cells - 1)
    c = cfg.wave_speed
    f = cfg.friction * max(state.friction_scale, 1e-3)

    dp_dx = np.diff(p) / dx
    dt_eff = min(cfg.dt, 0.25 * dx / max(c, 1e-6))
    q += dt_eff * (-(c**2) * dp_dx - f * q)
    q = np.nan_to_num(q, nan=0.0, posinf=0.0, neginf=0.0)

    q[0] += cfg.dt * inputs.pump_command * state.pump_gain
    q[-1] -= cfg.dt * inputs.valve_command

    dq_dx = np.concatenate(([q[0]], np.diff(q), [-q[-1]])) / dx
    p += dt_eff * (-dq_dx)
    p = np.clip(p, 0.0, None)
    p = np.nan_to_num(p, nan=0.0, posinf=0.0, neginf=0.0)

    return PipelineState(pressure=p, flow=q, friction_scale=state.friction_scale, pump_gain=state.pump_gain)
