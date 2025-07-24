"""Main menu state with clean animation and transition handling."""

import pygame
from dataclasses import dataclass
from typing import Optional

from settings import *
from game_states.gameplay import GameState
from ui.effects.particles import ParticleSystem
from ui.screens.main_menu_screen import MainMenuRenderer
from ui.effects.animations import AnimationState
from ui.effects.lighting import LightingConfig


class MainMenuState(GameState):
    """Main menu state handling user input, animations, and transitions."""
    
    def __init__(self, font, sound_manager):
        print("\n[System]: Initializing the Main Menu Screen\n")
        self.font = font
        self.sound_manager = sound_manager
        
        # Initialize state and systems
        self.animate_state = AnimationState()
        self.lighting_config = LightingConfig()
        self.particle_system = ParticleSystem()
        self.renderer = MainMenuRenderer(font, self.lighting_config)
        self.input_enabled = False
    
    # -------------------INITIALIZE & CLEANUP-----------------------------
    def enter(self) -> None:
        """Initialize menu state and start background music."""
        self.animate_state.reset()
        self.input_enabled = False
        self._start_background_music()
    
    def cleanup(self) -> None:
        """Clean up resources when leaving state."""
        self.sound_manager.stop_background_music()
        self.particle_system.clear()

    # -------------------CLASS METHOD-------------------------------------
    def start_transition(self, target_state: str) -> None:
        """Initiate fade transition to target state."""
        if self.animate_state.transitioning:
            return
            
        self.animate_state.transitioning = True
        self.animate_state.target = target_state
        self.animate_state.fade_direction = -1
        self.input_enabled = False

    # -------------------CLASS PROPERTIES---------------------------------
    def _start_background_music(self) -> None:
        """Load and start background music with error handling."""
        # MENEU_MUSIC_PATH
        if self.sound_manager.load_background_music(MENU_MUSIC_PATH):
            self.sound_manager.play_background_music()
    
    def _update_animations(self, dt: float) -> None:
        """Update all animation timers."""
        self.animate_state.title_pulse += dt
        self.animate_state.text_appear += dt
        self.animate_state.lighting += dt
    
    def _handle_fade_in(self, dt: float) -> None:
        """Handle initial fade-in when menu starts."""
        if self.animate_state.fade_direction == 1:
            self.animate_state.fade_alpha -= self.animate_state.fade_speed * dt
            if self.animate_state.fade_alpha <= 0:
                self.animate_state.fade_alpha = 0
                self.animate_state.fade_direction = 0
                self.input_enabled = True
    
    def _handle_fade_out(self, dt: float) -> Optional[str]:
        """Handle fade-out transition to next state."""
        # Apply quadratic easing for smooth transition
        fade_progress = 1.0 - (self.animate_state.fade_alpha / 255.0)
        self.animate_state.fade_alpha = 255 * (1.0 - fade_progress * fade_progress)
        self.animate_state.fade_alpha -= self.animate_state.fade_speed * dt
        
        # Check if transition is complete
        if self.animate_state.fade_alpha <= 0:
            return self.animate_state.target
        return None
    
    def _handle_input(self) -> Optional[str]:
        """Process user input when enabled."""
        if not self.input_enabled:
            return None
            
        if pygame.key.get_pressed()[pygame.K_RETURN]:
            self.start_transition("gameplay")
        
        return None

    # -------------------GAME STATE HANDLE-----------------------------
    def update(self, dt: float) -> Optional[str]:
        """Main update loop - handles animations, particles, and input."""
        # Update animations and particles
        self._update_animations(dt)
        self.particle_system.update(dt)
        
        # Handle fade transitions
        if self.animate_state.transitioning:
            return self._handle_fade_out(dt)
        else:
            self._handle_fade_in(dt)
            
        # Process input when ready
        return self._handle_input()

    def render(self, screen) -> None:
        """Render the main menu using the dedicated renderer."""
        self.renderer.render(
            screen=screen,
            particles=self.particle_system.get_particles(),
            animate_state=self.animate_state,
            lighting_time=self.animate_state.lighting
        )
