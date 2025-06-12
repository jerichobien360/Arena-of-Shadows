import pygame
import sys
from settings import *

# system files
from systems.sound_manager import *
from systems.wave_manager import *
from systems.game_state_manager import *

# entities
from entities.player import *

# game states
from game_states.gameplay import *
from game_states.menu import *
from game_states.game_over import *

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)


class ArenaOfShadows:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Arena of Shadows")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.running = True
        
        # Initialize managers
        self.sound_manager = SoundManager()
        self.state_manager = GameStateManager()
        
        # Setup states
        self.setup_states()
        self.state_manager.change_state("main_menu")
    
    def setup_states(self):
        self.state_manager.add_state("main_menu", MainMenuState(self.font, self.sound_manager))
        self.state_manager.add_state("gameplay", GameplayState(self.font, self.sound_manager))
        self.state_manager.add_state("game_over", GameOverState(self.font, self.sound_manager))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            self.handle_events()
            self.state_manager.update(dt)
            self.state_manager.render(self.screen)
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ArenaOfShadows()
    game.run()
