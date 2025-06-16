from settings import *
import random
from typing import Tuple

class Camera:
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.screen_width = width
        self.screen_height = height
        self.target_x = 0
        self.target_y = 0
        self.smoothing = CAMERA_SMOOTHING
        self.shake_intensity = 0
        self.shake_duration = 0
        self.zoom = 1.0
        self.target_zoom = 1.0
        
    def update(self, dt: float, target_x: float, target_y: float) -> None:
        """Update camera position to follow target with smooth movement"""
        # Calculate target camera position (center target on screen)
        half_screen = (self.screen_width / 2, self.screen_height / 2)
        self.target_x, self.target_y = (target_x - half_screen[0] / self.zoom, 
                                        target_y - half_screen[1] / self.zoom)
        
        # Smooth camera movement
        self.x += (self.target_x - self.x) * self.smoothing
        self.y += (self.target_y - self.y) * self.smoothing
        
        # Update screen shake
        if self.shake_duration > 0:
            self.shake_duration -= dt
            shake_offset = (random.uniform(-self.shake_intensity, self.shake_intensity) / self.zoom 
                            for _ in range(2))
            self.x, self.y = (pos + offset for pos, offset in zip((self.x, self.y), shake_offset))
        
        # Smooth zoom
        self.zoom += (self.target_zoom - self.zoom) * 0.05
    
    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """Convert world coordinates to screen coordinates"""
        return ((world_x - self.x) * self.zoom, (world_y - self.y) * self.zoom)
    
    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates"""
        return (screen_x / self.zoom + self.x, screen_y / self.zoom + self.y)
    
    def add_shake(self, intensity: float, duration: float) -> None:
        """Add screen shake effect"""
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_duration = max(self.shake_duration, duration)
    
    def set_zoom(self, zoom_level: float) -> None:
        """Set target zoom level"""
        self.target_zoom = max(0.5, min(3.0, zoom_level))
    
    def get_visible_bounds(self) -> Tuple[float, float, float, float]:
        """Get the bounds of what's visible on screen in world coordinates"""
        left, top = self.x / self.zoom, self.y / self.zoom
        return (left, top, left + self.screen_width / self.zoom, top + self.screen_height / self.zoom)
    
    def get_center_position(self) -> Tuple[float, float]:
        """Get the center position of the camera in world coordinates"""
        return (self.x + self.screen_width / 2 / self.zoom, self.y + self.screen_height / 2 / self.zoom)
