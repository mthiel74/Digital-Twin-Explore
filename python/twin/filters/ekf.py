import numpy as np
from dataclasses import dataclass
from typing import Callable, Optional, Tuple
from .utils.numerics import numerical_jacobian

@dataclass
class EKF:
    """Extended Kalman Filter for discrete-time models.

    Model:
        x_{k+1} = f(x_k, u_k, t_k) + w_k,  w ~ N(0, Q)
        y_k     = h(x_k, t_k) + v_k,      v ~ N(0, R)

    f: (x,u,t,dt) -> x_next
    h: (x,t) -> y
    """
    x: np.ndarray
    P: np.ndarray
    Q: np.ndarray
    R: np.ndarray
    f: Callable[[np.ndarray, Optional[np.ndarray], float, float], np.ndarray]
    h: Callable[[np.ndarray, float], np.ndarray]
    jac_eps: float = 1e-6

    def predict(self, u: Optional[np.ndarray], t: float, dt: float) -> None:
        x0 = self.x.copy()

        def fx(xx):
            return self.f(xx, u, t, dt)

        F = numerical_jacobian(fx, x0, eps=self.jac_eps)
        self.x = fx(x0)
        self.P = F @ self.P @ F.T + self.Q

    def update(self, y: np.ndarray, t: float) -> Tuple[np.ndarray, np.ndarray]:
        y = np.asarray(y, dtype=float)

        def hx(xx):
            return self.h(xx, t)

        H = numerical_jacobian(hx, self.x, eps=self.jac_eps)
        yhat = hx(self.x)
        r = y - yhat

        S = H @ self.P @ H.T + self.R
        K = self.P @ H.T @ np.linalg.inv(S)

        self.x = self.x + K @ r
        I = np.eye(self.P.shape[0])
        self.P = (I - K @ H) @ self.P @ (I - K @ H).T + K @ self.R @ K.T  # Joseph form

        return yhat, r

