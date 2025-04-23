from canvas_object import CanvasObject
import random

from config import Config


class Charger(CanvasObject):
    def __init__(self, name: str):
        """
        Initialize a Charger object with a given name and random position.

        Args:
            name (str): The name of the charger.
        """
        super().__init__()
        self.x = random.randint(Config.CHARGER_X_MIN.value, Config.CHARGER_X_MAX.value)
        self.y = random.randint(Config.CHARGER_Y_MIN.value, Config.CHARGER_Y_MAX.value)
        self.name = name

    def draw(self, canvas):
        """
        Draw the charger on the given canvas.

        Args:
            canvas (tk.Canvas): The canvas on which to draw the charger.
        """
        canvas.create_oval(
            self.x - 10,
            self.y - 10,
            self.x + 10,
            self.y + 10,
            fill="gold",
            tags=self.name,
        )
        canvas.create_text(
            self.x, self.y, text='C', tags=self.name
        )
