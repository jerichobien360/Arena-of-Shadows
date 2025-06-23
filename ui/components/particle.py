import pygame
import math
import random
from typing import Tuple, Optional, Callable
from enum import Enum


class ParticleType(Enum):
    """Different types of particles for various effects"""
    BLOOD = "blood"
    SPARKS = "sparks"
    EXPLOSION = "explosion"
    MAGIC = "magic"
    SMOKE = "smoke"
    DEBRIS = "debris"
    ENERGY = "energy"
    HEALING = "healing"
    SMOOTH_FADE = "smooth_fade"
    SMOOTH_SCALE = "smooth_scale"
    SMOOTH_FLOAT = "smooth_float"

class EaseType(Enum):
    """Different easing functions for smooth animations"""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    BOUNCE = "bounce"
    ELASTIC = "elastic"
    BACK = "back"
    SINE = "sine"
    EXPO = "expo"
    CIRC = "circ"

class EasingFunctions:
    """Collection of easing functions for smooth animations"""
    
    @staticmethod
    def linear(t: float) -> float:
        return t
    
    @staticmethod
    def ease_in_quad(t: float) -> float:
        return t * t
    
    @staticmethod
    def ease_out_quad(t: float) -> float:
        return 1 - (1 - t) * (1 - t)
    
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2
    
    @staticmethod
    def ease_in_cubic(t: float) -> float:
        return t * t * t
    
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        return 1 - pow(1 - t, 3)
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
    
    @staticmethod
    def ease_out_bounce(t: float) -> float:
        n1 = 7.5625
        d1 = 2.75
        
        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t -= 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t -= 2.625 / d1
            return n1 * t * t + 0.984375
    
    @staticmethod
    def ease_out_elastic(t: float) -> float:
        c4 = (2 * math.pi) / 3
        return 0 if t == 0 else 1 if t == 1 else pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1
    
    @staticmethod
    def ease_out_back(t: float) -> float:
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)
    
    @staticmethod
    def ease_out_sine(t: float) -> float:
        return math.sin(t * math.pi / 2)
    
    @staticmethod
    def ease_out_expo(t: float) -> float:
        return 1 if t == 1 else 1 - pow(2, -10 * t)
    
    @staticmethod
    def ease_out_circ(t: float) -> float:
        return math.sqrt(1 - pow(t - 1, 2))
    
    @staticmethod
    def get_easing_function(ease_type: EaseType) -> Callable[[float], float]:
        """Get easing function by type"""
        mapping = {
            EaseType.LINEAR: EasingFunctions.linear,
            EaseType.EASE_IN: EasingFunctions.ease_in_cubic,
            EaseType.EASE_OUT: EasingFunctions.ease_out_cubic,
            EaseType.EASE_IN_OUT: EasingFunctions.ease_in_out_cubic,
            EaseType.BOUNCE: EasingFunctions.ease_out_bounce,
            EaseType.ELASTIC: EasingFunctions.ease_out_elastic,
            EaseType.BACK: EasingFunctions.ease_out_back,
            EaseType.SINE: EasingFunctions.ease_out_sine,
            EaseType.EXPO: EasingFunctions.ease_out_expo,
            EaseType.CIRC: EasingFunctions.ease_out_circ,
        }
        return mapping.get(ease_type, EasingFunctions.linear)

class Particle:
    """Individual particle with realistic physics and smooth animations"""
    
    def __init__(self, x: float, y: float, velocity_x: float, velocity_y: float,
                 color: Tuple[int, int, int], size: float, lifetime: float,
                 particle_type: ParticleType = ParticleType.BLOOD,
                 gravity: float = 0.0, bounce: float = 0.0, fade: bool = True,
                 fade_ease: EaseType = EaseType.EASE_OUT,
                 scale_ease: EaseType = EaseType.LINEAR,
                 movement_ease: EaseType = EaseType.LINEAR):
        # Position and movement
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.original_velocity = math.hypot(velocity_x, velocity_y)
        
        # Visual properties
        self.color = color
        self.original_color = color
        self.size = size
        self.original_size = size
        self.alpha = 255
        self.original_alpha = 255
        
        # Physics
        self.gravity = gravity
        self.bounce = bounce
        self.air_resistance = 0.98
        self.ground_friction = 0.85
        
        # Lifecycle
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.age = 0.0
        self.fade = fade
        self.particle_type = particle_type
        
        # Easing properties
        self.fade_ease = fade_ease
        self.scale_ease = scale_ease
        self.movement_ease = movement_ease
        self.fade_function = EasingFunctions.get_easing_function(fade_ease)
        self.scale_function = EasingFunctions.get_easing_function(scale_ease)
        self.movement_function = EasingFunctions.get_easing_function(movement_ease)
        
        # Special effects
        self.rotation = random.uniform(0, 2 * math.pi)
        self.rotation_speed = random.uniform(-5, 5)
        self.pulse_frequency = random.uniform(2, 8)
        self.trail_positions = []
        self.max_trail_length = 8
        
        # Smooth animation properties
        self.target_size = size
        self.size_animation_speed = 5.0
        self.target_alpha = 255
        self.alpha_animation_speed = 3.0
        self.wave_offset = random.uniform(0, 2 * math.pi)
        self.wave_amplitude = random.uniform(5, 15)
        self.wave_frequency = random.uniform(0.5, 2.0)
        
        # Ground collision
        self.on_ground = False
        self.ground_y = None
        
        # Transparency layers for smooth blending
        self.transparency_layers = []
        self.max_transparency_layers = 3

    def update(self, dt: float, world_bounds: Optional[Tuple[float, float, float, float]] = None) -> bool:
        """Update particle physics with smooth animations"""
        self.age += dt
        
        if self.age >= self.lifetime:
            return False
        
        # Calculate progress (0.0 to 1.0)
        progress = min(1.0, self.age / self.lifetime)
        
        # Store trail position for certain particle types
        if self.particle_type in [ParticleType.ENERGY, ParticleType.MAGIC, ParticleType.SMOOTH_FADE]:
            self.trail_positions.append((self.x, self.y, self.alpha))
            if len(self.trail_positions) > self.max_trail_length:
                self.trail_positions.pop(0)
        
        # Update rotation with smooth easing
        rotation_progress = self.movement_function(progress)
        self.rotation += self.rotation_speed * dt * (1.0 - rotation_progress * 0.5)
        
        # Apply gravity with easing
        if self.gravity > 0:
            gravity_multiplier = 1.0 + progress * 0.5  # Gravity increases over time
            self.velocity_y += self.gravity * dt * gravity_multiplier
        
        # Apply air resistance with smooth transition
        resistance = self.air_resistance + (progress * 0.01)  # Slightly more resistance over time
        self.velocity_x *= resistance
        self.velocity_y *= resistance
        
        # Smooth floating motion for certain particle types
        if self.particle_type == ParticleType.SMOOTH_FLOAT:
            wave_y = self.wave_amplitude * math.sin(self.age * self.wave_frequency + self.wave_offset)
            self.velocity_y += wave_y * dt * 10
        
        # Update position with movement easing
        movement_multiplier = self.movement_function(1.0 - progress)
        self.x += self.velocity_x * dt * movement_multiplier
        self.y += self.velocity_y * dt * movement_multiplier
        
        # Handle ground collision
        if world_bounds and self.bounce > 0:
            left, top, right, bottom = world_bounds
            
            # Bottom collision (ground)
            if self.y + self.size >= bottom:
                if not self.on_ground:
                    self.y = bottom - self.size
                    self.velocity_y = -self.velocity_y * self.bounce
                    self.velocity_x *= self.ground_friction
                    if abs(self.velocity_y) < 20:
                        self.on_ground = True
                        self.velocity_y = 0
                        self.ground_y = self.y
            
            # Side collisions
            if self.x - self.size <= left:
                self.x = left + self.size
                self.velocity_x = -self.velocity_x * self.bounce
            elif self.x + self.size >= right:
                self.x = right - self.size
                self.velocity_x = -self.velocity_x * self.bounce
            
            # Top collision
            if self.y - self.size <= top:
                self.y = top + self.size
                self.velocity_y = -self.velocity_y * self.bounce
        
        # Update visual properties with smooth easing
        self._update_smooth_visuals(progress)
        
        return True

    def _update_smooth_visuals(self, progress: float) -> None:
        """Update visual properties with smooth easing functions"""
        if self.fade:
            # Smooth alpha transition
            if self.particle_type == ParticleType.SMOOTH_FADE:
                # Custom fade with multiple phases
                if progress < 0.1:
                    # Fade in quickly
                    fade_progress = self.fade_function(progress / 0.1)
                    self.alpha = int(255 * fade_progress)
                elif progress < 0.8:
                    # Stay fully visible
                    self.alpha = 255
                else:
                    # Smooth fade out
                    fade_out_progress = (progress - 0.8) / 0.2
                    eased_progress = self.fade_function(fade_out_progress)
                    self.alpha = int(255 * (1.0 - eased_progress))
            else:
                # Standard smooth fade
                eased_progress = self.fade_function(progress)
                self.alpha = int(255 * (1.0 - eased_progress))
            
            # Smooth size transitions based on particle type
            if self.particle_type == ParticleType.EXPLOSION:
                # Smooth explosion growth and shrink
                if progress < 0.3:
                    scale_progress = self.scale_function(progress / 0.3)
                    self.size = self.original_size * (1.0 + scale_progress * 2)
                else:
                    shrink_progress = (progress - 0.3) / 0.7
                    eased_shrink = self.scale_function(shrink_progress)
                    self.size = self.original_size * (3.0 - eased_shrink * 2.5)
            elif self.particle_type == ParticleType.SMOKE:
                # Smooth smoke expansion
                scale_progress = self.scale_function(progress)
                self.size = self.original_size * (1.0 + scale_progress * 1.8)
            elif self.particle_type == ParticleType.SMOOTH_SCALE:
                # Custom smooth scaling
                scale_progress = self.scale_function(progress)
                pulse = 0.9 + 0.2 * math.sin(self.age * 4)  # Gentle pulsing
                self.size = self.original_size * (1.2 - scale_progress * 0.4) * pulse
            elif self.particle_type in [ParticleType.BLOOD, ParticleType.DEBRIS]:
                # Smooth shrinking
                scale_progress = self.scale_function(progress)
                self.size = self.original_size * (1.0 - scale_progress * 0.4)
            elif self.particle_type == ParticleType.MAGIC:
                # Magical pulsing with smooth easing
                pulse_progress = self.scale_function(math.sin(self.age * self.pulse_frequency) * 0.5 + 0.5)
                self.size = self.original_size * (0.8 + pulse_progress * 0.6)
        
        # Update transparency layers for ultra-smooth blending
        self._update_transparency_layers()

    def _update_transparency_layers(self) -> None:
        """Create multiple transparency layers for ultra-smooth effects"""
        layer_alpha = self.alpha // self.max_transparency_layers
        self.transparency_layers = []
        
        for i in range(self.max_transparency_layers):
            layer_offset = i * 2
            layer_size = max(1, self.size - layer_offset)
            layer_color = (
                max(0, min(255, self.color[0] + i * 10)),
                max(0, min(255, self.color[1] + i * 5)),
                max(0, min(255, self.color[2] + i * 5))
            )
            self.transparency_layers.append((layer_size, layer_color, layer_alpha))

    def render(self, screen: pygame.Surface, camera=None) -> None:
        """Render particle with smooth transparency effects"""
        if self.alpha <= 0 or self.size <= 0:
            return
        
        # Convert world coordinates to screen coordinates
        if camera:
            screen_x, screen_y = camera.world_to_screen(self.x, self.y)
            zoom = camera.zoom
        else:
            screen_x, screen_y = self.x, self.y
            zoom = 1.0
        
        # Check if particle is on screen
        if (screen_x < -50 or screen_x > screen.get_width() + 50 or
            screen_y < -50 or screen_y > screen.get_height() + 50):
            return
        
        size = max(1, int(self.size * zoom))
        
        try:
            # Render smooth trail
            if self.particle_type in [ParticleType.ENERGY, ParticleType.MAGIC, ParticleType.SMOOTH_FADE] and len(self.trail_positions) > 1:
                self._render_smooth_trail(screen, camera, zoom)
            
            # Render multiple transparency layers for ultra-smooth effect
            if self.particle_type in [ParticleType.SMOOTH_FADE, ParticleType.SMOOTH_SCALE, ParticleType.MAGIC]:
                self._render_layered_particle(screen, screen_x, screen_y, size)
            else:
                # Standard rendering with smooth alpha
                self._render_standard_particle(screen, screen_x, screen_y, size)
        
        except (pygame.error, ValueError, OverflowError):
            pass

    def _render_smooth_trail(self, screen: pygame.Surface, camera, zoom: float) -> None:
        """Render smooth particle trail with alpha blending"""
        if len(self.trail_positions) < 2:
            return
        
        for i, (trail_x, trail_y, trail_alpha) in enumerate(self.trail_positions):
            if camera:
                screen_trail_x, screen_trail_y = camera.world_to_screen(trail_x, trail_y)
            else:
                screen_trail_x, screen_trail_y = trail_x, trail_y
            
            # Smooth alpha progression along trail
            alpha_progress = (i + 1) / len(self.trail_positions)
            eased_alpha = EasingFunctions.ease_out_cubic(alpha_progress)
            final_alpha = int(trail_alpha * eased_alpha * 0.6)
            
            # Smooth size progression
            size_progress = EasingFunctions.ease_out_quad(alpha_progress)
            trail_size = max(1, int(self.original_size * zoom * size_progress))
            
            if final_alpha > 5 and trail_size > 0:
                trail_surface = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
                
                # Create gradient effect on trail
                for layer in range(3):
                    layer_alpha = final_alpha // (layer + 1)
                    layer_size = max(1, trail_size - layer)
                    if layer_alpha > 0:
                        pygame.draw.circle(trail_surface, (*self.color, layer_alpha), 
                                         (trail_size, trail_size), layer_size)
                
                screen.blit(trail_surface, (screen_trail_x - trail_size, screen_trail_y - trail_size))

    def _render_layered_particle(self, screen: pygame.Surface, x: float, y: float, size: int) -> None:
        """Render particle with multiple transparency layers for ultra-smooth effect"""
        # Create surface for layered rendering
        particle_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
        center = size * 1.5
        
        # Render from largest to smallest layer
        for layer_size, layer_color, layer_alpha in reversed(self.transparency_layers):
            if layer_alpha > 0 and layer_size > 0:
                layer_size_scaled = max(1, int(layer_size * (size / max(1, self.size))))
                
                if self.particle_type == ParticleType.MAGIC:
                    # Magical glow effect
                    glow_surface = pygame.Surface((layer_size_scaled * 3, layer_size_scaled * 3), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surface, (*layer_color, layer_alpha // 3), 
                                     (layer_size_scaled * 1.5, layer_size_scaled * 1.5), layer_size_scaled * 1.5)
                    particle_surface.blit(glow_surface, (center - layer_size_scaled * 1.5, center - layer_size_scaled * 1.5))
                
                # Main particle layer
                pygame.draw.circle(particle_surface, (*layer_color, layer_alpha), 
                                 (int(center), int(center)), layer_size_scaled)
        
        # Special effects for specific particle types
        if self.particle_type == ParticleType.SMOOTH_SCALE:
            # Add sparkle effect
            sparkle_alpha = int(self.alpha * 0.8)
            if sparkle_alpha > 0:
                for _ in range(3):
                    sparkle_x = center + random.uniform(-size//2, size//2)
                    sparkle_y = center + random.uniform(-size//2, size//2)
                    sparkle_size = random.randint(1, max(1, size//4))
                    pygame.draw.circle(particle_surface, (255, 255, 255, sparkle_alpha), 
                                     (int(sparkle_x), int(sparkle_y)), sparkle_size)
        
        screen.blit(particle_surface, (x - center, y - center))

    def _render_standard_particle(self, screen: pygame.Surface, x: float, y: float, size: int) -> None:
        """Render standard particle with smooth alpha"""
        if self.alpha < 255:
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            
            if self.particle_type == ParticleType.SPARKS:
                self._render_spark(particle_surface, size)
            elif self.particle_type == ParticleType.ENERGY:
                self._render_energy(particle_surface, size, (*self.color, self.alpha))
            elif self.particle_type == ParticleType.EXPLOSION:
                self._render_explosion(particle_surface, size, (*self.color, self.alpha))
            else:
                # Smooth circular particle with gradient
                for layer in range(3):
                    layer_alpha = self.alpha // (layer + 1)
                    layer_size = max(1, size - layer)
                    if layer_alpha > 0:
                        pygame.draw.circle(particle_surface, (*self.color, layer_alpha), 
                                         (size, size), layer_size)
            
            screen.blit(particle_surface, (x - size, y - size))
        else:
            pygame.draw.circle(screen, self.color, (int(x), int(y)), size)

    def _render_spark(self, surface: pygame.Surface, size: int) -> None:
        """Render spark particle as a smooth line with glow"""
        length = size * 2
        end_x = length * math.cos(self.rotation)
        end_y = length * math.sin(self.rotation)
        
        # Glow effect
        glow_alpha = int(self.alpha * 0.3)
        if glow_alpha > 0:
            pygame.draw.line(surface, (*self.color, glow_alpha),
                           (size, size), (size + end_x, size + end_y), max(2, size // 2))
        
        # Main spark
        pygame.draw.line(surface, (*self.color, self.alpha),
                        (size, size), (size + end_x, size + end_y), max(1, size // 3))

    def _render_energy(self, surface: pygame.Surface, size: int, color_with_alpha: Tuple[int, int, int, int]) -> None:
        """Render energy particle with smooth electric effect"""
        # Main particle with glow
        glow_alpha = min(255, int(color_with_alpha[3] * 0.4))
        pygame.draw.circle(surface, (*self.color, glow_alpha), (size, size), size + 2)
        pygame.draw.circle(surface, color_with_alpha, (size, size), size)
        
        # Smooth electric arcs
        arc_count = max(2, size // 2)
        for i in range(arc_count):
            angle = (i * 2 * math.pi / arc_count) + self.rotation
            arc_length = random.uniform(size * 0.8, size * 1.5)
            end_x = size + arc_length * math.cos(angle)
            end_y = size + arc_length * math.sin(angle)
            
            arc_alpha = min(255, int(color_with_alpha[3] * 0.6))
            if arc_alpha > 0:
                pygame.draw.line(surface, (*self.color, arc_alpha),
                               (size, size), (int(end_x), int(end_y)), 1)

    def _render_explosion(self, surface: pygame.Surface, size: int, color_with_alpha: Tuple[int, int, int, int]) -> None:
        """Render explosion particle with smooth fragments"""
        # Main explosion with glow
        glow_alpha = min(255, int(color_with_alpha[3] * 0.3))
        pygame.draw.circle(surface, (*self.color, glow_alpha), (size, size), size + 3)
        pygame.draw.circle(surface, color_with_alpha, (size, size), size)
        
        # Smooth fragment lines
        fragment_count = 8
        for i in range(fragment_count):
            angle = (i * math.pi / 4) + self.rotation
            fragment_length = size * 1.2
            end_x = size + fragment_length * math.cos(angle)
            end_y = size + fragment_length * math.sin(angle)
            
            fragment_alpha = min(255, int(color_with_alpha[3] * 0.7))
            if fragment_alpha > 0:
                pygame.draw.line(surface, (*self.color, fragment_alpha),
                               (size, size), (int(end_x), int(end_y)), max(1, size // 4))
