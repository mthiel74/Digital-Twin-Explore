#!/usr/bin/env python3
import argparse
import json
import math
import os
import socket
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any

import numpy as np

from twin.filters.ekf import EKF
from twin.filters.ukf import UKF
from twin.utils.jsonl import append_jsonl

from twin.models.mass_spring_damper import MSDParams
import twin.models.mass_spring_damper as msd

from twin.models.thermal_rc import ThermalRCParams
import twin.models.thermal_rc as trc


def tcp_send_loop(host: str, port: int):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(1)
    print(f"[twin] waiting for Unity client on {host}:{port} ...")
    conn, addr = srv.accept()
    print(f"[twin] Unity connected from {addr}")
    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    return srv, conn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5555)
    ap.add_argument("--hz", type=float, default=50.0)
    ap.add_argument("--seconds", type=float, default=0.0, help="0 means run forever")
    ap.add_argument("--model", choices=["msd", "thermal"], default="msd")
    ap.add_argument("--filter", choices=["ekf", "ukf", "none"], default="ekf")
    ap.add_argument("--log", default="", help="JSONL log path, e.g. out/run.jsonl")
    ap.add_argument("--noise_y", type=float, default=0.02, help="measurement noise std")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    np.random.seed(args.seed)

    dt = 1.0 / args.hz
    t0 = time.time()

    if args.log:
        os.makedirs(os.path.dirname(args.log), exist_ok=True)
        if os.path.exists(args.log):
            os.remove(args.log)

    # Model selection
    if args.model == "msd":
        p = MSDParams()
        x_true = np.array([0.5, 0.0], dtype=float)
        u = None

        def f(x, u, t, dt):
            return msd.step(x, u, t, dt, p)

        def h(x, t):
            return msd.measure(x, t, p)

        n = 2
        m = 1
        Q = np.diag([1e-6, 1e-6])
        R = np.diag([args.noise_y**2])

        x0 = np.array([0.0, 0.0], dtype=float)
        P0 = np.diag([0.1, 0.1])

        meta = "msd"

        def pack(xhat: np.ndarray, y: np.ndarray, t: float) -> Dict[str, Any]:
            d = msd.derived(xhat, None, t, p)
            return {
                "t": float(t),
                "x1": float(d["pos"]),
                "x2": float(d["vel"]),
                "x3": float(d["acc"]),
                "y1": float(y[0]),
                "y2": 0.0,
                "meta": meta
            }

    else:  # thermal
        p = ThermalRCParams()
        x_true = np.array([20.0], dtype=float)

        def T_out_fun(t):
            # smooth outdoor temp variation (synthetic)
            return 8.0 + 4.0 * math.sin(2.0 * math.pi * t / 600.0)

        def heater_policy(t, xhat):
            # Simple setpoint tracking (open-loop / naive): heat more when below 21C
            setpoint = 21.0
            T_in = float(xhat[0])
            return np.array([1.5 if T_in < setpoint else 0.0], dtype=float)

        def f(x, u, t, dt):
            Tout = T_out_fun(t)
            return trc.step(x, u, t, dt, p, T_out=Tout)

        def h(x, t):
            return trc.measure(x, t, p)

        n = 1
        m = 1
        Q = np.diag([1e-5])
        R = np.diag([args.noise_y**2])

        x0 = np.array([19.0], dtype=float)
        P0 = np.diag([0.5])

        meta = "thermal"

        def pack(xhat: np.ndarray, y: np.ndarray, t: float) -> Dict[str, Any]:
            Tout = T_out_fun(t)
            u_now = heater_policy(t, xhat)
            d = trc.derived(xhat, u_now, t, p, T_out=Tout)
            return {
                "t": float(t),
                "x1": float(d["T_in"]),
                "x2": float(d["T_out"]),
                "x3": float(d["P_heat"]),
                "y1": float(y[0]),
                "y2": 0.0,
                "meta": meta
            }

    # Filter selection
    filt = None
    if args.filter == "ekf":
        filt = EKF(x=x0.copy(), P=P0.copy(), Q=Q, R=R, f=f, h=h)
    elif args.filter == "ukf":
        filt = UKF(x=x0.copy(), P=P0.copy(), Q=Q, R=R, f=f, h=h)

    # Start TCP server
    srv, conn = tcp_send_loop(args.host, args.port)

    # Main loop
    try:
        k = 0
        while True:
            now = time.time()
            t = now - t0
            if args.seconds > 0 and t >= args.seconds:
                break

            # Compute control (if thermal)
            if args.model == "thermal":
                if filt is None:
                    u = np.array([0.0], dtype=float)
                else:
                    # same simple policy uses estimated temperature
                    setpoint = 21.0
                    u = np.array([1.5 if float(filt.x[0]) < setpoint else 0.0], dtype=float)

            # Propagate true system
            x_true = f(x_true, u, t, dt)

            # Generate measurement
            y_true = h(x_true, t)
            y = y_true + np.random.normal(0.0, args.noise_y, size=y_true.shape)

            # Filter update
            if filt is None:
                xhat = x_true.copy()
                yhat = y_true.copy()
                r = y - yhat
            else:
                filt.predict(u=u, t=t, dt=dt)
                yhat, r = filt.update(y=y, t=t)
                xhat = filt.x.copy()

            rec = pack(xhat, y, t)
            # Add debug fields for evaluation
            rec["x_true"] = x_true.astype(float).tolist()
            rec["x_hat"] = xhat.astype(float).tolist()
            rec["y_hat"] = yhat.astype(float).tolist()
            rec["resid"] = r.astype(float).tolist()

            line = json.dumps(rec) + "\n"
            conn.sendall(line.encode("utf-8"))

            if args.log:
                append_jsonl(args.log, rec)

            k += 1
            time.sleep(dt)

    except (BrokenPipeError, ConnectionResetError):
        print("[twin] Unity disconnected.")
    finally:
        try:
            conn.close()
        except Exception:
            pass
        try:
            srv.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
