"""Sensor simulation with noise, bias, and latency."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import numpy as np

from .config import SensorConfig


@dataclass
class SensorState:
    pressure_bias: float = 0.0
    flow_bias: float = 0.0


class LatencyBuffer:
    """Fixed-latency buffer for sensor readings."""

    def __init__(self, latency_steps: int):
        self.latency_steps = latency_steps
        self.buffer = deque(maxlen=latency_steps + 1)

    def push(self, value):
        self.buffer.append(value)
        if len(self.buffer) <= self.latency_steps:
            return value
        return self.buffer[0]


def sample_sensors(pressure: np.ndarray, flow: np.ndarray, cfg: SensorConfig, state: SensorState, step_index: int, buffers: dict[str, LatencyBuffer], rng: np.random.Generator) -> dict:
    """Return noisy, biased, and latency-affected measurements."""
    if "pressure" not in buffers:
        buffers["pressure"] = LatencyBuffer(cfg.latency_steps)
    if "flow" not in buffers:
        buffers["flow"] = LatencyBuffer(cfg.latency_steps)

    state.pressure_bias += cfg.pressure_bias_drift
    state.flow_bias += cfg.flow_bias_drift

    if step_index % max(cfg.sample_every, 1) != 0:
        return {}

    p_meas = pressure + state.pressure_bias + rng.normal(0.0, cfg.pressure_noise, size=pressure.shape)
    f_meas = flow + state.flow_bias + rng.normal(0.0, cfg.flow_noise, size=flow.shape)

    p_meas = buffers["pressure"].push(p_meas)
    f_meas = buffers["flow"].push(f_meas)
    return {"pressure": p_meas, "flow": f_meas}
