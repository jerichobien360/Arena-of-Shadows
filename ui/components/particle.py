import pygame
import math
import random
import numpy as np
from typing import Tuple, Optional, Callable, List
from enum import Enum
from functools import lru_cache
from numba import jit, njit
import array


class ParticleType(Enum):
    """Different types of particles for various effects"""
    BLOOD = 0
    SPARKS = 1
    EXPLOSION = 2
    MAGIC = 3
    SMOKE = 4
    DEBRIS = 5
    ENERGY = 6
    HEALING = 7
    SMOOTH_FADE = 8
    SMOOTH_SCALE = 9
    SMOOTH_FLOAT = 10


class EaseType(Enum):
    """Different easing functions for smooth animations"""
    LINEAR = 0
    EASE_IN = 1
    EASE_OUT = 2
    EASE_IN_OUT = 3
    BOUNCE = 4
    ELASTIC = 5
    BACK = 6
    SINE = 7
    EXPO = 8
    CIRC = 9


# Pre-computed constants for performance
PI = math.pi
TWO_PI = 2 * PI
HALF_PI = PI / 2

# Lookup tables for trigonometric functions
_SIN_LOOKUP = np.sin(np.linspace(0, TWO_PI, 1024))
_COS_LOOKUP = np.cos(np.linspace(0, TWO_PI, 1024))


@njit(cache=True)
def fast_sin(angle: float) -> float:
    """Fast sine using lookup table"""
    index = int((angle % TWO_PI) * 1024 / TWO_PI)
    return _SIN_LOOKUP[index]


@njit(cache=True)
def fast_cos(angle: float) -> float:
    """Fast cosine using lookup table"""
    index = int((angle % TWO_PI) * 1024 / TWO_PI)
    return _COS_LOOKUP[index]


@njit(cache=True)
def fast_hypot(x: float, y: float) -> float:
    """Fast hypotenuse calculation"""
    return math.sqrt(x * x + y * y)


class EasingFunctions:
    """Collection of easing functions optimized with caching"""
    
    # Pre-compute common easing values
    _EASE_CACHE = {}
    
    @staticmethod
    @lru_cache(maxsize=1024)
    def _cached_ease(t: float, ease_type: int) -> float:
        """Cached easing calculations for common values"""
        if ease_type == 0:  # LINEAR
            return t
        elif ease_type == 1:  # EASE_IN
            return t * t * t
        elif ease_type == 2:  # EASE_OUT
            return 1 - pow(1 - t, 3)
        elif ease_type == 3:  # EASE_IN_OUT
            return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
        elif ease_type == 4:  # BOUNCE
            n1, d1 = 7.5625, 2.75
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
        elif ease_type == 5:  # ELASTIC
            c4 = TWO_PI / 3
            return 0 if t == 0 else 1 if t == 1 else pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1
        elif ease_type == 6:  # BACK
            c1, c3 = 1.70158, 2.70158
            return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)
        elif ease_type == 7:  # SINE
            return math.sin(t * HALF_PI)
        elif ease_type == 8:  # EXPO
            return 1 if t == 1 else 1 - pow(2, -10 * t)
        elif ease_type == 9:  # CIRC
            return math.sqrt(1 - pow(t - 1, 2))
        return t
    
    @staticmethod
    def get_easing_function(ease_type: EaseType) -> Callable[[float], float]:
        """Get optimized easing function"""
        ease_int = ease_type.value
        return lambda t: EasingFunctions._cached_ease(t, ease_int)


class Particle:
    """Individual particle with realistic physics and smooth animations"""
    
    # Class-level constants for performance
    __slots__ = (
        'x', 'y', 'start_x', 'start_y', 'velocity_x', 'velocity_y', 'original_velocity',
        'color', 'original_color', 'size', 'original_size', 'alpha', 'original_alpha',
        'gravity', 'bounce', 'air_resistance', 'ground_friction',
        'lifetime', 'max_lifetime', 'age', 'fade', 'particle_type',
        'fade_ease', 'scale_ease', 'movement_ease', '_fade_func_id', '_scale_func_id', '_movement_func_id',
        'rotation', 'rotation_speed', 'pulse_frequency', 'trail_positions', 'max_trail_length',
        'target_size', 'size_animation_speed', 'target_alpha', 'alpha_animation_speed',
        'wave_offset', 'wave_amplitude', 'wave_frequency', 'on_ground', 'ground_y',
        'transparency_layers', 'max_transparency_layers', '_color_tuple', '_update_counter'
    )
    
    def __init__(self, x: float, y: float, velocity_x: float, velocity_y: float,
                 color: Tuple[int, int, int], size: float, lifetime: float,
                 particle_type: ParticleType = ParticleType.BLOOD,
                 gravity: float = 0.0, bounce: float = 0.0, fade: bool = True,
                 fade_ease: EaseType = EaseType.EASE_OUT,
                 scale_ease: EaseType = EaseType.LINEAR,
                 movement_ease: EaseType = EaseType.LINEAR):
        
        # Position and movement (using primitive types for speed)
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.original_velocity = fast_hypot(velocity_x, velocity_y)
        
        # Visual properties
        self.color = color
        self.original_color = color
        self._color_tuple = (*color, 255)  # Pre-computed RGBA tuple
        self.size = size
        self.original_size = size
        self.alpha = 255
        self.original_alpha = 255
        
        # Physics constants
        self.gravity = gravity
        self.bounce = bounce
        self.air_resistance = 0.98
        self.ground_friction = 0.85
        
        # Lifecycle
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.age = 0.0
        self.fade = fade
        self.particle_type = particle_type.value  # Store as int for performance
        
        # Pre-compute easing function IDs for faster lookup
        self.fade_ease = fade_ease
        self.scale_ease = scale_ease
        self.movement_ease = movement_ease
        self._fade_func_id = fade_ease.value
        self._scale_func_id = scale_ease.value
        self._movement_func_id = movement_ease.value
        
        # Special effects (optimized with random seed for reproducibility)
        rand_state = random.getstate()
        random.seed(hash((x, y, velocity_x, velocity_y)) % 2**32)
        self.rotation = random.uniform(0, TWO_PI)
        self.rotation_speed = random.uniform(-5, 5)
        self.pulse_frequency = random.uniform(2, 8)
        self.wave_offset = random.uniform(0, TWO_PI)
        self.wave_amplitude = random.uniform(5, 15)
        self.wave_frequency = random.uniform(0.5, 2.0)
        random.setstate(rand_state)
        
        # Use deque for better performance on trail positions
        self.trail_positions = []
        self.max_trail_length = 8
        
        # Animation properties
        self.target_size = size
        self.size_animation_speed = 5.0
        self.target_alpha = 255
        self.alpha_animation_speed = 3.0
        
        # Ground collision
        self.on_ground = False
        self.ground_y = None
        
        # Transparency layers (pre-allocated for performance)
        self.transparency_layers = [(0, (0, 0, 0), 0)] * 3
        self.max_transparency_layers = 3
        
        # Update counter for optimization
        self._update_counter = 0

    def update(self, dt: float, world_bounds: Optional[Tuple[float, float, float, float]] = None) -> bool:
        """Update particle physics with optimized calculations"""
        self.age += dt
        
        if self.age >= self.lifetime:
            return False
        
        # Calculate progress with cached division
        progress = min(1.0, self.age / self.lifetime) if self.lifetime > 0 else 1.0
        
        # Optimized trail handling - only update every few frames
        self._update_counter += 1
        if (self._update_counter & 1) == 0 and self.particle_type in {6, 3, 8}:  # ENERGY, MAGIC, SMOOTH_FADE
            if len(self.trail_positions) >= self.max_trail_length:
                self.trail_positions.pop(0)
            self.trail_positions.append((self.x, self.y, self.alpha))
        
        # Update rotation with fast trigonometry
        rotation_progress = EasingFunctions._cached_ease(progress, self._movement_func_id)
        self.rotation += self.rotation_speed * dt * (1.0 - rotation_progress * 0.5)
        
        # Apply gravity with easing
        if self.gravity > 0:
            gravity_multiplier = 1.0 + progress * 0.5
            self.velocity_y += self.gravity * dt * gravity_multiplier
        
        # Apply air resistance
        resistance = self.air_resistance + (progress * 0.01)
        self.velocity_x *= resistance
        self.velocity_y *= resistance
        
        # Smooth floating motion for specific particle types
        if self.particle_type == 10:  # SMOOTH_FLOAT
            wave_y = self.wave_amplitude * fast_sin(self.age * self.wave_frequency + self.wave_offset)
            self.velocity_y += wave_y * dt * 10
        
        # Update position
        movement_multiplier = EasingFunctions._cached_ease(1.0 - progress, self._movement_func_id)
        self.x += self.velocity_x * dt * movement_multiplier
        self.y += self.velocity_y * dt * movement_multiplier
        
        # Optimized collision detection
        if world_bounds and self.bounce > 0:
            self._handle_collisions(world_bounds)
        
        # Update visual properties
        self._update_smooth_visuals(progress)
        
        return True

    def _handle_collisions(self, bounds: Tuple[float, float, float, float]) -> None:
        """Optimized collision handling"""
        left, top, right, bottom = bounds
        
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
        
        # Side and top collisions
        if self.x - self.size <= left:
            self.x = left + self.size
            self.velocity_x = -self.velocity_x * self.bounce
        elif self.x + self.size >= right:
            self.x = right - self.size
            self.velocity_x = -self.velocity_x * self.bounce
        
        if self.y - self.size <= top:
            self.y = top + self.size
            self.velocity_y = -self.velocity_y * self.bounce

    def _update_smooth_visuals(self, progress: float) -> None:
        """Optimized visual property updates"""
        if not self.fade:
            return
        
        # Pre-compute easing values
        fade_progress = EasingFunctions._cached_ease(progress, self._fade_func_id)
        scale_progress = EasingFunctions._cached_ease(progress, self._scale_func_id)
        
        # Update alpha based on particle type
        if self.particle_type == 8:  # SMOOTH_FADE
            if progress < 0.1:
                self.alpha = int(255 * fade_progress * 10)
            elif progress < 0.8:
                self.alpha = 255
            else:
                fade_out = EasingFunctions._cached_ease((progress - 0.8) * 5, self._fade_func_id)
                self.alpha = int(255 * (1.0 - fade_out))
        else:
            self.alpha = int(255 * (1.0 - fade_progress))
        
        # Update size based on particle type
        particle_type = self.particle_type
        if particle_type == 2:  # EXPLOSION
            if progress < 0.3:
                self.size = self.original_size * (1.0 + scale_progress * 10 / 3)
            else:
                shrink = EasingFunctions._cached_ease((progress - 0.3) / 0.7, self._scale_func_id)
                self.size = self.original_size * (3.0 - shrink * 2.5)
        elif particle_type == 4:  # SMOKE
            self.size = self.original_size * (1.0 + scale_progress * 1.8)
        elif particle_type == 9:  # SMOOTH_SCALE
            pulse = 0.9 + 0.2 * fast_sin(self.age * 4)
            self.size = self.original_size * (1.2 - scale_progress * 0.4) * pulse
        elif particle_type in {0, 5}:  # BLOOD, DEBRIS
            self.size = self.original_size * (1.0 - scale_progress * 0.4)
        elif particle_type == 3:  # MAGIC
            pulse = EasingFunctions._cached_ease(fast_sin(self.age * self.pulse_frequency) * 0.5 + 0.5, self._scale_func_id)
            self.size = self.original_size * (0.8 + pulse * 0.6)
        
        # Update transparency layers efficiently
        self._update_transparency_layers()

    def _update_transparency_layers(self) -> None:
        """Efficiently update transparency layers"""
        layer_alpha = max(1, self.alpha // self.max_transparency_layers)
        
        for i in range(self.max_transparency_layers):
            layer_offset = i * 2
            layer_size = max(1, self.size - layer_offset)
            # Pre-compute color adjustments
            r = min(255, max(0, self.color[0] + i * 10))
            g = min(255, max(0, self.color[1] + i * 5))
            b = min(255, max(0, self.color[2] + i * 5))
            self.transparency_layers[i] = (layer_size, (r, g, b), layer_alpha)

    def render(self, screen: pygame.Surface, camera=None) -> None:
        """Optimized rendering with early exits"""
        if self.alpha <= 0 or self.size <= 0:
            return
        
        # Screen coordinate conversion
        if camera:
            screen_x, screen_y = camera.world_to_screen(self.x, self.y)
            zoom = camera.zoom
        else:
            screen_x, screen_y = self.x, self.y
            zoom = 1.0
        
        # Early culling check
        screen_w, screen_h = screen.get_size()
        if (screen_x < -50 or screen_x > screen_w + 50 or
            screen_y < -50 or screen_y > screen_h + 50):
            return
        
        size = max(1, int(self.size * zoom))
        
        try:
            # Render trail for specific particle types
            if (self.particle_type in {6, 3, 8} and  # ENERGY, MAGIC, SMOOTH_FADE
                len(self.trail_positions) > 1):
                self._render_smooth_trail(screen, camera, zoom)
            
            # Choose rendering method based on particle type
            if self.particle_type in {8, 9, 3}:  # SMOOTH_FADE, SMOOTH_SCALE, MAGIC
                self._render_layered_particle(screen, screen_x, screen_y, size)
            else:
                self._render_standard_particle(screen, screen_x, screen_y, size)
        
        except (pygame.error, ValueError, OverflowError):
            pass

    def _render_smooth_trail(self, screen: pygame.Surface, camera, zoom: float) -> None:
        """Optimized trail rendering"""
        trail_len = len(self.trail_positions)
        if trail_len < 2:
            return
        
        # Pre-allocate surface for better performance
        max_size = int(self.original_size * zoom * 2)
        if max_size <= 0:
            return
        
        for i, (trail_x, trail_y, trail_alpha) in enumerate(self.trail_positions):
            if camera:
                screen_trail_x, screen_trail_y = camera.world_to_screen(trail_x, trail_y)
            else:
                screen_trail_x, screen_trail_y = trail_x, trail_y
            
            # Optimized alpha and size calculations
            alpha_progress = (i + 1) / trail_len
            eased_alpha = EasingFunctions._cached_ease(alpha_progress, 2)  # EASE_OUT
            final_alpha = int(trail_alpha * eased_alpha * 0.6)
            
            if final_alpha <= 5:
                continue
            
            size_progress = EasingFunctions._cached_ease(alpha_progress, 1)  # EASE_IN
            trail_size = max(1, int(self.original_size * zoom * size_progress))
            
            # Direct circle drawing for performance
            if trail_size > 0:
                pygame.draw.circle(screen, (*self.color, final_alpha), 
                                 (int(screen_trail_x), int(screen_trail_y)), trail_size)

    def _render_layered_particle(self, screen: pygame.Surface, x: float, y: float, size: int) -> None:
        """Optimized layered particle rendering"""
        if size <= 0:
            return
        
        # Direct rendering without intermediate surface for better performance
        center_x, center_y = int(x), int(y)
        
        # Render from largest to smallest layer
        for layer_size, layer_color, layer_alpha in reversed(self.transparency_layers):
            if layer_alpha <= 0 or layer_size <= 0:
                continue
            
            layer_size_scaled = max(1, int(layer_size * (size / max(1, self.size))))
            
            if self.particle_type == 3:  # MAGIC
                # Magical glow effect - draw outer glow first
                glow_alpha = max(1, layer_alpha // 3)
                glow_size = layer_size_scaled + 2
                pygame.draw.circle(screen, (*layer_color, glow_alpha), 
                                 (center_x, center_y), glow_size)
            
            # Main particle layer
            pygame.draw.circle(screen, (*layer_color, layer_alpha), 
                             (center_x, center_y), layer_size_scaled)
        
        # Special effects for SMOOTH_SCALE
        if self.particle_type == 9 and self.alpha > 50:  # SMOOTH_SCALE
            sparkle_alpha = int(self.alpha * 0.8)
            for _ in range(min(3, size // 2)):  # Limit sparkles based on size
                sparkle_x = center_x + random.randint(-size//2, size//2)
                sparkle_y = center_y + random.randint(-size//2, size//2)
                sparkle_size = max(1, size // 4)
                pygame.draw.circle(screen, (255, 255, 255, sparkle_alpha), 
                                 (sparkle_x, sparkle_y), sparkle_size)

    def _render_standard_particle(self, screen: pygame.Surface, x: float, y: float, size: int) -> None:
        """Optimized standard particle rendering"""
        center_x, center_y = int(x), int(y)
        
        if self.alpha < 255:
            # Special rendering for specific particle types
            if self.particle_type == 1:  # SPARKS
                self._render_spark_direct(screen, center_x, center_y, size)
            elif self.particle_type == 6:  # ENERGY
                self._render_energy_direct(screen, center_x, center_y, size)
            elif self.particle_type == 2:  # EXPLOSION
                self._render_explosion_direct(screen, center_x, center_y, size)
            else:
                # Optimized multi-layer circle
                for layer in range(min(3, size)):
                    layer_alpha = max(1, self.alpha // (layer + 1))
                    layer_size = max(1, size - layer)
                    if layer_alpha > 5:
                        pygame.draw.circle(screen, (*self.color, layer_alpha), 
                                         (center_x, center_y), layer_size)
        else:
            pygame.draw.circle(screen, self.color, (center_x, center_y), size)

    def _render_spark_direct(self, screen: pygame.Surface, x: int, y: int, size: int) -> None:
        """Direct spark rendering for performance"""
        length = size * 2
        end_x = int(x + length * fast_cos(self.rotation))
        end_y = int(y + length * fast_sin(self.rotation))
        
        # Glow effect
        glow_alpha = max(5, int(self.alpha * 0.3))
        if glow_alpha > 5:
            pygame.draw.line(screen, (*self.color, glow_alpha),
                           (x, y), (end_x, end_y), max(2, size // 2))
        
        # Main spark
        pygame.draw.line(screen, (*self.color, self.alpha),
                        (x, y), (end_x, end_y), max(1, size // 3))

    def _render_energy_direct(self, screen: pygame.Surface, x: int, y: int, size: int) -> None:
        """Direct energy rendering for performance"""
        # Main particle with glow
        glow_alpha = max(5, int(self.alpha * 0.4))
        pygame.draw.circle(screen, (*self.color, glow_alpha), (x, y), size + 2)
        pygame.draw.circle(screen, (*self.color, self.alpha), (x, y), size)
        
        # Optimized electric arcs
        arc_count = min(4, max(2, size // 2))  # Limit arc count
        for i in range(arc_count):
            angle = (i * TWO_PI / arc_count) + self.rotation
            arc_length = size * 1.2
            end_x = int(x + arc_length * fast_cos(angle))
            end_y = int(y + arc_length * fast_sin(angle))
            
            arc_alpha = max(5, int(self.alpha * 0.6))
            if arc_alpha > 5:
                pygame.draw.line(screen, (*self.color, arc_alpha), (x, y), (end_x, end_y), 1)

    def _render_explosion_direct(self, screen: pygame.Surface, x: int, y: int, size: int) -> None:
        """Direct explosion rendering for performance"""
        # Main explosion with glow
        glow_alpha = max(5, int(self.alpha * 0.3))
        pygame.draw.circle(screen, (*self.color, glow_alpha), (x, y), size + 3)
        pygame.draw.circle(screen, (*self.color, self.alpha), (x, y), size)
        
        # Optimized fragment lines
        fragment_count = min(8, size)  # Limit fragments based on size
        fragment_length = size * 1.2
        for i in range(fragment_count):
            angle = (i * PI / 4) + self.rotation
            end_x = int(x + fragment_length * fast_cos(angle))
            end_y = int(y + fragment_length * fast_sin(angle))
            
            fragment_alpha = max(5, int(self.alpha * 0.7))
            if fragment_alpha > 5:
                pygame.draw.line(screen, (*self.color, fragment_alpha),
                               (x, y), (end_x, end_y), max(1, size // 4))
