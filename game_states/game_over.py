from settings import *
import pygame

# gameplay state file
from game_states.gameplay import *

class GameOverState(GameState):
    def __init__(self, font, sound_manager):
        self.font = font
        self.sound_manager = sound_manager
    
    def enter(self):
        self.sound_manager.stop_background_music()
    
    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            return "main_menu"
        return None
    
    def render(self, screen):
        screen.fill(BLACK)
        
        game_over = self.font.render("GAME OVER", True, WHITE)
        restart = self.font.render("Press ENTER to return to menu", True, GRAY)
        
        screen.blit(game_over, (SCREEN_WIDTH//2 - game_over.get_width()//2, 300))
        screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, 350))
