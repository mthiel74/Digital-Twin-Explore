"""Leak model utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import numpy as np

from .config import LeakConfig


@dataclass
class LeakState:
    active: bool
    index: Optional[int]


def initialize_leak(cfg: LeakConfig, n_cells: int) -> LeakState:
    """Initialize leak activation flags."""
    index = cfg.index if cfg.index is not None else n_cells // 2
    return LeakState(active=False, index=index)


def apply_leak(state, cfg: LeakConfig, pressures: np.ndarray, dt: float, time: float | None = None) -> np.ndarray:
    """Compute leak withdrawal using a square-root orifice model."""
    withdrawal = np.zeros_like(pressures)
    if state.index is None:
        return withdrawal
    if cfg.start_time is not None and time is not None and time < cfg.start_time:
        return withdrawal
    coeff = max(cfg.coefficient, 0.0)
    withdrawal[state.index] = 5.0 * coeff * np.sqrt(max(pressures[state.index], 0.0)) * dt
    return withdrawal
