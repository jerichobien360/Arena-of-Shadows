"""Core gameplay logic with clean architecture and optimized combat systems."""

import math
import pygame
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any

from settings import *
from entities.player import *
from entities.enemies import *
from systems.manager.wave_manager import *
from systems.game_feature.camera import *
from systems.game_feature.background_system import *


@dataclass
class FormationSystem:
    """Optimized formation system for enemy combat coordination."""
    cooldown: float = 0.0
    min_enemies: int = 6
    proximity_threshold: int = 14400  # 120^2 for distance check
    
    def should_form(self, enemies: List, player) -> bool:
        """Check if enemies should form a tactical formation."""
        if len(enemies) < self.min_enemies or self.cooldown > 0:
            return False
        
        # Fast proximity clustering using generator expression
        close_pairs = sum(
            1 for i, e1 in enumerate(enemies[:12])
            for e2 in enemies[i+1:i+6]
            if self._distance_squared(e1, e2) < self.proximity_threshold
        )
        
        return close_pairs >= len(enemies) // 3
    
    def create_formation(self, enemies: List, player) -> None:
        """Create tactical formation based on enemy count."""
        if not enemies:
            return
            
        positions = self._get_formation_positions(len(enemies), player)
        
        for enemy, pos in zip(enemies, positions):
            enemy.form_target = pos
            enemy.form_active = True
        
        self.cooldown = 3.0
    
    def update(self, dt: float, enemies: List, player) -> None:
        """Update formation system and manage enemy coordination."""
        self.cooldown = max(0, self.cooldown - dt)
        
        # Clean up formations from dead enemies
        active_enemies = [e for e in enemies if getattr(e, 'form_active', False) and e.hp > 0]
        if len(active_enemies) < 3:
            for enemy in active_enemies:
                enemy.form_active = False
        
        # Check for new formations
        inactive_enemies = [e for e in enemies if not getattr(e, 'form_active', False)]
        if self.should_form(inactive_enemies, player):
            self.create_formation(inactive_enemies, player)
    
    def _distance_squared(self, e1, e2) -> float:
        """Calculate squared distance between two enemies."""
        return (e1.x - e2.x)**2 + (e1.y - e2.y)**2
    
    def _get_formation_positions(self, count: int, player) -> List[Tuple[float, float]]:
        """Generate formation positions based on enemy count."""
        if count <= 8:
            # Circle formation
            return [
                (player.x + 100 * math.cos(2 * math.pi * i / count),
                 player.y + 100 * math.sin(2 * math.pi * i / count))
                for i in range(count)
            ]
        
        # Pincer formation for larger groups
        half = count // 2
        left_flank = [(player.x - 140, player.y + (i - half//2) * 35) for i in range(half)]
        right_flank = [(player.x + 140, player.y + (i - half//2) * 35) for i in range(count - half)]
        return left_flank + right_flank


@dataclass
class InputHandler:
    """Clean input handling with state tracking."""
    prev_keys: set = field(default_factory=set)
    curr_keys: set = field(default_factory=set)
    
    def update(self) -> None:
        """Update key states for frame-based input detection."""
        self.prev_keys = self.curr_keys.copy()
        pressed = pygame.key.get_pressed()
        self.curr_keys = {i for i, key in enumerate(pressed) if key}
    
    def is_key_just_pressed(self, key: int) -> bool:
        """Check if key was just pressed this frame."""
        return key in self.curr_keys and key not in self.prev_keys


class GameplayCore:
    """Core gameplay logic with clean separation of concerns."""
    
    def __init__(self, sound_manager):
        self.sound_manager = sound_manager
        
        # Game entities
        self.player: Optional[Player] = None
        self.enemies: List = []
        
        # Game systems
        self.wave_manager: Optional[WaveManager] = None
        self.camera: Optional[Camera] = None
        self.background: Optional[BackgroundSystem] = None
        self.formation_system = FormationSystem()
        self.input_handler = InputHandler()
        
        # Game state
        self.is_paused = False
        self.game_time = 0.0
    
    def initialize(self) -> None:
        """Initialize all gameplay systems and entities."""
        self.game_time = 0.0
        self.is_paused = False
        
        # Initialize systems
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.background = BackgroundSystem(WORLD_WIDTH, WORLD_HEIGHT)
        self.wave_manager = WaveManager(self.sound_manager)
        self.formation_system = FormationSystem()
        
        # Initialize entities
        self.player = Player(self.sound_manager, self.camera)
        self.enemies = []
        
        # Start first wave and setup audio
        self.wave_manager.start_wave(1)
        self._setup_audio()
    
    def update(self, dt: float) -> Optional[str]:
        """Main update loop returning next state or None."""
        if self.is_paused:
            return None
            
        self.game_time += dt
        self.input_handler.update()
        
        # Process input first
        if next_state := self._handle_input():
            return next_state
        
        # Update game systems
        self._update_player(dt)
        self._update_combat(dt)
        self._update_systems(dt)
        
        # Check game over condition
        return "game_over" if self.player.hp <= 0 else None
    
    def pause(self) -> None:
        """Pause the game."""
        self.is_paused = True
    
    def unpause(self) -> None:
        """Resume the game."""
        self.is_paused = False
    
    def cleanup(self) -> None:
        """Clean up resources when exiting gameplay."""
        self.sound_manager.stop_background_music()
    
    @property
    def game_data(self) -> Dict[str, Any]:
        """Return all data needed for rendering."""
        return {
            'player': self.player,
            'enemies': self.enemies,
            'camera': self.camera,
            'background': self.background,
            'wave_manager': self.wave_manager,
            'game_time': self.game_time,
            'is_paused': self.is_paused
        }
    
    def _setup_audio(self) -> None:
        """Setup background music for gameplay."""
        self.sound_manager.stop_background_music()
        music_path = "assets/background_music/gameplay.mp3"
        if self.sound_manager.load_background_music(music_path):
            self.sound_manager.play_background_music()
    
    def _handle_input(self) -> Optional[str]:
        """Process player input and return state change if needed."""
        keys = pygame.key.get_pressed()
        
        # Check for pause
        if self.input_handler.is_key_just_pressed(pygame.K_ESCAPE):
            return "pause"
        
        # Player actions
        if keys[pygame.K_SPACE]:
            self.player.attack(self.enemies)
        
        # Camera zoom
        zoom_change = (keys[pygame.K_EQUALS] - keys[pygame.K_MINUS]) * 0.1
        if zoom_change:
            new_zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.camera.target_zoom + zoom_change))
            self.camera.set_zoom(new_zoom)
        
        return None
    
    def _update_player(self, dt: float) -> None:
        """Update player with world boundary constraints."""
        self.player.update(dt)
        
        # Apply world boundaries
        bounds = self.background.get_world_bounds()
        self.player.x = max(bounds[0] + self.player.radius, 
                           min(bounds[2] - self.player.radius, self.player.x))
        self.player.y = max(bounds[1] + self.player.radius, 
                           min(bounds[3] - self.player.radius, self.player.y))
    
    def _update_combat(self, dt: float) -> None:
        """Update combat system with formation management."""
        self.formation_system.update(dt, self.enemies, self.player)
        
        # Remove enemies that have completed death animations
        self.enemies = [enemy for enemy in self.enemies if not enemy.should_be_removed()]
        
        # Update each enemy with enhanced AI
        for enemy in self.enemies:
            if getattr(enemy, 'form_active', False):
                self._update_formation_ai(enemy, dt)
            else:
                self._update_standard_ai(enemy, dt)
            
            enemy.update(dt, self.player)
    
    def _update_formation_ai(self, enemy, dt: float) -> None:
        """Update AI for enemies in formation."""
        player_distance = self._get_player_distance(enemy)
        
        # Prioritize combat over formation positioning
        if player_distance <= enemy.attack_range * 1.2:
            self._execute_combat_behavior(enemy, player_distance)
        else:
            self._move_to_formation(enemy, dt, player_distance)
    
    def _update_standard_ai(self, enemy, dt: float) -> None:
        """Update standard enemy AI behavior."""
        player_distance = self._get_player_distance(enemy)
        unit_vector = self._get_unit_vector_to_player(enemy, player_distance)
        
        # Calculate movement speed with knockback consideration
        knockback_factor = max(0.4, 1.0 - math.hypot(*enemy.knockback_velocity) / 150)
        move_speed = enemy.speed * knockback_factor * dt
        
        # Handle different enemy types
        if enemy.type in {"crawler", "brute"}:
            self._handle_melee_enemy(enemy, player_distance, unit_vector, move_speed)
        else:
            self._handle_ranged_enemy(enemy, player_distance, unit_vector, move_speed)
    
    def _handle_melee_enemy(self, enemy, distance: float, unit_vector: Tuple[float, float], speed: float) -> None:
        """Handle melee enemy behavior."""
        if distance > enemy.attack_range:
            enemy.x += unit_vector[0] * speed
            enemy.y += unit_vector[1] * speed
        elif enemy.attack_cooldown <= 0 and not getattr(enemy, 'is_dying', False):
            self._execute_enemy_attack(enemy)
    
    def _handle_ranged_enemy(self, enemy, distance: float, unit_vector: Tuple[float, float], speed: float) -> None:
        """Handle ranged enemy behavior with tactical positioning."""
        # Define preferred combat distances
        preferred_distances = {"sniper": 220, "fireshooter": 100}
        preferred_distance = preferred_distances.get(enemy.type, 150)
        
        # Tactical movement based on distance
        if distance < preferred_distance * 0.8:
            # Retreat
            enemy.x -= unit_vector[0] * speed * 0.9
            enemy.y -= unit_vector[1] * speed * 0.9
        elif distance > preferred_distance * 1.3:
            # Advance
            enemy.x += unit_vector[0] * speed * 0.6
            enemy.y += unit_vector[1] * speed * 0.6
        else:
            # Strafe movement
            enemy.x += -unit_vector[1] * speed * 0.5
            enemy.y += unit_vector[0] * speed * 0.5
        
        # Attack if in range
        if (distance <= enemy.attack_range and enemy.attack_cooldown <= 0 
            and not getattr(enemy, 'is_dying', False)):
            self._execute_enemy_attack(enemy)
    
    def _move_to_formation(self, enemy, dt: float, player_distance: float) -> None:
        """Move enemy to formation position."""
        target_x, target_y = enemy.form_target
        dx, dy = target_x - enemy.x, target_y - enemy.y
        formation_distance = math.hypot(dx, dy)
        
        if formation_distance > 25:
            # Move to formation at reduced speed
            speed = enemy.speed * 0.7 * dt
            enemy.x += (dx / formation_distance) * speed
            enemy.y += (dy / formation_distance) * speed
        
        # Always ready to attack player
        if player_distance <= enemy.attack_range and enemy.attack_cooldown <= 0:
            self._execute_enemy_attack(enemy)
    
    def _execute_combat_behavior(self, enemy, distance: float) -> None:
        """Execute direct combat behavior."""
        if enemy.type in {"crawler", "brute"}:
            # Aggressive melee approach
            if distance > enemy.attack_range:
                unit_vector = self._get_unit_vector_to_player(enemy, distance)
                speed = enemy.speed * 1.1  # 10% faster in combat
                enemy.x += unit_vector[0] * speed
                enemy.y += unit_vector[1] * speed
            elif enemy.attack_cooldown <= 0:
                self._execute_enemy_attack(enemy)
        else:
            # Ranged combat
            if distance <= enemy.attack_range and enemy.attack_cooldown <= 0:
                self._execute_enemy_attack(enemy)
    
    def _execute_enemy_attack(self, enemy) -> None:
        """Execute enemy attack if not dying."""
        if getattr(enemy, 'is_dying', False):
            return
        
        if enemy.type in {"crawler", "brute"}:
            self.player.take_damage(enemy.attack_power, enemy=enemy)
            enemy.attack_cooldown = 0.9
        else:
            enemy._initiate_ranged_attack(self.player)
    
    def _get_player_distance(self, enemy) -> float:
        """Calculate distance from enemy to player."""
        return math.hypot(self.player.x - enemy.x, self.player.y - enemy.y)
    
    def _get_unit_vector_to_player(self, enemy, distance: Optional[float] = None) -> Tuple[float, float]:
        """Get unit vector from enemy to player."""
        if distance is None:
            distance = self._get_player_distance(enemy)
        
        if distance > 0:
            dx = self.player.x - enemy.x
            dy = self.player.y - enemy.y
            return dx / distance, dy / distance
        
        return 0.0, 0.0
    
    def _update_systems(self, dt: float) -> None:
        """Update world systems and wave management."""
        self.background.update(dt)
        self.camera.update(dt, self.player.x, self.player.y)
        
        # Handle wave progression
        if self.wave_manager.update(dt, self.enemies):
            self.wave_manager.start_wave(self.wave_manager.current_wave + 1)
