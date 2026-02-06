import pygame

# Screen settings
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TITLE = "Eco Defender"

# Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)  # Nature
DARK_GREEN = (0, 100, 0)
RED = (220, 20, 60)    # Pollution/Attack
GREY = (100, 100, 100) # Trash
BLUE = (0, 0, 255)     # Bin
BROWN = (139, 69, 19)  # Vendor/Soil
YELLOW = (255, 215, 0) # Money

# Player settings
PLAYER_SPEED = 300
PLAYER_START_X = SCREEN_WIDTH // 2
PLAYER_START_Y = SCREEN_HEIGHT // 2
PLAYER_SIZE = 32

# Economy settings
TRASH_VALUE = 10
SEED_COST = 20

# Tile settings
TILESIZE = 32
