"""Main Gameplay State (Abstraction | Refactor)"""

from abc import ABC, abstractmethod
from typing import Optional, Any
import pygame

from systems.gameplay_core import GameplayCore
from ui.components.gameplay_renderer import GameplayRenderer


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


class GameplayState(GameState):
    """Main gameplay state - combines core logic and rendering."""
    
    def __init__(self, font: pygame.font.Font, sound_manager: Any):
        self.core = GameplayCore(sound_manager)
        self.renderer = GameplayRenderer(font)
        self._initialized = False
    
    # -------------------INITIALIZE & CLEANUP-----------------------------
    def enter(self) -> None:
        """Initialize gameplay when entering state."""
        if not self._initialized:
            self.core.initialize()
            self._initialized = True
    
    def exit(self) -> None:
        """Clean up resources when exiting state."""
        if self._initialized:
            self.core.cleanup()
            self._initialized = False

    # -------------------CLASS METHOD-------------------------------------
    #TODO: Implement the Pause-Layout
    def pause(self) -> None:
        """Pause the game."""
        self.core.pause()
    
    #TODO: Implement the Pause-Layout
    def unpause(self) -> None:
        """Resume the game."""
        self.core.unpause()
    
    # -------------------CLASS PROPERTIES---------------------------------
    #TODO: Implement the Pause-Layout
    @property
    def is_paused(self) -> bool:
        """Check if game is currently paused."""
        return self.core.is_paused if hasattr(self.core, 'is_paused') else False
    
    @property
    def game_data(self) -> dict:
        """Access to current game data for debugging/testing."""
        return self.core.game_data

    # -------------------GAME STATE HANDLE-----------------------------
    def update(self, dt: float) -> Optional[str]:
        """Update game logic and return next state if needed."""
        return self.core.update(dt)
    
    def render(self, screen: pygame.Surface) -> None:
        """Render current game state."""
        self.renderer.render(screen, self.core.game_data)
