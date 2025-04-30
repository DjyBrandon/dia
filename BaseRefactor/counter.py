class Counter:
    """A counter class to track the amount of dirt collected."""

    def __init__(self, canvas):
        """
        Initializes the counter.

        Args:
            canvas: The tkinter canvas object where the counter display will be rendered.
        """
        self.dirt_collected = 0
        self.milestone_data = {}  # 记录关键点的数据
        self.milestones = [100, 200, 300, 400, 500]  # 需要记录的移动次数

        self.canvas = canvas  
        self.canvas.create_text(
            70,  
            50,  
            text="Dirt collected: " + str(self.dirt_collected),  
            tags="counter",  
        )

    def item_collected(self):
        """
        Increments the dirt collected counter by 1 and updates the display.

        This method should be called whenever a piece of dirt is collected.
        """
        self.dirt_collected += 1  
        self.canvas.itemconfigure(
            "counter", text="Dirt collected: " + str(self.dirt_collected)
        )


    def check_milestone(self, current_moves):
        for milestone in self.milestones:
            if current_moves == milestone:
                self.milestone_data[milestone] = self.dirt_collected
        return self.milestone_data
