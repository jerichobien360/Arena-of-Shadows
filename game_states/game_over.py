from settings import *
from game_function.game_function import *

from game_states.gameplay import GameState
from src.ui.screens.game_over_screen import GameOverVisuals

import pygame


class GameOverState(GameState):
    """Core game over state logic - handles timing, input, and state transitions"""
    
    def __init__(self, font, sound_manager):
        self.font = font
        self.sound_manager = sound_manager
        self.visuals = GameOverVisuals(font)
        self._reset_state()
    
    # -------------------INITIALIZE & CLEANUP-----------------------------
    def enter(self):
        """Initialize state when entering game over"""
        DEBUGGING('GAME_OVER_INIT', DEBUGGING_ENABLE)
        self.sound_manager.stop_background_music()
        self._reset_state()
        self.visuals.reset()
    
    def exit(self): # TODO: Create an exit function from line of "if self.can_exit and self._check_input():"
        DEBUGGING('GAME_OVER_EXIT', DEBUGGING_ENABLE)
        pass

    # -------------------CLASS METHOD-------------------------------------
    # EMPTY

    # -------------------CLASS PROPERTIES---------------------------------
    def _reset_state(self):
        """Reset all timing and state variables"""
        self.timer = 0.0
        self.can_exit = False
        
    def _check_input(self):
        """Check for restart input"""
        keys = pygame.key.get_pressed()
        return keys[pygame.K_RETURN] or keys[pygame.K_SPACE]
    
    # -------------------GAME STATE HANDLE-----------------------------
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
            print("Return to Main Menu Screen...")
            return "main_menu"
        
        return None

    def render(self, screen):
        """Delegate rendering to visuals component"""
        self.visuals.render(screen)
