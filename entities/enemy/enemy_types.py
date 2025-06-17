import math
import random
import pygame
from entities.enemy.enemy_base import Enemy, AttackIndicator, Projectile
from settings import *


class ShadowAssassin(Enemy):
    """Stealth assassin with burst damage, invisibility, and tactical positioning"""
    
    def __init__(self, x, y):
        super().__init__(x, y, "shadow_assassin")   
        # Core stats
        self.hp = self.max_hp = 60
        self.attack_power, self.speed, self.radius = 35, 55, 14
        self.color, self.exp_value, self.attack_range = (45, 15, 75), 150, 45
        
        # Add missing formation attribute
        self.formation = type('Formation', (), {'active': False})()
        
        # Add missing aggro_level attribute
        self.aggro_level = 1.0
        
        # Stealth system
        self.stealth = {
            'meter': 100, 'max': 100, 'regen_rate': 15, 'drain_rate': 30,
            'active': False, 'alpha': 0.2, 'cooldown': 0, 'last_break': 0
        }
        
        # Combat abilities
        self.abilities = {
            'assassination': {'range': 35, 'damage': 80, 'cooldown': 0, 'bonus': 1.8},
            'shadow_bolt': {'cooldown': 0, 'damage': 20, 'speed': 120},
            'shadow_trap': {'cooldown': 0, 'max': 2}
        }
        
        # AI state
        self.ai = {
            'state': 'hunting', 'timer': 0, 'patience': random.uniform(3.0, 6.0),
            'preferred_distance': 40, 'retreat_threshold': 25, 'flank_angle': 0
        }
        
        self.active_traps = []
        self.last_attack_time = self.combo_counter = 0
        self.projectiles = []  # Initialize projectiles list
    
    def update(self, dt, player, formation_manager=None):
        self._update_fade_states(dt)
        self._update_stealth(dt)  # Add this missing call
        self._update_cooldowns(dt)  # Add this missing call
        self._update_traps(dt, player)  # Add this missing call
        
        # Only update physics and AI if not in death fade
        if not self.is_dying:
            self._update_physics(dt)
            
            # AI with formation priority - Fix: Check if formation_manager exists
            if formation_manager and hasattr(formation_manager, 'update_enemy_behavior') and hasattr(self, 'formation') and self.formation.active:
                formation_manager.update_enemy_behavior(self, dt, player)
            else:
                self._update_ai(dt, player)  # Changed from _standard_ai to _update_ai
                
            self._update_attacks(dt, player)  # Add this missing call
        
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        self.damage_flash_timer = max(0, self.damage_flash_timer - dt)
        self.rect.center = (self.x, self.y)

        # Increase aggression over time
        self.aggro_level = min(3.0, self.aggro_level + dt * 0.2)
        self._check_rage_mode()
    
    def _update_attacks(self, dt, player):
        """Handle automatic attacks and ability usage"""
        current_time = pygame.time.get_ticks() / 1000.0
        distance = math.hypot(player.x - self.x, player.y - self.y)
        
        # Basic attack if in range and cooldown is ready
        if (distance <= self.attack_range and 
            self.attack_cooldown <= 0 and 
            current_time - self.last_attack_time > 0.8):
            
            # Melee attack
            if distance <= self.radius + getattr(player, 'radius', 15) + 5:
                player.take_damage(self.attack_power, enemy=self)
                self.attack_cooldown = 1.0
                self.last_attack_time = current_time
                self.combo_counter += 1
                
                if self.stealth['active']:
                    self._break_stealth()
    
    def _update_stealth(self, dt):
        current_time = pygame.time.get_ticks() / 1000.0
        stealth = self.stealth
        
        if stealth['active']:
            stealth['meter'] -= stealth['drain_rate'] * dt
            if stealth['meter'] <= 0:
                self._break_stealth()
        elif current_time - stealth['last_break'] > 2.0:
            stealth['meter'] = min(stealth['max'], stealth['meter'] + stealth['regen_rate'] * dt)
    
    def _enter_stealth(self):
        if self.stealth['meter'] < 30 or self.stealth['cooldown'] > 0 or self.stealth['active']:
            return False
        self.stealth.update({'active': True, 'cooldown': 1.0})
        self.combo_counter = 0
        return True
    
    def _break_stealth(self):
        if not self.stealth['active']:
            return
        self.stealth.update({
            'active': False, 'last_break': pygame.time.get_ticks() / 1000.0, 'cooldown': 3.0
        })
    
    def _update_ai(self, dt, player):
        self.ai['timer'] += dt
        distance = math.hypot(player.x - self.x, player.y - self.y)
        
        # State transitions using dictionary dispatch
        state_transitions = {
            'hunting': lambda: self._transition_from_hunting(distance),
            'stalking': lambda: self._transition_from_stalking(distance),
            'engaging': lambda: self._transition_from_engaging(distance),
            'retreating': lambda: self._transition_from_retreating(distance),
            'casting': lambda: self._transition_from_casting()
        }
        
        new_state = state_transitions[self.ai['state']]()
        if new_state != self.ai['state']:
            self.ai.update({'state': new_state, 'timer': 0})
        
        # Execute behavior
        behaviors = {
            'hunting': self._hunt, 'stalking': self._stalk, 'engaging': self._engage,
            'retreating': self._retreat, 'casting': self._cast
        }
        behaviors[self.ai['state']](dt, player)
    
    def _transition_from_hunting(self, distance):
        if distance < 100:
            if self._can_stealth() and random.random() < 0.7:
                self._enter_stealth()
                return 'stalking'
            return 'engaging'
        return 'hunting'
    
    def _transition_from_stalking(self, distance):
        if not self.stealth['active']:
            return 'engaging'
        if distance < self.abilities['assassination']['range'] and self.ai['timer'] > 1.0:
            return 'engaging'
        if self.ai['timer'] > self.ai['patience']:
            return 'engaging'
        return 'stalking'
    
    def _transition_from_engaging(self, distance):
        if distance > 120:
            return 'hunting'
        if distance < self.ai['retreat_threshold'] and self.hp < self.max_hp * 0.4:
            return 'retreating'
        if self._can_stealth() and self.combo_counter >= 2 and random.random() < 0.6:
            self._enter_stealth()
            return 'stalking'
        return 'engaging'
    
    def _transition_from_retreating(self, distance):
        if distance > 60:
            return 'stalking' if self._enter_stealth() else 'hunting'
        if self.ai['timer'] > 2.0:
            return 'engaging'
        return 'retreating'
    
    def _transition_from_casting(self):
        return 'engaging' if self.ai['timer'] > 0.8 else 'casting'
    
    def _can_stealth(self):
        return (self.stealth['meter'] >= 30 and self.stealth['cooldown'] <= 0 
                and not self.stealth['active'])
    
    def _hunt(self, dt, player):
        distance = math.hypot(player.x - self.x, player.y - self.y)
        if distance > self.ai['preferred_distance'] + 20:
            self._move_toward(player, dt, 0.7)
        else:
            self._circle_player(dt, player, self.ai['preferred_distance'])
    
    def _stalk(self, dt, player):
        distance = math.hypot(player.x - self.x, player.y - self.y)
        if distance > self.abilities['assassination']['range']:
            # Predictive movement
            pred_x, pred_y = self._predict_position(player, 0.5)
            self._move_toward_point(pred_x, pred_y, dt, speed_mult=0.5)
    
    def _engage(self, dt, player):
        distance = math.hypot(player.x - self.x, player.y - self.y)
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Try assassination
        if (self.stealth['active'] and distance <= self.abilities['assassination']['range'] 
            and self.abilities['assassination']['cooldown'] <= 0):
            self._attempt_assassination(player, current_time)
            return
        
        # Cast abilities
        if self._should_cast_ability(player, distance):
            self.ai['state'] = 'casting'
            return
        
        # Positioning and attacks
        if distance < self.ai['retreat_threshold']:
            self._move_away(player, dt, 1.2)
        elif distance > self.attack_range:
            self._move_to_flank(dt, player)
        else:
            self._circle_player(dt, player, distance, 0.8)
        
        if distance <= self.attack_range and current_time - self.last_attack_time > 1.2:
            self._cast_shadow_bolt(player, current_time)
    
    def _retreat(self, dt, player):
        self._move_away(player, dt, 1.3, add_jitter=True)
    
    def _cast(self, dt, player):
        pass  # Stationary while casting
    
    def _move_toward(self, target, dt, speed_mult=1.0):
        dx, dy = target.x - self.x, target.y - self.y
        self._move_in_direction(dx, dy, dt, speed_mult)
    
    def _move_toward_point(self, x, y, dt, speed_mult=1.0):
        dx, dy = x - self.x, y - self.y
        self._move_in_direction(dx, dy, dt, speed_mult)
    
    def _move_away(self, target, dt, speed_mult=1.0, add_jitter=False):
        dx, dy = self.x - target.x, self.y - target.y
        if add_jitter:
            angle_offset = math.sin(self.ai['timer'] * 3) * 0.3
            cos_o, sin_o = math.cos(angle_offset), math.sin(angle_offset)
            dx, dy = dx * cos_o - dy * sin_o, dx * sin_o + dy * cos_o
        self._move_in_direction(dx, dy, dt, speed_mult)
    
    def _move_in_direction(self, dx, dy, dt, speed_mult=1.0):
        distance = math.hypot(dx, dy)
        if distance > 0:
            speed = (self.speed if not self.stealth['active'] else 25) * dt * speed_mult
            self.x += (dx / distance) * speed
            self.y += (dy / distance) * speed
        self._keep_in_bounds()
    
    def _circle_player(self, dt, player, target_distance, speed_mult=1.0):
        dx, dy = player.x - self.x, player.y - self.y
        current_distance = math.hypot(dx, dy)
        
        if current_distance == 0:
            return
            
        unit_x, unit_y = dx / current_distance, dy / current_distance
        
        # Maintain distance
        distance_error = current_distance - target_distance
        if abs(distance_error) > 5:
            radial_speed = self.speed * dt * 0.5 * speed_mult
            direction = 1 if distance_error < 0 else -1
            self.x += unit_x * radial_speed * direction
            self.y += unit_y * radial_speed * direction
        
        # Circular movement
        perp_x, perp_y = -unit_y, unit_x
        circle_speed = self.speed * dt * 0.7 * speed_mult
        direction = 1 if self.ai['state'] == 'engaging' else -1
        self.x += perp_x * circle_speed * direction
        self.y += perp_y * circle_speed * direction
        
        self._keep_in_bounds()
    
    def _move_to_flank(self, dt, player):
        self.ai['flank_angle'] += dt * 1.5
        base_angle = math.atan2(player.y - self.y, player.x - self.x)
        flank_offset = math.sin(self.ai['flank_angle']) * math.pi / 3
        target_angle = base_angle + flank_offset
        
        target_x = player.x + math.cos(target_angle) * self.ai['preferred_distance']
        target_y = player.y + math.sin(target_angle) * self.ai['preferred_distance']
        
        self._move_toward_point(target_x, target_y, dt, 0.8)
    
    def _should_cast_ability(self, player, distance):
        current_time = pygame.time.get_ticks() / 1000.0
        return ((self.abilities['shadow_bolt']['cooldown'] <= 0 and distance <= self.attack_range 
                and current_time - self.last_attack_time > 1.0) or
                (self.abilities['shadow_trap']['cooldown'] <= 0 and 
                 len(self.active_traps) < self.abilities['shadow_trap']['max'] and
                 distance < 60 and random.random() < 0.3))
    
    def _attempt_assassination(self, player, current_time):
        if self.abilities['assassination']['cooldown'] > 0:
            return
            
        base_damage = self.abilities['assassination']['damage']
        if self.stealth['active']:
            base_damage = int(base_damage * self.abilities['assassination']['bonus'])
        
        player_radius = getattr(player, 'radius', 15)
        if math.hypot(player.x - self.x, player.y - self.y) <= self.radius + player_radius + 5:
            player.take_damage(base_damage, enemy=self)
            self.abilities['assassination']['cooldown'] = 8.0
            self.last_attack_time = current_time
            self.combo_counter = 0
            if self.stealth['active']:
                self._break_stealth()
    
    def _cast_shadow_bolt(self, player, current_time):
        if self.abilities['shadow_bolt']['cooldown'] > 0:
            return
            
        pred_x, pred_y = self._predict_position(player, 0.3)
        dx, dy = pred_x - self.x, pred_y - self.y
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            unit_x, unit_y = dx / distance, dy / distance
            bolt = ShadowBolt(
                self.x + unit_x * self.radius, self.y + unit_y * self.radius,
                unit_x * self.abilities['shadow_bolt']['speed'],
                unit_y * self.abilities['shadow_bolt']['speed'],
                self.abilities['shadow_bolt']['damage']
            )
            
            if hasattr(self, 'projectiles'):
                self.projectiles.append(bolt)
            
            self.abilities['shadow_bolt']['cooldown'] = 2.0
            self.last_attack_time = current_time
            self.combo_counter += 1
            
            if self.stealth['active'] and random.random() < 0.7:
                self._break_stealth()
    
    def _predict_position(self, player, time_ahead):
        if hasattr(player, 'vel_x') and hasattr(player, 'vel_y'):
            return (player.x + player.vel_x * time_ahead, player.y + player.vel_y * time_ahead)
        return (player.x, player.y)
    
    def _keep_in_bounds(self):
        margin = self.radius + 5
        self.x = max(margin, min(SCREEN_WIDTH - margin, self.x))
        self.y = max(margin, min(SCREEN_HEIGHT - margin, self.y))
    
    def _update_cooldowns(self, dt):
        for ability in self.abilities.values():
            if 'cooldown' in ability:
                ability['cooldown'] = max(0, ability['cooldown'] - dt)
        self.stealth['cooldown'] = max(0, self.stealth['cooldown'] - dt)
        self.damage_flash_timer = max(0, self.damage_flash_timer - dt)
    
    def _update_traps(self, dt, player):
        for trap in self.active_traps[:]:
            trap.update(dt, player)
            if trap.should_remove:
                self.active_traps.remove(trap)
    
    def take_damage(self, damage, attacker=None):
        result = super().take_damage(damage)  # Remove attacker param for parent call
        if self.stealth['active'] and damage >= 15:
            self._break_stealth()
        return result
    
    def render(self, screen, camera=None):
        current_alpha = self.get_current_alpha()
        if self.stealth['active']:
            current_alpha *= self.stealth['alpha']
        
        if current_alpha <= 0.01:
            return
        
        screen_x, screen_y, radius = self._get_screen_coords(camera)
        if not self._is_on_screen(screen, screen_x, screen_y, radius):
            return
        
        # Get color based on state
        color_map = {
            'stalking': (60, 20, 100), 'engaging': (80, 30, 120), 'default': self.color
        }
        color = color_map.get(self.ai['state'], color_map['default'])
        
        if self.damage_flash_timer > 0:
            flash_intensity = self.damage_flash_timer / 0.2
            color = tuple(min(255, c + int(100 * flash_intensity)) for c in color)
        
        self._render_body(screen, screen_x, screen_y, radius, color, current_alpha)
        self._render_indicators(screen, screen_x, screen_y, radius, current_alpha)
        
        for trap in self.active_traps:
            trap.render(screen, camera)
        
        if self.hp < self.max_hp and not self.is_dying and current_alpha > 0.3:
            self._draw_health_bar(screen, camera, current_alpha)
    
    def _get_screen_coords(self, camera):
        if camera:
            screen_x, screen_y = camera.world_to_screen(self.x, self.y)
            radius = max(1, int(self.radius * camera.zoom))
        else:
            screen_x, screen_y = int(self.x), int(self.y)
            radius = self.radius
        return screen_x, screen_y, radius
    
    def _is_on_screen(self, screen, screen_x, screen_y, radius):
        margin = radius + 20
        return not (screen_x < -margin or screen_x > screen.get_width() + margin or
                   screen_y < -margin or screen_y > screen.get_height() + margin)
    
    def _render_body(self, screen, screen_x, screen_y, radius, color, alpha):
        try:
            if alpha < 1.0:
                temp_surface = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
                alpha_color = (*color, int(255 * alpha))
                pygame.draw.circle(temp_surface, alpha_color, (radius + 1, radius + 1), radius)
                
                if self.stealth['active']:
                    aura_radius = radius + 4
                    pygame.draw.circle(temp_surface, (20, 5, 40, int(100 * alpha)), 
                                     (radius + 1, radius + 1), aura_radius, 2)
                
                screen.blit(temp_surface, (int(screen_x - radius - 1), int(screen_y - radius - 1)))
            else:
                pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), radius)
        except Exception as e:
            print(f"Render error: {e}")
    
    def _render_indicators(self, screen, screen_x, screen_y, radius, alpha):
        try:
            # Assassination ready indicator
            if (self.abilities['assassination']['cooldown'] <= 0 and self.stealth['active'] 
                and alpha > 0.3):
                indicator_size = radius + 8
                pulse = 0.6 + 0.4 * abs(math.sin(pygame.time.get_ticks() * 0.008))
                indicator_alpha = alpha * pulse * 0.8
                
                if indicator_alpha > 0.1:
                    indicator_surface = pygame.Surface((indicator_size * 2, indicator_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(indicator_surface, (150, 50, 50, int(255 * indicator_alpha)),
                                     (indicator_size, indicator_size), indicator_size, 2)
                    screen.blit(indicator_surface, 
                               (int(screen_x - indicator_size), int(screen_y - indicator_size)))
        except Exception as e:
            print(f"Indicator render error: {e}")
    
    def _draw_health_bar(self, screen, camera, alpha):
        try:
            screen_x, screen_y, _ = self._get_screen_coords(camera)
            bar_width, bar_height = (35, 4) if not camera else (max(20, int(35 * camera.zoom)), 
                                                                max(2, int(4 * camera.zoom)))
            offset_y = (self.radius + 10) if not camera else max(10, int(self.radius * camera.zoom + 10))
            
            bar_x, bar_y = int(screen_x - bar_width // 2), int(screen_y - offset_y)
            health_percent = max(0, self.hp / self.max_hp)
            health_width = max(1, int(bar_width * health_percent))
            
            # Background and health bar
            bg_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, int(255 * alpha * 0.8)))
            screen.blit(bg_surface, (bar_x, bar_y))
            
            if health_width > 0:
                health_surface = pygame.Surface((health_width, bar_height), pygame.SRCALPHA)
                health_surface.fill((150, 30, 80, int(255 * alpha)))
                screen.blit(health_surface, (bar_x, bar_y))
        except Exception as e:
            print(f"Health bar error: {e}")


class ShadowBolt(Projectile):
    """Shadow magic projectile with trail effect"""
    
    def __init__(self, x, y, vel_x, vel_y, damage):
        # Fix: Use proper Projectile constructor parameters
        target_x = x + vel_x  # Calculate target from velocity
        target_y = y + vel_y
        speed = math.hypot(vel_x, vel_y)  # Calculate speed from velocity
        
        super().__init__(x, y, target_x, target_y, speed, damage, (80, 30, 120), 6)
        
        # Override velocity with provided values
        self.velocity = [vel_x, vel_y]
        self.trail_positions, self.trail_length = [], 8
    
    def update(self, dt, player=None):
        super().update(dt)  # Parent update doesn't take player parameter
        self.trail_positions.append((self.x, self.y))
        if len(self.trail_positions) > self.trail_length:
            self.trail_positions.pop(0)
    
    def render(self, screen, camera=None):
        screen_x, screen_y = (camera.world_to_screen(self.x, self.y) if camera 
                             else (int(self.x), int(self.y)))
        radius = max(1, int(self.radius * camera.zoom)) if camera else self.radius
        
        try:
            # Render trail
            for i, (trail_x, trail_y) in enumerate(self.trail_positions):
                trail_screen_x, trail_screen_y = (camera.world_to_screen(trail_x, trail_y) if camera 
                                                 else (int(trail_x), int(trail_y)))
                alpha = (i + 1) / len(self.trail_positions) * 0.6
                trail_radius = max(1, int(radius * alpha))
                
                trail_surface = pygame.Surface((trail_radius * 2, trail_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, (*self.color, int(255 * alpha)), 
                                 (trail_radius, trail_radius), trail_radius)
                screen.blit(trail_surface, 
                           (int(trail_screen_x - trail_radius), int(trail_screen_y - trail_radius)))
            
            # Main projectile with glow
            pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), radius)
            if radius > 2:
                glow_color = tuple(min(255, c + 50) for c in self.color)
                pygame.draw.circle(screen, glow_color, (int(screen_x), int(screen_y)), radius // 2)
        except Exception as e:
            print(f"Shadow bolt render error: {e}")


class ShadowTrap:
    """Shadow trap that damages player when stepped on"""
    
    def __init__(self, x, y, damage=25, lifetime=8.0):
        self.x, self.y, self.damage = x, y, damage
        self.lifetime = self.max_lifetime = lifetime
        self.radius, self.trigger_radius = 20, 15
        self.armed_time, self.pulse_timer = 0.5, 0
        self.is_armed = self.triggered = self.should_remove = self.damage_dealt = False
        self.trigger_effect_timer = 0
    
    def update(self, dt, player):
        self.lifetime -= dt
        self.pulse_timer += dt
        
        if self.lifetime <= 0:
            self.should_remove = True
            return
        
        if not self.is_armed:
            self.armed_time -= dt
            if self.armed_time <= 0:
                self.is_armed = True
        
        if (self.is_armed and not self.triggered and not self.damage_dealt and
            math.hypot(player.x - self.x, player.y - self.y) <= self.trigger_radius):
            self.triggered = True
            self.trigger_effect_timer = 0.3
            player.take_damage(self.damage)
            self.damage_dealt = True
            self.lifetime = min(self.lifetime, 0.5)
        
        if self.triggered:
            self.trigger_effect_timer -= dt
    
    def render(self, screen, camera=None):
        screen_x, screen_y = (camera.world_to_screen(self.x, self.y) if camera 
                             else (int(self.x), int(self.y)))
        radius = max(1, int(self.radius * camera.zoom)) if camera else self.radius
        
        # Skip if off screen
        margin = radius + 20
        if (screen_x < -margin or screen_x > screen.get_width() + margin or
            screen_y < -margin or screen_y > screen.get_height() + margin):
            return
        
        try:
            alpha = self.lifetime / 2.0 if self.lifetime < 2.0 else 1.0
            
            # Trigger effect
            if self.triggered and self.trigger_effect_timer > 0:
                effect_alpha = self.trigger_effect_timer / 0.3
                effect_radius = int(radius * (1.5 - effect_alpha * 0.5))
                effect_surface = pygame.Surface((effect_radius * 2, effect_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(effect_surface, (150, 50, 50, int(255 * effect_alpha * 0.8)),
                                 (effect_radius, effect_radius), effect_radius)
                screen.blit(effect_surface, 
                           (int(screen_x - effect_radius), int(screen_y - effect_radius)))
            
            # Main trap visual
            if not self.is_armed:
                form_progress = 1.0 - (self.armed_time / 0.5)
                current_radius, trap_alpha = int(radius * form_progress), alpha * form_progress
            else:
                pulse = 0.7 + 0.3 * abs(math.sin(self.pulse_timer * 4))
                current_radius, trap_alpha = int(radius * pulse), alpha
            
            if current_radius > 0 and trap_alpha > 0.1:
                # Outer ring and inner core
                outer_surface = pygame.Surface((current_radius * 2 + 4, current_radius * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(outer_surface, (60, 20, 100, int(255 * trap_alpha * 0.6)),
                                 (current_radius + 2, current_radius + 2), current_radius, 2)
                screen.blit(outer_surface, 
                           (int(screen_x - current_radius - 2), int(screen_y - current_radius - 2)))
                
                inner_radius = max(1, current_radius // 3)
                inner_surface = pygame.Surface((inner_radius * 2, inner_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(inner_surface, (100, 40, 150, int(255 * trap_alpha)),
                                 (inner_radius, inner_radius), inner_radius)
                screen.blit(inner_surface, 
                           (int(screen_x - inner_radius), int(screen_y - inner_radius)))
        except Exception as e:
            print(f"Shadow trap render error: {e}")
