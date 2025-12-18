"""Plotting utilities for the pipeline twin."""
from __future__ import annotations

import os
import matplotlib.pyplot as plt
import numpy as np


def plot_pressure_heatmap(time: np.ndarray, pressure: np.ndarray, outdir: str) -> str:
    """Save a pressure heatmap to the outputs directory."""
    os.makedirs(outdir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    im = ax.imshow(pressure.T, aspect="auto", origin="lower", extent=[time[0], time[-1], 0, pressure.shape[1]])
    ax.set_xlabel("Time")
    ax.set_ylabel("Cell index")
    ax.set_title("Pressure heatmap")
    fig.colorbar(im, ax=ax, label="Pressure")
    path = os.path.join(outdir, "pressure_heatmap.png")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_residuals(time: np.ndarray, residuals: np.ndarray, outdir: str) -> str:
    """Save residual diagnostics plot."""
    os.makedirs(outdir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(time, residuals)
    ax.set_xlabel("Time")
    ax.set_ylabel("Residual")
    ax.set_title("Innovation magnitude")
    path = os.path.join(outdir, "residuals.png")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path
