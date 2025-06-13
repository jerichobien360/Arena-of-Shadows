from settings import *

# entities
from entities.player import *
from entities.enemies import *

# systems
from systems.wave_manager import *
from systems.camera import *
from systems.background_system import *

class GameState:
    """Base class for all game states"""
    def enter(self): 
        """Called when entering this state"""
        pass
    
    def exit(self): 
        """Called when exiting this state"""
        pass
    
    def update(self, dt): 
        """Update game logic. Return state name to switch to, or None to stay"""
        return None
    
    def render(self, screen): 
        """Render this state to the screen"""
        pass

class GameplayState(GameState):
    def __init__(self, font, sound_manager):
        self.font = font
        self.sound_manager = sound_manager
        
        # Core game objects
        self.player = None
        self.enemies = []
        
        # Game systems
        self.wave_manager = None
        self.camera = None
        self.background = None
        
        # Input handling
        self.input_handler = InputHandler()
        
        # Game state
        self.is_paused = False
        self.game_time = 0.0
    
    def enter(self):
        """Initialize the gameplay state"""
        self._initialize_systems()
        self._initialize_entities()
        self._start_game_music()
    
    def _initialize_systems(self):
        """Initialize all game systems"""
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.background = BackgroundSystem(WORLD_WIDTH, WORLD_HEIGHT)
        self.wave_manager = WaveManager(self.sound_manager)
    
    def _initialize_entities(self):
        """Initialize game entities"""
        self.player = Player(self.sound_manager, self.camera)
        self.enemies = []
        self.wave_manager.start_wave(1)
    
    def _start_game_music(self):
        """Start the gameplay background music"""
        self.sound_manager.stop_background_music()
        if self.sound_manager.load_background_music("assets/background_music/gameplay.mp3"):
            self.sound_manager.play_background_music()
    
    def update(self, dt):
        """Main game update loop"""
        if self.is_paused:
            return None
            
        self.game_time += dt
        
        # Handle input
        next_state = self._handle_input()
        if next_state:
            return next_state
            
        # Update game systems
        self._update_player(dt)
        self._update_enemies(dt)
        self._update_world_systems(dt)
        
        # Check game state transitions
        return self._check_state_transitions()
    
    def _handle_input(self):
        """Handle all input for the gameplay state"""
        keys = pygame.key.get_pressed()
        
        # Pause toggle
        if self.input_handler.is_key_just_pressed(pygame.K_ESCAPE):
            return "pause"
        
        # Player actions
        if keys[pygame.K_SPACE]:
            self.player.attack(self.enemies)
        
        # Camera controls
        self._handle_camera_input(keys)
        
        return None
    
    def _handle_camera_input(self, keys):
        """Handle camera-specific input"""
        zoom_speed = 0.1
        
        if keys[pygame.K_EQUALS] or keys[pygame.K_PLUS]:
            new_zoom = self.camera.target_zoom + zoom_speed
            self.camera.set_zoom(min(new_zoom, MAX_ZOOM))  # Assuming MAX_ZOOM is defined
        elif keys[pygame.K_MINUS]:
            new_zoom = self.camera.target_zoom - zoom_speed
            self.camera.set_zoom(max(new_zoom, MIN_ZOOM))  # Assuming MIN_ZOOM is defined
    
    def _update_player(self, dt):
        """Update player logic"""
        self.player.update(dt)
        self._constrain_player_to_world()
    
    def _constrain_player_to_world(self):
        """Keep player within world bounds"""
        world_bounds = self.background.get_world_bounds()
        self.player.x = max(world_bounds[0] + self.player.radius, 
                           min(world_bounds[2] - self.player.radius, self.player.x))
        self.player.y = max(world_bounds[1] + self.player.radius, 
                           min(world_bounds[3] - self.player.radius, self.player.y))
    
    def _update_enemies(self, dt):
        """Update all enemies and remove dead ones"""
        for enemy in self.enemies[:]:  # Use slice copy to avoid modification during iteration
            enemy.update(dt, self.player)
            if enemy.hp <= 0:
                self._on_enemy_death(enemy)
                self.enemies.remove(enemy)
    
    def _on_enemy_death(self, enemy):
        """Handle enemy death (experience, drops, etc.)"""
        # This is where you'd handle experience gain, item drops, etc.
        # For now, just a placeholder
        pass
    
    def _update_world_systems(self, dt):
        """Update world systems like background and camera"""
        self.background.update(dt)
        self.camera.update(dt, self.player.x, self.player.y)
        
        # Update wave system
        if self.wave_manager.update(dt, self.enemies):
            self.wave_manager.start_wave(self.wave_manager.current_wave + 1)
    
    def _check_state_transitions(self):
        """Check if we need to transition to another state"""
        if self.player.hp <= 0:
            return "game_over"
        
        # Could add other transitions here (level complete, boss defeated, etc.)
        return None
    
    def render(self, screen):
        """Render the entire gameplay state"""
        screen.fill(BLACK)
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Render in layers
        self._render_background(screen, current_time)
        self._render_entities(screen)
        self._render_ui(screen)
        
        # Render pause overlay if paused
        if self.is_paused:
            self._render_pause_overlay(screen)
    
    def _render_background(self, screen, current_time):
        """Render the background system"""
        self.background.render(screen, self.camera, current_time)
    
    def _render_entities(self, screen):
        """Render all game entities"""
        # Render player
        self._render_entity_with_camera(screen, self.player)
        
        # Render enemies (with frustum culling)
        self._render_enemies(screen)
    
    def _render_enemies(self, screen):
        """Render enemies with performance optimization"""
        for enemy in self.enemies:
            screen_x, screen_y = self.camera.world_to_screen(enemy.x, enemy.y)
            
            # Frustum culling - only render if on screen
            if self._is_on_screen(screen_x, screen_y):
                self._render_entity_at_position(screen, enemy, screen_x, screen_y)
    
    def _is_on_screen(self, x, y, margin=100):
        """Check if a position is visible on screen (with margin)"""
        return (-margin <= x <= SCREEN_WIDTH + margin and 
                -margin <= y <= SCREEN_HEIGHT + margin)
    
    def _render_entity_with_camera(self, screen, entity):
        """Render entity using camera transformation"""
        screen_x, screen_y = self.camera.world_to_screen(entity.x, entity.y)
        self._render_entity_at_position(screen, entity, screen_x, screen_y)
    
    def _render_entity_at_position(self, screen, entity, screen_x, screen_y):
        """Render entity at specific screen position with proper scaling"""
        # Store original values
        original_x, original_y = entity.x, entity.y
        original_radius = getattr(entity, 'radius', 10)
        
        try:
            # Set screen position and scaled size
            entity.x = screen_x
            entity.y = screen_y
            if hasattr(entity, 'radius'):
                entity.radius = original_radius * self.camera.zoom
            
            # Render the entity
            entity.render(screen)
        finally:
            # Always restore original values
            entity.x = original_x
            entity.y = original_y
            if hasattr(entity, 'radius'):
                entity.radius = original_radius
    
    def _render_ui(self, screen):
        """Render the user interface"""
        ui_elements = self._get_ui_elements()
        
        for i, text in enumerate(ui_elements):
            rendered = self.font.render(text, True, WHITE)
            screen.blit(rendered, (10, 10 + i * 30))
    
    def _get_ui_elements(self):
        """Get list of UI text elements to display"""
        return [
            f"HP: {self.player.hp}/{self.player.max_hp}",
            f"Level: {self.player.level}",
            f"Wave: {self.wave_manager.current_wave}",
            f"Exp: {self.player.experience}",
            f"Zoom: {self.camera.zoom:.1f}x",
            f"Time: {self.game_time:.1f}s"
        ]
    
    def _render_pause_overlay(self, screen):
        """Render pause overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        pause_text = self.font.render("PAUSED", True, WHITE)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(pause_text, text_rect)
    
    def pause(self):
        """Pause the game"""
        self.is_paused = True
    
    def unpause(self):
        """Unpause the game"""
        self.is_paused = False
    
    def exit(self):
        """Clean up when exiting gameplay state"""
        self.sound_manager.stop_background_music()


class InputHandler:
    """Helper class for handling input with key press detection"""
    def __init__(self):
        self.previous_keys = set()
        self.current_keys = set()
    
    def update(self):
        """Update input state - call this once per frame"""
        self.previous_keys = self.current_keys.copy()
        pressed_keys = pygame.key.get_pressed()
        self.current_keys = {key for key, pressed in enumerate(pressed_keys) if pressed}
    
    def is_key_just_pressed(self, key):
        """Check if key was just pressed this frame"""
        return key in self.current_keys and key not in self.previous_keys
    
    def is_key_just_released(self, key):
        """Check if key was just released this frame"""
        return key not in self.current_keys and key in self.previous_keys
