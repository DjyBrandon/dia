class Counter:
    """A counter class to track the amount of dirt collected."""

    def __init__(self, canvas):
        """
        Initializes the counter.

        Args:
            canvas: The tkinter canvas object where the counter display will be rendered.
        """
        self.dirt_collected = 0  
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
