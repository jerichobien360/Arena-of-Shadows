from settings import *
import pygame
import math
import random
from contextlib import suppress
from dataclasses import dataclass
from typing import Tuple

# Game state management
from game_states.gameplay import *


@dataclass
class ParticleConfig:
    """Configuration class for particle properties to reduce repetition"""
    speed_range: Tuple[float, float]
    size_range: Tuple[float, float]
    color_options: list
    alpha_range: Tuple[float, float] = (120, 200)


class Particle:
    """Base particle class with common behavior"""
    def __init__(self, x, y):
        self.x = self.start_x = x
        self.y = self.start_y = y


class Leaf(Particle):
    """Animated falling leaf with natural movement patterns"""
    
    CONFIG = ParticleConfig(
        speed_range=(15, 25),
        size_range=(2, 6),
        color_options=[(34, 89, 34), (67, 92, 35), (45, 67, 27), (30, 105, 30)]
    )
    
    def __init__(self, x, y):
        super().__init__(x, y)
        # Initialize all properties using random ranges for natural variation
        self.speed_y = random.uniform(*self.CONFIG.speed_range)
        self.speed_x = random.uniform(-5, 5)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-45, 45)
        self.sway_amplitude = random.uniform(5, 15)
        self.sway_frequency = random.uniform(0.5, 1.5)
        self.size = random.uniform(*self.CONFIG.size_range)
        self.color = random.choice(self.CONFIG.color_options)
        self.alpha = random.uniform(*self.CONFIG.alpha_range)
        self.time = 0
        
    def update(self, dt):
        """Update leaf position with natural swaying motion"""
        self.time += dt
        self.y += self.speed_y * dt
        self.x += self.speed_x * dt + math.sin(self.time * self.sway_frequency) * self.sway_amplitude * dt
        self.rotation += self.rotation_speed * dt
        
        # Reset position when leaf falls off screen
        if self.y > SCREEN_HEIGHT + 20:
            self.y = -20
            self.x = random.uniform(-50, SCREEN_WIDTH + 50)
            
    def render(self, screen):
        """Render organic leaf shape with rotation and transparency"""
        # Generate leaf points with natural variation
        points = []
        angle_offset = math.radians(self.rotation)
        for i in range(6):
            angle = (i * math.pi / 3) + angle_offset
            radius = self.size * (1 if i % 2 == 0 else 0.6)  # Alternating radius for organic shape
            points.append((
                self.x + math.cos(angle) * radius,
                self.y + math.sin(angle) * radius
            ))
        
        if len(points) >= 3:
            # Create alpha-blended surface for transparency
            leaf_surf = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
            adjusted_points = [(p[0] - self.x + self.size * 2, p[1] - self.y + self.size * 2) for p in points]
            pygame.draw.polygon(leaf_surf, (*self.color, int(self.alpha)), adjusted_points)
            screen.blit(leaf_surf, (self.x - self.size * 2, self.y - self.size * 2))


class Firefly(Particle):
    """Glowing firefly with realistic light emission and trailing effects"""
    
    CONFIG = ParticleConfig(
        speed_range=(8, 15),
        size_range=(1.5, 3),
        color_options=[(255, 255, 150), (150, 255, 150), (200, 200, 255)]
    )
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = random.uniform(*self.CONFIG.speed_range)
        self.direction = random.uniform(0, 2 * math.pi)
        self.direction_timer = 0
        self.direction_interval = random.uniform(2, 4)
        self.glow_phase = random.uniform(0, 2 * math.pi)
        self.glow_speed = random.uniform(2, 3)
        self.brightness = 0
        self.size = random.uniform(*self.CONFIG.size_range)
        self.trail_positions = []
        self.base_color = random.choice(self.CONFIG.color_options)
        
    def update(self, dt):
        """Update firefly movement with smooth direction changes and glow pulsing"""
        # Handle smooth direction changes for natural flight patterns
        self.direction_timer += dt
        if self.direction_timer >= self.direction_interval:
            self.direction += random.uniform(-math.pi/6, math.pi/6)
            self.direction_timer = 0
            self.direction_interval = random.uniform(2, 4)
            
        # Move with subtle wandering effect
        wander = math.sin(self.glow_phase * 0.5) * 0.2
        self.x += math.cos(self.direction + wander) * self.speed * dt
        self.y += math.sin(self.direction + wander) * self.speed * dt
        
        # Wrap around screen boundaries with margin for smooth transitions
        margin = 100
        self.x = (self.x + margin) % (SCREEN_WIDTH + 2 * margin) - margin
        self.y = (self.y + margin) % (SCREEN_HEIGHT + 2 * margin) - margin
            
        # Update natural glow pulsing
        self.glow_phase += self.glow_speed * dt
        pulse = (math.sin(self.glow_phase) + 1) * 0.5
        self.brightness = 0.3 + pulse * 0.7
        
        # Maintain light trail for realistic motion blur
        self.trail_positions.append((self.x, self.y))
        if len(self.trail_positions) > 12:
            self.trail_positions.pop(0)
            
    def render(self, screen):
        """Render firefly with multi-layered glow and trailing light effect"""
        # Render fading trail
        for i, (tx, ty) in enumerate(self.trail_positions[:-1]):
            trail_alpha = (i / len(self.trail_positions)) * self.brightness * 60
            trail_size = self.size * (i / len(self.trail_positions)) * 0.8
            if trail_size > 0.3:
                self._render_glow(screen, tx, ty, trail_size, trail_alpha)
        
        # Render main firefly with realistic multi-layer glow
        glow_intensity = int(self.brightness * 200)
        glow_size = self.size * 8
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        
        # Create layered glow effect for realism
        glow_layers = [
            (glow_size, glow_intensity * 0.15),      # Outer glow
            (glow_size * 0.6, glow_intensity * 0.3), # Middle glow
            (glow_size * 0.3, glow_intensity * 0.6), # Inner glow
        ]
        
        center = (glow_size, glow_size)
        for radius, alpha in glow_layers:
            pygame.draw.circle(glow_surf, (*self.base_color, int(alpha)), center, radius)
        
        # Bright core
        pygame.draw.circle(glow_surf, (255, 255, 255, glow_intensity), center, self.size)
        screen.blit(glow_surf, (self.x - glow_size, self.y - glow_size))
    
    def _render_glow(self, screen, x, y, size, alpha):
        """Helper method to render individual glow effect"""
        if alpha > 0:
            glow_surf = pygame.Surface((size * 6, size * 6), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.base_color, int(alpha)), (size * 3, size * 3), size * 2)
            screen.blit(glow_surf, (x - size * 3, y - size * 3))


class MainMenuState(GameState):
    """Main menu with animated background, particles, and smooth transitions"""
    
    def __init__(self, font, sound_manager):
        self.font = font
        self.sound_manager = sound_manager
        
        # Load background with error handling
        self.background_image = self._load_background()
        
        # Animation state - using single dict for cleaner organization
        self.anim_state = {
            'fade_alpha': 255, 'fade_speed': 200, 'fade_direction': 1,
            'transitioning': False, 'target': None,
            'title_pulse': 0, 'text_appear': 0, 'lighting': 0
        }
        
        # Lighting configuration
        self.lighting = {
            'ambient': 0.4, 'variation_speed': 0.8, 'variation_amp': 0.05,
            'background_dim': 0.25
        }
        
        # Initialize particle systems and surfaces
        self.particles = {'leaves': [], 'fireflies': []}
        self._init_particles()
        self._create_surfaces()
        
    def _load_background(self):
        """Load background image with graceful fallback"""
        with suppress(pygame.error):
            bg = pygame.image.load("assets/background/background_2.jpg")
            return pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        print("Warning: Using gradient background fallback")
        return self._create_gradient_background()
        
    def _create_gradient_background(self):
        """Generate gradient background as fallback"""
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            color = tuple(int(15 + (delta * ratio)) for delta in [10, 20, 20])  # Dark blue-green gradient
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))
        return surface
        
    def _init_particles(self):
        """Initialize particle systems with optimal distribution"""
        # Create leaves with natural spacing
        self.particles['leaves'] = [
            Leaf(random.uniform(-50, SCREEN_WIDTH + 50), random.uniform(-SCREEN_HEIGHT * 1.5, 0))
            for _ in range(12)
        ]
        
        # Create fireflies positioned away from edges
        self.particles['fireflies'] = [
            Firefly(random.uniform(150, SCREEN_WIDTH - 150), random.uniform(150, SCREEN_HEIGHT - 150))
            for _ in range(6)
        ]
        
    def _create_surfaces(self):
        """Create reusable surfaces for effects"""
        self.surfaces = {
            'fade': pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)),
            'lighting': pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA),
            'dim': pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        }
        self.surfaces['fade'].fill(BLACK)
        
    def enter(self):
        """Reset state and start menu music"""
        # Reset all animation values
        self.anim_state.update({'fade_alpha': 255, 'fade_direction': 1, 'transitioning': False,
                               'target': None, 'title_pulse': 0, 'text_appear': 0, 'lighting': 0})
        
        # Start background music
        if self.sound_manager.load_background_music("assets/background_music/main_menu.mp3"):
            self.sound_manager.play_background_music()
    
    def start_transition(self, target_state):
        """Initiate smooth fade transition to target state"""
        if not self.anim_state['transitioning']:
            self.anim_state.update({'transitioning': True, 'target': target_state, 'fade_direction': -1})
    
    def _update_lighting(self, dt):
        """Create realistic atmospheric lighting with subtle variations"""
        self.anim_state['lighting'] += dt
        
        # Natural light variation simulation (wind through trees effect)
        base_var = math.sin(self.anim_state['lighting'] * self.lighting['variation_speed']) * self.lighting['variation_amp']
        flicker = math.sin(self.anim_state['lighting'] * 3.2) * 0.02
        current_light = max(0.2, min(0.8, self.lighting['ambient'] + base_var + flicker))
        
        # Apply background dimming and atmospheric tinting
        self.surfaces['lighting'].fill((0, 0, 0, 0))
        self.surfaces['dim'].fill((0, 0, 0, int(255 * (1.0 - self.lighting['background_dim']))))
        
        # Add blue-purple night atmosphere
        if atmosphere_alpha := int((1.0 - current_light) * 120):
            atm_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            atm_surf.fill((10, 15, 40, atmosphere_alpha))
            self.surfaces['lighting'].blit(atm_surf, (0, 0))
    
    def update(self, dt):
        """Main update loop handling animations, particles, and input"""
        # Update animation timers
        for key in ['title_pulse', 'text_appear']:
            self.anim_state[key] += dt
            
        self._update_lighting(dt)
        
        # Update all particles efficiently
        for particle_list in self.particles.values():
            for particle in particle_list:
                particle.update(dt)
        
        # Handle fade transitions with easing
        if self.anim_state['transitioning']:
            fade_progress = 1.0 - (self.anim_state['fade_alpha'] / 255.0)
            self.anim_state['fade_alpha'] = 255 * (1.0 - fade_progress * fade_progress)  # Quadratic ease
            self.anim_state['fade_alpha'] -= self.anim_state['fade_speed'] * dt
            
            if self.anim_state['fade_alpha'] <= 0:
                return self.anim_state['target']
        else:
            if self.anim_state['fade_direction'] == 1:
                self.anim_state['fade_alpha'] -= self.anim_state['fade_speed'] * dt
                if self.anim_state['fade_alpha'] <= 0:
                    self.anim_state['fade_alpha'] = self.anim_state['fade_direction'] = 0
        
        # Handle input when ready
        if not self.anim_state['transitioning'] and self.anim_state['fade_alpha'] == 0:
            if pygame.key.get_pressed()[pygame.K_RETURN]:
                self.start_transition("gameplay")
        
        return None
    
    def render(self, screen):
        """Render complete menu scene with layered effects"""
        # Render background and apply dimming
        screen.blit(self.background_image, (0, 0))
        screen.blit(self.surfaces['dim'], (0, 0))
        
        # Render particles in proper order (leaves behind fireflies)
        for particle in self.particles['leaves'] + self.particles['fireflies']:
            particle.render(screen)
        
        # Apply atmospheric lighting
        screen.blit(self.surfaces['lighting'], (0, 0))
        
        # Render animated text elements
        self._render_animated_text(screen)
        
        # Apply fade overlay
        if self.anim_state['fade_alpha'] > 0:
            self.surfaces['fade'].set_alpha(int(self.anim_state['fade_alpha']))
            screen.blit(self.surfaces['fade'], (0, 0))
    
    def _render_animated_text(self, screen):
        """Render all text elements with smooth animations"""
        def ease_cubic(t): return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
        
        # Calculate animation progress for each text element
        title_progress = min(1.0, max(0.0, (self.anim_state['text_appear'] - 0.8) / 1.5))
        start_progress = min(1.0, max(0.0, (self.anim_state['text_appear'] - 1.0) / 1.2))
        controls_progress = min(1.0, max(0.0, (self.anim_state['text_appear'] - 1.5) / 1.0))
        
        # Render title with pulsing scale and smooth fade-in
        if title_alpha := int(255 * ease_cubic(title_progress)):
            title_scale = 1.0 + 0.05 * math.sin(self.anim_state['title_pulse'] * 1.5)
            title_font = pygame.font.Font(None, int(72 * title_scale))
            title_surface = title_font.render("ARENA OF SHADOWS", True, (255, 255, 255))
            title_surface.set_alpha(title_alpha)
            
            # Center title with subtle floating motion
            title_pos = (
                SCREEN_WIDTH // 2 - title_surface.get_width() // 2,
                160 + int(5 * math.sin(self.anim_state['title_pulse'] * 2))
            )
            screen.blit(title_surface, title_pos)
        
        # Render start prompt with breathing effect
        if start_alpha := int(255 * ease_cubic(start_progress)):
            start_surface = self.font.render("Press ENTER to Start", True, (180, 220, 180))
            if start_alpha >= 200:  # Apply breathing effect when fully visible
                breath_alpha = int(255 * (0.6 + 0.4 * math.sin(self.anim_state['title_pulse'] * 2)))
                start_surface.set_alpha(breath_alpha)
            else:
                start_surface.set_alpha(start_alpha)
            
            start_pos = (SCREEN_WIDTH // 2 - start_surface.get_width() // 2, 260)
            screen.blit(start_surface, start_pos)
        
        # Render controls text
        if controls_alpha := int(255 * ease_cubic(controls_progress)):
            controls_surface = self.font.render("WASD/Arrows: Move | SPACE: Attack", True, (120, 160, 120))
            controls_surface.set_alpha(controls_alpha)
            controls_pos = (SCREEN_WIDTH // 2 - controls_surface.get_width() // 2, 310)
            screen.blit(controls_surface, controls_pos)
