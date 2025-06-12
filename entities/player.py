from settings import *
import pygame, math, random


class Player:
    def __init__(self, sound_manager):
        self.sound_manager = sound_manager
        self.reset_stats()
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.radius = 15
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 
                               self.radius * 2, self.radius * 2)
        self.attack_cooldown = 0
        self.damage_flash_timer = 0
        
    def reset_stats(self):
        """Reset player stats"""
        self.hp = 100
        self.max_hp = 100
        self.attack_power = 25
        self.speed = 200
        self.level = 1
        self.experience = 0
        self.stat_points = 0
    
    def update(self, dt):
        """Update player state"""
        self.handle_movement(dt)
        self.update_timers(dt)
        self.check_level_up()
        self.update_rect()
    
    def handle_movement(self, dt):
        """Handle player movement input"""
        keys = pygame.key.get_pressed()
        dx = dy = 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1
        
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707
        
        # Update position with bounds checking
        self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, 
                                    self.x + dx * self.speed * dt))
        self.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, 
                                    self.y + dy * self.speed * dt))
    
    def update_timers(self, dt):
        """Update various timers"""
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        self.damage_flash_timer = max(0, self.damage_flash_timer - dt)
    
    def update_rect(self):
        """Update collision rectangle"""
        self.rect.center = (self.x, self.y)
    
    def attack(self, enemies):
        """Attack nearby enemies"""
        if self.attack_cooldown > 0:
            return 0
        
        self.attack_cooldown = 0.5
        self.sound_manager.play_sound('attack')
        
        hit_count = 0
        attack_range = 60
        
        for enemy in enemies[:]:  # Use slice to avoid modification during iteration
            distance = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
            if distance <= attack_range:
                damage = self.attack_power + random.randint(-3, 3)
                enemy_died = enemy.take_damage(damage)
                
                if enemy_died:
                    self.sound_manager.play_sound('enemy_death')
                    self.add_experience(enemy.exp_value)
                else:
                    self.sound_manager.play_sound('enemy_hit')
                    self.apply_knockback(enemy, distance)
                
                hit_count += 1
        
        return hit_count
    
    def apply_knockback(self, enemy, distance):
        """Apply smooth knockback to enemy"""
        if distance > 0:
            knockback_force = 80
            dx = (enemy.x - self.x) / distance
            dy = (enemy.y - self.y) / distance
            
            # Apply knockback with bounds checking
            new_x = enemy.x + dx * knockback_force
            new_y = enemy.y + dy * knockback_force
            
            enemy.x = max(enemy.radius, min(SCREEN_WIDTH - enemy.radius, new_x))
            enemy.y = max(enemy.radius, min(SCREEN_HEIGHT - enemy.radius, new_y))
            enemy.rect.center = (enemy.x, enemy.y)
    
    def take_damage(self, amount):
        """Take damage"""
        self.hp = max(0, self.hp - amount)
        self.damage_flash_timer = 0.3
    
    def add_experience(self, exp):
        """Add experience points"""
        self.experience += exp
    
    def check_level_up(self):
        """Check and handle level up"""
        exp_needed = self.level * 100
        if self.experience >= exp_needed:
            self.level += 1
            self.experience -= exp_needed
            self.stat_points += 3
            self.max_hp += 15
            self.hp = self.max_hp  # Full heal
            self.attack_power += 3
            self.sound_manager.play_sound('level_up')
    
    def render(self, screen):
        """Render player"""
        # Player color with damage flash
        color = GREEN
        if self.damage_flash_timer > 0:
            flash_intensity = self.damage_flash_timer / 0.3
            color = (min(255, int(GREEN[0] + 255 * flash_intensity)),
                    GREEN[1], GREEN[2])
        
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        
        # Attack range indicator (subtle)
        if self.attack_cooldown <= 0:
            pygame.draw.circle(screen, (0, 255, 0, 30), 
                             (int(self.x), int(self.y)), 60, 1)
