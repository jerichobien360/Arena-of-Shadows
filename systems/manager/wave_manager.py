from settings import *
from src.entities.enemies import *
from src.entities.player import *
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
        self.enemies_to_spawn = self.generate_wave_enemies(wave_number)
        self.spawn_timer = 0
        self.wave_complete = False
   
    def generate_wave_enemies(self, wave_number):
        """Generate smart enemy composition for wave"""
        enemies = []
       
        # Base crawlers (always present)
        crawler_count = 2 + wave_number
        enemies.extend(["crawler"] * crawler_count)
       
        # Add brutes after wave 2
        if wave_number >= 2:
            brute_count = max(1, wave_number // 3)
            enemies.extend(["brute"] * brute_count)
        
        # Add snipers after wave 3 (fewer but dangerous)
        if wave_number >= 3:
            sniper_count = max(1, wave_number // 4)
            enemies.extend(["sniper"] * sniper_count)
        
        # Add fireshooters after wave 4 (medium frequency)
        if wave_number >= 4:
            fire_count = max(1, wave_number // 3)
            enemies.extend(["fireshooter"] * fire_count)
        
        # Special wave compositions
        if wave_number % 5 == 0:  # Boss waves every 5 waves
            enemies.extend(["sniper"] * 2)  # Extra snipers for challenge
            enemies.extend(["brute"] * 2)   # Extra brutes for pressure
        
        random.shuffle(enemies)
        return enemies
   
    def update(self, dt, active_enemies):
        """Update wave spawning with smart timing"""
        self.handle_spawning(dt, active_enemies)
        return self.check_wave_completion(active_enemies)
   
    def handle_spawning(self, dt, active_enemies):
        """Handle enemy spawning with adaptive timing"""
        if self.enemies_to_spawn:
            self.spawn_timer -= dt
            
            # Dynamic spawn timing based on active enemies
            base_spawn_delay = 1.2
            enemy_pressure = len(active_enemies) / max(1, self.current_wave * 2)
            spawn_delay = base_spawn_delay * (1 + enemy_pressure * 0.5)
            
            if self.spawn_timer <= 0:
                enemy_type = self.enemies_to_spawn.pop()
                self.spawn_enemy(enemy_type, active_enemies)
                self.spawn_timer = random.uniform(spawn_delay * 0.8, spawn_delay * 1.2)
   
    def check_wave_completion(self, active_enemies):
        """Check if wave is complete - ignore dying enemies"""
        living_enemies = [e for e in active_enemies if not getattr(e, 'is_dying', False)]
        
        if not self.enemies_to_spawn and not living_enemies:
            if not self.wave_complete:
                self.wave_complete = True
                self.sound_manager.play_sound('wave_complete')
                return True
        return False
   
    def spawn_enemy(self, enemy_type, active_enemies):
        """Smart enemy spawning based on type"""
        # Smart positioning for different enemy types
        if enemy_type in ["sniper", "fireshooter"]:
            # Ranged enemies spawn further from screen center
            x, y = self.get_ranged_spawn_position()
        else:
            # Melee enemies use standard edge spawning
            x, y = self.get_standard_spawn_position()
        
        enemy = Enemy(x, y, enemy_type)
       
        # Scale with wave difficulty
        difficulty_scale = 1 + (self.current_wave - 1) * 0.15
        enemy.hp = int(enemy.hp * difficulty_scale)
        enemy.max_hp = enemy.hp
        enemy.attack_power = int(enemy.attack_power * (1 + (self.current_wave - 1) * 0.1))
       
        active_enemies.append(enemy)
    
    def get_standard_spawn_position(self):
        """Standard edge spawning for melee enemies"""
        side = random.randint(0, 3)
        positions = [
            (random.randint(0, SCREEN_WIDTH), -20),  # Top
            (SCREEN_WIDTH + 20, random.randint(0, SCREEN_HEIGHT)),  # Right
            (random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 20),  # Bottom
            (-20, random.randint(0, SCREEN_HEIGHT))  # Left
        ]
        return positions[side]
    
    def get_ranged_spawn_position(self):
        """Smart spawning for ranged enemies - corners and distance"""
        spawn_options = [
            # Corner positions for better sniping angles
            (-30, -30), (SCREEN_WIDTH + 30, -30),
            (-30, SCREEN_HEIGHT + 30), (SCREEN_WIDTH + 30, SCREEN_HEIGHT + 30),
            # Far edge positions
            (SCREEN_WIDTH // 2, -40), (-40, SCREEN_HEIGHT // 2),
            (SCREEN_WIDTH + 40, SCREEN_HEIGHT // 2), (SCREEN_WIDTH // 2, SCREEN_HEIGHT + 40)
        ]
        return random.choice(spawn_options)
