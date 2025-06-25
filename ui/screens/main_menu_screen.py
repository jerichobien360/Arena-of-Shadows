import pygame
import math
from contextlib import suppress
from typing import Dict, List, Any
from dataclasses import dataclass
from ui.effects.particles import Particle
from ui.effects.lighting import LightingConfig


class MainMenuRenderer:
    """Handles all visual rendering for the main menu"""
    
    def __init__(self, font: pygame.font.Font, lighting_config: LightingConfig):
        self.font = font
        self.lighting_config = lighting_config
        
        # Load and prepare visual assets
        self.background_image = self._load_background()
        self._create_surfaces()
        
    def _load_background(self) -> pygame.Surface:
        """Load background with graceful fallback"""
        from settings import SCREEN_WIDTH, SCREEN_HEIGHT
        
        # Try to load background image
        with suppress(pygame.error):
            bg = pygame.image.load("assets/background/background_2.jpg")
            return pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Use gradient fallback if image fails
        print("Warning: Using gradient background fallback")
        return self._create_gradient_background()
        
    def _create_gradient_background(self) -> pygame.Surface:
        """Generate fallback gradient background"""
        from settings import SCREEN_WIDTH, SCREEN_HEIGHT
        
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Create dark blue-green gradient
        for y in range(SCREEN_HEIGHT):
            gradient_ratio = y / SCREEN_HEIGHT
            red = int(15 + (10 * gradient_ratio))
            green = int(15 + (20 * gradient_ratio))
            blue = int(15 + (20 * gradient_ratio))
            color = (red, green, blue)
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))
            
        return surface
        
    def _create_surfaces(self):
        """Create reusable surfaces for effects"""
        from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK
        
        self.surfaces = {
            'fade': pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)),
            'lighting': pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA),
            'dim': pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        }
        self.surfaces['fade'].fill(BLACK)
        
    def _calculate_lighting_value(self, lighting_time: float) -> float:
        """Calculate current lighting intensity with natural variation"""
        cfg = self.lighting_config
        
        # Natural light variation (wind through trees effect)
        base_variation = math.sin(lighting_time * cfg.variation_speed) * cfg.variation_amp
        flicker_effect = math.sin(lighting_time * 3.2) * 0.02
        current_light = cfg.ambient + base_variation + flicker_effect
        
        # Clamp between reasonable values
        return max(0.2, min(0.8, current_light))
        
    def _update_atmospheric_lighting(self, lighting_time: float):
        """Create realistic atmospheric lighting effects"""
        from settings import SCREEN_WIDTH, SCREEN_HEIGHT
        
        current_light = self._calculate_lighting_value(lighting_time)
        
        # Clear surfaces
        self.surfaces['lighting'].fill((0, 0, 0, 0))
        self.surfaces['dim'].fill((0, 0, 0, int(255 * (1.0 - self.lighting_config.background_dim))))
        
        # Add blue-purple night atmosphere
        atmosphere_intensity = int((1.0 - current_light) * 120)
        if atmosphere_intensity > 0:
            atmosphere_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            atmosphere_surface.fill((10, 15, 40, atmosphere_intensity))
            self.surfaces['lighting'].blit(atmosphere_surface, (0, 0))
    
    def _render_particles(self, screen: pygame.Surface, particles: Dict[str, List[Particle]]):
        """Render all particles in proper layering order"""
        # Render leaves first (background layer)
        for particle in particles.get('leaves', []):
            particle.render(screen)
            
        # Render fireflies on top (foreground layer)
        for particle in particles.get('fireflies', []):
            particle.render(screen)
    
    def _calculate_animation_progress(self, animate_state: Any) -> Dict[str, float]:
        """Calculate animation progress for each text element"""
        return {
            'title': min(1.0, max(0.0, (animate_state.text_appear - 0.8) / 1.5)),
            'start': min(1.0, max(0.0, (animate_state.text_appear - 1.0) / 1.2)),
            'controls': min(1.0, max(0.0, (animate_state.text_appear - 1.5) / 1.0))
        }
    
    def _ease_cubic(self, t: float) -> float:
        """Cubic easing function for smooth animations"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2
    
    def _render_animated_text(self, screen: pygame.Surface, animate_state: Any):
        """Render all text elements with smooth animations"""
        progress = self._calculate_animation_progress(animate_state)
        
        self._render_title(screen, progress['title'], animate_state.title_pulse)
        self._render_start_prompt(screen, progress['start'], animate_state.title_pulse)
        self._render_controls_text(screen, progress['controls'])
    
    def _render_title(self, screen: pygame.Surface, progress: float, pulse_time: float):
        """Render animated title with pulsing effect"""
        from settings import SCREEN_WIDTH
        
        title_alpha = int(255 * self._ease_cubic(progress))
        if title_alpha <= 0:
            return
            
        # Create pulsing scale effect
        pulse_scale = 1.0 + 0.05 * math.sin(pulse_time * 1.5)
        title_font = pygame.font.Font(None, int(72 * pulse_scale))
        title_surface = title_font.render("ARENA OF SHADOWS", True, (255, 255, 255))
        title_surface.set_alpha(title_alpha)
        
        # Position with floating motion
        float_offset = int(5 * math.sin(pulse_time * 2))
        title_x = SCREEN_WIDTH // 2 - title_surface.get_width() // 2
        title_y = 160 + float_offset
        screen.blit(title_surface, (title_x, title_y))
    
    def _render_start_prompt(self, screen: pygame.Surface, progress: float, pulse_time: float):
        """Render start prompt with breathing effect"""
        from settings import SCREEN_WIDTH
        
        start_alpha = int(255 * self._ease_cubic(progress))
        if start_alpha <= 0:
            return
            
        start_surface = self.font.render("Press ENTER to Start", True, (180, 220, 180))
        
        # Apply breathing effect when fully visible
        if start_alpha >= 200:
            breathing_alpha = int(255 * (0.6 + 0.4 * math.sin(pulse_time * 2)))
            start_surface.set_alpha(breathing_alpha)
        else:
            start_surface.set_alpha(start_alpha)
        
        start_x = SCREEN_WIDTH // 2 - start_surface.get_width() // 2
        screen.blit(start_surface, (start_x, 260))
    
    def _render_controls_text(self, screen: pygame.Surface, progress: float):
        """Render controls information"""
        from settings import SCREEN_WIDTH
        
        controls_alpha = int(255 * self._ease_cubic(progress))
        if controls_alpha <= 0:
            return
            
        controls_surface = self.font.render("WASD/Arrows: Move | SPACE: Attack", True, (120, 160, 120))
        controls_surface.set_alpha(controls_alpha)
        
        controls_x = SCREEN_WIDTH // 2 - controls_surface.get_width() // 2
        screen.blit(controls_surface, (controls_x, 310))
    
    def render(self, screen: pygame.Surface, particles: Dict[str, List[Particle]], 
              animate_state: Any, lighting_time: float):
        """Main render method - orchestrates all visual elements"""
        # Render background layers
        screen.blit(self.background_image, (0, 0))
        screen.blit(self.surfaces['dim'], (0, 0))
        
        # Render particles
        self._render_particles(screen, particles)
        
        # Apply atmospheric lighting
        self._update_atmospheric_lighting(lighting_time)
        screen.blit(self.surfaces['lighting'], (0, 0))
        
        # Render animated text elements
        self._render_animated_text(screen, animate_state)
        
        # Apply fade overlay for transitions
        if animate_state.fade_alpha > 0:
            self.surfaces['fade'].set_alpha(int(animate_state.fade_alpha))
            screen.blit(self.surfaces['fade'], (0, 0))
