import os

# Grid settings
GRID_SIZE = 21
CELL_SIZE = 30
PADDING = 20

# UI settings
UI_HEIGHT = 80
UI_PADDING = 20
UI_BG_COLOR = (0, 20, 40, 200)
UI_TEXT_COLOR = (0, 200, 255)

# Window settings
WINDOW_WIDTH = GRID_SIZE * CELL_SIZE + 2 * PADDING
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE + 2 * PADDING + UI_HEIGHT  # Add UI height to total window height

# Font settings
FONT_SIZE = 36
SMALL_FONT_SIZE = 24

# Game states
MENU = 'menu'
PLAYING = 'playing'
PAUSED = 'paused'
GAME_OVER = 'game_over'

# Colors (RGBA)
DARK_BLUE = (0, 10, 30)
GRID_BLUE = (0, 20, 40)
LIGHT_BLUE = (0, 150, 255)
NEON_BLUE = (0, 200, 255)

# Player settings
PLAYER_COLOR = (200, 200, 255)
PLAYER_TRAIL_COLOR = (0, 150, 255, 80)
PLAYER_GLOW = (0, 150, 255, 100)
PLAYER_SPEED = 0.2
GLOW_RADIUS = 15

# Enemy settings
ENEMY_COLOR = (255, 100, 100)
ENEMY_TRAIL_COLOR = (255, 100, 100, 50)
ENEMY_GLOW = None
ENEMY_SPEED = 0.1

# Animation settings
ANIMATION_SPEED = 0.2

# Game timing
COUNTDOWN_DURATION = 3.0
IMMUNITY_DURATION = 1.5
POWER_UP_DURATION = 5.0

# Cell types
class Cell:
    WALL = 0
    PATH = 1
    START = 2
    EXIT = 3
    COIN = 4
    POWER_UP = 5

# Sound settings
VOLUME = 0.5
SOUNDS_DIR = os.path.join('src', 'assets', 'sounds')
ASSETS_DIR = os.path.join('src', 'assets')

# Sound effect filenames
SOUND_EFFECTS = {
    'coin': 'coin.wav',
    'powerup': 'powerup.wav',
    'game_over': 'game_over.wav',
    'level_complete': 'level_complete.wav',
    'background': 'background.wav'
}

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DEEP_BLUE = (0, 50, 100)

# Game settings
INITIAL_ENEMY_SPEED = ENEMY_SPEED
MAX_ENEMY_SPEED = PLAYER_SPEED * 0.5
SPEED_INCREASE_PER_LEVEL = 0.01

# Animation settings
TRANSITION_SPEED = 0.05

# Power-up settings
COUNTDOWN_DURATION = 3.0

# Asset paths
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')

# FPS
FPS = 60 