from canvas_object import CanvasObject
import random

from config import Config


class Dirt(CanvasObject):
    """Represents a piece of dirt that the robot needs to clean."""

    def __init__(self, name):
        """
        Initializes a new Dirt object at a random position.

        Args:
            name (str): The name identifier for this dirt object.
        """
        super().__init__()
        self.name = name
        while True:
            self.x = random.randint(Config.DIRT_X_MIN.value, Config.DIRT_X_MAX.value)
            self.y = random.randint(Config.DIRT_Y_MIN.value, Config.DIRT_Y_MAX.value)

            # 如果生成的位置不在障碍区域内，就跳出循环
            if not ((290 <= self.x <= 410 and 290 <= self.y <= 510)
            or (590 <= self.x <= 710 and 290 <= self.y <= 410)
            or (490 <= self.x <= 610 and 690 <= self.y <= 810)):
                break

    def draw(self, canvas):
        """
        Draws the dirt object on the provided canvas.

        Args:
            canvas (tkinter.Canvas): The canvas on which to draw the dirt.
        """
        canvas.create_oval(
            self.x - 5,
            self.y - 5,
            self.x + 5,
            self.y + 5,
            fill="grey",
            tags=self.name,
        )
