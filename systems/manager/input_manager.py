from dataclasses import dataclass, field
import pygame


@dataclass
class InputHandler:
    """Clean input handling with state tracking."""
    prev_keys: set = field(default_factory=set)
    curr_keys: set = field(default_factory=set)
    
    def update(self) -> None:
        """Update key states for frame-based input detection."""
        self.prev_keys = self.curr_keys.copy()
        pressed = pygame.key.get_pressed()
        self.curr_keys = {i for i, key in enumerate(pressed) if key}
    
    def is_key_just_pressed(self, key: int) -> bool:
        """Check if key was just pressed this frame."""
        return key in self.curr_keys and key not in self.prev_keys
