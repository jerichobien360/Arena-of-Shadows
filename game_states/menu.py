from settings import *
import pygame
from dataclasses import dataclass, field
from typing import Dict, Any
from game_states.gameplay import GameState
from ui.effects.particles import ParticleSystem
from ui.screens.main_menu_screen import MainMenuRenderer


@dataclass
class AnimationState:
    """Centralized animation state management"""
    fade_alpha: float = 255
    fade_speed: float = 200
    fade_direction: int = 1
    transitioning: bool = False
    target: str = None
    title_pulse: float = 0
    text_appear: float = 0
    lighting: float = 0
    
    def reset(self):
        """Reset all animation values to initial state"""
        self.fade_alpha = 255
        self.fade_direction = 1
        self.transitioning = False
        self.target = None
        self.title_pulse = 0
        self.text_appear = 0
        self.lighting = 0


@dataclass
class LightingConfig:
    """Lighting system configuration"""
    ambient: float = 0.4
    variation_speed: float = 0.8
    variation_amp: float = 0.05
    background_dim: float = 0.25


class MainMenuState(GameState):
    """Main menu core logic - handles state management and transitions"""
    
    def __init__(self, font, sound_manager):
        self.font = font
        self.sound_manager = sound_manager
        
        # Core state management
        self.anim_state = AnimationState()
        self.lighting_config = LightingConfig()
        
        # Initialize systems
        self.particle_system = ParticleSystem()
        self.renderer = MainMenuRenderer(font, self.lighting_config)
        
        # Input handling
        self.input_enabled = False
        
    def enter(self):
        """Initialize menu state and start background music"""
        self.anim_state.reset()
        self.input_enabled = False
        
        # Start background music with error handling
        if self.sound_manager.load_background_music("assets/background_music/main_menu.mp3"):
            self.sound_manager.play_background_music()
    
    def start_transition(self, target_state: str):
        """Initiate fade transition to target state"""
        if not self.anim_state.transitioning:
            self.anim_state.transitioning = True
            self.anim_state.target = target_state
            self.anim_state.fade_direction = -1
            self.input_enabled = False
    
    def _update_animations(self, dt: float):
        """Update all animation timers"""
        self.anim_state.title_pulse += dt
        self.anim_state.text_appear += dt
        self.anim_state.lighting += dt
    
    def _update_fade_transition(self, dt: float) -> str:
        """Handle fade transitions with quadratic easing"""
        if not self.anim_state.transitioning:
            # Fade in from black on menu start
            if self.anim_state.fade_direction == 1:
                self.anim_state.fade_alpha -= self.anim_state.fade_speed * dt
                if self.anim_state.fade_alpha <= 0:
                    self.anim_state.fade_alpha = 0
                    self.anim_state.fade_direction = 0
                    self.input_enabled = True
            return None
        
        # Fade out transition
        fade_progress = 1.0 - (self.anim_state.fade_alpha / 255.0)
        self.anim_state.fade_alpha = 255 * (1.0 - fade_progress * fade_progress)
        self.anim_state.fade_alpha -= self.anim_state.fade_speed * dt
        
        if self.anim_state.fade_alpha <= 0:
            return self.anim_state.target
        
        return None
    
    def _handle_input(self) -> str:
        """Process user input when enabled"""
        if not self.input_enabled:
            return None
            
        if pygame.key.get_pressed()[pygame.K_RETURN]:
            self.start_transition("gameplay")
            return None
        
        return None
    
    def update(self, dt: float) -> str:
        """Main update loop - pure logic, no rendering"""
        self._update_animations(dt)
        
        # Update particle system
        self.particle_system.update(dt)
        
        # Handle transitions
        if next_state := self._update_fade_transition(dt):
            return next_state
        
        # Handle input
        if next_state := self._handle_input():
            return next_state
            
        return None
    
    def render(self, screen):
        """Delegate all rendering to the renderer"""
        self.renderer.render(
            screen=screen,
            particles=self.particle_system.get_particles(),
            anim_state=self.anim_state,
            lighting_time=self.anim_state.lighting
        )
    
    def cleanup(self):
        """Clean up resources when leaving state"""
        self.sound_manager.stop_background_music()
        self.particle_system.clear()
