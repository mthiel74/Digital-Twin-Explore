# Webots notes (optional backend)

Webots is an open-source robot simulator under the Apache 2.0 license.

Suggested MSc direction:
- Create a Webots world (robot + sensors).
- Use its controllers (Python/C++) to publish state/sensors.
- Run filtering/calibration and evaluate.

What to implement next (agent tasks):
1) Add a Webots project folder with one robot and one sensor.
2) Add a Python controller that logs JSONL in the repo’s schema.
3) Compare EKF vs UKF robustness under missing data / noise.
