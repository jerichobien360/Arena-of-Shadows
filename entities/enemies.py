from settings import *
import pygame, math, random


class Enemy:
    def __init__(self, x, y, enemy_type="crawler"):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.damage_flash_timer = 0
        self.attack_cooldown = 0
        self.setup_enemy_stats()
        self.rect = pygame.Rect(x - self.radius, y - self.radius, 
                               self.radius * 2, self.radius * 2)
    
    def setup_enemy_stats(self):
        """Setup enemy stats based on type"""
        if self.type == "crawler":
            self.hp = self.max_hp = 40
            self.attack_power = 15
            self.speed = 120
            self.radius = 12
            self.color = RED
            self.exp_value = 25
        elif self.type == "brute":
            self.hp = self.max_hp = 100
            self.attack_power = 30
            self.speed = 80
            self.radius = 18
            self.color = (180, 0, 0)
            self.exp_value = 60
    
    def update(self, dt, player):
        """Update enemy state"""
        self.chase_player(dt, player)
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        self.damage_flash_timer = max(0, self.damage_flash_timer - dt)
        self.rect.center = (self.x, self.y)
    
    def chase_player(self, dt, player):
        """Chase and attack player"""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            dx /= distance
            dy /= distance
            
            if distance > 25:  # Chase
                self.x += dx * self.speed * dt
                self.y += dy * self.speed * dt
            elif self.attack_cooldown <= 0:  # Attack
                player.take_damage(self.attack_power)
                self.attack_cooldown = 1.2
    
    def take_damage(self, amount):
        """Take damage and return if enemy died"""
        self.hp -= amount
        self.damage_flash_timer = 0.25
        return self.hp <= 0
    
    def render(self, screen):
        """Render enemy"""
        # Enemy body with damage flash
        color = self.color
        if self.damage_flash_timer > 0:
            flash_intensity = self.damage_flash_timer / 0.25
            color = tuple(min(255, c + int(200 * flash_intensity)) for c in self.color)
        
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        
        # Health bar
        if self.hp < self.max_hp:
            self.draw_health_bar(screen)
    
    def draw_health_bar(self, screen):
        """Draw enemy health bar"""
        bar_width, bar_height = 25, 3
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.radius - 8
        
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = (self.hp / self.max_hp) * bar_width
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))
