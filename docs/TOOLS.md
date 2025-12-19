# Tools for Digital Twin projects (practical matrix)

This file is deliberately pragmatic: **what to use when** for MSc Digital Twin projects under laptop constraints.

## Core idea
A digital twin consists of:
1) A model (physics, data-driven, or hybrid)
2) Data assimilation (state estimation, calibration)
3) Prediction / what-if
4) (Optional) Decision / control
5) A visualization / UI layer

You can mix-and-match tools for these layers.

---

## Tool matrix (high-level)

### Unity (game engine / UI-heavy)
**Best for**
- Interactive 3D front-end, polished visuals, dashboard-like twin UI.
- Human-in-the-loop twin: sliders, scenario toggles, annotations.

**Weaknesses**
- You implement/own the physics fidelity unless you integrate external simulators.

**Integration**
- Direct TCP/UDP (this repo).
- ROS 2 via Unity ROS-TCP-Connector (see Unity Robotics packages).

---

### Gazebo Sim (robotics simulator)
**Best for**
- Robot/sensor simulation, physics + sensors, plugins, middleware integration.

**Weaknesses**
- Heavier install than Unity; learning curve for plugins + SDF/URDF.

---

### Webots (robotics simulator)
**Best for**
- Beginner-friendly, end-to-end robot simulation environment.
- Good for quick “working sim” without building a full engine.

**Weaknesses**
- Less “polished UI” than Unity for dashboards; but good enough for many twins.

---

### MuJoCo (physics engine)
**Best for**
- Contact-rich physics, model-based control, benchmark tasks.
- CPU-first workflows are realistic.

**Weaknesses**
- Not a “full world builder” like Unity; you work with XML models and code.

---

### ROS 2 (middleware / integration backbone)
**Best for**
- Multi-node systems, sensors, robots, message passing, interoperability.
- A strong choice if students work with hardware and simulation simultaneously.

**Weaknesses**
- Added complexity; keep it optional unless robotics is central.

---

## Practical recommendations by project type

### House / room thermal digital twin
- Model + filter + calibration: Python (NumPy/SciPy)
- Visualization: Unity (optional) or notebooks/plotly
- Real sensor integration: MQTT + time-series DB (optional)

### Robot twin / navigation twin
- Simulation: Webots or Gazebo
- Middleware: ROS 2
- Visualization: RViz or Unity (for polished UI)

### Contact / manipulation twin
- Simulation: MuJoCo
- Model-based control + identification: Python

---

## Tooling starter workflows

### Workflow 1: Python twin core + Unity front-end (minimum)
- Use this repo’s TCP/JSON stream.
- Add UI and scenario controls in Unity later.

### Workflow 2: ROS 2 as integration bus (recommended for robotics)
- Simulation publishes state/sensors as ROS topics.
- Twin core subscribes and runs filters/calibration.
- Unity visualizes by subscribing via ROS-TCP connector.

### Workflow 3: Simulator-only twin (no Unity)
- Use Webots/Gazebo + ROS visualization tools.
- Focus on estimation/calibration and metrics.

