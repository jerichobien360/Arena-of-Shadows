"""Arena of Shadows - Main Game Application"""

import pygame
import sys
import traceback
from settings import *

# Module Packages
from game_function.game_function import *
from systems.manager.sound_manager import SoundManager
from systems.manager.game_state_manager import GameStateManager

# Game States
from game_states.gameplay import GameplayState
from game_states.menu import MainMenuState
from game_states.game_over import GameOverState
from game_states.loading import LoadingScreenState


class ArenaOfShadows:
    """Main game class for Arena of Shadows."""
    
    def __init__(self):
        self.running = True
        self.debug_mode = False
        
        self._initialize_pygame()
        self._setup_display()
        self._initialize_managers()
        self._setup_game_states()
    
    def _initialize_pygame(self):
        """Initialize pygame and mixer."""
        pygame.init()
        pygame.mixer.init(
            frequency=22050, 
            size=-16, 
            channels=2, 
            buffer=512
        )
    
    def _setup_display(self):
        """Setup game display and window properties."""
        self.screen = SCREEN(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.clock = CLOCK()
        self.font = FONT()
        
        TITLE_CAPTION(TITLE)
        ICON_IMPORT(GAME_ICON)
        
        self.input_handler = InputHandler()
    
    def _initialize_managers(self):
        """Initialize game managers."""
        self.sound_manager = SoundManager()
        self.state_manager = GameStateManager()
    
    def _setup_game_states(self):
        """Setup and register all game states."""
        states = {
            "main_menu": MainMenuState(self.font, self.sound_manager),
            "gameplay": GameplayState(self.font, self.sound_manager),
            "game_over": GameOverState(self.font, self.sound_manager),
            "loading_screen_menu": LoadingScreenState("main_menu", self.sound_manager),
            "loading_screen_gameplay": LoadingScreenState("gameplay", self.sound_manager)
        }
        
        for name, state in states.items():
            self.state_manager.add_state(name, state)
        
        self.state_manager.change_state("loading_screen_menu") # ORIGINAL CODE: "main_menu"
    
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
            self._toggle_fullscreen()
        
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
    
    def _update_game(self, delta_time):
        """Update game logic."""
        next_state = self.state_manager.update(delta_time)
        
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
    
    def run(self):
        """Main game loop."""
        print("Starting Arena of Shadows...")
        
        while self.running:
            delta_time = self.clock.tick(FPS) / 1000.0
            
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
    """Entry point for the game."""
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
