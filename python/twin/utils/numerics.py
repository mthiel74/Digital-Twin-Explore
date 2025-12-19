import numpy as np
from typing import Callable

def numerical_jacobian(f: Callable[[np.ndarray], np.ndarray], x: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    """Central-difference Jacobian of vector function f at x."""
    x = np.asarray(x, dtype=float)
    y0 = np.asarray(f(x), dtype=float)
    n = x.size
    m = y0.size
    J = np.zeros((m, n), dtype=float)
    for i in range(n):
        dx = np.zeros(n, dtype=float)
        dx[i] = eps
        y_plus = np.asarray(f(x + dx), dtype=float)
        y_minus = np.asarray(f(x - dx), dtype=float)
        J[:, i] = (y_plus - y_minus) / (2.0 * eps)
    return J
