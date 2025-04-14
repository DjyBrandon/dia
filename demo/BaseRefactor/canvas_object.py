from abc import ABC, abstractmethod
from tkinter import Canvas
from typing import Tuple


class CanvasObject(ABC):
    def __init__(self):
        self.name: str | None = None
        self.x: float | None = None
        self.y: float | None = None

    def get_location(self) -> Tuple[float, float]:
        """
        Get the location of the object on the canvas.
        """
        return self.x, self.y

    @abstractmethod
    def draw(self, canvas: Canvas):
        """
        Draw the object on the canvas.
        """
        pass
