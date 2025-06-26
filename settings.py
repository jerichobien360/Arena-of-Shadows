from dataclasses import dataclass

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
