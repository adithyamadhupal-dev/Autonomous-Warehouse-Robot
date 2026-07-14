# 60-Second Demo Script

This project is an Autonomous Warehouse Robot simulator developed using Python and Pygame.

The warehouse is represented as a grid containing storage racks, pickup points, delivery points, and navigable aisles. Multiple warehouse orders are stored in a priority queue.

For each order, the robot uses the A* algorithm to calculate the shortest available path to the pickup point. During navigation, a temporary obstacle is introduced. The robot detects that the planned route is blocked and automatically calculates an alternate route.

At the pickup location, the robot performs simulated color-based item recognition, picks the item, and plans another route to the delivery point.

The dashboard displays the current task, robot state, position, battery level, total distance, completed tasks, and number of route recalculations.

After each delivery, the system saves the task details and performance data to a CSV report.

This lightweight implementation demonstrates warehouse navigation, obstacle avoidance, path planning, item recognition, and automated pickup-and-delivery workflow.
