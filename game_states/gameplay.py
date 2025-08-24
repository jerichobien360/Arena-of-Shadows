"""Main Gameplay State (Abstraction | Refactor)"""

from settings import *
from systems.gameplay_core import GameplayCore
from game_function.game_function import *

from abc import ABC, abstractmethod
from typing import Optional, Any

import pygame


class GameState(ABC):
    """Abstract base class for all game states."""
    
    def enter(self) -> None:
        """Called when entering this state."""
        pass
    
    def exit(self) -> None:
        """Called when exiting this state."""
        pass
    
    @abstractmethod
    def update(self, dt: float) -> Optional[str]:
        """Update state logic. Returns next state name or None to stay."""
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """Render this state to the screen."""
        pass
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events. Return True if event was consumed."""
        return False

class GameplayState(GameState):
    """Main gameplay state - combines core logic and rendering."""
    
    def __init__(self, font: pygame.font.Font, sound_manager: Any, player):
        self.core = GameplayCore(font, sound_manager, player)
        self._initialized = False
    
    # -------------------INITIALIZE & CLEANUP-----------------------------
    def enter(self) -> None:
        """Initialize gameplay when entering state."""
        if not self._initialized:
            DEBUGGING('GAMEPLAY_ENTER', DEBUGGING_ENABLE)
            self.core.initialize()
            self._initialized = True
    
    def exit(self) -> None:
        """Clean up resources when exiting state."""
        if self._initialized:
            self.core.cleanup()
            self._initialized = False
    
    # -------------------CLASS METHOD-------------------------------------
    def pause(self) -> None:
        """Pause the game."""
        self.core.pause()
    
    def unpause(self) -> None:
        """Resume the game."""
        self.core.unpause()
    
    # -------------------CLASS PROPERTIES---------------------------------
    @property
    def is_paused(self) -> bool:
        """Check if game is currently paused."""
        return self.core.is_paused if hasattr(self.core, 'is_paused') else False
    
    @property
    def game_data(self) -> dict:
        """Access to current game data for debugging/testing."""
        return self.core.game_data
    
    # -------------------EVENT HANDLING-----------------------------------
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events, including pause panel interactions."""
        # Let the core handle the event first (for pause panel)
        if self.core.handle_event(event):
            return True
        
        # Handle other gameplay-specific events here if needed
        return False
    
    # -------------------GAME STATE HANDLE-----------------------------
    def update(self, dt: float) -> Optional[str]:
        """Update game logic and return next state if needed."""
        return self.core.update(dt)
    
    def render(self, screen: pygame.Surface) -> None:
        """Render current game state."""
        self.core.renderer.render(screen, self.core.game_data)
