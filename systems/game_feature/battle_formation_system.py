from dataclasses import dataclass
from typing import List, Tuple
import math



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
