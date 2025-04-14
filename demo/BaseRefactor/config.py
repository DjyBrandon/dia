from enum import Enum
import math

import numpy as np


class Config(Enum):
    """ 配置类，包含了所有的配置项 """

    # 画布尺寸
    CANVAS_WIDTH = 1000  # 画布宽度，单位像素
    CANVAS_HEIGHT = 1000  # 画布高度，单位像素

    # Map 相关配置
    MAP_WIDTH = 10  # 地图宽度单位
    MAP_HEIGHT = 10  # 地图高度单位

    # 机器人相关配置
    BOT_NUM = 1  # 机器人数量
    BOT_BATTERY_CAPACITY = 2500  # 机器人电池容量
    BOT_V_POSITIVE_MAX = 10  # 机器人正向最大速度
    BOT_X_MIN = 100  # 机器人最小X坐标
    BOT_X_MAX = 900  # 机器人最大X坐标
    BOT_Y_MIN = 100  # 机器人最小Y坐标
    BOT_Y_MAX = 900  # 机器人最大Y坐标
    BOT_THETA_MIN = 0.0  # 机器人最小角度
    BOT_THETA_MAX = 2.0 * math.pi  # 机器人最大角度
    BOT_MOVES_MAX = 550  # 机器人最大移动步数 这里如果不限制的话给np.Inf应该也可以

    # Charger配置
    CHARGER_X_MIN = 100  # 充电站最小X坐标
    CHARGER_X_MAX = 900  # 充电站最大X坐标
    CHARGER_Y_MIN = 100  # 充电站最小Y坐标
    CHARGER_Y_MAX = 900  # 充电站最大Y坐标
    CHARGER_DISTANCE = 80  # 充电站距离机器人最小距离

    # WiFi集线器配置
    WIFI_HUB_X_MIN = 100  # WiFi集线器最小X坐标
    WIFI_HUB_X_MAX = 900  # WiFi集线器最大X坐标
    WIFI_HUB_Y_MIN = 100  # WiFi集线器最小Y坐标
    WIFI_HUB_Y_MAX = 900  # WiFi集线器最大Y坐标

    # Dirt配置
    DIRT_NUM = 2200  # 垃圾数量
    DIRT_X_MIN = 100  # 垃圾最小X坐标
    DIRT_X_MAX = 900  # 垃圾最大X坐标
    DIRT_Y_MIN = 100  # 垃圾最小Y坐标
    DIRT_Y_MAX = 900  # 垃圾最大Y坐标

    # Cat配置
    CAT_NUM = 0
    CAT_AVOID_DISTANCE = 125  # 猫的躲避距离

    # 其他配置
