from enum import Enum
from typing import List, Callable, Optional
from dataclasses import dataclass, field
import pygame


# Game Configuration
TITLE = "Arena of Shadows"
DEBUGGING_ENABLE = True
DEBUGGING_ENABLE_DETAILS = False

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
CUSTOM_FONT = "assets\\font\\pixelifySans\\PixelifySans-Medium.ttf"
CUSTOM_FONT_UI = "assets\\font\\segoeui\\segoeui.ttf"
CUSTOM_FONT_UI_BOLD = "assets\\font\\segoeui\\segoeuithebd.ttf"

# DATABASE FILEPATH
DATABASE_FILE = "data\\AOS_player_data.db"

# Gameplay Renderer Configuration
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

# Audio Configuration
MUSIC_VOLUME = 0.8  # Range: 0.0 ~ 1.0
SFX_VOLUME = 0.7    # Range: 0.0 ~ 1.0

# Sound Files Dictionary
SOUND_FILES = {
    # Game sounds
    'attack': 'assets/audio/sounds/attack.wav',
    'enemy_hit': 'assets/audio/sounds/enemy_hit.wav',
    'enemy_death': 'assets/audio/sounds/enemy_death.wav',
    'player_damage': 'assets/audio/sounds/player_damage.wav',
    'level_up': 'assets/audio/sounds/level_up.wav',
    'wave_complete': 'assets/audio/sounds/wave_complete.wav',
    
    # UI sounds
    'ui_click': 'assets/audio/sounds/ui_click.wav',
    'ui_hover': 'assets/audio/sounds/ui_hover.wav',
    'ui_slider': 'assets/audio/sounds/ui_slider.wav',
    'ui_toggle': 'assets/audio/sounds/ui_toggle.wav',
    'ui_dropdown': 'assets/audio/sounds/ui_dropdown.wav',
    'ui_focus': 'assets/audio/sounds/ui_focus.wav',
    'ui_panel': 'assets/audio/sounds/ui_panel.wav',
    'ui_error': 'assets/audio/sounds/ui_error.wav',
    'ui_success': 'assets/audio/sounds/ui_success.wav',
    
    # Ambient/feedback sounds
    'notification': 'assets/audio/sounds/notification.wav',
    'coin_collect': 'assets/audio/sounds/coin_collect.wav',
    'item_pickup': 'assets/audio/sounds/item_pickup.wav',
    'magic_cast': 'assets/audio/sounds/magic_cast.wav'
}

# Background Music Paths
MENU_MUSIC_PATH = "assets/audio/background_music/main_menu.mp3"
CLASS_SELECTION_MUSIC_PATH = "assets/audio/background_music/class_selection.mp3"
GAMEPLAY_MUSIC_PATH = "assets/audio/background_music/gameplay.mp3"

# UI Manager Enums and Classes
class ElementType(Enum):
    BUTTON = "button"
    LABEL = "label"
    INPUT = "input"
    SLIDER = "slider"
    CHECKBOX = "checkbox"
    DROPDOWN = "dropdown"
    SEPARATOR = "separator"

@dataclass
class PanelElement:
    type: ElementType
    id: str = ""
    text: str = ""
    value: str = ""
    options: List[str] = field(default_factory=list)
    callback: Optional[Callable] = None
    rect: pygame.Rect = field(default_factory=lambda: pygame.Rect(0, 0, 0, 0))
    active: bool = False
    enabled: bool = True
    min_val: float = 0
    max_val: float = 100
    checked: bool = False
    dropdown_open: bool = False
    selected_option: int = 0
    dragging: bool = False
    placeholder: str = ""
    cursor_pos: int = 0
    selection_start: int = 0
    selection_end: int = 0
    cursor_timer: int = 0
    selecting: bool = False  # Track if user is selecting text with mouse

# UI Color Scheme
COLORS = {
    'bg': (40, 40, 40), 
    'panel': (60, 60, 60), 
    'button': (80, 80, 80),
    'button_hover': (100, 100, 100), 
    'button_active': (120, 120, 120),
    'text': (255, 255, 255), 
    'input': (30, 30, 30), 
    'input_active': (50, 50, 50),
    'separator': (100, 100, 100), 
    'slider': (120, 120, 120),
    'checkbox': (200, 200, 200), 
    'placeholder': (150, 150, 150),
    'selection': (100, 150, 255)
}
