from settings import *
import pygame

# game_states file
from game_states.gameplay import *

class MainMenuState(GameState):
    def __init__(self, font, sound_manager):
        self.font = font
        self.sound_manager = sound_manager
    
    def enter(self):
        # Load and play menu music
        if self.sound_manager.load_background_music("assets/background_music/main_menu.mp3"):
            self.sound_manager.play_background_music()
    
    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            return "gameplay"
        return None
    
    def render(self, screen):
        screen.fill(BLACK)
        
        title = self.font.render("ARENA OF SHADOWS", True, WHITE)
        start = self.font.render("Press ENTER to Start", True, GRAY)
        controls = self.font.render("WASD/Arrows: Move | SPACE: Attack", True, GRAY)
        
        y_offset = 200
        for text in [title, start, controls]:
            x = SCREEN_WIDTH // 2 - text.get_width() // 2
            screen.blit(text, (x, y_offset))
            y_offset += 50
