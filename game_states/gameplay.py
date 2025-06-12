from settings import *

# entities
from entities.player import *
from entities.enemies import *

# systems
from systems.wave_manager import *


class GameState:
    def enter(self): pass
    def exit(self): pass
    def update(self, dt): return None
    def render(self, screen): pass

class GameplayState(GameState):
    def __init__(self, font, sound_manager):
        self.font = font
        self.sound_manager = sound_manager
        self.player = None
        self.enemies = []
        self.wave_manager = None
    
    def enter(self):
        self.player = Player(self.sound_manager)
        self.enemies = []
        self.wave_manager = WaveManager(self.sound_manager)
        self.wave_manager.start_wave(1)
        
        # Stop menu music and start game music
        self.sound_manager.stop_background_music()
        if self.sound_manager.load_background_music("assets/background_music/gameplay.mp3"):
            self.sound_manager.play_background_music()
    
    def update(self, dt):
        self.handle_input()
        self.player.update(dt)
        self.update_enemies(dt)
        
        # Check wave completion
        if self.wave_manager.update(dt, self.enemies):
            self.wave_manager.start_wave(self.wave_manager.current_wave + 1)
        
        # Check game over
        if self.player.hp <= 0:
            return "game_over"
        
        return None
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.player.attack(self.enemies)
    
    def update_enemies(self, dt):
        for enemy in self.enemies[:]:
            enemy.update(dt, self.player)
            if enemy.hp <= 0:
                self.enemies.remove(enemy)
    
    def render(self, screen):
        screen.fill(BLACK)
        
        # Render entities
        self.player.render(screen)
        for enemy in self.enemies:
            enemy.render(screen)
        
        # Render UI
        self.render_ui(screen)
    
    def render_ui(self, screen):
        ui_elements = [
            f"HP: {self.player.hp}/{self.player.max_hp}",
            f"Level: {self.player.level}",
            f"Wave: {self.wave_manager.current_wave}",
            f"Exp: {self.player.experience}"
        ]
        
        for i, text in enumerate(ui_elements):
            rendered = self.font.render(text, True, WHITE)
            screen.blit(rendered, (10, 10 + i * 30))
