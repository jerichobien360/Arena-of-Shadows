# gameplay_core.py - Pythonic Core Game Logic
from settings import *
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any

# Game entities
from entities.player import *
from entities.enemies import *

# Core systems
from systems.manager.wave_manager import *
from systems.game_feature.camera import *
from systems.game_feature.background_system import *

@dataclass
class FastFormations:
    """Ultra-fast formation system optimized for real-time combat"""
    cooldown: float = 0
    
    def should_form(self, enemies: List, player) -> bool:
        """Quick clustering check - only when many enemies are bunched up"""
        if len(enemies) < 6 or self.cooldown > 0:
            return False
        
        # Fast proximity check using list comprehension
        close_pairs = sum(1 for i, e1 in enumerate(enemies[:12])
                         for e2 in enemies[i+1:i+6]
                         if (e1.x - e2.x)**2 + (e1.y - e2.y)**2 < 14400)
        
        return close_pairs >= len(enemies) // 3
    
    def create_formation(self, enemies: List, player):
        """Instant formation creation with combat priority"""
        if not enemies:
            return
            
        positions = self._get_formation_positions(len(enemies), player)
        
        for enemy, pos in zip(enemies, positions):
            enemy.form_target = pos
            enemy.form_active = True
        
        self.cooldown = 3.0
    
    def _get_formation_positions(self, n: int, player) -> List[Tuple[float, float]]:
        """Generate formation positions based on enemy count"""
        if n <= 8:
            # Surround formation using list comprehension
            return [(player.x + 100 * math.cos(2 * math.pi * i / n),
                    player.y + 100 * math.sin(2 * math.pi * i / n)) 
                   for i in range(n)]
        
        # Pincer formation
        half = n // 2
        return ([(player.x - 140, player.y + (i - half//2) * 35) for i in range(half)] +
               [(player.x + 140, player.y + (i - half//2) * 35) for i in range(n - half)])
    
    def update(self, dt: float, enemies: List, player):
        """Minimal update - let enemies handle their own formation movement"""
        self.cooldown = max(0, self.cooldown - dt)
        
        # Clean up dead enemies from formations using list comprehension
        active_enemies = [e for e in enemies if getattr(e, 'form_active', False) and e.hp > 0]
        if len(active_enemies) < 3:
            for e in active_enemies:
                e.form_active = False
        
        # Check for new formations
        inactive = [e for e in enemies if not getattr(e, 'form_active', False)]
        if self.should_form(inactive, player):
            self.create_formation(inactive, player)

@dataclass
class InputHandler:
    """Simple input handler using dataclass"""
    prev_keys: set = field(default_factory=set)
    curr_keys: set = field(default_factory=set)
    
    def update(self):
        """Update key states"""
        self.prev_keys = self.curr_keys
        pressed = pygame.key.get_pressed()
        self.curr_keys = {i for i, key in enumerate(pressed) if key}
    
    def is_key_just_pressed(self, key: int) -> bool:
        """Check if key just pressed"""
        return key in self.curr_keys and key not in self.prev_keys

class GameplayCore:
    """Core gameplay logic without rendering"""
    
    def __init__(self, sound_manager):
        self.sound_manager = sound_manager
        self.player = self.enemies = None
        self.wave_manager = self.camera = self.background = None
        self.input_handler = InputHandler()
        self.is_paused = self.game_time = 0
        self.formations = FastFormations()
    
    def initialize(self):
        """Initialize gameplay systems"""
        self.game_time = 0
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.background = BackgroundSystem(WORLD_WIDTH, WORLD_HEIGHT)
        self.wave_manager = WaveManager(self.sound_manager)
        self.formations = FastFormations()
        self.player = Player(self.sound_manager, self.camera)
        self.enemies = []
        self.wave_manager.start_wave(1)
        self._setup_audio()
    
    def _setup_audio(self):
        """Setup background music"""
        self.sound_manager.stop_background_music()
        if self.sound_manager.load_background_music("assets/background_music/gameplay.mp3"):
            self.sound_manager.play_background_music()
    
    def update(self, dt: float) -> Optional[str]:
        """Main update loop - returns next state or None"""
        if self.is_paused:
            return None
            
        self.game_time += dt
        
        # Handle input and get state change
        if next_state := self._process_input():
            return next_state
        
        # Update game systems
        self._update_player(dt)
        self._update_combat_system(dt)
        self._update_world_systems(dt)
        
        return "game_over" if self.player.hp <= 0 else None
    
    def _process_input(self) -> Optional[str]:
        """Process input and return state change if needed"""
        keys = pygame.key.get_pressed()
        
        if self.input_handler.is_key_just_pressed(pygame.K_ESCAPE):
            return "pause"
        
        if keys[pygame.K_SPACE]:
            self.player.attack(self.enemies)
        
        # Zoom controls using walrus operator
        if zoom_delta := (keys[pygame.K_EQUALS] - keys[pygame.K_MINUS]) * 0.1:
            new_zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.camera.target_zoom + zoom_delta))
            self.camera.set_zoom(new_zoom)
        
        return None
    
    def _update_player(self, dt: float):
        """Update player with world boundaries"""
        self.player.update(dt)
        bounds = self.background.get_world_bounds()
        self.player.x = max(bounds[0] + self.player.radius, 
                           min(bounds[2] - self.player.radius, self.player.x))
        self.player.y = max(bounds[1] + self.player.radius, 
                           min(bounds[3] - self.player.radius, self.player.y))
    
    def _update_combat_system(self, dt: float):
        """Enhanced combat system with fade-aware enemy management"""
        self.formations.update(dt, self.enemies, self.player)
        
        # Remove enemies that have completed death fade
        self.enemies = [enemy for enemy in self.enemies 
                       if not enemy.should_be_removed()]
        
        for enemy in self.enemies:
            # Enhanced enemy AI with formation awareness
            if getattr(enemy, 'form_active', False):
                self._update_formation_combat_ai(enemy, dt)
            else:
                self._update_standard_combat_ai(enemy, dt)
            
            enemy.update(dt, self.player)
    
    def _update_formation_combat_ai(self, enemy, dt: float):
        """Formation AI that prioritizes combat over positioning"""
        player_dist = self._get_distance_to_player(enemy)
        
        # Combat has priority over formation
        if player_dist <= enemy.attack_range * 1.2:
            self._execute_direct_combat(enemy, dt)
        else:
            self._move_to_formation_position(enemy, dt, player_dist)
    
    def _move_to_formation_position(self, enemy, dt: float, player_dist: float):
        """Move enemy to formation position while maintaining combat readiness"""
        target_x, target_y = enemy.form_target
        dx, dy = target_x - enemy.x, target_y - enemy.y
        
        if (dist := math.hypot(dx, dy)) > 25:
            # Move to position at 70% speed to maintain combat awareness
            speed = enemy.speed * 0.7 * dt
            enemy.x += (dx / dist) * speed
            enemy.y += (dy / dist) * speed
        
        # Always ready to attack
        if player_dist <= enemy.attack_range and enemy.attack_cooldown <= 0:
            self._execute_enemy_attack(enemy)
    
    def _update_standard_combat_ai(self, enemy, dt: float):
        """Improved standard AI with tactical awareness"""
        player_dist = self._get_distance_to_player(enemy)
        unit_x, unit_y = self._get_unit_vector_to_player(enemy, player_dist)
        
        # Movement with knockback consideration
        knockback_factor = max(0.4, 1.0 - math.hypot(*enemy.knockback_velocity) / 150)
        move_speed = enemy.speed * knockback_factor * dt
        
        # Use dictionary for cleaner enemy type handling
        if enemy.type in {"crawler", "brute"}:
            self._handle_melee_ai(enemy, player_dist, unit_x, unit_y, move_speed)
        else:
            self._handle_ranged_ai(enemy, player_dist, unit_x, unit_y, move_speed)
    
    def _handle_melee_ai(self, enemy, player_dist: float, unit_x: float, unit_y: float, move_speed: float):
        """Handle melee enemy AI - no attacks while dying"""
        if player_dist > enemy.attack_range:
            enemy.x += unit_x * move_speed
        elif enemy.attack_cooldown <= 0 and not getattr(enemy, 'is_dying', False):
            self._execute_enemy_attack(enemy)
    
    def _handle_ranged_ai(self, enemy, player_dist: float, unit_x: float, unit_y: float, move_speed: float):
        """Handle ranged enemy AI with positioning"""
        preferred_distances = {"sniper": 220, "fireshooter": 100}
        preferred_dist = preferred_distances.get(enemy.type, 150)
        
        # Use match-case style logic with conditions
        if player_dist < preferred_dist * 0.8:
            # Retreat
            enemy.x -= unit_x * move_speed * 0.9
            enemy.y -= unit_y * move_speed * 0.9
        elif player_dist > preferred_dist * 1.3:
            # Advance
            enemy.x += unit_x * move_speed * 0.6
            enemy.y += unit_y * move_speed * 0.6
        else:
            # Strafe
            enemy.x += -unit_y * move_speed * 0.5
            enemy.y += unit_x * move_speed * 0.5
        
        if (player_dist <= enemy.attack_range and enemy.attack_cooldown <= 0 
        and not getattr(enemy, 'is_dying', False)):
            self._execute_enemy_attack(enemy)
    
    def _execute_direct_combat(self, enemy, dt: float):
        """Direct combat behavior for close-range encounters"""
        player_dist = self._get_distance_to_player(enemy)
        unit_x, unit_y = self._get_unit_vector_to_player(enemy, player_dist)
        
        if enemy.type in {"crawler", "brute"}:
            # Aggressive charge
            if player_dist > enemy.attack_range:
                speed = enemy.speed * 1.1 * dt  # 10% faster in combat
                enemy.x += unit_x * speed
                enemy.y += unit_y * speed
            elif enemy.attack_cooldown <= 0:
                self._execute_enemy_attack(enemy)
        else:
            # Ranged combat positioning
            if player_dist <= enemy.attack_range and enemy.attack_cooldown <= 0:
                self._execute_enemy_attack(enemy)
    
    def _execute_enemy_attack(self, enemy):
        """Execute enemy attack only if enemy is not dying"""
        # Prevent attacks during death fade
        if getattr(enemy, 'is_dying', False):
            return
            
        if enemy.type in {"crawler", "brute"}:
            self.player.take_damage(enemy.attack_power, enemy=enemy)
            enemy.attack_cooldown = 0.9
        else:
            enemy._initiate_ranged_attack(self.player)
    
    def _get_distance_to_player(self, enemy) -> float:
        """Calculate distance from enemy to player"""
        return math.hypot(self.player.x - enemy.x, self.player.y - enemy.y)
    
    def _get_unit_vector_to_player(self, enemy, player_dist: Optional[float] = None) -> Tuple[float, float]:
        """Get unit vector from enemy to player"""
        if player_dist is None:
            player_dist = self._get_distance_to_player(enemy)
        
        if player_dist > 0:
            dx, dy = self.player.x - enemy.x, self.player.y - enemy.y
            return dx / player_dist, dy / player_dist
        return 0.0, 0.0
    
    def _update_world_systems(self, dt: float):
        """Update world systems"""
        self.background.update(dt)
        self.camera.update(dt, self.player.x, self.player.y)
        
        # Wave management
        if self.wave_manager.update(dt, self.enemies):
            self.wave_manager.start_wave(self.wave_manager.current_wave + 1)
    
    def pause(self): 
        self.is_paused = True
    
    def unpause(self): 
        self.is_paused = False
    
    def cleanup(self):
        """Cleanup resources"""
        self.sound_manager.stop_background_music()
    
    @property
    def game_data(self) -> Dict[str, Any]:
        """Return all data needed for rendering"""
        return {
            'player': self.player,
            'enemies': self.enemies,
            'camera': self.camera,
            'background': self.background,
            'wave_manager': self.wave_manager,
            'game_time': self.game_time,
            'is_paused': self.is_paused
        }
