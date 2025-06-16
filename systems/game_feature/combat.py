from settings import *
import pygame, math, random
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple

class FormationType(Enum):
    SURROUND = "surround"
    PINCER = "pincer"
    AMBUSH = "ambush"
    PROTECT_RANGED = "protect_ranged"
    TRIANGLE_ASSAULT = "triangle_assault"
    ENCIRCLE_TRAP = "encircle_trap"

@dataclass
class FormationPosition:
    x: float
    y: float
    role: str = "default"  # "protector", "ranged", "flanker", "assault"
    assigned: bool = False
    priority: int = 1  # Higher priority positions filled first

class QuickFormation:
    """Advanced enemy formation system with ranged protection and coordinated attacks"""
    
    def __init__(self, enemies: List, player):
        self.enemies, self.player = enemies, player
        self.formation_type = None
        self.positions = []
        self.formation_timer = 0
        self.is_active = False
        self.coordinated_attack_timer = 0
        self.is_coordinated_attacking = False
        self.ranged_enemies = []
        self.melee_enemies = []
        self.formation_center = (0, 0)
        
    def _categorize_enemies(self):
        """Separate enemies by type for tactical positioning"""
        self.ranged_enemies = [e for e in self.enemies if e.type in ["fireshooter", "sniper"]]
        self.melee_enemies = [e for e in self.enemies if e.type in ["crawler", "brute"]]
    
    def should_regroup(self) -> bool:
        """Enhanced regrouping decision with tactical considerations"""
        if len(self.enemies) < 3 or self.formation_timer > 0:
            return False
        
        self._categorize_enemies()
        
        # Priority regroup if ranged enemies are exposed
        if self.ranged_enemies:
            for ranged in self.ranged_enemies:
                nearby_protectors = sum(1 for melee in self.melee_enemies 
                                      if math.hypot(melee.x - ranged.x, melee.y - ranged.y) < 80)
                if nearby_protectors < 2:  # Ranged enemy needs protection
                    return True
        
        # Standard clustering check
        close_count = sum(1 for i, e1 in enumerate(self.enemies) 
                         for e2 in self.enemies[i+1:] 
                         if math.hypot(e1.x - e2.x, e1.y - e2.y) < 120)
        
        return close_count >= max(2, len(self.enemies) // 3)
    
    def initiate_formation(self):
        """Enhanced formation setup with tactical selection"""
        if not self.enemies:
            return
        
        self._categorize_enemies()
        n = len(self.enemies)
        ranged_count = len(self.ranged_enemies)
        melee_count = len(self.melee_enemies)
        
        # Tactical formation selection
        if ranged_count > 0 and melee_count >= ranged_count * 2:
            self.formation_type = FormationType.PROTECT_RANGED
        elif n >= 6 and melee_count >= 4:
            # Choose between aggressive formations
            if random.random() < 0.6:
                self.formation_type = FormationType.ENCIRCLE_TRAP
            else:
                self.formation_type = FormationType.TRIANGLE_ASSAULT
        elif n <= 6:
            self.formation_type = FormationType.SURROUND
        elif n <= 10:
            self.formation_type = FormationType.PINCER
        else:
            self.formation_type = FormationType.AMBUSH
        
        self._assign_positions()
        self.is_active = True
        self.formation_timer = random.uniform(8.0, 12.0)  # Longer formation duration
        
        # Set coordinated attack timer for aggressive formations
        if self.formation_type in [FormationType.TRIANGLE_ASSAULT, FormationType.ENCIRCLE_TRAP]:
            self.coordinated_attack_timer = random.uniform(2.0, 4.0)
    
    def _assign_positions(self):
        """Advanced position assignment with role-based positioning"""
        player_pos = (self.player.x, self.player.y)
        
        if self.formation_type == FormationType.PROTECT_RANGED:
            self._create_protection_formation(player_pos)
        elif self.formation_type == FormationType.TRIANGLE_ASSAULT:
            self._create_triangle_assault(player_pos)
        elif self.formation_type == FormationType.ENCIRCLE_TRAP:
            self._create_encircle_trap(player_pos)
        else:
            self._create_standard_formation(player_pos)
        
        self._assign_enemies_to_positions()
    
    def _create_protection_formation(self, player_pos):
        """Create formation to protect ranged enemies"""
        self.positions = []
        ranged_count = len(self.ranged_enemies)
        melee_count = len(self.melee_enemies)
        
        # Position ranged enemies safely behind melee line
        safe_distance = 180
        for i, _ in enumerate(self.ranged_enemies):
            angle = (2 * math.pi * i / ranged_count) + math.pi  # Behind player
            safe_x = player_pos[0] + safe_distance * math.cos(angle)
            safe_y = player_pos[1] + safe_distance * math.sin(angle)
            self.positions.append(FormationPosition(safe_x, safe_y, "ranged", priority=3))
        
        # Position melee as protectors in front of ranged
        protect_distance = 100
        for i in range(melee_count):
            if i < ranged_count * 2:  # Primary protectors
                # Position between player and ranged enemies
                angle = 2 * math.pi * i / max(1, ranged_count * 2)
                protect_x = player_pos[0] + protect_distance * math.cos(angle)
                protect_y = player_pos[1] + protect_distance * math.sin(angle)
                self.positions.append(FormationPosition(protect_x, protect_y, "protector", priority=2))
            else:  # Additional flankers
                angle = 2 * math.pi * (i - ranged_count * 2) / max(1, melee_count - ranged_count * 2)
                flank_x = player_pos[0] + 90 * math.cos(angle)
                flank_y = player_pos[1] + 90 * math.sin(angle)
                self.positions.append(FormationPosition(flank_x, flank_y, "flanker", priority=1))
    
    def _create_triangle_assault(self, player_pos):
        """Create triangle formation for coordinated assault"""
        self.positions = []
        n = len(self.enemies)
        
        # Create triangle points
        triangle_distance = 120
        triangle_angles = [0, 2*math.pi/3, 4*math.pi/3]  # 120 degrees apart
        
        # Assign triangle tips (strongest enemies)
        for i, angle in enumerate(triangle_angles):
            tip_x = player_pos[0] + triangle_distance * math.cos(angle)
            tip_y = player_pos[1] + triangle_distance * math.sin(angle)
            self.positions.append(FormationPosition(tip_x, tip_y, "assault", priority=3))
        
        # Fill triangle sides
        remaining = n - 3
        for i in range(remaining):
            side = i % 3  # Which triangle side
            position_on_side = (i // 3 + 1) / max(1, (remaining // 3 + 1))
            
            angle1 = triangle_angles[side]
            angle2 = triangle_angles[(side + 1) % 3]
            
            # Interpolate between triangle points
            lerp_x = player_pos[0] + triangle_distance * (
                math.cos(angle1) * (1 - position_on_side) + 
                math.cos(angle2) * position_on_side
            )
            lerp_y = player_pos[1] + triangle_distance * (
                math.sin(angle1) * (1 - position_on_side) + 
                math.sin(angle2) * position_on_side
            )
            
            self.positions.append(FormationPosition(lerp_x, lerp_y, "assault", priority=2))
    
    def _create_encircle_trap(self, player_pos):
        """Create encircling formation to trap player"""
        self.positions = []
        n = len(self.enemies)
        
        # Create multiple concentric circles
        inner_radius = 80
        outer_radius = 140
        
        inner_count = min(n // 2, 6)  # Inner circle enemies
        outer_count = n - inner_count
        
        # Inner circle (closer, more aggressive)
        for i in range(inner_count):
            angle = 2 * math.pi * i / inner_count
            circle_x = player_pos[0] + inner_radius * math.cos(angle)
            circle_y = player_pos[1] + inner_radius * math.sin(angle)
            self.positions.append(FormationPosition(circle_x, circle_y, "assault", priority=3))
        
        # Outer circle (support and cut off escape)
        for i in range(outer_count):
            angle = 2 * math.pi * i / outer_count + math.pi / outer_count  # Offset from inner
            circle_x = player_pos[0] + outer_radius * math.cos(angle)
            circle_y = player_pos[1] + outer_radius * math.sin(angle)
            self.positions.append(FormationPosition(circle_x, circle_y, "flanker", priority=2))
    
    def _create_standard_formation(self, player_pos):
        """Create standard formations (surround, pincer, ambush)"""
        n = len(self.enemies)
        
        if self.formation_type == FormationType.SURROUND:
            positions = [(player_pos[0] + 120 * math.cos(2 * math.pi * i / n), 
                         player_pos[1] + 120 * math.sin(2 * math.pi * i / n)) for i in range(n)]
        elif self.formation_type == FormationType.PINCER:
            positions = [(player_pos[0] + (-160 if i < n//2 else 160), 
                         player_pos[1] + (i - n//4) * 45) for i in range(n)]
        else:  # AMBUSH
            positions = [(player_pos[0] + random.randint(-250, 250), 
                         player_pos[1] + random.randint(-250, 250)) for i in range(n)]
        
        self.positions = [FormationPosition(x, y, "default", priority=1) for x, y in positions]
    
    def _assign_enemies_to_positions(self):
        """Smart enemy-to-position assignment based on roles and priorities"""
        # Sort positions by priority (higher first)
        sorted_positions = sorted(self.positions, key=lambda p: p.priority, reverse=True)
        
        available_enemies = list(self.enemies)
        
        for pos in sorted_positions:
            if not available_enemies:
                break
            
            # Choose best enemy for this role
            if pos.role == "ranged":
                # Assign ranged enemies to ranged positions
                candidates = [e for e in available_enemies if e.type in ["fireshooter", "sniper"]]
                if not candidates:
                    candidates = available_enemies  # Fallback
            elif pos.role == "protector":
                # Assign tanky enemies to protection roles
                candidates = [e for e in available_enemies if e.type == "brute"]
                if not candidates:
                    candidates = [e for e in available_enemies if e.type == "crawler"]
                if not candidates:
                    candidates = available_enemies  # Fallback
            elif pos.role == "assault":
                # Assign aggressive enemies to assault roles
                candidates = [e for e in available_enemies if e.type in ["brute", "crawler"]]
                if not candidates:
                    candidates = available_enemies  # Fallback
            else:
                candidates = available_enemies
            
            # Find closest suitable enemy
            best_enemy = min(candidates, key=lambda e: math.hypot(e.x - pos.x, e.y - pos.y))
            
            # Assign enemy to position
            best_enemy.formation_target = (pos.x, pos.y)
            best_enemy.formation_role = pos.role
            best_enemy.in_formation = True
            pos.assigned = True
            available_enemies.remove(best_enemy)
    
    def update(self, dt: float):
        """Enhanced formation update with coordinated attacks"""
        if not self.is_active:
            if self.should_regroup():
                self.initiate_formation()
            return
        
        self.formation_timer -= dt
        
        # Handle coordinated attack timing
        if self.coordinated_attack_timer > 0:
            self.coordinated_attack_timer -= dt
            if self.coordinated_attack_timer <= 0:
                self._initiate_coordinated_attack()
        
        if self.formation_timer <= 0:
            self._disband_formation()
        else:
            self._maintain_formation()
    
    def _initiate_coordinated_attack(self):
        """Start coordinated group attack"""
        self.is_coordinated_attacking = True
        
        # Give all formation enemies attack boost and sync their attacks
        for enemy in self.enemies:
            if hasattr(enemy, 'in_formation') and enemy.in_formation:
                enemy.coordinated_attack = True
                enemy.attack_cooldown = max(0, enemy.attack_cooldown - 0.5)  # Reduce cooldown
                enemy.attack_boost = 1.3  # Damage boost during coordinated attack
                
        # Coordinated attack lasts for limited time
        self.coordinated_attack_timer = -2.0  # Negative means coordinated attack active
    
    def _maintain_formation(self):
        """Enhanced formation maintenance with role-based behavior"""
        for enemy in self.enemies:
            if not hasattr(enemy, 'formation_target'):
                continue
            
            target_x, target_y = enemy.formation_target
            distance = math.hypot(target_x - enemy.x, target_y - enemy.y)
            role = getattr(enemy, 'formation_role', 'default')
            
            # Role-based movement priority and behavior
            if role == "ranged":
                # Ranged enemies prioritize staying in safe positions
                enemy.formation_priority = 0.8 if distance > 30 else 0.3
                enemy.preferred_distance = 150  # Stay far from player
            elif role == "protector":
                # Protectors balance between formation and protecting ranged allies
                enemy.formation_priority = 0.6 if distance > 25 else 0.4
                # Check if any ranged ally needs protection
                for ranged in self.ranged_enemies:
                    if hasattr(ranged, 'in_formation'):
                        ranged_distance = math.hypot(enemy.x - ranged.x, enemy.y - ranged.y)
                        if ranged_distance > 100:  # Too far from ranged ally
                            enemy.formation_priority = 0.8
                            break
            elif role == "assault":
                # Assault enemies are more aggressive, move faster to position
                enemy.formation_priority = 0.7 if distance > 20 else 0.2
                enemy.attack_boost = getattr(enemy, 'attack_boost', 1.0)
            else:
                enemy.formation_priority = 0.5 if distance > 25 else 0.2
            
            # Enhanced coordinated attack behavior
            if self.is_coordinated_attacking and self.coordinated_attack_timer < 0:
                enemy.formation_priority *= 0.5  # Less formation focus during attack
                if self.coordinated_attack_timer <= -2.0:  # End coordinated attack
                    self.is_coordinated_attacking = False
                    enemy.coordinated_attack = False
                    enemy.attack_boost = 1.0
    
    def _disband_formation(self):
        """Enhanced formation cleanup"""
        self.is_active = False
        self.is_coordinated_attacking = False
        self.formation_timer = random.uniform(4.0, 8.0)
        
        for enemy in self.enemies:
            if hasattr(enemy, 'in_formation'):
                enemy.in_formation = False
                enemy.formation_priority = 0
                enemy.coordinated_attack = False
                enemy.attack_boost = 1.0
                
                # Clean up formation attributes
                for attr in ['formation_target', 'formation_role', 'preferred_distance']:
                    if hasattr(enemy, attr):
                        delattr(enemy, attr)

class TacticalAI:
    """Enhanced AI coordinator with role-based tactics"""
    
    def __init__(self):
        self.combat_formation = None
    
    def update_enemy_ai(self, enemy, dt: float, player, all_enemies: List):
        """Advanced AI with formation, role-based, and tactical awareness"""
        if hasattr(enemy, 'in_formation') and enemy.in_formation:
            self._formation_ai(enemy, dt, player, all_enemies)
        else:
            self._tactical_ai(enemy, dt, player, all_enemies)
    
    def _formation_ai(self, enemy, dt: float, player, all_enemies: List):
        """Enhanced formation AI with role-based behavior and coordinated attacks"""
        if not hasattr(enemy, 'formation_target'):
            return
        
        target_x, target_y = enemy.formation_target
        priority = getattr(enemy, 'formation_priority', 0.5)
        role = getattr(enemy, 'formation_role', 'default')
        
        # Move toward formation position with role considerations
        dx, dy = target_x - enemy.x, target_y - enemy.y
        distance = math.hypot(dx, dy)
        
        if distance > 15:
            speed = enemy.speed * priority * dt
            
            # Role-based speed modifiers
            if role == "assault":
                speed *= 1.3  # Assault units move faster
            elif role == "ranged":
                speed *= 0.8  # Ranged units move more cautiously
            
            enemy.x += (dx / distance) * speed
            enemy.y += (dy / distance) * speed
        
        # Enhanced combat behavior based on role and coordination
        player_dist = math.hypot(player.x - enemy.x, player.y - enemy.y)
        attack_boost = getattr(enemy, 'attack_boost', 1.0)
        coordinated = getattr(enemy, 'coordinated_attack', False)
        
        # Role-based combat behavior
        if role == "ranged":
            # Ranged enemies maintain distance and have enhanced accuracy during formation
            preferred_dist = getattr(enemy, 'preferred_distance', 120)
            if player_dist < preferred_dist - 20:
                # Move away from player
                flee_dx = enemy.x - player.x
                flee_dy = enemy.y - player.y
                flee_distance = math.hypot(flee_dx, flee_dy)
                if flee_distance > 0:
                    flee_speed = enemy.speed * 0.6 * dt
                    enemy.x += (flee_dx / flee_distance) * flee_speed
                    enemy.y += (flee_dy / flee_distance) * flee_speed
            
            # Enhanced ranged attack during formation
            if player_dist <= enemy.attack_range and enemy.attack_cooldown <= 0:
                enemy._initiate_ranged_attack(player, accuracy_boost=0.3 if coordinated else 0.1)
        
        elif role == "protector":
            # Protectors prioritize defending ranged allies
            ranged_allies = [e for e in all_enemies 
                           if e != enemy and e.type in ["fireshooter", "sniper"] 
                           and hasattr(e, 'in_formation')]
            
            # Check if any ranged ally is under threat
            threatened_ally = None
            for ally in ranged_allies:
                ally_player_dist = math.hypot(player.x - ally.x, player.y - ally.y)
                if ally_player_dist < 80:  # Player too close to ranged ally
                    threatened_ally = ally
                    break
            
            if threatened_ally:
                # Position between player and threatened ally
                intercept_x = (player.x + threatened_ally.x) / 2
                intercept_y = (player.y + threatened_ally.y) / 2
                intercept_dx = intercept_x - enemy.x
                intercept_dy = intercept_y - enemy.y
                intercept_dist = math.hypot(intercept_dx, intercept_dy)
                
                if intercept_dist > 10:
                    speed = enemy.speed * 1.2 * dt  # Move faster to intercept
                    enemy.x += (intercept_dx / intercept_dist) * speed
                    enemy.y += (intercept_dy / intercept_dist) * speed
            
            # Attack when in range
            if player_dist <= enemy.attack_range and enemy.attack_cooldown <= 0:
                if enemy.type in ["crawler", "brute"]:
                    damage = enemy.attack_power * attack_boost
                    player.take_damage(int(damage), enemy=enemy)
                    enemy.attack_cooldown = 0.8 if coordinated else 1.0
                else:
                    enemy._initiate_ranged_attack(player)
        
        elif role == "assault":
            # Assault enemies are more aggressive and coordinated
            if player_dist <= enemy.attack_range and enemy.attack_cooldown <= 0:
                if enemy.type in ["crawler", "brute"]:
                    damage = enemy.attack_power * attack_boost
                    player.take_damage(int(damage), enemy=enemy)
                    enemy.attack_cooldown = 0.6 if coordinated else 0.8  # Faster attacks
                else:
                    enemy._initiate_ranged_attack(player, accuracy_boost=0.2 if coordinated else 0)
            
            # Move more aggressively toward player when coordinated
            if coordinated and player_dist > enemy.attack_range:
                charge_dx = player.x - enemy.x
                charge_dy = player.y - enemy.y
                charge_dist = math.hypot(charge_dx, charge_dy)
                if charge_dist > 0:
                    charge_speed = enemy.speed * 0.4 * dt
                    enemy.x += (charge_dx / charge_dist) * charge_speed
                    enemy.y += (charge_dy / charge_dist) * charge_speed
        
        else:  # Default role
            # Standard formation combat
            if player_dist <= enemy.attack_range and enemy.attack_cooldown <= 0:
                if enemy.type in ["crawler", "brute"]:
                    damage = enemy.attack_power * attack_boost
                    player.take_damage(int(damage), enemy=enemy)
                    enemy.attack_cooldown = 1.0
                else:
                    enemy._initiate_ranged_attack(player)
    
    def _tactical_ai(self, enemy, dt: float, player, all_enemies: List):
        """Enhanced standard AI with improved coordination"""
        nearby = [e for e in all_enemies if e != enemy and 
                 math.hypot(e.x - enemy.x, e.y - enemy.y) < 100]
        
        if len(nearby) >= 2:
            self._coordinated_movement(enemy, dt, player, nearby)
        else:
            # Enhanced individual AI
            enemy._standard_ai(dt, player)
    
    def _coordinated_movement(self, enemy, dt: float, player, allies: List):
        """Enhanced coordinated positioning with enemy type considerations"""
        player_angle = math.atan2(player.y - enemy.y, player.x - enemy.x)
        
        # Type-based positioning
        if enemy.type in ["fireshooter", "sniper"]:
            # Ranged enemies stay back and spread out
            spread = len(allies) * 0.6
            optimal_distance = 160
        elif enemy.type == "brute":
            # Brutes take point positions
            spread = len(allies) * 0.3
            optimal_distance = 60
        else:  # Crawlers
            spread = len(allies) * 0.4
            optimal_distance = 80
        
        optimal_angle = player_angle + spread
        target_x = player.x + math.cos(optimal_angle) * optimal_distance
        target_y = player.y + math.sin(optimal_angle) * optimal_distance
        
        # Move toward optimal position
        dx, dy = target_x - enemy.x, target_y - enemy.y
        distance = math.hypot(dx, dy)
        
        if distance > 20:
            speed = enemy.speed * dt * 0.8
            enemy.x += (dx / distance) * speed
            enemy.y += (dy / distance) * speed
