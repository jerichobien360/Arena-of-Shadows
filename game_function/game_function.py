"""Game Function Module - Core game utilities and window management"""

import pygame
from pathlib import Path

# Module Packages
from settings import *
from systems.manager.asset_manager import *


# For Debugging
class InputHandler:
    """Handles global input processing."""

    def __init__(self):
        """Initialize the input handler."""
        self.key_bindings = {
            pygame.K_ESCAPE: self._handle_escape,
            pygame.K_F1: self._handle_help,
        }

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle a pygame event.

        Args:
            event: The pygame event to handle

        Returns:
            bool: True to continue processing, False to quit
        """
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            handler = self.key_bindings.get(event.key)
            if handler:
                return handler(event)

        return True

    def _handle_escape(self, event: pygame.event.Event) -> bool:
        """Handle escape key press."""
        # For now, don't quit on escape - let states handle it
        return True

    def _handle_help(self, event: pygame.event.Event) -> bool:
        """Handle F1 help key press."""
        print("=== Arena of Shadows Controls ===")
        print("F1: Show this help")
        print("F3: Toggle debug mode")
        print("F11: Toggle fullscreen")
        print("Alt+F4: Quit game")
        print("ESC: Context-dependent (usually back/pause)")
        return True





def SCREEN(width, height) -> pygame.Surface:
    screen = pygame.display.set_mode((width, height))
    return screen

def ICON_IMPORT(path) -> None:
    try:
        # Check if GAME_ICON is defined and file exists
        if 'GAME_ICON' in globals() and Path(path).exists():
            image_icon_load(path)
        else:
            print(f"Icon file not found or GAME_ICON not defined: {globals().get('GAME_ICON', 'Not defined')}")
    except (pygame.error, FileNotFoundError, AttributeError) as e:
        print(f"Could not load game icon: {e}")

def TITLE_CAPTION(title) -> None:
    pygame.display.set_caption(title)

def CLOCK() -> pygame.time.Clock:
    return pygame.time.Clock()

def FONT() -> pygame.font.Font:
    try:
        return create_font(CUSTOM_FONT, 18)
    except Exception as e:
        print(f"Could not load custom font, using default: {e}")
        return pygame.font.Font(None, 18)

def GAME_INPUT_HANDLER(event: pygame.event.Event) -> bool:
    """Legacy wrapper for input handling."""
    handler = InputHandler()
    return handler.handle_event(event)


def DEBUGGING(state, enable, item=None, details=False):
    if (state == 'MENU_INIT') and enable:
        print("\n[System]: Initializing the Main Menu Screen\n")

    if (state == 'MENU_CLEANUP') and enable:
        print("\tCleaning up...")

    if (state == 'GAMEPLAY_ENTER') and enable:
        print("\t>Entering the gameplay\n")

    if (state == 'GAME_OVER_INIT') and enable:
        print("\n[System]: Initializing the Game Over Screen\n")

    if (state == 'GAME_OVER_EXIT') and enable:
        print("\t>Exiting the game over screen successfully")

    if (state == 'GAME_CLOSED') and enable:
        print("\nArena of Shadows closed")

    if (state == 'GENERATE_FALLBACK') and (enable and details):
        print(f"Generating fallback sound for: {item}")

    if (state == 'LOADED_SOUNDS') and (enable and details):
        print(f"Loaded sound: {item}")
