import argparse
import os
from dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt

try:
    from PIL import Image
except Exception:
    Image = None


@dataclass
class Meta:
    sigma_p: float
    sigma_q: float
    kb: float
    leak_on_time: float
    pump_degrade_time: float
    true_C: float
    true_R: float


def simulate_true_system(T: float, dt: float, seed: int = 0):
    rng = np.random.default_rng(seed)
    n = int(T / dt)
    t = np.arange(n) * dt

    # True parameters (unknown to estimator)
    C_true = 2.5e-3
    R_true = 8.0
    kp_true = 1.2
    kb_true = 0.08
    kl_true = 0.0

    # Fault schedule
    leak_on_time = 0.55 * T
    pump_degrade_time = 0.75 * T

    # Control input
    u = 0.7 + 0.2*np.sin(2*np.pi*t/40.0)
    u += 0.15*(t > 0.2*T) - 0.25*(t > 0.45*T) + 0.3*(t > 0.65*T)
    u = np.clip(u, 0.0, 1.2)

    p = 0.0
    p_true = np.zeros(n)
    qout_true = np.zeros(n)
    kp_series = np.zeros(n)
    kl_series = np.zeros(n)

    sigma_p = 0.03
    sigma_q = 0.02
    y_p = np.zeros(n)
    y_q = np.zeros(n)

    for k in range(n):
        if t[k] >= leak_on_time:
            kl_true = 0.18
        if t[k] >= pump_degrade_time:
            kp_true = 0.95

        qin = kp_true*u[k] - kb_true*p
        qout = p / R_true
        qleak = kl_true*np.sqrt(max(p, 0.0))

        dp = (1.0/C_true) * (qin - qout - qleak)
        p = max(0.0, p + dt*dp)

        y_p[k] = p + rng.normal(0.0, sigma_p)
        y_q[k] = qout + rng.normal(0.0, sigma_q)

        p_true[k] = p
        qout_true[k] = qout
        kp_series[k] = kp_true
        kl_series[k] = kl_true

    meta = Meta(
        sigma_p=sigma_p,
        sigma_q=sigma_q,
        kb=kb_true,
        leak_on_time=leak_on_time,
        pump_degrade_time=pump_degrade_time,
        true_C=C_true,
        true_R=R_true,
    )
    return t, u, y_p, y_q, p_true, qout_true, meta, kp_series, kl_series


def ekf_run(t, u, y_p, y_q, meta: Meta, dt: float):
    kb = meta.kb
    sigma_p = meta.sigma_p
    sigma_q = meta.sigma_q

    n = len(t)
    nx = 5

    x = np.array([max(0.0, y_p[0]), 10.0, 3.5e-3, 1.0, 0.02], dtype=float)

    P = np.diag([0.2, 8.0, 1.0e-6, 0.25, 0.08])
    Q = np.diag([2e-3, 5e-4, 1e-10, 2e-4, 5e-4])
    Rm = np.diag([sigma_p**2, sigma_q**2])

    X = np.zeros((n, nx))
    innov = np.zeros((n, 2))

    def f(xk, uk):
        p, R, C, kp, kl = xk
        R = max(1e-3, R)
        C = max(1e-6, C)
        kp = max(0.0, kp)
        kl = max(0.0, kl)

        qin = kp*uk - kb*p
        qout = p / R
        qleak = kl*np.sqrt(max(p, 0.0))
        dp = (1.0/C) * (qin - qout - qleak)
        p_next = max(0.0, p + dt*dp)
        return np.array([p_next, R, C, kp, kl], dtype=float)

    def h(xk):
        p, R, C, kp, kl = xk
        R = max(1e-3, R)
        return np.array([p, p / R], dtype=float)

    def jacobian_F(xk, uk, eps=1e-6):
        F = np.zeros((nx, nx))
        fx = f(xk, uk)
        for i in range(nx):
            dx = np.zeros(nx)
            step = eps if abs(xk[i]) < 1.0 else eps*abs(xk[i])
            dx[i] = step
            F[:, i] = (f(xk + dx, uk) - fx) / step
        return F

    def jacobian_H(xk, eps=1e-6):
        H = np.zeros((2, nx))
        hx = h(xk)
        for i in range(nx):
            dx = np.zeros(nx)
            step = eps if abs(xk[i]) < 1.0 else eps*abs(xk[i])
            dx[i] = step
            H[:, i] = (h(xk + dx) - hx) / step
        return H

    for k in range(n):
        F = jacobian_F(x, u[k])
        x_pred = f(x, u[k])
        P_pred = F @ P @ F.T + Q

        H = jacobian_H(x_pred)
        y_pred = h(x_pred)
        yk = np.array([y_p[k], y_q[k]], dtype=float)

        S = H @ P_pred @ H.T + Rm
        K = P_pred @ H.T @ np.linalg.inv(S)
        r = yk - y_pred

        x = x_pred + K @ r
        P = (np.eye(nx) - K @ H) @ P_pred

        x[0] = max(0.0, x[0])
        x[1] = max(1e-3, x[1])
        x[2] = max(1e-6, x[2])
        x[3] = max(0.0, x[3])
        x[4] = max(0.0, x[4])

        X[k] = x
        innov[k] = r

    return X, innov


def make_plots(t, u, y_p, p_true, X, meta: Meta, true_kp, true_kl, outdir=None, show=True):
    p_hat = X[:, 0]
    R_hat = X[:, 1]
    kp_hat = X[:, 3]
    kl_hat = X[:, 4]

    leak_on_time = meta.leak_on_time
    pump_deg_time = meta.pump_degrade_time

    fig = plt.figure(figsize=(12, 10))

    ax1 = plt.subplot(4, 1, 1)
    ax1.plot(t, u)
    ax1.set_ylabel("Control u")
    ax1.axvline(leak_on_time, linestyle="--")
    ax1.axvline(pump_deg_time, linestyle="--")
    ax1.set_title("Input and fault times (dashed)")

    ax2 = plt.subplot(4, 1, 2)
    ax2.plot(t, p_true, label="true p")
    ax2.plot(t, y_p, alpha=0.5, label="measured p")
    ax2.plot(t, p_hat, label="EKF p_hat")
    ax2.set_ylabel("Pressure p")
    ax2.axvline(leak_on_time, linestyle="--")
    ax2.axvline(pump_deg_time, linestyle="--")
    ax2.legend(loc="upper right")

    ax3 = plt.subplot(4, 1, 3)
    ax3.plot(t, R_hat, label="R_hat")
    ax3.plot(t, np.full_like(t, meta.true_R), linestyle="--", label="true R")
    ax3.plot(t, kp_hat, label="kp_hat")
    ax3.plot(t, true_kp, linestyle="--", label="true kp")
    ax3.plot(t, kl_hat, label="kl_hat")
    ax3.plot(t, true_kl, linestyle="--", label="true kl")
    ax3.set_ylabel("Estimated params")
    ax3.axvline(leak_on_time, linestyle="--")
    ax3.axvline(pump_deg_time, linestyle="--")
    ax3.legend(loc="upper right", ncol=3)

    # Simple visualization score
    score = np.abs(y_p - p_hat) / max(meta.sigma_p, 1e-12)

    ax4 = plt.subplot(4, 1, 4)
    ax4.plot(t, score)
    ax4.set_ylabel("Innovation proxy |y_p - p_hat|/σ_p")
    ax4.set_xlabel("Time")
    ax4.axvline(leak_on_time, linestyle="--")
    ax4.axvline(pump_deg_time, linestyle="--")
    ax4.set_title("Simple fault indication proxy")

    plt.tight_layout()

    if outdir is not None:
        os.makedirs(outdir, exist_ok=True)
        fig.savefig(os.path.join(outdir, "overview.png"), dpi=180)

        f2 = plt.figure(figsize=(12, 4))
        ax = plt.gca()
        ax.plot(t, p_true, label="true p")
        ax.plot(t, p_hat, label="p_hat")
        ax.axvline(leak_on_time, linestyle="--")
        ax.axvline(pump_deg_time, linestyle="--")
        ax.set_xlabel("Time")
        ax.set_ylabel("Pressure")
        ax.legend()
        plt.tight_layout()
        f2.savefig(os.path.join(outdir, "pressure_tracking.png"), dpi=180)
        plt.close(f2)

        f3 = plt.figure(figsize=(12, 4))
        ax = plt.gca()
        ax.plot(t, kl_hat, label="kl_hat")
        ax.plot(t, true_kl, linestyle="--", label="true kl")
        ax.axvline(leak_on_time, linestyle="--")
        ax.set_xlabel("Time")
        ax.set_ylabel("Leak coefficient")
        ax.legend()
        plt.tight_layout()
        f3.savefig(os.path.join(outdir, "leak_estimate.png"), dpi=180)
        plt.close(f3)

    if show:
        plt.show()
    else:
        plt.close(fig)


def make_gif_pressure(t, p_true, p_hat, outpath, stride=40, max_frames=200):
    if Image is None:
        raise RuntimeError("Pillow is not available. Install with: pip install pillow")

    frames = []
    fig = plt.figure(figsize=(7.5, 3.5))
    ax = plt.gca()
    ax.plot(t, p_true, label="true p")
    ax.plot(t, p_hat, label="p_hat")
    ax.set_xlabel("Time")
    ax.set_ylabel("Pressure")
    ax.legend(loc="upper right")
    ax.set_title("Pressure tracking (animated marker)")
    plt.tight_layout()

    marker_true, = ax.plot([t[0]], [p_true[0]], marker="o")
    marker_hat,  = ax.plot([t[0]], [p_hat[0]], marker="o")

    k_list = list(range(0, len(t), stride))[:max_frames]
    for k in k_list:
        marker_true.set_data([t[k]], [p_true[k]])
        marker_hat.set_data([t[k]], [p_hat[k]])
        fig.canvas.draw()
        w, h = fig.canvas.get_width_height()
        img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8).reshape(h, w, 3)
        frames.append(Image.fromarray(img))

    plt.close(fig)
    frames[0].save(outpath, save_all=True, append_images=frames[1:], duration=70, loop=0)


def main():
    ap = argparse.ArgumentParser(description="Laptop-scale digital twin demo: pump + pipeline + leak, EKF estimation.")
    ap.add_argument("--T", type=float, default=2000.0)
    ap.add_argument("--dt", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=2)
    ap.add_argument("--save-plots", action="store_true")
    ap.add_argument("--make-gif", action="store_true", help="Also create a small GIF (requires pillow).")
    ap.add_argument("--outdir", type=str, default="outputs")
    ap.add_argument("--no-show", action="store_true")
    args = ap.parse_args()

    t, u, y_p, y_q, p_true, qout_true, meta, true_kp, true_kl = simulate_true_system(T=args.T, dt=args.dt, seed=args.seed)
    X, innov = ekf_run(t, u, y_p, y_q, meta, dt=args.dt)

    show = not args.no_show
    outdir = args.outdir if args.save_plots else None
    make_plots(t, u, y_p, p_true, X, meta, true_kp, true_kl, outdir=outdir, show=show)

    if args.save_plots and args.make_gif and Image is not None:
        p_hat = X[:, 0]
        os.makedirs(args.outdir, exist_ok=True)
        gif_path = os.path.join(args.outdir, "pressure_tracking.gif")
        make_gif_pressure(t, p_true, p_hat, gif_path)
        print(f"Saved GIF: {gif_path}")


if __name__ == "__main__":
    main()
