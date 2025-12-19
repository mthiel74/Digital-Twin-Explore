# Digital Twin MSc project ideas (CPU-first)

Below are concrete project ideas with clear deliverables. Pick one.

## 1) Room/house thermal digital twin (recommended)
- Model: 1R1C or 2R2C thermal network.
- Data: temperature/humidity sensors (optional) + outside temperature from an API (optional).
- Tasks:
  - parameter calibration (R,C, heater gain)
  - EKF/UKF state estimation (include unmeasured disturbances)
  - MPC-lite control to track a setpoint vs energy use
- Deliverables: calibrated twin + what-if scenarios + evaluation

## 2) Vibration/oscillator digital twin
- Model: mass-spring-damper with forcing.
- Data: accelerometer or synthetic.
- Tasks:
  - state estimation from noisy displacement only
  - estimate damping/spring constant (calibration)
  - anomaly detection when parameters drift
- Deliverables: detection delay curves + robust estimates.

## 3) Predictive maintenance twin (dataset-driven)
- Use an open dataset (bearings/turbofan/etc.).
- Build a minimal physics-inspired degradation model + data-driven residual.
- Deliverables: remaining useful life intervals + failure mode analysis.

## 4) Multi-sensor fusion twin (networked)
- Multiple nodes (rooms or devices) with heterogeneous sampling and missing data.
- Tasks: fusion + uncertainty + graph-based anomaly detection.

## 5) Simulator-backed twin (robotics)
- Use Webots or Gazebo.
- Build a twin that estimates pose/state from sensors and predicts trajectory.
- Deliverables: estimation accuracy vs compute, robustness to noise and delays.

