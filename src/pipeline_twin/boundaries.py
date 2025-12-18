"""Boundary actuator models for the pipeline twin."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .config import BoundaryConfig


@dataclass
class ActuatorState:
    pump: float
    valve: float


def initialize_actuators(cfg: BoundaryConfig) -> ActuatorState:
    """Create actuator states starting at zero command."""
    return ActuatorState(pump=0.0, valve=0.0)


def apply_actuator_dynamics(state: ActuatorState, pump_cmd: float, valve_cmd: float, cfg: BoundaryConfig, dt: float) -> ActuatorState:
    """First-order lag model to capture actuator latency."""
    alpha = np.exp(-dt / max(cfg.actuator_tau, 1e-3))
    state.pump += (1 - alpha) * (pump_cmd - state.pump)
    state.valve += (1 - alpha) * (valve_cmd - state.valve)
    return state


def pump_profile(t: float, cfg: BoundaryConfig) -> float:
    """Simple pump ramp profile."""
    return min(1.0, t / max(cfg.pump_ramp, 1e-6)) * cfg.pump_head


def valve_profile(t: float, cfg: BoundaryConfig) -> float:
    """Simple valve opening profile (higher means more restrictive)."""
    return min(1.0, t / max(cfg.valve_ramp, 1e-6)) * cfg.valve_setpoint
