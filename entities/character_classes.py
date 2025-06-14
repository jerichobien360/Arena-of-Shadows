from settings import *
import pygame
import math
import random


class BaseCharacterClass:
    """Base class for all character types with common attributes and methods"""
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.color = WHITE
        self.secondary_color = GRAY
        
        # Base stats that will be modified by each class
        self.base_hp = 100
        self.base_attack_power = 25
        self.base_speed = 200
        self.base_attack_range = 60
        self.base_attack_cooldown = 0.5
        
        # Special abilities
        self.special_ability_cooldown = 3.0
        self.special_ability_name = "Basic Attack"
        
    def apply_stats(self, player):
        """Apply this class's stats to a player instance"""
        player.max_hp = self.base_hp
        player.hp = self.base_hp
        player.attack_power = self.base_attack_power
        player.speed = self.base_speed
        player.attack_range = self.base_attack_range
        player.base_attack_cooldown = self.base_attack_cooldown
        player.character_class = self
        player.special_cooldown = 0
        
    def special_attack(self, player, enemies):
        """Override in subclasses for unique special abilities"""
        return player.attack(enemies)
        
    def render_special_effects(self, screen, player):
        """Override in subclasses for visual effects"""
        pass


class Warrior(BaseCharacterClass):
    """Tank class with high HP and melee focus"""
    
    def __init__(self):
        super().__init__("Warrior", "High HP tank with powerful melee attacks")
        self.color = (200, 50, 50)  # Red
        self.secondary_color = (150, 30, 30)
        
        # Warrior stats - high HP, moderate attack, slow but steady
        self.base_hp = 150
        self.base_attack_power = 35
        self.base_speed = 180
        self.base_attack_range = 70
        self.base_attack_cooldown = 0.4
        
        self.special_ability_name = "Whirlwind Strike"
        self.special_ability_cooldown = 4.0
        
    def special_attack(self, player, enemies):
        """Whirlwind attack that hits all nearby enemies"""
        if player.special_cooldown > 0:
            return 0
            
        player.special_cooldown = self.special_ability_cooldown
        player.sound_manager.play_sound('attack')
        
        hit_count = 0
        whirlwind_range = 100  # Larger range than normal attack
        
        for enemy in enemies[:]:
            distance = math.hypot(enemy.x - player.x, enemy.y - player.y)
            if distance <= whirlwind_range:
                damage = player.attack_power * 1.5 + random.randint(-5, 5)
                if enemy.take_damage(int(damage)):
                    player.sound_manager.play_sound('enemy_death')
                    player.add_experience(enemy.exp_value)
                else:
                    player.sound_manager.play_sound('enemy_hit')
                    # Stronger knockback for whirlwind
                    if distance > 0:
                        knockback = 120 / distance
                        enemy.x = max(enemy.radius, min(SCREEN_WIDTH - enemy.radius, 
                                     enemy.x + (enemy.x - player.x) * knockback))
                        enemy.y = max(enemy.radius, min(SCREEN_HEIGHT - enemy.radius, 
                                     enemy.y + (enemy.y - player.y) * knockback))
                        enemy.rect.center = (enemy.x, enemy.y)
                hit_count += 1
                
        return hit_count
        
    def render_special_effects(self, screen, player):
        """Render whirlwind effect during special attack"""
        if player.special_cooldown > self.special_ability_cooldown - 0.5:
            # Draw spinning effect
            angle_offset = (self.special_ability_cooldown - player.special_cooldown) * 20
            for i in range(6):
                angle = (i * 60 + angle_offset) * math.pi / 180
                end_x = player.x + math.cos(angle) * 80
                end_y = player.y + math.sin(angle) * 80
                pygame.draw.line(screen, self.color, (int(player.x), int(player.y)), 
                               (int(end_x), int(end_y)), 3)


class Mage(BaseCharacterClass):
    """Ranged spellcaster with magical projectiles"""
    
    def __init__(self):
        super().__init__("Mage", "Ranged spellcaster with magical projectiles")
        self.color = (50, 50, 200)  # Blue
        self.secondary_color = (30, 30, 150)
        
        # Mage stats - low HP, high attack, fast casting
        self.base_hp = 80
        self.base_attack_power = 30
        self.base_speed = 220
        self.base_attack_range = 120  # Longer range
        self.base_attack_cooldown = 0.3
        
        self.special_ability_name = "Magic Missile"
        self.special_ability_cooldown = 2.5
        
    def special_attack(self, player, enemies):
        """Launch homing magic missiles"""
        if player.special_cooldown > 0 or not enemies:
            return 0
            
        player.special_cooldown = self.special_ability_cooldown
        player.sound_manager.play_sound('attack')
        
        # Create magic missiles for up to 3 nearest enemies
        targets = sorted(enemies, key=lambda e: math.hypot(e.x - player.x, e.y - player.y))[:3]
        
        if not hasattr(player, 'magic_missiles'):
            player.magic_missiles = []
            
        for target in targets:
            missile = MagicMissile(player.x, player.y, target, player.attack_power * 1.2)
            player.magic_missiles.append(missile)
            
        return len(targets)


class FireShooter(BaseCharacterClass):
    """Rapid-fire ranged attacker with fire-based abilities"""
    
    def __init__(self):
        super().__init__("Fire Shooter", "Rapid-fire attacker with burning projectiles")
        self.color = (255, 100, 0)  # Orange
        self.secondary_color = (200, 50, 0)
        
        # Fire Shooter stats - balanced HP, rapid fire
        self.base_hp = 110
        self.base_attack_power = 20
        self.base_speed = 210
        self.base_attack_range = 100
        self.base_attack_cooldown = 0.2  # Very fast attacks
        
        self.special_ability_name = "Fire Storm"
        self.special_ability_cooldown = 3.5
        
    def special_attack(self, player, enemies):
        """Create a storm of fire projectiles"""
        if player.special_cooldown > 0:
            return 0
            
        player.special_cooldown = self.special_ability_cooldown
        player.sound_manager.play_sound('attack')
        
        if not hasattr(player, 'fire_projectiles'):
            player.fire_projectiles = []
            
        # Create 8 fire projectiles in all directions
        for i in range(8):
            angle = (i * 45) * math.pi / 180
            direction = (math.cos(angle), math.sin(angle))
            projectile = FireProjectile(player.x, player.y, direction, player.attack_power * 0.8)
            player.fire_projectiles.append(projectile)
            
        return 1  # Visual feedback


class MagicMissile:
    """Homing projectile for Mage special ability"""
    
    def __init__(self, x, y, target, damage):
        self.x, self.y = x, y
        self.target = target
        self.damage = damage
        self.speed = 300
        self.lifetime = 3.0
        self.trail = []
        
    def update(self, dt):
        """Update missile position and homing behavior"""
        self.lifetime -= dt
        if self.lifetime <= 0:
            return False
            
        # Calculate direction to target
        if self.target.hp > 0:  # Target still alive
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = math.hypot(dx, dy)
            
            if distance < 20:  # Hit target
                self.target.take_damage(int(self.damage))
                return False
                
            # Move towards target
            if distance > 0:
                self.x += (dx / distance) * self.speed * dt
                self.y += (dy / distance) * self.speed * dt
        
        # Add to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)
            
        return True
        
    def render(self, screen):
        """Render missile with magical trail"""
        # Draw trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            if alpha > 0:
                trail_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(trail_surf, (100, 100, 255, alpha), (3, 3), 3)
                screen.blit(trail_surf, (int(tx - 3), int(ty - 3)))
        
        # Draw missile
        pygame.draw.circle(screen, (150, 150, 255), (int(self.x), int(self.y)), 4)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 2)


class FireProjectile:
    """Fire projectile for Fire Shooter special ability"""
    
    def __init__(self, x, y, direction, damage):
        self.x, self.y = x, y
        self.direction = direction
        self.damage = damage
        self.speed = 250
        self.lifetime = 2.0
        self.size = 6
        
    def update(self, dt, enemies):
        """Update projectile and check for collisions"""
        self.lifetime -= dt
        if self.lifetime <= 0:
            return False
            
        # Move projectile
        self.x += self.direction[0] * self.speed * dt
        self.y += self.direction[1] * self.speed * dt
        
        # Check bounds
        if (self.x < 0 or self.x > SCREEN_WIDTH or 
            self.y < 0 or self.y > SCREEN_HEIGHT):
            return False
            
        # Check enemy collisions
        for enemy in enemies:
            distance = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if distance < enemy.radius + self.size:
                enemy.take_damage(int(self.damage))
                return False
                
        return True
        
    def render(self, screen):
        """Render fire projectile with flame effect"""
        # Outer flame
        pygame.draw.circle(screen, (255, 100, 0), (int(self.x), int(self.y)), self.size)
        # Inner flame
        pygame.draw.circle(screen, (255, 200, 0), (int(self.x), int(self.y)), self.size - 2)
        # Core
        pygame.draw.circle(screen, (255, 255, 200), (int(self.x), int(self.y)), self.size - 4)



# Global registry of available character classes
CHARACTER_CLASSES = {
    'warrior': Warrior(),
    'mage': Mage(),
    'fireshooter': FireShooter()
}
