import pygame
import os
from typing import Dict, Optional, Tuple

class SpriteManager:
    """Manages sprite loading, scaling, and caching for the game."""
    
    def __init__(self):
        self.sprites: Dict[str, pygame.Surface] = {}
        self.sprite_sheets: Dict[str, pygame.Surface] = {}
        self.animations: Dict[str, list] = {}
        
    def load_sprite(self, name: str, path: str, scale: Optional[Tuple[int, int]] = None) -> bool:
        """Load a single sprite image."""
        try:
            if not os.path.exists(path):
                print(f"Warning: Sprite file not found: {path}")
                return False
                
            sprite = pygame.image.load(path).convert_alpha()
            
            if scale:
                sprite = pygame.transform.scale(sprite, scale)
                
            self.sprites[name] = sprite
            return True
            
        except pygame.error as e:
            print(f"Error loading sprite {name}: {e}")
            return False
    
    def load_sprite_sheet(self, name: str, path: str, frame_width: int, frame_height: int, 
                         frames: int, scale: Optional[Tuple[int, int]] = None) -> bool:
        """Load a sprite sheet and extract individual frames."""
        try:
            if not os.path.exists(path):
                print(f"Warning: Sprite sheet not found: {path}")
                return False
                
            sheet = pygame.image.load(path).convert_alpha()
            frames_list = []
            
            # Extract frames from sprite sheet
            for i in range(frames):
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
                
                if scale:
                    frame = pygame.transform.scale(frame, scale)
                    
                frames_list.append(frame)
            
            self.animations[name] = frames_list
            return True
            
        except pygame.error as e:
            print(f"Error loading sprite sheet {name}: {e}")
            return False
    
    def get_sprite(self, name: str) -> Optional[pygame.Surface]:
        """Get a sprite by name."""
        return self.sprites.get(name)
    
    def get_animation_frame(self, name: str, frame_index: int) -> Optional[pygame.Surface]:
        """Get a specific frame from an animation."""
        if name in self.animations and 0 <= frame_index < len(self.animations[name]):
            return self.animations[name][frame_index]
        return None
    
    def create_fallback_sprite(self, name: str, size: Tuple[int, int], color: Tuple[int, int, int]) -> pygame.Surface:
        """Create a simple colored rectangle as fallback sprite."""
        sprite = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.circle(sprite, color, (size[0]//2, size[1]//2), min(size)//2)
        self.sprites[name] = sprite
        return sprite
