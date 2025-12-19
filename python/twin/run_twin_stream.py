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

from twin.models.robot_arm import ArmParams
import twin.models.robot_arm as arm


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
    ap.add_argument("--model", choices=["msd", "thermal", "arm"], default="msd")
    ap.add_argument("--filter", choices=["ekf", "ukf", "none"], default="ekf")
    ap.add_argument("--log", default="", help="JSONL log path, e.g. out/run.jsonl")
    ap.add_argument("--noise_y", type=float, default=0.02, help="measurement noise std")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--headless", action="store_true", help="Run without TCP client (simulation only)")
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
                "joints": [],
                "meta": meta
            }

    elif args.model == "arm":
        p = ArmParams()
        # Initial state: Hanging down? Or horizontal?
        x_true = np.array([0.0, 0.0, 0.0, 0.0], dtype=float) 
        
        def controller(t, x):
            # Target: Draw a circle? Or just wave.
            # q1_des = sin(t), q2_des = cos(t)
            q1_des = 0.5 * math.sin(t) + math.pi/2 # Uprightish
            q2_des = 1.0 * math.sin(2*t)
            
            q_des = np.array([q1_des, q2_des])
            dq_des = np.array([0.5*math.cos(t), 2.0*math.cos(2*t)]) # Approx feedforward
            
            q = x[:2]
            dq = x[2:]
            
            # PD Control
            tau = p.kp * (q_des - q) + p.kd * (dq_des - dq)
            return tau

        def f(x, u, t, dt):
            # u is computed externally usually, but here we can wrap it if needed.
            # However, for EKF, 'u' is input.
            # For simulation, we compute u based on True State.
            # For Filter, we usually assume we KNOW u (applied torque).
            return arm.step(x, u, t, dt, p)

        def h(x, t):
            return arm.measure(x, t, p)

        n = 4
        m = 2
        Q = np.diag([1e-5, 1e-5, 1e-4, 1e-4]) # Process noise
        R = np.diag([args.noise_y**2, args.noise_y**2])

        x0 = np.array([0.1, 0.1, 0.0, 0.0], dtype=float) # Slight offset
        P0 = np.eye(4) * 0.1

        meta = "arm"

        def pack(xhat: np.ndarray, y: np.ndarray, t: float) -> Dict[str, Any]:
            # Recalculate u for derived info? Or just pass what we have.
            # We'll calculate derived stats from xhat
            d = arm.derived(xhat, None, t, p)
            
            # Simple Gripper Logic for Demo: Open/Close every few seconds
            # Period = 4pi (approx 12s). 
            # 0..1 range.
            grip = 1.0 if math.sin(0.5 * t) > 0.5 else 0.0
            
            return {
                "t": float(t),
                "x1": float(d["ee_x"]), # End effector X
                "x2": float(d["ee_y"]), # End effector Y
                "x3": 0.0,
                "y1": float(y[0]), # Measured q1
                "y2": float(y[1]), # Measured q2
                "joints": [float(d["q1"]), float(d["q2"])],
                "gripper": float(grip),
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
                "joints": [],
                "meta": meta
            }


    # Filter selection
    filt = None
    if args.filter == "ekf":
        filt = EKF(x=x0.copy(), P=P0.copy(), Q=Q, R=R, f=f, h=h)
    elif args.filter == "ukf":
        filt = UKF(x=x0.copy(), P=P0.copy(), Q=Q, R=R, f=f, h=h)

    # Start TCP server
    srv = None
    conn = None
    if not args.headless:
        srv, conn = tcp_send_loop(args.host, args.port)
    else:
        print("[twin] Running in headless mode (no TCP server)")

    # Main loop
    try:
        k = 0
        while True:
            now = time.time()
            t = now - t0
            if args.seconds > 0 and t >= args.seconds:
                break

            # Compute control
            if args.model == "thermal":
                if filt is None:
                    u = np.array([0.0], dtype=float)
                else:
                    setpoint = 21.0
                    u = np.array([1.5 if float(filt.x[0]) < setpoint else 0.0], dtype=float)
            elif args.model == "arm":
                # Simple tracking controller using TRUE state for simulation physics
                # In a real twin, this would be the actual control signal sent to the robot
                # For the "Twin" prediction step (filt.predict), we pass this known 'u'.
                
                # Re-define controller logic here or use function
                q1_des = 0.5 * math.sin(t) + math.pi/2
                q2_des = 1.0 * math.sin(2*t)
                q_des = np.array([q1_des, q2_des])
                dq_des = np.array([0.5*math.cos(t), 2.0*math.cos(2*t)])
                
                q = x_true[:2]
                dq = x_true[2:]
                
                # Gains hardcoded in param p, but we need 'p' here.
                # 'p' is available from the scope above.
                tau = p.kp * (q_des - q) + p.kd * (dq_des - dq)
                u = tau

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
                unc = 0.0
            else:
                filt.predict(u=u, t=t, dt=dt)
                yhat, r = filt.update(y=y, t=t)
                xhat = filt.x.copy()
                unc = np.trace(filt.P)

            rec = pack(xhat, y, t)
            rec["unc"] = float(unc)
            # Add debug fields for evaluation
            rec["x_true"] = x_true.astype(float).tolist()
            rec["x_hat"] = xhat.astype(float).tolist()
            rec["y_hat"] = yhat.astype(float).tolist()
            rec["resid"] = r.astype(float).tolist()

            line = json.dumps(rec) + "\n"
            if conn:
                conn.sendall(line.encode("utf-8"))

            if args.log:
                append_jsonl(args.log, rec)

            k += 1
            time.sleep(dt)

    except (BrokenPipeError, ConnectionResetError):
        print("[twin] Unity disconnected.")
    except KeyboardInterrupt:
        print("[twin] Interrupted by user.")
    finally:
        try:
            if conn: conn.close()
        except Exception:
            pass
        try:
            if srv: srv.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
