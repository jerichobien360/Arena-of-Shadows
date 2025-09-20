"""Arena of Shadows - Main Game Application"""

# Module Packages
from settings import *
from game_function.game_function import *
from game_function.debugging import *
from systems.manager.sound_manager import *
from systems.manager.game_state_manager import *

# Global Entities
from entities.player import Player

# Game States
from game_states.gameplay import GameplayState
from game_states.menu import MainMenuState
from game_states.game_over import GameOverState
from game_states.loading import LoadingScreenState
from game_states.game_class.class_selection import ClassSelectionState

import pygame
import sys
import traceback


"""
This is the class for the main game application, and it shall START HERE
as a main model of this code structuure.

For complexities, it helds with the main system:
    > State Manager (Main Hierarchy of the Game Flows)
    > Debugging Tool
    > Handling Events (Sequences that deals on the game application)
    > Rendering (CPU-Based)

As of now, working on separating all of pygame renderer to the renderer class
and switch from CPU to GPU. Also, for documenting all of these game project for fun.
"""


class ArenaOfShadows:
    """Main Game Class of Arena of Shadows."""
    def __init__(self):
        self.running = True
        self.debug_mode = False
        
        # Initialize Game Packages
        self._initialize_pygame()
        self._initialize_components()
        
    # -------------------- INITIALIZE -------------------------------------
    def _initialize_pygame(self):
        """Initialize game packages."""
        # Pygame and Mixer
        pygame.init()
        pygame.mixer.init(
            frequency=22050, 
            size=-16, 
            channels=2, 
            buffer=512
        )
    
    def _initialize_components(self):
        """Main Components"""
        self._setup_display()
        self._setup_managers()
        self._setup_entity()
        self._setup_game_states()
    
    # -------------------- COMPONENTS -------------------------------------
    def _setup_display(self):
        """Setup game display and window properties."""
        self.screen = SCREEN(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.clock = CLOCK()
        self.font = FONT()
        
        TITLE_CAPTION(TITLE)
        ICON_IMPORT(GAME_ICON)
        
        self.input_handler = InputHandler()
    
    def _setup_managers(self):
        """Initialize game managers."""
        self.sound_manager = SoundManager()
        self.state_manager = GameStateManager()
    
    def _setup_entity(self):
        self.player = Player()
    
    def _setup_game_states(self):
        """Setup and register all game states."""
        states = {
            "main_menu": MainMenuState(self.font, self.sound_manager),
            "class_selection": ClassSelectionState(self.font, self.sound_manager, self.player),
            "gameplay": GameplayState(self.font, self.sound_manager, self.player),
            "game_over": GameOverState(self.font, self.sound_manager),
            "loading_screen_menu": LoadingScreenState("main_menu", self.sound_manager),
            "loading_screen_gameplay": LoadingScreenState("gameplay", self.sound_manager)
        }
        
        # Adding to the state manager's main data
        for name, state in states.items():
            self.state_manager.add_state(name, state)
        
        # Default
        self.state_manager.change_state("loading_screen_menu")
    
    # -------------------- HANDLE EVENTS ----------------------------------
    def _handle_events(self):
        """Handle pygame events and return False if game should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle global input
            if not self.input_handler.handle_event(event):
                return False
            
            # Pass event to current state
            current_state = self.state_manager.get_current_state()
            if current_state and hasattr(current_state, 'handle_event'):
                current_state.handle_event(event)
            
            # Handle global keyboard shortcuts
            if not self._handle_global_keys(event):
                return False
        
        return True
    
    def _handle_global_keys(self, event):
        """Handle global keyboard shortcuts."""
        if event.type != pygame.KEYDOWN:
            return True
        
        # Alt+F4 to quit
        if event.key == pygame.K_F4 and (event.mod & pygame.KMOD_ALT):
            return False
        
        # F11 for fullscreen toggle
        if event.key == pygame.K_F11:
            pass #self._toggle_fullscreen()
        
        # F3 for debug mode toggle
        if event.key == pygame.K_F3:
            self.debug_mode = not self.debug_mode
        
        return True
    
    def _toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode."""
        current_flags = self.screen.get_flags()
        if current_flags & pygame.FULLSCREEN:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT), 
                pygame.FULLSCREEN
            )
    
    # -------------------- GAME UPDATE ------------------------------------
    def _update_game(self, delta_time: float):
        """Update game logic."""
        next_state = self.state_manager.update(delta_time)
        
        # Safety net for exiting the game within a game state loop
        if next_state == "quit":
            self.running = False
        
        elif next_state:
            self.state_manager.change_state(next_state)
    
    def _render_game(self):
        """Render the game."""
        self.screen.fill(BLACK)
        self.state_manager.render(self.screen)
        
        if self.debug_mode:
            self._render_debug_info()
        
        pygame.display.flip()
    
    # -------------------- GAME DEBUG -------------------------------------
    def _render_debug_info(self):
        """Render debug information on screen."""
        # FPS counter
        fps = int(self.clock.get_fps())
        fps_text = self.font.render(f"FPS: {fps}", False, WHITE)
        self.screen.blit(fps_text, (SCREEN_WIDTH - 100, 10))
        
        # Current state name
        state_name = getattr(self.state_manager, 'current_state_name', 'Unknown')
        state_text = self.font.render(f"State: {state_name}", True, WHITE)
        self.screen.blit(state_text, (10, 10))
    
    # -------------------- CLEANUP ----------------------------------------
    def run(self):
        """Main game loop."""
        DEBUGGING('GAME_STARTUP', DEBUGGING_ENABLE)
        
        while self.running:
            # Updating the delta for game manager
            delta_time = self.clock.tick(FPS) / 1000.0
            
            # Closing the game
            if not self._handle_events():
                break
            
            self._update_game(delta_time)
            self._render_game()
        
        self._cleanup()
    
    def _cleanup(self):
        """Clean up resources and exit gracefully."""
        DEBUGGING('MENU_CLEANUP', DEBUGGING_ENABLE)
        pygame.quit()
        DEBUGGING('GAME_CLOSED', DEBUGGING_ENABLE)


def main():
    """Entry point for this game."""
    try:
        game = ArenaOfShadows()
        game.run()
    except Exception as e:
        print(f"Game error: {e}")
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()
