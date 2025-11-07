from settings import *
from game_function.game_function import *
from src.entities.character_classes import CHARACTER_CLASSES
from src.ui.effects.particles import ParticleSystem 

import pygame
import math


class ClassSelectionState:
    """State for selecting character class before to start the game"""
    
    def __init__(self, font: pygame.font, sound_manager, player):
        # Existing Components
        self.font = font
        self.sound_manager = sound_manager

        # Create a Custom Font
        self.large_font = FONT(CUSTOM_FONT_UI, 24)
        self.medium_font = FONT(CUSTOM_FONT_UI, 20)
        self.small_font = FONT(CUSTOM_FONT_UI, 16)

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
        
        # Particle system for magical atmosphere
        self.particle_system = ParticleSystem()
        
        # Selection-specific particle effects
        self.selection_particles = []
        self.class_aura_particles = {}  # Store particles for each class
        
        # Create class preview surfaces
        self.preview_surfaces = {}
        self._create_preview_surfaces()
        
    def _create_preview_surfaces(self):
        """Create preview surfaces for each character class"""
        if self.player.level != 1:
            self.player.restart_stats()

        for class_name, class_obj in zip(self.classes, self.class_objects):
            surface = pygame.Surface((140, 140), pygame.SRCALPHA)  # Increased size for glow
            
            # Draw class representation
            center = (70, 70)  # Adjusted center for larger surface
            
            # Create glowing effect for character
            self._add_character_glow(surface, center, class_obj, class_name)
            
            # Main character circle with enhanced glow
            pygame.draw.circle(surface, class_obj.color, center, 22)
            pygame.draw.circle(surface, class_obj.secondary_color, center, 22, 3)
            
            # Inner glow
            glow_surf = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*class_obj.color, 80), (25, 25), 25)
            surface.blit(glow_surf, (center[0] - 25, center[1] - 25))
            
            # Class-specific visual elements - scaled down
            if class_name == 'warrior':
                # Draw sword with metallic glow
                sword_points = [
                    (center[0] - 3, center[1] - 30),
                    (center[0] + 3, center[1] - 30),
                    (center[0] + 2, center[1] + 15),
                    (center[0] - 2, center[1] + 15)
                ]
                # Sword glow
                glow_points = [(p[0], p[1]) for p in sword_points]
                for i in range(3):
                    expanded_points = [(p[0] + (1 if p[0] > center[0] else -1) * i, 
                                      p[1] + (1 if p[1] > center[1] else -1) * i) for p in glow_points]
                    pygame.draw.polygon(surface, (200, 200, 255, 30 - i * 10), expanded_points)
                
                pygame.draw.polygon(surface, (180, 180, 200), sword_points)
                # Sword hilt
                pygame.draw.rect(surface, (120, 70, 20), (center[0] - 6, center[1] + 15, 12, 5))
                
            elif class_name == 'mage':
                # Draw staff with magical glow
                pygame.draw.line(surface, (120, 70, 20), 
                               (center[0] + 15, center[1] - 25), 
                               (center[0] + 15, center[1] + 25), 3)
                
                # Staff orb with magical aura
                orb_center = (center[0] + 15, center[1] - 27)
                # Magical aura layers
                for radius in [12, 9, 6]:
                    alpha = 150 - (radius * 10)
                    orb_glow = pygame.Surface((radius * 3, radius * 3), pygame.SRCALPHA)
                    pygame.draw.circle(orb_glow, (150, 150, 255, alpha), 
                                     (radius * 3 // 2, radius * 3 // 2), radius)
                    surface.blit(orb_glow, (orb_center[0] - radius * 3 // 2, 
                                          orb_center[1] - radius * 3 // 2))
                
                pygame.draw.circle(surface, (120, 120, 255), orb_center, 7)
                pygame.draw.circle(surface, (220, 220, 255), orb_center, 4)
                
            elif class_name == 'fireshooter':
                # Draw flame weapon with fire glow
                flame_points = [
                    (center[0] + 20, center[1] - 10),
                    (center[0] + 28, center[1] - 14),
                    (center[0] + 32, center[1]),
                    (center[0] + 28, center[1] + 14),
                    (center[0] + 20, center[1] + 10)
                ]
                
                # Fire glow effect
                for i in range(4):
                    glow_points = [(p[0] + i, p[1]) for p in flame_points]
                    alpha = 100 - i * 20
                    flame_glow = pygame.Surface((50, 50), pygame.SRCALPHA)
                    pygame.draw.polygon(flame_glow, (255, 100 + i * 30, 0, alpha), 
                                      [(p[0] - center[0] + 25, p[1] - center[1] + 25) for p in glow_points])
                    surface.blit(flame_glow, (center[0] - 25, center[1] - 25))
                
                pygame.draw.polygon(surface, (255, 120, 0), flame_points)
                pygame.draw.polygon(surface, (255, 220, 50), flame_points[1:-1])
            
            self.preview_surfaces[class_name] = surface

    def _add_character_glow(self, surface: pygame.Surface, center: int, class_obj, class_name):
        """Add unique character glow based on class"""
        if class_name == 'warrior':
            # Metallic silver glow
            for radius in [35, 30, 25]:
                alpha = 40 - (35 - radius) * 2
                pygame.draw.circle(surface, (*class_obj.color, alpha), center, radius)
        elif class_name == 'mage':
            # Mystical purple-blue glow
            for radius in [38, 32, 26]:
                alpha = 50 - (38 - radius) * 3
                pygame.draw.circle(surface, (150, 100, 255, alpha), center, radius)
        elif class_name == 'fireshooter':
            # Fiery orange-red glow
            for radius in [36, 31, 26]:
                alpha = 45 - (36 - radius) * 2
                pygame.draw.circle(surface, (255, 100, 50, alpha), center, radius)

    def _create_selection_particles(self, x, y, class_obj):
        """Create magical particles around selected class"""
        import random
        from src.ui.effects.particles import Firefly
        
        # Clear existing selection particles
        self.selection_particles.clear()
        
        # Create fireflies with class-specific colors around the selected class
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(60, 100)
            particle_x = x + math.cos(angle) * distance
            particle_y = y + math.sin(angle) * distance
            
            # Create firefly and customize its color to match class
            firefly = Firefly(particle_x, particle_y)
            
            # Override base color with class colors
            if hasattr(class_obj, 'color') and class_obj.color:
                firefly.base_color = class_obj.color
            
            # Make them orbit around the selection
            firefly.orbit_center = (x, y)
            firefly.orbit_radius = distance
            firefly.orbit_angle = angle
            firefly.orbit_speed = random.uniform(0.5, 1.0)
            
            self.selection_particles.append(firefly)

    def _update_selection_particles(self, dt, selected_x, selected_y):
        """Update particles orbiting around selected class"""
        for particle in self.selection_particles:
            if hasattr(particle, 'orbit_center'):
                # Update orbital motion
                particle.orbit_angle += particle.orbit_speed * dt
                particle.x = selected_x + math.cos(particle.orbit_angle) * particle.orbit_radius
                particle.y = selected_y + math.sin(particle.orbit_angle) * particle.orbit_radius
                
                # Update particle-specific systems
                if hasattr(particle, '_update_glow'):
                    particle._update_glow(dt)
                if hasattr(particle, '_update_trail'):
                    particle._update_trail()
                if hasattr(particle, 'update'):
                    particle.update(dt)

    def _create_class_aura_effects(self):
        """Create subtle aura effects for each class position"""
        class_spacing = 180
        total_width = class_spacing * (len(self.classes) - 1)
        start_x = (SCREEN_WIDTH - total_width) // 2
        class_y = 200
        
        for i, (class_name, class_obj) in enumerate(zip(self.classes, self.class_objects)):
            x = start_x + i * class_spacing
            y = class_y
            
            if class_name not in self.class_aura_particles:
                self.class_aura_particles[class_name] = []
            
            # Create subtle ambient particles for each class
            if len(self.class_aura_particles[class_name]) < 3:
                from src.ui.effects.particles import Firefly
                import random
                
                for _ in range(3 - len(self.class_aura_particles[class_name])):
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.uniform(80, 120)
                    particle_x = x + math.cos(angle) * distance
                    particle_y = y + math.sin(angle) * distance
                    
                    firefly = Firefly(particle_x, particle_y)
                    firefly.base_color = class_obj.secondary_color
                    firefly.brightness *= 0.3  # Make them more subtle
                    firefly.size *= 0.7
                    
                    self.class_aura_particles[class_name].append(firefly)
    
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
        
        # Initialize particle effects
        self.particle_system = ParticleSystem()
        self._create_class_aura_effects()
        
        # Create initial selection particles
        class_spacing = 180
        total_width = class_spacing * (len(self.classes) - 1)
        start_x = (SCREEN_WIDTH - total_width) // 2
        class_y = 200
        selected_x = start_x + self.selected_index * class_spacing
        self._create_selection_particles(selected_x, class_y, self.class_objects[self.selected_index])
        
        # Play selection music if available
        self.sound_manager.stop_background_music()
        if self.sound_manager.load_background_music(CLASS_SELECTION_MUSIC_PATH):
            self.sound_manager.play_background_music()
    
    def cleanup(self):
        """Clean up when leaving state"""
        # Clear all particle effects
        self.selection_particles.clear()
        self.class_aura_particles.clear()
        if hasattr(self, 'particle_system'):
            self.particle_system.clear()

    # -------------------CLASS METHOD-------------------------------------
    def _start_transition(self, target: str | None = None):
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
    
    # -------------------GAME STATE HANDLE--------------------------------
    def render(self, screen: pygame.display.set_mode):
        """Enhanced render method with hover effects"""
        screen.fill((15, 15, 30))  # Darker background for cleaner look
        
        # Render background particle effects first (behind everything)
        self.particle_system.update(0.016)  # Approximate dt for smooth animation
        particles = self.particle_system.get_particles()
        
        # Render leaves behind everything
        for leaf in particles.get('leaves', []):
            leaf.render(screen)
        
        # Render fireflies behind UI but above leaves
        for firefly in particles.get('fireflies', []):
            firefly.render(screen)
        
        # Render class aura effects
        for class_particles in self.class_aura_particles.values():
            for particle in class_particles:
                particle.render(screen)
        
        # Render title with better positioning
        title_surface = self.large_font.render("Choose Your Class", True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 60))
        screen.blit(title_surface, title_rect)
        
        # Calculate positions for class previews - more compact layout
        class_spacing = 180
        total_width = class_spacing * (len(self.classes) - 1)
        start_x = (SCREEN_WIDTH - total_width) // 2
        class_y = 200
        
        # Render each class option
        for i, (class_name, class_obj) in enumerate(zip(self.classes, self.class_objects)):
            x = start_x + i * class_spacing
            y = class_y
            
            # Check selection and hover states
            is_selected = i == self.selected_index
            is_hovered = hasattr(self, 'hovered_index') and self.hovered_index == i
            
            # Animated selection indicator - smaller
            if is_selected:
                pulse = 1.0 + 0.08 * math.sin(self.animation_time * 4)
                glow_radius = int(50 * pulse)
                
                # Create glow effect
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*class_obj.color, 25), 
                                 (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surf, (x - glow_radius, y - glow_radius))
                
                # Selection border - smaller
                pygame.draw.circle(screen, class_obj.color, (x, y), 55, 3)
            
            # Hover effect for non-selected classes
            elif is_hovered:
                hover_pulse = 1.0 + 0.04 * math.sin(self.animation_time * 6)
                hover_radius = int(45 * hover_pulse)
                
                # Create subtle hover glow
                hover_surf = pygame.Surface((hover_radius * 2, hover_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(hover_surf, (*class_obj.secondary_color, 15), 
                                 (hover_radius, hover_radius), hover_radius)
                screen.blit(hover_surf, (x - hover_radius, y - hover_radius))
                
                # Hover border
                pygame.draw.circle(screen, class_obj.secondary_color, (x, y), 52, 2)
            
            # Background circle for class preview with different states
            if is_selected:
                bg_color = (55, 55, 75)
            elif is_hovered:
                bg_color = (45, 45, 65)  # Slightly lighter when hovered
            else:
                bg_color = (40, 40, 60)
            
            pygame.draw.circle(screen, bg_color, (x, y), 50)
            pygame.draw.circle(screen, class_obj.secondary_color, (x, y), 50, 2)
            
            # Render class preview
            preview_surf = self.preview_surfaces[class_name]
            preview_rect = preview_surf.get_rect(center=(x, y))
            screen.blit(preview_surf, preview_rect)
            
            # Class name with hover effect
            if is_selected:
                name_color = class_obj.color
            elif is_hovered:
                name_color = class_obj.secondary_color
            else:
                name_color = WHITE
            
            name_surface = self.medium_font.render(class_obj.name.title(), True, name_color)
            name_rect = name_surface.get_rect(center=(x, y + 75))
            screen.blit(name_surface, name_rect)
        
        # Render selection particles (orbiting around selected class)
        for particle in self.selection_particles:
            particle.render(screen)
        
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
        
        # Controls - updated to include mouse controls
        controls_y = SCREEN_HEIGHT - 40
        controls_surface = self.small_font.render(
            "A/D or LEFT/RIGHT: Navigate | ENTER/SPACE/CLICK: Select | ESC: Back", 
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
    
    def update(self, dt: float):
        """Update selection state (without keyboard polling - handled by events)"""
        self.animation_time += dt
        self.preview_time += dt
        
        # Update particle systems
        self.particle_system.update(dt)
        
        # Update class aura particles
        for class_particles in self.class_aura_particles.values():
            for particle in class_particles:
                particle.update(dt)
        
        # Update selection particles to orbit around selected class
        if self.selection_particles:
            class_spacing = 180
            total_width = class_spacing * (len(self.classes) - 1)
            start_x = (SCREEN_WIDTH - total_width) // 2
            class_y = 200
            selected_x = start_x + self.selected_index * class_spacing
            self._update_selection_particles(dt, selected_x, class_y)
        
        # Handle input cooldown
        if self.input_cooldown > 0:
            self.input_cooldown -= dt
        
        # Handle fade in
        if not self.transitioning and self.fade_alpha > 0:
            self.fade_alpha = max(0, self.fade_alpha - 300 * dt)
        
        # Handle mouse interactions
        self.mouse_handler()
        
        # Handle transition
        if self.transitioning:
            self.fade_alpha = min(255, self.fade_alpha + 400 * dt)
            if self.fade_alpha >= 255:
                return self.transition_target
        
        return None

    # ------------------------MOUSE HANDLE--------------------------------
    def handle_event(self, event):
        """Handle pygame events including mouse interactions"""
        if self.input_cooldown > 0 or self.transitioning:
            return None
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = event.pos
                
                # Check if click is on a class selection area
                class_spacing = 180
                total_width = class_spacing * (len(self.classes) - 1)
                start_x = (SCREEN_WIDTH - total_width) // 2
                class_y = 200
                
                for i in range(len(self.classes)):
                    class_x = start_x + i * class_spacing
                    
                    # Check if mouse is within the class circle (radius 55 for selection area)
                    distance = math.sqrt((mouse_x - class_x) ** 2 + (mouse_y - class_y) ** 2)
                    
                    if distance <= 55:  # Click area radius
                        if i == self.selected_index:
                            # Already selected - confirm selection
                            self.selected_class = self.classes[self.selected_index]
                            self._apply_class_stats()
                            self._start_transition()
                            self.sound_manager.play_sound('menu_select')
                            return self.transition_target
                        else:
                            # Change selection
                            old_index = self.selected_index
                            self.selected_index = i
                            if old_index != self.selected_index:
                                # Recreate selection particles for new class
                                selected_x = start_x + self.selected_index * class_spacing
                                self._create_selection_particles(selected_x, class_y, self.class_objects[self.selected_index])
                            self.input_cooldown = 0.2
                            self.sound_manager.play_sound('menu_move')
                        break
        
        elif event.type == pygame.KEYDOWN:
            # Navigation
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                old_index = self.selected_index
                self.selected_index = (self.selected_index - 1) % len(self.classes)
                if old_index != self.selected_index:
                    # Recreate selection particles for new class
                    class_spacing = 180
                    total_width = class_spacing * (len(self.classes) - 1)
                    start_x = (SCREEN_WIDTH - total_width) // 2
                    class_y = 200
                    selected_x = start_x + self.selected_index * class_spacing
                    self._create_selection_particles(selected_x, class_y, self.class_objects[self.selected_index])
                self.input_cooldown = 0.2
                self.sound_manager.play_sound('menu_move')
                
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                old_index = self.selected_index
                self.selected_index = (self.selected_index + 1) % len(self.classes)
                if old_index != self.selected_index:
                    # Recreate selection particles for new class
                    class_spacing = 180
                    total_width = class_spacing * (len(self.classes) - 1)
                    start_x = (SCREEN_WIDTH - total_width) // 2
                    class_y = 200
                    selected_x = start_x + self.selected_index * class_spacing
                    self._create_selection_particles(selected_x, class_y, self.class_objects[self.selected_index])
                self.input_cooldown = 0.2
                self.sound_manager.play_sound('menu_move')
            
            # Selection
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                self.selected_class = self.classes[self.selected_index]
                self._apply_class_stats()
                self._start_transition()
                self.sound_manager.play_sound('menu_select')
            
            # Go back
            elif event.key == pygame.K_ESCAPE:
                self._start_transition("main_menu")
        
        return None

    def mouse_handler(self):
        """Handle continuous mouse interactions (called every frame)"""
        if self.transitioning:
            return
        
        # Get current mouse position
        mouse_pos = pygame.mouse.get_pos()
        self.mouse_hover(mouse_pos)

    def mouse_hover(self, mouse_pos=None):
        """Handle mouse hover effects"""
        if self.transitioning or self.input_cooldown > 0:
            return
        
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()
            
        mouse_x, mouse_y = mouse_pos
        
        # Check if mouse is hovering over any class
        class_spacing = 180
        total_width = class_spacing * (len(self.classes) - 1)
        start_x = (SCREEN_WIDTH - total_width) // 2
        class_y = 200
        
        hovered_index = None
        for i in range(len(self.classes)):
            class_x = start_x + i * class_spacing
            distance = math.sqrt((mouse_x - class_x) ** 2 + (mouse_y - class_y) ** 2)
            
            if distance <= 55:  # Hover detection radius
                hovered_index = i
                break
        
        # Store hovered index for rendering
        self.hovered_index = hovered_index
