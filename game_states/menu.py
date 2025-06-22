"""Main menu state with clean animation and transition handling."""

import pygame
from dataclasses import dataclass
from typing import Optional

from settings import *
from game_states.gameplay import GameState
from ui.effects.particles import ParticleSystem
from ui.screens.main_menu_screen import MainMenuRenderer


@dataclass
class AnimationState:
    """Centralized animation state management."""
    fade_alpha: float = 255.0
    fade_speed: float = 200.0
    fade_direction: int = 1
    transitioning: bool = False
    target: Optional[str] = None
    title_pulse: float = 0.0
    text_appear: float = 0.0
    lighting: float = 0.0
    
    def reset(self) -> None:
        """Reset all animation values to initial state."""
        self.fade_alpha = 255.0
        self.fade_direction = 1
        self.transitioning = False
        self.target = None
        self.title_pulse = 0.0
        self.text_appear = 0.0
        self.lighting = 0.0


@dataclass
class LightingConfig:
    """Lighting system configuration."""
    ambient: float = 0.4
    variation_speed: float = 0.8
    variation_amp: float = 0.05
    background_dim: float = 0.25


class MainMenuState(GameState):
    """Main menu state handling user input, animations, and transitions."""
    
    def __init__(self, font, sound_manager):
        self.font = font
        self.sound_manager = sound_manager
        
        # Initialize state and systems
        self.anim_state = AnimationState()
        self.lighting_config = LightingConfig()
        self.particle_system = ParticleSystem()
        self.renderer = MainMenuRenderer(font, self.lighting_config)
        self.input_enabled = False
        
    def enter(self) -> None:
        """Initialize menu state and start background music."""
        self.anim_state.reset()
        self.input_enabled = False
        self._start_background_music()
    
    def start_transition(self, target_state: str) -> None:
        """Initiate fade transition to target state."""
        if self.anim_state.transitioning:
            return
            
        self.anim_state.transitioning = True
        self.anim_state.target = target_state
        self.anim_state.fade_direction = -1
        self.input_enabled = False
    
    def update(self, dt: float) -> Optional[str]:
        """Main update loop - handles animations, particles, and input."""
        self._update_animations(dt)
        self.particle_system.update(dt)
        
        # Check for state transitions
        if next_state := self._update_fade_transition(dt):
            return next_state
            
        return self._handle_input()
    
    def render(self, screen) -> None:
        """Render the main menu using the dedicated renderer."""
        self.renderer.render(
            screen=screen,
            particles=self.particle_system.get_particles(),
            anim_state=self.anim_state,
            lighting_time=self.anim_state.lighting
        )
    
    def cleanup(self) -> None:
        """Clean up resources when leaving state."""
        self.sound_manager.stop_background_music()
        self.particle_system.clear()
    
    def _start_background_music(self) -> None:
        """Load and start background music with error handling."""
        music_path = "assets/background_music/main_menu.mp3"
        if self.sound_manager.load_background_music(music_path):
            self.sound_manager.play_background_music()
    
    def _update_animations(self, dt: float) -> None:
        """Update all animation timers."""
        self.anim_state.title_pulse += dt
        self.anim_state.text_appear += dt
        self.anim_state.lighting += dt
    
    def _update_fade_transition(self, dt: float) -> Optional[str]:
        """Handle fade transitions with quadratic easing."""
        if not self.anim_state.transitioning:
            return self._handle_fade_in(dt)
        
        return self._handle_fade_out(dt)
    
    def _handle_fade_in(self, dt: float) -> None:
        """Handle initial fade-in when menu starts."""
        if self.anim_state.fade_direction != 1:
            return
            
        self.anim_state.fade_alpha -= self.anim_state.fade_speed * dt
        if self.anim_state.fade_alpha <= 0:
            self.anim_state.fade_alpha = 0
            self.anim_state.fade_direction = 0
            self.input_enabled = True
    
    def _handle_fade_out(self, dt: float) -> Optional[str]:
        """Handle fade-out transition to next state."""
        fade_progress = 1.0 - (self.anim_state.fade_alpha / 255.0)
        self.anim_state.fade_alpha = 255 * (1.0 - fade_progress * fade_progress)
        self.anim_state.fade_alpha -= self.anim_state.fade_speed * dt
        
        if self.anim_state.fade_alpha <= 0:
            return self.anim_state.target
        return None
    
    def _handle_input(self) -> Optional[str]:
        """Process user input when enabled."""
        if not self.input_enabled:
            return None
            
        if pygame.key.get_pressed()[pygame.K_RETURN]:
            self.start_transition("gameplay")
        
        return None
