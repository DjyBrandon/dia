import tkinter as tk
import sys
from bot import Bot
from charger import Charger
from config import Config
from counter import Counter
from dirt import Dirt
from wifihub import WiFiHub
from cat import Cat
from strategy import Strategy
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import time


def initialize(window):
    """Initialize window and canvas

    Args:
        window: tkinter window object

    Returns:
        tkinter.Canvas: The created canvas object
    """
    window.resizable(True, True)
    canvas = tk.Canvas(
        window,
        width=Config.CANVAS_WIDTH.value,
        height=Config.CANVAS_HEIGHT.value,
    )
    canvas.pack()
    canvas.create_rectangle(
        300, 300,
        400, 500,
        fill="green", width=0, tags="item1"
    )
    canvas.create_rectangle(
        600, 300,
        700, 400,
        fill="green", width=0, tags="item2"
    )
    canvas.create_rectangle(
        500, 700,
        600, 800,
        fill="green", width=0, tags="item3"
    )

    return canvas


millis_log_time = int(round(time.time() * 1000))

def plot_dirt_distribution(dirt_list):
    # 网格参数
    GRID_SIZE = 100
    CANVAS_WIDTH = Config.CANVAS_WIDTH.value
    CANVAS_HEIGHT = Config.CANVAS_HEIGHT.value
    NUM_GRIDS_X = CANVAS_WIDTH // GRID_SIZE
    NUM_GRIDS_Y = CANVAS_HEIGHT // GRID_SIZE

    # 初始化计数矩阵
    grid_counts = np.zeros((NUM_GRIDS_Y, NUM_GRIDS_X), dtype=int)
    print(f"grid_counts\n{grid_counts}")

    # 统计每个网格的 dirt 数量
    for dirt in dirt_list:
        grid_x = min(int(dirt.x // GRID_SIZE), NUM_GRIDS_X - 1)
        grid_y = min(int((dirt.y) // GRID_SIZE), NUM_GRIDS_Y - 1)  # 关键转换
        grid_counts[grid_y, grid_x] += 1
    print(f"grid_counts\n{grid_counts}")

    # 绘制热力图
    plt.figure(figsize=(10, 8))
    heatmap = plt.imshow(
        grid_counts,
        cmap="viridis",
        origin="lower",
        extent=[0, CANVAS_WIDTH, 0, CANVAS_HEIGHT],
        aspect="auto",
    )
    plt.colorbar(heatmap, label="Number of Dirt")
    plt.title("Dirt Distribution Heatmap")
    plt.xlabel("X Coordinate (pixels)")
    plt.ylabel("Y Coordinate (pixels)")
    plt.grid(True, color="white", linestyle="--", alpha=0.5)
    plt.savefig(f"figures/{millis_log_time}_dirt_distribution.png")
    plt.show()


def register(canvas):
    """Register all simulation objects

    Create and register robots, chargers, WiFi hubs, and dirt

    Args:
        canvas: Drawing canvas object

    Returns:
        tuple: Contains active objects list, passive objects list, and counter
    """
    registry_actives = []
    registry_passives = []

    num_dirt = Config.DIRT_NUM.value
    for i in range(0, num_dirt):
        dirt = Dirt("Dirt" + str(i))
        registry_passives.append(dirt)
        dirt.draw(canvas)

    dirt_list = [item for item in registry_passives if isinstance(item, Dirt)]
    plot_dirt_distribution(dirt_list)
    # for i, dirt in enumerate(dirt_list, start=1):
    #     print(f"name: {dirt.name}: ({dirt.x}, {dirt.y})")

    # def get_grid_index(x, y):
    #     """返回 (x, y) 所在的网格索引 (grid_x, grid_y)"""
    #     grid_x = x // Config.CELL_SIZE.value
    #     grid_y = y // Config.CELL_SIZE.value
    #     return (grid_x, grid_y)

    # grid_dict = defaultdict(list)
    # # 将 dirt 分配到网格
    # for dirt in dirt_list:
    #     grid_x, grid_y = get_grid_index(dirt.x, dirt.y)
    #     grid_dict[(grid_x, grid_y)].append(dirt)

    # 打印结果
    # for (grid_x, grid_y), dirts in grid_dict.items():
    #     print(f"\nGrid ({grid_x}, {grid_y}) has {len(dirts)} dirts:")
    # for dirt in dirts:
    #     print(f"  - {dirt.name}: ({dirt.x}, {dirt.y})")

    num_bots = Config.BOT_NUM.value
    for i in range(0, num_bots):
        bot = Bot("Bot" + str(i), canvas, dirt_list)
        registry_actives.append(bot)
        bot.draw(canvas)

    charger = Charger("Charger")
    registry_passives.append(charger)
    charger.draw(canvas)

    hub1 = WiFiHub("Hub1", 950, 50)
    registry_passives.append(hub1)
    hub1.draw(canvas)
    hub2 = WiFiHub("Hub2", 50, 500)
    registry_passives.append(hub2)
    hub2.draw(canvas)

    num_cats = Config.CAT_NUM.value
    if num_cats > 0:
        for i in range(num_cats):
            cat = Cat("Cat" + str(i))
            registry_passives.append(cat)
            cat.draw(canvas)

    count = Counter(canvas)

    def handle_button_clicked(x, y, actives):
        """Handle mouse click event, move robot to clicked position

        Args:
            x: Clicked x-coordinate
            y: Clicked y-coordinate
            actives: Active objects list
        """
        for rr in actives:
            if isinstance(rr, Bot):
                rr.x = x
                rr.y = y

    canvas.bind(
        "<Button-1>",
        lambda event: handle_button_clicked(event.x, event.y, registry_actives),
    )

    return registry_actives, registry_passives, count


def move_it(canvas, registry_actives, registry_passives, counter, moves=0):
    """Update simulation state, move robots and handle interactions

    Args:
        canvas: Drawing canvas object
        registry_actives: Active objects list
        registry_passives: Passive objects list
        counter: Counter object
        moves: Current move count
    """
    moves += 1

    # 检查里程碑
    milestone_data = counter.check_milestone(moves)
    if milestone_data:  # 如果达到里程碑点
        print(f"Move {moves}: Collected {counter.dirt_collected} dirt")


    for rr in registry_actives:
        chargerIntensityL, chargerIntensityR = rr.sense_charger(registry_passives)

        rr.brain(chargerIntensityL, chargerIntensityR)
        rr.move(canvas, registry_passives, 1.0)
        registry_passives = rr.collect_dirt(canvas, registry_passives, counter)

        if moves >= Config.BOT_MOVES_MAX.value:
            print("\nFinal results:")
            for milestone in sorted(counter.milestone_data.keys()):
                print(f"Move {milestone}: Collected {counter.milestone_data[milestone]} dirt")
            print(f"Total dirt collected in {moves} moves is {counter.dirt_collected}")
            sys.exit()

        # # Check if maximum number of moves (1000) is reached
        # num_moves = Config.BOT_MOVES_MAX.value
        # if moves > num_moves:
        #     print(
        #         "total dirt collected in",
        #         num_moves,
        #         "moves is",
        #         counter.dirt_collected,
        #     )
        #     sys.exit()  # End program

        # if counter.dirt_collected >= 600:
        #     print(f"Have collected {counter.dirt_collected} dirt，cost：{moves}")
        #     sys.exit()

    canvas.after(50, move_it, canvas, registry_actives, registry_passives, counter, moves)
