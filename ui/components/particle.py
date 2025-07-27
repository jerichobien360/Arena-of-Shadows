import pygame
import math
import random
import numpy as np
from typing import Tuple, Optional, Callable, List
from enum import Enum
from functools import lru_cache
from settings import *


# TODO: Simplify the code and follow on the DRY and KISS Principle

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

# Simplified lookup tables - much smaller for faster access
_LOOKUP_SIZE = 256
_ANGLE_STEP = TWO_PI / _LOOKUP_SIZE
_SIN_LOOKUP = [math.sin(i * _ANGLE_STEP) for i in range(_LOOKUP_SIZE)]
_COS_LOOKUP = [math.cos(i * _ANGLE_STEP) for i in range(_LOOKUP_SIZE)]


def fast_sin(angle: float) -> float:
    """Fast sine using lookup table - no numba compilation"""
    index = int((angle % TWO_PI) / _ANGLE_STEP) & (_LOOKUP_SIZE - 1)
    return _SIN_LOOKUP[index]


def fast_cos(angle: float) -> float:
    """Fast cosine using lookup table - no numba compilation"""
    index = int((angle % TWO_PI) / _ANGLE_STEP) & (_LOOKUP_SIZE - 1)
    return _COS_LOOKUP[index]


def fast_hypot(x: float, y: float) -> float:
    """Fast hypotenuse calculation - no numba compilation"""
    return math.sqrt(x * x + y * y)


class EasingFunctions:
    """Collection of easing functions optimized with caching"""
    
    @staticmethod
    @lru_cache(maxsize=512)  # Reduced cache size
    def _cached_ease(t: float, ease_type: int) -> float:
        """Cached easing calculations - simplified"""
        t = max(0.0, min(1.0, t))  # Clamp input
        
        if ease_type == 0:  # LINEAR
            return t
        elif ease_type == 1:  # EASE_IN
            return t * t * t
        elif ease_type == 2:  # EASE_OUT
            return 1 - (1 - t) ** 3
        elif ease_type == 3:  # EASE_IN_OUT
            return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2
        elif ease_type == 7:  # SINE - most commonly used
            return math.sin(t * HALF_PI)
        else:  # Simplified fallback for other types
            return t * t if ease_type in (4, 5, 6) else 1 - (1 - t) ** 2
    
    @staticmethod
    def get_easing_function(ease_type: EaseType) -> Callable[[float], float]:
        """Get optimized easing function"""
        ease_int = ease_type.value
        return lambda t: EasingFunctions._cached_ease(t, ease_int)


class Particle:
    """Individual particle with realistic physics and smooth animations"""
    
    __slots__ = (
        'x', 'y', 'velocity_x', 'velocity_y', 'color', 'size', 'alpha',
        'gravity', 'bounce', 'lifetime', 'age', 'fade', 'particle_type',
        'fade_ease', 'scale_ease', 'rotation', 'rotation_speed',
        'original_size', 'original_alpha', 'on_ground', '_update_skip'
    )
    
    def __init__(self, x: float, y: float, velocity_x: float, velocity_y: float,
                 color: Tuple[int, int, int], size: float, lifetime: float,
                 particle_type: ParticleType = ParticleType.BLOOD,
                 gravity: float = 0.0, bounce: float = 0.0, fade: bool = True,
                 fade_ease: EaseType = EaseType.EASE_OUT,
                 scale_ease: EaseType = EaseType.LINEAR,
                 movement_ease: EaseType = EaseType.LINEAR):
        
        # Core properties
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.color = color
        self.size = size
        self.alpha = 255
        
        # Physics
        self.gravity = gravity
        self.bounce = bounce
        self.on_ground = False
        
        # Lifecycle
        self.lifetime = lifetime
        self.age = 0.0
        self.fade = fade
        self.particle_type = particle_type.value
        
        # Animation
        self.fade_ease = fade_ease.value
        self.scale_ease = scale_ease.value
        self.original_size = size
        self.original_alpha = 255
        
        # Rotation (simplified)
        self.rotation = random.uniform(0, TWO_PI)
        self.rotation_speed = random.uniform(-3, 3)
        
        # Performance optimization - skip updates occasionally
        self._update_skip = 0

    def update(self, dt: float, world_bounds: Optional[Tuple[float, float, float, float]] = None) -> bool:
        """Optimized update with reduced calculations"""
        self.age += dt
        if self.age >= self.lifetime:
            return False
        
        # Skip some updates for distant/small particles
        self._update_skip = (self._update_skip + 1) % 3
        if self._update_skip != 0 and self.size < 3:
            return True
        
        progress = self.age / self.lifetime
        
        # Simplified physics
        if self.gravity > 0:
            self.velocity_y += self.gravity * dt
        
        # Simple air resistance
        resistance = 0.98
        self.velocity_x *= resistance
        self.velocity_y *= resistance
        
        # Position update
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Simple collision handling
        if world_bounds and self.bounce > 0:
            left, top, right, bottom = world_bounds
            if self.y >= bottom - self.size:
                self.y = bottom - self.size
                self.velocity_y *= -self.bounce
                self.velocity_x *= 0.8
                self.on_ground = True
            
            if self.x <= left + self.size or self.x >= right - self.size:
                self.velocity_x *= -self.bounce
        
        # Update visuals
        if self.fade:
            fade_progress = EasingFunctions._cached_ease(progress, self.fade_ease)
            self.alpha = max(0, int(255 * (1.0 - fade_progress)))
            
            # Simplified size changes based on particle type
            if self.particle_type == 2:  # EXPLOSION
                self.size = self.original_size * (2.0 - progress)
            elif self.particle_type == 4:  # SMOKE
                self.size = self.original_size * (1.0 + progress * 0.5)
            elif self.particle_type in (8, 9):  # SMOOTH types
                pulse = 1.0 + 0.1 * fast_sin(self.age * 4)
                self.size = self.original_size * (1.0 - progress * 0.3) * pulse
        
        # Simple rotation update
        self.rotation += self.rotation_speed * dt
        
        return True

    def render(self, screen: pygame.Surface, camera=None) -> None:
        """Simplified rendering for better performance"""
        if self.alpha <= 0 or self.size <= 0:
            return
        
        # Screen coordinates
        if camera:
            screen_x, screen_y = camera.world_to_screen(self.x, self.y)
            size = max(1, int(self.size * camera.zoom))
        else:
            screen_x, screen_y = int(self.x), int(self.y)
            size = max(1, int(self.size))
        
        # Early culling
        screen_w, screen_h = screen.get_size()
        if (screen_x < -size or screen_x > screen_w + size or
            screen_y < -size or screen_y > screen_h + size):
            return
        
        try:
            # Particle type specific rendering
            if self.particle_type == 1:  # SPARKS
                self._render_spark(screen, screen_x, screen_y, size)
            elif self.particle_type == 6:  # ENERGY
                self._render_energy(screen, screen_x, screen_y, size)
            elif self.particle_type == 3:  # MAGIC
                self._render_magic(screen, screen_x, screen_y, size)
            else:
                # Standard circle rendering
                if self.alpha < 255:
                    # Create temporary surface for alpha blending
                    temp_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(temp_surface, (*self.color, self.alpha), 
                                     (size, size), size)
                    screen.blit(temp_surface, (screen_x - size, screen_y - size))
                else:
                    pygame.draw.circle(screen, self.color, (screen_x, screen_y), size)
        
        except (pygame.error, ValueError):
            pass

    def _render_spark(self, screen: pygame.Surface, x: int, y: int, size: int) -> None:
        """Simplified spark rendering"""
        length = size * 2
        end_x = int(x + length * fast_cos(self.rotation))
        end_y = int(y + length * fast_sin(self.rotation))
        
        # Simple line with alpha
        if self.alpha < 255:
            temp_surface = pygame.Surface((abs(end_x - x) + 4, abs(end_y - y) + 4), pygame.SRCALPHA)
            start_pos = (2, 2) if x < end_x else (abs(end_x - x) + 2, abs(end_y - y) + 2)
            end_pos = (abs(end_x - x) + 2, abs(end_y - y) + 2) if x < end_x else (2, 2)
            pygame.draw.line(temp_surface, (*self.color, self.alpha), start_pos, end_pos, max(1, size // 2))
            screen.blit(temp_surface, (min(x, end_x) - 2, min(y, end_y) - 2))
        else:
            pygame.draw.line(screen, self.color, (x, y), (end_x, end_y), max(1, size // 2))

    def _render_energy(self, screen: pygame.Surface, x: int, y: int, size: int) -> None:
        """Simplified energy rendering"""
        # Main circle with glow effect
        if self.alpha < 255:
            temp_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
            center = (size * 2, size * 2)
            # Outer glow
            pygame.draw.circle(temp_surface, (*self.color, self.alpha // 3), center, size + 2)
            # Inner core
            pygame.draw.circle(temp_surface, (*self.color, self.alpha), center, size)
            screen.blit(temp_surface, (x - size * 2, y - size * 2))
        else:
            pygame.draw.circle(screen, self.color, (x, y), size + 2)
            pygame.draw.circle(screen, (255, 255, 255), (x, y), size)

    def _render_magic(self, screen: pygame.Surface, x: int, y: int, size: int) -> None:
        """Simplified magic rendering"""
        if self.alpha < 255:
            temp_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
            center = (size * 2, size * 2)
            
            # Pulsing effect
            pulse_size = size + int(2 * fast_sin(self.age * 6))
            
            # Outer glow
            pygame.draw.circle(temp_surface, (*self.color, self.alpha // 4), center, pulse_size + 3)
            # Main particle  
            pygame.draw.circle(temp_surface, (*self.color, self.alpha), center, pulse_size)
            # Bright center
            pygame.draw.circle(temp_surface, (255, 255, 255, self.alpha), center, max(1, pulse_size // 2))
            
            screen.blit(temp_surface, (x - size * 2, y - size * 2))
        else:
            pygame.draw.circle(screen, self.color, (x, y), size)
