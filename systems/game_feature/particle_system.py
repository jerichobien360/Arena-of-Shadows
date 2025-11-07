import pygame
import math
import random
from typing import List, Tuple, Optional
from src.ui.components.particle import *


# TODO: Simplify the code and follow on the DRY and KISS Principle

class ParticleSystem:
    """Enhanced particle system with smooth effects"""
    
    def __init__(self, world_bounds: Optional[Tuple[float, float, float, float]] = None):
        self.particles: List[Particle] = []
        self.world_bounds = world_bounds
        self.max_particles = 750  # Increased for smooth effects
    
    def set_world_bounds(self, bounds: Tuple[float, float, float, float]) -> None:
        """Set world boundaries for particle physics"""
        self.world_bounds = bounds
    
    def create_smooth_fade_effect(self, x: float, y: float, color: Tuple[int, int, int],
                                count: int = 15, intensity: float = 1.0) -> None:
        """Create smooth fading particle effect"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 120) * intensity
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed - random.uniform(0, 30)
            
            size = random.uniform(3, 8) * intensity
            lifetime = random.uniform(2.0, 4.0)
            
            particle = Particle(x, y, vel_x, vel_y, color, size, lifetime,
                              ParticleType.SMOOTH_FADE, gravity=50, bounce=0.2,
                              fade_ease=EaseType.EASE_OUT, scale_ease=EaseType.EASE_IN_OUT)
            self.particles.append(particle)
    
    def create_smooth_magic_effect(self, x: float, y: float, color: Tuple[int, int, int],
                                 count: int = 20) -> None:
        """Create smooth magical particle effect"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, 80)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed - random.uniform(20, 60)
            
            size = random.uniform(4, 10)
            lifetime = random.uniform(2.5, 4.5)
            
            particle = Particle(x, y, vel_x, vel_y, color, size, lifetime,
                              ParticleType.MAGIC, gravity=-30, bounce=0,
                              fade_ease=EaseType.SINE, scale_ease=EaseType.ELASTIC)
            self.particles.append(particle)
    
    def create_smooth_float_effect(self, x: float, y: float, color: Tuple[int, int, int],
                                 count: int = 12) -> None:
        """Create smooth floating particle effect"""
        for _ in range(count):
            angle = random.uniform(-math.pi/3, math.pi/3)
            speed = random.uniform(15, 60)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed - random.uniform(40, 80)
            
            size = random.uniform(3, 7)
            lifetime = random.uniform(3.0, 6.0)
            
            particle = Particle(x, y, vel_x, vel_y, color, size, lifetime,
                              ParticleType.SMOOTH_FLOAT, gravity=-20, bounce=0,
                              fade_ease=EaseType.EASE_IN_OUT, movement_ease=EaseType.SINE)
            self.particles.append(particle)
    
    def create_smooth_scale_effect(self, x: float, y: float, color: Tuple[int, int, int],
                                 count: int = 10) -> None:
        """Create smooth scaling particle effect"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(40, 100)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            size = random.uniform(5, 12)
            lifetime = random.uniform(1.5, 3.0)
            
            particle = Particle(x, y, vel_x, vel_y, color, size, lifetime,
                              ParticleType.SMOOTH_SCALE, gravity=0, bounce=0,
                              fade_ease=EaseType.EASE_OUT, scale_ease=EaseType.BOUNCE)
            self.particles.append(particle)
    
    def create_damage_effect(self, x: float, y: float, damage: int,
                                    is_player: bool = False, enemy_type: str = None) -> None:
        """Create enhanced damage particles with smooth effects"""
        particle_count = min(20, max(8, damage // 2))
        
        if is_player:
            # Enhanced player damage with smooth effects
            self.create_smooth_fade_effect(x, y, (255, 50, 50),
                                            count=particle_count, intensity=1.2)
            self.create_smooth_scale_effect(x, y, (255, 100, 100), count=6)
        else:
            # Enhanced enemy damage based on type
            if enemy_type == "crawler":
                self.create_smooth_fade_effect(x, y, (150, 0, 0), count=particle_count)
            elif enemy_type == "brute":
                self.create_smooth_fade_effect(x, y, (100, 0, 0), count=particle_count, intensity=1.5)
                self._create_debris_particles(x, y, particle_count // 2, (80, 40, 20))
            elif enemy_type == "sniper":
                self.create_smooth_scale_effect(x, y, (100, 100, 200), count=particle_count)
                self._create_energy_particles(x, y, particle_count // 2, (150, 150, 255))
            elif enemy_type == "fireshooter":
                self._create_explosion_particles(x, y, particle_count, (255, 100, 0))
                self._create_smoke_particles(x, y, particle_count // 2, (100, 50, 0))
            else:
                # Default enhanced enemy damage
                self.create_smooth_fade_effect(x, y, (120, 0, 0), count=particle_count)
    
    def create_death_effect(self, x: float, y: float, entity_type: str, 
                                   is_player: bool = False) -> None:
        """Create dramatic death effect with smooth animations"""
        if is_player:
            # Enhanced player death - dramatic smooth effects
            self._create_explosion_particles(x, y, 25, (255, 0, 0), intensity=2.5)
            self.create_smooth_fade_effect(x, y, (200, 0, 0), count=30, intensity=2.0)
            self.create_smooth_magic_effect(x, y, (255, 100, 100), count=20)
            self.create_smooth_float_effect(x, y, (255, 50, 50), count=15)
        else:
            # Enhanced enemy death effects
            if entity_type == "crawler":
                self.create_smooth_fade_effect(x, y, (120, 0, 0), count=20, intensity=1.5)
                self.create_smooth_scale_effect(x, y, (150, 20, 20), count=8)
            elif entity_type == "brute":
                self._create_explosion_particles(x, y, 25, (100, 50, 0), intensity=1.8)
                self._create_debris_particles(x, y, 20, (80, 40, 20), intensity=1.5)
                self.create_smooth_fade_effect(x, y, (120, 60, 30), count=15)
            elif entity_type == "sniper":
                self.create_smooth_scale_effect(x, y, (100, 100, 200), count=25, intensity=1.5)
                self._create_energy_particles(x, y, 15, (150, 150, 255))
                self.create_smooth_float_effect(x, y, (120, 120, 255), count=12)
            elif entity_type == "fireshooter":
                self._create_explosion_particles(x, y, 30, (255, 80, 0), intensity=2.0)
                self._create_smoke_particles(x, y, 20, (100, 50, 0))
                self.create_smooth_magic_effect(x, y, (255, 120, 0), count=15)
    
    def create_attack_effect(self, x: float, y: float, attack_type: str = "melee") -> None:
        """Create enhanced attack impact effects"""
        if attack_type == "melee":
            self.create_smooth_scale_effect(x, y, (255, 255, 100), count=10)
            self._create_spark_particles(x, y, 12, (255, 255, 150))
        elif attack_type == "projectile":
            self._create_explosion_particles(x, y, 8, (255, 150, 0))
            self.create_smooth_fade_effect(x, y, (255, 180, 50), count=6)
        elif attack_type == "magic":
            self.create_smooth_magic_effect(x, y, (100, 255, 200), count=15)
            self.create_smooth_float_effect(x, y, (150, 255, 180), count=8)
    
    def create_healing_effect(self, x: float, y: float) -> None:
        """Create enhanced healing particles with smooth animations"""
        self.create_smooth_magic_effect(x, y, (100, 255, 100), count=15)
        self.create_smooth_float_effect(x, y, (150, 255, 150), count=10)
        self._create_magic_particles(x, y, 12, (120, 255, 120), 
                                            ParticleType.HEALING, velocity_range=80, gravity=-50)
    
    def _create_blood_particles(self, x: float, y: float, count: int, 
                                       color: Tuple[int, int, int], intensity: float = 1.0) -> None:
        """Create enhanced blood splatter particles with smooth physics"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150) * intensity
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed - random.uniform(0, 50)
            
            size = random.uniform(2, 6) * intensity
            lifetime = random.uniform(1.5, 3.5)
            
            # Enhanced color variation
            r = max(0, min(255, color[0] + random.randint(-30, 30)))
            g = max(0, min(255, color[1] + random.randint(-10, 10)))
            b = max(0, min(255, color[2] + random.randint(-10, 10)))
            
            particle = Particle(x, y, vel_x, vel_y, (r, g, b), size, lifetime,
                               ParticleType.BLOOD, gravity=200, bounce=0.4,
                               fade_ease=EaseType.EASE_OUT, scale_ease=EaseType.EASE_IN_OUT)
            self.particles.append(particle)
    
    def _create_spark_particles(self, x: float, y: float, count: int,
                                       color: Tuple[int, int, int], intensity: float = 1.0) -> None:
        """Create enhanced spark particles with smooth animations"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 300) * intensity
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            size = random.uniform(1, 4)
            lifetime = random.uniform(0.5, 1.5)
            
            particle = Particle(x, y, vel_x, vel_y, color, size, lifetime,
                               ParticleType.SPARKS, gravity=120, bounce=0.8,
                               fade_ease=EaseType.EASE_OUT, movement_ease=EaseType.EASE_IN_OUT)
            self.particles.append(particle)
    
    def _create_explosion_particles(self, x: float, y: float, count: int,
                                           color: Tuple[int, int, int], intensity: float = 1.0) -> None:
        """Create enhanced explosion particles with smooth scaling"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(80, 200) * intensity
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            size = random.uniform(3, 10) * intensity
            lifetime = random.uniform(0.8, 2.0)
            
            # Enhanced color variation for fire effect
            r = max(0, min(255, color[0] + random.randint(-50, 50)))
            g = max(0, min(255, color[1] + random.randint(-30, 30)))
            b = max(0, min(255, color[2] + random.randint(-20, 20)))
            
            particle = Particle(x, y, vel_x, vel_y, (r, g, b), size, lifetime,
                               ParticleType.EXPLOSION, gravity=60, bounce=0.3,
                               fade_ease=EaseType.EASE_OUT, scale_ease=EaseType.BOUNCE)
            self.particles.append(particle)
    
    def _create_debris_particles(self, x: float, y: float, count: int,
                                        color: Tuple[int, int, int], intensity: float = 1.0) -> None:
        """Create enhanced debris particles with realistic physics"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(60, 180) * intensity
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed - random.uniform(20, 80)
            
            size = random.uniform(2, 6)
            lifetime = random.uniform(2.5, 5.0)
            
            particle = Particle(x, y, vel_x, vel_y, color, size, lifetime,
                               ParticleType.DEBRIS, gravity=350, bounce=0.7,
                               fade_ease=EaseType.EASE_IN_OUT, movement_ease=EaseType.EASE_OUT)
            self.particles.append(particle)
    
    def _create_energy_particles(self, x: float, y: float, count: int,
                                        color: Tuple[int, int, int]) -> None:
        """Create enhanced energy particles with smooth trails"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            size = random.uniform(2, 6)
            lifetime = random.uniform(1.0, 2.5)
            
            particle = Particle(x, y, vel_x, vel_y, color, size, lifetime,
                               ParticleType.ENERGY, gravity=0, bounce=0,
                               fade_ease=EaseType.SINE, scale_ease=EaseType.ELASTIC)
            self.particles.append(particle)
    
    def _create_magic_particles(self, x: float, y: float, count: int,
                                       color: Tuple[int, int, int], 
                                       particle_type: ParticleType = ParticleType.MAGIC,
                                       velocity_range: float = 120, gravity: float = 0) -> None:
        """Create enhanced magical particles with smooth pulsing"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, velocity_range)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            size = random.uniform(3, 8)
            lifetime = random.uniform(1.5, 3.5)
            
            particle = Particle(x, y, vel_x, vel_y, color, size, lifetime,
                               particle_type, gravity=gravity, bounce=0,
                               fade_ease=EaseType.SINE, scale_ease=EaseType.ELASTIC)
            self.particles.append(particle)
    
    def _create_smoke_particles(self, x: float, y: float, count: int,
                                       color: Tuple[int, int, int]) -> None:
        """Create enhanced smoke particles with smooth expansion"""
        for _ in range(count):
            angle = random.uniform(-math.pi/3, math.pi/3)  # Upward bias
            speed = random.uniform(20, 80)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed - random.uniform(30, 80)
            
            size = random.uniform(4, 12)
            lifetime = random.uniform(2.5, 5.0)
            
            particle = Particle(x, y, vel_x, vel_y, color, size, lifetime,
                               ParticleType.SMOKE, gravity=-25, bounce=0,
                               fade_ease=EaseType.EASE_IN_OUT, scale_ease=EaseType.EASE_OUT)
            self.particles.append(particle)
    
    def create_environmental_effect(self, x: float, y: float, effect_type: str) -> None:
        """Create environmental particle effects"""
        if effect_type == "dust":
            self._create_dust_particles(x, y, 8, (150, 130, 100))
        elif effect_type == "steam":
            self._create_steam_particles(x, y, 10, (200, 200, 255))
        elif effect_type == "rain":
            self._create_rain_particles(x, y, 15, (100, 150, 255))
        elif effect_type == "leaves":
            self._create_leaf_particles(x, y, 6, (100, 150, 50))
    
    def _create_dust_particles(self, x: float, y: float, count: int, color: Tuple[int, int, int]) -> None:
        """Create dust particles with gentle floating motion"""
        for _ in range(count):
            vel_x = random.uniform(-20, 20)
            vel_y = random.uniform(-40, -10)
            size = random.uniform(1, 3)
            lifetime = random.uniform(3.0, 6.0)
            
            particle = Particle(x, y, vel_x, vel_y, color, size, lifetime,
                               ParticleType.SMOOTH_FLOAT, gravity=-10, bounce=0,
                               fade_ease=EaseType.EASE_IN_OUT)
            self.particles.append(particle)
    
    def _create_steam_particles(self, x: float, y: float, count: int, color: Tuple[int, int, int]) -> None:
        """Create steam particles with upward floating motion"""
        for _ in range(count):
            vel_x = random.uniform(-15, 15)
            vel_y = random.uniform(-60, -20)
            size = random.uniform(2, 5)
            lifetime = random.uniform(2.0, 4.0)
            
            particle = Particle(x, y, vel_x, vel_y, color, size, lifetime,
                               ParticleType.SMOKE, gravity=-40, bounce=0,
                               fade_ease=EaseType.EASE_OUT, scale_ease=EaseType.EASE_OUT)
            self.particles.append(particle)
    
    def _create_rain_particles(self, x: float, y: float, count: int, color: Tuple[int, int, int]) -> None:
        """Create rain particles with downward motion"""
        for _ in range(count):
            vel_x = random.uniform(-10, 10)
            vel_y = random.uniform(100, 200)
            size = random.uniform(1, 2)
            lifetime = random.uniform(1.0, 2.0)
            
            particle = Particle(x, y, vel_x, vel_y, color, size, lifetime,
                               ParticleType.SPARKS, gravity=300, bounce=0,
                               fade_ease=EaseType.LINEAR)
            self.particles.append(particle)
    
    def _create_leaf_particles(self, x: float, y: float, count: int, color: Tuple[int, int, int]) -> None:
        """Create falling leaf particles with swaying motion"""
        for _ in range(count):
            vel_x = random.uniform(-30, 30)
            vel_y = random.uniform(20, 60)
            size = random.uniform(2, 4)
            lifetime = random.uniform(4.0, 8.0)
            
            particle = Particle(x, y, vel_x, vel_y, color, size, lifetime,
                               ParticleType.SMOOTH_FLOAT, gravity=50, bounce=0.2,
                               fade_ease=EaseType.EASE_IN_OUT, movement_ease=EaseType.SINE)
            self.particles.append(particle)
    
    def update(self, dt: float) -> None:
        """Update all particles with performance optimization"""
        # Limit particles for performance
        if len(self.particles) > self.max_particles:
            # Remove oldest particles first, prioritizing less important ones
            self.particles.sort(key=lambda p: (p.particle_type.value, p.age))
            self.particles = self.particles[-self.max_particles:]
        
        # Update existing particles
        self.particles = [p for p in self.particles if p.update(dt, self.world_bounds)]
    
    def render(self, screen: pygame.Surface, camera=None) -> None:
        """Render all particles with depth sorting for better visual quality"""
        # Sort particles by y-coordinate for proper depth rendering
        sorted_particles = sorted(self.particles, key=lambda p: p.y)
        
        for particle in sorted_particles:
            particle.render(screen, camera)
    
    def render_bloom_effect(self, screen: pygame.Surface, camera=None) -> None:
        """Render particles with bloom effect for enhanced visuals"""
        # Create bloom surface
        bloom_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        
        # Render particles that should have bloom
        bloom_types = [ParticleType.MAGIC, ParticleType.ENERGY, ParticleType.EXPLOSION, 
                      ParticleType.SMOOTH_FADE, ParticleType.SMOOTH_SCALE]
        
        for particle in self.particles:
            if particle.particle_type in bloom_types and particle.alpha > 50:
                # Render bloom effect
                if camera:
                    screen_x, screen_y = camera.world_to_screen(particle.x, particle.y)
                    zoom = camera.zoom
                else:
                    screen_x, screen_y = particle.x, particle.y
                    zoom = 1.0
                
                bloom_size = int(particle.size * zoom * 2)
                bloom_alpha = min(100, particle.alpha // 3)
                
                if bloom_alpha > 10 and bloom_size > 0:
                    bloom_color = (*particle.color, bloom_alpha)
                    pygame.draw.circle(bloom_surface, bloom_color, 
                                     (int(screen_x), int(screen_y)), bloom_size)
        
        # Apply bloom to main screen
        screen.blit(bloom_surface, (0, 0), special_flags=pygame.BLEND_ADD)
        
        # Render normal particles
        self.render(screen, camera)
    
    def clear(self) -> None:
        """Clear all particles"""
        self.particles.clear()
    
    def get_particle_count(self) -> int:
        """Get current particle count"""
        return len(self.particles)
    
    def get_particles_by_type(self, particle_type: ParticleType) -> List[Particle]:
        """Get particles of a specific type"""
        return [p for p in self.particles if p.particle_type == particle_type]
    
    def remove_particles_by_type(self, particle_type: ParticleType) -> None:
        """Remove all particles of a specific type"""
        self.particles = [p for p in self.particles if p.particle_type != particle_type]
    
    def set_max_particles(self, max_count: int) -> None:
        """Set maximum particle count for performance tuning"""
        self.max_particles = max_count
        if len(self.particles) > max_count:
            self.particles = self.particles[-max_count:]

    # Dash Effect
    def create_dash_start_effect(self, x: float, y: float, dx: float, dy: float) -> None:
        """Create enhanced dash start effect with directional particles"""
        # Normalize direction vector for consistent effects
        dash_length = math.sqrt(dx * dx + dy * dy)
        if dash_length > 0:
            norm_dx = dx / dash_length
            norm_dy = dy / dash_length
        else:
            norm_dx, norm_dy = 1.0, 0.0
        
        # Calculate dash intensity based on direction magnitude
        intensity = min(2.0, max(0.5, dash_length / 100.0))
        
        # Create main dash burst effect
        self._create_dash_burst_particles(x, y, norm_dx, norm_dy, intensity)
        
        # Create directional trail particles
        self._create_dash_trail_particles(x, y, norm_dx, norm_dy, intensity)
        
        # Create energy wave effect
        self._create_dash_wave_particles(x, y, intensity)
        
        # Create dust/debris kicked up by the dash
        self._create_dash_debris_particles(x, y, -norm_dx, -norm_dy, intensity)

    def _create_dash_burst_particles(self, x: float, y: float, dx: float, dy: float, intensity: float) -> None:
        """Create the main burst of particles at dash start"""
        count = int(12 * intensity)
        
        for _ in range(count):
            # Create particles in a cone behind the dash direction
            angle_offset = random.uniform(-math.pi/3, math.pi/3)
            base_angle = math.atan2(-dy, -dx)  # Opposite to dash direction
            angle = base_angle + angle_offset
            
            speed = random.uniform(80, 150) * intensity
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            size = random.uniform(3, 7) * intensity
            lifetime = random.uniform(0.8, 1.5)
            
            # Dynamic color based on intensity
            base_color = (100, 150, 255)  # Blue energy color
            r = min(255, int(base_color[0] + intensity * 50))
            g = min(255, int(base_color[1] + intensity * 30))
            b = min(255, int(base_color[2]))
            
            particle = Particle(x, y, vel_x, vel_y, (r, g, b), size, lifetime,
                            ParticleType.SMOOTH_FADE, gravity=30, bounce=0.1,
                            fade_ease=EaseType.EASE_OUT, scale_ease=EaseType.EASE_IN_OUT)
            self.particles.append(particle)

    def _create_dash_trail_particles(self, x: float, y: float, dx: float, dy: float, intensity: float) -> None:
        """Create trailing particles that follow the dash direction"""
        count = int(8 * intensity)
        
        for _ in range(count):
            # Create particles that move in the dash direction but slower
            speed_factor = random.uniform(0.3, 0.7)
            vel_x = dx * random.uniform(50, 120) * speed_factor
            vel_y = dy * random.uniform(50, 120) * speed_factor
            
            # Add some perpendicular spread
            perp_x = -dy * random.uniform(-30, 30)
            perp_y = dx * random.uniform(-30, 30)
            vel_x += perp_x
            vel_y += perp_y
            
            size = random.uniform(2, 5)
            lifetime = random.uniform(1.0, 2.0)
            
            # Lighter, more ethereal color for trails
            color = (150, 200, 255)
            
            particle = Particle(x, y, vel_x, vel_y, color, size, lifetime,
                            ParticleType.SMOOTH_FLOAT, gravity=-10, bounce=0,
                            fade_ease=EaseType.EASE_IN_OUT, movement_ease=EaseType.SINE)
            self.particles.append(particle)

    def _create_dash_wave_particles(self, x: float, y: float, intensity: float) -> None:
        """Create expanding wave effect from dash start point"""
        count = int(15 * intensity)
        
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(60, 120) * intensity
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            size = random.uniform(1, 4)
            lifetime = random.uniform(0.5, 1.2)
            
            # Bright, energetic color for the wave
            color = (200, 220, 255)
            
            particle = Particle(x, y, vel_x, vel_y, color, size, lifetime,
                            ParticleType.SMOOTH_SCALE, gravity=0, bounce=0,
                            fade_ease=EaseType.EASE_OUT, scale_ease=EaseType.BOUNCE)
            self.particles.append(particle)

    def _create_dash_debris_particles(self, x: float, y: float, dx: float, dy: float, intensity: float) -> None:
        """Create debris particles kicked up opposite to dash direction"""
        count = int(6 * intensity)
        
        for _ in range(count):
            # Create particles moving opposite to dash with some spread
            angle_offset = random.uniform(-math.pi/4, math.pi/4)
            base_angle = math.atan2(dy, dx)
            angle = base_angle + angle_offset
            
            speed = random.uniform(40, 80) * intensity
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed - random.uniform(10, 30)  # Slight upward bias
            
            size = random.uniform(2, 4)
            lifetime = random.uniform(1.5, 3.0)
            
            # Earthy debris color
            color = (120, 100, 80)
            
            particle = Particle(x, y, vel_x, vel_y, color, size, lifetime,
                            ParticleType.DEBRIS, gravity=200, bounce=0.4,
                            fade_ease=EaseType.EASE_IN_OUT, movement_ease=EaseType.EASE_OUT)
            self.particles.append(particle)

    # Dash Trail Effect
    def create_dash_trail(self, x: float, y: float) -> None:
        """Create continuous dash trail effect during dash movement"""
        # Create main energy trail particles
        self._create_dash_energy_trail(x, y)
        
        # Create afterimage particles for smooth trail
        self._create_dash_afterimage_particles(x, y)
        
        # Create subtle speed lines
        self._create_dash_speed_lines(x, y)
        
        # Occasionally create spark particles for extra flair
        if random.random() < 0.3:  # 30% chance per call
            self._create_dash_spark_trail(x, y)

    def _create_dash_energy_trail(self, x: float, y: float) -> None:
        """Create the main energy trail particles"""
        count = random.randint(3, 6)  # Variable count for organic feel
        
        for _ in range(count):
            # Small random spread around the position
            offset_x = random.uniform(-8, 8)
            offset_y = random.uniform(-8, 8)
            
            # Minimal velocity with slight randomness
            vel_x = random.uniform(-20, 20)
            vel_y = random.uniform(-15, 15)
            
            size = random.uniform(2, 5)
            lifetime = random.uniform(0.8, 1.5)
            
            # Bright blue energy color with slight variation
            r = random.randint(80, 120)
            g = random.randint(140, 180)
            b = random.randint(240, 255)
            
            particle = Particle(
                x + offset_x, y + offset_y, vel_x, vel_y, 
                (r, g, b), size, lifetime,
                ParticleType.SMOOTH_FADE, gravity=0, bounce=0,
                fade_ease=EaseType.EASE_OUT, scale_ease=EaseType.EASE_IN_OUT
            )
            self.particles.append(particle)

    def _create_dash_afterimage_particles(self, x: float, y: float) -> None:
        """Create afterimage particles that linger briefly"""
        count = random.randint(2, 4)
        
        for _ in range(count):
            # Very small spread for tight trail
            offset_x = random.uniform(-5, 5)
            offset_y = random.uniform(-5, 5)
            
            # Almost stationary with tiny drift
            vel_x = random.uniform(-10, 10)
            vel_y = random.uniform(-10, 10)
            
            size = random.uniform(3, 6)
            lifetime = random.uniform(0.5, 1.0)
            
            # Lighter, more transparent blue
            color = (120, 160, 220)
            
            particle = Particle(
                x + offset_x, y + offset_y, vel_x, vel_y,
                color, size, lifetime,
                ParticleType.SMOOTH_FLOAT, gravity=0, bounce=0,
                fade_ease=EaseType.EASE_IN_OUT, movement_ease=EaseType.SINE
            )
            self.particles.append(particle)

    def _create_dash_speed_lines(self, x: float, y: float) -> None:
        """Create subtle speed line particles"""
        count = random.randint(1, 3)
        
        for _ in range(count):
            # Wider spread for speed lines
            offset_x = random.uniform(-15, 15)
            offset_y = random.uniform(-10, 10)
            
            # Slight backward drift to simulate motion blur
            vel_x = random.uniform(-30, -10)
            vel_y = random.uniform(-5, 5)
            
            size = random.uniform(1, 3)
            lifetime = random.uniform(0.3, 0.8)
            
            # Subtle white/light blue for speed lines
            color = (180, 200, 240)
            
            particle = Particle(
                x + offset_x, y + offset_y, vel_x, vel_y,
                color, size, lifetime,
                ParticleType.SPARKS, gravity=0, bounce=0,
                fade_ease=EaseType.LINEAR, movement_ease=EaseType.EASE_OUT
            )
            self.particles.append(particle)

    def _create_dash_spark_trail(self, x: float, y: float) -> None:
        """Create occasional spark particles for extra visual flair"""
        count = random.randint(2, 4)
        
        for _ in range(count):
            # Random spread around position
            offset_x = random.uniform(-10, 10)
            offset_y = random.uniform(-10, 10)
            
            # More dynamic velocity for sparks
            vel_x = random.uniform(-40, 40)
            vel_y = random.uniform(-30, 30)
            
            size = random.uniform(1, 2)
            lifetime = random.uniform(0.4, 0.9)
            
            # Bright white/yellow sparks
            r = random.randint(200, 255)
            g = random.randint(200, 255)
            b = random.randint(100, 150)
            
            particle = Particle(
                x + offset_x, y + offset_y, vel_x, vel_y,
                (r, g, b), size, lifetime,
                ParticleType.SPARKS, gravity=20, bounce=0.1,
                fade_ease=EaseType.EASE_OUT, movement_ease=EaseType.EASE_IN_OUT
            )
            self.particles.append(particle)
