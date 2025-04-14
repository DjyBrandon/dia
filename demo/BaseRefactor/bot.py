import math
import random
import numpy as np
from canvas_object import CanvasObject
from charger import Charger
from config import Config
from dirt import Dirt
from cat import Cat

# 机器人类，继承自 CanvasObject，用于在画布上模拟清洁机器人
class Bot(CanvasObject):
    """机器人类，代表一个清洁机器人"""

    def __init__(self, name, canvas_p):
        """初始化机器人
        
        参数：
            name: 机器人名称
            canvas_p: 绘图画布对象
        """
        super().__init__()
        # 随机初始化机器人位置在规定范围内
        self.name = name  # 保存机器人名称
        self.x = random.randint(Config.BOT_X_MIN.value, Config.BOT_X_MAX.value)  # 随机生成 x 坐标
        self.y = random.randint(Config.BOT_Y_MIN.value, Config.BOT_Y_MAX.value)  # 随机生成 y 坐标
        self.canvas = canvas_p  # 记录画布引用
        # 创建一个 10x10 的地图矩阵，记录机器人的探索区域
        self.map = np.zeros((Config.MAP_WIDTH.value, Config.MAP_HEIGHT.value))
        self.sensor_positions = None  # 传感器位置初始为空
        # 随机初始化机器人的朝向（角度范围在 0 到 2π 之间）
        self.theta = random.uniform(Config.BOT_THETA_MIN.value, Config.BOT_THETA_MAX.value)
        self.ll = 60  # 车轴宽度，用于运动学计算
        self.vl = 0.0  # 左轮速度初始为 0
        self.vr = 0.0  # 右轮速度初始为 0
        self.battery = Config.BOT_BATTERY_CAPACITY.value  # 电池初始容量

        self.turning = 0  # 当前转向的剩余时间
        self.moving = random.randrange(50, 100)  # 直行剩余时间（随机）
        self.currently_turning = False  # 标记是否处于转向状态

        self.is_turning = False
        self.boundary_turn_count = 0
        self.boundary_buffer = 20  # 边界缓冲距离

    def brain(self, charger_l, charger_r):
        """机器人决策逻辑，根据充电站传感器读数来决定基本运动状态
        
        参数：
            charger_l: 左侧充电站传感器读数
            charger_r: 右侧充电站传感器读数
        """
        if self.is_turning:
            return  # 转向时跳过常规决策
        if self.currently_turning:
            self.vl = -2.0  # 转向时左轮倒退
            self.vr = 2.0   # 转向时右轮正转
            self.turning -= 1  # 减少转向剩余时间
        else:
            self.vl = 5.0  # 直行状态时两轮同速
            self.vr = 5.0
            self.moving -= 1  # 减少直行剩余时间

        # 判断是否需要切换运动模式（从直行转为转向）
        if self.moving == 0 and not self.currently_turning:
            self.turning = random.randrange(20, 40)  # 随机设定转向时间
            self.currently_turning = True
        # 判断转向结束后切换回直行模式
        if self.turning == 0 and self.currently_turning:
            self.moving = random.randrange(50, 100)
            self.currently_turning = False

        # 电池管理：电量较低时调整行为向充电站靠近
        if self.battery < 800:
            if charger_r > charger_l:
                self.vl = 2.0
                self.vr = -2.0
            elif charger_r < charger_l:
                self.vl = -2.0
                self.vr = 2.0
            if abs(charger_r - charger_l) < charger_l * 0.1:
                self.vl = 5.0
                self.vr = 5.0

        # 当充电站强度足够且电池未满时，停止运动
        if charger_l + charger_r > 200 and self.battery < Config.BOT_BATTERY_CAPACITY.value:
            self.vl = 0.0
            self.vr = 0.0

    def avoid_cats(self, cat_list):
        """躲避猫的逻辑，参考 reactToDanger 策略
        
        参数：
            cat_list: 猫的对象列表
        """
        base_speed = 8.0  # 定义基础速度
        # 遍历所有猫对象，检测是否处于避让范围内
        for cat in cat_list:
            distance = self.distance_to(cat)  # 计算机器人到猫的距离
            if distance < Config.CAT_AVOID_DISTANCE.value:  # 如果距离小于预设避让距离
                # 构造威胁向量（从机器人指向猫）
                threat_vector = (cat.x - self.x, cat.y - self.y)
                # 计算威胁方向的角度
                threat_angle = math.atan2(threat_vector[1], threat_vector[0])
                current_angle = self.theta  # 当前机器人的朝向
                # 计算逃生角：向右转90度，即逃生方向
                escape_angle = threat_angle + math.pi / 2
                # 计算当前朝向与逃生方向的角度差，并归一化到[-π, π]
                angle_diff = (escape_angle - current_angle + math.pi) % (2 * math.pi) - math.pi
                # 根据角度差计算转向比例，放大效果（乘以1.5）
                turn_ratio = np.clip(angle_diff / math.pi, -1, 1) * 1.5
                # 根据转向比例设置左右轮速度
                self.vl = base_speed * (1 - turn_ratio)
                self.vr = base_speed * (1 + turn_ratio)
                # 注意：不使用 break 以便持续检测所有猫（如果有多个威胁时后续猫的检测会覆盖之前的调整）
                
    def draw(self, canvas):
        """在画布上绘制机器人的图形表示
        
        参数：
            canvas: 绘图画布对象
        """
        # 根据当前位置和朝向计算机器人的八个顶点坐标
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
        canvas.create_polygon(points, fill="blue", tags=self.name)  # 绘制机器人主体为蓝色多边形

        # 计算传感器位置（用于其他感知操作）
        self.sensor_positions = [
            (self.x + 20 * math.sin(self.theta)) + 30 * math.sin((math.pi / 2.0) - self.theta),
            (self.y - 20 * math.cos(self.theta)) + 30 * math.cos((math.pi / 2.0) - self.theta),
            (self.x - 20 * math.sin(self.theta)) + 30 * math.sin((math.pi / 2.0) - self.theta),
            (self.y + 20 * math.cos(self.theta)) + 30 * math.cos((math.pi / 2.0) - self.theta),
        ]

        # 绘制机器人中心的金色圆形，显示电池电量
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

        # 绘制左轮（红色）
        wheel1PosX = self.x - 30 * math.sin(self.theta)
        wheel1PosY = self.y + 30 * math.cos(self.theta)
        canvas.create_oval(
            wheel1PosX - 3,
            wheel1PosY - 3,
            wheel1PosX + 3,
            wheel1PosY + 3,
            fill="red", tags=self.name
        )

        # 绘制右轮（绿色）
        wheel2PosX = self.x + 30 * math.sin(self.theta)
        wheel2PosY = self.y - 30 * math.cos(self.theta)
        canvas.create_oval(
            wheel2PosX - 3,
            wheel2PosY - 3,
            wheel2PosX + 3,
            wheel2PosY + 3,
            fill="green", tags=self.name
        )

        # 绘制两个传感器（黄色），用于视觉或其他感知模拟
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
        """计算机器人到目标物体的角度差
        
        参数：
            target: 目标物体（可以是猫或其他对象，要求具有 x, y 属性）
        返回：
            float: 目标相对于机器人当前朝向的角度差（弧度）
        """
        dx = target.x - self.x
        dy = target.y - self.y
        return math.atan2(dy, dx) - self.theta

    def move(self, canvas, registry_passives, dt):
        """更新机器人位置和状态
        
        使用差动驱动模型计算机器人的新位置和朝向，并更新地图及重绘
        
        参数：
            canvas: 绘图画布对象
            registry_passives: 被动对象注册表（包含充电站、猫等）
            dt: 时间步长
        """
        # 消耗电池
        if self.battery > 0:
            self.battery -= 1
        if self.battery == 0:
            self.vl = 0
            self.vr = 0

        # 添加边界预测逻辑
        if not self.is_turning:
            # 预测下一帧坐标
            avg_speed = (self.vl + self.vr) / 2
            lookahead = 5  # 预测5帧后的位置
            temp_x = self.x + avg_speed * math.cos(self.theta) * dt * lookahead
            temp_y = self.y + avg_speed * math.sin(self.theta) * dt * lookahead
            # 动态缓冲距离计算
            dynamic_buffer = self.boundary_buffer + abs(avg_speed) * 2
            if (temp_x < Config.BOT_X_MIN.value - dynamic_buffer or
                    temp_x > Config.BOT_X_MAX.value + dynamic_buffer or
                    temp_y < Config.BOT_Y_MIN.value - dynamic_buffer or
                    temp_y > Config.BOT_Y_MAX.value + dynamic_buffer):
                self.init_boundary_turn()
                return

        # 处理转向状态
        if self.is_turning:
            self.boundary_turn_count -= 1

            # 速度衰减机制
            decay = 0.95 if self.boundary_turn_count > 5 else 0.85
            self.vl *= decay
            self.vr *= decay

            # 强坐标修正
            self.x = np.clip(self.x,
                             Config.BOT_X_MIN.value + 30,  # 保留30像素安全距离
                             Config.BOT_X_MAX.value - 30)
            self.y = np.clip(self.y,
                             Config.BOT_Y_MIN.value + 30,
                             Config.BOT_Y_MAX.value - 30)

            # 角度更新
            omega = (self.vl - self.vr) / self.ll
            self.theta += omega * dt
            self.theta %= 2 * math.pi

            # 转向终止条件
            if self.boundary_turn_count <= 0 or abs(omega) < 0.1:
                self.is_turning = False
                self.vl, self.vr = 5.0, 5.0  # 恢复默认运动

            canvas.delete(self.name)
            self.draw(canvas)
            return

        # 检查充电站：若接近充电站且电量较低，则增加电量
        for rr in registry_passives:
            if isinstance(rr, Charger) and self.distance_to(rr) < Config.CHARGER_DISTANCE.value and self.battery < Config.BOT_BATTERY_CAPACITY.value:
                self.battery += 10

        # 提取所有猫对象并调用躲避猫逻辑
        cat_list = [rr for rr in registry_passives if isinstance(rr, Cat)]
        self.avoid_cats(cat_list)

        # 差动驱动运动学计算部分
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
        """更新机器人的探索地图，并重绘地图
        """
        xMapPosition = int(math.floor(self.x / 100))
        yMapPosition = int(math.floor(self.y / 100))
        self.map[xMapPosition][yMapPosition] = 1
        self.draw_map()

    def draw_map(self):
        """在画布上绘制探索地图
        """
        for xx in range(10):
            for yy in range(10):
                if self.map[xx][yy] == 1:
                    self.canvas.create_rectangle(
                        100 * xx, 100 * yy,
                        100 * xx + 100, 100 * yy + 100,
                        fill="pink", width=0, tags="map"
                    )
        # 上边界（水平线）
        self.canvas.create_line(
            Config.BOT_X_MIN.value, Config.BOT_Y_MIN.value,  # 起点 (左,上)
            Config.BOT_X_MAX.value, Config.BOT_Y_MIN.value,  # 终点 (右,上)
            fill="red", width=2, tags="border"
        )
        # 下边界（水平线）
        self.canvas.create_line(
            Config.BOT_X_MIN.value, Config.BOT_Y_MAX.value,  # 起点 (左,下)
            Config.BOT_X_MAX.value, Config.BOT_Y_MAX.value,  # 终点 (右,下)
            fill="red", width=2, tags="border"
        )
        # 左边界（垂直线）
        self.canvas.create_line(
            Config.BOT_X_MIN.value, Config.BOT_Y_MIN.value,  # 起点 (左,上)
            Config.BOT_X_MIN.value, Config.BOT_Y_MAX.value,  # 终点 (左,下)
            fill="red", width=2, tags="border"
        )
        # 右边界（垂直线）
        self.canvas.create_line(
            Config.BOT_X_MAX.value, Config.BOT_Y_MIN.value,  # 起点 (右,上)
            Config.BOT_X_MAX.value, Config.BOT_Y_MAX.value,  # 终点 (右,下)
            fill="red", width=2, tags="border"
        )
        self.canvas.tag_lower("map")  # 确保地图位于底层

    def sense_charger(self, registry_passives):
        """检测充电站，通过传感器估计左右充电站信号强度
        
        参数：
            registry_passives: 被动对象注册表
        返回：
            tuple: (左侧信号强度, 右侧信号强度)
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
        """计算机器人到指定对象的欧几里得距离
        
        参数：
            obj: 目标对象（需实现 get_location 方法）
        返回：
            float: 距离值
        """
        xx, yy = obj.get_location()
        return math.sqrt((self.x - xx) ** 2 + (self.y - yy) ** 2)

    def collect_dirt(self, canvas, registry_passives, counter):
        """收集机器人附近的垃圾
        
        参数：
            canvas: 绘图画布对象
            registry_passives: 被动对象注册表（包含垃圾对象）
            counter: 计数器对象，用于统计收集数量
        返回：
            list: 更新后的被动对象注册表（删除已收集的垃圾）
        """
        to_delete = []
        for idx, rr in enumerate(registry_passives):
            if isinstance(rr, Dirt):
                if self.distance_to(rr) < 30:
                    canvas.delete(rr.name)
                    to_delete.append(idx)
                    counter.item_collected()
        for ii in sorted(to_delete, reverse=True):
            del registry_passives[ii]
        return registry_passives

    def _check_battery(self):
        """检查电池电量，确保在有效范围内
        """
        if self.battery < 0:
            self.battery = 0
        elif self.battery > Config.BOT_BATTERY_CAPACITY.value:
            self.battery = Config.BOT_BATTERY_CAPACITY.value

    def init_boundary_turn(self):
        """初始化180度转向
        """
        self.is_turning = True
        turn_speed = 15.0  # 提高转向    # 根据当前方向确定最优转向方向
        current_angle = self.theta % (2 * math.pi)
        if current_angle < math.pi / 2 or current_angle > 3 * math.pi / 2:
            self.vl = turn_speed  # 向右转
            self.vr = -turn_speed
        else:
            self.vl = -turn_speed  # 向左转
            self.vr = turn_speed

        # 精确计算转向时间
        omega = abs((self.vl - self.vr) / self.ll)
        required_frames = math.ceil(math.pi / omega)
        self.boundary_turn_count = required_frames + 3  # 增加安全余量

        # 强制坐标修正
        self.x = np.clip(self.x,
                         Config.BOT_X_MIN.value + 50,  # 碰撞后强制保持50像素距离
                         Config.BOT_X_MAX.value - 50)
        self.y = np.clip(self.y,
                         Config.BOT_Y_MIN.value + 50,  # Y轴最小值处理
                         Config.BOT_Y_MAX.value - 50)