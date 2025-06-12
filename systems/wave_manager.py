from settings import *
from entities.enemies import *
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
        """Start a new wave"""
        self.current_wave = wave_number
        self.enemies_to_spawn = self.generate_wave_enemies(wave_number)
        self.spawn_timer = 0
        self.wave_complete = False
    
    def generate_wave_enemies(self, wave_number):
        """Generate enemy composition for wave"""
        enemies = []
        
        # Base crawlers
        crawler_count = 3 + wave_number
        enemies.extend(["crawler"] * crawler_count)
        
        # Add brutes after wave 2
        if wave_number >= 2:
            brute_count = max(1, wave_number // 2)
            enemies.extend(["brute"] * brute_count)
        
        random.shuffle(enemies)
        return enemies
    
    def update(self, dt, active_enemies):
        """Update wave spawning"""
        self.handle_spawning(dt, active_enemies)
        return self.check_wave_completion(active_enemies)
    
    def handle_spawning(self, dt, active_enemies):
        """Handle enemy spawning"""
        if self.enemies_to_spawn:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                enemy_type = self.enemies_to_spawn.pop()
                self.spawn_enemy(enemy_type, active_enemies)
                self.spawn_timer = random.uniform(0.8, 2.0)
    
    def check_wave_completion(self, active_enemies):
        """Check if wave is complete"""
        if not self.enemies_to_spawn and not active_enemies:
            if not self.wave_complete:
                self.wave_complete = True
                self.sound_manager.play_sound('wave_complete')
                return True
        return False
    
    def spawn_enemy(self, enemy_type, active_enemies):
        """Spawn enemy at screen edge"""
        # Choose random edge
        side = random.randint(0, 3)
        positions = [
            (random.randint(0, SCREEN_WIDTH), -20),  # Top
            (SCREEN_WIDTH + 20, random.randint(0, SCREEN_HEIGHT)),  # Right
            (random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 20),  # Bottom
            (-20, random.randint(0, SCREEN_HEIGHT))  # Left
        ]
        
        x, y = positions[side]
        enemy = Enemy(x, y, enemy_type)
        
        # Scale with wave difficulty
        scale_factor = 1 + (self.current_wave - 1) * 0.2
        enemy.hp = int(enemy.hp * scale_factor)
        enemy.max_hp = enemy.hp
        enemy.attack_power = int(enemy.attack_power * (1 + (self.current_wave - 1) * 0.1))
        
        active_enemies.append(enemy)
