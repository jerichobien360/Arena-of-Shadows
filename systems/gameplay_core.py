"""Core gameplay logic with clean architecture and optimized combat systems."""

import math
import pygame
from typing import List, Tuple, Optional, Dict, Any

from settings import *
from entities.player import *
from entities.enemies import *
from systems.manager.wave_manager import *
from systems.game_feature.camera import *
from systems.game_feature.background_system import *
from systems.game_feature.battle_formation_system import FormationSystem
from systems.manager.input_manager import InputHandler
from systems.manager.ui_manager import UniversalPanel, PanelTemplates
from game_function.ui import *


class GameplayCore:
    """Core gameplay logic with clean separation of concerns."""

    def __init__(self, sound_manager):
        '''
        These are the packages will be used for a gameplay.
            1. Update on the game_data() method for rendering.
            2. Use on the CLASS PROPERTIES for modifying the flow of gameplay.
        '''
        self.sound_manager = sound_manager

        # Game entities
        self.player: Optional[Player] = None
        self.enemies: List = []

        # Game systems
        self.wave_manager: Optional[WaveManager] = None
        self.camera: Optional[Camera] = None
        self.background: Optional[BackgroundSystem] = None
        self.formation_system = FormationSystem()
        self.input_handler = InputHandler()

        # Game state
        self.is_paused = False
        self.game_time = 0.0

        # Pause panel system
        self.panel_template = PanelTemplates(self.sound_manager)
        self.pause_panel: Optional[UniversalPanel] = None
        self.show_pause_panel = False

    # -------------------INITIALIZE & CLEANUP-----------------------------
    def initialize(self) -> None:
        """Initialize all gameplay systems and entities."""
        self.game_time = 0.0
        self.is_paused = False
        self.show_pause_panel = False

        # Initialize systems
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.background = BackgroundSystem(WORLD_WIDTH, WORLD_HEIGHT)
        self.wave_manager = WaveManager(self.sound_manager)
        self.formation_system = FormationSystem()

        # Initialize entities
        self.player = Player(self.sound_manager, self.camera)
        self.enemies = []

        # Initialize pause panel
        self._setup_pause_panel()

        # Start first wave and setup audio
        self.wave_manager.start_wave(WAVE_STARTING_POINT)
        self._setup_audio()

    def cleanup(self) -> None:
        """Clean up resources when exiting gameplay."""
        self.sound_manager.stop_background_music()

    # -------------------PAUSE PANEL SETUP--------------------------------
    def _setup_pause_panel(self) -> None:
        """Setup the pause panel with callbacks."""
        self.pause_panel = self.panel_template.pause_menu_panel()

        # Override the default callbacks with actual functionality
        for element in self.pause_panel.elements:
            if element.text == "Resume Game":
                element.callback = self._resume_game
            elif element.text == "Save Game":
                element.callback = self._save_game
            elif element.text == "Load Game":
                element.callback = self._load_game
            elif element.text == "Settings":
                element.callback = self._open_settings
            elif element.text == "Controls":
                element.callback = self._open_controls
            elif element.text == "Main Menu":
                element.callback = self._return_to_menu
            elif element.text == "Quit Game":
                element.callback = self._quit_game
            elif element.id == "mute_audio":
                element.callback = self._toggle_mute
            elif element.id == "master_vol":
                element.callback = self._update_volume

    def _resume_game(self) -> None:
        """Resume the game from pause."""
        self.unpause()

    def _save_game(self) -> None:
        """Save current game state."""
        print("[Pause Menu] Game saved successfully!")
        # TODO: Implement actual save functionality

    def _load_game(self) -> None:
        """Load a saved game state."""
        print("[Pause Menu] Game loaded!")
        # TODO: Implement actual load functionality

    def _open_settings(self) -> None:
        """Open settings menu."""
        print("[Pause Menu] Opening settings...")
        # TODO: Could create a settings panel here

    def _open_controls(self) -> None:
        """Open controls menu."""
        print("[Pause Menu] Opening controls...")
        # TODO: Could show control scheme

    def _return_to_menu(self) -> None:
        """Return to main menu."""
        print("[Pause Menu] Returning to main menu...")
        # This should trigger a state change
        self.unpause()
        self._next_state = "main_menu"

    def _quit_game(self) -> None:
        """Quit the game."""
        print("[Pause Menu] Quitting game...")
        pygame.quit()
        exit()

    def _toggle_mute(self, checked: bool) -> None:
        """Toggle audio mute."""
        if checked:
            self.sound_manager.set_master_volume(0)
            print("[Pause Menu] Audio muted")
        else:
            # Get the current volume slider value
            volume_element = None
            for element in self.pause_panel.elements:
                if element.id == "master_vol":
                    volume_element = element
                    break

            if volume_element:
                self.sound_manager.set_master_volume(volume_element.value / 100.0)
            print("[Pause Menu] Audio unmuted")

    def _update_volume(self, value: float) -> None:
        """Update master volume."""
        # Check if audio is not muted
        mute_element = None
        for element in self.pause_panel.elements:
            if element.id == "mute_audio":
                mute_element = element
                break

        if not (mute_element and mute_element.checked):
            self.sound_manager.set_master_volume(value / 100.0)
            print(f"[Pause Menu] Volume set to {int(value)}%")

    # -------------------CLASS METHOD-------------------------------------
    def pause(self) -> None:
        """Pause the game and show pause panel."""
        self.is_paused = True
        self.show_pause_panel = True
        # Pause background music or reduce volume
        self.sound_manager.pause_background_music()

    def unpause(self) -> None:
        """Resume the game and hide pause panel."""
        self.is_paused = False
        self.show_pause_panel = False
        # Resume background music
        self.sound_manager.resume_background_music()

    # -------------------CLASS PROPERTIES---------------------------------
    @property
    def game_data(self) -> Dict[str, Any]:
        """Return all data needed for rendering."""
        return {
            'player': self.player,
            'enemies': self.enemies,
            'camera': self.camera,
            'background': self.background,
            'wave_manager': self.wave_manager,
            'game_time': self.game_time,
            'is_paused': self.is_paused,
            'pause_panel': self.pause_panel,
            'show_pause_panel': self.show_pause_panel
        }

    def _setup_audio(self) -> None:
        """Setup background music for gameplay."""
        self.sound_manager.stop_background_music()
        # GAMEPLAY_MUSIC_PATH
        if self.sound_manager.load_background_music(GAMEPLAY_MUSIC_PATH):
            self.sound_manager.play_background_music()

    def _handle_input(self) -> Optional[str]:
        """Process player input and return state change if needed."""
        keys = pygame.key.get_pressed()

        # Check for pause toggle using key state instead of InputHandler
        if keys[pygame.K_ESCAPE]:
            # Add a simple debounce to prevent multiple toggles
            current_time = pygame.time.get_ticks()
            if not hasattr(self, '_last_esc_time') or current_time - self._last_esc_time > 200:
                self._last_esc_time = current_time
                if self.is_paused:
                    self.unpause()
                else:
                    self.pause()

        if keys[DASH_KEY]:
            # print("This player should take an effect of dash")
            self.player.dash()

        # If paused, don't process game input
        if self.is_paused:
            return None

        # Player actions (only when not paused)
        if keys[pygame.K_SPACE]:
            self.player.attack(self.enemies)

        # Camera zoom
        zoom_change = (keys[pygame.K_EQUALS] - keys[pygame.K_MINUS]) * 0.1
        if zoom_change:
            new_zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.camera.target_zoom + zoom_change))
            self.camera.set_zoom(new_zoom)

        # Check for state changes from pause panel actions
        if hasattr(self, '_next_state'):
            next_state = self._next_state
            delattr(self, '_next_state')
            return next_state

        return None

    def _handle_pause_panel_events(self, event) -> bool:
        """Handle events for the pause panel when visible."""
        if not self.show_pause_panel or not self.pause_panel:
            return False

        # Calculate panel position (centered on screen)
        panel_x = (SCREEN_WIDTH - self.pause_panel.width) // 2
        panel_y = (SCREEN_HEIGHT - self.pause_panel.height) // 2
        panel_position = (panel_x, panel_y)

        # Let the panel handle the event
        return self.pause_panel.handle_event(event, panel_position)

    # -------------------Player Properties-----------------------------
    def _get_player_distance(self, enemy) -> float:
        """Calculate distance from enemy to player."""
        return math.hypot(self.player.x - enemy.x, self.player.y - enemy.y)

    def _update_player(self, dt: float) -> None:
        """Update player with world boundary constraints."""
        if self.is_paused:
            return

        self.player.update(dt)

        # Apply world boundaries
        bounds = self.background.get_world_bounds()
        self.player.x = max(bounds[0] + self.player.radius,
                           min(bounds[2] - self.player.radius, self.player.x))
        self.player.y = max(bounds[1] + self.player.radius,
                           min(bounds[3] - self.player.radius, self.player.y))

    # -------------------Enemy Properties------------------------------
    def _handle_melee_enemy(self, enemy, distance: float, unit_vector: Tuple[float, float], speed: float) -> None:
        """Handle melee enemy behavior."""
        if distance > enemy.attack_range:
            enemy.x += unit_vector[0] * speed
            enemy.y += unit_vector[1] * speed
        elif enemy.attack_cooldown <= 0 and not getattr(enemy, 'is_dying', False):
            self._execute_enemy_attack(enemy)

    def _handle_ranged_enemy(self, enemy, distance: float, unit_vector: Tuple[float, float], speed: float) -> None:
        """Handle ranged enemy behavior with tactical positioning."""
        # Define preferred combat distances
        preferred_distances = {"sniper": 220, "fireshooter": 100}
        preferred_distance = preferred_distances.get(enemy.type, 150)

        # Tactical movement based on distance
        if distance < preferred_distance * 0.8:
            # Retreat
            enemy.x -= unit_vector[0] * speed * 0.9
            enemy.y -= unit_vector[1] * speed * 0.9
        elif distance > preferred_distance * 1.3:
            # Advance
            enemy.x += unit_vector[0] * speed * 0.6
            enemy.y += unit_vector[1] * speed * 0.6
        else:
            # Strafe movement
            enemy.x += -unit_vector[1] * speed * 0.5
            enemy.y += unit_vector[0] * speed * 0.5

        # Attack if in range
        if (distance <= enemy.attack_range and enemy.attack_cooldown <= 0
            and not getattr(enemy, 'is_dying', False)):
            self._execute_enemy_attack(enemy)

    def _get_unit_vector_to_player(self, enemy, distance: Optional[float] = None) -> Tuple[float, float]:
        """Get unit vector from enemy to player."""
        if distance is None:
            distance = self._get_player_distance(enemy)

        if distance > 0:
            dx = self.player.x - enemy.x
            dy = self.player.y - enemy.y
            return dx / distance, dy / distance

        return 0.0, 0.0

    def _execute_enemy_attack(self, enemy) -> None:
        """Execute enemy attack if not dying."""
        if getattr(enemy, 'is_dying', False):
            return

        if enemy.type in {"crawler", "brute"}:
            self.player.take_damage(enemy.attack_power, enemy=enemy)
            enemy.attack_cooldown = 0.9
        else:
            enemy._initiate_ranged_attack(self.player)

    # -------------------Combat Formation Properties-------------------
    def _update_formation_ai(self, enemy, dt: float) -> None:
        """Update AI for enemies in formation."""
        player_distance = self._get_player_distance(enemy)

        # Prioritize combat over formation positioning
        if player_distance <= enemy.attack_range * 1.2:
            self._execute_combat_behavior(enemy, player_distance)
        else:
            self._move_to_formation(enemy, dt, player_distance)

    def _update_standard_ai(self, enemy, dt: float) -> None:
        """Update standard enemy AI behavior."""
        player_distance = self._get_player_distance(enemy)
        unit_vector = self._get_unit_vector_to_player(enemy, player_distance)

        # Calculate movement speed with knockback consideration
        knockback_factor = max(0.4, 1.0 - math.hypot(*enemy.knockback_velocity) / 150)
        move_speed = enemy.speed * knockback_factor * dt

        # Handle different enemy types
        if enemy.type in {"crawler", "brute"}:
            self._handle_melee_enemy(enemy, player_distance, unit_vector, move_speed)
        else:
            self._handle_ranged_enemy(enemy, player_distance, unit_vector, move_speed)

    def _move_to_formation(self, enemy, dt: float, player_distance: float) -> None:
        """Move enemy to formation position."""
        target_x, target_y = enemy.form_target
        dx, dy = target_x - enemy.x, target_y - enemy.y
        formation_distance = math.hypot(dx, dy)

        if formation_distance > 25:
            # Move to formation at reduced speed
            speed = enemy.speed * 0.7 * dt
            enemy.x += (dx / formation_distance) * speed
            enemy.y += (dy / formation_distance) * speed

        # Always ready to attack player
        if player_distance <= enemy.attack_range and enemy.attack_cooldown <= 0:
            self._execute_enemy_attack(enemy)

    def _execute_combat_behavior(self, enemy, distance: float) -> None:
        """Execute direct combat behavior."""
        if enemy.type in {"crawler", "brute"}:
            # Aggressive melee approach
            if distance > enemy.attack_range:
                unit_vector = self._get_unit_vector_to_player(enemy, distance)
                speed = enemy.speed * 1.1  # 10% faster in combat
                enemy.x += unit_vector[0] * speed
                enemy.y += unit_vector[1] * speed
            elif enemy.attack_cooldown <= 0:
                self._execute_enemy_attack(enemy)
        else:
            # Ranged combat
            if distance <= enemy.attack_range and enemy.attack_cooldown <= 0:
                self._execute_enemy_attack(enemy)

    def _update_combat(self, dt: float) -> None:
        """Update combat system with formation management."""
        if self.is_paused:
            return

        self.formation_system.update(dt, self.enemies, self.player)

        # Remove enemies that have completed death animations
        self.enemies = [enemy for enemy in self.enemies if not enemy.should_be_removed()]

        # Update each enemy with enhanced AI
        for enemy in self.enemies:
            if getattr(enemy, 'form_active', False):
                self._update_formation_ai(enemy, dt)
            else:
                self._update_standard_ai(enemy, dt)

            enemy.update(dt, self.player)

    # -------------------Background Properties-------------------------
    def _update_systems(self, dt: float) -> None:
        """Update world systems and wave management."""
        if self.is_paused:
            # Still update camera for smooth pause transitions
            self.camera.update(dt, self.player.x, self.player.y)
            return

        self.background.update(dt)
        self.camera.update(dt, self.player.x, self.player.y)

        # Handle wave progression
        if self.wave_manager.update(dt, self.enemies):
            self.wave_manager.start_wave(self.wave_manager.current_wave + 1)

    # -------------------MAIN GAMEPLAY STATE HANDLE--------------------
    def update(self, dt: float) -> Optional[str]:
        """Main update loop returning next state or None."""
        self.game_time += dt
        self.input_handler.update()

        # Process input first
        if next_state := self._handle_input():
            return next_state

        # Update pause panel if visible
        if self.show_pause_panel and self.pause_panel:
            self.pause_panel.update()
            # Add cursor management for pause panel
            panel_x = (SCREEN_WIDTH - self.pause_panel.width) // 2
            panel_y = (SCREEN_HEIGHT - self.pause_panel.height) // 2
            self.pause_panel.update_cursor((panel_x, panel_y))
        else:
            # Reset cursor to default when pause panel is not shown
            set_cursor_pointer()

        # Update game systems (respects pause state internally)
        self._update_player(dt)
        self._update_combat(dt)
        self._update_systems(dt)

        # Check game over condition (only when not paused)
        if not self.is_paused and self.player.hp <= 0:
            return "game_over"

        return None

    def handle_event(self, event) -> bool:
        """Handle pygame events, return True if event was consumed."""
        # First, let pause panel handle events if it's visible
        if self.show_pause_panel and self.pause_panel:
            if self._handle_pause_panel_events(event):
                return True

        return False

    def render(self): # DO NOTHING: Since the gameplay_renderer.py will handle those
        pass
