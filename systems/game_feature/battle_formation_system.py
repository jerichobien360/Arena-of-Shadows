from dataclasses import dataclass
from typing import List, Tuple, Optional
import random
import math


@dataclass
class FormationSystem:
    """Intelligent formation system with natural enemy behavior."""
    cooldown: float = 0.0
    min_enemies: int = 4  # More flexible threshold
    proximity_threshold: int = 14400  # 120^2 for distance check
    last_formation_style: Optional[str] = None
    formation_attempts: int = 0
    
    def should_form(self, enemies: List, player) -> bool:
        """Intelligent formation trigger with context awareness."""
        if len(enemies) < self.min_enemies or self.cooldown > 0:
            return False
        
        # Dynamic proximity threshold based on player behavior
        # If player is moving fast, enemies need to be closer to coordinate
        player_speed = getattr(player, 'speed', 0)
        dynamic_threshold = self.proximity_threshold * (1.2 if player_speed > 50 else 1.0)
        
        # Use full enemy list, but with smart sampling for performance
        sample_size = min(15, len(enemies))
        enemies_sample = random.sample(enemies, sample_size) if len(enemies) > sample_size else enemies
        
        # Count proximity clusters with weighted scoring
        close_pairs = 0
        cluster_bonus = 0
        
        for i, e1 in enumerate(enemies_sample):
            nearby_count = 0
            for e2 in enemies_sample[i+1:]:
                dist_sq = self._distance_squared(e1, e2)
                if dist_sq < dynamic_threshold:
                    close_pairs += 1
                    nearby_count += 1
                    # Bonus for very tight clusters (more tactical)
                    if dist_sq < dynamic_threshold * 0.5:
                        cluster_bonus += 1
        
        # Adaptive threshold based on enemy density and previous attempts
        base_threshold = max(2, sample_size // 4)
        
        # Reduce threshold if previous attempts failed (enemies are trying harder)
        if self.formation_attempts > 2:
            base_threshold = max(1, base_threshold - 1)
        
        formation_score = close_pairs + cluster_bonus
        should_form = formation_score >= base_threshold
        
        if not should_form:
            self.formation_attempts += 1
        else:
            self.formation_attempts = 0  # Reset on success
            
        return should_form
    
    def create_formation(self, enemies: List, player) -> None:
        """Create intelligent formation with contextual positioning."""
        if not enemies:
            return

        # Choose formation intelligently based on context
        formation_style = self._choose_intelligent_formation(len(enemies), player)
        positions = self._get_formation_positions(len(enemies), player, formation_style)

        # Stagger formation assignment to look more natural
        assignment_delay = 0.0
        
        for i, (enemy, pos) in enumerate(zip(enemies, positions)):
            # Natural positioning variation based on enemy "personality"
            enemy_id = id(enemy) % 1000  # Use object id for consistency
            random.seed(enemy_id)  # Consistent randomness per enemy
            
            # Larger, more natural offset ranges
            offset_x = random.uniform(-15, 15)
            offset_y = random.uniform(-15, 15)
            
            # Some enemies are "messier" than others
            messiness = (enemy_id % 3) * 5
            offset_x += random.uniform(-messiness, messiness)
            offset_y += random.uniform(-messiness, messiness)
            
            # Set formation target with natural offset
            enemy.form_target = (pos[0] + offset_x, pos[1] + offset_y)
            
            # Initialize attributes naturally
            enemy.form_active = True
            enemy.formation_buffer = 0.3 + random.uniform(0, 0.4)  # Varied timing
            enemy.formation_assignment_delay = assignment_delay
            
            # Stagger assignments for natural look
            assignment_delay += random.uniform(0.05, 0.15)
            
            # Reset seed for next iteration
            random.seed()

        # Longer, more varied cooldown
        self.cooldown = random.uniform(2.0, 4.0)
        self.last_formation_style = formation_style
    
    def update(self, dt: float, enemies: List, player) -> None:
        """Update with natural, intelligent behavior."""
        self.cooldown = max(0, self.cooldown - dt)

        # Handle formation assignment delays
        for enemy in enemies:
            if hasattr(enemy, 'formation_assignment_delay'):
                if enemy.formation_assignment_delay > 0:
                    enemy.formation_assignment_delay -= dt
                    if enemy.formation_assignment_delay <= 0:
                        # Enemy just received formation orders
                        if hasattr(enemy, 'form_target'):
                            enemy.form_active = True

        # Natural formation maintenance
        active_enemies = [
            e for e in enemies 
            if getattr(e, 'form_active', False) and getattr(e, 'hp', 1) > 0
        ]
        
        # Update buffers with natural variation
        for enemy in active_enemies:
            if not hasattr(enemy, 'formation_buffer'):
                enemy.formation_buffer = 0.0
            if enemy.formation_buffer > 0:
                enemy.formation_buffer -= dt
        
        # Natural formation breakdown - not instant
        if len(active_enemies) < 3:
            # Enemies gradually lose formation discipline
            for enemy in active_enemies:
                if getattr(enemy, 'formation_buffer', 0) <= 0:
                    # Some enemies abandon formation, others try to maintain it
                    if random.random() < 0.7:  # 70% chance to abandon
                        enemy.form_active = False
                    else:
                        # Reset buffer to keep trying
                        enemy.formation_buffer = random.uniform(1.0, 2.0)

        # Intelligent formation creation
        inactive_enemies = [
            e for e in enemies 
            if not getattr(e, 'form_active', False) and getattr(e, 'hp', 1) > 0
        ]
        
        if self.should_form(inactive_enemies, player):
            self.create_formation(inactive_enemies, player)
    
    def _choose_intelligent_formation(self, count: int, player) -> str:
        """Choose formation based on tactical situation."""
        # Avoid repeating the same formation immediately
        available_styles = ["wall", "wedge", "pincer", "block", "circle"]
        if self.last_formation_style in available_styles:
            available_styles.remove(self.last_formation_style)
        
        # Choose based on enemy count and tactical situation
        player_x = getattr(player, 'x', 0)
        player_y = getattr(player, 'y', 0)
        
        # Prefer certain formations based on context
        if count <= 6:
            return "circle"
        elif count >= 12:
            # Large groups prefer organized formations
            return random.choice(["wall", "block"])
        else:
            # Medium groups use varied tactics
            weights = {
                "wall": 0.25,
                "wedge": 0.3,
                "pincer": 0.25,
                "block": 0.2
            }
            
            # Adjust weights based on situation
            if hasattr(player, 'near_wall') and player.near_wall:
                weights["pincer"] *= 1.5  # Pincer when player is cornered
                
            # Weighted random selection
            styles = list(weights.keys())
            weight_values = list(weights.values())
            return random.choices(styles, weights=weight_values)[0]
    
    def _distance_squared(self, e1, e2) -> float:
        """Calculate squared distance between two enemies."""
        return (e1.x - e2.x)**2 + (e1.y - e2.y)**2
    
    def _get_formation_positions(self, count: int, player, style: str) -> List[Tuple[float, float]]:
        """Generate formation positions with intelligent spacing."""
        
        if style == "circle" or count <= 6:
            # Dynamic circle radius based on enemy count
            radius = 50 + (count * 8)  # Larger circles for more enemies
            return [
                (player.x + radius * math.cos(2 * math.pi * i / count),
                 player.y + radius * math.sin(2 * math.pi * i / count))
                for i in range(count)
            ]

        elif style == "wall":
            # Intelligent wall formation
            wall_distance = 80 + random.uniform(-10, 10)  # Varied distance
            spacing = max(25, 60 - count)  # Tighter spacing for more enemies
            start_x = player.x - (count // 2) * spacing
            y = player.y + wall_distance
            return [(start_x + i * spacing, y) for i in range(count)]

        elif style == "wedge":
            # Adaptive V-formation
            wedge_distance = 70 + random.uniform(-10, 10)
            spacing = max(25, 50 - count // 2)
            positions = []
            mid = count // 2
            for i in range(count):
                offset = (i - mid)
                x = player.x + offset * spacing
                # More dramatic wedge for larger groups
                depth_multiplier = 15 + (count // 3)
                y = player.y + wedge_distance + abs(offset) * depth_multiplier
                positions.append((x, y))
            return positions

        elif style == "pincer":
            # Intelligent flanking maneuver
            flank_distance = 80 + random.uniform(-15, 15)
            spacing = max(30, 50 - count // 4)
            left = count // 2
            right = count - left
            
            # Asymmetric positioning for more natural look
            left_x = player.x - (100 + random.uniform(-20, 20))
            right_x = player.x + (100 + random.uniform(-20, 20))
            
            left_flank = [
                (left_x, player.y + (i - left//2) * spacing + flank_distance) 
                for i in range(left)
            ]
            right_flank = [
                (right_x, player.y + (i - right//2) * spacing + flank_distance) 
                for i in range(right)
            ]
            return left_flank + right_flank

        elif style == "block":
            # Adaptive phalanx formation
            rows = max(2, min(4, int(math.sqrt(count))))  # Limit max rows
            cols = (count + rows - 1) // rows
            spacing_x = max(25, 40 - count // 4)
            spacing_y = max(25, 40 - count // 4)
            
            # Add some natural irregularity to the block
            base_x = player.x
            base_y = player.y + 70
            
            positions = []
            for i in range(count):
                row = i // cols
                col = i % cols
                
                # Add slight row staggering for natural look
                row_offset = (row % 2) * (spacing_x // 4)
                
                x = base_x + (col - cols // 2) * spacing_x + row_offset
                y = base_y + row * spacing_y
                positions.append((x, y))
            return positions

        # Fallback to circle
        return [
            (player.x + 70 * math.cos(2 * math.pi * i / count),
             player.y + 70 * math.sin(2 * math.pi * i / count))
            for i in range(count)
        ]
