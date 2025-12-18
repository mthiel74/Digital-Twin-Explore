"""Plotting utilities for the pipeline twin."""
from __future__ import annotations

import os
import matplotlib.pyplot as plt
import numpy as np


def plot_pressure_heatmap(time: np.ndarray, pressure: np.ndarray, outdir: str, ext: str = "png") -> str:
    """Save a pressure heatmap to the outputs directory."""
    os.makedirs(outdir, exist_ok=True)
    plt.style.use("seaborn-v0_8")
    fig, ax = plt.subplots(figsize=(10, 4))
    im = ax.imshow(
        pressure.T,
        aspect="auto",
        origin="lower",
        extent=[time[0], time[-1], 0, pressure.shape[1]],
        cmap="viridis",
    )
    ax.set_xlabel("Time")
    ax.set_ylabel("Cell index")
    ax.set_title("Pressure heatmap")
    fig.colorbar(im, ax=ax, label="Pressure")
    path = os.path.join(outdir, f"pressure_heatmap.{ext}")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_residuals(time: np.ndarray, residuals: np.ndarray, outdir: str, ext: str = "png") -> str:
    """Save residual diagnostics plot."""
    os.makedirs(outdir, exist_ok=True)
    plt.style.use("seaborn-v0_8")
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(time, residuals, color="#b23b3b", linewidth=1.8)
    ax.set_xlabel("Time")
    ax.set_ylabel("Residual")
    ax.set_title("Innovation magnitude")
    path = os.path.join(outdir, f"residuals.{ext}")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_boundary_commands(time: np.ndarray, commands: np.ndarray, outdir: str, ext: str = "png") -> str:
    """Plot pump and valve commands over time."""
    os.makedirs(outdir, exist_ok=True)
    plt.style.use("seaborn-v0_8")
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(time, commands[:, 0], label="Pump command", color="#0b6fa4", linewidth=2.0)
    ax.plot(time, commands[:, 1], label="Valve command", color="#d48b1a", linewidth=2.0)
    ax.set_xlabel("Time")
    ax.set_ylabel("Command")
    ax.legend()
    ax.set_title("Boundary actuation profiles")
    path = os.path.join(outdir, f"boundary_commands.{ext}")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def plot_flow_heatmap(time: np.ndarray, flow: np.ndarray, outdir: str, ext: str = "png") -> str:
    """Save a flow heatmap to the outputs directory."""
    os.makedirs(outdir, exist_ok=True)
    plt.style.use("seaborn-v0_8")
    fig, ax = plt.subplots(figsize=(10, 4))
    im = ax.imshow(
        flow.T,
        aspect="auto",
        origin="lower",
        extent=[time[0], time[-1], 0, flow.shape[1]],
        cmap="coolwarm",
    )
    ax.set_xlabel("Time")
    ax.set_ylabel("Flow segment index")
    ax.set_title("Flow heatmap")
    fig.colorbar(im, ax=ax, label="Flow")
    path = os.path.join(outdir, f"flow_heatmap.{ext}")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_pressure_sections(time: np.ndarray, pressure_truth: np.ndarray, measurements: np.ndarray, outdir: str, ext: str = "png") -> str:
    """Plot pressure at inlet, mid, and outlet with measurements."""
    os.makedirs(outdir, exist_ok=True)
    plt.style.use("seaborn-v0_8")
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    labels = ["Inlet (cell 0)", "Mid (cell N/2)", "Outlet (cell N-1)"]
    indices = [0, pressure_truth.shape[1] // 2, pressure_truth.shape[1] - 1]
    colors = ["#0b6fa4", "#009e73", "#b23b3b"]

    for ax, idx, label, color in zip(axes, indices, labels, colors):
        ax.plot(time, pressure_truth[:, idx], label=f"Pressure true @ {label}", color=color, linewidth=2.0)
        if measurements.size > 0:
            ax.scatter(time, measurements[:, idx], s=8, color="black", alpha=0.25, label="Pressure meas")
        ax.set_ylabel("Pressure")
        ax.legend(loc="upper right")
        ax.grid(True, alpha=0.2)
    axes[-1].set_xlabel("Time")
    fig.suptitle("Pressure sections with measurements", y=0.95)
    path = os.path.join(outdir, f"pressure_sections.{ext}")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def plot_leak_scores(scores: dict[int, float], outdir: str, ext: str = "png") -> str:
    """Bar plot of leak hypothesis scores."""
    os.makedirs(outdir, exist_ok=True)
    plt.style.use("seaborn-v0_8")
    fig, ax = plt.subplots(figsize=(8, 4))
    items = sorted(scores.items())
    locations = [k for k, _ in items]
    values = [v for _, v in items]
    bars = ax.bar(locations, values, color="#4c72b0", alpha=0.85)
    best_idx = int(locations[int(np.argmin(values))])
    for bar, loc in zip(bars, locations):
        if loc == best_idx:
            bar.set_color("#2ca02c")
    ax.set_xlabel("Leak index hypothesis")
    ax.set_ylabel("Score (lower is better)")
    ax.set_title("Leak localization scores")
    path = os.path.join(outdir, f"leak_scores.{ext}")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path
