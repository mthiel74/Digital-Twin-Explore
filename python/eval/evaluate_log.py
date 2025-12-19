#!/usr/bin/env python3
import argparse
import json
import numpy as np
import matplotlib.pyplot as plt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True, help="JSONL log from run_twin_stream.py")
    ap.add_argument("--out_prefix", default="", help="If set, write plots to out_prefix_*.png")
    args = ap.parse_args()

    t = []
    x1 = []
    y1 = []
    x_true0 = []
    x_hat0 = []

    with open(args.log, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            t.append(obj["t"])
            x1.append(obj.get("x1", 0.0))
            y1.append(obj.get("y1", 0.0))
            xt = obj.get("x_true", None)
            xh = obj.get("x_hat", None)
            if isinstance(xt, list) and len(xt) > 0:
                x_true0.append(float(xt[0]))
            if isinstance(xh, list) and len(xh) > 0:
                x_hat0.append(float(xh[0]))

    t = np.array(t)
    x1 = np.array(x1)
    y1 = np.array(y1)
    x_true0 = np.array(x_true0) if len(x_true0) else None
    x_hat0 = np.array(x_hat0) if len(x_hat0) else None

    if x_true0 is not None and x_hat0 is not None and len(x_true0) == len(x_hat0):
        rmse = np.sqrt(np.mean((x_true0 - x_hat0)**2))
        print(f"RMSE(state[0] true vs hat): {rmse:.6f}")
    else:
        print("No x_true/x_hat fields found for RMSE.")

    plt.figure()
    plt.plot(t, y1, label="measurement y1")
    plt.plot(t, x1, label="reported x1")
    if x_true0 is not None:
        plt.plot(t[:len(x_true0)], x_true0, label="x_true[0]")
    if x_hat0 is not None:
        plt.plot(t[:len(x_hat0)], x_hat0, label="x_hat[0]")
    plt.xlabel("t [s]")
    plt.legend()
    plt.title("Digital twin traces")
    plt.tight_layout()

    if args.out_prefix:
        out = f"{args.out_prefix}_traces.png"
        plt.savefig(out, dpi=200)
        print(f"Wrote {out}")
    else:
        plt.show()

if __name__ == "__main__":
    main()
