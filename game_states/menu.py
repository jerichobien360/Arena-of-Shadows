from settings import *
import pygame

# game_states file
from game_states.gameplay import *

class MainMenuState(GameState):
    def __init__(self, font, sound_manager):
        self.font = font
        self.sound_manager = sound_manager
        
        # Animation variables
        self.fade_alpha = 0
        self.fade_speed = 255  # Alpha units per second
        self.fade_direction = 1  # 1 for fade in, -1 for fade out
        self.transitioning = False
        self.transition_target = None
        
        # Text animation variables
        self.title_pulse_time = 0
        self.text_appear_time = 0
        self.text_stagger_delay = 0.3  # Delay between text elements appearing
        
        # Create surfaces for fade transitions
        self.fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fade_surface.fill(BLACK)
        
    def enter(self):
        # Reset animation state when entering
        self.fade_alpha = 255  # Start fully black
        self.fade_direction = 1  # Fade in
        self.transitioning = False
        self.transition_target = None
        self.title_pulse_time = 0
        self.text_appear_time = 0
        
        # Load and play menu music
        if self.sound_manager.load_background_music("assets/background_music/main_menu.mp3"):
            self.sound_manager.play_background_music()
    
    def start_transition(self, target_state):
        """Start a fade-out transition to the target state"""
        if not self.transitioning:
            self.transitioning = True
            self.transition_target = target_state
            self.fade_direction = -1  # Fade out
    
    def update(self, dt):
        # Update animation timers
        self.title_pulse_time += dt
        self.text_appear_time += dt
        
        # Handle fade transitions
        if self.transitioning:
            # Fade out
            self.fade_alpha -= self.fade_speed * dt
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                return self.transition_target
        else:
            # Fade in when not transitioning
            if self.fade_direction == 1:
                self.fade_alpha -= self.fade_speed * dt
                if self.fade_alpha <= 0:
                    self.fade_alpha = 0
                    self.fade_direction = 0  # Stop fading
        
        # Handle input only when not transitioning and fully faded in
        if not self.transitioning and self.fade_alpha == 0:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
                self.start_transition("gameplay")
        
        return None
    
    def render(self, screen):
        screen.fill(BLACK)
        
        # Calculate text animations
        title_scale = 1.0 + 0.1 * math.sin(self.title_pulse_time * 2)  # Pulsing effect
        title_alpha = min(255, max(0, (self.text_appear_time - 0.5) * 255))
        
        start_alpha = min(255, max(0, (self.text_appear_time - self.text_stagger_delay) * 255))
        controls_alpha = min(255, max(0, (self.text_appear_time - self.text_stagger_delay * 2) * 255))
        
        # Create animated title with scaling and alpha
        if title_alpha > 0:
            title_font_size = int(self.font.get_height() * title_scale)
            title_font = pygame.font.Font(None, title_font_size)
            title_surface = title_font.render("ARENA OF SHADOWS", True, WHITE)
            title_surface.set_alpha(int(title_alpha))
            
            title_x = SCREEN_WIDTH // 2 - title_surface.get_width() // 2
            title_y = 180 + int(10 * math.sin(self.title_pulse_time * 3))  # Floating effect
            screen.blit(title_surface, (title_x, title_y))
        
        # Render start text with fade-in and blinking when fully visible
        if start_alpha > 0:
            start_text = "Press ENTER to Start"
            start_surface = self.font.render(start_text, True, GRAY)
            
            # Add blinking effect when fully visible
            if start_alpha >= 255:
                blink_alpha = int(255 * (0.7 + 0.3 * math.sin(self.title_pulse_time * 4)))
                start_surface.set_alpha(blink_alpha)
            else:
                start_surface.set_alpha(int(start_alpha))
            
            start_x = SCREEN_WIDTH // 2 - start_surface.get_width() // 2
            start_y = 280
            screen.blit(start_surface, (start_x, start_y))
        
        # Render controls text with fade-in
        if controls_alpha > 0:
            controls_surface = self.font.render("WASD/Arrows: Move | SPACE: Attack", True, GRAY)
            controls_surface.set_alpha(int(controls_alpha))
            
            controls_x = SCREEN_WIDTH // 2 - controls_surface.get_width() // 2
            controls_y = 330
            screen.blit(controls_surface, (controls_x, controls_y))
        
        # Apply fade overlay
        if self.fade_alpha > 0:
            self.fade_surface.set_alpha(int(self.fade_alpha))
            screen.blit(self.fade_surface, (0, 0))
