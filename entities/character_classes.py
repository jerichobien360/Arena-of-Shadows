from settings import *
import pygame
import math
import random

class CharacterClass:
    """Base class for all character classes"""
    def __init__(self, name, description):
        self.name = name
        self.description = description
        
        # Base stats (these will be applied to player)
        self.base_hp = 100
        self.base_attack = 25
        self.base_speed = 200
        self.base_defense = 0
        
        # Class-specific modifiers
        self.hp_modifier = 1.0
        self.attack_modifier = 1.0
        self.speed_modifier = 1.0
        self.defense_modifier = 1.0
        
        # Special abilities
        self.abilities = []
        self.passive_abilities = []
        
        # Visual properties
        self.color = (0, 255, 0)  # Default green
        self.secondary_color = (255, 255, 255)
        self.size_modifier = 1.0
        
    def get_modified_stats(self, base_stats):
        """Apply class modifiers to base stats"""
        return {
            'hp': int(base_stats['hp'] * self.hp_modifier),
            'max_hp': int(base_stats['max_hp'] * self.hp_modifier),
            'attack_power': int(base_stats['attack_power'] * self.attack_modifier),
            'speed': int(base_stats['speed'] * self.speed_modifier),
            'defense': int(base_stats.get('defense', 0) * self.defense_modifier)
        }
    
    def on_attack(self, player, enemies):
        """Called when player attacks - override for class-specific behavior"""
        return self.basic_attack(player, enemies)
    
    def basic_attack(self, player, enemies):
        """Basic attack implementation"""
        hit_count = 0
        attack_range = 60
        
        for enemy in enemies[:]:
            distance = math.sqrt((enemy.x - player.x)**2 + (enemy.y - player.y)**2)
            if distance <= attack_range:
                damage = player.attack_power + random.randint(-3, 3)
                enemy_died = enemy.take_damage(damage)
                
                if enemy_died:
                    player.sound_manager.play_sound('enemy_death')
                    player.add_experience(enemy.exp_value)
                else:
                    player.sound_manager.play_sound('enemy_hit')
                    self.apply_knockback(player, enemy, distance)
                
                hit_count += 1
        
        return hit_count
    
    def apply_knockback(self, player, enemy, distance):
        """Apply knockback to enemy"""
        if distance > 0:
            knockback_force = 80
            dx = (enemy.x - player.x) / distance
            dy = (enemy.y - player.y) / distance
            
            new_x = enemy.x + dx * knockback_force
            new_y = enemy.y + dy * knockback_force
            
            enemy.x = max(enemy.radius, min(SCREEN_WIDTH - enemy.radius, new_x))
            enemy.y = max(enemy.radius, min(SCREEN_HEIGHT - enemy.radius, new_y))
            enemy.rect.center = (enemy.x, enemy.y)
    
    def on_level_up(self, player):
        """Called when player levels up - override for class bonuses"""
        pass
    
    def update(self, player, dt):
        """Update class-specific logic"""
        pass
    
    def render_effects(self, screen, player):
        """Render class-specific visual effects"""
        pass

class Warrior(CharacterClass):
    """Tanky melee fighter with high HP and defense"""
    def __init__(self):
        super().__init__("Warrior", "A mighty warrior with high health and strong melee attacks")
        
        # Stat modifiers
        self.hp_modifier = 1.5  # 50% more HP
        self.attack_modifier = 1.2  # 20% more attack
        self.speed_modifier = 0.8  # 20% slower
        self.defense_modifier = 2.0  # Double defense
        
        # Visual properties
        self.color = (200, 50, 50)  # Red
        self.secondary_color = (150, 150, 150)  # Gray
        self.size_modifier = 1.2
        
        # Warrior abilities
        self.charge_cooldown = 0
        self.berserker_mode = False
        self.berserker_timer = 0
        self.shield_bash_cooldown = 0
        
    def on_attack(self, player, enemies):
        """Warrior's powerful melee attack with chance for cleave"""
        hit_count = 0
        attack_range = 70  # Slightly larger range
        cleave_chance = 0.3  # 30% chance to hit multiple enemies
        
        primary_targets = []
        secondary_targets = []
        
        for enemy in enemies[:]:
            distance = math.sqrt((enemy.x - player.x)**2 + (enemy.y - player.y)**2)
            if distance <= attack_range:
                primary_targets.append((enemy, distance))
            elif distance <= attack_range * 1.5 and random.random() < cleave_chance:
                secondary_targets.append((enemy, distance))
        
        # Hit primary targets with full damage
        for enemy, distance in primary_targets:
            damage = int(player.attack_power * 1.1) + random.randint(-2, 5)  # 10% more damage
            enemy_died = enemy.take_damage(damage)
            
            if enemy_died:
                player.sound_manager.play_sound('enemy_death')
                player.add_experience(enemy.exp_value)
            else:
                player.sound_manager.play_sound('enemy_hit')
                self.apply_knockback(player, enemy, distance)
            
            hit_count += 1
        
        # Hit secondary targets with reduced damage (cleave)
        for enemy, distance in secondary_targets:
            damage = int(player.attack_power * 0.6) + random.randint(-1, 2)
            enemy_died = enemy.take_damage(damage)
            
            if enemy_died:
                player.sound_manager.play_sound('enemy_death')
                player.add_experience(enemy.exp_value)
            else:
                player.sound_manager.play_sound('enemy_hit')
            
            hit_count += 1
        
        return hit_count
    
    def on_level_up(self, player):
        """Warrior gets extra HP and attack on level up"""
        player.max_hp += 5  # Extra HP bonus
        player.attack_power += 2  # Extra attack bonus
        player.hp = player.max_hp  # Full heal
    
    def update(self, player, dt):
        """Update warrior abilities"""
        self.charge_cooldown = max(0, self.charge_cooldown - dt)
        self.shield_bash_cooldown = max(0, self.shield_bash_cooldown - dt)
        
        if self.berserker_mode:
            self.berserker_timer -= dt
            if self.berserker_timer <= 0:
                self.berserker_mode = False
                player.attack_power = int(player.attack_power / 1.5)  # Remove berserker bonus
    
    def render_effects(self, screen, player):
        """Render warrior effects"""
        # Render shield outline
        pygame.draw.circle(screen, self.secondary_color, (int(player.x), int(player.y)), 
                          int(player.radius * 1.3), 2)
        
        # Berserker mode effect
        if self.berserker_mode:
            pygame.draw.circle(screen, (255, 0, 0), (int(player.x), int(player.y)), 
                             int(player.radius * 1.5), 3)

class Mage(CharacterClass):
    """Magical ranged fighter with spell casting abilities"""
    def __init__(self):
        super().__init__("Mage", "A powerful spellcaster with magical projectiles and area spells")
        
        # Stat modifiers
        self.hp_modifier = 0.7  # 30% less HP
        self.attack_modifier = 1.4  # 40% more attack (magical power)
        self.speed_modifier = 0.9  # 10% slower
        self.defense_modifier = 0.5  # Half defense
        
        # Visual properties
        self.color = (50, 50, 200)  # Blue
        self.secondary_color = (150, 150, 255)  # Light blue
        self.size_modifier = 0.9
        
        # Mage abilities
        self.mana = 100
        self.max_mana = 100
        self.mana_regen = 20  # per second
        self.projectiles = []
        self.spell_cooldown = 0
        
    def on_attack(self, player, enemies):
        """Mage's ranged magical attack"""
        if self.mana < 10:
            return 0  # Not enough mana
        
        self.mana -= 10
        
        # Find nearest enemy
        nearest_enemy = None
        min_distance = float('inf')
        
        for enemy in enemies:
            distance = math.sqrt((enemy.x - player.x)**2 + (enemy.y - player.y)**2)
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = enemy
        
        if nearest_enemy:
            # Create magic projectile
            projectile = MagicProjectile(player.x, player.y, nearest_enemy.x, nearest_enemy.y, 
                                       player.attack_power, player.sound_manager)
            self.projectiles.append(projectile)
            player.sound_manager.play_sound('attack')
            return 1
        
        return 0
    
    def update(self, player, dt, enemies=None):
        """Update mage abilities with enemy collision"""
        # Regenerate mana
        self.mana = min(self.max_mana, self.mana + self.mana_regen * dt)
        self.spell_cooldown = max(0, self.spell_cooldown - dt)
        
        # Update projectiles with collision detection
        for projectile in self.projectiles[:]:
            projectile.update(dt, enemies)
            if not projectile.active:
                self.projectiles.remove(projectile)
    
    def render_effects(self, screen, player):
        """Render mage effects"""
        # Render magical aura
        pygame.draw.circle(screen, self.secondary_color, (int(player.x), int(player.y)), 
                          int(player.radius * 1.2), 1)
        
        # Render projectiles
        for projectile in self.projectiles:
            projectile.render(screen)
        
        # Render mana bar
        mana_ratio = self.mana / self.max_mana
        bar_width = 60
        bar_height = 8
        bar_x = int(player.x - bar_width // 2)
        bar_y = int(player.y - player.radius - 15)
        
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (50, 50, 200), (bar_x, bar_y, int(bar_width * mana_ratio), bar_height))

class Fireshooter(CharacterClass):
    """Fast ranged fighter with fire-based attacks"""
    def __init__(self):
        super().__init__("Fireshooter", "A swift archer with flaming arrows and explosive attacks")
        
        # Stat modifiers
        self.hp_modifier = 0.9  # 10% less HP
        self.attack_modifier = 1.1  # 10% more attack
        self.speed_modifier = 1.3  # 30% faster
        self.defense_modifier = 0.8  # 20% less defense
        
        # Visual properties
        self.color = (255, 100, 0)  # Orange
        self.secondary_color = (255, 200, 0)  # Yellow
        self.size_modifier = 1.0
        
        # Fireshooter abilities
        self.fire_arrows = []
        self.rapid_fire_mode = False
        self.rapid_fire_timer = 0
        self.explosion_cooldown = 0
        
    def on_attack(self, player, enemies):
        """Fireshooter's ranged fire attack"""
        if not enemies:
            return 0
        
        # Multi-shot: fire arrows at up to 3 nearest enemies
        sorted_enemies = sorted(enemies, key=lambda e: 
                              math.sqrt((e.x - player.x)**2 + (e.y - player.y)**2))
        
        targets = sorted_enemies[:3]  # Target up to 3 enemies
        hit_count = 0
        
        for target in targets:
            distance = math.sqrt((target.x - player.x)**2 + (target.y - player.y)**2)
            if distance <= 300:  # Long range
                arrow = FireArrow(player.x, player.y, target.x, target.y, 
                                player.attack_power, player.sound_manager)
                self.fire_arrows.append(arrow)
                hit_count += 1
        
        if hit_count > 0:
            player.sound_manager.play_sound('attack')
        
        return hit_count
    
    def update(self, player, dt, enemies=None):
        """Update fireshooter abilities with enemy collision"""
        self.explosion_cooldown = max(0, self.explosion_cooldown - dt)
        
        if self.rapid_fire_mode:
            self.rapid_fire_timer -= dt
            if self.rapid_fire_timer <= 0:
                self.rapid_fire_mode = False
        
        # Update fire arrows with collision detection
        for arrow in self.fire_arrows[:]:
            arrow.update(dt, enemies)
            if not arrow.active:
                self.fire_arrows.remove(arrow)
    
    def render_effects(self, screen, player):
        """Render fireshooter effects"""
        # Render flame aura
        pygame.draw.circle(screen, self.secondary_color, (int(player.x), int(player.y)), 
                          int(player.radius * 1.1), 1)
        
        # Render fire arrows
        for arrow in self.fire_arrows:
            arrow.render(screen)
        
        # Rapid fire mode effect
        if self.rapid_fire_mode:
            pygame.draw.circle(screen, (255, 255, 0), (int(player.x), int(player.y)), 
                             int(player.radius * 1.3), 2)

class MagicProjectile:
    """Enhanced magical projectile for mage with collision detection"""
    def __init__(self, start_x, start_y, target_x, target_y, damage, sound_manager):
        self.x = start_x
        self.y = start_y
        self.damage = damage
        self.sound_manager = sound_manager
        self.speed = 400
        self.active = True
        self.lifetime = 3.0
        self.size = 8
        self.has_hit = False  # Prevent multiple hits
        
        # Calculate direction
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.vel_x = (dx / distance) * self.speed
            self.vel_y = (dy / distance) * self.speed
        else:
            self.vel_x = self.vel_y = 0
    
    def update(self, dt, enemies=None):
        """Update projectile with collision detection"""
        if not self.active:
            return
        
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.lifetime -= dt
        
        # Check collision with enemies
        if enemies and not self.has_hit:
            for enemy in enemies:
                distance = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                if distance <= enemy.radius + self.size:
                    # Hit enemy
                    enemy_died = enemy.take_damage(self.damage)
                    if enemy_died:
                        self.sound_manager.play_sound('enemy_death')
                    else:
                        self.sound_manager.play_sound('enemy_hit')
                    
                    self.has_hit = True
                    self.active = False
                    return
        
        # Check bounds
        if (self.x < 0 or self.x > SCREEN_WIDTH or 
            self.y < 0 or self.y > SCREEN_HEIGHT or 
            self.lifetime <= 0):
            self.active = False
    
    def render(self, screen):
        if self.active:
            # Add particle effect
            pygame.draw.circle(screen, (150, 150, 255), (int(self.x), int(self.y)), self.size)
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.size // 2)
            
            # Add glow effect
            pygame.draw.circle(screen, (100, 100, 200), (int(self.x), int(self.y)), self.size + 2, 1)

class FireArrow:
    """Enhanced fire arrow with collision detection"""
    def __init__(self, start_x, start_y, target_x, target_y, damage, sound_manager):
        self.x = start_x
        self.y = start_y
        self.damage = damage
        self.sound_manager = sound_manager
        self.speed = 500
        self.active = True
        self.lifetime = 2.0
        self.size = 6
        self.has_hit = False
        
        # Calculate direction
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.vel_x = (dx / distance) * self.speed
            self.vel_y = (dy / distance) * self.speed
        else:
            self.vel_x = self.vel_y = 0
        
        # Trail effect
        self.trail_positions = []
    
    def update(self, dt, enemies=None):
        """Update arrow with collision detection"""
        if not self.active:
            return
        
        self.trail_positions.append((self.x, self.y))
        if len(self.trail_positions) > 8:
            self.trail_positions.pop(0)
        
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.lifetime -= dt
        
        # Check collision with enemies
        if enemies and not self.has_hit:
            for enemy in enemies:
                distance = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                if distance <= enemy.radius + self.size:
                    # Hit enemy with fire damage
                    base_damage = self.damage + random.randint(-2, 5)
                    enemy_died = enemy.take_damage(base_damage)
                    
                    # Apply burn effect (if enemy has burn system)
                    if hasattr(enemy, 'apply_burn'):
                        enemy.apply_burn(self.damage // 4, 3.0)  # Burn for 3 seconds
                    
                    if enemy_died:
                        self.sound_manager.play_sound('enemy_death')
                    else:
                        self.sound_manager.play_sound('enemy_hit')
                    
                    self.has_hit = True
                    self.active = False
                    return
        
        # Check bounds
        if (self.x < 0 or self.x > SCREEN_WIDTH or 
            self.y < 0 or self.y > SCREEN_HEIGHT or 
            self.lifetime <= 0):
            self.active = False
    
    def render(self, screen):
        if self.active:
            # Render trail
            for i, (tx, ty) in enumerate(self.trail_positions):
                alpha = i / len(self.trail_positions)
                size = int(self.size * alpha)
                if size > 0:
                    color = (255, int(100 + 155 * alpha), 0)
                    pygame.draw.circle(screen, color, (int(tx), int(ty)), size)
            
            # Render main arrow
            pygame.draw.circle(screen, (255, 200, 0), (int(self.x), int(self.y)), self.size)
            pygame.draw.circle(screen, (255, 100, 0), (int(self.x), int(self.y)), self.size // 2)

# Class registry for easy access
CHARACTER_CLASSES = {
    'warrior': Warrior(),
    'mage': Mage(),
    'fireshooter': Fireshooter()
}
