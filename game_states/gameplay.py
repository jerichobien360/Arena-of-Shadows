# gameplay.py - Main Gameplay State (Refactored)
from systems.gameplay_core import GameplayCore
from ui.components.gameplay_renderer import GameplayRenderer

class GameState:
    """Base class for all game states"""
    def enter(self): pass
    def exit(self): pass
    def update(self, dt): return None
    def render(self, screen): pass

class GameplayState(GameState):
    """Main gameplay state - combines core logic and rendering"""
    
    def __init__(self, font, sound_manager):
        self.core = GameplayCore(sound_manager)
        self.renderer = GameplayRenderer(font)
    
    def enter(self):
        """Initialize gameplay"""
        self.core.initialize()
    
    def update(self, dt):
        """Update game logic"""
        return self.core.update(dt)
    
    def render(self, screen):
        """Render game"""
        self.renderer.render(screen, self.core.game_data)
    
    def pause(self):
        """Pause game"""
        self.core.pause()
    
    def unpause(self):
        """Unpause game"""
        self.core.unpause()
    
    def exit(self):
        """Cleanup"""
        self.core.cleanup()
