import pygame
import math
from contextlib import suppress
from typing import Dict, List, Any
from dataclasses import dataclass
from ui.effects.particles import Particle


@dataclass
class LightingConfig:
    """Lighting configuration for atmospheric effects"""
    ambient: float = 0.4
    variation_speed: float = 0.8
    variation_amp: float = 0.05
    background_dim: float = 0.25


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
        
        with suppress(pygame.error):
            bg = pygame.image.load("assets/background/background_2.jpg")
            return pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        print("Warning: Using gradient background fallback")
        return self._create_gradient_background()
        
    def _create_gradient_background(self) -> pygame.Surface:
        """Generate fallback gradient background"""
        from settings import SCREEN_WIDTH, SCREEN_HEIGHT
        
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            # Dark blue-green gradient
            color = tuple(int(15 + (delta * ratio)) for delta in [10, 20, 20])
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
        
    def _update_atmospheric_lighting(self, lighting_time: float):
        """Create realistic atmospheric lighting effects"""
        from settings import SCREEN_WIDTH, SCREEN_HEIGHT
        
        cfg = self.lighting_config
        
        # Natural light variation (wind through trees effect)
        base_var = math.sin(lighting_time * cfg.variation_speed) * cfg.variation_amp
        flicker = math.sin(lighting_time * 3.2) * 0.02
        current_light = max(0.2, min(0.8, cfg.ambient + base_var + flicker))
        
        # Clear and prepare surfaces
        self.surfaces['lighting'].fill((0, 0, 0, 0))
        self.surfaces['dim'].fill((0, 0, 0, int(255 * (1.0 - cfg.background_dim))))
        
        # Add blue-purple night atmosphere
        atmosphere_alpha = int((1.0 - current_light) * 120)
        if atmosphere_alpha > 0:
            atm_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            atm_surf.fill((10, 15, 40, atmosphere_alpha))
            self.surfaces['lighting'].blit(atm_surf, (0, 0))
    
    def _render_particles(self, screen: pygame.Surface, particles: Dict[str, List[Particle]]):
        """Render all particles in proper layering order"""
        # Render leaves first (background layer)
        for particle in particles.get('leaves', []):
            particle.render(screen)
            
        # Render fireflies on top (foreground layer)
        for particle in particles.get('fireflies', []):
            particle.render(screen)
    
    def _render_animated_text(self, screen: pygame.Surface, anim_state: Any):
        """Render all text elements with smooth animations"""
        from settings import SCREEN_WIDTH
        
        def ease_cubic(t: float) -> float:
            """Cubic easing function for smooth animations"""
            return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
        
        # Calculate animation progress for each text element
        title_progress = min(1.0, max(0.0, (anim_state.text_appear - 0.8) / 1.5))
        start_progress = min(1.0, max(0.0, (anim_state.text_appear - 1.0) / 1.2))
        controls_progress = min(1.0, max(0.0, (anim_state.text_appear - 1.5) / 1.0))
        
        self._render_title(screen, title_progress, anim_state.title_pulse)
        self._render_start_prompt(screen, start_progress, anim_state.title_pulse)
        self._render_controls_text(screen, controls_progress)
    
    def _render_title(self, screen: pygame.Surface, progress: float, pulse_time: float):
        """Render animated title with pulsing effect"""
        from settings import SCREEN_WIDTH
        
        def ease_cubic(t): return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
        
        title_alpha = int(255 * ease_cubic(progress))
        if title_alpha <= 0:
            return
            
        # Pulsing scale effect
        title_scale = 1.0 + 0.05 * math.sin(pulse_time * 1.5)
        title_font = pygame.font.Font(None, int(72 * title_scale))
        title_surface = title_font.render("ARENA OF SHADOWS", True, (255, 255, 255))
        title_surface.set_alpha(title_alpha)
        
        # Center with floating motion
        title_pos = (
            SCREEN_WIDTH // 2 - title_surface.get_width() // 2,
            160 + int(5 * math.sin(pulse_time * 2))
        )
        screen.blit(title_surface, title_pos)
    
    def _render_start_prompt(self, screen: pygame.Surface, progress: float, pulse_time: float):
        """Render start prompt with breathing effect"""
        from settings import SCREEN_WIDTH
        
        def ease_cubic(t): return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
        
        start_alpha = int(255 * ease_cubic(progress))
        if start_alpha <= 0:
            return
            
        start_surface = self.font.render("Press ENTER to Start", True, (180, 220, 180))
        
        # Apply breathing effect when fully visible
        if start_alpha >= 200:
            breath_alpha = int(255 * (0.6 + 0.4 * math.sin(pulse_time * 2)))
            start_surface.set_alpha(breath_alpha)
        else:
            start_surface.set_alpha(start_alpha)
        
        start_pos = (SCREEN_WIDTH // 2 - start_surface.get_width() // 2, 260)
        screen.blit(start_surface, start_pos)
    
    def _render_controls_text(self, screen: pygame.Surface, progress: float):
        """Render controls information"""
        from settings import SCREEN_WIDTH
        
        def ease_cubic(t): return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
        
        controls_alpha = int(255 * ease_cubic(progress))
        if controls_alpha <= 0:
            return
            
        controls_surface = self.font.render("WASD/Arrows: Move | SPACE: Attack", True, (120, 160, 120))
        controls_surface.set_alpha(controls_alpha)
        controls_pos = (SCREEN_WIDTH // 2 - controls_surface.get_width() // 2, 310)
        screen.blit(controls_surface, controls_pos)
    
    def render(self, screen: pygame.Surface, particles: Dict[str, List[Particle]], 
              anim_state: Any, lighting_time: float):
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
        self._render_animated_text(screen, anim_state)
        
        # Apply fade overlay for transitions
        if anim_state.fade_alpha > 0:
            self.surfaces['fade'].set_alpha(int(anim_state.fade_alpha))
            screen.blit(self.surfaces['fade'], (0, 0))
