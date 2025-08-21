import pygame


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
        print("ESC: Context Dependent: e.g. Pause/Back")
        return True


def DEBUGGING(state, enable, item=None, details=False):
    if (state == 'MENU_INIT') and enable:
        print("\n[System] Initializing the Main Menu Screen\n")

    messages = {
        'MENU_INIT': "\n[System] Initializing the Main Menu Screen\n",
        'MENU_CLEANUP': "\t> Cleaning up...",
        'GAMEPLAY_ENTER': "\t> Entering the gameplay\n",
        'GAME_OVER_INIT': "\n[System] Initializing the Game Over Screen\n",
        'GAME_OVER_EXIT': "\t> Exiting the game over screen successfully",
        'GAME_CLOSED': "\nArena of Shadows closed",
        'GAME_STARTUP': "\n[System] Starting Arena of Shadows..."
    }

    if state in ('GENERATE_FALLBACK', 'LOADED_SOUNDS') and details:
        label = 'Generating fallback sound for' if state == 'GENERATE_FALLBACK' else 'Loaded sound'
        print(f"{label}: {item}")
        return
    
    if state == 'PLAYER_MS' and enable:
        print(f"Current Position: ({round(item[0], 0)}, {round(item[1], 0)})")


    message = messages.get(state)
    if message:
        print(message)

