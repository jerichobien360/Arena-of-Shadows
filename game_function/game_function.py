import pygame
# import sys
from settings import *

# System files - Core game management systems
from systems.manager.sound_manager import *
from systems.manager.wave_manager import *
from systems.manager.game_state_manager import *
from systems.manager.asset_manager import *

# Entities - Game objects and characters
from entities.player import *

# Game states - Different screens/modes of the game
from game_states.gameplay import *
from game_states.menu import *
from game_states.game_over import *


# ==================================================================

"""Window Initialization"""


def ICON_IMPORT():
    try:
        icon = image_icon_load(GAME_ICON)
        pygame.display.set_icon(icon)
    except:
        pass  # Skip if icon loading fails

def SCREEN():
    return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

def TITLE_CAPTION():
    pygame.display.set_caption("Arena of Shadows")

def CLOCK():
    return pygame.time.Clock()

def FONT():
    return create_font(CUSTOM_FONT, 18)

def GAME_INPUT_HANDLER(event):
    """Main Window Handler"""
    # Click EXIT icon button to quit
    if event.type == pygame.QUIT:
        return False
    
    # Allow ESC key to quit
    #if event.type == pygame.KEYDOWN and event.key == ESCAPE:
    #    return False

    return True

# ==================================================================

"""Game State Manager"""



# ==================================================================

"""Gameplay"""


# ==================================================================

"""HUD"""

# ==================================================================

"""User Interface (UI)"""

