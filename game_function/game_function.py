"""Game Function Module - Core game utilities and window management"""

import pygame
from pathlib import Path

# Module Packages
from settings import *
from systems.manager.asset_manager import *
from game_function.debugging import *


def SCREEN(width, height) -> pygame.Surface:
    return pygame.display.set_mode((width, height))

def ICON_IMPORT(path) -> None:
    try:
        if Path(path).exists():
            image_icon_load(path)
        else:
            print(f"Icon file not found: {path}")
    except (pygame.error, FileNotFoundError, AttributeError) as e:
        print(f"Could not load game icon: {e}")

def TITLE_CAPTION(title) -> None:
    pygame.display.set_caption(title)

def CLOCK() -> pygame.time.Clock:
    return pygame.time.Clock()

def FONT(filepath=CUSTOM_FONT, size=18) -> pygame.font.Font:
    try:
        return create_font(CUSTOM_FONT, size)
    except Exception as e:
        print(f"Could not load custom font, using default: {e}")
        return pygame.font.Font(None, size)

def GAME_INPUT_HANDLER(event: pygame.event.Event) -> bool:
    """Legacy wrapper for input handling."""
    handler = InputHandler()
    return handler.handle_event(event)
