"""Combat system implies with the formation, tactics, and optimization"""

from settings import *
import pygame
import math
import random
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


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
    role: str = "default"
    assigned: bool = False
    priority: int = 1

    @property
    def pos(self) -> Tuple[float, float]:
        return (self.x, self.y)


class QuickFormation:
    """Advanced enemy formation system with ranged protection and coordinated attacks"""
    
    def __init__(self, enemies: List, player):
        self.enemies = enemies
        self.player = player
        self.formation_type: Optional[FormationType] = None
        self.positions: List[FormationPosition] = []
        self.formation_timer = 0.0
        self.is_active = False
        self.coordinated_attack_timer = 0.0
        self.is_coordinated_attacking = False
        
    @property
    def ranged_enemies(self):
        return [e for e in self.enemies if e.type in {"fireshooter", "sniper"}]
    
    @property
    def melee_enemies(self):
        return [e for e in self.enemies if e.type in {"crawler", "brute"}]
    
    @property
    def player_pos(self) -> Tuple[float, float]:
        return (self.player.x, self.player.y)
    
    def _distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        return math.hypot(pos1[0] - pos2[0], pos1[1] - pos2[1])
    
    def _angle_between(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        return math.atan2(pos2[1] - pos1[1], pos2[0] - pos1[0])
    
    def _position_at_angle(self, center: Tuple[float, float], angle: float, distance: float) -> Tuple[float, float]:
        return (center[0] + distance * math.cos(angle), center[1] + distance * math.sin(angle))
    
    def should_regroup(self) -> bool:
        """Determine if enemies should form up based on tactical situation"""
        if len(self.enemies) < 3 or self.formation_timer > 0:
            return False
        
        # Check if ranged enemies need protection
        for ranged in self.ranged_enemies:
            ranged_pos = (ranged.x, ranged.y)
            nearby_protectors = sum(
                1 for melee in self.melee_enemies 
                if self._distance((melee.x, melee.y), ranged_pos) < 80
            )
            if nearby_protectors < 2:
                return True
        
        # Check enemy clustering
        close_pairs = sum(
            1 for i, e1 in enumerate(self.enemies) 
            for e2 in self.enemies[i+1:] 
            if self._distance((e1.x, e1.y), (e2.x, e2.y)) < 120
        )
        
        return close_pairs >= max(2, len(self.enemies) // 3)
    
    def initiate_formation(self):
        """Set up formation based on enemy composition and tactical needs"""
        if not self.enemies:
            return
        
        self.formation_type = self._select_formation_type()
        self.positions = self._create_formation_positions()
        self._assign_enemies_to_positions()
        
        self.is_active = True
        self.formation_timer = random.uniform(8.0, 12.0)
        
        # Set up coordinated attacks for aggressive formations
        if self.formation_type in {FormationType.TRIANGLE_ASSAULT, FormationType.ENCIRCLE_TRAP}:
            self.coordinated_attack_timer = random.uniform(2.0, 4.0)
    
    def _select_formation_type(self) -> FormationType:
        """Choose formation type based on enemy composition"""
        enemy_count = len(self.enemies)
        ranged_count = len(self.ranged_enemies)
        melee_count = len(self.melee_enemies)
        
        if ranged_count > 0 and melee_count >= ranged_count * 2:
            return FormationType.PROTECT_RANGED
        elif enemy_count >= 6 and melee_count >= 4:
            return random.choice([FormationType.ENCIRCLE_TRAP, FormationType.TRIANGLE_ASSAULT])
        elif enemy_count <= 6:
            return FormationType.SURROUND
        elif enemy_count <= 10:
            return FormationType.PINCER
        else:
            return FormationType.AMBUSH
    
    def _create_formation_positions(self) -> List[FormationPosition]:
        """Create positions based on formation type"""
        formation_creators = {
            FormationType.PROTECT_RANGED: self._create_protection_formation,
            FormationType.TRIANGLE_ASSAULT: self._create_triangle_assault,
            FormationType.ENCIRCLE_TRAP: self._create_encircle_trap,
            FormationType.SURROUND: self._create_surround_formation,
            FormationType.PINCER: self._create_pincer_formation,
            FormationType.AMBUSH: self._create_ambush_formation,
        }
        
        return formation_creators[self.formation_type]()
    
    def _create_protection_formation(self) -> List[FormationPosition]:
        """Create formation to protect ranged enemies"""
        positions = []
        ranged_count = len(self.ranged_enemies)
        melee_count = len(self.melee_enemies)
        
        # Position ranged enemies safely
        for i in range(ranged_count):
            angle = (2 * math.pi * i / ranged_count) + math.pi
            x, y = self._position_at_angle(self.player_pos, angle, 180)
            positions.append(FormationPosition(x, y, "ranged", priority=3))
        
        # Position melee as protectors
        for i in range(melee_count):
            if i < ranged_count * 2:  # Primary protectors
                angle = 2 * math.pi * i / max(1, ranged_count * 2)
                x, y = self._position_at_angle(self.player_pos, angle, 100)
                positions.append(FormationPosition(x, y, "protector", priority=2))
            else:  # Flankers
                angle = 2 * math.pi * (i - ranged_count * 2) / max(1, melee_count - ranged_count * 2)
                x, y = self._position_at_angle(self.player_pos, angle, 90)
                positions.append(FormationPosition(x, y, "flanker", priority=1))
        
        return positions
    
    def _create_triangle_assault(self) -> List[FormationPosition]:
        """Create triangle formation for coordinated assault"""
        positions = []
        enemy_count = len(self.enemies)
        triangle_angles = [0, 2*math.pi/3, 4*math.pi/3]
        
        # Create triangle tips
        for angle in triangle_angles:
            x, y = self._position_at_angle(self.player_pos, angle, 120)
            positions.append(FormationPosition(x, y, "assault", priority=3))
        
        # Fill triangle sides
        remaining = enemy_count - 3
        for i in range(remaining):
            side = i % 3
            t = (i // 3 + 1) / max(1, (remaining // 3 + 1))
            
            angle1, angle2 = triangle_angles[side], triangle_angles[(side + 1) % 3]
            x = self.player_pos[0] + 120 * (math.cos(angle1) * (1 - t) + math.cos(angle2) * t)
            y = self.player_pos[1] + 120 * (math.sin(angle1) * (1 - t) + math.sin(angle2) * t)
            
            positions.append(FormationPosition(x, y, "assault", priority=2))
        
        return positions
    
    def _create_encircle_trap(self) -> List[FormationPosition]:
        """Create encircling formation to trap player"""
        positions = []
        enemy_count = len(self.enemies)
        inner_count = min(enemy_count // 2, 6)
        outer_count = enemy_count - inner_count
        
        # Inner circle
        for i in range(inner_count):
            angle = 2 * math.pi * i / inner_count
            x, y = self._position_at_angle(self.player_pos, angle, 80)
            positions.append(FormationPosition(x, y, "assault", priority=3))
        
        # Outer circle
        for i in range(outer_count):
            angle = 2 * math.pi * i / outer_count + math.pi / outer_count
            x, y = self._position_at_angle(self.player_pos, angle, 140)
            positions.append(FormationPosition(x, y, "flanker", priority=2))
        
        return positions
    
    def _create_surround_formation(self) -> List[FormationPosition]:
        """Create surrounding circle formation"""
        enemy_count = len(self.enemies)
        return [
            FormationPosition(*self._position_at_angle(self.player_pos, 2 * math.pi * i / enemy_count, 120))
            for i in range(enemy_count)
        ]
    
    def _create_pincer_formation(self) -> List[FormationPosition]:
        """Create pincer movement formation"""
        enemy_count = len(self.enemies)
        return [
            FormationPosition(
                self.player_pos[0] + (-160 if i < enemy_count // 2 else 160),
                self.player_pos[1] + (i - enemy_count // 4) * 45
            ) for i in range(enemy_count)
        ]
    
    def _create_ambush_formation(self) -> List[FormationPosition]:
        """Create ambush positions around player"""
        return [
            FormationPosition(
                self.player_pos[0] + random.randint(-250, 250),
                self.player_pos[1] + random.randint(-250, 250)
            ) for _ in range(len(self.enemies))
        ]
    
    def _assign_enemies_to_positions(self):
        """Assign enemies to positions based on roles and priorities"""
        sorted_positions = sorted(self.positions, key=lambda p: p.priority, reverse=True)
        available_enemies = list(self.enemies)
        
        role_preferences = {
            "ranged": {"fireshooter", "sniper"},
            "protector": {"brute", "crawler"},
            "assault": {"brute", "crawler"},
        }
        
        for pos in sorted_positions:
            if not available_enemies:
                break
            
            # Find best enemy for this role
            preferred_types = role_preferences.get(pos.role, set())
            candidates = [e for e in available_enemies if e.type in preferred_types] or available_enemies
            
            # Choose closest suitable enemy
            best_enemy = min(candidates, key=lambda e: self._distance((e.x, e.y), pos.pos))
            
            # Assign enemy to position
            self._assign_enemy_to_position(best_enemy, pos)
            available_enemies.remove(best_enemy)
    
    def _assign_enemy_to_position(self, enemy, position: FormationPosition):
        """Assign an enemy to a specific formation position"""
        enemy.formation_target = position.pos
        enemy.formation_role = position.role
        enemy.in_formation = True
        position.assigned = True
    
    def update(self, dt: float):
        """Update formation state and coordinated attacks"""
        if not self.is_active:
            if self.should_regroup():
                self.initiate_formation()
            return
        
        self.formation_timer -= dt
        
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
        
        for enemy in self.enemies:
            if getattr(enemy, 'in_formation', False):
                enemy.coordinated_attack = True
                enemy.attack_cooldown = max(0, enemy.attack_cooldown - 0.5)
                enemy.attack_boost = 1.3
        
        self.coordinated_attack_timer = -2.0  # Duration of coordinated attack
    
    def _maintain_formation(self):
        """Maintain formation positions and update enemy behavior"""
        for enemy in self.enemies:
            if not hasattr(enemy, 'formation_target'):
                continue
            
            self._update_enemy_formation_behavior(enemy)
    
    def _update_enemy_formation_behavior(self, enemy):
        """Update individual enemy behavior within formation"""
        target_pos = enemy.formation_target
        distance = self._distance((enemy.x, enemy.y), target_pos)
        role = getattr(enemy, 'formation_role', 'default')
        
        # Role-based priorities and behaviors
        role_configs = {
            "ranged": {"priority": 0.8 if distance > 30 else 0.3, "preferred_distance": 150},
            "protector": {"priority": 0.6 if distance > 25 else 0.4, "check_allies": True},
            "assault": {"priority": 0.7 if distance > 20 else 0.2, "attack_boost": True},
            "default": {"priority": 0.5 if distance > 25 else 0.2}
        }
        
        config = role_configs.get(role, role_configs["default"])
        enemy.formation_priority = config["priority"]
        
        if "preferred_distance" in config:
            enemy.preferred_distance = config["preferred_distance"]
        
        if config.get("check_allies") and role == "protector":
            self._check_protector_duties(enemy)
        
        # Handle coordinated attack behavior
        if self.is_coordinated_attacking and self.coordinated_attack_timer < 0:
            enemy.formation_priority *= 0.5
            
            if self.coordinated_attack_timer <= -2.0:
                self._end_coordinated_attack(enemy)
    
    def _check_protector_duties(self, protector):
        """Check if protector needs to defend ranged allies"""
        for ranged in self.ranged_enemies:
            if hasattr(ranged, 'in_formation'):
                ally_distance = self._distance((protector.x, protector.y), (ranged.x, ranged.y))
                if ally_distance > 100:
                    protector.formation_priority = 0.8
                    break
    
    def _end_coordinated_attack(self, enemy):
        """End coordinated attack for an enemy"""
        self.is_coordinated_attacking = False
        enemy.coordinated_attack = False
        enemy.attack_boost = 1.0
    
    def _disband_formation(self):
        """Clean up formation and reset enemy states"""
        self.is_active = False
        self.is_coordinated_attacking = False
        self.formation_timer = random.uniform(4.0, 8.0)
        
        formation_attrs = ['formation_target', 'formation_role', 'preferred_distance', 'in_formation']
        
        for enemy in self.enemies:
            if hasattr(enemy, 'in_formation'):
                enemy.formation_priority = 0
                enemy.coordinated_attack = False
                enemy.attack_boost = 1.0
                
                for attr in formation_attrs:
                    if hasattr(enemy, attr):
                        delattr(enemy, attr)


class TacticalAI:
    """Enhanced AI coordinator with role-based tactics"""
    
    def __init__(self):
        self.combat_formation: Optional[QuickFormation] = None
    
    def update_enemy_ai(self, enemy, dt: float, player, all_enemies: List):
        """Update enemy AI based on formation status"""
        if getattr(enemy, 'in_formation', False):
            self._formation_ai(enemy, dt, player, all_enemies)
        else:
            self._tactical_ai(enemy, dt, player, all_enemies)
    
    def _formation_ai(self, enemy, dt: float, player, all_enemies: List):
        """Handle AI for enemies in formation"""
        if not hasattr(enemy, 'formation_target'):
            return
        
        self._move_to_formation_position(enemy, dt)
        self._execute_formation_combat(enemy, player, all_enemies)
    
    def _move_to_formation_position(self, enemy, dt: float):
        """Move enemy towards their formation position"""
        target_x, target_y = enemy.formation_target
        dx, dy = target_x - enemy.x, target_y - enemy.y
        distance = math.hypot(dx, dy)
        
        if distance <= 15:
            return
        
        priority = getattr(enemy, 'formation_priority', 0.5)
        role = getattr(enemy, 'formation_role', 'default')
        
        # Role-based speed modifiers
        speed_modifiers = {"assault": 1.3, "ranged": 0.8}
        speed_modifier = speed_modifiers.get(role, 1.0)
        
        speed = enemy.speed * priority * speed_modifier * dt
        enemy.x += (dx / distance) * speed
        enemy.y += (dy / distance) * speed
    
    def _execute_formation_combat(self, enemy, player, all_enemies: List):
        """Execute role-based combat behavior"""
        role = getattr(enemy, 'formation_role', 'default')
        player_dist = math.hypot(player.x - enemy.x, player.y - enemy.y)
        
        combat_handlers = {
            "ranged": self._handle_ranged_combat,
            "protector": self._handle_protector_combat,
            "assault": self._handle_assault_combat,
        }
        
        handler = combat_handlers.get(role, self._handle_default_combat)
        handler(enemy, player, all_enemies, player_dist)
    
    def _handle_ranged_combat(self, enemy, player, all_enemies: List, player_dist: float):
        """Handle combat for ranged enemies"""
        preferred_dist = getattr(enemy, 'preferred_distance', 120)
        
        if player_dist < preferred_dist - 20:
            self._retreat_from_player(enemy, player)
        
        if player_dist <= enemy.attack_range and enemy.attack_cooldown <= 0:
            coordinated = getattr(enemy, 'coordinated_attack', False)
            accuracy_boost = 0.3 if coordinated else 0.1
            enemy._initiate_ranged_attack(player, accuracy_boost=accuracy_boost)
    
    def _handle_protector_combat(self, enemy, player, all_enemies: List, player_dist: float):
        """Handle combat for protector enemies"""
        threatened_ally = self._find_threatened_ranged_ally(player, all_enemies)
        
        if threatened_ally:
            self._intercept_threat(enemy, player, threatened_ally)
        
        if player_dist <= enemy.attack_range and enemy.attack_cooldown <= 0:
            self._execute_attack(enemy, player)
    
    def _handle_assault_combat(self, enemy, player, all_enemies: List, player_dist: float):
        """Handle combat for assault enemies"""
        coordinated = getattr(enemy, 'coordinated_attack', False)
        
        if player_dist <= enemy.attack_range and enemy.attack_cooldown <= 0:
            cooldown = 0.6 if coordinated else 0.8
            self._execute_attack(enemy, player, cooldown)
        elif coordinated and player_dist > enemy.attack_range:
            self._charge_player(enemy, player)
    
    def _handle_default_combat(self, enemy, player, all_enemies: List, player_dist: float):
        """Handle default combat behavior"""
        if player_dist <= enemy.attack_range and enemy.attack_cooldown <= 0:
            self._execute_attack(enemy, player)
    
    def _retreat_from_player(self, enemy, player):
        """Move enemy away from player"""
        dx, dy = enemy.x - player.x, enemy.y - player.y
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            speed = enemy.speed * 0.6
            enemy.x += (dx / distance) * speed
            enemy.y += (dy / distance) * speed
    
    def _find_threatened_ranged_ally(self, player, all_enemies: List) -> Optional[object]:
        """Find ranged ally that needs protection"""
        ranged_allies = [
            e for e in all_enemies 
            if e.type in {"fireshooter", "sniper"} and hasattr(e, 'in_formation')
        ]
        
        for ally in ranged_allies:
            if math.hypot(player.x - ally.x, player.y - ally.y) < 80:
                return ally
        
        return None
    
    def _intercept_threat(self, enemy, player, threatened_ally):
        """Position enemy between player and threatened ally"""
        intercept_x = (player.x + threatened_ally.x) / 2
        intercept_y = (player.y + threatened_ally.y) / 2
        
        dx, dy = intercept_x - enemy.x, intercept_y - enemy.y
        distance = math.hypot(dx, dy)
        
        if distance > 10:
            speed = enemy.speed * 1.2
            enemy.x += (dx / distance) * speed
            enemy.y += (dy / distance) * speed
    
    def _charge_player(self, enemy, player):
        """Move enemy aggressively toward player"""
        dx, dy = player.x - enemy.x, player.y - enemy.y
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            speed = enemy.speed * 0.4
            enemy.x += (dx / distance) * speed
            enemy.y += (dy / distance) * speed
    
    def _execute_attack(self, enemy, player, cooldown: float = 1.0):
        """Execute enemy attack on player"""
        attack_boost = getattr(enemy, 'attack_boost', 1.0)
        
        if enemy.type in {"crawler", "brute"}:
            damage = enemy.attack_power * attack_boost
            player.take_damage(int(damage), enemy=enemy)
            enemy.attack_cooldown = cooldown
        else:
            enemy._initiate_ranged_attack(player)
    
    def _tactical_ai(self, enemy, dt: float, player, all_enemies: List):
        """Handle AI for enemies not in formation"""
        nearby_allies = [
            e for e in all_enemies 
            if e != enemy and math.hypot(e.x - enemy.x, e.y - enemy.y) < 100
        ]
        
        if len(nearby_allies) >= 2:
            self._coordinated_movement(enemy, dt, player, nearby_allies)
        else:
            enemy._standard_ai(dt, player)
    
    def _coordinated_movement(self, enemy, dt: float, player, allies: List):
        """Coordinate movement with nearby allies"""
        player_angle = math.atan2(player.y - enemy.y, player.x - enemy.x)
        
        # Type-based positioning parameters
        positioning = {
            "fireshooter": {"spread": 0.6, "distance": 160},
            "sniper": {"spread": 0.6, "distance": 160},
            "brute": {"spread": 0.3, "distance": 60},
            "crawler": {"spread": 0.4, "distance": 80},
        }
        
        config = positioning.get(enemy.type, {"spread": 0.4, "distance": 80})
        spread = len(allies) * config["spread"]
        optimal_distance = config["distance"]
        
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
