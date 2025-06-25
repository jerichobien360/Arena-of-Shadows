import pygame
from dataclasses import dataclass
from typing import Optional


@dataclass
class AnimationState:
    """Centralized animation state management."""
    fade_alpha: float = 255.0
    fade_speed: float = 200.0
    fade_direction: int = 1
    transitioning: bool = False
    target: Optional[str] = None
    title_pulse: float = 0.0
    text_appear: float = 0.0
    lighting: float = 0.0
    
    def reset(self) -> None:
        """Reset all animation values to initial state."""
        self.fade_alpha = 255.0
        self.fade_direction = 1
        self.transitioning = False
        self.target = None
        self.title_pulse = 0.0
        self.text_appear = 0.0
        self.lighting = 0.0
