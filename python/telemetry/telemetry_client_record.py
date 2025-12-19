#!/usr/bin/env python3
import argparse
import json
import os
import socket
from typing import Optional

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5555)
    ap.add_argument("--out", required=True, help="Output JSONL file")
    ap.add_argument("--max_lines", type=int, default=0, help="0 means unlimited")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((args.host, args.port))
    buf = ""
    n_lines = 0
    with open(args.out, "w", encoding="utf-8") as f:
        while True:
            chunk = s.recv(8192)
            if not chunk:
                break
            buf += chunk.decode("utf-8", errors="ignore")
            while True:
                idx = buf.find("\n")
                if idx < 0:
                    break
                line = buf[:idx].strip()
                buf = buf[idx+1:]
                if not line:
                    continue
                # validate JSON
                obj = json.loads(line)
                f.write(json.dumps(obj) + "\n")
                n_lines += 1
                if args.max_lines > 0 and n_lines >= args.max_lines:
                    s.close()
                    return

if __name__ == "__main__":
    main()
