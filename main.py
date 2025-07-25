"""Arena of Shadows - Main Game Application"""

import pygame
import sys
import traceback
from settings import *

# Module Packages
from game_function.game_function import *
from systems.manager.sound_manager import *
from systems.manager.game_state_manager import *

# Game States
from game_states.gameplay import GameplayState
from game_states.menu import MainMenuState
from game_states.game_over import GameOverState


class ArenaOfShadows:
    """Main game class - simplified version."""
    
    def __init__(self):
        # Debugging
        self.running = True
        self.debug_mode = False # Debugging for memory optimization
        
        # Initialize pygame
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Setup display - use your existing GameWindow
        self.screen = SCREEN(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.clock = CLOCK()
        self.font = FONT()
        
        # Load game icon properly
        TITLE_CAPTION(TITLE)
        ICON_IMPORT(GAME_ICON)
        self.input_handler = InputHandler()
        
        # Initialize managers
        self.sound_manager = SoundManager()
        self.state_manager = GameStateManager()
        
        # Setup states
        states = {
            "main_menu": MainMenuState(self.font, self.sound_manager),
            "gameplay": GameplayState(self.font, self.sound_manager),
            "game_over": GameOverState(self.font, self.sound_manager)
        }
        
        for name, state in states.items():
            self.state_manager.add_state(name, state)
        
        # Start with main menu
        self.state_manager.change_state("main_menu")
    
    def _handle_events(self) -> bool:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Global input handling
            if not self.input_handler.handle_event(event):
                return False
            
            # Let current state handle the event
            current_state = self.state_manager.get_current_state()
            if current_state and hasattr(current_state, 'handle_event'):
                current_state.handle_event(event)
            
            # Global keys
            if event.type == pygame.KEYDOWN:
                # Alt+F4 to quit
                if event.key == pygame.K_F4 and (event.mod & pygame.KMOD_ALT):
                    return False
                
                # F11 fullscreen
                if event.key == pygame.K_F11:
                    current_flags = self.screen.get_flags()
                    if current_flags & pygame.FULLSCREEN:
                        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    else:
                        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                
                # F3 debug
                if event.key == pygame.K_F3:
                    self.debug_mode = not self.debug_mode
        
        return True
    
    def _update_game(self, delta_time: float) -> None:
        """Update game logic."""
        next_state = self.state_manager.update(delta_time)
        
        if next_state:
            if next_state == "quit":
                self.running = False
            else:
                self.state_manager.change_state(next_state)
    
    def _render_game(self) -> None:
        """Render game."""
        self.screen.fill(BLACK)
        self.state_manager.render(self.screen)
        
        # Debug info
        if self.debug_mode:
            fps = int(self.clock.get_fps())
            fps_text = self.font.render(f"FPS: {fps}", True, WHITE)
            self.screen.blit(fps_text, (SCREEN_WIDTH - 100, 10))
            
            # Get state name properly
            if hasattr(self.state_manager, 'current_state_name'):
                state_name = self.state_manager.current_state_name
            else:
                state_name = "Unknown"
            
            state_text = self.font.render(f"State: {state_name}", True, WHITE)
            self.screen.blit(state_text, (10, 10))
        
        pygame.display.flip()
    
    def run(self) -> None:
        """Main game loop."""
        print("Starting Arena of Shadows...")
        
        while self.running:
            delta_time = self.clock.tick(FPS) / 1000.0
            
            if not self._handle_events():
                break
            
            self._update_game(delta_time)
            self._render_game()
        
        self._cleanup()
    
    def _cleanup(self) -> None:
        """Clean up."""
        DEBUGGING('MENU_CLEANUP', DEBUGGING_ENABLE)
        pygame.quit()
        DEBUGGING('GAME_CLOSED', DEBUGGING_ENABLE)


def main() -> None:
    """Entry point."""
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
