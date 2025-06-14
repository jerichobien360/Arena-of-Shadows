from settings import *
from contextlib import contextmanager

# Game entities - Player and enemy objects
from entities.player import *
from entities.enemies import *

# Core game systems - Wave management, camera, and background rendering
from systems.wave_manager import *
from systems.camera import *
from systems.background_system import *


class GameState:
    """Base class for all game states with lifecycle management"""
    def enter(self): pass
    def exit(self): pass
    def update(self, dt): return None
    def render(self, screen): pass


class GameplayState(GameState):
    """Main gameplay state handling player interaction and game logic"""
    
    def __init__(self, font, sound_manager):
        self.font, self.sound_manager = font, sound_manager
        self.player = self.enemies = None
        self.wave_manager = self.camera = self.background = None
        self.input_handler = InputHandler()
        self.is_paused = self.game_time = False
    
    def enter(self):
        """Initialize gameplay components and start background music"""
        # Initialize core systems in one go
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.background = BackgroundSystem(WORLD_WIDTH, WORLD_HEIGHT)
        self.wave_manager = WaveManager(self.sound_manager)
        
        # Setup player and start first wave
        self.player = Player(self.sound_manager, self.camera)
        self.enemies = []
        self.wave_manager.start_wave(1)
        
        # Start gameplay music
        self.sound_manager.stop_background_music()
        if self.sound_manager.load_background_music("assets/background_music/gameplay.mp3"):
            self.sound_manager.play_background_music()
    
    def update(self, dt):
        """Main game loop - handles input, updates entities, and checks transitions"""
        if self.is_paused:
            return None
            
        self.game_time += dt
        
        # Handle input and check for state changes
        if next_state := self._handle_input():
            return next_state
            
        # Update all game components
        self._update_player(dt)
        self._update_enemies(dt)
        self._update_systems(dt)
        
        # Check for game over or other state transitions
        return "game_over" if self.player.hp <= 0 else None
    
    def _handle_input(self):
        """Process player input for movement, actions, and camera controls"""
        keys = pygame.key.get_pressed()
        
        # Check for pause toggle
        if self.input_handler.is_key_just_pressed(pygame.K_ESCAPE):
            return "pause"
        
        # Handle player attack
        if keys[pygame.K_SPACE]:
            self.player.attack(self.enemies)
        
        # Handle camera zoom with clamping
        zoom_delta = 0.1 * ((keys[pygame.K_EQUALS] or keys[pygame.K_PLUS]) - keys[pygame.K_MINUS])
        if zoom_delta:
            new_zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.camera.target_zoom + zoom_delta))
            self.camera.set_zoom(new_zoom)
        
        return None
    
    def _update_player(self, dt):
        """Update player and constrain to world boundaries"""
        self.player.update(dt)
        
        # Keep player within world bounds using tuple unpacking
        bounds = self.background.get_world_bounds()
        self.player.x = max(bounds[0] + self.player.radius, 
                           min(bounds[2] - self.player.radius, self.player.x))
        self.player.y = max(bounds[1] + self.player.radius, 
                           min(bounds[3] - self.player.radius, self.player.y))
    
    def _update_enemies(self, dt):
        """Update enemies and remove defeated ones"""
        # Use list comprehension for efficient enemy filtering
        alive_enemies = []
        for enemy in self.enemies:
            enemy.update(dt, self.player)
            if enemy.hp > 0:
                alive_enemies.append(enemy)
            # Handle enemy death effects here if needed
        self.enemies = alive_enemies
    
    def _update_systems(self, dt):
        """Update background, camera, and wave management systems"""
        self.background.update(dt)
        self.camera.update(dt, self.player.x, self.player.y)
        
        # Progress to next wave if current wave is complete
        if self.wave_manager.update(dt, self.enemies):
            self.wave_manager.start_wave(self.wave_manager.current_wave + 1)
    
    def render(self, screen):
        """Render all game elements in layers with optional pause overlay"""
        screen.fill(BLACK)
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Render game world
        self.background.render(screen, self.camera, current_time)
        self._render_entity(screen, self.player)
        
        # Render visible enemies only (frustum culling for performance)
        for enemy in self.enemies:
            screen_pos = self.camera.world_to_screen(enemy.x, enemy.y)
            if self._is_visible(*screen_pos):
                self._render_entity_at(screen, enemy, screen_pos)
        
        # Render UI and pause overlay
        self._render_ui(screen)
        if self.is_paused:
            self._render_pause_overlay(screen)
    
    def _is_visible(self, x, y, margin=100):
        """Check if position is visible on screen with margin"""
        return -margin <= x <= SCREEN_WIDTH + margin and -margin <= y <= SCREEN_HEIGHT + margin
    
    def _render_entity(self, screen, entity):
        """Render entity using camera transformation"""
        screen_pos = self.camera.world_to_screen(entity.x, entity.y)
        self._render_entity_at(screen, entity, screen_pos)
    
    @contextmanager
    def _temp_transform(self, entity, screen_pos):
        """Context manager for temporarily transforming entity for rendering"""
        orig_x, orig_y = entity.x, entity.y
        orig_radius = getattr(entity, 'radius', 10)
        
        try:
            # Apply screen transformation
            entity.x, entity.y = screen_pos
            if hasattr(entity, 'radius'):
                entity.radius = orig_radius * self.camera.zoom
            yield
        finally:
            # Restore original values
            entity.x, entity.y = orig_x, orig_y
            if hasattr(entity, 'radius'):
                entity.radius = orig_radius
    
    def _render_entity_at(self, screen, entity, screen_pos):
        """Render entity at specific screen position with proper scaling"""
        with self._temp_transform(entity, screen_pos):
            entity.render(screen)
    
    def _render_ui(self, screen):
        """Render game UI with player stats and game info"""
        ui_data = [
            f"HP: {self.player.hp}/{self.player.max_hp}",
            f"Level: {self.player.level}",
            f"Wave: {self.wave_manager.current_wave}",
            f"Exp: {self.player.experience}",
            f"Zoom: {self.camera.zoom:.1f}x",
            f"Time: {self.game_time:.1f}s"
        ]
        
        # Render all UI elements in one loop
        for i, text in enumerate(ui_data):
            surface = self.font.render(text, True, WHITE)
            screen.blit(surface, (10, 10 + i * 30))
    
    def _render_pause_overlay(self, screen):
        """Render semi-transparent pause overlay with centered text"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Center pause text on screen
        pause_text = self.font.render("PAUSED", True, WHITE)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(pause_text, text_rect)
    
    def pause(self): self.is_paused = True
    def unpause(self): self.is_paused = False
    
    def exit(self):
        """Clean up resources when leaving gameplay state"""
        self.sound_manager.stop_background_music()


class InputHandler:
    """Lightweight input handler for detecting key press/release events"""
    
    def __init__(self):
        self.prev_keys = self.curr_keys = set()
    
    def update(self):
        """Update input state - call once per frame before checking keys"""
        self.prev_keys = self.curr_keys
        pressed = pygame.key.get_pressed()
        self.curr_keys = {i for i, pressed in enumerate(pressed) if pressed}
    
    def is_key_just_pressed(self, key):
        """Check if key was pressed this frame (not held from previous frame)"""
        return key in self.curr_keys and key not in self.prev_keys
    
    def is_key_just_released(self, key):
        """Check if key was released this frame"""
        return key not in self.curr_keys and key in self.prev_keys
