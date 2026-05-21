# Autonomous Mobile Robot Navigation — ROS2 & Nav2

A differential drive robot built from scratch in ROS2 and Gazebo, capable of autonomous navigation using SLAM-based mapping and the Nav2 navigation stack.

[![Demo Video](https://img.youtube.com/vi/y4XCQdMSPc4/0.jpg)](https://youtu.be/y4XCQdMSPc4?si=oFY1qMcEZjCUfGG8)

---

## Overview

This project implements a complete autonomous navigation pipeline for a simulated differential drive robot. The robot maps an unknown custom environment using SLAM Toolbox, then navigates autonomously to goal poses using the Nav2 stack with AMCL localization and MPPI control.

Everything in this project, the robot URDF, the Gazebo world, the Nav2 configuration — was built from scratch without CAD tools or copied templates.

---

## Features

- Custom differential drive robot modeled entirely in URDF from scratch
- Custom Gazebo simulation environment built with brick wall layouts
- 2D LiDAR-based SLAM mapping using SLAM Toolbox
- Autonomous navigation with Nav2 (AMCL localization + NavFn global planner + MPPI local controller)
- Twist multiplexer for priority-based velocity command handling (navigation vs teleop)
- Sensor suite: 2D planar LiDAR, IMU, RGB Camera (data published to ROS2 topics)
- Full ROS2 Humble + Gazebo Classic simulation

---

## System Architecture

```
Gazebo Simulation
      │
      ├── diff_drive robot (URDF)
      │       ├── 2D LiDAR  ──► /scan
      │       ├── IMU       ──► /imu
      │       └── Camera    ──► /camera/image_raw
      │
      ├── gazebo_ros2_control
      │       └── diff_cont (DiffDriveController)
      │
Nav2 Stack
      ├── SLAM Toolbox       ──► /map
      ├── AMCL               ──► map → odom TF
      ├── NavFn Planner      ──► global path
      ├── MPPI Controller    ──► /cmd_vel_nav
      └── Behavior Server    ──► recovery behaviors

Twist Mux
      ├── /cmd_vel_nav    (priority 10)
      └── /cmd_vel_teleop (priority 100)
              │
              └──► /diff_cont/cmd_vel_unstamped
```

---

## Robot Description

The robot is a differential drive platform modeled entirely in URDF:

- **Chassis** with left and right drive wheels
- **Caster wheel** for passive support
- **2D planar LiDAR** mounted on laser_frame
- **IMU** on imu_link
- **RGB Camera** with optical frame
- ros2_control interface with velocity-controlled wheel joints

---

## Navigation Pipeline

**Phase 1 — Mapping**

The robot is teleoperated through the environment while SLAM Toolbox builds an occupancy grid map in real time. The map is saved as a `.pgm` + `.yaml` file pair.

**Phase 2 — Autonomous Navigation**

The saved map is loaded by Nav2's map server. AMCL localizes the robot within the map using LiDAR scan matching. Goal poses are sent via RViz2 and the robot plans and executes a path using:

- **NavFn** (Dijkstra-based global planner)
- **MPPI Controller** (Model Predictive Path Integral local controller)
- **Recovery behaviors**: spin, backup, wait

---

## Dependencies

- ROS2 Humble
- Gazebo Classic (gazebo_ros_pkgs)
- Nav2 (navigation2)
- SLAM Toolbox (slam_toolbox)
- gazebo_ros2_control
- twist_mux
- robot_state_publisher
- joint_state_broadcaster

---

## Build & Run

```bash
# Clone the repository
git clone https://github.com/Subhanjal-Pant/Navigation-and-Perception.git
cd Navigation-and-Perception

# Build
colcon build --symlink-install

# Source
source /opt/ros/humble/setup.bash
source install/setup.bash

# Launch
ros2 launch robot_description launch_sim.launch.py
```

Once launched:
1. Set the **2D Pose Estimate** in RViz2 to match the robot's position in Gazebo
2. Send a **2D Nav Goal** to any reachable location on the map
3. The robot will plan and navigate autonomously

---

## What's Next

This project forms the navigation foundation for an upcoming active perception project involving:

- Custom EKF in C++ fusing wheel odometry, IMU, and visual SLAM (ORB-SLAM3)
- A physical robotic arm as an active perception head
- Entropy-based Next Best View (NBV) selection for pre-navigation mapping

---

## Author

**Subhanjal Pant**  
Final Year Mechanical Engineering, Pulchowk Campus, IOE, Tribhuvan University  
Research Interests: Autonomous Navigation, SLAM, Sensor Fusion, Active Perception