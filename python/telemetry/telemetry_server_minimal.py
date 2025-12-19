#!/usr/bin/env python3
import json
import socket
import time
import math

HOST = "127.0.0.1"
PORT = 5555
HZ = 50.0

def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(1)
    print(f"[server] waiting on {HOST}:{PORT}")
    conn, addr = srv.accept()
    print(f"[server] client connected: {addr}")
    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    dt = 1.0 / HZ
    t0 = time.time()
    x = 0.0
    while True:
        t = time.time() - t0
        x = math.sin(2.0 * math.pi * 0.5 * t)
        msg = {"t": t, "x1": x, "x2": 0.0, "x3": 0.0, "y1": x, "y2": 0.0, "meta": "sine"}
        conn.sendall((json.dumps(msg) + "\n").encode("utf-8"))
        time.sleep(dt)

if __name__ == "__main__":
    main()
