from settings import *
import pygame
import math
import random

# game_states file
from game_states.gameplay import *

class Particle:
    """Base class for animated particles"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        
class Leaf(Particle):
    """Animated falling leaf particle"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed_y = random.uniform(15, 25)  # Slower, more graceful
        self.speed_x = random.uniform(-5, 5)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-45, 45)  # Gentler rotation
        self.sway_amplitude = random.uniform(5, 15)  # Reduced sway
        self.sway_frequency = random.uniform(0.5, 1.5)
        self.size = random.uniform(2, 6)
        self.color = random.choice([
            (34, 89, 34),    # Darker Forest Green
            (67, 92, 35),    # Darker Olive Drab
            (45, 67, 27),    # Darker Dark Olive Green
            (30, 105, 30),   # Darker Lime Green
        ])
        self.alpha = random.uniform(120, 200)  # Semi-transparent
        self.time = 0
        
    def update(self, dt):
        self.time += dt
        self.y += self.speed_y * dt
        self.x += self.speed_x * dt + math.sin(self.time * self.sway_frequency) * self.sway_amplitude * dt
        self.rotation += self.rotation_speed * dt
        
        # Reset when off screen
        if self.y > SCREEN_HEIGHT + 20:
            self.y = -20
            self.x = random.uniform(-50, SCREEN_WIDTH + 50)
            
    def render(self, screen):
        # Create leaf shape (more organic oval)
        points = []
        angle_offset = math.radians(self.rotation)
        for i in range(6):  # More points for smoother shape
            angle = (i * math.pi / 3) + angle_offset
            if i % 2 == 0:
                radius = self.size
            else:
                radius = self.size * 0.6
            px = self.x + math.cos(angle) * radius
            py = self.y + math.sin(angle) * radius
            points.append((px, py))
        
        if len(points) >= 3:
            # Create surface for alpha blending
            leaf_surf = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
            adjusted_points = [(p[0] - self.x + self.size * 2, p[1] - self.y + self.size * 2) for p in points]
            color_with_alpha = (*self.color, int(self.alpha))
            pygame.draw.polygon(leaf_surf, color_with_alpha, adjusted_points)
            screen.blit(leaf_surf, (self.x - self.size * 2, self.y - self.size * 2))

class Firefly(Particle):
    """Glowing firefly particle with improved lighting"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = random.uniform(8, 15)  # Slower movement
        self.direction = random.uniform(0, 2 * math.pi)
        self.direction_change_timer = 0
        self.direction_change_interval = random.uniform(2, 4)  # Less frequent direction changes
        self.glow_phase = random.uniform(0, 2 * math.pi)
        self.glow_speed = random.uniform(2, 3)  # Slower glow pulse
        self.brightness = 0
        self.size = random.uniform(1.5, 3)
        self.trail_positions = []
        self.max_trail_length = 12
        self.base_color = random.choice([
            (255, 255, 150),  # Warm yellow
            (150, 255, 150),  # Soft green
            (200, 200, 255),  # Cool blue
        ])
        
    def update(self, dt):
        # Update direction with smoother transitions
        self.direction_change_timer += dt
        if self.direction_change_timer >= self.direction_change_interval:
            self.direction += random.uniform(-math.pi/6, math.pi/6)  # Smaller direction changes
            self.direction_change_timer = 0
            self.direction_change_interval = random.uniform(2, 4)
            
        # Move with slight wandering
        wander = math.sin(self.glow_phase * 0.5) * 0.2
        self.x += math.cos(self.direction + wander) * self.speed * dt
        self.y += math.sin(self.direction + wander) * self.speed * dt
        
        # Smooth boundary wrapping
        margin = 100
        if self.x < -margin:
            self.x = SCREEN_WIDTH + margin
        elif self.x > SCREEN_WIDTH + margin:
            self.x = -margin
        if self.y < -margin:
            self.y = SCREEN_HEIGHT + margin
        elif self.y > SCREEN_HEIGHT + margin:
            self.y = -margin
            
        # Update glow with more natural pulsing
        self.glow_phase += self.glow_speed * dt
        pulse = (math.sin(self.glow_phase) + 1) * 0.5
        self.brightness = 0.3 + pulse * 0.7  # Between 0.3 and 1.0
        
        # Update trail with position smoothing
        self.trail_positions.append((self.x, self.y))
        if len(self.trail_positions) > self.max_trail_length:
            self.trail_positions.pop(0)
            
    def render(self, screen):
        # Render softer trail
        for i, (tx, ty) in enumerate(self.trail_positions):
            if i < len(self.trail_positions) - 1:
                trail_alpha = (i / len(self.trail_positions)) * self.brightness * 60
                trail_size = self.size * (i / len(self.trail_positions)) * 0.8
                if trail_size > 0.3:
                    color = (*self.base_color, int(trail_alpha))
                    glow_surf = pygame.Surface((trail_size * 6, trail_size * 6), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, color, (trail_size * 3, trail_size * 3), trail_size * 2)
                    screen.blit(glow_surf, (tx - trail_size * 3, ty - trail_size * 3))
        
        # Render main firefly with realistic glow
        glow_intensity = int(self.brightness * 200)
        
        # Create multi-layered glow
        glow_size = self.size * 8
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        
        # Outer glow (largest, most transparent)
        outer_color = (*self.base_color, int(glow_intensity * 0.15))
        pygame.draw.circle(glow_surf, outer_color, (glow_size, glow_size), glow_size)
        
        # Middle glow
        middle_color = (*self.base_color, int(glow_intensity * 0.3))
        pygame.draw.circle(glow_surf, middle_color, (glow_size, glow_size), glow_size * 0.6)
        
        # Inner glow
        inner_color = (*self.base_color, int(glow_intensity * 0.6))
        pygame.draw.circle(glow_surf, inner_color, (glow_size, glow_size), glow_size * 0.3)
        
        # Core
        core_color = (255, 255, 255, glow_intensity)
        pygame.draw.circle(glow_surf, core_color, (glow_size, glow_size), self.size)
        
        screen.blit(glow_surf, (self.x - glow_size, self.y - glow_size))

class MainMenuState(GameState):
    def __init__(self, font, sound_manager):
        self.font = font
        self.sound_manager = sound_manager
        
        # Load background image
        self.background_image = None
        try:
            self.background_image = pygame.image.load("assets/background/background_2.jpg")
            self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error:
            print("Warning: Could not load background image. Using default gradient background.")
        
        # Animation variables
        self.fade_alpha = 255
        self.fade_speed = 200  # Slower fade for smoother transition
        self.fade_direction = 1
        self.transitioning = False
        self.transition_target = None
        
        # Text animation variables
        self.title_pulse_time = 0
        self.text_appear_time = 0
        self.text_stagger_delay = 0.5
        
        # Enhanced lighting system
        self.lighting_time = 0
        self.ambient_light = 0.4  # Darker base lighting (60% dim)
        self.light_variation_speed = 0.8
        self.light_variation_amplitude = 0.05
        self.background_dim = 0.12  # 88% dim (12% brightness)
        
        # Particle systems
        self.leaves = []
        self.fireflies = []
        
        # Initialize particles
        self.init_particles()
        
        # Create surfaces
        self.fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fade_surface.fill(BLACK)
        
        self.lighting_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.background_dim_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Create gradient background as fallback
        self.create_gradient_background()
        
    def create_gradient_background(self):
        """Create a beautiful gradient background as fallback"""
        self.gradient_background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Create vertical gradient from dark blue-green to darker
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(15 + (25 - 15) * ratio)
            g = int(25 + (45 - 25) * ratio)
            b = int(35 + (55 - 35) * ratio)
            color = (r, g, b)
            pygame.draw.line(self.gradient_background, color, (0, y), (SCREEN_WIDTH, y))
        
    def init_particles(self):
        """Initialize particle systems with better distribution"""
        # Create leaves with staggered timing
        for i in range(12):  # Reduced number for cleaner look
            x = random.uniform(-50, SCREEN_WIDTH + 50)
            y = random.uniform(-SCREEN_HEIGHT * 1.5, 0)  # Spread them out more
            self.leaves.append(Leaf(x, y))
            
        # Create fireflies with better positioning
        for i in range(6):  # Fewer fireflies for elegance
            x = random.uniform(150, SCREEN_WIDTH - 150)
            y = random.uniform(150, SCREEN_HEIGHT - 150)
            self.fireflies.append(Firefly(x, y))
        
    def enter(self):
        # Reset animation state when entering
        self.fade_alpha = 255
        self.fade_direction = 1
        self.transitioning = False
        self.transition_target = None
        self.title_pulse_time = 0
        self.text_appear_time = 0
        self.lighting_time = 0
        
        # Load and play menu music
        if self.sound_manager.load_background_music("assets/background_music/main_menu.mp3"):
            self.sound_manager.play_background_music()
    
    def start_transition(self, target_state):
        """Start a fade-out transition to the target state"""
        if not self.transitioning:
            self.transitioning = True
            self.transition_target = target_state
            self.fade_direction = -1
    
    def update_lighting(self, dt):
        """Update realistic lighting system"""
        self.lighting_time += dt
        
        # Create subtle ambient light variations (like wind through trees)
        base_variation = math.sin(self.lighting_time * self.light_variation_speed) * self.light_variation_amplitude
        flicker_variation = math.sin(self.lighting_time * 3.2) * 0.02  # Subtle flicker
        
        current_light = self.ambient_light + base_variation + flicker_variation
        current_light = max(0.2, min(0.8, current_light))  # Clamp between 20% and 80%
        
        # Clear and rebuild lighting overlay
        self.lighting_overlay.fill((0, 0, 0, 0))
        
        # Apply background dimming (88% dim = 12% brightness)
        dim_alpha = int(255 * (1.0 - self.background_dim))
        self.background_dim_surface.fill((0, 0, 0, dim_alpha))
        
        # Add atmospheric lighting with color tinting
        atmosphere_alpha = int((1.0 - current_light) * 120)
        if atmosphere_alpha > 0:
            # Use a subtle blue-purple tint for night atmosphere
            atmosphere_color = (10, 15, 40, atmosphere_alpha)
            atmosphere_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            atmosphere_surf.fill(atmosphere_color)
            self.lighting_overlay.blit(atmosphere_surf, (0, 0))
    
    def update(self, dt):
        # Update animation timers
        self.title_pulse_time += dt
        self.text_appear_time += dt
        
        # Update lighting
        self.update_lighting(dt)
        
        # Update particles
        for leaf in self.leaves:
            leaf.update(dt)
            
        for firefly in self.fireflies:
            firefly.update(dt)
        
        # Handle fade transitions with easing
        if self.transitioning:
            # Ease out transition
            fade_progress = 1.0 - (self.fade_alpha / 255.0)
            eased_progress = fade_progress * fade_progress  # Quadratic ease
            self.fade_alpha = 255 * (1.0 - eased_progress)
            self.fade_alpha -= self.fade_speed * dt
            
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                return self.transition_target
        else:
            if self.fade_direction == 1:
                # Ease in fade
                self.fade_alpha -= self.fade_speed * dt
                if self.fade_alpha <= 0:
                    self.fade_alpha = 0
                    self.fade_direction = 0
        
        # Handle input only when not transitioning and fully faded in
        if not self.transitioning and self.fade_alpha == 0:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
                self.start_transition("gameplay")
        
        return None
    
    def render(self, screen):
        # Render background
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.blit(self.gradient_background, (0, 0))
        
        # Apply background dimming
        screen.blit(self.background_dim_surface, (0, 0))
        
        # Render particles (leaves behind fireflies for proper layering)
        for leaf in self.leaves:
            leaf.render(screen)
            
        for firefly in self.fireflies:
            firefly.render(screen)
        
        # Apply atmospheric lighting
        screen.blit(self.lighting_overlay, (0, 0))
        
        # Calculate text animations with smoother easing
        def ease_in_out_cubic(t):
            if t < 0.5:
                return 4 * t * t * t
            else:
                return 1 - pow(-2 * t + 2, 3) / 2
        
        # Title animations
        title_scale = 1.0 + 0.05 * math.sin(self.title_pulse_time * 1.5)  # Subtle pulsing
        title_alpha_t = min(1.0, max(0.0, (self.text_appear_time - 0.8) / 1.5))
        title_alpha = int(255 * ease_in_out_cubic(title_alpha_t))
        
        # Other text animations
        start_alpha_t = min(1.0, max(0.0, (self.text_appear_time - self.text_stagger_delay * 2) / 1.2))
        start_alpha = int(255 * ease_in_out_cubic(start_alpha_t))
        
        controls_alpha_t = min(1.0, max(0.0, (self.text_appear_time - self.text_stagger_delay * 3) / 1.0))
        controls_alpha = int(255 * ease_in_out_cubic(controls_alpha_t))
        
        # Render animated title with enhanced glow
        if title_alpha > 0:
            title_font_size = int(72 * title_scale)  # Fixed base size
            title_font = pygame.font.Font(None, title_font_size)
            
            title_text = "ARENA OF SHADOWS"
            
            # Simple plain text rendering
            title_surface = title_font.render(title_text, True, (255, 255, 255))
            title_surface.set_alpha(title_alpha)
            
            title_x = SCREEN_WIDTH // 2 - title_surface.get_width() // 2
            title_y = 160 + int(5 * math.sin(self.title_pulse_time * 2))  # Subtle float
            
            # Render main title (no glow layers)
            screen.blit(title_surface, (title_x, title_y))
        
        # Render start text with elegant blinking
        if start_alpha > 0:
            start_text = "Press ENTER to Start"
            start_surface = self.font.render(start_text, True, (180, 220, 180))
            
            if start_alpha >= 200:
                # Gentle breathing effect
                breath_alpha = int(255 * (0.6 + 0.4 * math.sin(self.title_pulse_time * 2)))
                start_surface.set_alpha(breath_alpha)
            else:
                start_surface.set_alpha(start_alpha)
            
            start_x = SCREEN_WIDTH // 2 - start_surface.get_width() // 2
            start_y = 260
            screen.blit(start_surface, (start_x, start_y))
        
        # Render controls text
        if controls_alpha > 0:
            controls_surface = self.font.render("WASD/Arrows: Move | SPACE: Attack", True, (120, 160, 120))
            controls_surface.set_alpha(controls_alpha)
            
            controls_x = SCREEN_WIDTH // 2 - controls_surface.get_width() // 2
            controls_y = 310
            screen.blit(controls_surface, (controls_x, controls_y))
        
        # Apply fade overlay with smooth blending
        if self.fade_alpha > 0:
            self.fade_surface.set_alpha(int(self.fade_alpha))
            screen.blit(self.fade_surface, (0, 0))
