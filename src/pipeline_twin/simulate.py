"""Synthetic data generation for the pipeline twin."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import numpy as np

from .boundaries import ActuatorState, apply_actuator_dynamics, pump_profile, valve_profile
from .config import TwinConfig
from .leak import initialize_leak, apply_leak
from .physics import BoundaryInputs, PipelineState, initialize_state, step
from .sensors import SensorConfig, SensorState, sample_sensors


@dataclass
class SimulationResult:
    time: np.ndarray
    states: List[PipelineState]
    measurements: List[Dict]
    commands: List[BoundaryInputs]


def run_simulation(cfg: TwinConfig) -> SimulationResult:
    """Run a deterministic simulation and return trajectories."""
    domain = cfg.domain
    n_steps = int(domain.total_time / domain.dt)
    times = np.arange(n_steps) * domain.dt

    state = initialize_state(domain)
    leak_state = initialize_leak(cfg.leak, domain.n_cells)
    actuator = ActuatorState(pump=0.0, valve=0.0)
    sensor_state = SensorState()
    rng = np.random.default_rng(cfg.sensors.seed)

    states: List[PipelineState] = []
    meas: List[Dict] = []
    commands: List[BoundaryInputs] = []

    buffers = {}
    for k, t in enumerate(times):
        pump_cmd = pump_profile(t, cfg.boundaries)
        valve_cmd = valve_profile(t, cfg.boundaries)
        actuator = apply_actuator_dynamics(actuator, pump_cmd, valve_cmd, cfg.boundaries, dt=domain.dt)
        inputs = BoundaryInputs(pump_command=actuator.pump, valve_command=actuator.valve)

        leak_draw = apply_leak(leak_state, cfg.leak, state.pressure, domain.dt, time=t)
        state = step(state, inputs, domain)
        state.pressure -= leak_draw
        state.pressure = np.clip(state.pressure, 0.0, None)

        measurements = sample_sensors(state.pressure, state.flow, cfg.sensors, sensor_state, step_index=k, buffers=buffers, rng=rng)

        states.append(state)
        meas.append(measurements)
        commands.append(inputs)

    return SimulationResult(time=times, states=states, measurements=meas, commands=commands)
