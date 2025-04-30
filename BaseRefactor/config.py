from enum import Enum
import math


class Config(Enum):
    """Configuration settings for the simulation."""

    CANVAS_WIDTH = 1000
    CANVAS_HEIGHT = 1000
    CELL_SIZE = 100

    MAP_WIDTH = 10 
    MAP_HEIGHT = 10 

    BOT_NUM = 1  
    BOT_BATTERY_CAPACITY = 3000  
    BOT_V_POSITIVE_MAX = 10  
    BOT_X_MIN = 100  
    BOT_X_MAX = 900  
    BOT_Y_MIN = 100  
    BOT_Y_MAX = 900  
    BOT_THETA_MIN = 0.0  
    BOT_THETA_MAX = 2.0 * math.pi  
    BOT_MOVES_MAX = 500

    CHARGER_X_MIN = 100  
    CHARGER_X_MAX = 900  
    CHARGER_Y_MIN = 100 
    CHARGER_Y_MAX = 900  
    CHARGER_DISTANCE = 80  

    WIFI_HUB_X_MIN = 100  
    WIFI_HUB_X_MAX = 900  
    WIFI_HUB_Y_MIN = 100  
    WIFI_HUB_Y_MAX = 900  

    DIRT_NUM = 2200  
    DIRT_X_MIN = 100  
    DIRT_X_MAX = 900  
    DIRT_Y_MIN = 100  
    DIRT_Y_MAX = 900  

    CAT_NUM = 0
    CAT_AVOID_DISTANCE = 125 
