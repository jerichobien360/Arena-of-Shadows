import pygame
import math
import random
from dataclasses import dataclass
from typing import List, Tuple, Dict
from abc import ABC, abstractmethod


@dataclass
class ParticleConfig:
    """Configuration for particle properties"""
    speed_range: Tuple[float, float]
    size_range: Tuple[float, float]
    color_options: List[Tuple[int, int, int]]
    alpha_range: Tuple[float, float] = (120, 200)


class Particle(ABC):
    """Base particle class with common behavior"""
    
    def __init__(self, x: float, y: float):
        self.x = self.start_x = x
        self.y = self.start_y = y
        
    @abstractmethod
    def update(self, dt: float):
        """Update particle state"""
        pass
        
    @abstractmethod
    def render(self, screen: pygame.Surface):
        """Render particle to screen"""
        pass


class Leaf(Particle):
    """Animated falling leaf with natural movement"""
    
    CONFIG = ParticleConfig(
        speed_range=(15, 25),
        size_range=(2, 6),
        color_options=[(34, 89, 34), (67, 92, 35), (45, 67, 27), (30, 105, 30)]
    )
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self._init_properties()
        
    def _init_properties(self):
        """Initialize random properties for natural variation"""
        cfg = self.CONFIG
        self.speed_y = random.uniform(*cfg.speed_range)
        self.speed_x = random.uniform(-5, 5)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-45, 45)
        self.sway_amplitude = random.uniform(5, 15)
        self.sway_frequency = random.uniform(0.5, 1.5)
        self.size = random.uniform(*cfg.size_range)
        self.color = random.choice(cfg.color_options)
        self.alpha = random.uniform(*cfg.alpha_range)
        self.time = 0
        
    def update(self, dt: float):
        """Update leaf position with natural swaying"""
        from settings import SCREEN_HEIGHT, SCREEN_WIDTH
        
        self.time += dt
        self.y += self.speed_y * dt
        sway = math.sin(self.time * self.sway_frequency) * self.sway_amplitude * dt
        self.x += self.speed_x * dt + sway
        self.rotation += self.rotation_speed * dt
        
        # Reset when off screen
        if self.y > SCREEN_HEIGHT + 20:
            self.y = -20
            self.x = random.uniform(-50, SCREEN_WIDTH + 50)
            
    def render(self, screen: pygame.Surface):
        """Render organic leaf shape"""
        points = self._generate_leaf_points()
        if len(points) >= 3:
            self._render_leaf_surface(screen, points)
    
    def _generate_leaf_points(self) -> List[Tuple[float, float]]:
        """Generate organic leaf shape points"""
        points = []
        angle_offset = math.radians(self.rotation)
        
        for i in range(6):
            angle = (i * math.pi / 3) + angle_offset
            radius = self.size * (1 if i % 2 == 0 else 0.6)
            points.append((
                self.x + math.cos(angle) * radius,
                self.y + math.sin(angle) * radius
            ))
        return points
    
    def _render_leaf_surface(self, screen: pygame.Surface, points: List[Tuple[float, float]]):
        """Render leaf with alpha blending"""
        leaf_surf = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        adjusted_points = [
            (p[0] - self.x + self.size * 2, p[1] - self.y + self.size * 2) 
            for p in points
        ]
        pygame.draw.polygon(leaf_surf, (*self.color, int(self.alpha)), adjusted_points)
        screen.blit(leaf_surf, (self.x - self.size * 2, self.y - self.size * 2))


class Firefly(Particle):
    """Glowing firefly with realistic light effects"""
    
    CONFIG = ParticleConfig(
        speed_range=(8, 15),
        size_range=(1.5, 3),
        color_options=[(255, 255, 150), (150, 255, 150), (200, 200, 255)]
    )
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self._init_properties()
        
    def _init_properties(self):
        """Initialize firefly properties"""
        cfg = self.CONFIG
        self.speed = random.uniform(*cfg.speed_range)
        self.direction = random.uniform(0, 2 * math.pi)
        self.direction_timer = 0
        self.direction_interval = random.uniform(2, 4)
        self.glow_phase = random.uniform(0, 2 * math.pi)
        self.glow_speed = random.uniform(2, 3)
        self.brightness = 0
        self.size = random.uniform(*cfg.size_range)
        self.trail_positions: List[Tuple[float, float]] = []
        self.base_color = random.choice(cfg.color_options)
        
    def update(self, dt: float):
        """Update firefly movement and glow"""
        from settings import SCREEN_HEIGHT, SCREEN_WIDTH
        
        self._update_direction(dt)
        self._update_position(dt, SCREEN_WIDTH, SCREEN_HEIGHT)
        self._update_glow(dt)
        self._update_trail()
        
    def _update_direction(self, dt: float):
        """Handle smooth direction changes"""
        self.direction_timer += dt
        if self.direction_timer >= self.direction_interval:
            self.direction += random.uniform(-math.pi/6, math.pi/6)
            self.direction_timer = 0
            self.direction_interval = random.uniform(2, 4)
            
    def _update_position(self, dt: float, screen_w: int, screen_h: int):
        """Update position with wrapping"""
        wander = math.sin(self.glow_phase * 0.5) * 0.2
        self.x += math.cos(self.direction + wander) * self.speed * dt
        self.y += math.sin(self.direction + wander) * self.speed * dt
        
        # Wrap with margin
        margin = 100
        self.x = (self.x + margin) % (screen_w + 2 * margin) - margin
        self.y = (self.y + margin) % (screen_h + 2 * margin) - margin
    
    def _update_glow(self, dt: float):
        """Update natural glow pulsing"""
        self.glow_phase += self.glow_speed * dt
        pulse = (math.sin(self.glow_phase) + 1) * 0.5
        self.brightness = 0.3 + pulse * 0.7
        
    def _update_trail(self):
        """Maintain light trail"""
        self.trail_positions.append((self.x, self.y))
        if len(self.trail_positions) > 12:
            self.trail_positions.pop(0)
            
    def render(self, screen: pygame.Surface):
        """Render firefly with glow and trail"""
        self._render_trail(screen)
        self._render_main_glow(screen)
    
    def _render_trail(self, screen: pygame.Surface):
        """Render fading trail effect"""
        for i, (tx, ty) in enumerate(self.trail_positions[:-1]):
            trail_alpha = (i / len(self.trail_positions)) * self.brightness * 60
            trail_size = self.size * (i / len(self.trail_positions)) * 0.8
            if trail_size > 0.3:
                self._render_glow_at(screen, tx, ty, trail_size, trail_alpha)
    
    def _render_main_glow(self, screen: pygame.Surface):
        """Render main firefly with layered glow"""
        glow_intensity = int(self.brightness * 200)
        glow_size = self.size * 8
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        
        # Layered glow effect
        center = (glow_size, glow_size)
        glow_layers = [
            (glow_size, glow_intensity * 0.15),
            (glow_size * 0.6, glow_intensity * 0.3),
            (glow_size * 0.3, glow_intensity * 0.6),
        ]
        
        for radius, alpha in glow_layers:
            pygame.draw.circle(glow_surf, (*self.base_color, int(alpha)), center, radius)
        
        # Bright core
        pygame.draw.circle(glow_surf, (255, 255, 255, glow_intensity), center, self.size)
        screen.blit(glow_surf, (self.x - glow_size, self.y - glow_size))
    
    def _render_glow_at(self, screen: pygame.Surface, x: float, y: float, size: float, alpha: float):
        """Helper to render glow at specific position"""
        if alpha > 0:
            glow_surf = pygame.Surface((size * 6, size * 6), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.base_color, int(alpha)), (size * 3, size * 3), size * 2)
            screen.blit(glow_surf, (x - size * 3, y - size * 3))


class ParticleSystem:
    """Manages all particle systems efficiently"""
    
    def __init__(self):
        self.particles: Dict[str, List[Particle]] = {'leaves': [], 'fireflies': []}
        self._initialize_particles()
    
    def _initialize_particles(self):
        """Create initial particle distributions"""
        from settings import SCREEN_WIDTH, SCREEN_HEIGHT
        
        # Natural leaf distribution
        self.particles['leaves'] = [
            Leaf(
                random.uniform(-50, SCREEN_WIDTH + 50),
                random.uniform(-SCREEN_HEIGHT * 1.5, 0)
            ) for _ in range(12)
        ]
        
        # Fireflies away from edges
        self.particles['fireflies'] = [
            Firefly(
                random.uniform(150, SCREEN_WIDTH - 150),
                random.uniform(150, SCREEN_HEIGHT - 150)
            ) for _ in range(6)
        ]
    
    def update(self, dt: float):
        """Update all particle systems"""
        for particle_list in self.particles.values():
            for particle in particle_list:
                particle.update(dt)
    
    def get_particles(self) -> Dict[str, List[Particle]]:
        """Get all particles for rendering"""
        return self.particles
    
    def clear(self):
        """Clear all particles"""
        for particle_list in self.particles.values():
            particle_list.clear()
