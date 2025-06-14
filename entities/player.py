from settings import *
import pygame
import math
import random


class Player:
    """
    Player class representing the main character in the game.
    Handles movement, combat, leveling, and rendering.
    """
    
    def __init__(self, sound_manager, camera, start_x=0, start_y=0):
        self.sound_manager = sound_manager
        self.camera = camera
        self.x, self.y = start_x, start_y
        self.radius = 15
        self.world_bounds = None
        self.attack_cooldown = self.damage_flash_timer = 0
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
        self.handle_movement(dt)
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        self.damage_flash_timer = max(0, self.damage_flash_timer - dt)
        self.check_level_up()
        self.update_rect()

    def handle_movement(self, dt):
        """Handle WASD/arrow key movement with bounds checking"""
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        
        # Normalize diagonal movement
        if dx and dy:
            dy *= 0.707; dx *= 0.707
        
        # Apply movement with screen bounds
        self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x + dx * self.speed * dt))
        self.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.y + dy * self.speed * dt))
        
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
                    self.apply_knockback(enemy, distance)
                hit_count += 1
        
        return hit_count

    def apply_knockback(self, enemy, distance):
        """Apply knockback force to enemy"""
        if distance > 0:
            knockback = 80 / distance
            enemy.x = max(enemy.radius, min(SCREEN_WIDTH - enemy.radius, 
                         enemy.x + (enemy.x - self.x) * knockback))
            enemy.y = max(enemy.radius, min(SCREEN_HEIGHT - enemy.radius, 
                         enemy.y + (enemy.y - self.y) * knockback))
            enemy.rect.center = (enemy.x, enemy.y)

    def take_damage(self, amount):
        """Take damage and trigger visual feedback"""
        self.hp = max(0, self.hp - amount)
        self.damage_flash_timer = 0.3
        self.camera.add_shake(intensity=1, duration=1)

    def add_experience(self, exp):
        """Add experience points"""
        self.experience += exp

    def check_level_up(self):
        """Check for level up and apply bonuses"""
        exp_needed = self.level * 100
        if self.experience >= exp_needed:
            self.level += 1
            self.experience -= exp_needed
            self.stat_points += 3
            self.max_hp += 15
            self.hp = self.max_hp  # Full heal on level up
            self.attack_power += 3
            self.sound_manager.play_sound('level_up')

    def render(self, screen):
        """Render player with damage flash effect"""
        # Calculate color with damage flash
        color = GREEN
        if self.damage_flash_timer > 0:
            flash = int(255 * self.damage_flash_timer / 0.3)
            color = (min(255, GREEN[0] + flash), GREEN[1], GREEN[2])
        
        # Draw player circle
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        
        # Show attack range when ready
        if self.attack_cooldown <= 0:
            pygame.draw.circle(screen, (0, 255, 0, 30), 
                             (int(self.x), int(self.y)), 60, 1)

    def set_world_bounds(self, bounds):
        """Set world boundaries as (left, top, right, bottom) tuple"""
        self.world_bounds = bounds
