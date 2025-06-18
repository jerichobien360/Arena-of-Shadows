import pygame
import sys
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


class ArenaOfShadows:
    """Main game class that handles initialization, game loop, and cleanup."""
    
    def __init__(self):
        # Initialize Pygame subsystems
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Setup display and core components
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Arena of Shadows")
        
        image_load(GAME_ICON)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(CUSTOM_FONT, 18)
        
        # Initialize game managers
        self.sound_manager = SoundManager()
        self.state_manager = GameStateManager()
        
        # Setup game states and start with main menu
        self._setup_states()
        self.state_manager.change_state("main_menu")
    
    def _setup_states(self):
        """Initialize all game states with required dependencies."""
        states = {
            "main_menu": MainMenuState(self.font, self.sound_manager),
            "gameplay": GameplayState(self.font, self.sound_manager),
            "game_over": GameOverState(self.font, self.sound_manager)
        }
        
        for name, state in states.items():
            self.state_manager.add_state(name, state)
    
    def _handle_events(self):
        """Process pygame events and handle quit conditions."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                return False
        return True
    
    def run(self):
        """Main game loop - handles events, updates, and rendering."""
        running = True
        
        while running:
            # Calculate delta time for frame-independent movement
            dt = self.clock.tick(FPS) / 1000.0
            
            # Process events and check if we should continue running
            running = self._handle_events()
            
            # Update game state and render to screen
            self.state_manager.update(dt)
            self.state_manager.render(self.screen)
            pygame.display.flip()
        
        # Clean shutdown
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    # Create and run the game instance
    ArenaOfShadows().run()
