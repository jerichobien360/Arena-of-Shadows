import pygame
from dataclasses import dataclass
from enum import Enum

# Constants
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 525
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
DARK_RED = (139, 0, 0)
DARK_BLUE = (0, 0, 139)

# CAMERA
CAMERA_SMOOTHING = 1 # Default: 0.10
MAX_ZOOM = 500
MIN_ZOOM = 0

# WORLD SETTINGS
WORLD_WIDTH = 3000
WORLD_HEIGHT = 3000


FIRESHOOTER_INNER_COLOR = (255, 200, 0)


# ASSET HANDLER
GAME_ICON = "assets\\icon.png"
CUSTOM_FONT = "assets\\font\\PixelifySans-Medium.ttf"

# DATABASE FILEPATH
DATABASE_FILE = "data\\AOS_player_data.db"

# Gamerplay Renderer Configuration
@dataclass
class UIConfig:
    """UI configuration constants."""
    margin: int = 15
    line_height: int = 24
    view_margin: int = 80
    bar_width: int = 160
    bar_height: int = 14
    bar_border: int = 2
    bar_spacing: int = 6
    bar_corner_radius: int = 5
    panel_padding: int = 12
    panel_corner_radius: int = 8
    panel_alpha: int = 30
    panel_width: int = 320
    low_health_threshold: float = 0.3
    effect_alpha: int = 64
    level_up_duration: int = 2000

class ParticleType(Enum):
    """Different types of particles for various effects"""
    BLOOD = 0
    SPARKS = 1
    EXPLOSION = 2
    MAGIC = 3
    SMOKE = 4
    DEBRIS = 5
    ENERGY = 6
    HEALING = 7
    SMOOTH_FADE = 8
    SMOOTH_SCALE = 9
    SMOOTH_FLOAT = 10


# Input Handler
MOVE_LEFT = pygame.K_LEFT
MOVE_RIGHT = pygame.K_RIGHT
MOVE_DOWN = pygame.K_DOWN
MOVE_UP = pygame.K_UP
JUMP = pygame.K_SPACE
ESCAPE = pygame.K_ESCAPE

# Audio
MUSIC_VOLUME = 0.5
SFX_VOLUME = 0.7
