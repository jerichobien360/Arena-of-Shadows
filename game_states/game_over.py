from settings import *
import pygame
from game_states.gameplay import GameState
from ui.screens.game_over_screen import GameOverVisuals


class GameOverState(GameState):
    """Core game over state logic - handles timing, input, and state transitions"""
    
    def __init__(self, font, sound_manager):
        self.font = font
        self.sound_manager = sound_manager
        self.visuals = GameOverVisuals(font)
        self._reset_state()
    
    def _reset_state(self):
        """Reset all timing and state variables"""
        self.timer = 0.0
        self.can_exit = False
        
    def enter(self):
        """Initialize state when entering game over"""
        self.sound_manager.stop_background_music()
        self._reset_state()
        self.visuals.reset()
    
    def update(self, dt):
        """Update timing and handle input"""
        self.timer += dt
        
        # Update visual animations
        self.visuals.update(dt)
        
        # Enable input after sufficient time has passed
        if self.timer >= 1.7:  # Allow input after most animations complete
            self.can_exit = True
        
        # Handle input
        if self.can_exit and self._check_input():
            return "main_menu"
        
        return None
    
    def _check_input(self):
        """Check for restart input"""
        keys = pygame.key.get_pressed()
        return keys[pygame.K_RETURN] or keys[pygame.K_SPACE]
    
    def render(self, screen):
        """Delegate rendering to visuals component"""
        self.visuals.render(screen)
