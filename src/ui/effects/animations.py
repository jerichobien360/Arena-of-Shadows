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


@dataclass
class AnimationConfig:
    """Configuration for progress bar animations."""
    speed: float = 0.08
    threshold: float = 0.1
    change_duration: int = 300


class AnimatedProgressBar:
    """Handles smooth animations for progress bars."""
    
    def __init__(self, initial_value: float = 0.0, initial_max: float = 100.0):
        self.target_value = initial_value
        self.target_max = initial_max
        self.current_value = initial_value
        self.current_max = initial_max
        self.display_value = initial_value
        self.display_max = initial_max
        
        self.config = AnimationConfig()
        self.previous_value = initial_value
        self.value_change_timer = 0
    
    def update(self, new_value: float, new_max: float, dt_ms: int) -> None:
        """Update target values and animate towards them."""
        if abs(new_value - self.target_value) > 0.1:
            self.previous_value = self.display_value
            self.value_change_timer = dt_ms
        
        self.target_value = new_value
        self.target_max = new_max
        
        self.current_value = self._ease_towards(self.current_value, self.target_value)
        self.current_max = self._ease_towards(self.current_max, self.target_max)
        self.display_value = self.current_value
        self.display_max = self.current_max
    
    def _ease_towards(self, current: float, target: float) -> float:
        """Smooth easing function."""
        diff = target - current
        return target if abs(diff) < self.config.threshold else current + diff * self.config.speed
    
    def get_progress(self) -> float:
        """Get current progress as 0.0 to 1.0."""
        return min(self.display_value / max(self.display_max, 1), 1.0)
    
    def is_animating(self) -> bool:
        """Check if the bar is currently animating."""
        return (abs(self.current_value - self.target_value) > self.config.threshold or
                abs(self.current_max - self.target_max) > self.config.threshold)
    
    def get_change_effect_alpha(self, current_time_ms: int) -> float:
        """Get alpha for change effect overlay."""
        if not self.value_change_timer:
            return 0.0
        
        elapsed = current_time_ms - self.value_change_timer
        if elapsed > self.config.change_duration:
            return 0.0
        
        return 1.0 - (elapsed / self.config.change_duration)
    
    def was_damage(self) -> bool:
        """Check if the last change was damage."""
        return self.previous_value > self.target_value
