# ROS 2 + Unity integration (optional)

Unity has ROS integration packages (ROS-TCP Connector and endpoint). Use ROS 2 if your twin spans multiple nodes (sim + real + estimator).

This repo does NOT include a full ROS workspace by default. If you add it:
- Create `ros2_ws/` (colcon)
- Add a node that publishes telemetry in a ROS message
- Bridge into Unity via ROS-TCP connector

Agent tasks:
1) Decide ROS 2 distro (match your OS).
2) Add a publisher node and message definitions.
3) Document exact install steps and a demo run.
