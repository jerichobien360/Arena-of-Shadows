from settings import *
from entities.enemy.enemy_base import *
from entities.enemy.enemy_types import *
from entities.player import *
import pygame, math, random

class WaveManager:
    def __init__(self, sound_manager):
        self.sound_manager = sound_manager
        self.current_wave = 0
        self.enemies_to_spawn = []
        self.spawn_timer = 0
        self.wave_complete = False
   
    def start_wave(self, wave_number):
        """Start a new wave with progressive difficulty"""
        self.current_wave = wave_number
        self.enemies_to_spawn = self._generate_wave_enemies(wave_number)
        self.spawn_timer = 0
        self.wave_complete = False
   
    def _generate_wave_enemies(self, wave):
        """Generate enemy composition using dictionary-based scaling"""
        enemy_config = {
            "crawler": {"base": 2, "scale": 1, "min_wave": 1},
            "brute": {"base": 0, "scale": 1/3, "min_wave": 2},
            "sniper": {"base": 0, "scale": 1/4, "min_wave": 3},
            "fireshooter": {"base": 0, "scale": 1/3, "min_wave": 4},
            "shadow_assassin": {"base": 0, "scale": 1/6, "min_wave": 6}
        }
        
        enemies = []
        
        # Generate base enemies
        for enemy_type, config in enemy_config.items():
            if wave >= config["min_wave"]:
                count = max(config["base"], int(wave * config["scale"]))
                enemies.extend([enemy_type] * count)
        
        # Boss wave multipliers
        boss_multipliers = {5: 2, 10: 3, 12: 2}
        if wave % 5 == 0 or wave in boss_multipliers:
            multiplier = boss_multipliers.get(wave % 10, 2)
            if wave >= 3:
                enemies.extend(["sniper"] * multiplier)
            if wave >= 2:
                enemies.extend(["brute"] * multiplier)
            if wave >= 10:
                enemies.extend(["shadow_assassin"] * (multiplier - 1))
        
        random.shuffle(enemies)
        return enemies
   
    def update(self, dt, active_enemies):
        """Update wave spawning and check completion"""
        self._handle_spawning(dt, active_enemies)
        return self._check_completion(active_enemies)
   
    def _handle_spawning(self, dt, active_enemies):
        """Handle enemy spawning with adaptive timing"""
        if not self.enemies_to_spawn:
            return
            
        self.spawn_timer -= dt
        
        # Dynamic spawn timing
        enemy_pressure = len(active_enemies) / max(1, self.current_wave * 2)
        base_delay = 1.2 * (1 + enemy_pressure * 0.5)
        
        # Faster spawn for assassins
        if self.enemies_to_spawn[-1] == "shadow_assassin":
            base_delay *= 0.8
        
        if self.spawn_timer <= 0:
            enemy_type = self.enemies_to_spawn.pop()
            self._spawn_enemy(enemy_type, active_enemies)
            
            # Variable timing based on enemy type
            timing_factor = 0.6 if enemy_type == "shadow_assassin" else 0.8
            self.spawn_timer = random.uniform(base_delay * timing_factor, base_delay * 1.2)
   
    def _check_completion(self, active_enemies):
        """Check if wave is complete"""
        living_enemies = [e for e in active_enemies if not getattr(e, 'is_dying', False)]
        
        if not self.enemies_to_spawn and not living_enemies and not self.wave_complete:
            self.wave_complete = True
            self.sound_manager.play_sound('wave_complete')
            return True
        return False
   
    def _spawn_enemy(self, enemy_type, active_enemies):
        """Spawn enemy with appropriate positioning and scaling"""
        # Get spawn position based on enemy type
        spawn_pos = (self._get_stealth_position() if enemy_type == "shadow_assassin" 
                    else self._get_ranged_position() if enemy_type in ["sniper", "fireshooter"]
                    else self._get_standard_position())
        
        # Create enemy
        enemy = (ShadowAssassin(*spawn_pos) if enemy_type == "shadow_assassin" 
                else Enemy(*spawn_pos, enemy_type))
        
        # Apply difficulty scaling
        self._apply_scaling(enemy, enemy_type)
        active_enemies.append(enemy)
    
    def _get_standard_position(self):
        """Standard edge spawning"""
        positions = [
            (random.randint(0, SCREEN_WIDTH), -20),
            (SCREEN_WIDTH + 20, random.randint(0, SCREEN_HEIGHT)),
            (random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 20),
            (-20, random.randint(0, SCREEN_HEIGHT))
        ]
        return random.choice(positions)
    
    def _get_ranged_position(self):
        """Corner and far edge positions for ranged enemies"""
        positions = [
            (-30, -30), (SCREEN_WIDTH + 30, -30),
            (-30, SCREEN_HEIGHT + 30), (SCREEN_WIDTH + 30, SCREEN_HEIGHT + 30),
            (SCREEN_WIDTH // 2, -40), (-40, SCREEN_HEIGHT // 2),
            (SCREEN_WIDTH + 40, SCREEN_HEIGHT // 2), (SCREEN_WIDTH // 2, SCREEN_HEIGHT + 40)
        ]
        return random.choice(positions)
    
    def _get_stealth_position(self):
        """Strategic positions for stealth enemies"""
        positions = [
            (SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.1), (SCREEN_WIDTH * 0.9, SCREEN_HEIGHT * 0.1),
            (SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.9), (SCREEN_WIDTH * 0.9, SCREEN_HEIGHT * 0.9),
            (-30, SCREEN_HEIGHT * 0.3), (-30, SCREEN_HEIGHT * 0.7),
            (SCREEN_WIDTH + 30, SCREEN_HEIGHT * 0.3), (SCREEN_WIDTH + 30, SCREEN_HEIGHT * 0.7),
            (SCREEN_WIDTH * 0.3, -30), (SCREEN_WIDTH * 0.7, -30),
            (SCREEN_WIDTH * 0.3, SCREEN_HEIGHT + 30), (SCREEN_WIDTH * 0.7, SCREEN_HEIGHT + 30)
        ]
        return random.choice(positions)
    
    def _apply_scaling(self, enemy, enemy_type):
        """Apply difficulty scaling to enemy stats"""
        if enemy_type == "shadow_assassin":
            # Minimal scaling for assassins
            if self.current_wave >= 10:
                scale = 1 + (self.current_wave - 10) * 0.05
                enemy.hp = int(enemy.hp * scale)
                enemy.max_hp = enemy.hp
        else:
            # Standard scaling for other enemies
            hp_scale = 1 + (self.current_wave - 1) * 0.15
            attack_scale = 1 + (self.current_wave - 1) * 0.1
            enemy.hp = int(enemy.hp * hp_scale)
            enemy.max_hp = enemy.hp
            enemy.attack_power = int(enemy.attack_power * attack_scale)
    
    def get_wave_info(self, wave_number):
        """Get wave difficulty information"""
        enemies = self._generate_wave_enemies(wave_number)
        enemy_counts = {enemy: enemies.count(enemy) for enemy in set(enemies)}
        
        enemy_icons = {
            "shadow_assassin": "⚔️", "sniper": "🎯", "fireshooter": "🔥",
            "brute": "💪", "crawler": "🏃"
        }
        
        indicators = [f"{enemy_icons.get(enemy, '🔸')} {enemy.title()}s: {count}" 
                     for enemy, count in enemy_counts.items()]
        
        return {
            "total_enemies": len(enemies),
            "enemy_counts": enemy_counts,
            "difficulty_indicators": indicators,
            "has_stealth": "shadow_assassin" in enemy_counts,
            "is_boss_wave": wave_number % 5 == 0
        }
