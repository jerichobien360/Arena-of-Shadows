from settings import *
from systems.manager.asset_manager import *
from ui.visuals.circle import Circle

from typing import Dict, List, Any
from dataclasses import dataclass

import pygame
import math


class MainMenuRenderer:
    """Handles main menu visual rendering"""
    
    def __init__(self, font: pygame.font.Font, lighting_config):
        """Integrated Components from UI, Managers, Pygame"""
        self.font = font
        self.lighting_config = lighting_config
        self.background_image = self._load_background()
        self.surfaces = self._create_surfaces()
        
        # Custom game visuals
        self.circles = []
        self._init_circle()
        
    def _init_circle(self):
        for _ in range(50): # Number of circles to be created
            x = random.randint(-100, SCREEN_WIDTH + 100)
            y = random.randint(-100, SCREEN_HEIGHT + 100)
            radius = random.randint(10, 40)
            color = BLACK # random.choice(BLACK)
            speed = random.uniform(0.5, 2.0)  # Variance of Speed
            self.circles.append(Circle(x, y, radius, color, speed)) # Create a bunch of circles
        
    def _load_background(self) -> pygame.Surface:
        """Load background with gradient fallback""" 
        file_path = MENU_BACKGROUND_TILE_PATH
        return image_background_load(file_path, SCREEN_WIDTH, SCREEN_HEIGHT)
        
    def _create_gradient_background(self) -> pygame.Surface:
        """Generate dark blue-green gradient background"""
        screen_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            color = (15 + int(10 * ratio),
                     15 + int(20 * ratio),
                     15 + int(20 * ratio))
            pygame.draw.line(screen_surface, color,
                            (0, y), (SCREEN_WIDTH, y))
        
        return screen_surface
        
    def _create_surfaces(self) -> Dict[str, pygame.Surface]:
        """Create reusable surfaces for effects"""
        surfaces = {
            'fade': pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)),
            'lighting': pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA),
            'dim': pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        }
        surfaces['fade'].fill(BLACK)
        return surfaces
        
    def _get_lighting_intensity(self, time: float) -> float:
        """Calculate lighting intensity with natural variation"""
        config = self.lighting_config
        variation = math.sin(time * config.variation_speed) * config.variation_amp
        flicker = math.sin(time * 3.2) * 0.02
        return max(0.2, min(0.8, config.ambient + variation + flicker))
        
    def _update_lighting(self, time: float):
        """Update atmospheric lighting effects"""
        intensity = self._get_lighting_intensity(time)
        
        # Clear and setup surfaces
        self.surfaces['lighting'].fill((0, 0, 0, 0))
        dim_alpha = int(255 * (1.0 - self.lighting_config.background_dim))
        self.surfaces['dim'].fill((0, 0, 0, dim_alpha))
        
        # Add night atmosphere
        atmosphere_alpha = int((1.0 - intensity) * 120)
        if atmosphere_alpha > 0:
            atmosphere = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            atmosphere.fill((10, 15, 40, atmosphere_alpha))
            self.surfaces['lighting'].blit(atmosphere, (0, 0))
    
    def _render_particles(self, screen: pygame.Surface, particles: Dict[str, List]):
        """Render particles in layered order"""
        for particle in particles.get('leaves', []):
            particle.render(screen)
        for particle in particles.get('fireflies', []):
            particle.render(screen)
    
    @staticmethod
    def _ease_cubic(t: float) -> float:
        """Smooth cubic easing function"""
        return 4 * t**3 if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
    
    def _get_text_alpha(self, appear_time: float, start_offset: float, duration: float) -> int:
        """Calculate text alpha based on appearance timing"""
        progress = max(0.0, min(1.0, (appear_time - start_offset) / duration))
        return int(255 * self._ease_cubic(progress))
    
    def _render_title(self, screen: pygame.Surface, appear_time: float, pulse_time: float):
        """Render animated title with pulsing effect"""
        alpha = self._get_text_alpha(appear_time, 0.8, 1.5)
        if alpha <= 0:
            return
            
        # Pulsing scale and floating motion
        scale = 1.0 + 0.05 * math.sin(pulse_time * 1.5)
        float_y = 160 + int(5 * math.sin(pulse_time * 2))
        
        font = pygame.font.Font(None, int(72 * scale))
        surface = font.render("ARENA OF SHADOWS", True, (255, 255, 255))
        surface.set_alpha(alpha)
        
        x = SCREEN_WIDTH // 2 - surface.get_width() // 2
        screen.blit(surface, (x, float_y))
    
    def _render_start_prompt(self, screen: pygame.Surface, appear_time: float, pulse_time: float):
        """Render start prompt with breathing effect"""
        alpha = self._get_text_alpha(appear_time, 1.0, 1.2)
        if alpha <= 0:
            return
            
        surface = self.font.render("Press ENTER to Start", False, (180, 220, 180))
        
        # Breathing effect when fully visible
        if alpha >= 200:
            breathing_alpha = int(255 * (0.6 + 0.4 * math.sin(pulse_time * 2)))
            surface.set_alpha(breathing_alpha)
        else:
            surface.set_alpha(alpha)
        
        x = SCREEN_WIDTH // 2 - surface.get_width() // 2
        screen.blit(surface, (x, 260))
    
    def _render_controls(self, screen: pygame.Surface, appear_time: float):
        """Render controls information"""
        alpha = self._get_text_alpha(appear_time, 1.5, 1.0)
        if alpha <= 0:
            return
            
        surface = self.font.render("WASD/Arrows: Move | SPACE: Attack | E: Dash", True, (120, 160, 120))
        surface.set_alpha(alpha)
        
        x = SCREEN_WIDTH // 2 - surface.get_width() // 2
        screen.blit(surface, (x, 310))
    
    def render(self, screen: pygame.Surface, particles: Dict[str, List], 
              animate_state: Any, lighting_time: float):
        """Main render method"""
        # Background layers
        screen.blit(self.background_image, (0, 0))
        screen.blit(self.surfaces['dim'], (0, 0))
        
        # Visual Rendering
        for circle in self.circles:
            circle.update()
            circle.draw(screen)
        
        # Particles and lighting
        self._render_particles(screen, particles)
        self._update_lighting(lighting_time)
        screen.blit(self.surfaces['lighting'], (0, 0))
        
        # Text elements
        self._render_title(screen, animate_state.text_appear, animate_state.title_pulse)
        self._render_start_prompt(screen, animate_state.text_appear, animate_state.title_pulse)
        self._render_controls(screen, animate_state.text_appear)
        
        # Fade overlay
        if animate_state.fade_alpha > 0:
            self.surfaces['fade'].set_alpha(int(animate_state.fade_alpha))
            screen.blit(self.surfaces['fade'], (0, 0))
