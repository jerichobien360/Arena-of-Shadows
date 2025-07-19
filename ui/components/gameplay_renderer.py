"""Handling the Gameplay with Rendering."""

import pygame
import math
from dataclasses import dataclass
from typing import Dict, Tuple, Any, Optional
from contextlib import contextmanager
from settings import *
from ui.effects.animations import AnimationConfig, AnimatedProgressBar


class ScreenEffects:
    """Handles screen overlay effects."""
    
    def __init__(self, config: UIConfig):
        self.config = config
        self.level_up_timer = 0
        self.last_player_level = 1
    
    # -------------------CLASS METHOD-------------------------------------
    def check_level_up(self, player, current_time_ms: int) -> None:
        """Check for level-up and trigger effect."""
        if player.level > self.last_player_level:
            self.level_up_timer = current_time_ms
            self.last_player_level = player.level
    
    def render(self, screen: pygame.Surface, player, current_time_ms: int) -> None:
        """Render screen effects."""
        if self._is_level_up_active(current_time_ms):
            self._render_level_up_effect(screen, current_time_ms)
        elif self._should_show_low_health(player):
            self._render_low_health_effect(screen, current_time_ms)
    
    # -------------------CLASS PROPERTIES---------------------------------
    def _is_level_up_active(self, current_time_ms: int) -> bool:
        """Check if level-up effect is active."""
        return (self.level_up_timer > 0 and 
                current_time_ms - self.level_up_timer < self.config.level_up_duration)
    
    def _should_show_low_health(self, player) -> bool:
        """Check if low health effect should show."""
        return player.hp / player.max_hp <= self.config.low_health_threshold
    
    def _render_low_health_effect(self, screen: pygame.Surface, current_time_ms: int) -> None:
        """Render red heartbeat effect for low health."""
        heartbeat = (math.sin(current_time_ms * 0.002) + 1) / 2
        intensity = 0.3 + 0.4 * heartbeat
        alpha = int(self.config.effect_alpha * intensity)
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 0, 0, alpha))
        screen.blit(overlay, (0, 0))
    
    def _render_level_up_effect(self, screen: pygame.Surface, current_time_ms: int) -> None:
        """Render cyan pulsing effect for level-up."""
        elapsed = current_time_ms - self.level_up_timer
        fade_progress = min(elapsed / self.config.level_up_duration, 1.0)
        pulse = (math.sin(current_time_ms * 0.003) + 1) / 2
        
        intensity = (1.0 - fade_progress) * (0.3 + 0.7 * pulse)
        alpha = int(self.config.effect_alpha * intensity)
        
        if alpha > 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 255, 255, alpha))
            screen.blit(overlay, (0, 0))
        else:
            self.level_up_timer = 0


class UIRenderer:
    """Handles UI rendering."""
    
    def __init__(self, font: pygame.font.Font, config: UIConfig):
        self.font = font
        self.config = config
    
    # -------------------CLASS METHOD-------------------------------------
    def render_panel(self, screen: pygame.Surface, x: int, y: int, width: int, height: int) -> None:
        """Render semi-transparent UI panel."""
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        rect = pygame.Rect(0, 0, width, height)
        
        pygame.draw.rect(panel, (0, 0, 0, self.config.panel_alpha), rect, 
                        border_radius=self.config.panel_corner_radius)
        pygame.draw.rect(panel, (80, 80, 80, 200), rect, width=2, 
                        border_radius=self.config.panel_corner_radius)
        
        screen.blit(panel, (x, y))
    
    def render_text_elements(self, screen: pygame.Surface, elements: list, start_y: int) -> None:
        """Render list of text elements."""
        for i, text in enumerate(elements):
            surface = self.font.render(text, True, (240, 240, 240))
            x = self.config.margin + self.config.panel_padding
            y = start_y + i * self.config.line_height
            screen.blit(surface, (x, y))
    
    def render_progress_bar(self, screen: pygame.Surface, x: int, y: int, 
                          animated_bar: AnimatedProgressBar, label: str,
                          colors: Tuple[Tuple[int, int, int], Tuple[int, int, int]],
                          current_time_ms: int) -> None:
        """Render animated progress bar."""
        fill_color, glow_color = colors
        progress = animated_bar.get_progress()
        fill_width = int(self.config.bar_width * progress)
        
        # Create bar surface
        bar_surface = pygame.Surface((self.config.bar_width, self.config.bar_height), pygame.SRCALPHA)
        bg_rect = pygame.Rect(0, 0, self.config.bar_width, self.config.bar_height)
        
        # Background
        pygame.draw.rect(bar_surface, (40, 40, 40, 200), bg_rect, 
                        border_radius=self.config.bar_corner_radius)
        
        # Fill
        if fill_width > 0:
            fill_rect = pygame.Rect(0, 0, fill_width, self.config.bar_height)
            main_color = self._get_animated_color(fill_color, glow_color, animated_bar.is_animating())
            
            pygame.draw.rect(bar_surface, main_color, fill_rect, 
                           border_radius=self.config.bar_corner_radius)
            
            # Highlight
            if fill_width > 4:
                highlight_rect = pygame.Rect(2, 2, fill_width - 4, self.config.bar_height // 3)
                highlight_color = tuple(min(255, c + 40) for c in main_color)
                pygame.draw.rect(bar_surface, highlight_color, highlight_rect, 
                               border_radius=self.config.bar_corner_radius // 2)
        
        # Change effect
        self._add_change_effect(bar_surface, animated_bar, bg_rect, current_time_ms)
        
        # Border
        pygame.draw.rect(bar_surface, (200, 200, 200, 255), bg_rect, 
                        width=self.config.bar_border, 
                        border_radius=self.config.bar_corner_radius)
        
        # Glow effect
        if animated_bar.is_animating():
            self._add_glow_effect(screen, x, y, glow_color)
        
        screen.blit(bar_surface, (x, y))
        
        # Labels and values
        self._render_bar_labels(screen, x, y, label, animated_bar, progress)
    
    # -------------------CLASS PROPERTIES---------------------------------
    def _get_animated_color(self, base_color: Tuple[int, int, int], 
                          glow_color: Tuple[int, int, int], is_animating: bool) -> Tuple[int, int, int]:
        """Get color with animation glow if needed."""
        if not is_animating:
            return base_color
        
        glow_intensity = 0.3
        return tuple(min(255, int(c + (glow_color[i] - c) * glow_intensity)) 
                    for i, c in enumerate(base_color))
    
    def _add_change_effect(self, surface: pygame.Surface, animated_bar: AnimatedProgressBar,
                          rect: pygame.Rect, current_time_ms: int) -> None:
        """Add damage/heal effect overlay."""
        alpha = animated_bar.get_change_effect_alpha(current_time_ms)
        if alpha <= 0:
            return
        
        color = (255, 100, 100) if animated_bar.was_damage() else (100, 255, 100)
        effect_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        effect_surface.fill((*color, int(100 * alpha)))
        surface.blit(effect_surface, (0, 0))
    
    def _add_glow_effect(self, screen: pygame.Surface, x: int, y: int, 
                        glow_color: Tuple[int, int, int]) -> None:
        """Add glow effect around animated bars."""
        glow_surface = pygame.Surface((self.config.bar_width + 4, self.config.bar_height + 4), 
                                     pygame.SRCALPHA)
        glow_rect = pygame.Rect(2, 2, self.config.bar_width, self.config.bar_height)
        pygame.draw.rect(glow_surface, (*glow_color, 30), glow_rect, 
                        border_radius=self.config.bar_corner_radius)
        screen.blit(glow_surface, (x - 2, y - 2))
    
    def _render_bar_labels(self, screen: pygame.Surface, x: int, y: int, label: str,
                          animated_bar: AnimatedProgressBar, progress: float) -> None:
        """Render bar label, values, and percentage."""
        # Label
        label_surface = self.font.render(f"{label}:", True, (255, 255, 255))
        label_x = max(x - label_surface.get_width() - 8, 
                     self.config.margin + self.config.panel_padding)
        label_y = y + (self.config.bar_height - label_surface.get_height()) // 2
        screen.blit(label_surface, (label_x, label_y))
        
        # Values
        current = int(animated_bar.display_value)
        maximum = int(animated_bar.display_max)
        value_text = f"{current//1000}k/{maximum//1000}k" if maximum >= 1000 else f"{current}/{maximum}"
        
        value_surface = self.font.render(value_text, True, (220, 220, 220))
        value_x = min(x + self.config.bar_width + 8,
                     self.config.margin + self.config.panel_width - 
                     self.config.panel_padding - value_surface.get_width())
        value_y = y + (self.config.bar_height - value_surface.get_height()) // 2
        screen.blit(value_surface, (value_x, value_y))
        
        # Percentage
        percentage = int(progress * 100)
        if int(self.config.bar_width * progress) > 40 and percentage > 0:
            percent_surface = self.font.render(f"{percentage}%", True, (180, 180, 180))
            percent_x = x + (self.config.bar_width - percent_surface.get_width()) // 2
            percent_y = y + (self.config.bar_height - percent_surface.get_height()) // 2
            screen.blit(percent_surface, (percent_x, percent_y))


class GameplayRenderer:
    """Handles all rendering for gameplay state."""
    
    def __init__(self, font: pygame.font.Font):
        self.font = font
        self.config = UIConfig()
        
        self.ui_renderer = UIRenderer(font, self.config)
        self.screen_effects = ScreenEffects(self.config)
        
        self.hp_bar = AnimatedProgressBar()
        self.exp_bar = AnimatedProgressBar()
        self._initialized = False
    
    # -------------------CLASS METHOD-------------------------------------
    def render(self, screen: pygame.Surface, game_data: Dict[str, Any]) -> None:
        """Main render method."""
        screen.fill(BLACK)
        current_time_ms = pygame.time.get_ticks()
        
        player = game_data['player']
        
        # Initialize progress bars on first render
        if not self._initialized:
            self._initialize_progress_bars(player, current_time_ms)
        
        # Update animations and effects
        self._update_progress_bars(player, current_time_ms)
        self.screen_effects.check_level_up(player, current_time_ms)
        
        # Render world and entities
        self._render_world_and_entities(screen, game_data)
        
        # Render UI and effects
        self._render_ui(screen, game_data, current_time_ms)
        self.screen_effects.render(screen, player, current_time_ms)
        
        if game_data['is_paused']:
            self._render_pause_overlay(screen)
    
    # -------------------CLASS PROPERTIES---------------------------------
    # HUD 1 - HP & EXP =========================================
    def _initialize_progress_bars(self, player, current_time_ms: int) -> None:
        """Initialize progress bars with current values."""
        self.hp_bar.update(player.hp, player.max_hp, current_time_ms)
        self.exp_bar.update(player.experience, self._get_exp_for_next_level(player.level), current_time_ms)
        self._initialized = True
    
    def _update_progress_bars(self, player, current_time_ms: int) -> None:
        """Update animated progress bars."""
        self.hp_bar.update(player.hp, player.max_hp, current_time_ms)
        self.exp_bar.update(player.experience, self._get_exp_for_next_level(player.level), current_time_ms)
    
    def _render_ui(self, screen: pygame.Surface, game_data: Dict[str, Any], current_time_ms: int) -> None:
        """Render game UI elements."""
        player = game_data['player']
        wave_manager = game_data['wave_manager']
        camera = game_data['camera']
        
        # UI elements
        ui_elements = [
            f"Level: {player.level}",
            f"Wave: {wave_manager.current_wave}",
            f"Zoom: {camera.zoom:.1f}x"
        ]
        
        # Calculate panel dimensions
        text_height = len(ui_elements) * self.config.line_height
        bars_height = 2 * (self.config.bar_height + self.config.bar_spacing) - self.config.bar_spacing
        panel_height = text_height + 12 + bars_height + 2 * self.config.panel_padding
        
        # Render UI panel
        self.ui_renderer.render_panel(screen, self.config.margin, self.config.margin, 
                                     self.config.panel_width, panel_height)
        
        # Render text elements
        text_start_y = self.config.margin + self.config.panel_padding
        self.ui_renderer.render_text_elements(screen, ui_elements, text_start_y)
        
        # Render progress bars
        bars_start_y = text_start_y + text_height + 12
        bar_x = self.config.margin + self.config.panel_padding + 45
        
        # HP bar
        self.ui_renderer.render_progress_bar(
            screen, bar_x, bars_start_y, self.hp_bar, "HP",
            ((220, 50, 50), (255, 100, 100)), current_time_ms
        )
        
        # EXP bar
        exp_y = bars_start_y + self.config.bar_height + self.config.bar_spacing
        self.ui_renderer.render_progress_bar(
            screen, bar_x, exp_y, self.exp_bar, "EXP",
            ((50, 100, 220), (100, 150, 255)), current_time_ms
        )

    def _get_exp_for_next_level(self, level: int) -> int:
        """Get experience needed for next level."""
        return level * 100

    # CAMERA SYSTEM ============================================
    def _render_world_and_entities(self, screen: pygame.Surface, game_data: Dict[str, Any]) -> None:
        """Render world background and all entities."""
        camera = game_data['camera']
        current_time = pygame.time.get_ticks() / 1000.0
        
        # World
        game_data['background'].render(screen, camera, current_time)
        
        # Player
        self._render_entity(screen, game_data['player'], camera)
        
        # Enemies with culling
        for enemy in game_data['enemies']:
            screen_pos = camera.world_to_screen(enemy.x, enemy.y)
            if self._is_in_view(screen_pos):
                self._render_entity_at(screen, enemy, screen_pos, camera)
    
    def _is_in_view(self, pos: Tuple[float, float]) -> bool:
        """Check if position is visible on screen."""
        x, y = pos
        margin = self.config.view_margin
        return (-margin <= x <= SCREEN_WIDTH + margin and 
                -margin <= y <= SCREEN_HEIGHT + margin)
    
    def _render_entity(self, screen: pygame.Surface, entity, camera) -> None:
        """Render entity with camera transform."""
        screen_pos = camera.world_to_screen(entity.x, entity.y)
        self._render_entity_at(screen, entity, screen_pos, camera)
    
    @contextmanager
    def _temp_transform(self, entity, screen_pos: Tuple[float, float], camera):
        """Temporarily transform entity for rendering."""
        original_pos = (entity.x, entity.y)
        original_radius = getattr(entity, 'radius', 10)
        
        try:
            entity.x, entity.y = screen_pos
            if hasattr(entity, 'radius'):
                entity.radius = original_radius * camera.zoom
            yield
        finally:
            entity.x, entity.y = original_pos
            if hasattr(entity, 'radius'):
                entity.radius = original_radius
    
    def _render_entity_at(self, screen: pygame.Surface, entity, screen_pos: Tuple[float, float], camera) -> None:
        """Render entity at specific screen position."""
        if not hasattr(entity, 'render'):
            return
        
        with self._temp_transform(entity, screen_pos, camera):
            if hasattr(entity, 'type'):  # Enemy
                entity.render(screen, camera)
            else:
                entity.render(screen)
    
    # GAME PAUSE ===============================================
    def _render_pause_overlay(self, screen: pygame.Surface) -> None:
        """Render pause screen overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        
        # Pause panel
        panel_size = (300, 100)
        panel_pos = ((SCREEN_WIDTH - panel_size[0]) // 2, (SCREEN_HEIGHT - panel_size[1]) // 2)
        
        panel = pygame.Surface(panel_size, pygame.SRCALPHA)
        rect = pygame.Rect(0, 0, *panel_size)
        pygame.draw.rect(panel, (20, 20, 20, 240), rect, border_radius=15)
        pygame.draw.rect(panel, (100, 100, 100, 255), rect, width=3, border_radius=15)
        screen.blit(panel, panel_pos)
        
        # Text
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        pause_text = self.font.render("PAUSED", True, (255, 255, 255))
        pause_rect = pause_text.get_rect(center=(center_x, center_y - 10))
        screen.blit(pause_text, pause_rect)
        
        instruction_font = pygame.font.Font(None, 24)
        instruction_text = instruction_font.render("Press SPACE to continue", True, (180, 180, 180))
        instruction_rect = instruction_text.get_rect(center=(center_x, center_y + 20))
        screen.blit(instruction_text, instruction_rect)
