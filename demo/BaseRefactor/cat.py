import random
import tkinter as tk
import os
from config import Config
from PIL import Image, ImageTk

class Cat:
    def __init__(self, name):
        self.name = name
        self.x = random.randint(0, 19) * 50
        self.y = random.randint(0, 11) * 50
        self.size = 40
        self.image = None

    def get_location(self):
        """返回猫的位置"""
        return self.x, self.y
    
    def draw(self, canvas):
        try:
            path = os.path.join("assets", "cat.png")  # 保证路径跨平台兼容
            img = Image.open(path).resize((50, 50))
            self.image = ImageTk.PhotoImage(img)
            canvas.create_image(self.x, self.y, anchor="nw", image=self.image)
        except Exception as e:
            print(f"Error loading cat image: {e}")
            canvas.create_rectangle(
                self.x, self.y, self.x + self.size, self.y + self.size,
                fill="gray"
            )
