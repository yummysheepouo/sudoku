import os
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 750
GRID_SIZE = 450
CELL_SIZE = GRID_SIZE // 9
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_SIZE) // 2
GRID_OFFSET_Y = 120
BUTTON_HEIGHT = 45
BUTTON_WIDTH = 160
BUTTON_MARGIN = 15
BUTTON_ROW_MARGIN = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (220, 220, 220)
GRAY = (180, 180, 180)
DARK_GRAY = (100, 100, 100)
BLUE = (65, 105, 225)
LIGHT_BLUE = (173, 216, 230)
RED = (220, 20, 60)
GREEN = (50, 205, 50)
YELLOW = (255, 215, 0)
PURPLE = (147, 112, 219)
BACKGROUND = (240, 248, 255)
SHADOW = (150, 150, 150)
ALERT_BG = (255, 255, 255, 200)
OVERLAY_BG = (0, 0, 0, 150)
DISABLED_GRAY = (200, 200, 200)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUZZLE_DIR = os.path.join(BASE_DIR, "puzzle")
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")
SETTINGS_ICON_PATH = os.path.join("./img/settings.png")  

# Difficulty and hints
DIFFICULTY_LEVELS = {"beginner": 60, "normal": 40, "advanced": 20}
HINT_LIMITS = {"beginner": 7, "normal": 5, "advanced": 3}