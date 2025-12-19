# Unity setup (minimal)

Goal: a clean Unity project that visualizes a streaming digital twin.

## Steps
1. Create a new Unity 3D project.
2. Copy the folder `Scripts/` into `Assets/Scripts/`.
3. Create an empty GameObject named `TelemetryClient`.
4. Add component `TcpJsonTelemetryClient`.
5. Create a Cube (or any object).
6. Drag the Cube into the `target` field.
7. Set `host=127.0.0.1`, `port=5555` (defaults).
8. Press Play.

## Python side
From the repo root:
```bash
cd python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m twin.run_twin_stream --model msd --filter ekf --port 5555
```

## JSON schema
Unity expects newline-delimited JSON objects with fields:
- `t` (float)
- `x1,x2,x3` (float)
- `y1,y2` (float)
- `meta` (string)

Example:
```json
{"t":0.12,"x1":0.1,"x2":0.0,"x3":0.0,"y1":0.1,"y2":0.0,"meta":"msd"}
```
