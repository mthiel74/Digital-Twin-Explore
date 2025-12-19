# AGENTS.md — Instructions for a coding agent (Codex / Claude)

## Goal
Turn this repository into one or more complete MSc projects in **Digital Twins**. Keep everything reproducible and CPU-first.

## Non-negotiables
- All experiments must be runnable on a laptop CPU.
- Every run writes a **log** (JSONL) plus **plots/metrics** into `python/out/`.
- The Unity demo must run by copying `unity/Scripts/` into a clean Unity project.

## Start here
1. Read `docs/TOOLS.md` and `docs/TWIN_MATH.md`.
2. Run the pipeline end-to-end:
   - `python -m twin.run_twin_stream --model msd --filter ekf --log out/test.jsonl`
   - `python -m eval.evaluate_log --log out/test.jsonl`
3. Verify Unity streaming with `unity/Scripts/TcpJsonTelemetryClient.cs`.

## Expansion tasks (pick at least 2)
### A) Add uncertainty visualization in Unity
- Add a UI canvas with text showing x1,x2,x3 and optionally +/- std.
- If you add TMPro, document it and keep it optional.

### B) Add parameter calibration
- Implement least squares calibration for `thermal_rc`:
  - Fit R and C using logged data (T_in, T_out, P_heat)
  - Output parameter CI via bootstrap or approximate covariance.

### C) Add a controller
- Implement PID or MPC-lite for `thermal_rc`:
  - Objective: track setpoint with minimal heater power.
  - Evaluate trade-off curves.

### D) Add a real sensor data adaptor
- Write `python/telemetry/serial_to_jsonl.py`:
  - Read from Arduino/ESP32 serial and convert into the same JSONL schema.
  - Allow replay mode into Unity (stream recorded JSONL).

### E) Add a second simulator backend
- Add `docs/` + minimal example for one free simulator:
  - Gazebo Sim OR Webots OR MuJoCo.
- Provide “Hello sensor” example and how to export telemetry.

## JSON schema conventions
All messages are newline-delimited JSON:
```json
{"t": 1.23, "x1": 0.1, "x2": 0.2, "x3": 0.0, "y1": 0.11, "y2": 0.0, "meta":"msd"}
```
- `x1..x3`: primary state / derived values
- `y1..y2`: raw measurements
- `meta`: model identifier (string)

## Output expectations
- A clean README for the chosen project.
- A `docs/REPORT_OUTLINE.md` describing how the student should write the thesis.
- Reproducible runs and plots.

