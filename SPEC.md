# Pipeline Digital Twin Specification

This document defines the laptop-scale digital twin for a 1D transient pipeline
with pumping, downstream valve control, unknown leak location, and online
estimation. The design is intentionally lightweight (NumPy + Matplotlib only)
to enable deterministic, reproducible experiments on commodity laptops.

## Overview
- **Physics:** 1D transient dynamics with pressure/flow coupling, frictional
  damping, pump head boundary, downstream valve restriction, and optional leak
  orifice at an unknown location.
- **Sensing:** Synthetic measurements with configurable noise, bias drift, and
  fixed-step latency; sampling rate can be down-sampled deterministically.
- **Estimation:** Ensemble Kalman Filter (state + parameters), friction scale
  and pump gain parameter tracking, leak localization via a bank of filters.
- **Outputs:** Metrics, plots saved under `outputs/`, and deterministic
  golden-run tests exercised via `python -m pytest`.

## Phase 1 — Physics Backbone
**Goal:** Deterministic 1D transient pipeline model with boundary actuation and
optional leak withdrawal.

**Scope:** `src/pipeline_twin/physics.py`, `src/pipeline_twin/boundaries.py`,
`src/pipeline_twin/leak.py`, `configs/default.yaml`.

**Acceptance criteria:**
- Pipeline stepping produces non-negative pressures and stable flows for
  `total_time` without blowing up for `default.yaml`.
- Pump and valve ramps follow first-order lags; commands remain in [0, pump_head]
  and [0, valve_setpoint].
- Leak withdrawal reduces local pressure deterministically when coefficient > 0.

**Tests:**
- `tests/test_phase1_physics.py` seeds the simulation and checks stability,
  monotonic ramping, and deterministic leak-induced pressure drop.

## Phase 2 — Sensor Layer
**Goal:** Deterministic synthetic sensor outputs with noise, bias drift, latency,
and configurable sampling.

**Scope:** `src/pipeline_twin/sensors.py`.

**Acceptance criteria:**
- Bias drift accumulates linearly with step index when enabled.
- Latency buffer delays measurements by `latency_steps` without loss.
- Sampling skip works for `sample_every > 1`.

**Tests:**
- `tests/test_phase2_sensors.py` validates bias accumulation, latency, and
  sub-sampling deterministically via fixed RNG seeds.

## Phase 3 — State Estimation (EnKF)
**Goal:** Maintain an ensemble pipeline state and assimilate pressure/flow
measurements via Ensemble Kalman Filter updates.

**Scope:** `src/pipeline_twin/enkf.py`, `src/pipeline_twin/config.py` (EnKF),
`src/pipeline_twin/simulate.py` (integration).

**Acceptance criteria:**
- Ensemble dimension matches discretization (2 * n_cells - 1 + 2 parameters).
- Propagation step deterministically advances each ensemble member using the
  physics backbone.
- Update step reduces innovation norm when measurements are provided.

**Tests:**
- `tests/test_phase3_enkf_state.py` checks ensemble shape and verifies that a
  measurement update decreases innovation magnitude for seeded data.

## Phase 4 — Parameter Estimation
**Goal:** Track friction scale and pump gain parameters alongside state within
EnKF.

**Scope:** `src/pipeline_twin/enkf.py`.

**Acceptance criteria:**
- Parameter states remain positive and respond to repeated updates.
- Small process noise (parameter_drift) is injected deterministically when set.
- Inflation is applied after each update.

**Tests:**
- `tests/test_phase4_param_estimation.py` asserts deterministic parameter drift
  and inflation effects with fixed seeds.

## Phase 5 — Leak Localization
**Goal:** Bank-of-filters approach that scores candidate leak locations.

**Scope:** `src/pipeline_twin/multihypothesis.py`, `configs/leak_sweep.yaml`,
`src/pipeline_twin/simulate.py` (for data), `src/pipeline_twin/metrics.py`.

**Acceptance criteria:**
- Each hypothesis returns a finite score computed from ensemble innovations.
- The correct leak index yields the lowest (best) score on synthetic data with
  a seeded leak scenario.

**Tests:**
- `tests/test_phase5_leak_localization.py` seeds a leak scenario, evaluates a
  small hypothesis set, and checks that the planted leak ranks best.

## Outputs & Determinism
- All plots save under `outputs/` (e.g., heatmaps, residuals).
- Tests must run via `python -m pytest` with deterministic seeds; no reliance on
  external services or heavyweight dependencies.

## Configurations
- `configs/default.yaml` — nominal scenario without a leak.
- `configs/leak_sweep.yaml` — example hypothesis sweep with an injected leak.

## CLI
- `python -m pipeline_twin.run --config CONFIG_PATH --outdir outputs/` executes a
  simulation and writes plots (unless `--no-plots` is set). Update `README.md`
  when adding or altering CLI flags.
