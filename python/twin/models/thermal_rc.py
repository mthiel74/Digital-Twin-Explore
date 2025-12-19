import numpy as np
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class ThermalRCParams:
    """1R1C thermal model.

    State: x = [T_in]
    Input: u = [P_heat]   (heater power in arbitrary units)
    Disturbance: T_out(t) is provided by a function (see run script).
    Dynamics:
        C dT/dt = (T_out - T_in)/R + eta * P_heat + q_int
    """
    R: float = 2.0      # thermal resistance (K / power-unit)
    C: float = 8.0      # thermal capacitance (power-unit * s / K)
    eta: float = 0.9    # heater gain
    q_int: float = 0.0  # internal heat gains (power-unit)

def step(x: np.ndarray, u: Optional[np.ndarray], t: float, dt: float, p: ThermalRCParams, T_out: float) -> np.ndarray:
    T_in = float(x[0])
    P_heat = float(u[0]) if u is not None else 0.0
    dTdt = ((T_out - T_in) / p.R + p.eta * P_heat + p.q_int) / p.C
    T_in = T_in + dTdt * dt
    return np.array([T_in], dtype=float)

def measure(x: np.ndarray, t: float, p: ThermalRCParams) -> np.ndarray:
    """Measurement: indoor temperature only."""
    return np.array([float(x[0])], dtype=float)

def derived(x: np.ndarray, u: Optional[np.ndarray], t: float, p: ThermalRCParams, T_out: float) -> Dict[str, float]:
    T_in = float(x[0])
    P_heat = float(u[0]) if u is not None else 0.0
    return {"T_in": T_in, "T_out": float(T_out), "P_heat": P_heat}
