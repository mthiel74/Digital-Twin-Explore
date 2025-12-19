import numpy as np
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class ArmParams:
    l1: float = 1.0  # Length of link 1
    l2: float = 1.0  # Length of link 2
    m1: float = 1.0  # Mass of link 1
    m2: float = 1.0  # Mass of link 2
    g: float = 9.81
    # PD Controller gains
    kp: float = 50.0
    kd: float = 10.0

def _dynamics(x: np.ndarray, u: np.ndarray, p: ArmParams) -> np.ndarray:
    """Computes ddq (acceleration) given state x=[q1, q2, dq1, dq2] and torque u=[tau1, tau2]."""
    q1, q2, dq1, dq2 = x
    tau1, tau2 = u
    
    # Mass Matrix M(q)
    c2 = np.cos(q2)
    s2 = np.sin(q2)
    
    M11 = (p.m1 + p.m2) * p.l1**2 + p.m2 * p.l2**2 + 2 * p.m2 * p.l1 * p.l2 * c2
    M12 = p.m2 * p.l2**2 + p.m2 * p.l1 * p.l2 * c2
    M21 = M12
    M22 = p.m2 * p.l2**2
    
    # Coriolis/Centrifugal C(q, dq)
    h = -p.m2 * p.l1 * p.l2 * s2
    C1 = h * dq2 * (2 * dq1 + dq2)
    C2 = -h * dq1**2 # Simplified, usually h * dq1 * dq1? 
    # Standard form:
    # C11*dq1 + C12*dq2
    # C21*dq1 + C22*dq2
    # Let's stick to the resulting terms directly:
    cor1 = -p.m2 * p.l1 * p.l2 * s2 * (2 * dq1 * dq2 + dq2**2)
    cor2 = p.m2 * p.l1 * p.l2 * s2 * dq1**2
    
    # Gravity G(q)
    c1 = np.cos(q1)
    c12 = np.cos(q1 + q2)
    G1 = (p.m1 + p.m2) * p.g * p.l1 * c1 + p.m2 * p.g * p.l2 * c12 # Assuming 0 is horizontal right, y up
    G2 = p.m2 * p.g * p.l2 * c12
    
    # Solve M * ddq = u - C - G
    # M is symmetric positive definite
    M = np.array([[M11, M12], [M21, M22]])
    B = np.array([tau1 - cor1 - G1, tau2 - cor2 - G2])
    
    ddq = np.linalg.solve(M, B)
    return ddq

def step(x: np.ndarray, u: Optional[np.ndarray], t: float, dt: float, p: ArmParams) -> np.ndarray:
    """
    x: [q1, q2, dq1, dq2]
    u: [tau1, tau2] (motor torques)
    """
    if u is None:
        u = np.array([0.0, 0.0])
        
    q1, q2, dq1, dq2 = x
    
    # RK4 integration for better stability than Euler
    def dx_dt(xn):
        qn = xn[:2]
        dqn = xn[2:]
        ddqn = _dynamics(xn, u, p)
        return np.concatenate([dqn, ddqn])

    k1 = dx_dt(x)
    k2 = dx_dt(x + 0.5 * dt * k1)
    k3 = dx_dt(x + 0.5 * dt * k2)
    k4 = dx_dt(x + dt * k3)
    
    x_next = x + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
    return x_next

def measure(x: np.ndarray, t: float, p: ArmParams) -> np.ndarray:
    """Measure joint angles [q1, q2]."""
    return np.array([x[0], x[1]], dtype=float)

def derived(x: np.ndarray, u: Optional[np.ndarray], t: float, p: ArmParams) -> Dict[str, float]:
    q1, q2 = x[0], x[1]
    # Forward Kinematics for End Effector
    # Assuming q1 is angle from X-axis, q2 is relative to q1
    x_ee = p.l1 * np.cos(q1) + p.l2 * np.cos(q1 + q2)
    y_ee = p.l1 * np.sin(q1) + p.l2 * np.sin(q1 + q2)
    
    return {"q1": q1, "q2": q2, "dq1": x[2], "dq2": x[3], "ee_x": x_ee, "ee_y": y_ee}
