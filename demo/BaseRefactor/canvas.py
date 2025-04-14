import tkinter as tk
import sys
from bot import Bot
from charger import Charger
from config import Config
from counter import Counter
from dirt import Dirt
from wifihub import WiFiHub
from cat import Cat

def initialize(window):
    """初始化窗口和画布

    Args:
        window: tkinter窗口对象

    Returns:
        tkinter.Canvas: 创建的画布对象
    """
    window.resizable(True, True)  # 允许调整窗口大小
    # 创建指定大小的画布
    canvas = tk.Canvas(
        window,
        width=Config.CANVAS_WIDTH.value,
        height=Config.CANVAS_HEIGHT.value,
    )
    canvas.pack()  # 将画布添加到窗口
    return canvas


def register(canvas):
    """注册所有仿真对象

    创建和注册机器人、充电站、WiFi集线器和垃圾

    Args:
        canvas: 绘图画布对象

    Returns:
        tuple: 包含主动对象列表、被动对象列表和计数器
    """
    registry_actives = []  # 主动对象列表（机器人）
    registry_passives = []  # 被动对象列表（充电站、垃圾等）

    # 创建机器人 1
    num_bots = Config.BOT_NUM.value
    for i in range(0, num_bots):
        bot = Bot("Bot" + str(i), canvas)
        registry_actives.append(bot)
        bot.draw(canvas)

    # 创建充电站
    charger = Charger("Charger")
    registry_passives.append(charger)
    charger.draw(canvas)

    # 创建WiFi集线器
    hub1 = WiFiHub("Hub1", 950, 50)
    registry_passives.append(hub1)
    hub1.draw(canvas)
    hub2 = WiFiHub("Hub2", 50, 500)
    registry_passives.append(hub2)
    hub2.draw(canvas)

    # 创建垃圾 300
    num_dirt = Config.DIRT_NUM.value
    for i in range(0, num_dirt):
        dirt = Dirt("Dirt" + str(i))
        registry_passives.append(dirt)
        dirt.draw(canvas)

    # 创建猫（障碍物）
    num_cats = Config.CAT_NUM.value  
    if num_cats > 0:
        for i in range(num_cats):
            cat = Cat("Cat" + str(i))
            registry_passives.append(cat)
            cat.draw(canvas)

    # 创建计数器
    count = Counter(canvas)

    def handle_button_clicked(x, y, actives):
        """处理鼠标点击事件，移动机器人到点击位置

        Args:
            x: 点击位置x坐标
            y: 点击位置y坐标
            actives: 主动对象列表
        """
        for rr in actives:
            if isinstance(rr, Bot):
                rr.x = x
                rr.y = y

    # 绑定鼠标点击事件
    canvas.bind(
        "<Button-1>",
        lambda event: handle_button_clicked(event.x, event.y, registry_actives),
    )

    return registry_actives, registry_passives, count


def move_it(canvas, registry_actives, registry_passives, counter, moves=0):
    """更新模拟状态，移动机器人并处理交互

    Args:
        canvas: 绘图画布对象
        registry_actives: 主动对象列表
        registry_passives: 被动对象列表
        counter: 计数器对象
        moves: 当前移动步数
    """
    moves += 1  # 增加移动步数

    # 更新所有主动对象（机器人）
    for rr in registry_actives:
        # 获取充电站传感器读数
        chargerIntensityL, chargerIntensityR = rr.sense_charger(
            registry_passives
        )
        # 执行决策逻辑
        rr.brain(chargerIntensityL, chargerIntensityR)
        # 移动机器人
        rr.move(canvas, registry_passives, 1.0)
        # 收集垃圾
        registry_passives = rr.collect_dirt(canvas, registry_passives, counter)

        # 检查是否达到最大步数 500
        num_moves = Config.BOT_MOVES_MAX.value
        if moves > num_moves:
            print(
                "total dirt collected in",
                num_moves,
                "moves is",
                counter.dirt_collected,
            )
            sys.exit()  # 结束程序

    # 50毫秒后再次调用此函数，创建动画效果
    canvas.after(
        50, move_it, canvas, registry_actives, registry_passives, counter, moves
    )
