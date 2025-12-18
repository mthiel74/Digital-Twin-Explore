"""Metrics for evaluating the digital twin."""
from __future__ import annotations

import numpy as np


def rmse(truth: np.ndarray, estimate: np.ndarray) -> float:
    """Root mean squared error."""
    return float(np.sqrt(np.mean((truth - estimate) ** 2)))


def nll(residuals: np.ndarray, sigma: float) -> float:
    """Gaussian negative log likelihood up to constants."""
    var = max(sigma ** 2, 1e-12)
    return float(0.5 * np.sum(residuals ** 2 / var))


def detection_delay(event_index: int, alarm_index: int) -> int:
    """Detection delay in samples."""
    return max(alarm_index - event_index, 0)


def localization_accuracy(true_index: int, estimated_index: int, n_cells: int) -> float:
    """Normalized localization error in [0, 1]."""
    return 1.0 - abs(true_index - estimated_index) / max(n_cells - 1, 1)
