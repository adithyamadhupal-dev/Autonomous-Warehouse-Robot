# Autonomous Warehouse Robot

A simple, visual warehouse-automation project built with **Python and Pygame**.  
The robot completes multiple pickup-and-delivery tasks using **A\* path planning**, detects blocked routes, recalculates an alternate path, simulates item recognition, and exports a task report.

## Features

- 2D virtual warehouse with storage racks and navigable aisles
- Multiple priority-based delivery tasks
- A* shortest-path planning
- Dynamic obstacle detection and route replanning
- Simulated color-based item recognition
- Pickup and drop-off state machine
- Battery, distance, completed-task, and replan counters
- CSV report generated automatically
- Keyboard controls for pause, restart, and task skipping

## Technology

- Python 3.10+
- Pygame
- A* path-planning algorithm
- Priority queue and finite-state machine

## Run on Windows

### Option 1: Use the included batch file

Double-click:

```text
run_windows.bat
```

### Option 2: Use Command Prompt or PowerShell

```bash
pip install -r requirements.txt
python warehouse_robot.py
```

## Controls

| Key | Action |
|---|---|
| Space | Pause or resume |
| R | Restart the simulation |
| N | Skip the current task |
| Esc | Exit |

## Project Workflow

1. The task manager selects the highest-priority warehouse order.
2. A* calculates a route from the robot to the pickup location.
3. The robot follows the planned path.
4. A temporary obstacle is introduced to demonstrate route replanning.
5. The robot performs simulated color-label recognition.
6. The item is picked up and transported to the delivery zone.
7. The completed task is recorded in `output/task_report.csv`.
8. The robot automatically starts the next task.

## Folder Structure

```text
Autonomous_Warehouse_Robot/
├── warehouse_robot.py
├── requirements.txt
├── run_windows.bat
├── README.md
├── REPORT.md
├── DEMO_SCRIPT.md
├── LICENSE
├── .gitignore
├── assets/
│   └── architecture.png
├── screenshots/
│   └── simulation_preview.png
└── output/
    └── sample_task_report.csv
```

## A* Algorithm

A* evaluates candidate grid cells using:

```text
f(n) = g(n) + h(n)
```

- `g(n)` is the movement cost from the starting cell.
- `h(n)` is the Manhattan distance from the current cell to the target.
- Rack cells and detected obstacles are excluded from the search.

## Item Recognition

To keep the project lightweight and easy to run, item recognition is simulated using a color label assigned to each warehouse package. This represents the decision step that a camera and OpenCV module would perform in a larger implementation.

## Output

After completing tasks, the program creates:

```text
output/task_report.csv
```

The report contains task ID, item, priority, pickup location, drop-off location, distance travelled, route replans, completion time, and status.

## Internship Objective Coverage

| Required objective | Implementation |
|---|---|
| Navigate a virtual warehouse | Pygame warehouse simulation |
| Pick and place items | Simulated pickup and drop-off states |
| Obstacle avoidance | Grid obstacles and dynamic rerouting |
| A* or Dijkstra path planning | A* implementation |
| Object recognition | Simulated color-based recognition |

## Limitations

This is a lightweight simulation rather than a full ROS/Webots robot. It does not model wheel physics, LiDAR point clouds, or a mechanical gripper. The project focuses on the core autonomous-robot logic required for a fast internship demonstration.

## Future Improvements

- Replace simulated recognition with OpenCV camera input
- Move the controller to Webots or Gazebo
- Add several robots and collision coordination
- Add charging-station logic
- Use SLAM for unknown warehouse maps

## Author

**Adithya Madhupal**  
Project: **Autonomous Warehouse Robot**
