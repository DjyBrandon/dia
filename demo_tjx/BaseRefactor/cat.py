import random
import tkinter as tk
import os
from config import Config
from PIL import Image, ImageTk

class Cat:
    def __init__(self, name):
        """
        Initialize a Cat object with a given name and random position.

        Args:
            name (str): The name of the cat.
        """
        self.name = name
        self.x = random.randint(0, 19) * 50
        self.y = random.randint(0, 11) * 50
        self.size = 40
        self.image = None

    def get_location(self):
        """
        Get the current location of the cat.

        Returns:
            tuple: A tuple containing the x and y coordinates of the cat.
        """
        return self.x, self.y
    
    def draw(self, canvas):
        """
        Draw the cat on the given canvas. If the image cannot be loaded,
        a gray rectangle is drawn as a placeholder.

        Args:
            canvas (tk.Canvas): The canvas on which to draw the cat.
        """
        try:
            path = os.path.join("assets", "cat.png")
            img = Image.open(path).resize((50, 50))
            self.image = ImageTk.PhotoImage(img)
            canvas.create_image(self.x, self.y, anchor="nw", image=self.image)
        except Exception as e:
            print(f"Error loading cat image: {e}")
            canvas.create_rectangle(
                self.x, self.y, self.x + self.size, self.y + self.size,
                fill="gray"
            )
