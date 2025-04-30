import math
import random
from typing import Tuple

import numpy as np
import heapq

from BaseRefactor.strategy import Strategy
from canvas_object import CanvasObject
from charger import Charger
from config import Config
from dirt import Dirt
from cat import Cat


class Bot(CanvasObject):
    def __init__(self, name, canvas_p, dirt_list):
        """
        Initialize the robot with its name, canvas, and list of dirt positions.

        Args:
            name (str): The name of the robot.
            canvas_p: The canvas object for drawing or visualization.
            dirt_list (list): A list of dirt objects or positions the robot should clean.
        """
        super().__init__()
        self.name = name
        self.x, self.y = self.generate_random_position()
        # self.x = random.randint(Config.BOT_X_MIN.value, Config.BOT_X_MAX.value)
        # self.y = random.randint(Config.BOT_Y_MIN.value, Config.BOT_Y_MAX.value)
        self.canvas = canvas_p
        self.map = np.zeros((Config.MAP_WIDTH.value, Config.MAP_HEIGHT.value))
        self.sensor_positions = None
        self.theta = random.uniform(Config.BOT_THETA_MIN.value, Config.BOT_THETA_MAX.value)
        self.ll = 60
        self.vl = 0.0
        self.vr = 0.0
        self.battery = Config.BOT_BATTERY_CAPACITY.value

        self.turning = 0
        self.moving = random.randrange(50, 100)
        self.currently_turning = False

        self.is_turning = False
        self.boundary_turn_count = 0
        self.boundary_buffer = 20

        self.dirt_list = dirt_list
        self.strategy = Strategy(dirt_list)  # 初始化策略类
        self.brain_strategy = self.strategy.a_star_strategy  # 使用策略类的方法
        self.a_star_path = []
        self.a_star_target = None

        # self.path_history = []  # 新增：存储轨迹坐标的列表
        # self.path_color = "#FF5722"  # 轨迹颜色（橙色）
        # self.path_max_length = 1000  # 轨迹最大长度（避免内存溢出）

    def brain(self, charger_l, charger_r):
        """
        Execute the robot's decision-making strategy.

        This method delegates control to the current brain strategy function,
        which determines the robot's actions based on sensor inputs.

        Args:
            charger_l (float): Sensor reading from the left charger detector.
            charger_r (float): Sensor reading from the right charger detector.
        """
        self.brain_strategy(self, charger_l, charger_r)


    @staticmethod
    def generate_random_position() -> tuple[int, int] | None:
        """
        生成一个不在任何障碍物范围内的随机位置
        :return: (x, y) 坐标元组
        :raises RuntimeError: 如果无法在尝试次数内找到有效位置
        """
        def is_valid_position(x: int, y: int) -> bool:
            """检查坐标是否在任何障碍物内"""
            if ((280 <= x <= 420 and 280 <= y <= 520)
            or (580 <= x <= 720 and 280 <= y <= 420)
            or (480 <= x <= 620 and 680 <= y <= 820)):
                    return False
            return True

        for _ in range(1000):
            x = random.randint(Config.BOT_X_MIN.value, Config.BOT_X_MAX.value)
            y = random.randint(Config.BOT_Y_MIN.value, Config.BOT_Y_MAX.value)
            if is_valid_position(x, y):
                return x, y


    def avoid_cats(self, cat_list):
        """
        Adjust wheel speeds to steer away from nearby cats by computing an escape angle
        perpendicular to the threat vector, ensuring safe avoidance behavior.
        """
        base_speed = 8.0

        for cat in cat_list:
            print(f"cat: {cat}")
            distance = self.distance_to(cat)
            if distance < Config.CAT_AVOID_DISTANCE.value:
                threat_vector = (cat.x - self.x, cat.y - self.y)
                threat_angle = math.atan2(threat_vector[1], threat_vector[0])
                current_angle = self.theta
                escape_angle = threat_angle + math.pi / 2
                angle_diff = (escape_angle - current_angle + math.pi) % (2 * math.pi) - math.pi
                turn_ratio = np.clip(angle_diff / math.pi, -1, 1) * 1.5
                self.vl = base_speed * (1 - turn_ratio)
                self.vr = base_speed * (1 + turn_ratio)

    def draw(self, canvas):
        """
        Render the robot on the canvas, including its body, wheels, sensors, and battery level.
        Calculates positions based on the robot's current orientation (theta) and position (x, y).
        """
        points = [
            (self.x + 30 * math.sin(self.theta)) - 30 * math.sin((math.pi / 2.0) - self.theta),
            (self.y - 30 * math.cos(self.theta)) - 30 * math.cos((math.pi / 2.0) - self.theta),
            (self.x - 30 * math.sin(self.theta)) - 30 * math.sin((math.pi / 2.0) - self.theta),
            (self.y + 30 * math.cos(self.theta)) - 30 * math.cos((math.pi / 2.0) - self.theta),
            (self.x - 30 * math.sin(self.theta)) + 30 * math.sin((math.pi / 2.0) - self.theta),
            (self.y + 30 * math.cos(self.theta)) + 30 * math.cos((math.pi / 2.0) - self.theta),
            (self.x + 30 * math.sin(self.theta)) + 30 * math.sin((math.pi / 2.0) - self.theta),
            (self.y - 30 * math.cos(self.theta)) + 30 * math.cos((math.pi / 2.0) - self.theta),
        ]
        canvas.create_polygon(points, fill="blue", tags=self.name)

        self.sensor_positions = [
            (self.x + 20 * math.sin(self.theta)) + 30 * math.sin((math.pi / 2.0) - self.theta),
            (self.y - 20 * math.cos(self.theta)) + 30 * math.cos((math.pi / 2.0) - self.theta),
            (self.x - 20 * math.sin(self.theta)) + 30 * math.sin((math.pi / 2.0) - self.theta),
            (self.y + 20 * math.cos(self.theta)) + 30 * math.cos((math.pi / 2.0) - self.theta),
        ]

        centre1PosX = self.x
        centre1PosY = self.y
        canvas.create_oval(
            centre1PosX - 15,
            centre1PosY - 15,
            centre1PosX + 15,
            centre1PosY + 15,
            fill="gold", tags=self.name
        )
        canvas.create_text(self.x, self.y, text=str(self.battery), tags=self.name)

        wheel1PosX = self.x - 30 * math.sin(self.theta)
        wheel1PosY = self.y + 30 * math.cos(self.theta)
        canvas.create_oval(
            wheel1PosX - 3,
            wheel1PosY - 3,
            wheel1PosX + 3,
            wheel1PosY + 3,
            fill="red", tags=self.name
        )

        wheel2PosX = self.x + 30 * math.sin(self.theta)
        wheel2PosY = self.y - 30 * math.cos(self.theta)
        canvas.create_oval(
            wheel2PosX - 3,
            wheel2PosY - 3,
            wheel2PosX + 3,
            wheel2PosY + 3,
            fill="green", tags=self.name
        )

        sensor1PosX = self.sensor_positions[0]
        sensor1PosY = self.sensor_positions[1]
        sensor2PosX = self.sensor_positions[2]
        sensor2PosY = self.sensor_positions[3]
        canvas.create_oval(
            sensor1PosX - 3,
            sensor1PosY - 3,
            sensor1PosX + 3,
            sensor1PosY + 3,
            fill="yellow", tags=self.name
        )
        canvas.create_oval(
            sensor2PosX - 3,
            sensor2PosY - 3,
            sensor2PosX + 3,
            sensor2PosY + 3,
            fill="yellow", tags=self.name
        )

    def angle_to(self, target):
        """
        Calculate the angle between the robot's current orientation and the direction
        towards a target point.

        Args:
            target (object): The target object with 'x' and 'y' attributes representing
                            its coordinates.

        Returns:
            float: The angle in radians between the robot's current orientation and the
                direction towards the target. A positive value indicates a counter-
                clockwise direction, while a negative value indicates a clockwise direction.
        """
        dx = target.x - self.x
        dy = target.y - self.y
        return math.atan2(dy, dx) - self.theta

    def move(self, canvas, registry_passives, dt):
        """
        Update the robot's position, velocity, and other states based on its current movement and interaction with the environment.

        - Decreases battery over time and stops movement when battery is empty.
        - Checks if the robot is about to go out of bounds and adjusts its path to avoid collision.
        - Handles boundary turns by reducing velocity and updating the robot's position to stay within allowed boundaries.
        - Interacts with passive objects like chargers to recharge the battery when close enough.
        - Avoids cats if detected within a specific range.
        - Updates robot's position and orientation according to its wheel velocities and turn rates.
        - Redraws the robot's updated position on the canvas.
        """
        # 更新机器人坐标后记录轨迹点
        # if len(self.path_history) > self.path_max_length:
        #     self.path_history.pop(0)  # 删除最旧的点，控制内存
        # self.path_history.append((self.x, self.y))  # 记录当前坐标

        if self.battery > 0:
            self.battery -= 1
        if self.battery == 0:
            self.vl = 0
            self.vr = 0

        if not self.is_turning:
            avg_speed = (self.vl + self.vr) / 2
            lookahead = 5
            temp_x = self.x + avg_speed * math.cos(self.theta) * dt * lookahead
            temp_y = self.y + avg_speed * math.sin(self.theta) * dt * lookahead
            dynamic_buffer = self.boundary_buffer + abs(avg_speed) * 2

            if (temp_x < Config.BOT_X_MIN.value - dynamic_buffer or
                    temp_x > Config.BOT_X_MAX.value + dynamic_buffer or
                    temp_y < Config.BOT_Y_MIN.value - dynamic_buffer or
                    temp_y > Config.BOT_Y_MAX.value + dynamic_buffer or

                    ((300 - dynamic_buffer < temp_x < 400 + dynamic_buffer) and
                     (300 - dynamic_buffer < temp_y < 500 + dynamic_buffer)) or
                    ((600 - dynamic_buffer < temp_x < 700 + dynamic_buffer) and
                     (300 - dynamic_buffer < temp_y < 400 + dynamic_buffer)) or
                    ((500 - dynamic_buffer < temp_x < 600 + dynamic_buffer) and
                     (700 - dynamic_buffer < temp_y < 800 + dynamic_buffer))

            ):
                self.init_boundary_turn()
                return

        if self.is_turning:
            self.boundary_turn_count -= 1

            decay = 0.95 if self.boundary_turn_count > 5 else 0.85
            self.vl *= decay
            self.vr *= decay

            self.x = np.clip(self.x,
                             Config.BOT_X_MIN.value + 30,
                             Config.BOT_X_MAX.value - 30)
            self.y = np.clip(self.y,
                             Config.BOT_Y_MIN.value + 30,
                             Config.BOT_Y_MAX.value - 30)

            omega = (self.vl - self.vr) / self.ll
            self.theta += omega * dt
            self.theta %= 2 * math.pi

            if self.boundary_turn_count <= 0 or abs(omega) < 0.1:
                self.is_turning = False
                self.vl, self.vr = 5.0, 5.0

            canvas.delete(self.name)
            self.draw(canvas)
            return

        for rr in registry_passives:
            if isinstance(rr, Charger) and self.distance_to(
                    rr) < Config.CHARGER_DISTANCE.value and self.battery < Config.BOT_BATTERY_CAPACITY.value:
                self.battery += 10

        cat_list = [rr for rr in registry_passives if isinstance(rr, Cat)]
        self.avoid_cats(cat_list)

        if self.vl == self.vr and not self.is_turning:
            R = 0
        else:
            R = (self.ll / 2.0) * ((self.vr + self.vl) / (self.vl - self.vr))
        omega = (self.vl - self.vr) / self.ll
        ICCx = self.x - R * math.sin(self.theta)
        ICCy = self.y + R * math.cos(self.theta)
        m = np.matrix([
            [math.cos(omega * dt), -math.sin(omega * dt), 0],
            [math.sin(omega * dt), math.cos(omega * dt), 0],
            [0, 0, 1],
        ])
        v1 = np.matrix([[self.x - ICCx], [self.y - ICCy], [self.theta]])
        v2 = np.matrix([[ICCx], [ICCy], [omega * dt]])
        new_v = np.add(np.dot(m, v1), v2)
        newX = new_v.item(0)
        newY = new_v.item(1)
        newTheta = new_v.item(2)
        newTheta = newTheta % (2.0 * math.pi)
        self.x = newX
        self.y = newY
        self.theta = newTheta
        if self.vl == self.vr:
            self.x += self.vr * math.cos(self.theta)
            self.y += self.vr * math.sin(self.theta)
        self.update_map()
        canvas.delete(self.name)
        self.draw(canvas)

    def update_map(self):
        """
        Updates the robot's position on the occupancy grid map.

        This method calculates the robot's current grid cell based on its (x, y) coordinates,
        then sets the corresponding cell in the map to 1, indicating the robot's presence.
        After updating the map, it calls the draw_map method to visually reflect the change.

        The grid cells are determined by dividing the robot's coordinates by the cell size (100 units).
        The resulting indices are used to access and modify the appropriate cell in the map.
        """
        xMapPosition = int(math.floor(self.x / 100))
        yMapPosition = int(math.floor(self.y / 100))
        self.map[xMapPosition][yMapPosition] = 1
        self.draw_map()

    def draw_map(self):
        """
        Draws the current map on the canvas, displaying the robot's path and boundaries.

        This method iterates through the 2D map and draws rectangles in areas where the robot
        has passed, as indicated by the value of '1' in the map. It also draws red border lines
        around the designated boundary of the map.

        The rectangles are drawn in a grid pattern, and the border lines are drawn using specific
        coordinates from the configuration.
        """
        self.canvas.delete("map")
        for xx in range(10):
            for yy in range(10):
                if self.map[xx][yy] == 1:
                    self.canvas.create_rectangle(
                        100 * xx, 100 * yy,
                        100 * xx + 100, 100 * yy + 100,
                        fill="pink", width=0, tags="map"
                    )
        self.canvas.create_line(
            Config.BOT_X_MIN.value, Config.BOT_Y_MIN.value,
            Config.BOT_X_MAX.value, Config.BOT_Y_MIN.value,
            fill="red", width=2, tags="border"
        )
        self.canvas.create_line(
            Config.BOT_X_MIN.value, Config.BOT_Y_MAX.value,
            Config.BOT_X_MAX.value, Config.BOT_Y_MAX.value,
            fill="red", width=2, tags="border"
        )
        self.canvas.create_line(
            Config.BOT_X_MIN.value, Config.BOT_Y_MIN.value,
            Config.BOT_X_MIN.value, Config.BOT_Y_MAX.value,
            fill="red", width=2, tags="border"
        )

        self.canvas.create_line(
            Config.BOT_X_MAX.value, Config.BOT_Y_MIN.value,
            Config.BOT_X_MAX.value, Config.BOT_Y_MAX.value,
            fill="red", width=2, tags="border"
        )
        self.canvas.tag_lower("map")

        # 删除旧轨迹
        # self.canvas.delete("bot_path")

        # if len(self.path_history) >= 2:
        #     # 将轨迹点转换为画布坐标序列 [x1,y1, x2,y2,...]
        #     path_points = []
        #     for x, y in self.path_history:
        #         path_points.extend([x, y])
        #
        #     # 绘制轨迹线（半透明橙色，宽度渐变）
        #     self.canvas.create_line(
        #         *path_points,
        #         fill=self.path_color,
        #         width=2,
        #         tags="bot_path",
        #         stipple="gray50",  # 可选：虚线样式
        #         smooth=True  # 曲线平滑
        #     )

    def sense_charger(self, registry_passives):
        """
        Detects the presence of chargers near the robot using light intensity sensors.

        This method calculates the light intensity detected by the robot's left and right sensors
        based on the inverse square law, which states that light intensity decreases with the square
        of the distance from the light source. The method iterates through all passive objects in the
        registry, identifies chargers, and computes the light intensity received by each sensor.

        Args:
            registry_passives (list): A list of passive objects in the environment, such as chargers.

        Returns:
            tuple: A tuple containing two float values representing the light intensity detected by
                the left and right sensors, respectively.
        """
        lightL = 0.0
        lightR = 0.0
        for pp in registry_passives:
            if isinstance(pp, Charger):
                lx, ly = pp.get_location()
                distanceL = math.sqrt(
                    (lx - self.sensor_positions[0]) ** 2 +
                    (ly - self.sensor_positions[1]) ** 2
                )
                distanceR = math.sqrt(
                    (lx - self.sensor_positions[2]) ** 2 +
                    (ly - self.sensor_positions[3]) ** 2
                )
                lightL += 200000 / (distanceL * distanceL)
                lightR += 200000 / (distanceR * distanceR)
        return lightL, lightR

    def distance_to(self, obj):
        """
        Calculates the Euclidean distance between the robot and another object.

        This method computes the straight-line distance between the robot's current position
        and the position of the specified object. The Euclidean distance formula is used,
        which is derived from the Pythagorean theorem.

        Args:
            obj (object): The target object to which the distance is to be calculated.
                        It must have a `get_location()` method that returns its (x, y) coordinates.

        Returns:
            float: The Euclidean distance between the robot and the target object.
        """
        xx, yy = obj.get_location()
        return math.sqrt((self.x - xx) ** 2 + (self.y - yy) ** 2)

    def collect_dirt(self, canvas, registry_passives, counter):
        """
        Collects nearby dirt objects within a specified radius and updates the canvas and registry.

        This method checks for dirt objects in the registry that are within a certain distance from
        the robot. If a dirt object is within range, it is removed from the canvas, deleted from the
        registry, and the collection counter is updated. Additionally, if the dirt is part of the robot's
        internal dirt list, it is removed, and the robot's A* path is cleared.

        Args:
            canvas (tkinter.Canvas): The canvas on which the robot and dirt objects are drawn.
            registry_passives (list): A list of passive objects in the environment, such as dirt and chargers.
            counter (Counter): An object responsible for tracking the number of collected items.

        Returns:
            list: The updated registry of passive objects after the collection process.
        """
        to_delete = []
        for idx, rr in enumerate(registry_passives):
            if isinstance(rr, Dirt):
                if self.distance_to(rr) < 30:
                    canvas.delete(rr.name)
                    to_delete.append(idx)
                    counter.item_collected()
                    if rr in self.dirt_list:
                        self.dirt_list.remove(rr)
                        self.a_star_target = None
                        self.a_star_path.clear()
        for ii in sorted(to_delete, reverse=True):
            del registry_passives[ii]
        return registry_passives

    def _check_battery(self):
        """
        Collects nearby dirt objects within a specified radius and updates the canvas and registry.

        This method checks for dirt objects in the registry that are within a certain distance from
        the robot. If a dirt object is within range, it is removed from the canvas, deleted from the
        registry, and the collection counter is updated. Additionally, if the dirt is part of the robot's
        internal dirt list, it is removed, and the robot's A* path is cleared.

        Args:
            canvas (tkinter.Canvas): The canvas on which the robot and dirt objects are drawn.
            registry_passives (list): A list of passive objects in the environment, such as dirt and chargers.
            counter (Counter): An object responsible for tracking the number of collected items.

        Returns:
            list: The updated registry of passive objects after the collection process.
        """
        if self.battery < 0:
            self.battery = 0
        elif self.battery > Config.BOT_BATTERY_CAPACITY.value:
            self.battery = Config.BOT_BATTERY_CAPACITY.value


    def init_boundary_turn(self):
        """
        Initializes a boundary turn when the robot approaches the edge of the defined area.

        This method calculates the appropriate wheel speeds to perform a turn that brings the robot
        back toward the center of the defined boundary. The turn direction is determined based on the
        robot's current orientation, and the turn duration is calculated to achieve a 90-degree turn.

        The robot's position is also constrained within the defined boundaries to prevent it from
        moving outside the allowed area.

        Args:
            None

        Returns:
            None
        """
        self.is_turning = True
        turn_speed = 15.0
        current_angle = self.theta % (2 * math.pi)
        if current_angle < math.pi / 2 or current_angle > 3 * math.pi / 2:
            self.vl = turn_speed
            self.vr = -turn_speed
        else:
            self.vl = -turn_speed
            self.vr = turn_speed

        omega = abs((self.vl - self.vr) / self.ll)
        required_frames = math.ceil(math.pi / omega)
        self.boundary_turn_count = required_frames + 3

        self.x = np.clip(self.x,
                         Config.BOT_X_MIN.value + 50,
                         Config.BOT_X_MAX.value - 50)
        self.y = np.clip(self.y,
                         Config.BOT_Y_MIN.value + 50,
                         Config.BOT_Y_MAX.value - 50)
