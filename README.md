# Digital Twin Starter Kit (CPU-first, laptop friendly)

This repository is a **starter kit** for MSc Data Science projects in **Digital Twins** under realistic constraints:
- **No advanced GPU required**
- Works on a **laptop** (CPU-first)
- Supports **simulator-first** workflows and **real sensor** integration
- Designed so a coding agent (Codex / Claude) can extend it into a full MSc project repo

> A digital twin here means: a computational model that is **synchronized** to an asset (real or simulated) via data,
> performs **state estimation + parameter calibration**, and supports **prediction / what-if / decision-making**.

## What’s included

### 1) A minimal “twin telemetry spine” (Python → Unity via TCP/JSON)
- Python runs a dynamical system (example models included) and streams newline-delimited JSON over TCP.
- Unity receives the stream and updates a GameObject in real time.

Files:
- `python/twin/run_twin_stream.py`  (streams state + measurements)
- `unity/Scripts/TcpJsonTelemetryClient.cs`  (Unity receiver)

### 2) Twin models (examples)
- `python/twin/models/mass_spring_damper.py`  
- `python/twin/models/thermal_rc.py`  (room/house thermal 1R1C)

### 3) Filters / state estimation
- `python/twin/filters/ekf.py`  (Extended Kalman Filter with numerical Jacobians)
- `python/twin/filters/ukf.py`  (Unscented Kalman Filter)

### 4) Evaluation hooks
- `python/eval/evaluate_log.py` computes basic RMSE and plots traces from recorded runs.
- `python/telemetry/telemetry_client_record.py` records the JSON stream into CSV/JSONL.

### 5) Tool landscape notes (Unity, Gazebo, Webots, MuJoCo, ROS 2)
- `docs/TOOLS.md` provides a practical tool matrix and recommendations.

---

## Quick start

### Prereqs
- Python 3.10+
- Unity (any recent LTS is fine; URP optional)
- (Optional) VS Code

### Python environment
```bash
cd python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run the twin stream (no Unity needed yet)
```bash
python -m twin.run_twin_stream --model msd --filter ekf --port 5555 --hz 50 --log out/msd_run.jsonl
```

### Unity setup (minimal)
1. Create a new Unity 3D project.
2. Copy `unity/Scripts/` into `Assets/Scripts/`.
3. Create a Cube.
4. Add the `TcpJsonTelemetryClient` component to an empty GameObject.
5. Drag the Cube into the `target` field.
6. Press Play (Unity) after starting the Python streamer.

See: `unity/README_Unity_Setup.md`

### Headless Mode (No Unity)
To run the simulation and logging without a Unity connection:
```bash
python -m twin.run_twin_stream --headless --seconds 10 --log out/run.jsonl
```

### 3D Animation (Python)
To generate a 3D animation (GIF) from a recorded log:
```bash
python -m eval.animate_msd --log out/run.jsonl --out out/animation.gif
```

---

## Core project patterns (choose one)

### Pattern A — “State-estimation twin”
- Define a dynamical model.
- Define a measurement model (noisy sensors).
- Run EKF/UKF to estimate hidden state.
- Visualize estimated state and uncertainty.

### Pattern B — “Hybrid physics + ML residual”
Model:
\[
x_{k+1} = f(x_k, u_k; \theta) + \Delta f_\phi(x_k,u_k)
\]
- Start with a physics model.
- Learn a small residual model \(\Delta f_\phi\) on CPU (tiny MLP / ridge / kernel).
- Validate generalization and failure modes.

### Pattern C — “Calibration/identifiability twin”
- Simulate data with unknown \(\theta\).
- Fit \(\hat\theta\) by optimization (least squares, CMA-ES, Bayesian optimization).
- Quantify identifiability and confidence intervals.

### Pattern D — “Twin + decision”
- Add a controller / policy (PID, MPC-lite).
- Optimize a cost (comfort vs energy; tracking vs actuation).

---

## Recommended tool choices

### When Unity is a good choice
Use Unity when you want:
- A polished **interactive** 3D front-end / UI
- Fast iteration on scenes, user interaction, AR/VR options
- A “twin dashboard” that is more than plots

### When to prefer robotics simulators
If you want high-fidelity sensor/robot models with less custom coding, consider:
- **Gazebo Sim** (robotics, sensors, physics, plugins)
- **Webots** (beginner-friendly, full robot environment)
- **MuJoCo** (excellent contact dynamics; great for model-based control / RL baselines)

See: `docs/TOOLS.md`

---

## Repo layout

```
digital-twin-starter-kit/
  README.md
  AGENTS.md
  docs/
    TOOLS.md
    PROJECT_IDEAS.md
    TWIN_MATH.md
  python/
    requirements.txt
    telemetry/
      telemetry_server_minimal.py
      telemetry_client_record.py
    twin/
      __init__.py
      run_twin_stream.py
      models/
        mass_spring_damper.py
        thermal_rc.py
      filters/
        ekf.py
        ukf.py
      utils/
        jsonl.py
        numerics.py
    eval/
      evaluate_log.py
  unity/
    README_Unity_Setup.md
    Scripts/
      TcpJsonTelemetryClient.cs
      Telemetry.cs
```

---

## Next steps (for a student)
1. Pick a system and define:
   - state \(x\), inputs \(u\), measurements \(y\)
2. Implement \(f\) and \(h\)
3. Run EKF/UKF; record logs
4. Create evaluation plots + metrics
5. Optionally add:
   - parameter calibration
   - uncertainty quantification
   - decision/control
   - multi-sensor fusion
   - real sensor data (MQTT, serial, etc.)

---

## Notes
- This repo intentionally avoids heavy dependencies and GPUs.
- The Unity side is deliberately minimal; expand it into a dashboard (UI, plots, uncertainty bands) as needed.

