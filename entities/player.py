from settings import *
from game_function.game_function import *
from systems.game_feature.particle_system import *
from systems.manager.game_state_manager import *

from typing import Optional, Tuple, List
import pygame
import math
import random



class Player:
    """Player class with movement, combat, leveling, dash ability, and smooth knockback effects."""
    
    def __init__(self, sound_manager=None, camera=None, start_x: float = 0, start_y: float = 0):
        # Components and Properties
        self.sound_manager = sound_manager
        self.camera = camera
        self.radius = 15
        self.world_bounds: Optional[Tuple[float, float, float, float]] = None
        self.status_effect = {
            "stunned": None,
            "slow down": None,
            "burning": None,
            "hyponotized": None,
            "freezed": None,
            "healing": None
        } # TODO: Create a class that handles on these status effect, and make a simple design for this

        # Setup the player's position
        if start_x is None:
            start_x = WORLD_WIDTH // 2
        if start_y is None:
            start_y = WORLD_HEIGHT // 2

        # Position
        self.position = {'x': start_x, 'y': start_y}
        
        # Initial Position
        self.x = start_x
        self.y = start_y

        # Timers
        self.skill_timer = {'attack_cooldown': 0, 'damage_flash_timer': 0}
        
        # Knockback physics
        self.knockback = {'velocity': [0.0, 0.0], 'decay': 0.88, 'threshold': 8, 'resistance': 0.7}

        # Dash mechanics
        self.dash_property = {'cooldown': 0, 'duration': 0, 'velocity': [0.0, 0.0], 'distance': 150,
                              'speed': 800, 'cooldown_time': 2.0, 'duration_time': 0.2,
                              'is_invincible': False, 'last_movement_direction': [0, 0]}

        # Game Feature
        self.particle_system = ParticleSystem()
        self.particle_system.set_world_bounds((0, 0, WORLD_WIDTH, WORLD_HEIGHT))
        
        # Reset/Update
        self._reset_stats()
        self._update_rect()

        # Time
        self.time = 0

    def _reset_stats(self) -> None:
        """Reset player stats to initial values."""
        self.hp = self.max_hp = 100
        self.attack_power = 25
        self.speed = 200
        self.level = 1
        self.experience = 0
        self.stat_points = 0

    def restart_stats(self):
        self._reset_stats()

    def get_camera_target_position(self):
        """Get the position the camera should target."""
        return (self.x, self.y)

    def update(self, dt: float) -> None:
        """Update player state each frame."""
        self._update_dash(dt)
        self._update_knockback(dt)
        self._handle_movement(dt)
        
        self.skill_timer['attack_cooldown'] = max(0, self.skill_timer['attack_cooldown'] - dt)
        self.skill_timer['damage_flash_timer'] = max(0, self.skill_timer['damage_flash_timer'] - dt)
        self.dash_property['cooldown'] = max(0, self.dash_property['cooldown'] - dt)
        
        self._check_level_up()
        self._update_rect()
        self.particle_system.update(dt)

        if DEBUGGING_ENABLE:
            self.time += dt
            if self.time >= 1:
                DEBUGGING('PLAYER_MS', DEBUGGING_ENABLE, item=(self.x, self.y))
                self.time = 0

    def _update_dash(self, dt: float) -> None:
        """Update dash mechanics."""
        if self.dash_property['duration'] > 0:
            self.dash_property['duration'] -= dt
            
            # Apply dash movement
            new_x = self.x + self.dash_property['velocity'][0] * dt
            new_y = self.y + self.dash_property['velocity'][1] * dt
            
            # Apply bounds
            new_x, new_y = self._apply_bounds(new_x, new_y)
            self.x, self.y = new_x, new_y
            
            # Create dash trail particles
            self.particle_system.create_dash_trail(self.x, self.y)
            
            # End dash
            if self.dash_property['duration'] <= 0:
                self.dash_property['velocity'] = [0.0, 0.0]
                self.dash_property['is_invincible'] = False

    def _update_knockback(self, dt: float) -> None:
        """Update knockback physics."""
        # Don't apply knockback during dash
        if self.dash_property['duration'] > 0:
            return
            
        vx, vy = self.knockback['velocity']
        
        if abs(vx) > self.knockback['threshold'] or abs(vy) > self.knockback['threshold']:
            # Apply knockback velocity
            new_x = self.x + vx * dt
            new_y = self.y + vy * dt
            
            # Apply bounds
            new_x, new_y = self._apply_bounds(new_x, new_y)
            
            self.x, self.y = new_x, new_y
            
            # Apply decay
            self.knockback['velocity'][0] *= self.knockback['decay']
            self.knockback['velocity'][1] *= self.knockback['decay']
        else:
            self.knockback['velocity'] = [0.0, 0.0]

    def _handle_movement(self, dt: float) -> None:
        """Handle WASD/arrow key movement with bounds checking."""
        # Don't handle normal movement during dash
        if self.dash_property['duration'] > 0:
            return
        
        # Player's Movement
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        
        # Store movement direction for dash
        if dx != 0 or dy != 0:
            self.dash_property['last_movement_direction'] = [dx, dy]
        
        # Normalize diagonal movement
        if dx and dy:
            dx *= 0.707
            dy *= 0.707
        
        # Reduce movement during knockback
        knockback_magnitude = math.hypot(*self.knockback['velocity'])
        movement_reduction = max(0.3, 1.0 - (knockback_magnitude / 250))
        
        # Apply movement
        move_speed = self.speed * movement_reduction
        new_x = self.x + dx * move_speed * dt
        new_y = self.y + dy * move_speed * dt
        
        # Updating (x, y) coordinates before to take an effect
        self.x, self.y = self._apply_bounds(new_x, new_y)

    def dash(self) -> bool:
        """Perform dash ability."""
        if self.dash_property['cooldown'] > 0 or self.dash_property['duration'] > 0:
            return False
        
        # Get dash direction from current input or last movement
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        
        # If no current input, use last movement direction
        if dx == 0 and dy == 0:
            dx, dy = self.dash_property['last_movement_direction']
        
        # If still no direction, dash forward (right)
        if dx == 0 and dy == 0:
            dx = 1
        
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707
        
        # Set dash properties
        self.dash_property['velocity'] = [dx * self.dash_property['speed'], dy * self.dash_property['speed']]
        self.dash_property['duration'] = self.dash_property['duration_time']
        self.dash_property['cooldown'] = self.dash_property['cooldown_time']
        self.dash_property['is_invincible'] = True
        
        # Clear existing knockback
        self.knockback['velocity'] = [0.0, 0.0]
        
        # Play dash sound and create effects
        self.sound_manager.play_sound('dash')
        self.particle_system.create_dash_start_effect(self.x, self.y, dx, dy)
        
        # Add camera shake
        self.camera.add_shake(intensity=0.5, duration=0.3)
        
        return True

    def _apply_bounds(self, x: float, y: float) -> Tuple[float, float]:
        """Apply screen and world bounds to coordinates."""
        # Screen bounds
        x = max(self.radius, min(SCREEN_WIDTH - self.radius, x))
        y = max(self.radius, min(SCREEN_HEIGHT - self.radius, y))
        
        # World bounds
        if self.world_bounds:
            left, top, right, bottom = self.world_bounds
            x = max(left + self.radius, min(right - self.radius, x))
            y = max(top + self.radius, min(bottom - self.radius, y))
        
        return x, y

    def _update_rect(self) -> None:
        """Update collision rectangle."""
        self.rect = pygame.Rect(
            self.x - self.radius, self.y - self.radius,
            self.radius * 2, self.radius * 2
        )

    def attack(self, enemies: List) -> int:
        """Attack nearby enemies within range."""
        if self.skill_timer['attack_cooldown'] > 0 or self.dash_property['duration'] > 0:
            return 0
        
        self.skill_timer['attack_cooldown'] = 0.5
        self.sound_manager.play_sound('attack')
        
        hit_count = 0
        for enemy in enemies[:]:  # Shallow copy to avoid modification issues
            distance = math.hypot(enemy.x - self.x, enemy.y - self.y) * self.camera.zoom

            # Converting from world to screen size
            attack_range = 60
            screen_range = self.camera.screen_view(attack_range)
            
            if distance <= screen_range:  # Check if the player's enemies within range
                damage = self.attack_power + random.randint(-3, 3)

                self.particle_system.create_attack_effect(enemy.x, enemy.y, "melee") # Particle effect
                
                if enemy.take_damage(damage):  # Enemy died
                    self.sound_manager.play_sound('enemy_death')
                    self.add_experience(enemy.exp_value)
                else:  # Enemy survived
                    self.sound_manager.play_sound('enemy_hit')
                    self._apply_enemy_knockback(enemy, distance, damage)
                    self.particle_system.create_damage_effect(enemy.x, enemy.y, damage, 
                                                        enemy_type=enemy.type)
                
                hit_count += 1
        
        return hit_count

    def _apply_enemy_knockback(self, enemy, distance: float, damage: int) -> None:
        """Apply knockback to enemy."""
        if distance <= 0:
            return
        
        # Calculate knockback direction
        dx = (enemy.x - self.x) / distance
        dy = (enemy.y - self.y) / distance
        
        # Calculate knockback force (increased during dash)
        base_knockback = 150
        if self.dash_property['duration'] > 0:
            base_knockback *= 2.0  # Dash attacks have more knockback
            
        damage_multiplier = damage / 25.0
        distance_multiplier = max(0.5, 60 / distance)
        knockback_force = base_knockback * damage_multiplier * distance_multiplier
        
        enemy.apply_knockback_velocity(dx * knockback_force, dy * knockback_force)

    def take_damage(self, amount: int, enemy=None) -> None:
        """Take damage with visual feedback and knockback."""
        # Invincible during dash
        if self.dash_property['is_invincible']:
            return
            
        self.hp = max(0, self.hp - amount)
        self.skill_timer['damage_flash_timer'] = 0.3
        
        self.sound_manager.play_sound('player_damage')

        self.particle_system.create_damage_effect(self.x, self.y, amount, is_player=True)
        
        if enemy:
            self._apply_damage_knockback(enemy, amount)
            
        # Camera shake based on damage and enemy
        shake_intensity = self._calculate_shake_intensity(amount, enemy)
        self.camera.add_shake(intensity=shake_intensity, duration=1)

        if self.hp <= 0:
            self.particle_system.create_death_effect(self.x, self.y, "player", is_player=True)

    def _calculate_shake_intensity(self, damage: int, enemy) -> float:
        """Calculate camera shake intensity."""
        shake_intensity = 1
        if enemy:
            size_multiplier = enemy.radius / 12.0
            damage_multiplier = damage / 15.0
            shake_intensity = min(3, 1 + size_multiplier * damage_multiplier)
        return shake_intensity

    def _apply_damage_knockback(self, enemy, damage: int) -> None:
        """Apply knockback when taking damage."""
        # No knockback during dash
        if self.dash_property['duration'] > 0:
            return
            
        dx = self.x - enemy.x
        dy = self.y - enemy.y
        distance = math.hypot(dx, dy)
        
        if distance <= 0:
            return
        
        # Normalize direction
        dx /= distance
        dy /= distance
        
        # Calculate knockback force
        base_knockback = 120
        size_multiplier = enemy.radius / 12.0
        damage_multiplier = damage / 15.0
        distance_multiplier = max(0.8, 30 / max(distance, 1))
        
        knockback_force = (base_knockback * size_multiplier * 
                          damage_multiplier * distance_multiplier * 
                          self.knockback['resistance'])
        
        # Apply velocity with capping
        vx = self.knockback['velocity'][0] + dx * knockback_force
        vy = self.knockback['velocity'][1] + dy * knockback_force
        
        # Cap maximum velocity
        max_knockback = 300
        magnitude = math.hypot(vx, vy)
        if magnitude > max_knockback:
            scale = max_knockback / magnitude
            vx *= scale
            vy *= scale
        
        self.knockback['velocity'] = [vx, vy]

    def add_experience(self, exp: int) -> None:
        """Add experience points."""
        self.experience += exp

    def _check_level_up(self) -> None:
        """Check and handle level ups."""
        leveled_up = False
        
        while self.experience >= self.level * 100:
            self.experience -= self.level * 100
            self.level += 1
            self.stat_points += 3
            self.max_hp += 15
            self.hp = self.max_hp
            self.attack_power += 3
            self.knockback['resistance'] = min(0.9, self.knockback['resistance'] + 0.02)
            
            # Improve dash with level
            self.dash_property['cooldown_time'] = max(1.0, self.dash_property['cooldown_time'] - 0.05)
            self.dash_property['distance'] = min(200, self.dash_property['distance'] + 5)
            
            leveled_up = True
        
        if leveled_up:
            self.sound_manager.play_sound('level_up')

    def is_dashing(self) -> bool:
        """Check if player is currently dashing."""
        return self.dash_property['duration'] > 0

    def get_dash_cooldown_percent(self) -> float:
        """Get dash cooldown as percentage (0-1, where 0 is ready)."""
        return self.dash_property['cooldown'] / self.dash_property['cooldown_time']

    def render(self, screen: pygame.Surface) -> None:
        """Render player with visual effects."""
        # Calculate color with damage flash and dash effects
        color = GREEN
        if self.skill_timer['damage_flash_timer'] > 0:
            flash = int(255 * self.skill_timer['damage_flash_timer'] / 0.3)
            color = (min(255, GREEN[0] + flash), GREEN[1], GREEN[2])
        
        # Dash visual effects
        if self.dash_property['duration'] > 0:
            # Make player slightly transparent and add blue tint during dash
            dash_progress = 1.0 - (self.dash_property['duration'] / self.dash_property['duration_time'])
            blue_tint = int(100 * (1.0 - dash_progress))
            color = (color[0], color[1], min(255, color[2] + blue_tint))
            
            # Create afterimage effect
            self._render_dash_afterimage(screen, color)
        
        # Render motion trail during knockback (but not during dash)
        if self.dash_property['duration'] <= 0:
            self._render_motion_trail(screen, color)
        
        # Draw player
        player_scale = self.radius
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(player_scale))
        
        # Show attack range when ready (but not during dash)
        if self.skill_timer['attack_cooldown'] <= 0 and self.dash_property['duration'] <= 0:
            # Converting from world to screen size
            attack_range = 60
            screen_range = self.camera.screen_view(attack_range)

            # Create a max limit range of an attacking player
            pygame.draw.circle(screen, (0, 255, 0, 30), 
                            (int(self.x), int(self.y)), int(screen_range), 1)
        
        # Update the particle rendering (universal update)
        self.particle_system.render(screen, self.camera)

    def _render_dash_afterimage(self, screen: pygame.Surface, color: Tuple[int, int, int]) -> None:
        """Render afterimage effect during dash."""
        dash_progress = 1.0 - (self.dash_property['duration'] / self.dash_property['duration_time'])
        
        for i in range(3):
            afterimage_factor = (i + 1) * 0.3
            afterimage_x = self.x - self.dash_property['velocity'][0] * afterimage_factor * 0.02
            afterimage_y = self.y - self.dash_property['velocity'][1] * afterimage_factor * 0.02
            
            try:
                alpha = int(100 * (1.0 - dash_progress) / (i + 2))
                afterimage_surface = pygame.Surface((self.radius * 2, self.radius * 2), 
                                                  pygame.SRCALPHA)
                afterimage_color = (*color, alpha)
                pygame.draw.circle(afterimage_surface, afterimage_color,
                                 (self.radius, self.radius), self.radius - 1)
                screen.blit(afterimage_surface, (afterimage_x - self.radius, afterimage_y - self.radius))
            except:
                pass  # Skip if not supported

    def _render_dash_indicator(self, screen: pygame.Surface) -> None:
        """Render dash cooldown indicator."""
        if self.dash_property['cooldown'] > 0:
            # Draw cooldown circle
            indicator_radius = 20
            indicator_x = int(self.x + self.radius + 10)
            indicator_y = int(self.y - self.radius - 10)
            
            # Background circle
            pygame.draw.circle(screen, (50, 50, 50), (indicator_x, indicator_y), indicator_radius, 2)
            
            # Cooldown progress
            cooldown_percent = self.get_dash_cooldown_percent()
            if cooldown_percent > 0:
                angle = 2 * math.pi * (1.0 - cooldown_percent) - math.pi / 2
                end_x = indicator_x + int(indicator_radius * 0.8 * math.cos(angle))
                end_y = indicator_y + int(indicator_radius * 0.8 * math.sin(angle))
                pygame.draw.line(screen, BLUE, (indicator_x, indicator_y), (end_x, end_y), 3)

    def _render_motion_trail(self, screen: pygame.Surface, color: Tuple[int, int, int]) -> None:
        """Render motion trail effect during knockback."""
        knockback_magnitude = math.hypot(*self.knockback['velocity'])
        if knockback_magnitude <= 15:
            return
        
        trail_alpha = min(80, int(knockback_magnitude / 4))
        
        for i in range(2):
            trail_factor = (i + 1) * 0.4
            trail_x = self.x - self.knockback['velocity'][0] * trail_factor * 0.015
            trail_y = self.y - self.knockback['velocity'][1] * trail_factor * 0.015
            
            try:
                trail_alpha_current = trail_alpha // (i + 2)
                trail_surface = pygame.Surface((self.radius * 2, self.radius * 2), 
                                             pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, (*color, trail_alpha_current),
                                 (self.radius, self.radius), self.radius - 2)
                screen.blit(trail_surface, (trail_x - self.radius, trail_y - self.radius))
            except:
                pass  # Skip if not supported

    def set_world_bounds(self, bounds: Tuple[float, float, float, float]) -> None:
        """Set world boundaries as (left, top, right, bottom)."""
        self.world_bounds = bounds
