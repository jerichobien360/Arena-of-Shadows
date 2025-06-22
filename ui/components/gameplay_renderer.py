"""Handling the Gameplay with Rendering."""

import pygame
from settings import *
from contextlib import contextmanager
from typing import Dict, Tuple, Any


class GameplayRenderer:
    """Handles all rendering for gameplay state."""
    
    def __init__(self, font: pygame.font.Font):
        self.font = font
        self._ui_margin = 10
        self._ui_line_height = 25
        self._view_margin = 80
    
    def render(self, screen: pygame.Surface, game_data: Dict[str, Any]) -> None:
        """Main render method."""
        screen.fill(BLACK)
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Extract game components
        player = game_data['player']
        enemies = game_data['enemies']
        camera = game_data['camera']
        background = game_data['background']
        wave_manager = game_data['wave_manager']
        is_paused = game_data['is_paused']
        
        # Render world
        self._render_world(screen, background, camera, current_time)
        self._render_player(screen, player, camera)
        self._render_enemies(screen, enemies, camera)
        
        # Render UI
        self._render_ui(screen, player, wave_manager, camera)
        
        if is_paused:
            self._render_pause_overlay(screen)
    
    def _render_world(self, screen: pygame.Surface, background, camera, current_time: float) -> None:
        """Render the game world background."""
        background.render(screen, camera, current_time)
    
    def _render_player(self, screen: pygame.Surface, player, camera) -> None:
        """Render the player entity."""
        self._render_entity(screen, player, camera)
    
    def _render_enemies(self, screen: pygame.Surface, enemies, camera) -> None:
        """Render all visible enemies with culling."""
        for enemy in enemies:
            screen_pos = camera.world_to_screen(enemy.x, enemy.y)
            if self._is_in_view(screen_pos):
                self._render_entity_at(screen, enemy, screen_pos, camera)
    
    def _is_in_view(self, pos: Tuple[float, float], margin: int = None) -> bool:
        """Check if position is visible on screen."""
        if margin is None:
            margin = self._view_margin
        
        x, y = pos
        return (-margin <= x <= SCREEN_WIDTH + margin and 
                -margin <= y <= SCREEN_HEIGHT + margin)
    
    def _render_entity(self, screen: pygame.Surface, entity, camera) -> None:
        """Render entity with camera transform."""
        screen_pos = camera.world_to_screen(entity.x, entity.y)
        self._render_entity_at(screen, entity, screen_pos, camera)
    
    @contextmanager
    def _temp_transform(self, entity, screen_pos: Tuple[float, float], camera):
        """Temporarily transform entity for rendering."""
        # Store original values
        original_pos = (entity.x, entity.y)
        original_radius = getattr(entity, 'radius', 10)
        
        try:
            # Apply temporary transformation
            entity.x, entity.y = screen_pos
            if hasattr(entity, 'radius'):
                entity.radius = original_radius * camera.zoom
            yield
        finally:
            # Restore original values
            entity.x, entity.y = original_pos
            if hasattr(entity, 'radius'):
                entity.radius = original_radius
    
    def _render_entity_at(self, screen: pygame.Surface, entity, screen_pos: Tuple[float, float], camera) -> None:
        """Render entity at specific screen position."""
        if not hasattr(entity, 'render'):
            return
        
        with self._temp_transform(entity, screen_pos, camera):
            # Determine render parameters based on entity type
            if self._is_enemy(entity):
                entity.render(screen, camera)
            else:
                entity.render(screen)
    
    def _is_enemy(self, entity) -> bool:
        """Check if entity is an enemy (has type attribute)."""
        return hasattr(entity, 'type')
    
    def _render_ui(self, screen: pygame.Surface, player, wave_manager, camera) -> None:
        """Render game UI elements."""
        ui_elements = [
            f"HP: {player.hp}/{player.max_hp}",
            f"Level: {player.level}",
            f"Wave: {wave_manager.current_wave}",
            f"Exp: {player.experience}",
            f"Zoom: {camera.zoom:.1f}x"
        ]
        
        for i, text in enumerate(ui_elements):
            self._render_ui_text(screen, text, i)
    
    def _render_ui_text(self, screen: pygame.Surface, text: str, line_index: int) -> None:
        """Render a single UI text element."""
        surface = self.font.render(text, True, WHITE)
        y_pos = self._ui_margin + line_index * self._ui_line_height
        screen.blit(surface, (self._ui_margin, y_pos))
    
    def _render_pause_overlay(self, screen: pygame.Surface) -> None:
        """Render pause screen overlay."""
        # Create semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Render pause text
        pause_text = self.font.render("PAUSED", True, WHITE)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(pause_text, text_rect)
