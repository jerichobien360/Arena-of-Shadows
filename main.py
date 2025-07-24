"""Arena of Shadows - Main Game Application"""

import pygame
import sys
from settings import *
from game_function.game_function import *
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


class ArenaOfShadows:
    """Main game class handling initialization and game loop."""
    
    def __init__(self):
        """Initialize pygame subsystems and game components."""
        self._init_pygame()
        self._setup_display()
        self._init_managers()
        self._setup_states()
        self.state_manager.change_state("main_menu")  # Default on the chosen game state
        self.running = True
    
    def _init_pygame(self):
        """Initialize pygame subsystems."""
        pygame.init()
        pygame.mixer.init(
            frequency=22050,
            size=-16,
            channels=2,
            buffer=512
        )
    
    def _setup_display(self):
        """Setup display and core visual components."""
        # Load Windows
        self.screen = SCREEN()
        TITLE_CAPTION()
        ICON_IMPORT()
        
        # Other Essentials
        self.clock = CLOCK()
        self.font = FONT()
    
    def _init_managers(self):
        """Initialize game managers."""
        # Main Game Composition
        self.sound_manager = SoundManager()
        self.state_manager = GameStateManager()
    
    def _setup_states(self):
        """Initialize all game states with required dependencies."""
        # Create all game states
        main_menu = MainMenuState(self.font, self.sound_manager)
        gameplay = GameplayState(self.font, self.sound_manager)
        game_over = GameOverState(self.font, self.sound_manager)
        
        # Add states to manager
        self.state_manager.add_state("main_menu", main_menu)
        self.state_manager.add_state("gameplay", gameplay)
        self.state_manager.add_state("game_over", game_over)
    
    def _handle_events(self):
        """Process pygame events and handle quit conditions."""
        for event in pygame.event.get():
            # Handle quit events
            if event.type == pygame.QUIT:
                return False
            
            # Use your custom game input handler if it exists
            if hasattr(self, 'GAME_INPUT_HANDLER'):
                if GAME_INPUT_HANDLER(event):
                    continue
            
            # Let current state handle the event
            current_state = self.state_manager.get_current_state()
            if current_state and hasattr(current_state, 'handle_event'):
                if current_state.handle_event(event):
                    continue
            
            # Handle global key events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F4 and (event.mod & pygame.KMOD_ALT):
                    return False  # Alt+F4 to quit
                elif event.key == pygame.K_F11:
                    self._toggle_fullscreen()
        
        return True
    
    def _toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode."""
        try:
            if self.screen.get_flags() & pygame.FULLSCREEN:
                # Switch to windowed mode
                self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            else:
                # Switch to fullscreen mode
                self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        except Exception as e:
            print(f"Failed to toggle fullscreen: {e}")
    
    def _update_game(self, dt):
        """Update game logic and handle state transitions."""
        # Update current state and get potential state change
        next_state = self.state_manager.update(dt)
        
        # Handle state transitions
        if next_state:
            if next_state == "quit":
                self.running = False
            else:
                self.state_manager.change_state(next_state)
    
    def _render_game(self):
        """Render current game state and update display."""
        # Clear screen with black background
        self.screen.fill(BLACK)
        
        # Render current state
        self.state_manager.render(self.screen)
        
        # Optional: Add global UI elements here (like FPS counter in debug mode)
        if hasattr(self, 'debug_mode') and self.debug_mode:
            self._render_debug_info()
        
        # Update display
        pygame.display.flip()
    
    def _render_debug_info(self):
        """Render debug information like FPS."""
        if hasattr(self.clock, 'get_fps'):
            fps = int(self.clock.get_fps())
            fps_text = self.font.render(f"FPS: {fps}", True, WHITE)
            self.screen.blit(fps_text, (SCREEN_WIDTH - 100, 10))
    
    def _handle_state_changes(self):
        """Handle any pending state changes."""
        # This method can be expanded to handle more complex state transitions
        # For now, the state manager handles transitions internally
        pass
    
    def run(self):
        """Main game loop - handles events, updates, and rendering."""
        print("Starting Arena of Shadows...")
        
        try:
            while self.running:
                # Calculate delta time for frame-independent movement
                dt = self.clock.tick(FPS) / 1000.0
                
                # Process input events
                if not self._handle_events():
                    self.running = False
                    break
                
                # Update game logic
                self._update_game(dt)
                
                # Render everything
                self._render_game()
                
                # Handle any state changes
                self._handle_state_changes()
                
        except KeyboardInterrupt:
            print("\nGame interrupted by user")
        except Exception as e:
            print(f"Game error during main loop: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Clean shutdown
            self._cleanup()
    
    def _cleanup(self):
        """Clean up resources and exit gracefully."""
        print("Cleaning up game resources...")
        
        # Clean up managers
        if hasattr(self, 'sound_manager'):
            pass
            # self.sound_manager.cleanup()
        
        if hasattr(self, 'state_manager'):
            pass
            # self.state_manager.cleanup()
        
        # Quit pygame
        pygame.quit()
        print("Arena of Shadows closed successfully")
        sys.exit()


def main():
    """Entry point for the game."""
    print("Initializing Arena of Shadows...")
    
    try:
        game = ArenaOfShadows()
        game.run()
    except Exception as e:
        print(f"Fatal game error: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()
