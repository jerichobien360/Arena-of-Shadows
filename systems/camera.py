from settings import *
import random

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
        
    def update(self, dt, target_x, target_y):
        """Update camera position to follow target with smooth movement"""
        # Calculate target camera position (center target on screen)
        self.target_x = target_x - self.screen_width // 2
        self.target_y = target_y - self.screen_height // 2
        
        # Smooth camera movement
        self.x += (self.target_x - self.x) * self.smoothing
        self.y += (self.target_y - self.y) * self.smoothing
        
        # Update screen shake
        if self.shake_duration > 0:
            self.shake_duration -= dt
            shake_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            shake_y = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.x += shake_x
            self.y += shake_y
        
        # Smooth zoom
        self.zoom += (self.target_zoom - self.zoom) * 0.05
    
    def world_to_screen(self, world_x, world_y):
        """Convert world coordinates to screen coordinates"""
        screen_x = (world_x - self.x) * self.zoom
        screen_y = (world_y - self.y) * self.zoom
        return screen_x, screen_y
    
    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        world_x = (screen_x / self.zoom) + self.x
        world_y = (screen_y / self.zoom) + self.y
        return world_x, world_y
    
    def add_shake(self, intensity, duration):
        """Add screen shake effect"""
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_duration = max(self.shake_duration, duration)
    
    def set_zoom(self, zoom_level):
        """Set target zoom level"""
        self.target_zoom = max(0.5, min(3.0, zoom_level))
    
    def get_visible_bounds(self):
        """Get the bounds of what's visible on screen in world coordinates"""
        left = self.x / self.zoom
        top = self.y / self.zoom
        right = (self.x + self.screen_width) / self.zoom
        bottom = (self.y + self.screen_height) / self.zoom
        return left, top, right, bottom
