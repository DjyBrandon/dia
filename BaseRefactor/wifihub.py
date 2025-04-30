import random

from canvas_object import CanvasObject
from config import Config


class WiFiHub(CanvasObject):
    """WiFi Hub class for network connectivity"""

    def __init__(self, name, x=None, y=None):
        """Initialize the WiFi hub

        Args:
            name: The name of the WiFi hub
            x: x-coordinate (optional)
            y: y-coordinate (optional)
        """
        super().__init__()
        self.name = name
        self.x = x
        self.y = y
        if x is None:
            self.x = random.randint(Config.WIFI_HUB_X_MIN.value, Config.WIFI_HUB_X_MAX.value)
        if y is None:
            self.y = random.randint(Config.WIFI_HUB_Y_MIN.value, Config.WIFI_HUB_Y_MAX.value)

    def draw(self, canvas):
        """Draw the WiFi hub on the canvas

        Args:
            canvas: The drawing canvas object
        """
        canvas.create_oval(
            self.x - 10,
            self.y - 10,
            self.x + 10,
            self.y + 10,
            fill="purple",
            tags=self.name,
        )
        canvas.create_text(
            self.x, self.y, text="W", tags=self.name
        )