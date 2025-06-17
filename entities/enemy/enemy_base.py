from settings import *
import pygame
import math
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple
from enum import Enum


class FormationType(Enum):
    SURROUND = "surround"
    PINCER = "pincer" 
    AMBUSH = "ambush"


@dataclass
class FormationData:
    target: Tuple[float, float] = (0, 0)
    active: bool = False


class AttackIndicator:
    """Visual attack warning"""
    def __init__(self, enemy, player, duration, color, attack_type, delay=0, angle_offset=0):
        self.enemy, self.duration, self.color, self.attack_type = enemy, duration, color, attack_type
        self.delay, self.angle_offset = delay, angle_offset
        self.timer = 0
        self.should_fire = self.expired = False
        self.final_target_x = self.final_target_y = None
        self._update_target(player)
    
    def _update_target(self, player):
        """Calculate target with spread"""
        if self.attack_type == "sniper":
            self.current_target_x, self.current_target_y = player.x, player.y
        else:
            base_angle = math.atan2(player.y - self.enemy.y, player.x - self.enemy.x)
            spread_angle = base_angle + self.angle_offset
            offset = 25
            self.current_target_x = player.x + math.cos(spread_angle) * offset
            self.current_target_y = player.y + math.sin(spread_angle) * offset
    
    def update(self, dt, player):
        """Update indicator"""
        self.timer += dt
        
        if not self.should_fire and self.timer >= self.delay:
            self._update_target(player)
        
        if not self.should_fire and self.timer >= self.delay + self.duration:
            self.final_target_x, self.final_target_y = self.current_target_x, self.current_target_y
            self.should_fire = self.expired = True
    
    def render(self, screen, camera=None):
        """Clean target indicator"""
        if self.timer < self.delay:
            return
        
        if camera:
            target_x, target_y = camera.world_to_screen(self.current_target_x, self.current_target_y)
            zoom = camera.zoom
        else:
            target_x, target_y, zoom = self.current_target_x, self.current_target_y, 1.0
        
        progress = min(1.0, (self.timer - self.delay) / self.duration)
        pulse = 0.5 + 0.5 * abs(math.sin(progress * math.pi * 8))
        
        intensity = pulse * (0.8 if self.attack_type == "sniper" else 0.6)
        color = tuple(min(255, int(c * intensity)) for c in self.color)
        radius = int((6 if self.attack_type == "sniper" else 8) * zoom * (0.8 + 0.4 * pulse))
        
        try:
            pygame.draw.circle(screen, color, (int(target_x), int(target_y)), radius, 2)
        except (ValueError, OverflowError):
            pass


class Projectile:
    """Enemy projectile with fixed collision detection and render method"""
    def __init__(self, x, y, target_x, target_y, speed, damage, color, size, owner=None):
        self.x, self.y, self.speed, self.damage, self.color, self.size = x, y, speed, damage, color, size
        self.owner = owner  # Reference to the enemy that created this projectile
        
        dx, dy = target_x - x, target_y - y
        distance = math.hypot(dx, dy) or 1
        self.velocity = [(dx / distance) * speed, (dy / distance) * speed]
        
        # Add lifetime to prevent infinite projectiles
        self.lifetime = 5.0  # 5 seconds max
    
    def update(self, dt):
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt
        self.lifetime -= dt
    
    def check_collision(self, player):
        if not hasattr(player, 'x') or not hasattr(player, 'y'):
            return False
            
        player_radius = getattr(player, 'radius', 15)
        collision_distance = player_radius + self.size + 2  # Small buffer
        return math.hypot(player.x - self.x, player.y - self.y) < collision_distance
    
    def is_off_world(self):
        # Use consistent bounds - check against screen bounds with margin
        margin = 100
        return (self.x < -margin or self.x > SCREEN_WIDTH + margin or
                self.y < -margin or self.y > SCREEN_HEIGHT + margin or
                self.lifetime <= 0)
    
    def is_expired(self):
        """Alternative method name for clarity"""
        return self.is_off_world()
    
    def render(self, screen, camera=None):
        """Render the projectile with camera support"""
        if camera:
            screen_x, screen_y = camera.world_to_screen(self.x, self.y)
            radius = max(1, int(self.size * camera.zoom))
        else:
            screen_x, screen_y = self.x, self.y
            radius = self.size
        
        # Only render if on screen
        if (0 <= screen_x <= screen.get_width() and 
            0 <= screen_y <= screen.get_height()):
            try:
                pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), radius)
            except (ValueError, OverflowError):
                # Handle any drawing errors gracefully
                pass


class Enemy:
    """Base enemy class with all common functionality"""
    
    ENEMY_STATS = {
        "crawler": (40, 15, 120, 12, RED, 25, 25),
        "brute": (100, 30, 80, 18, (180, 0, 0), 60, 25),
        "sniper": (60, 45, 60, 10, (100, 100, 200), 80, 300),
        "fireshooter": (70, 25, 90, 14, (255, 100, 0), 70, 180),
        "shadow_assassin": (80, 40, 140, 16, (64, 0, 64), 120, 60)
    }
    
    def __init__(self, x, y, enemy_type="crawler"):
        self.x, self.y, self.type = x, y, enemy_type
        self.damage_flash_timer = self.attack_cooldown = 0
        self.knockback_velocity = [0, 0]
        self.attack_indicators, self.projectiles = [], []
        
        # Formation system
        self.formation = FormationData()
        self.group_id = None
        
        # Aggression system
        self.aggro_level = 0.0
        self.rage_mode = False
        
        # Unpack stats
        stats = self.ENEMY_STATS[enemy_type]
        (self.hp, self.attack_power, self.speed, self.radius, 
        self.color, self.exp_value, self.attack_range) = stats
        self.max_hp = self.hp
        
        # Ranged enemy preferred distance
        self.preferred_distance = {"sniper": 250, "fireshooter": 120}.get(enemy_type, 0)
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)

        # Fade transition properties
        self.spawn_alpha = 0.0  # Start invisible
        self.death_alpha = 1.0  # Start visible
        self.is_spawning = True
        self.is_dying = False
        self.spawn_duration = 0.8  # Fade in over 0.8 seconds
        self.death_duration = 0.6  # Fade out over 0.6 seconds

    def _check_rage_mode(self):
        """Basic rage mode implementation for all enemies"""
        # Simple rage mode: activate when HP is below 30%
        if not self.rage_mode and self.hp <= self.max_hp * 0.3:
            self.rage_mode = True
            # Slight damage boost when enraged
            self.attack_power = int(self.attack_power * 1.2)
            # Visual indicator - slightly redder color
            if hasattr(self, 'original_color'):
                pass  # Keep original color stored
            else:
                self.original_color = self.color
            
            # Add red tint to color
            r, g, b = self.color
            self.color = (min(255, r + 30), max(0, g - 10), max(0, b - 10))

    def update(self, dt, player, formation_manager=None):
        """Enhanced update with fade transitions"""
        self._update_fade_states(dt)
        
        # Only update physics and AI if not in death fade
        if not self.is_dying:
            self._update_physics(dt)
            
            # AI with formation priority
            if formation_manager and self.formation.active:
                formation_manager.update_enemy_behavior(self, dt, player)
            else:
                self._standard_ai(dt, player)
                
            self._update_attacks(dt, player)
        
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        self.damage_flash_timer = max(0, self.damage_flash_timer - dt)
        self.rect.center = (self.x, self.y)

        # Increase aggression over time
        self.aggro_level = min(3.0, self.aggro_level + dt * 0.2)
        self._check_rage_mode()
    
    def _update_fade_states(self, dt):
        """Update spawn and death fade effects"""
        if self.is_spawning:
            self.spawn_alpha = min(1.0, self.spawn_alpha + dt / self.spawn_duration)
            if self.spawn_alpha >= 1.0:
                self.is_spawning = False
        
        if self.is_dying:
            self.death_alpha = max(0.0, self.death_alpha - dt / self.death_duration)

    def _update_physics(self, dt):
        """Physics update with boundary constraints"""
        if any(abs(v) > 5 for v in self.knockback_velocity):
            self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, 
                        self.x + self.knockback_velocity[0] * dt))
            self.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, 
                        self.y + self.knockback_velocity[1] * dt))
            self.knockback_velocity = [v * 0.85 for v in self.knockback_velocity]
        else:
            self.knockback_velocity = [0, 0]

    def _standard_ai(self, dt, player):
        """Standard AI behavior for all enemy types"""
        if self.is_dying:
            return
            
        distance = math.hypot(player.x - self.x, player.y - self.y)
        
        # Standard movement AI for different enemy types
        if self.type == "crawler":
            # Simple chase behavior
            if distance > 0:
                dx, dy = player.x - self.x, player.y - self.y
                unit_x, unit_y = dx / distance, dy / distance
                
                move_speed = self.speed * dt
                self.x += unit_x * move_speed
                self.y += unit_y * move_speed
        
        elif self.type == "brute":
            # Slower but more aggressive movement
            if distance > 0:
                dx, dy = player.x - self.x, player.y - self.y
                unit_x, unit_y = dx / distance, dy / distance
                
                move_speed = self.speed * dt
                self.x += unit_x * move_speed
                self.y += unit_y * move_speed
        
        elif self.type in ["sniper", "fireshooter"]:
            # Ranged enemies maintain preferred distance
            if distance > 0:
                dx, dy = player.x - self.x, player.y - self.y
                unit_x, unit_y = dx / distance, dy / distance
                
                # Move toward or away from player to maintain preferred distance
                if distance < self.preferred_distance:
                    # Move away
                    move_speed = self.speed * dt
                    self.x -= unit_x * move_speed
                    self.y -= unit_y * move_speed
                elif distance > self.preferred_distance + 50:
                    # Move closer
                    move_speed = self.speed * dt
                    self.x += unit_x * move_speed
                    self.y += unit_y * move_speed
        
        # Keep within bounds
        self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.y))
        
        # Combat behavior
        if distance <= self.attack_range and self.attack_cooldown <= 0:
            if self.type in ["crawler", "brute"]:
                # Melee attack
                player.take_damage(self.attack_power, enemy=self)
                self.attack_cooldown = 1.0
            elif self.type in ["sniper", "fireshooter"]:
                # Ranged attack
                self._initiate_ranged_attack(player)
    
    def _throw_dagger_with_indicator(self, player):
        """Throw dagger with proper attack indicator system"""
        indicator = AttackIndicator(
            enemy=self,
            player=player,
            duration=0.5,  # Warning time
            color=(200, 0, 200),  # Purple indicator
            attack_type="dagger",
            delay=0,
            angle_offset=0
        )
        self.attack_indicators.append(indicator)
        
        # Faster cooldown in rage mode
        self.dagger_cooldown = random.uniform(1.0, 1.5) if self.rage_mode else random.uniform(1.5, 2.0)

    def _initiate_ranged_attack(self, player):
        """Ranged attack initialization"""
        configs = {
            "sniper": (1, 1.2, (255, 255, 0), 2.5, 0),
            "fireshooter": (3, 0.6, (255, 100, 0), 2.0, 0.1),
            "shadow_assassin": (3, 1, (64, 0, 64), 3, 0.05)
        }
        
        # Skip if this enemy type doesn't have ranged attacks
        if self.type not in configs:
            return
            
        shot_count, duration, color, cooldown, delay = configs[self.type]
        
        for i in range(shot_count):
            angle_offset = (i - 1) * 0.25 if shot_count > 1 else 0
            indicator = AttackIndicator(self, player, duration, color, self.type, 
                                    delay=i * delay, angle_offset=angle_offset)
            self.attack_indicators.append(indicator)
        
        self.attack_cooldown = cooldown
    
    def _update_attacks(self, dt, player):
        """Update attack systems"""
        # Update indicators
        for indicator in self.attack_indicators[:]:
            indicator.update(dt, player)
            if indicator.should_fire:
                self._fire_projectile(indicator)
                indicator.should_fire = False
            if indicator.expired:
                self.attack_indicators.remove(indicator)
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update(dt)
            if projectile.check_collision(player):
                player.take_damage(projectile.damage, enemy=self)
                self.projectiles.remove(projectile)
            elif projectile.is_off_world():
                self.projectiles.remove(projectile)
    
    def _fire_projectile(self, indicator):
        """Fire projectile"""
        configs = {
            "sniper": (400, (255, 255, 100), 3),
            "fireshooter": (250, (255, 150, 0), 5),
            "dagger": (450, (200, 200, 200), 4)  # Fast silver dagger
        }
        
        if indicator.attack_type not in configs:
            return
            
        speed, color, size = configs[indicator.attack_type]
        
        projectile = Projectile(self.x, self.y, indicator.final_target_x, 
                            indicator.final_target_y, speed, self.attack_power // 2, color, size)  # Half damage for ranged
        self.projectiles.append(projectile)
    
    def apply_knockback_velocity(self, vel_x, vel_y):
        """Apply capped knockback"""
        self.knockback_velocity[0] += vel_x
        self.knockback_velocity[1] += vel_y
        
        # Cap velocity
        magnitude = math.hypot(*self.knockback_velocity)
        if magnitude > 400:
            scale = 400 / magnitude
            self.knockback_velocity = [v * scale for v in self.knockback_velocity]
   
    def take_damage(self, amount, attacker=None):  # Add attacker parameter
        """Enhanced damage with death fade trigger"""
        self.hp -= amount
        self.damage_flash_timer = 0.2
        
        if self.hp <= 0 and not self.is_dying:
            self.is_dying = True
            return True  # Don't remove immediately, let fade complete
        
        return False

    def should_be_removed(self):
        """Check if enemy should be removed (after death fade)"""
        return self.is_dying and self.death_alpha <= 0.0
    
    def get_current_alpha(self):
        """Get current alpha based on fade states"""
        if self.is_spawning:
            return self.spawn_alpha
        elif self.is_dying:
            return self.death_alpha
        return 1.0

    def render(self, screen, camera=None):
        """Enhanced render with fade transitions"""
        # Calculate current alpha
        current_alpha = self.get_current_alpha()
        
        # Skip rendering if completely transparent
        if current_alpha <= 0.01:
            return
        
        # Render attacks (they should appear normally)
        if not self.is_dying:  # Don't show attacks while dying
            for indicator in self.attack_indicators:
                indicator.render(screen, camera)
            for projectile in self.projectiles:
                projectile.render(screen, camera)
        
        zoom = camera.zoom if camera else 1.0
        radius = int(self.radius * zoom)
        
        # Calculate color with damage flash
        color = self.color
        if self.damage_flash_timer > 0:
            flash = self.damage_flash_timer / 0.2
            color = tuple(min(255, c + int(150 * flash)) for c in color)
        
        if self.rage_mode:
            # Add pulsing red glow in rage mode
            pulse = 0.7 + 0.3 * abs(math.sin(pygame.time.get_ticks() * 0.01))
            rage_glow = int(80 * pulse)
            color = (min(255, color[0] + rage_glow), color[1], color[2])

        # Apply alpha to color
        alpha_color = (*color, int(255 * current_alpha))
        
        # Create a surface for alpha blending
        if current_alpha < 1.0:
            temp_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, alpha_color, (radius, radius), radius)
            screen.blit(temp_surface, (int(self.x - radius), int(self.y - radius)))
        else:
            # Normal rendering for performance when fully opaque
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), radius)
        
        # Formation indicator (with alpha)
        if self.formation.active and not self.is_dying:
            formation_alpha = int(255 * current_alpha * 0.8)  # Slightly dimmer
            formation_color = (*GREEN, formation_alpha)
            if current_alpha < 1.0:
                temp_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, formation_color, (2, 2), 2)
                screen.blit(temp_surface, (int(self.x - 2), int(self.y - 2)))
            else:
                pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), 2)
        
        # Type markers (with alpha)
        if not self.is_dying:
            if self.type == "sniper":
                line_len = int(4 * zoom)
                line_alpha = int(255 * current_alpha)
                line_color = (*WHITE, line_alpha)
                if current_alpha < 1.0:
                    # Draw on temp surface for alpha
                    temp_surface = pygame.Surface((line_len * 2, line_len * 2), pygame.SRCALPHA)
                    pygame.draw.line(temp_surface, line_color, 
                                   (0, line_len), (line_len * 2, line_len), 1)
                    pygame.draw.line(temp_surface, line_color, 
                                   (line_len, 0), (line_len, line_len * 2), 1)
                    screen.blit(temp_surface, (int(self.x - line_len), int(self.y - line_len)))
                else:
                    pygame.draw.line(screen, WHITE, (self.x - line_len, self.y), 
                                   (self.x + line_len, self.y), 1)
                    pygame.draw.line(screen, WHITE, (self.x, self.y - line_len), 
                                   (self.x, self.y + line_len), 1)
            
            elif self.type == "fireshooter":
                inner_radius = max(1, int((self.radius - 3) * zoom))
                inner_alpha = int(255 * current_alpha)
                # Define FIRESHOOTER_INNER_COLOR if not in settings
                inner_color = (*((255, 200, 0)), inner_alpha)  # Yellow-orange
                if current_alpha < 1.0:
                    temp_surface = pygame.Surface((inner_radius * 2, inner_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(temp_surface, inner_color, (inner_radius, inner_radius), inner_radius)
                    screen.blit(temp_surface, (int(self.x - inner_radius), int(self.y - inner_radius)))
                else:
                    pygame.draw.circle(screen, (255, 200, 0), (int(self.x), int(self.y)), inner_radius)
        
        # Health bar (with alpha)
        if self.hp < self.max_hp and not self.is_dying:
            self._draw_health_bar(screen, camera, current_alpha)
   
    def _draw_health_bar(self, screen, camera=None, alpha=1.0):
        """Health bar with alpha support"""
        zoom = camera.zoom if camera else 1.0
        bar_width, bar_height = int(20 * zoom), int(3 * zoom)
        bar_x = self.x - bar_width // 2
        bar_y = self.y - (self.radius * zoom) - 6 * zoom
        
        red_alpha = int(255 * alpha)
        green_alpha = int(255 * alpha)
        
        if alpha < 1.0:
            # Create temp surface for alpha blending
            temp_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
            pygame.draw.rect(temp_surface, (*RED, red_alpha), (0, 0, bar_width, bar_height))
            health_width = (self.hp / self.max_hp) * bar_width
            pygame.draw.rect(temp_surface, (*GREEN, green_alpha), (0, 0, health_width, bar_height))
            screen.blit(temp_surface, (bar_x, bar_y))
        else:
            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
            health_width = (self.hp / self.max_hp) * bar_width
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))
