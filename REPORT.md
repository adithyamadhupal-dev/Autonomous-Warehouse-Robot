# Project Report: Autonomous Warehouse Robot

## 1. Introduction

Warehouses require fast and reliable movement of goods between storage and dispatch areas. This project demonstrates a virtual autonomous warehouse robot that receives delivery tasks, calculates safe routes, identifies the requested package, and transports it to the assigned delivery location.

The project is intentionally lightweight so it can run on a normal Windows computer without ROS, Gazebo, or a physical robot.

## 2. Objective

The main objective is to develop a virtual robot capable of:

- Navigating a warehouse map
- Avoiding racks and detected obstacles
- Planning an efficient path using A*
- Handling several pickup-and-delivery tasks
- Simulating item recognition
- Producing a task-performance report

## 3. Tools and Technologies

- Python 3
- Pygame
- A* path-planning algorithm
- Priority queue
- Finite-state machine
- CSV reporting

## 4. System Modules

### 4.1 Warehouse Environment

The warehouse is represented as a two-dimensional grid. Rack locations are blocked cells, while aisles are free cells through which the robot can move.

### 4.2 Task Manager

Each task contains:

- Task ID
- Item name
- Priority
- Pickup location
- Delivery location
- Status

The task with the highest priority is processed first.

### 4.3 Path Planner

A* searches the grid for the shortest available route. Manhattan distance is used as the heuristic because the robot moves horizontally and vertically.

### 4.4 Navigation Controller

The robot follows the planned path one grid cell at a time. If a newly detected obstacle blocks the route, the planner calculates a new route from the robot’s current location.

### 4.5 Item Recognition

Each package has a simulated color label. At the pickup point, the robot verifies the target item before beginning the pickup operation. This provides a lightweight representation of camera-based recognition.

### 4.6 Pickup and Delivery Controller

The controller uses these states:

```text
IDLE
MOVING_TO_PICKUP
RECOGNIZING_ITEM
PICKING_ITEM
MOVING_TO_DROPOFF
PLACING_ITEM
COMPLETED
```

### 4.7 Analytics

The simulator records:

- Number of completed tasks
- Travel distance
- Route recalculations
- Completion time
- Final task status

The data is stored in a CSV file.

## 5. Working Procedure

1. Start the simulator.
2. Load and prioritize the warehouse tasks.
3. Select the first task.
4. Use A* to plan a route to the pickup point.
5. Navigate through warehouse aisles.
6. Detect an obstacle and recalculate the route when required.
7. Recognize and pick the assigned item.
8. Plan a route to the delivery point.
9. Deliver the item.
10. Save the task result and continue with the next task.

## 6. Result

The system demonstrates autonomous task selection, warehouse navigation, obstacle rerouting, simulated object recognition, pickup, delivery, and report generation in a single visual application.

## 7. Limitations

- The robot uses grid movement rather than physical wheel dynamics.
- Recognition is color-label simulation rather than a trained vision model.
- Only one robot is active.
- Rack positions are predefined.

## 8. Future Scope

- OpenCV-based object detection
- ROS or Webots integration
- Multi-robot scheduling
- SLAM mapping
- Battery charging and task resumption
- Real motor and sensor integration

## 9. Conclusion

The project successfully demonstrates the key software logic of an autonomous warehouse robot while remaining simple to install, run, explain, and publish on GitHub.
