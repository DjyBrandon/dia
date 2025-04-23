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
                        300 , 300,
                        400 , 400,
                        fill="green", width=0, tags="item1"
                    )

    return canvas


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

    for rr in registry_actives:
        chargerIntensityL, chargerIntensityR = rr.sense_charger(
            registry_passives
        )

        rr.brain(chargerIntensityL, chargerIntensityR)
        rr.move(canvas, registry_passives, 1.0)
        registry_passives = rr.collect_dirt(canvas, registry_passives, counter)

        """
        # Check if maximum number of moves (500) is reached
        num_moves = Config.BOT_MOVES_MAX.value
        if moves > num_moves:
            print(
                "total dirt collected in",
                num_moves,
                "moves is",
                counter.dirt_collected,
            )
            sys.exit()  # End program
        """
        if counter.dirt_collected >= 600:
            print(f"Have collected {counter.dirt_collected} dirt，cost：{moves}")
            sys.exit()
    canvas.after(
        50, move_it, canvas, registry_actives, registry_passives, counter, moves
    )