import pygame
import math
from settings import *


class GameOverVisuals:
    """Handles all visual effects and animations for the game over screen"""
    
    def __init__(self, font):
        self.font = font
        self.timer = 0.0
        
        # Animation configuration
        self.config = {
            'overlay_fade_duration': 0.8,
            'overlay_max_alpha': int(255 * 0.12),
            'text_delay': 0.5,
            'game_over_duration': 1.0,
            'restart_delay_factor': 0.7,
            'restart_duration': 0.8,
            'pulse_intensity': 0.1,
            'pulse_speed': 2.0,
            'float_speed': 1.5,
            'float_amplitude': 2.0
        }
        
        # Create reusable overlay surface
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay.fill((0, 0, 0))
        
        # Cached text surfaces
        self._game_over_text = self.font.render("GAME OVER", True, WHITE)
        self._restart_text = self.font.render("Press ENTER to return to menu", True, GRAY)
        self._shadow_text = self.font.render("GAME OVER", True, (20, 20, 20))
    
    def reset(self):
        """Reset animation state"""
        self.timer = 0.0
    
    def update(self, dt):
        """Update animation timer"""
        self.timer += dt
    
    def render(self, screen):
        """Render all visual elements with animations"""
        self._render_overlay(screen)
        self._render_game_over_text(screen)
        self._render_restart_text(screen)
        self._render_particles(screen)
    
    def _render_overlay(self, screen):
        """Render the background overlay with fade-in"""
        progress = min(1.0, self.timer / self.config['overlay_fade_duration'])
        alpha = int(self.config['overlay_max_alpha'] * (progress * progress))  # Ease-in
        
        if alpha > 0:
            self.overlay.set_alpha(alpha)
            screen.blit(self.overlay, (0, 0))
    
    def _render_game_over_text(self, screen):
        """Render main 'GAME OVER' text with animations"""
        start_time = self.config['text_delay']
        if self.timer < start_time:
            return
        
        # Calculate fade progress
        progress = min(1.0, (self.timer - start_time) / self.config['game_over_duration'])
        alpha = int(255 * (1.0 - (1.0 - progress) ** 3))  # Ease-out curve
        
        if alpha <= 0:
            return
        
        # Apply pulsing effect after fade completes
        scale = 1.0
        if progress >= 1.0:
            pulse = math.sin(self.timer * self.config['pulse_speed'])
            scale = 1.0 + pulse * self.config['pulse_intensity']
        
        # Scale text if needed
        text = self._game_over_text
        if scale != 1.0:
            size = text.get_size()
            new_size = (int(size[0] * scale), int(size[1] * scale))
            text = pygame.transform.scale(text, new_size)
        
        # Position text
        x = SCREEN_WIDTH // 2 - text.get_width() // 2
        y = SCREEN_HEIGHT // 2 - 50
        
        # Render shadow
        if alpha > 100:
            shadow_alpha = min(80, alpha - 100)
            shadow = self._shadow_text if scale == 1.0 else pygame.transform.scale(self._shadow_text, new_size)
            shadow.set_alpha(shadow_alpha)
            screen.blit(shadow, (x + 3, y + 3))
        
        # Render main text
        text.set_alpha(alpha)
        screen.blit(text, (x, y))
    
    def _render_restart_text(self, screen):
        """Render restart instruction with fade and floating animation"""
        start_time = (self.config['text_delay'] + 
                     self.config['game_over_duration'] * self.config['restart_delay_factor'])
        
        if self.timer < start_time:
            return
        
        # Calculate fade progress
        progress = min(1.0, (self.timer - start_time) / self.config['restart_duration'])
        alpha = int(180 * progress)  # Linear fade, dimmer than main text
        
        if alpha <= 0:
            return
        
        # Apply floating animation
        float_offset = (math.sin(self.timer * self.config['float_speed']) * 
                       self.config['float_amplitude'])
        
        # Position text
        x = SCREEN_WIDTH // 2 - self._restart_text.get_width() // 2
        y = SCREEN_HEIGHT // 2 + 30 + float_offset
        
        # Render glow effect when fully visible
        if alpha > 150:
            glow_alpha = min(30, alpha - 150)
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                glow_text = self.font.render("Press ENTER to return to menu", True, WHITE)
                glow_text.set_alpha(glow_alpha)
                screen.blit(glow_text, (x + dx, y + dy))
        
        # Render main text
        text = self._restart_text.copy()
        text.set_alpha(alpha)
        screen.blit(text, (x, y))
    
    def _render_particles(self, screen):
        """Render atmospheric particle effects"""
        if self.timer < 2.0:  # Don't show particles until animations settle
            return
        
        for i in range(8):
            # Generate particle properties
            base_time = self.timer + i * 0.5
            x = (SCREEN_WIDTH * 0.2 + i * SCREEN_WIDTH * 0.1 + 
                 math.sin(base_time * 0.8) * 30)
            y = (SCREEN_HEIGHT * 0.3 + math.cos(base_time * 0.6) * 40 + i * 15)
            
            # Calculate particle alpha with fade in/out
            alpha = int(20 + math.sin(base_time * 1.2) * 15)
            alpha = max(0, min(35, alpha))
            
            if alpha > 0:
                size = 2 + int(math.sin(base_time))
                self._render_particle(screen, (int(x), int(y)), size, alpha)
    
    def _render_particle(self, screen, pos, size, alpha):
        """Render a single particle with alpha blending"""
        particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        color = (100, 100, 100, alpha)
        pygame.draw.circle(particle_surf, color, (size, size), size)
        screen.blit(particle_surf, pos)
