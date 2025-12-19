# Gazebo Sim notes (optional backend)

Gazebo Sim is an open-source robotics simulator with physics, rendering, and sensor models.

Suggested MSc direction:
- Build a simulated robot or sensor rig in Gazebo.
- Publish simulated sensors.
- Run a twin-core (filters/calibration) in Python.
- Optionally visualize in Unity (ROS or TCP bridge).

What to implement next (agent tasks):
1) Provide a minimal Gazebo world + model.
2) Stream a simulated sensor signal to `python/twin/`.
3) Evaluate estimation/calibration accuracy vs noise and latency.
