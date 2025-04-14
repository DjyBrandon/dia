import random

from canvas_object import CanvasObject
from config import Config


class WiFiHub(CanvasObject):
    """WiFi集线器类，用于网络连接"""

    def __init__(self, name, x=None, y=None):
        """初始化WiFi集线器

        Args:
            name: 集线器名称
            x: x坐标
            y: y坐标
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
        """在画布上绘制WiFi集线器

        Args:
            canvas: 绘图画布对象
        """
        # 绘制紫色圆形表示WiFi集线器
        canvas.create_oval(
            self.x - 10,
            self.y - 10,
            self.x + 10,
            self.y + 10,
            fill="purple",
            tags=self.name,
        )
        # 在圆形上绘制字母"W"
        canvas.create_text(
            self.x, self.y, text="W", tags=self.name
        )