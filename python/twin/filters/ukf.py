import numpy as np
from dataclasses import dataclass
from typing import Callable, Optional, Tuple

def _sigma_points(x: np.ndarray, P: np.ndarray, alpha: float, beta: float, kappa: float):
    n = x.size
    lam = alpha**2 * (n + kappa) - n
    S = np.linalg.cholesky((n + lam) * P)
    X = np.zeros((2*n + 1, n), dtype=float)
    X[0] = x
    for i in range(n):
        X[i+1]     = x + S[:, i]
        X[i+1+n]   = x - S[:, i]

    Wm = np.full(2*n + 1, 1.0 / (2*(n + lam)), dtype=float)
    Wc = np.full(2*n + 1, 1.0 / (2*(n + lam)), dtype=float)
    Wm[0] = lam / (n + lam)
    Wc[0] = lam / (n + lam) + (1 - alpha**2 + beta)
    return X, Wm, Wc

@dataclass
class UKF:
    """Unscented Kalman Filter (discrete-time).

    x_{k+1} = f(x_k, u_k, t_k, dt) + w_k, w ~ N(0,Q)
    y_k     = h(x_k, t_k) + v_k,       v ~ N(0,R)
    """
    x: np.ndarray
    P: np.ndarray
    Q: np.ndarray
    R: np.ndarray
    f: Callable[[np.ndarray, Optional[np.ndarray], float, float], np.ndarray]
    h: Callable[[np.ndarray, float], np.ndarray]
    alpha: float = 1e-3
    beta: float = 2.0
    kappa: float = 0.0

    def predict(self, u: Optional[np.ndarray], t: float, dt: float) -> None:
        X, Wm, Wc = _sigma_points(self.x, self.P, self.alpha, self.beta, self.kappa)
        Xp = np.array([self.f(xi, u, t, dt) for xi in X], dtype=float)
        x_pred = np.sum(Wm[:, None] * Xp, axis=0)

        P_pred = self.Q.copy()
        for i in range(Xp.shape[0]):
            dx = (Xp[i] - x_pred).reshape(-1, 1)
            P_pred += Wc[i] * (dx @ dx.T)

        self.x = x_pred
        self.P = P_pred

    def update(self, y: np.ndarray, t: float) -> Tuple[np.ndarray, np.ndarray]:
        y = np.asarray(y, dtype=float)

        X, Wm, Wc = _sigma_points(self.x, self.P, self.alpha, self.beta, self.kappa)
        Y = np.array([self.h(xi, t) for xi in X], dtype=float)
        y_pred = np.sum(Wm[:, None] * Y, axis=0)

        Pyy = self.R.copy()
        Pxy = np.zeros((self.x.size, y.size), dtype=float)

        for i in range(Y.shape[0]):
            dy = (Y[i] - y_pred).reshape(-1, 1)
            dx = (X[i] - self.x).reshape(-1, 1)
            Pyy += Wc[i] * (dy @ dy.T)
            Pxy += Wc[i] * (dx @ dy.T)

        K = Pxy @ np.linalg.inv(Pyy)
        r = y - y_pred
        self.x = self.x + K @ r
        self.P = self.P - K @ Pyy @ K.T
        return y_pred, r
