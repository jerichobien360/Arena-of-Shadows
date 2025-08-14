from settings import *
from entities.character_classes import CHARACTER_CLASSES
import pygame
import math


class ClassSelectionState:
    """State for selecting character class before starting the game"""
    
    def __init__(self, font, sound_manager, player):
        self.font = font
        self.sound_manager = sound_manager
        self.large_font = pygame.font.Font(None, 48)
        self.medium_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 20)

        # Global Entities - For Stats Modification
        self.player = player
        
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
        if self.player.level != 1:
            self.player.restart_stats()

        for class_name, class_obj in zip(self.classes, self.class_objects):
            surface = pygame.Surface((120, 120), pygame.SRCALPHA)  # Reduced from 200x200
            
            # Draw class representation
            center = (60, 60)  # Adjusted center
            
            # Main character circle - smaller
            pygame.draw.circle(surface, class_obj.color, center, 20)  # Reduced from 30
            pygame.draw.circle(surface, class_obj.secondary_color, center, 20, 2)  # Thinner border
            
            # Class-specific visual elements - scaled down
            if class_name == 'warrior':
                # Draw sword - smaller
                sword_points = [
                    (center[0] - 3, center[1] - 28),
                    (center[0] + 3, center[1] - 28),
                    (center[0] + 2, center[1] + 15),
                    (center[0] - 2, center[1] + 15)
                ]
                pygame.draw.polygon(surface, (150, 150, 150), sword_points)
                # Sword hilt - smaller
                pygame.draw.rect(surface, (100, 50, 0), (center[0] - 5, center[1] + 15, 10, 4))
                
            elif class_name == 'mage':
                # Draw staff - smaller
                pygame.draw.line(surface, (100, 50, 0), 
                               (center[0] + 15, center[1] - 22), 
                               (center[0] + 15, center[1] + 22), 2)
                # Staff orb - smaller
                pygame.draw.circle(surface, (100, 100, 255), (center[0] + 15, center[1] - 25), 6)
                pygame.draw.circle(surface, (200, 200, 255), (center[0] + 15, center[1] - 25), 3)
                
            elif class_name == 'fireshooter':
                # Draw flame weapon - smaller
                flame_points = [
                    (center[0] + 18, center[1] - 8),
                    (center[0] + 26, center[1] - 12),
                    (center[0] + 30, center[1]),
                    (center[0] + 26, center[1] + 12),
                    (center[0] + 18, center[1] + 8)
                ]
                pygame.draw.polygon(surface, (255, 100, 0), flame_points)
                pygame.draw.polygon(surface, (255, 200, 0), flame_points[1:-1])
            
            self.preview_surfaces[class_name] = surface
    
    # -------------------INITIALIZE & CLEANUP-----------------------------
    def enter(self):
        """Initialize state when entering"""
        print("Entering the class selection successfully!")
        pygame.time.delay(150)
        self.selected_index = 0
        self.selected_class = None
        self.animation_time = 0
        self.fade_alpha = 255
        self.transitioning = False
        
        # Play selection music if available
        self.sound_manager.stop_background_music()
        if self.sound_manager.load_background_music(CLASS_SELECTION_MUSIC_PATH):
            self.sound_manager.play_background_music()
    
    def cleanup(self):
        """Clean up when leaving state"""
        pass

    # -------------------CLASS METHOD-------------------------------------
    def _start_transition(self, target=None):
        """Start transition animation"""
        self.transitioning = True
        if target:
            self.transition_target = target
        else:
            self.transition_target = "loading_screen_gameplay"
    
    def get_selected_class(self):
        """Get the currently selected class"""
        return self.selected_class
    
    def _apply_class_stats(self):
        """Apply the selected class stats to the player"""
        if self.selected_class and self.player:
            selected_class_obj = CHARACTER_CLASSES[self.selected_class]
            
            # Use the character class's apply_stats method
            selected_class_obj.apply_stats(self.player)
            
            print(f"Applied {self.selected_class} stats to player:")
            print(f"HP: {self.player.max_hp}, ATK: {self.player.attack_power}, SPD: {self.player.speed}")
    
    # -------------------GAME STATE HANDLE-----------------------------
    def render(self, screen):
        """Render class selection interface"""
        screen.fill((15, 15, 30))  # Darker background for cleaner look
        
        # Render title with better positioning
        title_surface = self.large_font.render("Choose Your Class", True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 60))  # Moved up
        screen.blit(title_surface, title_rect)
        
        # Calculate positions for class previews - more compact layout
        class_spacing = 180  # Reduced spacing
        total_width = class_spacing * (len(self.classes) - 1)
        start_x = (SCREEN_WIDTH - total_width) // 2
        class_y = 200  # Moved up for more space below
        
        # Render each class option
        for i, (class_name, class_obj) in enumerate(zip(self.classes, self.class_objects)):
            x = start_x + i * class_spacing
            y = class_y
            
            # Highlight selected class
            is_selected = i == self.selected_index
            
            # Animated selection indicator - smaller
            if is_selected:
                pulse = 1.0 + 0.08 * math.sin(self.animation_time * 4)  # Reduced pulse
                glow_radius = int(50 * pulse)  # Smaller glow
                
                # Create glow effect
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*class_obj.color, 25), 
                                 (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surf, (x - glow_radius, y - glow_radius))
                
                # Selection border - smaller
                pygame.draw.circle(screen, class_obj.color, (x, y), 55, 3)
            
            # Background circle for class preview - smaller
            bg_color = (40, 40, 60) if not is_selected else (55, 55, 75)
            pygame.draw.circle(screen, bg_color, (x, y), 50)  # Reduced from 80
            pygame.draw.circle(screen, class_obj.secondary_color, (x, y), 50, 2)
            
            # Render class preview
            preview_surf = self.preview_surfaces[class_name]
            preview_rect = preview_surf.get_rect(center=(x, y))
            screen.blit(preview_surf, preview_rect)
            
            # Class name - positioned closer
            name_color = class_obj.color if is_selected else WHITE
            name_surface = self.medium_font.render(class_obj.name.title(), True, name_color)
            name_rect = name_surface.get_rect(center=(x, y + 75))  # Closer to circle
            screen.blit(name_surface, name_rect)
        
        # Create info panel for selected class - more organized
        if 0 <= self.selected_index < len(self.class_objects):
            selected_class = self.class_objects[self.selected_index]
            
            # Info panel background
            panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 300, class_y + 150, 600, 120)
            panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(panel_surface, (30, 30, 50, 200), (0, 0, panel_rect.width, panel_rect.height))
            pygame.draw.rect(panel_surface, selected_class.color, (0, 0, panel_rect.width, panel_rect.height), 2)
            screen.blit(panel_surface, panel_rect)
            
            # Description - centered in panel
            desc_surface = self.font.render(selected_class.description, True, WHITE)
            desc_rect = desc_surface.get_rect(center=(panel_rect.centerx, panel_rect.y + 25))
            screen.blit(desc_surface, desc_rect)
            
            # Stats in a cleaner grid layout
            stats_y = panel_rect.y + 50
            stats = [
                f"HP: {selected_class.base_hp}",
                f"ATK: {selected_class.base_attack_power}",
                f"SPD: {selected_class.base_speed}",
                f"RNG: {selected_class.base_attack_range}"
            ]
            
            # Render stats in two rows
            stats_per_row = 2
            for i, stat in enumerate(stats):
                row = i // stats_per_row
                col = i % stats_per_row
                
                stat_x = panel_rect.centerx - 100 + col * 200
                stat_y = stats_y + row * 25
                
                stat_surface = self.small_font.render(stat, True, (220, 220, 220))
                stat_rect = stat_surface.get_rect(center=(stat_x, stat_y))
                screen.blit(stat_surface, stat_rect)
            
            # Special ability - at bottom of panel
            special_y = panel_rect.y + 100
            special_text = f"Special: {selected_class.special_ability_name}"
            special_surface = self.small_font.render(special_text, True, selected_class.color)
            special_rect = special_surface.get_rect(center=(panel_rect.centerx, special_y))
            screen.blit(special_surface, special_rect)
        
        # Controls - moved to bottom with cleaner styling
        controls_y = SCREEN_HEIGHT - 40
        controls_surface = self.small_font.render(
            "A/D or ←/→: Navigate | ENTER/SPACE: Select | ESC: Back", 
            True, (120, 120, 120)
        )
        controls_rect = controls_surface.get_rect(center=(SCREEN_WIDTH // 2, controls_y))
        
        # Add background to controls for better readability
        controls_bg = pygame.Rect(controls_rect.x - 10, controls_rect.y - 5, 
                                 controls_rect.width + 20, controls_rect.height + 10)
        pygame.draw.rect(screen, (20, 20, 40, 150), controls_bg)
        screen.blit(controls_surface, controls_rect)
        
        # Fade overlay
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surf.set_alpha(int(self.fade_alpha))
            fade_surf.fill(BLACK)
            screen.blit(fade_surf, (0, 0))
    
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
                self._apply_class_stats()
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
