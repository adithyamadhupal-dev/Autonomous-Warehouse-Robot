"""
Autonomous Warehouse Robot
A lightweight Pygame simulation demonstrating:
- A* path planning
- Multiple warehouse delivery tasks
- Obstacle avoidance and route replanning
- Simulated item recognition, pickup, and delivery
- Live dashboard and CSV task reporting

Controls:
SPACE  Pause / resume
R      Restart simulation
N      Skip current task
ESC    Exit
"""

from __future__ import annotations

import csv
import heapq
import math
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pygame

GridPos = Tuple[int, int]

# ----------------------------- Configuration -----------------------------

WINDOW_WIDTH = 1120
WINDOW_HEIGHT = 720
CELL_SIZE = 48
GRID_COLS = 15
GRID_ROWS = 11
GRID_ORIGIN = (28, 78)
FPS = 60
MOVE_INTERVAL_MS = 260
ACTION_DELAY_MS = 850

BG = (242, 245, 248)
GRID_BG = (255, 255, 255)
GRID_LINE = (215, 220, 226)
RACK = (75, 83, 93)
ROBOT = (33, 150, 243)
ROBOT_OUTLINE = (15, 87, 160)
PATH = (190, 225, 255)
PICKUP = (255, 193, 7)
DROPOFF = (76, 175, 80)
DYNAMIC_OBSTACLE = (229, 57, 53)
TEXT = (35, 40, 45)
MUTED = (100, 110, 120)
PANEL = (255, 255, 255)
PANEL_BORDER = (220, 225, 230)
SUCCESS = (46, 125, 50)

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
REPORT_FILE = OUTPUT_DIR / "task_report.csv"

# ----------------------------- Data models -----------------------------

@dataclass(order=True)
class WarehouseTask:
    priority: int
    task_id: str = field(compare=False)
    item_name: str = field(compare=False)
    item_color: Tuple[int, int, int] = field(compare=False)
    pickup: GridPos = field(compare=False)
    dropoff: GridPos = field(compare=False)
    status: str = field(default="WAITING", compare=False)
    started_at: float = field(default=0.0, compare=False)
    completed_at: float = field(default=0.0, compare=False)
    distance_cells: int = field(default=0, compare=False)
    replans: int = field(default=0, compare=False)


class AStarPlanner:
    """A* path planner for a 4-direction warehouse grid."""

    def __init__(self, cols: int, rows: int, obstacles: set[GridPos]):
        self.cols = cols
        self.rows = rows
        self.obstacles = obstacles

    @staticmethod
    def heuristic(a: GridPos, b: GridPos) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def neighbors(self, node: GridPos) -> List[GridPos]:
        x, y = node
        options = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return [
            p for p in options
            if 0 <= p[0] < self.cols
            and 0 <= p[1] < self.rows
            and p not in self.obstacles
        ]

    def find_path(self, start: GridPos, goal: GridPos) -> List[GridPos]:
        if start == goal:
            return []
        if start in self.obstacles or goal in self.obstacles:
            return []

        frontier: List[Tuple[int, GridPos]] = [(0, start)]
        came_from: Dict[GridPos, Optional[GridPos]] = {start: None}
        cost_so_far: Dict[GridPos, int] = {start: 0}

        while frontier:
            _, current = heapq.heappop(frontier)

            if current == goal:
                break

            for nxt in self.neighbors(current):
                new_cost = cost_so_far[current] + 1
                if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                    cost_so_far[nxt] = new_cost
                    priority = new_cost + self.heuristic(nxt, goal)
                    heapq.heappush(frontier, (priority, nxt))
                    came_from[nxt] = current

        if goal not in came_from:
            return []

        path: List[GridPos] = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]  # type: ignore[assignment]
        path.reverse()
        return path


class WarehouseSimulation:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Autonomous Warehouse Robot")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("segoeui", 18)
        self.small_font = pygame.font.SysFont("segoeui", 15)
        self.title_font = pygame.font.SysFont("segoeui", 28, bold=True)
        self.bold_font = pygame.font.SysFont("segoeui", 18, bold=True)

        self.static_obstacles = self.build_warehouse()
        self.dynamic_obstacles: set[GridPos] = set()
        self.tasks_template = self.build_tasks()
        self.reset()

    @staticmethod
    def build_warehouse() -> set[GridPos]:
        obstacles: set[GridPos] = set()

        # Outer warehouse boundary.
        for x in range(GRID_COLS):
            obstacles.add((x, 0))
            obstacles.add((x, GRID_ROWS - 1))
        for y in range(GRID_ROWS):
            obstacles.add((0, y))
            obstacles.add((GRID_COLS - 1, y))

        # Storage rack blocks with aisles between them.
        rack_columns = [3, 4, 7, 8, 11, 12]
        for x in rack_columns:
            for y in [2, 3, 4, 6, 7, 8]:
                obstacles.add((x, y))

        return obstacles

    @staticmethod
    def build_tasks() -> List[WarehouseTask]:
        return [
            WarehouseTask(1, "T-001", "Blue Motor Box", (66, 135, 245), (2, 2), (13, 2)),
            WarehouseTask(2, "T-002", "Red Sensor Kit", (239, 83, 80), (5, 8), (13, 8)),
            WarehouseTask(3, "T-003", "Green Battery Pack", (76, 175, 80), (9, 2), (1, 8)),
            WarehouseTask(4, "T-004", "Purple Controller", (156, 100, 220), (9, 8), (13, 5)),
        ]

    def reset(self) -> None:
        self.robot_pos: GridPos = (1, 1)
        self.tasks = [
            WarehouseTask(
                t.priority, t.task_id, t.item_name, t.item_color, t.pickup, t.dropoff
            )
            for t in self.tasks_template
        ]
        heapq.heapify(self.tasks)

        self.current_task: Optional[WarehouseTask] = None
        self.completed_tasks: List[WarehouseTask] = []
        self.state = "IDLE"
        self.status_message = "Preparing task queue..."
        self.path: List[GridPos] = []
        self.target: Optional[GridPos] = None
        self.carrying_item = False
        self.paused = False
        self.last_move_ms = pygame.time.get_ticks()
        self.action_started_ms = 0
        self.total_moves = 0
        self.total_replans = 0
        self.dynamic_obstacle_added = False
        self.battery = 100.0
        self.simulation_started = time.time()
        self.static_obstacles = self.build_warehouse()
        self.dynamic_obstacles.clear()
        self.planner = AStarPlanner(
            GRID_COLS, GRID_ROWS, self.static_obstacles | self.dynamic_obstacles
        )

        OUTPUT_DIR.mkdir(exist_ok=True)
        if REPORT_FILE.exists():
            REPORT_FILE.unlink()

    @property
    def obstacles(self) -> set[GridPos]:
        return self.static_obstacles | self.dynamic_obstacles

    def plan_route(self, target: GridPos) -> bool:
        self.planner.obstacles = self.obstacles
        self.target = target
        self.path = self.planner.find_path(self.robot_pos, target)
        if self.robot_pos != target and not self.path:
            self.status_message = f"No route available to {target}"
            self.state = "ERROR"
            return False
        return True

    def begin_next_task(self) -> None:
        if not self.tasks:
            self.current_task = None
            self.state = "ALL_COMPLETE"
            self.status_message = "All warehouse tasks completed successfully."
            return

        self.current_task = heapq.heappop(self.tasks)
        self.current_task.status = "MOVING_TO_PICKUP"
        self.current_task.started_at = time.time()
        self.state = "TO_PICKUP"
        self.carrying_item = False
        self.status_message = f"Navigating to {self.current_task.item_name}"
        self.plan_route(self.current_task.pickup)

    def replan_current_route(self) -> None:
        if self.target is None or self.current_task is None:
            return
        self.current_task.replans += 1
        self.total_replans += 1
        self.status_message = "Obstacle detected — calculating alternate route"
        self.plan_route(self.target)

    def maybe_add_dynamic_obstacle(self) -> None:
        """Inject one temporary obstacle to visibly demonstrate route replanning."""
        if self.dynamic_obstacle_added or self.total_moves < 7 or len(self.path) < 3:
            return

        blocked = self.path[1]
        reserved = {
            t.pickup for t in self.tasks_template
        } | {
            t.dropoff for t in self.tasks_template
        } | {self.robot_pos}

        if blocked not in reserved and blocked not in self.static_obstacles:
            self.dynamic_obstacles.add(blocked)
            self.dynamic_obstacle_added = True
            self.replan_current_route()

    def move_robot(self) -> None:
        now = pygame.time.get_ticks()
        if now - self.last_move_ms < MOVE_INTERVAL_MS:
            return
        self.last_move_ms = now

        if not self.path:
            self.on_target_reached()
            return

        self.maybe_add_dynamic_obstacle()

        if not self.path:
            return

        next_cell = self.path[0]
        if next_cell in self.obstacles:
            self.replan_current_route()
            return

        self.robot_pos = next_cell
        self.path.pop(0)
        self.total_moves += 1
        self.battery = max(0.0, self.battery - 0.35)

        if self.current_task:
            self.current_task.distance_cells += 1

        if not self.path:
            self.on_target_reached()

    def on_target_reached(self) -> None:
        if self.current_task is None:
            return

        now = pygame.time.get_ticks()

        if self.state == "TO_PICKUP":
            self.state = "RECOGNIZING"
            self.current_task.status = "RECOGNIZING_ITEM"
            self.action_started_ms = now
            self.status_message = f"Recognizing {self.current_task.item_name} by color label"

        elif self.state == "TO_DROPOFF":
            self.state = "DROPPING"
            self.current_task.status = "PLACING_ITEM"
            self.action_started_ms = now
            self.status_message = "Placing item at delivery zone"

    def process_actions(self) -> None:
        now = pygame.time.get_ticks()

        # Start the next queued task while the robot is idle.
        if self.state == "IDLE" and self.current_task is None:
            if now - self.action_started_ms >= 500:
                self.begin_next_task()
            return

        if self.current_task is None:
            return

        if self.state == "RECOGNIZING" and now - self.action_started_ms >= ACTION_DELAY_MS:
            self.state = "PICKING"
            self.current_task.status = "PICKING_ITEM"
            self.action_started_ms = now
            self.status_message = "Correct item recognized — pickup in progress"

        elif self.state == "PICKING" and now - self.action_started_ms >= ACTION_DELAY_MS:
            self.carrying_item = True
            self.state = "TO_DROPOFF"
            self.current_task.status = "MOVING_TO_DROPOFF"
            self.status_message = "Item secured — moving to delivery zone"
            self.plan_route(self.current_task.dropoff)

        elif self.state == "DROPPING" and now - self.action_started_ms >= ACTION_DELAY_MS:
            self.carrying_item = False
            self.current_task.status = "COMPLETED"
            self.current_task.completed_at = time.time()
            self.completed_tasks.append(self.current_task)
            self.write_report_row(self.current_task)
            self.status_message = f"{self.current_task.task_id} completed"
            self.current_task = None
            self.state = "IDLE"
            self.action_started_ms = now


    @staticmethod
    def write_report_row(task: WarehouseTask) -> None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        file_exists = REPORT_FILE.exists()
        duration = round(task.completed_at - task.started_at, 2)

        with REPORT_FILE.open("a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow([
                    "task_id",
                    "item_name",
                    "priority",
                    "pickup",
                    "dropoff",
                    "distance_cells",
                    "route_replans",
                    "completion_time_seconds",
                    "status",
                ])
            writer.writerow([
                task.task_id,
                task.item_name,
                task.priority,
                task.pickup,
                task.dropoff,
                task.distance_cells,
                task.replans,
                duration,
                task.status,
            ])

    def skip_current_task(self) -> None:
        if self.current_task:
            self.current_task.status = "SKIPPED"
            self.current_task = None
            self.path = []
            self.target = None
            self.carrying_item = False
            self.state = "IDLE"
            self.action_started_ms = pygame.time.get_ticks()
            self.status_message = "Task skipped by user"

    def update(self) -> None:
        if self.paused:
            return

        if self.state == "IDLE" and self.current_task is None:
            self.process_actions()
        elif self.state in {"TO_PICKUP", "TO_DROPOFF"}:
            self.move_robot()
        elif self.state in {"RECOGNIZING", "PICKING", "DROPPING"}:
            self.process_actions()

    # ----------------------------- Drawing -----------------------------

    def cell_rect(self, pos: GridPos) -> pygame.Rect:
        x, y = pos
        return pygame.Rect(
            GRID_ORIGIN[0] + x * CELL_SIZE,
            GRID_ORIGIN[1] + y * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE,
        )

    def draw_text(
        self,
        text: str,
        pos: Tuple[int, int],
        color: Tuple[int, int, int] = TEXT,
        font: Optional[pygame.font.Font] = None,
    ) -> None:
        surface = (font or self.font).render(text, True, color)
        self.screen.blit(surface, pos)

    def draw_grid(self) -> None:
        map_rect = pygame.Rect(
            GRID_ORIGIN[0],
            GRID_ORIGIN[1],
            GRID_COLS * CELL_SIZE,
            GRID_ROWS * CELL_SIZE,
        )
        pygame.draw.rect(self.screen, GRID_BG, map_rect, border_radius=8)

        # Planned path.
        for pos in self.path:
            rect = self.cell_rect(pos).inflate(-10, -10)
            pygame.draw.rect(self.screen, PATH, rect, border_radius=8)

        # Grid cells and rack obstacles.
        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                pos = (x, y)
                rect = self.cell_rect(pos)

                if pos in self.static_obstacles:
                    pygame.draw.rect(self.screen, RACK, rect.inflate(-4, -4), border_radius=5)
                elif pos in self.dynamic_obstacles:
                    pygame.draw.rect(
                        self.screen,
                        DYNAMIC_OBSTACLE,
                        rect.inflate(-8, -8),
                        border_radius=8,
                    )
                    self.draw_text("!", (rect.x + 20, rect.y + 11), (255, 255, 255), self.bold_font)

                pygame.draw.rect(self.screen, GRID_LINE, rect, width=1)

        # Pickup and delivery markers.
        for task in self.tasks_template:
            pickup_rect = self.cell_rect(task.pickup).inflate(-15, -15)
            drop_rect = self.cell_rect(task.dropoff).inflate(-15, -15)
            pygame.draw.circle(self.screen, task.item_color, pickup_rect.center, 12)
            pygame.draw.circle(self.screen, DROPOFF, drop_rect.center, 13, width=4)

        # Robot.
        robot_rect = self.cell_rect(self.robot_pos).inflate(-10, -10)
        pygame.draw.rect(self.screen, ROBOT, robot_rect, border_radius=10)
        pygame.draw.rect(self.screen, ROBOT_OUTLINE, robot_rect, width=3, border_radius=10)
        pygame.draw.circle(
            self.screen,
            (255, 255, 255),
            (robot_rect.centerx, robot_rect.centery),
            7,
        )
        if self.carrying_item and self.current_task:
            pygame.draw.circle(
                self.screen,
                self.current_task.item_color,
                (robot_rect.right - 6, robot_rect.top + 6),
                7,
            )

        pygame.draw.rect(self.screen, PANEL_BORDER, map_rect, width=2, border_radius=8)

    def draw_panel(self) -> None:
        panel_x = GRID_ORIGIN[0] + GRID_COLS * CELL_SIZE + 24
        panel = pygame.Rect(panel_x, 78, 330, 600)
        pygame.draw.rect(self.screen, PANEL, panel, border_radius=12)
        pygame.draw.rect(self.screen, PANEL_BORDER, panel, width=2, border_radius=12)

        x = panel.x + 20
        y = panel.y + 18

        self.draw_text("LIVE STATUS", (x, y), MUTED, self.small_font)
        y += 27
        self.draw_text(self.state.replace("_", " "), (x, y), TEXT, self.bold_font)
        y += 34

        self.draw_text("Current task", (x, y), MUTED, self.small_font)
        y += 23
        if self.current_task:
            self.draw_text(self.current_task.task_id, (x, y), TEXT, self.bold_font)
            y += 23
            self.draw_text(self.current_task.item_name, (x, y), self.current_task.item_color)
        else:
            self.draw_text("No active task", (x, y), MUTED)
        y += 38

        self.draw_text("Robot position", (x, y), MUTED, self.small_font)
        self.draw_text(str(self.robot_pos), (x + 160, y), TEXT, self.bold_font)
        y += 27

        self.draw_text("Battery", (x, y), MUTED, self.small_font)
        battery_rect = pygame.Rect(x + 90, y + 2, 190, 16)
        pygame.draw.rect(self.screen, (230, 234, 238), battery_rect, border_radius=8)
        fill_width = int(190 * self.battery / 100)
        pygame.draw.rect(
            self.screen,
            SUCCESS if self.battery > 35 else PICKUP,
            pygame.Rect(battery_rect.x, battery_rect.y, fill_width, battery_rect.height),
            border_radius=8,
        )
        self.draw_text(f"{self.battery:.0f}%", (x + 285, y - 2), TEXT, self.small_font)
        y += 42

        stats = [
            ("Completed", str(len(self.completed_tasks))),
            ("Queued", str(len(self.tasks))),
            ("Distance", f"{self.total_moves} cells"),
            ("Replans", str(self.total_replans)),
        ]
        self.draw_text("PERFORMANCE", (x, y), MUTED, self.small_font)
        y += 27
        for label, value in stats:
            self.draw_text(label, (x, y), MUTED, self.small_font)
            self.draw_text(value, (x + 160, y), TEXT, self.bold_font)
            y += 28

        y += 12
        self.draw_text("TASK QUEUE", (x, y), MUTED, self.small_font)
        y += 26

        queue_items = sorted(self.tasks)[:4]
        if not queue_items:
            self.draw_text("Queue empty", (x, y), MUTED, self.small_font)
        else:
            for task in queue_items:
                self.draw_text(
                    f"{task.task_id}  P{task.priority}",
                    (x, y),
                    TEXT,
                    self.small_font,
                )
                self.draw_text(task.item_name[:22], (x + 95, y), MUTED, self.small_font)
                y += 24

        y = panel.bottom - 92
        self.draw_text("CONTROLS", (x, y), MUTED, self.small_font)
        y += 25
        self.draw_text("SPACE Pause   R Restart   N Skip", (x, y), TEXT, self.small_font)

    def draw(self) -> None:
        self.screen.fill(BG)
        self.draw_text("Autonomous Warehouse Robot", (28, 24), TEXT, self.title_font)
        self.draw_text(
            "A* navigation • obstacle rerouting • simulated item recognition",
            (28, 55),
            MUTED,
            self.small_font,
        )

        self.draw_grid()
        self.draw_panel()

        footer_y = 690
        status_color = DYNAMIC_OBSTACLE if "Obstacle" in self.status_message else TEXT
        self.draw_text(self.status_message, (30, footer_y), status_color, self.small_font)
        if self.paused:
            self.draw_text("PAUSED", (650, 28), DYNAMIC_OBSTACLE, self.bold_font)

        pygame.display.flip()

    def run(self) -> None:
        self.action_started_ms = pygame.time.get_ticks() - 1000
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_n:
                        self.skip_current_task()

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    WarehouseSimulation().run()
