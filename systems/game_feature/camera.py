"""Camera system with a Zoom, Conversion, and Optimization"""

from settings import *
import random
from typing import Tuple


class Camera:
    """Camera system with smooth following, screen shake, and zoom functionality."""
    
    def __init__(self, width: int, height: int):
        # Position and movement
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        
        # Screen dimensions
        self.screen_width = width
        self.screen_height = height
        self._half_screen = (width // 2, height // 2)
        
        # Camera settings
        self.smoothing = CAMERA_SMOOTHING
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.zoom_smoothing = 0.05
        
        # Screen shake
        self.shake_intensity = 0.0
        self.shake_duration = 0.0
        
        # Zoom constraints
        self.min_zoom = 0.5
        self.max_zoom = 3.0
    
    def update(self, dt: float, target_x: float, target_y: float) -> None:
        """Update camera position to follow target with smooth movement."""
        self._update_target_position(target_x, target_y)
        self._apply_smooth_movement()
        self._apply_screen_shake(dt)
        self._apply_smooth_zoom()
    
    def _update_target_position(self, target_x: float, target_y: float) -> None:
        """Calculate target camera position to center target on screen."""
        half_w, half_h = self._half_screen
        self.target_x = target_x - half_w / self.zoom
        self.target_y = target_y - half_h / self.zoom
    
    def _apply_smooth_movement(self) -> None:
        """Apply smooth camera movement towards target."""
        self.x += (self.target_x - self.x) * self.smoothing
        self.y += (self.target_y - self.y) * self.smoothing
    
    def _apply_screen_shake(self, dt: float) -> None:
        """Apply screen shake effect if active."""
        if self.shake_duration <= 0:
            return
        
        self.shake_duration -= dt
        
        # Generate random shake offsets
        shake_x = random.uniform(-self.shake_intensity, self.shake_intensity) / self.zoom
        shake_y = random.uniform(-self.shake_intensity, self.shake_intensity) / self.zoom
        
        self.x += shake_x
        self.y += shake_y
    
    def _apply_smooth_zoom(self) -> None:
        """Apply smooth zoom transition."""
        self.zoom += (self.target_zoom - self.zoom) * self.zoom_smoothing
    
    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """Convert world coordinates to screen coordinates."""
        screen_x = (world_x - self.x) * self.zoom
        screen_y = (world_y - self.y) * self.zoom
        return (screen_x, screen_y)
    
    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        world_x = screen_x / self.zoom + self.x
        world_y = screen_y / self.zoom + self.y
        return (world_x, world_y)
    
    def add_shake(self, intensity: float, duration: float) -> None:
        """Add screen shake effect with given intensity and duration."""
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_duration = max(self.shake_duration, duration)
    
    def set_zoom(self, zoom_level: float) -> None:
        """Set target zoom level within constraints."""
        self.target_zoom = max(self.min_zoom, min(self.max_zoom, zoom_level))
    
    def get_visible_bounds(self) -> Tuple[float, float, float, float]:
        """Get the bounds of what's visible on screen in world coordinates.
        
        Returns:
            Tuple of (left, top, right, bottom) coordinates.
        """
        left = self.x
        top = self.y
        right = left + self.screen_width / self.zoom
        bottom = top + self.screen_height / self.zoom
        return (left, top, right, bottom)
    
    def get_center_position(self) -> Tuple[float, float]:
        """Get the center position of the camera in world coordinates."""
        center_x = self.x + self.screen_width / 2 / self.zoom
        center_y = self.y + self.screen_height / 2 / self.zoom
        return (center_x, center_y)
    
    def is_point_visible(self, world_x: float, world_y: float, margin: float = 0) -> bool:
        """Check if a world point is visible on screen with optional margin."""
        left, top, right, bottom = self.get_visible_bounds()
        return (left - margin <= world_x <= right + margin and 
                top - margin <= world_y <= bottom + margin)
    
    def clamp_to_bounds(self, min_x: float, min_y: float, max_x: float, max_y: float) -> None:
        """Clamp camera position to world bounds."""
        # Calculate camera bounds considering zoom
        cam_width = self.screen_width / self.zoom
        cam_height = self.screen_height / self.zoom
        
        # Clamp target position
        self.target_x = max(min_x, min(max_x - cam_width, self.target_x))
        self.target_y = max(min_y, min(max_y - cam_height, self.target_y))
        
        # Clamp current position
        self.x = max(min_x, min(max_x - cam_width, self.x))
        self.y = max(min_y, min(max_y - cam_height, self.y))
    
    def screen_view(self, world_size:float) -> float:
        """Convert world size to screen size based on zoom"""
        return world_size * self.zoom # pow(self.zoom, pow(0.3, 0.5)) # Non-exponential
    
    @property
    def position(self) -> Tuple[float, float]:
        """Get current camera position."""
        return (self.x, self.y)
    
    @property
    def is_shaking(self) -> bool:
        """Check if camera is currently shaking."""
        return self.shake_duration > 0
