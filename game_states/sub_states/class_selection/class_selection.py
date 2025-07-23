from settings import *
from entities.character_classes import CHARACTER_CLASSES
import pygame
import math


class ClassSelectionState:
    """State for selecting character class before starting the game"""
    
    def __init__(self, font, sound_manager):
        self.font = font
        self.sound_manager = sound_manager
        self.large_font = pygame.font.Font(None, 64)
        self.medium_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Available classes
        self.classes = ['warrior', 'mage', 'fireshooter']
        self.class_objects = [CHARACTER_CLASSES[cls] for cls in self.classes]
        
        # Selection state
        self.selected_index = 0
        self.selected_class = None
        self.animation_time = 0
        self.preview_time = 0
        
        # Input handling
        self.input_cooldown = 0
        
        # Animation states
        self.fade_alpha = 255
        self.transitioning = False
        self.transition_target = None
        
        # Create class preview surfaces
        self.preview_surfaces = {}
        self._create_preview_surfaces()
        
    def _create_preview_surfaces(self):
        """Create preview surfaces for each character class"""
        for class_name, class_obj in zip(self.classes, self.class_objects):
            surface = pygame.Surface((200, 200), pygame.SRCALPHA)
            
            # Draw class representation
            center = (100, 100)
            
            # Main character circle
            pygame.draw.circle(surface, class_obj.color, center, 30)
            pygame.draw.circle(surface, class_obj.secondary_color, center, 30, 3)
            
            # Class-specific visual elements
            if class_name == 'warrior':
                # Draw sword
                sword_points = [
                    (center[0] - 5, center[1] - 40),
                    (center[0] + 5, center[1] - 40),
                    (center[0] + 3, center[1] + 20),
                    (center[0] - 3, center[1] + 20)
                ]
                pygame.draw.polygon(surface, (150, 150, 150), sword_points)
                # Sword hilt
                pygame.draw.rect(surface, (100, 50, 0), (center[0] - 8, center[1] + 20, 16, 6))
                
            elif class_name == 'mage':
                # Draw staff
                pygame.draw.line(surface, (100, 50, 0), 
                               (center[0] + 20, center[1] - 30), 
                               (center[0] + 20, center[1] + 30), 3)
                # Staff orb
                pygame.draw.circle(surface, (100, 100, 255), (center[0] + 20, center[1] - 35), 8)
                pygame.draw.circle(surface, (200, 200, 255), (center[0] + 20, center[1] - 35), 5)
                
            elif class_name == 'fireshooter':
                # Draw flame weapon
                flame_points = [
                    (center[0] + 25, center[1] - 10),
                    (center[0] + 35, center[1] - 15),
                    (center[0] + 40, center[1]),
                    (center[0] + 35, center[1] + 15),
                    (center[0] + 25, center[1] + 10)
                ]
                pygame.draw.polygon(surface, (255, 100, 0), flame_points)
                pygame.draw.polygon(surface, (255, 200, 0), flame_points[1:-1])
            
            self.preview_surfaces[class_name] = surface
    
    def enter(self):
        """Initialize state when entering"""
        self.selected_index = 0
        self.selected_class = None
        self.animation_time = 0
        self.fade_alpha = 255
        self.transitioning = False
        
        # Play selection music if available
        self.sound_manager.stop_background_music()
        if self.sound_manager.load_background_music(CLASS_SELECTION_MUSIC_PATH):
            self.sound_manager.play_background_music()
    
    def update(self, dt):
        """Update selection state"""
        self.animation_time += dt
        self.preview_time += dt
        
        # Handle input cooldown
        if self.input_cooldown > 0:
            self.input_cooldown -= dt
        
        # Handle fade in
        if not self.transitioning and self.fade_alpha > 0:
            self.fade_alpha = max(0, self.fade_alpha - 300 * dt)
        
        # Handle input
        if self.input_cooldown <= 0 and not self.transitioning:
            keys = pygame.key.get_pressed()
            
            # Navigation
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.selected_index = (self.selected_index - 1) % len(self.classes)
                self.input_cooldown = 0.2
                self.sound_manager.play_sound('menu_move')
                
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.selected_index = (self.selected_index + 1) % len(self.classes)
                self.input_cooldown = 0.2
                self.sound_manager.play_sound('menu_move')
            
            # Selection
            elif keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                self.selected_class = self.classes[self.selected_index]
                self._start_transition()
                self.sound_manager.play_sound('menu_select')
            
            # Go back
            elif keys[pygame.K_ESCAPE]:
                self._start_transition("main_menu")
        
        # Handle transition
        if self.transitioning:
            self.fade_alpha = min(255, self.fade_alpha + 400 * dt)
            if self.fade_alpha >= 255:
                return self.transition_target
        
        return None
    
    def _start_transition(self, target=None):
        """Start transition animation"""
        self.transitioning = True
        if target:
            self.transition_target = target
        else:
            self.transition_target = "gameplay"
    
    def render(self, screen):
        """Render class selection interface"""
        screen.fill((20, 20, 40))  # Dark blue background
        
        # Render title
        title_surface = self.large_font.render("Choose Your Class", True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title_surface, title_rect)
        
        # Calculate positions for class previews
        class_width = 250
        total_width = class_width * len(self.classes)
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        # Render each class option
        for i, (class_name, class_obj) in enumerate(zip(self.classes, self.class_objects)):
            x = start_x + i * class_width + class_width // 2
            y = SCREEN_HEIGHT // 2
            
            # Highlight selected class
            is_selected = i == self.selected_index
            
            # Animated selection indicator
            if is_selected:
                pulse = 1.0 + 0.1 * math.sin(self.animation_time * 4)
                glow_radius = int(80 * pulse)
                
                # Create glow effect
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*class_obj.color, 30), 
                                 (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surf, (x - glow_radius, y - glow_radius))
                
                # Selection border
                pygame.draw.circle(screen, class_obj.color, (x, y), 85, 4)
            
            # Background circle for class preview
            bg_color = (60, 60, 80) if not is_selected else (80, 80, 100)
            pygame.draw.circle(screen, bg_color, (x, y), 80)
            pygame.draw.circle(screen, class_obj.secondary_color, (x, y), 80, 2)
            
            # Render class preview
            preview_surf = self.preview_surfaces[class_name]
            preview_rect = preview_surf.get_rect(center=(x, y))
            screen.blit(preview_surf, preview_rect)
            
            # Class name
            name_color = class_obj.color if is_selected else WHITE
            name_surface = self.medium_font.render(class_obj.name.title(), True, name_color)
            name_rect = name_surface.get_rect(center=(x, y + 120))
            screen.blit(name_surface, name_rect)
        
        # Render selected class details
        if 0 <= self.selected_index < len(self.class_objects):
            selected_class = self.class_objects[self.selected_index]
            
            # Description
            desc_y = SCREEN_HEIGHT - 200
            desc_surface = self.font.render(selected_class.description, True, WHITE)
            desc_rect = desc_surface.get_rect(center=(SCREEN_WIDTH // 2, desc_y))
            screen.blit(desc_surface, desc_rect)
            
            # Stats
            stats_y = desc_y + 40
            stats = [
                f"HP: {selected_class.base_hp}",
                f"Attack: {selected_class.base_attack_power}",
                f"Speed: {selected_class.base_speed}",
                f"Range: {selected_class.base_attack_range}"
            ]
            
            stats_text = " | ".join(stats)
            stats_surface = self.small_font.render(stats_text, True, (200, 200, 200))
            stats_rect = stats_surface.get_rect(center=(SCREEN_WIDTH // 2, stats_y))
            screen.blit(stats_surface, stats_rect)
            
            # Special ability
            special_y = stats_y + 30
            special_text = f"Special: {selected_class.special_ability_name}"
            special_surface = self.small_font.render(special_text, True, selected_class.color)
            special_rect = special_surface.get_rect(center=(SCREEN_WIDTH // 2, special_y))
            screen.blit(special_surface, special_rect)
        
        # Controls
        controls_y = SCREEN_HEIGHT - 60
        controls_surface = self.small_font.render(
            "A/D or ←/→: Navigate | ENTER/SPACE: Select | ESC: Back", 
            True, (150, 150, 150)
        )
        controls_rect = controls_surface.get_rect(center=(SCREEN_WIDTH // 2, controls_y))
        screen.blit(controls_surface, controls_rect)
        
        # Fade overlay
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surf.set_alpha(int(self.fade_alpha))
            fade_surf.fill(BLACK)
            screen.blit(fade_surf, (0, 0))
    
    def get_selected_class(self):
        """Get the currently selected class"""
        return self.selected_class
    
    def exit(self):
        """Clean up when leaving state"""
        pass
