from canvas_object import CanvasObject
import random

from config import Config


class Dirt(CanvasObject):
    """垃圾类，代表需要机器人清理的物体"""

    def __init__(self, name):
        """初始化垃圾对象

        Args:
            name: 垃圾名称
        """
        super().__init__()
        # 随机位置
        self.name = name
        self.x = random.randint(Config.DIRT_X_MIN.value, Config.DIRT_X_MAX.value)
        self.y = random.randint(Config.DIRT_Y_MIN.value, Config.DIRT_Y_MAX.value)

    def draw(self, canvas):
        """在画布上绘制垃圾

        Args:
            canvas: 绘图画布对象
        """
        # 绘制灰色小点表示垃圾
        canvas.create_oval(
            self.x - 5,
            self.y - 5,
            self.x + 5,
            self.y + 5,
            fill="grey",
            tags=self.name,
        )
