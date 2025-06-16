from settings import *
import pygame
import math
import random


class Player:
    """
    Player class representing the main character in the game.
    Handles movement, combat, leveling, and rendering with smooth knockback effects.
    """
    
    def __init__(self, sound_manager, camera, start_x=0, start_y=0):
        self.sound_manager = sound_manager
        self.camera = camera
        self.x, self.y = start_x, start_y
        self.radius = 15
        self.world_bounds = None
        self.attack_cooldown = self.damage_flash_timer = 0
        
        # Knockback system
        self.knockback_velocity_x = 0
        self.knockback_velocity_y = 0
        self.knockback_decay = 0.88  # How fast knockback slows down (0-1)
        self.knockback_threshold = 8  # Minimum velocity before stopping
        self.knockback_resistance = 0.7  # Player resistance to knockback (0-1, lower = more resistance)
        
        self.reset_stats()
        self.update_rect()

    def reset_stats(self):
        """Reset player stats to initial values"""
        self.hp = self.max_hp = 100
        self.attack_power = 25
        self.speed = 200
        self.level = 1
        self.experience = self.stat_points = 0

    def update(self, dt):
        """Update player state each frame"""
        self.update_knockback(dt)
        self.handle_movement(dt)
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        self.damage_flash_timer = max(0, self.damage_flash_timer - dt)
        self.check_level_up()
        self.update_rect()

    def update_knockback(self, dt):
        """Update knockback physics"""
        # Apply knockback velocity to position
        if abs(self.knockback_velocity_x) > self.knockback_threshold or abs(self.knockback_velocity_y) > self.knockback_threshold:
            # Move based on knockback velocity
            new_x = self.x + self.knockback_velocity_x * dt
            new_y = self.y + self.knockback_velocity_y * dt
            
            # Apply screen bounds
            new_x = max(self.radius, min(SCREEN_WIDTH - self.radius, new_x))
            new_y = max(self.radius, min(SCREEN_HEIGHT - self.radius, new_y))
            
            # Apply world bounds if set
            if self.world_bounds:
                left, top, right, bottom = self.world_bounds
                new_x = max(left + self.radius, min(right - self.radius, new_x))
                new_y = max(top + self.radius, min(bottom - self.radius, new_y))
            
            self.x = new_x
            self.y = new_y
            
            # Apply decay to knockback velocity
            self.knockback_velocity_x *= self.knockback_decay
            self.knockback_velocity_y *= self.knockback_decay
        else:
            # Stop knockback when velocity is too small
            self.knockback_velocity_x = 0
            self.knockback_velocity_y = 0

    def handle_movement(self, dt):
        """Handle WASD/arrow key movement with bounds checking and knockback consideration"""
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        
        # Normalize diagonal movement
        if dx and dy:
            dy *= 0.707; dx *= 0.707
        
        # Reduce movement speed if experiencing knockback
        knockback_magnitude = math.sqrt(self.knockback_velocity_x**2 + self.knockback_velocity_y**2)
        movement_reduction = max(0.3, 1.0 - (knockback_magnitude / 250))  # Reduce movement when knocked back
        
        # Apply movement with reduced speed during knockback
        move_speed = self.speed * movement_reduction
        new_x = self.x + dx * move_speed * dt
        new_y = self.y + dy * move_speed * dt
        
        # Apply screen bounds
        self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, new_x))
        self.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, new_y))
        
        # Apply world bounds if set
        if self.world_bounds:
            left, top, right, bottom = self.world_bounds
            self.x = max(left + self.radius, min(right - self.radius, self.x))
            self.y = max(top + self.radius, min(bottom - self.radius, self.y))

    def update_rect(self):
        """Update collision rectangle to match position"""
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 
                               self.radius * 2, self.radius * 2)

    def attack(self, enemies):
        """Attack nearby enemies within range"""
        if self.attack_cooldown > 0:
            return 0
        
        self.attack_cooldown = 0.5
        self.sound_manager.play_sound('attack')
        
        hit_count = 0
        for enemy in enemies[:]:  # Slice copy to avoid modification issues
            distance = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if distance <= 60:  # Attack range
                damage = self.attack_power + random.randint(-3, 3)
                if enemy.take_damage(damage):  # Enemy died
                    self.sound_manager.play_sound('enemy_death')
                    self.add_experience(enemy.exp_value)
                else:  # Enemy survived, apply knockback
                    self.sound_manager.play_sound('enemy_hit')
                    self.apply_smooth_knockback(enemy, distance, damage)
                hit_count += 1
        
        return hit_count

    def apply_smooth_knockback(self, enemy, distance, damage):
        """Apply smooth knockback force to enemy based on damage and distance"""
        if distance > 0:
            # Calculate knockback direction (normalized)
            knockback_dir_x = (enemy.x - self.x) / distance
            knockback_dir_y = (enemy.y - self.y) / distance
            
            # Calculate knockback force based on damage and inverse distance
            base_knockback = 150  # Base knockback strength
            damage_multiplier = damage / 25.0  # Scale with damage (25 is base attack)
            distance_multiplier = max(0.5, 60 / distance)  # Stronger knockback when closer
            
            knockback_force = base_knockback * damage_multiplier * distance_multiplier
            
            # Apply knockback velocity to enemy
            enemy.apply_knockback_velocity(knockback_dir_x * knockback_force, 
                                         knockback_dir_y * knockback_force)

    def take_damage(self, amount, enemy=None):
        """Take damage and trigger visual feedback with knockback effect"""
        self.hp = max(0, self.hp - amount)
        self.damage_flash_timer = 0.3
        
        # PLAY PLAYER DAMAGE SOUND EFFECT
        self.sound_manager.play_sound('player_damage')
        
        # Apply knockback if enemy is provided
        if enemy:
            self.apply_damage_knockback(enemy, amount)
        
        # Enhanced camera shake based on damage and enemy size
        shake_intensity = 1
        if enemy:
            # Scale shake based on enemy size and damage
            size_multiplier = enemy.radius / 12.0  # 12 is base crawler radius
            damage_multiplier = amount / 15.0  # 15 is base crawler damage
            shake_intensity = min(3, 1 + size_multiplier * damage_multiplier)
        
        self.camera.add_shake(intensity=shake_intensity, duration=1)

    def apply_damage_knockback(self, enemy, damage):
        """Apply knockback to player when taking damage from an enemy"""
        # Calculate knockback direction (away from enemy)
        dx = self.x - enemy.x
        dy = self.y - enemy.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Normalize direction
            dx /= distance
            dy /= distance
            
            # Calculate knockback force based on enemy size, damage, and distance
            base_knockback = 120  # Base knockback strength for player
            
            # Size multiplier based on enemy radius (larger enemies = more knockback)
            size_multiplier = enemy.radius / 12.0  # 12 is base crawler radius
            
            # Damage multiplier
            damage_multiplier = damage / 15.0  # 15 is base damage
            
            # Distance multiplier (closer = more knockback)
            distance_multiplier = max(0.8, 30 / max(distance, 1))
            
            # Calculate final knockback force
            knockback_force = base_knockback * size_multiplier * damage_multiplier * distance_multiplier
            
            # Apply resistance factor
            knockback_force *= self.knockback_resistance
            
            # Apply knockback velocity
            self.knockback_velocity_x += dx * knockback_force
            self.knockback_velocity_y += dy * knockback_force
            
            # Cap maximum knockback velocity
            max_knockback = 300
            knockback_magnitude = math.sqrt(self.knockback_velocity_x**2 + self.knockback_velocity_y**2)
            if knockback_magnitude > max_knockback:
                scale = max_knockback / knockback_magnitude
                self.knockback_velocity_x *= scale
                self.knockback_velocity_y *= scale

    def add_experience(self, exp):
        """Add experience points with immediate level up check"""
        self.experience += exp

    def check_level_up(self):
        """Check for level up and handle it immediately"""
        leveled_up = False
        
        # Handle multiple level ups in one go if player gained a lot of exp
        while self.experience >= self.level * 100:
            exp_needed = self.level * 100
            self.level += 1
            self.experience -= exp_needed
            self.stat_points += 3
            self.max_hp += 15
            self.hp = self.max_hp
            self.attack_power += 3
            self.knockback_resistance = min(0.9, self.knockback_resistance + 0.02)
            leveled_up = True
        
        # Play sound only once, even if multiple levels were gained
        if leveled_up:
            self.sound_manager.play_sound('level_up')

    def render(self, screen):
        """Render player with damage flash effect and knockback visual effects"""
        # Calculate color with damage flash
        color = GREEN
        if self.damage_flash_timer > 0:
            flash = int(255 * self.damage_flash_timer / 0.3)
            color = (min(255, GREEN[0] + flash), GREEN[1], GREEN[2])
        
        # Knockback visual effect - motion trail
        knockback_magnitude = math.sqrt(self.knockback_velocity_x**2 + self.knockback_velocity_y**2)
        if knockback_magnitude > 15:  # Only show effect for significant knockback
            # Draw a motion trail effect
            trail_alpha = min(80, int(knockback_magnitude / 4))
            trail_positions = []
            
            # Calculate trail positions
            for i in range(2):
                trail_factor = (i + 1) * 0.4
                trail_x = self.x - self.knockback_velocity_x * trail_factor * 0.015
                trail_y = self.y - self.knockback_velocity_y * trail_factor * 0.015
                trail_positions.append((trail_x, trail_y))
            
            # Draw motion trails
            try:
                for i, (trail_x, trail_y) in enumerate(trail_positions):
                    trail_alpha_current = trail_alpha // (i + 2)
                    trail_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(trail_surface, (*color, trail_alpha_current), 
                                     (self.radius, self.radius), self.radius - 2)
                    screen.blit(trail_surface, (trail_x - self.radius, trail_y - self.radius))
            except:
                pass  # Skip trail effect if not supported
        
        # Draw player circle
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        
        # Show attack range when ready
        if self.attack_cooldown <= 0:
            pygame.draw.circle(screen, (0, 255, 0, 30), 
                             (int(self.x), int(self.y)), 60, 1)

    def set_world_bounds(self, bounds):
        """Set world boundaries as (left, top, right, bottom) tuple"""
        self.world_bounds = bounds
