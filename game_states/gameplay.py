# Enhanced gameplay.py - Streamlined Formation System
from settings import *
from contextlib import contextmanager

# Game entities
from entities.player import *
from entities.enemies import *

# Core systems
from systems.wave_manager import *
from systems.camera import *
from systems.background_system import *

class FastFormations:
    """Ultra-fast formation system optimized for real-time combat"""
    
    def __init__(self):
        self.groups = {}
        self.cooldown = 0
        
    def should_form(self, enemies, player):
        """Quick clustering check - only when many enemies are bunched up"""
        if len(enemies) < 6 or self.cooldown > 0:
            return False
        
        # Fast proximity check - count close pairs
        close = sum(1 for i, e1 in enumerate(enemies[:12])  # Limit check for performance
                   for e2 in enemies[i+1:i+6] 
                   if (e1.x - e2.x)**2 + (e1.y - e2.y)**2 < 14400)  # 120px squared
        
        return close >= len(enemies) // 3  # 1/3 of enemies are clustered
    
    def create_formation(self, enemies, player):
        """Instant formation creation with combat priority"""
        if not enemies:
            return
            
        # Simple formation based on count
        n = len(enemies)
        if n <= 8:
            # Surround formation
            positions = [(player.x + 100 * math.cos(2 * math.pi * i / n),
                         player.y + 100 * math.sin(2 * math.pi * i / n)) for i in range(n)]
        else:
            # Pincer formation
            half = n // 2
            positions = ([(player.x - 140, player.y + (i - half//2) * 35) for i in range(half)] +
                        [(player.x + 140, player.y + (i - half//2) * 35) for i in range(n - half)])
        
        # Assign positions by distance
        for enemy, pos in zip(enemies, positions):
            enemy.form_target = pos
            enemy.form_active = True
        
        self.cooldown = 3.0  # Quick cooldown
    
    def update(self, dt, enemies, player):
        """Minimal update - let enemies handle their own formation movement"""
        self.cooldown = max(0, self.cooldown - dt)
        
        # Clean up dead enemies from formations
        active_enemies = [e for e in enemies if hasattr(e, 'form_active') and e.form_active and e.hp > 0]
        if len(active_enemies) < 3:
            for e in active_enemies:
                e.form_active = False
        
        # Check for new formations
        inactive = [e for e in enemies if not getattr(e, 'form_active', False)]
        if self.should_form(inactive, player):
            self.create_formation(inactive, player)

class GameState:
    """Base class for all game states"""
    def enter(self): pass
    def exit(self): pass
    def update(self, dt): return None
    def render(self, screen): pass

class GameplayState(GameState):
    """Optimized gameplay state with fast formation system"""
    
    def __init__(self, font, sound_manager):
        self.font, self.sound_manager = font, sound_manager
        self.player = self.enemies = None
        self.wave_manager = self.camera = self.background = None
        self.input_handler = InputHandler()
        self.is_paused = self.game_time = 0
        self.formations = FastFormations()
    
    def enter(self):
        """Initialize gameplay"""
        self.game_time = 0
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.background = BackgroundSystem(WORLD_WIDTH, WORLD_HEIGHT)
        self.wave_manager = WaveManager(self.sound_manager)
        self.formations = FastFormations()
        self.player = Player(self.sound_manager, self.camera)
        self.enemies = []
        self.wave_manager.start_wave(1)
        
        # Background music
        self.sound_manager.stop_background_music()
        if self.sound_manager.load_background_music("assets/background_music/gameplay.mp3"):
            self.sound_manager.play_background_music()
    
    def update(self, dt):
        """Main update loop with enhanced combat"""
        if self.is_paused:
            return None
            
        self.game_time += dt
        
        # Input handling
        if next_state := self._handle_input():
            return next_state
        
        # Core updates
        self._update_player(dt)
        self._update_combat_system(dt)
        self._update_systems(dt)
        
        return "game_over" if self.player.hp <= 0 else None
    
    def _handle_input(self):
        """Clean input handling"""
        keys = pygame.key.get_pressed()
        
        if self.input_handler.is_key_just_pressed(pygame.K_ESCAPE):
            return "pause"
        
        if keys[pygame.K_SPACE]:
            self.player.attack(self.enemies)
        
        # Zoom controls
        zoom_change = (keys[pygame.K_EQUALS] - keys[pygame.K_MINUS]) * 0.1
        if zoom_change:
            new_zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.camera.target_zoom + zoom_change))
            self.camera.set_zoom(new_zoom)
        
        return None
    
    def _update_player(self, dt):
        """Update player with boundaries"""
        self.player.update(dt)
        bounds = self.background.get_world_bounds()
        self.player.x = max(bounds[0] + self.player.radius, 
                           min(bounds[2] - self.player.radius, self.player.x))
        self.player.y = max(bounds[1] + self.player.radius, 
                           min(bounds[3] - self.player.radius, self.player.y))
    
    def _update_combat_system(self, dt):
        """Enhanced combat system with smart formations"""
        # Fast formation update
        self.formations.update(dt, self.enemies, self.player)
        
        # Update enemies with enhanced AI
        for enemy in self.enemies[:]:
            if enemy.hp <= 0:
                self.enemies.remove(enemy)
                continue
            
            # Enhanced enemy AI with formation awareness
            if getattr(enemy, 'form_active', False):
                self._formation_combat_ai(enemy, dt)
            else:
                self._enhanced_combat_ai(enemy, dt)
            
            enemy.update(dt, self.player)
    
    def _formation_combat_ai(self, enemy, dt):
        """Formation AI that prioritizes combat over positioning"""
        player_dist = math.hypot(self.player.x - enemy.x, self.player.y - enemy.y)
        
        # Combat has priority over formation
        if player_dist <= enemy.attack_range * 1.2:
            # Close to player - focus on combat
            self._direct_combat(enemy, dt)
        else:
            # Move to formation position, but with combat readiness
            target_x, target_y = enemy.form_target
            dx, dy = target_x - enemy.x, target_y - enemy.y
            dist = math.hypot(dx, dy)
            
            if dist > 25:
                # Move to position at 70% speed to maintain combat awareness
                speed = enemy.speed * 0.7 * dt
                enemy.x += (dx / dist) * speed
                enemy.y += (dy / dist) * speed
            
            # Always ready to attack
            if player_dist <= enemy.attack_range and enemy.attack_cooldown <= 0:
                self._execute_attack(enemy)
    
    def _enhanced_combat_ai(self, enemy, dt):
        """Improved standard AI with tactical awareness"""
        player_dist = math.hypot(self.player.x - enemy.x, self.player.y - enemy.y)
        dx, dy = self.player.x - enemy.x, self.player.y - enemy.y
        
        # Normalize direction
        if player_dist > 0:
            unit_x, unit_y = dx / player_dist, dy / player_dist
        else:
            unit_x = unit_y = 0
        
        # Movement with knockback consideration
        knockback_factor = max(0.4, 1.0 - math.hypot(*enemy.knockback_velocity) / 150)
        move_speed = enemy.speed * knockback_factor * dt
        
        if enemy.type in ["crawler", "brute"]:
            # Aggressive melee approach
            if player_dist > enemy.attack_range:
                enemy.x += unit_x * move_speed
                enemy.y += unit_y * move_speed
            elif enemy.attack_cooldown <= 0:
                self._execute_attack(enemy)
        else:
            # Smart ranged positioning
            preferred_dist = {"sniper": 220, "fireshooter": 100}.get(enemy.type, 150)
            
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
            
            if player_dist <= enemy.attack_range and enemy.attack_cooldown <= 0:
                self._execute_attack(enemy)
    
    def _direct_combat(self, enemy, dt):
        """Direct combat behavior for close-range encounters"""
        player_dist = math.hypot(self.player.x - enemy.x, self.player.y - enemy.y)
        dx, dy = self.player.x - enemy.x, self.player.y - enemy.y
        
        if player_dist > 0:
            unit_x, unit_y = dx / player_dist, dy / player_dist
            
            if enemy.type in ["crawler", "brute"]:
                # Aggressive charge
                if player_dist > enemy.attack_range:
                    speed = enemy.speed * 1.1 * dt  # 10% faster in combat
                    enemy.x += unit_x * speed
                    enemy.y += unit_y * speed
                elif enemy.attack_cooldown <= 0:
                    self._execute_attack(enemy)
            else:
                # Ranged combat positioning
                if player_dist <= enemy.attack_range and enemy.attack_cooldown <= 0:
                    self._execute_attack(enemy)
    
    def _execute_attack(self, enemy):
        """Execute enemy attack based on type"""
        if enemy.type in ["crawler", "brute"]:
            self.player.take_damage(enemy.attack_power, enemy=enemy)
            enemy.attack_cooldown = 0.9  # Slightly faster attacks
        else:
            enemy._initiate_ranged_attack(self.player)
    
    def _update_systems(self, dt):
        """Update core systems"""
        self.background.update(dt)
        self.camera.update(dt, self.player.x, self.player.y)
        
        # Wave management
        if self.wave_manager.update(dt, self.enemies):
            self.wave_manager.start_wave(self.wave_manager.current_wave + 1)
    
    def render(self, screen):
        """Clean rendering without annoying UI elements"""
        screen.fill(BLACK)
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Render world
        self.background.render(screen, self.camera, current_time)
        self._render_entity(screen, self.player)
        
        # Render enemies with culling
        for enemy in self.enemies:
            screen_pos = self.camera.world_to_screen(enemy.x, enemy.y)
            if self._in_view(*screen_pos):
                self._render_entity_at(screen, enemy, screen_pos)
        
        # Clean UI without annoying text
        self._render_ui(screen)
        
        if self.is_paused:
            self._render_pause_overlay(screen)
    
    def _in_view(self, x, y, margin=80):
        """Check if position is visible on screen"""
        return -margin <= x <= SCREEN_WIDTH + margin and -margin <= y <= SCREEN_HEIGHT + margin
    
    def _render_entity(self, screen, entity):
        """Render entity with camera transform"""
        screen_pos = self.camera.world_to_screen(entity.x, entity.y)
        self._render_entity_at(screen, entity, screen_pos)
    
    @contextmanager
    def _temp_transform(self, entity, screen_pos):
        """Temporary transform for rendering"""
        orig_x, orig_y = entity.x, entity.y
        orig_radius = getattr(entity, 'radius', 10)
        
        try:
            entity.x, entity.y = screen_pos
            if hasattr(entity, 'radius'):
                entity.radius = orig_radius * self.camera.zoom
            yield
        finally:
            entity.x, entity.y = orig_x, orig_y
            if hasattr(entity, 'radius'):
                entity.radius = orig_radius
    
    def _render_entity_at(self, screen, entity, screen_pos):
        """Render entity at screen position"""
        with self._temp_transform(entity, screen_pos):
            if hasattr(entity, 'render'):
                # Check if entity expects camera parameter (enemies) vs just screen (player)
                if hasattr(entity, 'type'):  # This is an enemy
                    entity.render(screen, self.camera)
                else:  # This is the player
                    entity.render(screen)  # Player only takes screen parameter
    
    def _render_ui(self, screen):
        """Clean UI without annoying formation messages"""
        ui_texts = [
            f"HP: {self.player.hp}/{self.player.max_hp}",
            f"Level: {self.player.level}",
            f"Wave: {self.wave_manager.current_wave}",
            f"Exp: {self.player.experience}",
            f"Zoom: {self.camera.zoom:.1f}x"
        ]
        
        for i, text in enumerate(ui_texts):
            surface = self.font.render(text, True, WHITE)
            screen.blit(surface, (10, 10 + i * 25))
    
    def _render_pause_overlay(self, screen):
        """Pause screen overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        pause_text = self.font.render("PAUSED", True, WHITE)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(pause_text, text_rect)
    
    def pause(self): self.is_paused = True
    def unpause(self): self.is_paused = False
    
    def exit(self):
        """Cleanup"""
        self.sound_manager.stop_background_music()

class InputHandler:
    """Simple input handler"""
    
    def __init__(self):
        self.prev_keys = self.curr_keys = set()
    
    def update(self):
        """Update key states"""
        self.prev_keys = self.curr_keys
        pressed = pygame.key.get_pressed()
        self.curr_keys = {i for i, key in enumerate(pressed) if key}
    
    def is_key_just_pressed(self, key):
        """Check if key just pressed"""
        return key in self.curr_keys and key not in self.prev_keys
