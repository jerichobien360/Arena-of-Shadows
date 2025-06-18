# gameplay_renderer.py - Pure Rendering Logic
import pygame
from settings import *
from contextlib import contextmanager

class GameplayRenderer:
    """Handles all rendering for gameplay state"""
    
    def __init__(self, font):
        self.font = font
    
    def render(self, screen, game_data):
        """Main render method"""
        screen.fill(BLACK)
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Extract data
        player = game_data['player']
        enemies = game_data['enemies']
        camera = game_data['camera']
        background = game_data['background']
        wave_manager = game_data['wave_manager']
        is_paused = game_data['is_paused']
        
        # Render world
        background.render(screen, camera, current_time)
        self._render_entity(screen, player, camera)
        
        # Render enemies with culling
        for enemy in enemies:
            screen_pos = camera.world_to_screen(enemy.x, enemy.y)
            if self._is_in_view(*screen_pos):
                self._render_entity_at(screen, enemy, screen_pos, camera)
        
        # Render UI
        self._render_ui(screen, player, wave_manager, camera)
        
        # Render pause overlay if needed
        if is_paused:
            self._render_pause_overlay(screen)
    
    def _is_in_view(self, x, y, margin=80):
        """Check if position is visible on screen"""
        return -margin <= x <= SCREEN_WIDTH + margin and -margin <= y <= SCREEN_HEIGHT + margin
    
    def _render_entity(self, screen, entity, camera):
        """Render entity with camera transform"""
        screen_pos = camera.world_to_screen(entity.x, entity.y)
        self._render_entity_at(screen, entity, screen_pos, camera)
    
    @contextmanager
    def _temp_transform(self, entity, screen_pos, camera):
        """Temporary transform for rendering"""
        orig_x, orig_y = entity.x, entity.y
        orig_radius = getattr(entity, 'radius', 10)
        
        try:
            entity.x, entity.y = screen_pos
            if hasattr(entity, 'radius'):
                entity.radius = orig_radius * camera.zoom
            yield
        finally:
            entity.x, entity.y = orig_x, orig_y
            if hasattr(entity, 'radius'):
                entity.radius = orig_radius
    
    def _render_entity_at(self, screen, entity, screen_pos, camera):
        """Render entity at screen position"""
        with self._temp_transform(entity, screen_pos, camera):
            if hasattr(entity, 'render'):
                # Check if entity expects camera parameter (enemies) vs just screen (player)
                if hasattr(entity, 'type'):  # This is an enemy
                    entity.render(screen, camera)
                else:  # This is the player
                    entity.render(screen)  # Player only takes screen parameter
    
    def _render_ui(self, screen, player, wave_manager, camera):
        """Render clean UI"""
        ui_data = [
            f"HP: {player.hp}/{player.max_hp}",
            f"Level: {player.level}",
            f"Wave: {wave_manager.current_wave}",
            f"Exp: {player.experience}",
            f"Zoom: {camera.zoom:.1f}x"
        ]
        
        for i, text in enumerate(ui_data):
            surface = self.font.render(text, True, WHITE)
            screen.blit(surface, (10, 10 + i * 25))
    
    def _render_pause_overlay(self, screen):
        """Render pause screen overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        pause_text = self.font.render("PAUSED", True, WHITE)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(pause_text, text_rect)
