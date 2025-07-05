"""Arena of Shadows - Main Game Application"""

import pygame
import sys
from settings import *
from game_function import *

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
        self.state_manager.change_state("main_menu") # Default: Selected Game State
    
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
            if GAME_INPUT_HANDLER(event):
                continue
            else:
                return False
        
        return True
    
    def run(self):
        """Main game loop - handles events, updates, and rendering."""
        running = True
        
        while running:
            # Calculate delta time for frame-independent movement
            dt = self.clock.tick(FPS) / 1000.0
            
            # Process input events
            running = self._handle_events()
            
            # Update current game state
            self.state_manager.update(dt)
            
            # Render current game state
            self.state_manager.render(self.screen)
            
            # Update display
            pygame.display.flip()
        
        # Clean shutdown
        self._cleanup()
    
    def _cleanup(self):
        """Clean up resources and exit gracefully."""
        pygame.quit()
        sys.exit()


def main():
    """Entry point for the game."""
    try:
        game = ArenaOfShadows()
        game.run()
    except Exception as e:
        print(f"Game error: {e}")
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()
