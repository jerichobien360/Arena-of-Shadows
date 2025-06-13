from settings import *
import pygame
import math
# gameplay state file
from game_states.gameplay import *

class GameOverState(GameState):
    def __init__(self, font, sound_manager):
        self.font = font
        self.sound_manager = sound_manager
        
        # Animation properties
        self.fade_timer = 0.0
        self.fade_duration = 2.0  # Total fade in duration
        self.text_delay = 0.5     # Delay before text starts appearing
        self.pulse_timer = 0.0
        
        # Text animation states
        self.game_over_alpha = 0
        self.restart_alpha = 0
        
        # Overlay properties
        self.overlay_alpha = 0
        self.max_overlay_alpha = int(255 * 0.12)  # 12% transparency
        
        # Create overlay surface
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay.fill((0, 0, 0))  # Black overlay
        
        # Animation completed flags
        self.fade_complete = False
        self.can_exit = False
   
    def enter(self):
        """Reset animation state when entering game over"""
        self.sound_manager.stop_background_music()
        
        # Reset all animation timers
        self.fade_timer = 0.0
        self.pulse_timer = 0.0
        self.game_over_alpha = 0
        self.restart_alpha = 0
        self.overlay_alpha = 0
        self.fade_complete = False
        self.can_exit = False
   
    def update(self, dt):
        """Update animations and handle input"""
        # Update fade timer
        self.fade_timer += dt
        self.pulse_timer += dt
        
        # Calculate overlay fade-in (quick fade to 12% opacity)
        overlay_fade_duration = 0.8
        if self.fade_timer <= overlay_fade_duration:
            progress = self.fade_timer / overlay_fade_duration
            # Smooth ease-in curve
            progress = progress * progress
            self.overlay_alpha = int(self.max_overlay_alpha * progress)
        else:
            self.overlay_alpha = self.max_overlay_alpha
        
        # Calculate "GAME OVER" text fade-in
        game_over_start = self.text_delay
        game_over_duration = 1.0
        if self.fade_timer >= game_over_start:
            progress = min(1.0, (self.fade_timer - game_over_start) / game_over_duration)
            # Smooth ease-out curve for dramatic effect
            progress = 1.0 - (1.0 - progress) ** 3
            self.game_over_alpha = int(255 * progress)
        
        # Calculate restart text fade-in (appears after game over text)
        restart_start = game_over_start + game_over_duration * 0.7
        restart_duration = 0.8
        if self.fade_timer >= restart_start:
            progress = min(1.0, (self.fade_timer - restart_start) / restart_duration)
            # Linear fade for subtitle text
            self.restart_alpha = int(180 * progress)  # Slightly dimmer than main text
            
            # Enable input after restart text appears
            if progress >= 0.5:
                self.can_exit = True
        
        # Mark fade as complete
        if self.fade_timer >= self.fade_duration:
            self.fade_complete = True
        
        # Handle input (only after animation is mostly complete)
        if self.can_exit:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                return "main_menu"
        
        return None
   
    def render(self, screen):
        """Render the animated game over screen"""
        # Don't fill the screen with black - keep the game state visible underneath
        
        # Draw transparent overlay
        if self.overlay_alpha > 0:
            self.overlay.set_alpha(self.overlay_alpha)
            screen.blit(self.overlay, (0, 0))
        
        # Render "GAME OVER" text with fade and pulse effect
        if self.game_over_alpha > 0:
            # Create pulsing effect for dramatic impact
            pulse_scale = 1.0
            if self.fade_complete:
                pulse_intensity = 0.1
                pulse_scale = 1.0 + math.sin(self.pulse_timer * 2.0) * pulse_intensity
            
            # Render main text
            game_over_text = self.font.render("GAME OVER", True, WHITE)
            
            # Apply pulse scaling
            if pulse_scale != 1.0:
                original_size = game_over_text.get_size()
                new_width = int(original_size[0] * pulse_scale)
                new_height = int(original_size[1] * pulse_scale)
                game_over_text = pygame.transform.scale(game_over_text, (new_width, new_height))
            
            # Set alpha and position
            game_over_text.set_alpha(self.game_over_alpha)
            text_x = SCREEN_WIDTH // 2 - game_over_text.get_width() // 2
            text_y = SCREEN_HEIGHT // 2 - 50
            
            # Add subtle drop shadow for depth
            if self.game_over_alpha > 100:
                shadow_alpha = min(80, self.game_over_alpha - 100)
                shadow_text = self.font.render("GAME OVER", True, (20, 20, 20))
                if pulse_scale != 1.0:
                    shadow_text = pygame.transform.scale(shadow_text, (new_width, new_height))
                shadow_text.set_alpha(shadow_alpha)
                screen.blit(shadow_text, (text_x + 3, text_y + 3))
            
            screen.blit(game_over_text, (text_x, text_y))
        
        # Render restart instruction with fade and subtle animation
        if self.restart_alpha > 0:
            # Create subtle floating animation for restart text
            float_offset = 0
            if self.fade_complete:
                float_offset = math.sin(self.pulse_timer * 1.5) * 2
            
            restart_text = self.font.render("Press ENTER to return to menu", True, GRAY)
            restart_text.set_alpha(self.restart_alpha)
            
            restart_x = SCREEN_WIDTH // 2 - restart_text.get_width() // 2
            restart_y = SCREEN_HEIGHT // 2 + 30 + float_offset
            
            # Add subtle glow effect when text is fully visible
            if self.restart_alpha > 150:
                glow_alpha = min(30, self.restart_alpha - 150)
                for offset in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    glow_text = self.font.render("Press ENTER to return to menu", True, WHITE)
                    glow_text.set_alpha(glow_alpha)
                    screen.blit(glow_text, (restart_x + offset[0], restart_y + offset[1]))
            
            screen.blit(restart_text, (restart_x, restart_y))
        
        # Optional: Add particle effects or additional visual elements
        self._render_particles(screen)
    
    def _render_particles(self, screen):
        """Render subtle particle effects for atmosphere"""
        if not self.fade_complete:
            return
        
        # Simple floating particles effect
        particle_count = 8
        for i in range(particle_count):
            # Create deterministic but varied particle positions
            base_time = self.pulse_timer + i * 0.5
            x = (SCREEN_WIDTH * 0.2) + (i * SCREEN_WIDTH * 0.1) + math.sin(base_time * 0.8) * 30
            y = (SCREEN_HEIGHT * 0.3) + math.cos(base_time * 0.6) * 40 + (i * 15)
            
            # Fade particles in and out
            particle_alpha = int(20 + math.sin(base_time * 1.2) * 15)
            particle_alpha = max(0, min(35, particle_alpha))
            
            if particle_alpha > 0:
                particle_size = 2 + int(math.sin(base_time) * 1)
                particle_color = (100, 100, 100, particle_alpha)
                
                # Create particle surface with per-pixel alpha
                particle_surf = pygame.Surface((particle_size * 2, particle_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, particle_color, 
                                 (particle_size, particle_size), particle_size)
                
                screen.blit(particle_surf, (int(x), int(y)))
