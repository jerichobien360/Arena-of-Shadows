from settings import *
from systems.manager.asset_manager import *
from game_function.game_function import *

import pygame
import math


class LoadingScreenState:
    """A simple loading screen state with animated loading indicators."""
    
    def __init__(self, prev_state, sound_manager=None):
        """Initialize the loading screen.
        
        Args:
            screen_width (int): Width of the screen
            screen_height (int): Height of the screen
        """
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.prev_state = prev_state
        
        # Loading animation properties
        self.loading_time = 0.0
        self.dots_count = 3
        self.dot_flash_speed = 0.5
        
        # Spinner properties
        self.spinner_angle = 0
        self.spinner_speed = 180  # degrees per second
        
        # Colors
        self.bg_color = (20, 20, 30)
        self.text_color = (255, 255, 255)
        self.accent_color = (100, 150, 255)
        self.spinner_color = (150, 200, 255)
        
        # Font (will be initialized in enter())
        self.font = None
        self.title_font = None
        
        # Loading progress (0.0 to 1.0)
        self.progress = 0.0
        self.loading_complete = False
        
        # Customizable loading text
        self.loading_text = "Loading"
        self.title_text = "Game Loading"

        # Main Component - for loading computation
        self.sound_manager = sound_manager
    
    def enter(self):
        """Called when entering this state."""
        # Initialize fonts
        pygame.font.init()
        self.font = FONT() # pygame.font.Font(None, 48)
        self.title_font = FONT() # pygame.font.Font(None, 72)
        
        # Reset loading state
        self.loading_time = 0.0
        self.progress = 0.0
        self.loading_complete = False
        self.spinner_angle = 0
        
        print("Loading screen entered")
    
    def exit(self):
        """Called when exiting this state."""
        print("Loading screen exited")
    
    def update(self, delta_time):
        """Update the loading screen animation.
        
        Args:
            delta_time (float): Time since last update in seconds
            
        Returns:
            str or None: Next state name if loading complete, None otherwise
        """
        self.loading_time += delta_time
        
        # Update spinner rotation
        self.spinner_angle += self.spinner_speed * delta_time
        self.spinner_angle %= 360
        seconds = 250 # Default: 1000
        
        if self.sound_manager:
            # Load one file per frame
            self.sound_manager.update_loading()
            
            # Calculate progress
            if self.sound_manager.total_assets > 0:
                self.progress = self.sound_manager.loaded_assets / self.sound_manager.total_assets
            
            # Check if loading is complete
            if self.sound_manager.loading_complete:
                self.loading_complete = True
                pygame.time.wait(seconds) # Improving the loading screen with a slight delay
                return self.prev_state
        else:
            # Fallback
            self.progress += delta_time * 0.2
            if self.progress >= 1.0:
                self.progress = 1.0
                self.loading_complete = True
                pygame.time.wait(seconds) # Improving the loading screen with a slight delay
                return self.prev_state
        
        return None
    
    def render(self, screen):
        """Render the loading screen.
        
        Args:
            screen: Pygame screen surface to render to
        """
        # Clear screen with background color
        screen.fill(self.bg_color)
        
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        # Render title
        title_surface = self.title_font.render(self.title_text, True, self.text_color)
        title_rect = title_surface.get_rect(center=(center_x, center_y - 100))
        screen.blit(title_surface, title_rect)
        
        # Render animated loading text with dots
        # dots = ""
        # for i in range(self.dots_count):
        #     # Make dots flash in sequence
        #     flash_time = (self.loading_time - i * 0.2) % (self.dots_count * self.dot_flash_speed)
        #     if flash_time < self.dot_flash_speed:
        #         dots += "."
        #     else:
        #         dots += " "
        
        # loading_display = f"{self.loading_text}{dots}"
        # loading_surface = self.font.render(loading_display, True, self.text_color)
        # loading_rect = loading_surface.get_rect(center=(center_x, center_y + 50))
        # screen.blit(loading_surface, loading_rect)
        
        # # Render loading progress bar
        # bar_width = 300
        # bar_height = 20
        # bar_x = center_x - bar_width // 2
        # bar_y = center_y + 100
        
        # # Background bar
        # pygame.draw.rect(screen, (50, 50, 60), (bar_x, bar_y, bar_width, bar_height))
        
        # # Progress bar
        # progress_width = int(bar_width * self.progress)
        # if progress_width > 0:
        #     pygame.draw.rect(screen, self.accent_color, (bar_x, bar_y, progress_width, bar_height))
        
        # # Progress percentage
        # percentage = int(self.progress * 100)
        # percent_text = f"{percentage}%"
        # percent_surface = self.font.render(percent_text, True, self.text_color)
        # percent_rect = percent_surface.get_rect(center=(center_x, bar_y + bar_height + 30))
        # screen.blit(percent_surface, percent_rect)
        
        # # Render spinning loading indicator
        # self._draw_spinner(screen, center_x, center_y - 20, 30)

        if self.sound_manager:
            loading_info = f"Loading Assets: {self.sound_manager.loaded_assets}/{self.sound_manager.total_assets}"
        else:
            # Animated dots fallback
            dots = "." * (int(self.loading_time * 2) % 4)
            loading_info = f"{self.loading_text}{dots}"
        
        loading_surface = self.font.render(loading_info, True, self.text_color)
        loading_rect = loading_surface.get_rect(center=(center_x, center_y + 50))
        screen.blit(loading_surface, loading_rect)
        
        # Progress bar
        bar_width = 300
        bar_height = 20
        bar_x = center_x - bar_width // 2
        bar_y = center_y + 100
        
        pygame.draw.rect(screen, (50, 50, 60), (bar_x, bar_y, bar_width, bar_height))
        
        progress_width = int(bar_width * self.progress)
        if progress_width > 0:
            pygame.draw.rect(screen, self.accent_color, (bar_x, bar_y, progress_width, bar_height))
        
        # Percentage
        percentage = int(self.progress * 100)
        percent_text = f"{percentage}%"
        percent_surface = self.font.render(percent_text, True, self.text_color)
        percent_rect = percent_surface.get_rect(center=(center_x, bar_y + bar_height + 30))
        screen.blit(percent_surface, percent_rect)
        
        # Spinner
        self._draw_spinner(screen, center_x, center_y - 20, 30)
    
    def _draw_spinner(self, screen, x, y, radius):
        """Draw a rotating spinner.
        
        Args:
            screen: Pygame screen surface
            x (int): Center x coordinate
            y (int): Center y coordinate
            radius (int): Radius of the spinner
        """
        # Draw multiple arcs to create spinner effect
        arc_count = 8
        arc_length = 30  # degrees
        
        for i in range(arc_count):
            # Calculate angle for this arc
            angle = (self.spinner_angle + i * (360 / arc_count)) % 360
            
            # Calculate alpha (transparency) based on position
            alpha = int(255 * (i / arc_count))
            
            # Create surface for this arc with alpha
            arc_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
            
            # Draw arc on the surface
            start_angle = math.radians(angle)
            end_angle = math.radians(angle + arc_length)
            
            # Draw thick arc using multiple thin arcs
            thickness = 4
            for t in range(thickness):
                current_radius = radius - t
                if current_radius > 0:
                    arc_color = (*self.spinner_color, alpha)
                    
                    # Calculate arc points
                    points = []
                    steps = 10
                    for step in range(steps + 1):
                        a = start_angle + (end_angle - start_angle) * (step / steps)
                        px = radius * 2 + current_radius * math.cos(a)
                        py = radius * 2 + current_radius * math.sin(a)
                        points.append((px, py))
                    
                    # Draw the arc if we have enough points
                    if len(points) > 1:
                        pygame.draw.lines(arc_surface, arc_color, False, points, 2)
            
            # Blit the arc surface to the main screen
            arc_rect = arc_surface.get_rect(center=(x, y))
            screen.blit(arc_surface, arc_rect)
    
    def handle_event(self, event):
        """Handle input events.
        
        Args:
            event: Pygame event to handle
        """
        # You can add event handling here if needed
        # For example, skip loading on key press:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Skip loading
                self.progress = 1.0
                self.loading_complete = True
    
    def set_loading_text(self, text):
        """Set custom loading text.
        
        Args:
            text (str): The loading text to display
        """
        self.loading_text = text
    
    def set_title_text(self, text):
        """Set custom title text.
        
        Args:
            text (str): The title text to display
        """
        self.title_text = text
    
    def set_progress(self, progress):
        """Manually set loading progress.
        
        Args:
            progress (float): Progress value between 0.0 and 1.0
        """
        self.progress = max(0.0, min(1.0, progress))
        if self.progress >= 1.0:
            self.loading_complete = True
    
    def cleanup(self):
        """Clean up resources when the state is destroyed."""
        pass
