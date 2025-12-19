import numpy as np
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class MSDParams:
    m: float = 1.0
    k: float = 2.0
    c: float = 0.25
    drive: float = 0.8
    w: float = 1.2

def step(x: np.ndarray, u: Optional[np.ndarray], t: float, dt: float, p: MSDParams) -> np.ndarray:
    """State x=[pos, vel]. Forcing = drive*sin(w*t). Semi-implicit Euler."""
    pos, vel = float(x[0]), float(x[1])
    force = p.drive * np.sin(p.w * t)
    acc = (force - p.c * vel - p.k * pos) / p.m
    vel = vel + acc * dt
    pos = pos + vel * dt
    return np.array([pos, vel], dtype=float)

def measure(x: np.ndarray, t: float, p: MSDParams) -> np.ndarray:
    """Measurement: displacement only."""
    return np.array([float(x[0])], dtype=float)

def derived(x: np.ndarray, u: Optional[np.ndarray], t: float, p: MSDParams) -> Dict[str, float]:
    pos, vel = float(x[0]), float(x[1])
    force = p.drive * np.sin(p.w * t)
    acc = (force - p.c * vel - p.k * pos) / p.m
    return {"pos": pos, "vel": vel, "acc": acc}
