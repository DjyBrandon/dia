from collections import defaultdict

from config import Config
import math
import random
import heapq


class Strategy:
    def __init__(self, dirt_list=None):
        self.dirt_list = dirt_list or []

    def find_nearest_dirt(self, current_grid):
        """
        Find the nearest dirt cell to the current grid position.

        Args:
            current_grid (tuple): The current grid coordinates (col, row).

        Returns:
            tuple: The grid coordinates (col, row) of the nearest dirt cell, or None if no dirt is found.
        """
        if not self.dirt_list:
            return None
        dirt_positions = [(int(d.x // Config.CELL_SIZE.value), int(d.y // Config.CELL_SIZE.value))
                          for d in self.dirt_list]
        dirt_positions.sort(key=lambda pos: abs(pos[0] - current_grid[0]) + abs(pos[1] - current_grid[1]))
        return dirt_positions[0] if dirt_positions else None

    def find_farest_dirt(self, current_grid):
        """
        Find the farthest dirt cell from the current grid position.

        Args:
            current_grid (tuple): The current grid coordinates (col, row).

        Returns:
            tuple: The grid coordinates (col, row) of the farthest dirt cell, or None if no dirt is found.
        """
        if not self.dirt_list:
            return None
        dirt_positions = [(int(d.x // Config.CELL_SIZE.value), int(d.y // Config.CELL_SIZE.value))
                          for d in self.dirt_list]
        dirt_positions.sort(key=lambda pos: abs(pos[0] - current_grid[0]) + abs(pos[1] - current_grid[1]), reverse=True)
        return dirt_positions[0] if dirt_positions else None

    def calculate_dirt_per_cell(self):
        """计算每个网格中的灰尘数量"""
        dirt_per_cell = defaultdict(int)
        cell_size = Config.CELL_SIZE.value
        for dirt in self.dirt_list:
            col = int(dirt.x // cell_size)
            row = int(dirt.y // cell_size)
            dirt_per_cell[(col, row)] += 1
        return dirt_per_cell

    def find_most_dirty_cell(self, current_grid):
        """找到灰尘最多且离当前网格最近的网格"""
        dirt_per_cell = self.calculate_dirt_per_cell()
        if not dirt_per_cell:
            return None
        max_count = max(dirt_per_cell.values())
        max_cells = [cell for cell, count in dirt_per_cell.items() if count == max_count]
        closest_cell = None
        min_distance = float('inf')
        for cell in max_cells:
            distance = abs(cell[0] - current_grid[0]) + abs(cell[1] - current_grid[1])  # 曼哈顿距离
            if distance < min_distance:
                min_distance = distance
                closest_cell = cell
        return closest_cell


    @staticmethod
    def compute_a_star_path(start, goal, dirt_list):
        """
        Compute the shortest path from start to goal using the A* algorithm.

        Args:
            start (tuple): The starting grid coordinates (x, y).
            goal (tuple): The goal grid coordinates (x, y).
            dirt_list (list): List of dirt positions to consider as potential obstacles.

        Returns:
            list: A list of grid coordinates representing the path from start to goal.
        """
        # print(f"start: {start}, goal: {goal}")
        cols, rows = Config.MAP_WIDTH.value, Config.MAP_HEIGHT.value
        obstacles = {(x, y) for x in range(cols) for y in range(rows)
                     if x == 0 or y == 0 or x == cols - 1 or y == rows - 1}

        def heuristic(a, b):
            # print(f"heuristic: {abs(a[0] - b[0]) + abs(a[1] - b[1])}")
            return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

        # 新增：计算全局路径直线的参数ax + by + c = 0（连接起点和目标点）
        dx = goal[0] - start[0]
        dy = goal[1] - start[1]
        a = dy
        b = -dx
        c = dx * start[1] - dy * start[0]

        def hybrid_heuristic(node):
            # 点对线距离项
            denominator = math.sqrt(a ** 2 + b ** 2)
            h1 = abs(a * node[0] + b * node[1] + c) / denominator if denominator > 0 else 0
            # 欧几里得距离项
            h2 = math.sqrt((node[0] - goal[0]) ** 2 + (node[1] - goal[1]) ** 2)
            # 可调整两个启发式的权重比例
            return 0.3 * h1 + 0.7 * h2  # 更注重目标距离

        open_heap = []
        heapq.heappush(open_heap, (0 + heuristic(start, goal), 0, start))
        # heapq.heappush(open_heap, (0 + hybrid_heuristic(start), 0, start))
        came_from = {start: None}
        g_score = {start: 0}
        closed_set = set()

        if goal in obstacles:
            return []

        while open_heap:
            _, current_g, current = heapq.heappop(open_heap)

            if current == goal:
                path = []
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                print(f"path: {path}")
                return path
                # return path[1:]  # 排除起点

            closed_set.add(current)

            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if (0 <= neighbor[0] < cols and 0 <= neighbor[1] < rows and
                        neighbor not in obstacles and neighbor not in closed_set):
                    tentative_g = current_g + 1

                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score = tentative_g + heuristic(neighbor, goal)
                        # f_score = tentative_g + hybrid_heuristic(neighbor)
                        heapq.heappush(open_heap, (f_score, tentative_g, neighbor))

            # for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:  # 4个方向移动
            #     neighbor = (current[0] + dx, current[1] + dy)
            #     if (neighbor[0] < 0 or neighbor[0] >= cols or
            #             neighbor[1] < 0 or neighbor[1] >= rows or
            #             neighbor in obstacles):
            #         continue
            #
            #     tentative_g = current_g + 1
            #
            #     if neighbor in closed_set and tentative_g >= g_score.get(neighbor, float('inf')):
            #         continue
            #
            #     if tentative_g < g_score.get(neighbor, float('inf')):
            #         came_from[neighbor] = current
            #         g_score[neighbor] = tentative_g
            #         f_score = tentative_g + hybrid_heuristic(neighbor)
            #         heapq.heappush(open_heap, (f_score, tentative_g, neighbor))

        return []  # 没有找到路径

    @staticmethod
    def random_walk_strategy(bot, charger_l, charger_r):
        """
        Execute a random walk strategy for robot movement.
        """
        if bot.is_turning:
            return
        if bot.currently_turning:
            bot.vl = -2.0
            bot.vr = 2.0
            bot.turning -= 1
        else:
            bot.vl = 5.0
            bot.vr = 5.0
            bot.moving -= 1

        if bot.moving == 0 and not bot.currently_turning:
            bot.turning = random.randrange(20, 40)
            bot.currently_turning = True

        if bot.turning == 0 and bot.currently_turning:
            bot.moving = random.randrange(50, 100)
            bot.currently_turning = False

        if bot.battery < 800:
            if charger_r > charger_l:
                bot.vl = 2.0
                bot.vr = -2.0
            elif charger_r < charger_l:
                bot.vl = -2.0
                bot.vr = 2.0
            if abs(charger_r - charger_l) < charger_l * 0.1:
                bot.vl = 5.0
                bot.vr = 5.0

        if charger_l + charger_r > 200 and bot.battery < Config.BOT_BATTERY_CAPACITY.value:
            bot.vl = 0.0
            bot.vr = 0.0

    @staticmethod
    def a_star_strategy(bot, charger_l, charger_r):
        """
        Execute an A* pathfinding strategy for robot navigation.

        This method directs the robot to seek a charging station when the battery is low,
        using sensor readings to orient towards the charger. Otherwise, it computes or follows
        an A* path to the nearest dirt cell in the occupancy grid. The robot adjusts its wheel
        speeds to orient and move toward each waypoint, and resets the target once reached.

        Args:
            bot: Bot
            charger_l (float): Sensor reading from the left charger detector.
            charger_r (float): Sensor reading from the right charger detector.
        """
        if bot.battery < 800:
            if charger_r > charger_l:
                bot.vl, bot.vr = 2.0, -2.0
            elif charger_r < charger_l:
                bot.vl, bot.vr = -2.0, 2.0
            elif abs(charger_r - charger_l) < charger_l * 0.1:
                bot.vl, bot.vr = 5.0, 5.0
            return

        if bot.is_turning:
            return

        cell_size = Config.CELL_SIZE.value
        curr_col = int(bot.x // cell_size)
        curr_row = int(bot.y // cell_size)
        current_grid = (curr_col, curr_row)

        if bot.a_star_target is None:
            strategy = Strategy(bot.dirt_list)
            # bot.a_star_target = strategy.find_nearest_dirt(current_grid)
            # bot.a_star_target = strategy.find_farest_dirt(current_grid)
            # print(f"a_star_target: {bot.a_star_target}")

            # 根据当前网格灰尘数量选择目标
            dirt_per_cell = strategy.calculate_dirt_per_cell()
            current_dirt_count = dirt_per_cell.get(current_grid, 0)
            threshold = 10  # 可调整阈值
            if current_dirt_count <= threshold:
                bot.a_star_target = strategy.find_most_dirty_cell(current_grid)
            else:
                bot.a_star_target = strategy.find_nearest_dirt(current_grid)


            if bot.a_star_target is None:
                bot.vl = bot.vr = 0.0
                return
            bot.a_star_path.clear()
        # else:
            # print("a_star_target: exists")
            # return

        if not bot.a_star_path or bot.a_star_path[0] != current_grid:
            bot.a_star_path = Strategy.compute_a_star_path(current_grid, bot.a_star_target, bot.dirt_list)

        if bot.a_star_path:
            next_cell = bot.a_star_path[0]
            target_x = next_cell[0] * cell_size + cell_size / 2
            target_y = next_cell[1] * cell_size + cell_size / 2

            desired_angle = math.atan2(target_y - bot.y, target_x - bot.x)
            angle_diff = (desired_angle - bot.theta + math.pi) % (2 * math.pi) - math.pi

            if abs(angle_diff) < 0.1:
                bot.vl = bot.vr = 5.0
            elif angle_diff > 0:
                bot.vl, bot.vr = 2.0, 5.0
            else:
                bot.vl, bot.vr = 5.0, 2.0

            threshold = max(5, (bot.vl + bot.vr) / 2 * 1.2)
            if math.hypot(bot.x - target_x, bot.y - target_y) < threshold:
                bot.a_star_path.pop(0)
                if not bot.a_star_path:
                    bot.a_star_target = None
        else:
            bot.vl = bot.vr = 5.0
