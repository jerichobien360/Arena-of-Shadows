from settings import *
import pygame, math
from typing import List

from systems.game_feature.particle_system import *


class SmartFormationAI:
    """Fast, tactical enemy formation system"""
    def __init__(self):
        self.active_groups = {} # Handling the enemies into group
        self.cooldown = 0
        
    def should_regroup(self, enemies: List, player) -> bool:
        """Fast regrouping when many enemies are close together"""
        if len(enemies) < 4 or self.cooldown > 0:
            return False
        
        # Check if enemies are clustered (fast regrouping condition)
        close_pairs = sum(1 for i, e1 in enumerate(enemies) 
                         for e2 in enemies[i+1:] 
                         if math.hypot(e1.x - e2.x, e1.y - e2.y) < 120)
        
        return close_pairs >= len(enemies) // 2  # Half the enemies are close together
    
    def initiate_formation(self, enemies: List, player):
        """Quick formation assignment"""
        if not enemies:
            return
            
        # Simple formation selection based on enemy count
        formation_type = (FormationType.SURROUND if len(enemies) <= 6 
                         else FormationType.PINCER if len(enemies) <= 10 
                         else FormationType.AMBUSH)
        
        positions = self.FORMATIONS[formation_type]((player.x, player.y), len(enemies))
        group_id = f"group_{id(player)}"
        
        # Quick assignment by distance to formation positions
        for enemy, pos in zip(enemies, positions):
            enemy.formation = FormationData(pos, True)
            enemy.group_id = group_id
        
        self.active_groups[group_id] = enemies
        self.cooldown = LAUNCH_ATTACK_COOLDOWN  # Shorter cooldown for faster battles
    
    def update_enemy_behavior(self, enemy, dt: float, player):
        """Formation movement with maintained combat capability"""
        if not enemy.formation.active:
            return enemy._standard_ai(dt, player)
        
        # Move to formation (faster movement)
        target_x, target_y = enemy.formation.target
        dx, dy = target_x - enemy.x, target_y - enemy.y
        distance = math.hypot(dx, dy)
        
        # Quick formation movement
        if distance > 20:
            speed = enemy.speed * 1.2 * dt  # 20% faster formation movement
            enemy.x += (dx / distance) * speed
            enemy.y += (dy / distance) * speed
        
        # Always maintain combat effectiveness
        self._execute_combat(enemy, player, dt)
    
    def _execute_combat(self, enemy, player, dt):
        """Ensure enemies attack only when alive and not dying"""
        # Skip combat if enemy is dying
        if getattr(enemy, 'is_dying', False):
            return

        if not self._is_enemy_in_combat_range(enemy):
            return
            
        player_dist = math.hypot(player.x - enemy.x, player.y - enemy.y)
        
        if player_dist <= enemy.attack_range and enemy.attack_cooldown <= 0:
            if enemy.type in ["crawler", "brute"]:
                player.take_damage(enemy.attack_power, enemy=enemy)
                enemy.attack_cooldown = 1.0
            else:
                enemy._initiate_ranged_attack(player)
    
    def _is_enemy_in_combat_range(self, enemy):
        """Check if enemy is within reasonable combat bounds"""
        # Allow some buffer outside screen for smooth gameplay
        buffer = 300  # Pixels outside screen where combat is still allowed
        return (-buffer <= enemy.x <= WORLD_WIDTH + buffer and 
                -buffer <= enemy.y <= WORLD_HEIGHT + buffer)
    
    def update(self, dt: float, all_enemies: List, player):
        """Streamlined formation system update"""
        self.cooldown = max(0, self.cooldown - dt)
        
        # Clean disbanded formations
        self.active_groups = {gid: [e for e in enemies if e.hp > 0] 
                             for gid, enemies in self.active_groups.items()}
        self.active_groups = {gid: enemies for gid, enemies in self.active_groups.items() 
                             if len(enemies) >= 2}
        
        # Disable formation for enemies in disbanded groups
        for enemy in all_enemies:
            if hasattr(enemy, 'group_id') and enemy.group_id not in self.active_groups:
                enemy.formation.active = False
        
        # Check for new formations
        unformed = [e for e in all_enemies if not e.formation.active]
        if self.should_regroup(unformed, player):
            self.initiate_formation(unformed, player)


class Enemy:
    def __init__(self, x, y, enemy_type="crawler"):
        self.x, self.y, self.type = x, y, enemy_type
        self.damage_flash_timer = self.attack_cooldown = 0
        self.knockback_velocity = [0, 0]
        self.attack_indicators, self.projectiles = [], []
        
        # Formation system
        self.formation = FormationData()
        self.group_id = None
        
        # Unpack stats
        stats = ENEMY_STATS[enemy_type]
        (self.hp, self.attack_power, self.speed, self.radius, 
         self.color, self.exp_value, self.attack_range) = stats
        self.max_hp = self.hp
        
        # Ranged enemy preferred distance
        self.preferred_distance = {"sniper": 250, "fireshooter": 120}.get(enemy_type, 0)
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)
   
        # Fade transition properties
        self.spawn_alpha = 0.0  # Start invisible
        self.death_alpha = 1.0  # Start visible
        self.is_spawning = True
        self.is_dying = False
        self.spawn_duration = 0.8  # Fade in over 0.8 seconds
        self.death_duration = 0.6  # Fade out over 0.6 seconds

        # Particle System
        self.particle_system = ParticleSystem()
        self.particle_system.set_world_bounds((0, 0, WORLD_WIDTH, WORLD_HEIGHT))

    def update(self, dt, player, formation_manager=None):
        """Enhanced update with fade transitions"""
        self._update_fade_states(dt)
        
        # Only update physics and AI if not in death fade
        if not self.is_dying:
            self._update_physics(dt)
            
            # AI with formation priority
            if formation_manager and self.formation.active:
                formation_manager.update_enemy_behavior(self, dt, player)
            else:
                self._standard_ai(dt, player)
                
            self._update_attacks(dt, player)
        
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        self.damage_flash_timer = max(0, self.damage_flash_timer - dt)
        self.rect.center = (self.x, self.y)
    
    def _update_fade_states(self, dt):
        """Update spawn and death fade effects"""
        if self.is_spawning:
            self.spawn_alpha = min(1.0, self.spawn_alpha + dt / self.spawn_duration)
            if self.spawn_alpha >= 1.0:
                self.is_spawning = False
        
        if self.is_dying:
            self.death_alpha = max(0.0, self.death_alpha - dt / self.death_duration)

    def _update_physics(self, dt):
        """Physics update with boundary constraints"""
        if any(abs(v) > 5 for v in self.knockback_velocity):
            # FIX: Use WORLD bounds instead of SCREEN bounds for enemies
            new_x = self.x + self.knockback_velocity[0] * dt
            new_y = self.y + self.knockback_velocity[1] * dt
            
            # Clamp to world bounds with buffer
            buffer = self.radius + 10
            self.x = max(buffer, min(WORLD_WIDTH - buffer, new_x))
            self.y = max(buffer, min(WORLD_HEIGHT - buffer, new_y))
            
            self.knockback_velocity = [v * 0.85 for v in self.knockback_velocity]
        else:
            self.knockback_velocity = [0, 0]

    def _standard_ai(self, dt, player):
        """Improved AI behavior - no combat while dying"""
        # Skip AI if dying
        if getattr(self, 'is_dying', False):
            return
        
        if not self._is_in_attack_bounds():
            # Move back toward world center if too far out
            center_x, center_y = WORLD_WIDTH / 2, WORLD_HEIGHT / 2
            dx, dy = center_x - self.x, center_y - self.y
            distance = math.hypot(dx, dy) or 1
            move_speed = self.speed * dt
            self.x += (dx / distance) * move_speed * 0.5
            self.y += (dy / distance) * move_speed * 0.5
            return

        dx, dy = player.x - self.x, player.y - self.y
        distance = math.hypot(dx, dy) or 1
        unit_x, unit_y = dx / distance, dy / distance
        
        knockback_reduction = max(0.3, 1.0 - math.hypot(*self.knockback_velocity) / 200)
        move_speed = self.speed * knockback_reduction * dt
        
        if self.type in ["crawler", "brute"]:
            if distance > self.attack_range:
                new_x = self.x + unit_x * move_speed
                new_y = self.y + unit_y * move_speed
                
                # FIX: Keep enemy within reasonable bounds
                self.x = max(0, min(WORLD_WIDTH, new_x))
                self.y = max(0, min(WORLD_HEIGHT, new_y))
            elif self.attack_cooldown <= 0:
                player.take_damage(self.attack_power, enemy=self)
                self.attack_cooldown = 1.0
        else:
            # Ranged enemy movement with bounds checking
            new_x, new_y = self.x, self.y
            
            if distance < self.preferred_distance * 0.7:
                new_x -= unit_x * move_speed * 0.8
                new_y -= unit_y * move_speed * 0.8
            elif distance > self.preferred_distance * 1.3:
                new_x += unit_x * move_speed * 0.6
                new_y += unit_y * move_speed * 0.6
            else:
                new_x += -unit_y * move_speed * 0.4
                new_y += unit_x * move_speed * 0.4
            
            # FIX: Apply bounds checking to ranged enemy movement
            buffer = 50
            self.x = max(buffer, min(WORLD_WIDTH - buffer, new_x))
            self.y = max(buffer, min(WORLD_HEIGHT - buffer, new_y))
            
            if distance <= self.attack_range and self.attack_cooldown <= 0:
                self._initiate_ranged_attack(player)
    
    def _is_in_attack_bounds(self):
        """Check if enemy is within bounds to attack"""
        buffer = 400  # Generous buffer for attacks
        return (-buffer <= self.x <= WORLD_WIDTH + buffer and 
                -buffer <= self.y <= WORLD_HEIGHT + buffer)

    def _initiate_ranged_attack(self, player):
        """Ranged attack initialization"""
        # Don't attack if the enemy is too far outside of bounds
        if not self._is_in_attack_bounds():
            return
        
        configs = {
            "sniper": (1, 1.2, (255, 255, 0), 2.5, 0),
            "fireshooter": (3, 0.6, (255, 100, 0), 2.0, 0.1)
        }
        
        shot_count, duration, color, cooldown, delay = configs[self.type]
        
        for i in range(shot_count):
            angle_offset = (i - 1) * 0.25 if shot_count > 1 else 0
            indicator = AttackIndicator(self, player, duration, color, self.type, 
                                      delay=i * delay, angle_offset=angle_offset)
            self.attack_indicators.append(indicator)
        
        self.attack_cooldown = cooldown
    
    def _update_attacks(self, dt, player):
        """Update attack systems"""
        # Update indicators
        for indicator in self.attack_indicators[:]:
            indicator.update(dt, player)
            if indicator.should_fire:
                # FIX: Validate projectile creation
                if self._can_create_projectile(indicator):
                    self._fire_projectile(indicator)
                indicator.should_fire = False
            if indicator.expired:
                self.attack_indicators.remove(indicator)
        
        # Update projectiles with better bounds checking
        for projectile in self.projectiles[:]:
            projectile.update(dt)
            
            # FIX: Check if projectile is valid before collision
            if projectile.is_valid() and projectile.check_collision(player):
                player.take_damage(projectile.damage, enemy=self)
                self.particle_system.create_attack_effect(projectile.x, projectile.y, "projectile")
                self.projectiles.remove(projectile)
            elif projectile.is_off_world() or not projectile.is_valid():
                self.projectiles.remove(projectile)
    
    def _can_create_projectile(self, indicator):
        """Check if projectile creation is valid"""
        # Don't create projectiles if target is invalid
        if (indicator.final_target_x is None or indicator.final_target_y is None):
            return False
            
        # Don't create projectiles if they would go way outside bounds
        distance_to_target = math.hypot(
            indicator.final_target_x - self.x,
            indicator.final_target_y - self.y
        )
        
        # Reasonable max distance to prevent extreme projectiles
        return distance_to_target < 2000

    def _fire_projectile(self, indicator):
        """Fire projectile"""
        configs = {
            "sniper": (400, (255, 255, 100), 3),
            "fireshooter": (250, (255, 150, 0), 5)
        }
        
        if indicator.attack_type not in configs:
            return
            
        speed, color, size = configs[indicator.attack_type]
        
        # FIX: Validate target position before creating projectile
        target_x = indicator.final_target_x
        target_y = indicator.final_target_y
        
        # Clamp target to reasonable bounds
        max_range = 1500  # Maximum projectile range
        dx, dy = target_x - self.x, target_y - self.y
        distance = math.hypot(dx, dy)
        
        if distance > max_range:
            # Limit target to max range
            scale = max_range / distance
            target_x = self.x + dx * scale
            target_y = self.y + dy * scale
        
        try:
            projectile = Projectile(self.x, self.y, target_x, target_y, 
                                  speed, self.attack_power, color, size)
            if projectile.is_valid():
                self.projectiles.append(projectile)
        except (ValueError, ZeroDivisionError, OverflowError):
            # Handle any math errors gracefully
            pass
    
    def apply_knockback_velocity(self, vel_x, vel_y):
        """Apply capped knockback"""
        self.knockback_velocity[0] += vel_x
        self.knockback_velocity[1] += vel_y
        
        # Cap velocity
        magnitude = math.hypot(*self.knockback_velocity)
        if magnitude > 400:
            scale = 400 / magnitude
            self.knockback_velocity = [v * scale for v in self.knockback_velocity]
   
    def take_damage(self, amount):
        """Enhanced damage with death fade trigger"""
        self.hp -= amount
        self.damage_flash_timer = 0.2

        self.particle_system.create_damage_effect(self.x, self.y, amount, enemy_type=self.type)
        
        if self.hp <= 0 and not self.is_dying:
            self.is_dying = True
            return True  # Don't remove immediately, let fade complete
        
        return False

    def should_be_removed(self):
        """Check if enemy should be removed (after death fade)"""
        return self.is_dying and self.death_alpha <= 0.0
    
    def get_current_alpha(self):
        """Get current alpha based on fade states"""
        if self.is_spawning:
            return self.spawn_alpha
        elif self.is_dying:
            return self.death_alpha
        return 1.0

    def render(self, screen, camera=None):
        """Enhanced render with fade transitions"""
        # Calculate current alpha
        current_alpha = self.get_current_alpha()
        
        # Skip rendering if completely transparent
        if current_alpha <= 0.01:
            return
        
        # Render attacks (they should appear normally)
        if not self.is_dying:  # Don't show attacks while dying
            for indicator in self.attack_indicators:
                indicator.render(screen, camera)
            for projectile in self.projectiles:
                projectile.render(screen, camera)
        
        zoom = camera.zoom if camera else 1.0
        radius = int(self.radius * zoom)
        
        # Calculate color with damage flash
        color = self.color
        if self.damage_flash_timer > 0:
            flash = self.damage_flash_timer / 0.2
            color = tuple(min(255, c + int(150 * flash)) for c in color)
        
        # Apply alpha to color
        alpha_color = (*color, int(255 * current_alpha))
        
        # Create a surface for alpha blending
        if current_alpha < 1.0:
            temp_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, alpha_color, (radius, radius), radius)
            screen.blit(temp_surface, (int(self.x - radius), int(self.y - radius)))
        else:
            # Normal rendering for performance when fully opaque
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), radius)
        
        # Formation indicator (with alpha)
        if self.formation.active and not self.is_dying:
            formation_alpha = int(255 * current_alpha * 0.8)  # Slightly dimmer
            formation_color = (*GREEN, formation_alpha)
            if current_alpha < 1.0:
                temp_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, formation_color, (2, 2), 2)
                screen.blit(temp_surface, (int(self.x - 2), int(self.y - 2)))
            else:
                pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), 2)
        
        # Type markers (with alpha)
        if not self.is_dying:
            if self.type == "sniper":
                line_len = int(4 * zoom)
                line_alpha = int(255 * current_alpha)
                line_color = (*WHITE, line_alpha)
                if current_alpha < 1.0:
                    # Draw on temp surface for alpha
                    temp_surface = pygame.Surface((line_len * 2, line_len * 2), pygame.SRCALPHA)
                    pygame.draw.line(temp_surface, line_color, 
                                   (0, line_len), (line_len * 2, line_len), 1)
                    pygame.draw.line(temp_surface, line_color, 
                                   (line_len, 0), (line_len, line_len * 2), 1)
                    screen.blit(temp_surface, (int(self.x - line_len), int(self.y - line_len)))
                else:
                    pygame.draw.line(screen, WHITE, (self.x - line_len, self.y), 
                                   (self.x + line_len, self.y), 1)
                    pygame.draw.line(screen, WHITE, (self.x, self.y - line_len), 
                                   (self.x, self.y + line_len), 1)
            
            elif self.type == "fireshooter":
                inner_radius = max(1, int((self.radius - 3) * zoom))
                inner_alpha = int(255 * current_alpha)
                inner_color = (*FIRESHOOTER_INNER_COLOR, inner_alpha)  # Define this color
                if current_alpha < 1.0:
                    temp_surface = pygame.Surface((inner_radius * 2, inner_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(temp_surface, inner_color, (inner_radius, inner_radius), inner_radius)
                    screen.blit(temp_surface, (int(self.x - inner_radius), int(self.y - inner_radius)))
                else:
                    pygame.draw.circle(screen, (255, 200, 0), (int(self.x), int(self.y)), inner_radius)
        
        # Health bar (with alpha)
        if self.hp < self.max_hp and not self.is_dying:
            self._draw_health_bar(screen, camera, current_alpha)
   
    def _draw_health_bar(self, screen, camera=None, alpha=1.0):
        """Health bar with alpha support"""
        zoom = camera.zoom if camera else 1.0
        bar_width, bar_height = int(20 * zoom), int(3 * zoom)
        bar_x = self.x - bar_width // 2
        bar_y = self.y - (self.radius * zoom) - 6 * zoom
        
        red_alpha = int(255 * alpha)
        green_alpha = int(255 * alpha)
        
        if alpha < 1.0:
            # Create temp surface for alpha blending
            temp_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
            pygame.draw.rect(temp_surface, (*RED, red_alpha), (0, 0, bar_width, bar_height))
            health_width = (self.hp / self.max_hp) * bar_width
            pygame.draw.rect(temp_surface, (*GREEN, green_alpha), (0, 0, health_width, bar_height))
            screen.blit(temp_surface, (bar_x, bar_y))
        else:
            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
            health_width = (self.hp / self.max_hp) * bar_width
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))


class AttackIndicator:
    """Visual attack warning"""
    def __init__(self, enemy, player, duration, color, attack_type, delay=0, angle_offset=0):
        self.enemy, self.duration, self.color, self.attack_type = enemy, duration, color, attack_type
        self.delay, self.angle_offset = delay, angle_offset
        self.timer = 0
        self.should_fire = self.expired = False
        self.final_target_x = self.final_target_y = None
        self.current_target_x = self.current_target_y = None
        self._update_target(player)
    
    def _update_target(self, player):
        """Calculate target with spread"""
        if self.attack_type == "sniper":
            self.current_target_x, self.current_target_y = player.x, player.y
        else:
            base_angle = math.atan2(player.y - self.enemy.y, player.x - self.enemy.x)
            spread_angle = base_angle + self.angle_offset
            offset = 25
            self.current_target_x = player.x + math.cos(spread_angle) * offset
            self.current_target_y = player.y + math.sin(spread_angle) * offset
        
        # FIX: Clamp target should take on to reasonable bounds
        buffer = 200
        self.current_target_x = max(-buffer, min(WORLD_WIDTH + buffer, self.current_target_x))
        self.current_target_y = max(-buffer, min(WORLD_HEIGHT + buffer, self.current_target_y))
    
    def update(self, dt, player):
        """Update indicator"""
        self.timer += dt
        
        if not self.should_fire and self.timer >= self.delay:
            self._update_target(player)
        
        if not self.should_fire and self.timer >= self.delay + self.duration:
            self.final_target_x, self.final_target_y = self.current_target_x, self.current_target_y
            self.should_fire = self.expired = True
    
    def render(self, screen, camera=None):
        """Clean target indicator"""
        if self.timer < self.delay:
            return
        
        if camera:
            target_x, target_y = camera.world_to_screen(self.current_target_x, self.current_target_y)
            zoom = camera.zoom
        else:
            target_x, target_y, zoom = self.current_target_x, self.current_target_y, 1.0
        
        # FIX: Skip rendering if target is way off screen (for optimization)
        if camera and not camera.is_point_visible(self.current_target_x, self.current_target_y, margin=100):
            return

        progress = min(1.0, (self.timer - self.delay) / self.duration)
        pulse = 0.5 + 0.5 * abs(math.sin(progress * math.pi * 8))
        
        intensity = pulse * (0.8 if self.attack_type == "sniper" else 0.6)
        color = tuple(min(255, int(c * intensity)) for c in self.color)
        radius = int((6 if self.attack_type == "sniper" else 8) * zoom * (0.8 + 0.4 * pulse))
        
        try:
            pygame.draw.circle(screen, color, (int(target_x), int(target_y)), radius, 2)
        except (ValueError, OverflowError):
            pass


class Projectile:
    """Enemy projectile"""
    def __init__(self, x, y, target_x, target_y, speed, damage, color, size):
        self.x, self.y, self.speed, self.damage, self.color, self.size = x, y, speed, damage, color, size
        
        # FIX: Validate inputs
        if not all(isinstance(val, (int, float)) and not math.isnan(val) and not math.isinf(val) 
                  for val in [x, y, target_x, target_y, speed]):
            self.valid = False
            self.velocity = [0, 0]
            return
        
        dx, dy = target_x - x, target_y - y
        distance = math.hypot(dx, dy) or 1
        self.velocity = [(dx / distance) * speed, (dy / distance) * speed]

        if distance < 0.1:  # Too close to target
            self.valid = False
            self.velocity = [0, 0]
        else:
            self.valid = True
            self.velocity = [(dx / distance) * speed, (dy / distance) * speed]
    
    def is_valid(self):
        """Check if projectile is valid"""
        return (hasattr(self, 'valid') and self.valid and 
                all(isinstance(val, (int, float)) and not math.isnan(val) and not math.isinf(val) 
                    for val in [self.x, self.y] + self.velocity))

    def update(self, dt):
        """FIX: Safe update with validation"""
        if not self.is_valid():
            return
            
        try:
            self.x += self.velocity[0] * dt
            self.y += self.velocity[1] * dt
            
            # Validate position after update
            if (math.isnan(self.x) or math.isnan(self.y) or 
                math.isinf(self.x) or math.isinf(self.y)):
                self.valid = False
        except (ValueError, OverflowError):
            self.valid = False
    
    def check_collision(self, player):
        """Safe collision check"""
        if not self.is_valid():
            return False
            
        try:
            return math.hypot(player.x - self.x, player.y - self.y) < (player.radius + self.size)
        except (ValueError, OverflowError):
            return False
    
    def is_off_world(self):
        """FIX: More generous bounds checking"""
        if not self.is_valid():
            return True
            
        buffer = 500  # Larger buffer to prevent premature removal
        return not (-buffer <= self.x <= WORLD_WIDTH + buffer and 
                   -buffer <= self.y <= WORLD_HEIGHT + buffer)
    
    def render(self, screen, camera=None):
        """Safe rendering with bounds checking"""
        if not self.is_valid():
            return
            
        try:
            if camera:
                screen_x, screen_y = camera.world_to_screen(self.x, self.y)
                size = max(1, int(self.size * camera.zoom))
                
                # Skip if way off screen
                if not (0 <= screen_x <= screen.get_width() and 0 <= screen_y <= screen.get_height()):
                    return
            else:
                screen_x, screen_y, size = self.x, self.y, self.size
            
            pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), size)
        except (ValueError, OverflowError, TypeError):
            pass
