import math
import random
from typing import List
from entities.enemy.enemy_base import FormationType


class SmartFormationAI:
    """Fast, tactical enemy formation system"""
    
    FORMATIONS = {
        FormationType.SURROUND: lambda pos, n: [(pos[0] + 100*math.cos(2*math.pi*i/n), 
                                                pos[1] + 100*math.sin(2*math.pi*i/n)) for i in range(n)],
        FormationType.PINCER: lambda pos, n: [(pos[0] + (-150 if i < n//2 else 150), 
                                              pos[1] + (i-n//4)*40) for i in range(n)],
        FormationType.AMBUSH: lambda pos, n: [(pos[0] + random.randint(-200, 200), 
                                              pos[1] + random.randint(-200, 200)) for i in range(n)]
    }
    
    def __init__(self):
        self.active_groups = {}
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
            enemy.formation.target = pos  # Use dataclass properly
            enemy.formation.active = True
            enemy.group_id = group_id
        
        self.active_groups[group_id] = enemies
        self.cooldown = 5.0  # Shorter cooldown for faster battles
    
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
            
        player_dist = math.hypot(player.x - enemy.x, player.y - enemy.y)
        
        if player_dist <= enemy.attack_range and enemy.attack_cooldown <= 0:
            if enemy.type in ["crawler", "brute"]:
                player.take_damage(enemy.attack_power, enemy=enemy)
                enemy.attack_cooldown = 1.0
            else:
                enemy._initiate_ranged_attack(player)
    
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
        unformed = [e for e in all_enemies if not enemy.formation.active]
        if self.should_regroup(unformed, player):
            self.initiate_formation(unformed, player)
