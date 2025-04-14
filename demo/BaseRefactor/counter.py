class Counter:
    """计数器类，用于跟踪收集的垃圾数量"""

    def __init__(self, canvas):
        """初始化计数器

        Args:
            canvas: 绘图画布对象
        """
        self.dirt_collected = 0  # 初始化收集的垃圾数量为0
        self.canvas = canvas  # 存储画布引用
        # 在画布上创建文本显示当前收集的垃圾数量
        self.canvas.create_text(
            70,  # x坐标
            50,  # y坐标
            text="Dirt collected: " + str(self.dirt_collected),  # 显示文本
            tags="counter",  # 标签，用于后续更新
        )

    def item_collected(self):
        """当垃圾被收集时调用此方法更新计数
        """
        self.dirt_collected += 1  # 增加计数
        # 更新画布上的文本显示
        self.canvas.itemconfigure(
            "counter", text="Dirt collected: " + str(self.dirt_collected)
        )
