import pygame
import math


class MiniMap:
    """A minimap that displays the game world, player, enemies, and camera viewport."""
    
    def __init__(self, world_width, world_height, background_system=None, 
                 width=180, height=120, margin=16):
        # World dimensions (actual world spans 3x the provided dimensions)
        self.world_width = world_width
        self.world_height = world_height
        self.actual_world_width = world_width * 3
        self.actual_world_height = world_height * 3
        
        # Minimap display properties
        self.width = width
        self.height = height
        self.margin = margin
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Terrain rendering
        self.background_system = background_system
        self.terrain_cache = None
        self.cache_dirty = True
        
        # State
        self._visible = True
        
        # Coordinate conversion factors
        self.scale_x = width / (world_width * 2)
        self.scale_y = height / (world_height * 2)
        self.world_offset_x = world_width
        self.world_offset_y = world_height
        
        # Generate initial terrain cache
        if self.background_system:
            self._generate_terrain_cache()
    
    def _generate_terrain_cache(self):
        """Create a cached surface of the terrain for efficient rendering."""
        if not self.background_system:
            return
        
        # Create terrain surface with dark background
        self.terrain_cache = pygame.Surface((self.width, self.height))
        self.terrain_cache.fill((5, 5, 15))
        
        # Find and render ground layer
        ground_layer = next((layer for layer in self.background_system.layers 
                           if layer['type'] == 'ground'), None)
        
        if ground_layer:
            self._render_ground_tiles(ground_layer['elements'])
        
        # Render other terrain features
        self._render_terrain_features()
        self.cache_dirty = False
    
    def _render_ground_tiles(self, tiles):
        """Render ground tiles to the terrain cache."""
        for tile in tiles:
            minimap_x, minimap_y = self.world_to_minimap(tile['x'], tile['y'])
            minimap_size = max(1, int(tile['size'] * self.scale_x))
            
            if self._is_in_bounds(minimap_x, minimap_y):
                # Brighten colors for visibility
                color = tuple(min(255, max(20, int(c * 2.0))) for c in tile['color'])
                rect = pygame.Rect(minimap_x, minimap_y, minimap_size, minimap_size)
                pygame.draw.rect(self.terrain_cache, color, rect)
    
    def _render_terrain_features(self):
        """Render mountains, crystals, and other terrain features."""
        for layer in self.background_system.layers:
            if layer['type'] == 'distant_mountains':
                self._render_mountains(layer['elements'])
            elif layer['type'] == 'details':
                self._render_details(layer['elements'])
    
    def _render_mountains(self, mountains):
        """Render mountain features as small circles."""
        for mountain in mountains:
            minimap_x, minimap_y = self.world_to_minimap(mountain['x'], mountain['y'])
            if self._is_in_bounds(minimap_x, minimap_y):
                color = tuple(min(255, max(20, int(c * 2))) for c in mountain['color'])
                radius = max(1, int(2 * self.scale_x))
                pygame.draw.circle(self.terrain_cache, color, 
                                 (minimap_x, minimap_y), radius)
    
    def _render_details(self, details):
        """Render detail elements like crystals and rocks."""
        for detail in details:
            minimap_x, minimap_y = self.world_to_minimap(detail['x'], detail['y'])
            if not self._is_in_bounds(minimap_x, minimap_y):
                continue
                
            color = tuple(min(255, max(20, int(c * 1.2))) for c in detail['color'])
            
            if detail['type'] == 'crystal':
                pygame.draw.circle(self.terrain_cache, color, (minimap_x, minimap_y), 1)
            elif detail['type'] == 'rock' and hash((detail['x'], detail['y'])) % 10 == 0:
                # Show only 10% of rocks to avoid clutter
                pygame.draw.circle(self.terrain_cache, color, (minimap_x, minimap_y), 1)
    
    def _is_in_bounds(self, x, y):
        """Check if coordinates are within minimap bounds."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def world_to_minimap(self, world_x, world_y):
        """Convert world coordinates to minimap pixel coordinates."""
        minimap_x = int((world_x + self.world_offset_x) * self.scale_x)
        minimap_y = int((world_y + self.world_offset_y) * self.scale_y)
        return minimap_x, minimap_y
    
    def minimap_to_world(self, minimap_x, minimap_y):
        """Convert minimap pixel coordinates to world coordinates."""
        world_x = (minimap_x / self.scale_x) - self.world_offset_x
        world_y = (minimap_y / self.scale_y) - self.world_offset_y
        return world_x, world_y
    
    def draw(self, screen, player, enemies, camera=None):
        """Render the minimap to the screen."""
        # Refresh terrain if needed
        if self.cache_dirty and self.background_system:
            self._generate_terrain_cache()
        
        # Prepare minimap surface
        self.surface.fill((0, 0, 0, 180))  # Semi-transparent background
        
        # Draw terrain
        if self.terrain_cache:
            self.surface.blit(self.terrain_cache, (0, 0))
        
        # Draw UI elements
        self._draw_grid_and_border()
        
        # Draw game elements
        if camera:
            self._draw_camera_viewport(camera)
        self._draw_enemies(enemies)
        self._draw_player(player)
        self._draw_title()
        
        # Blit to screen if visible
        if self._visible:
            pos = (screen.get_width() - self.width - self.margin, self.margin)
            screen.blit(self.surface, pos)
    
    def _draw_grid_and_border(self):
        """Draw grid lines and border for orientation."""
        # Border
        pygame.draw.rect(self.surface, (100, 100, 100), 
                        (0, 0, self.width, self.height), 2)
        
        # Grid lines
        grid_spacing = max(20, min(40, self.width // 8))
        for i in range(grid_spacing, self.width, grid_spacing):
            pygame.draw.line(self.surface, (20, 20, 25), (i, 0), (i, self.height))
        for i in range(grid_spacing, self.height, grid_spacing):
            pygame.draw.line(self.surface, (20, 20, 25), (0, i), (self.width, i))
    
    def _draw_camera_viewport(self, camera):
        """Draw the camera's current viewport area."""
        # Calculate viewport bounds in world space
        cam_left = camera.x
        cam_top = camera.y
        cam_right = camera.x + (camera.screen_width / camera.zoom)
        cam_bottom = camera.y + (camera.screen_height / camera.zoom)
        
        # Convert to minimap coordinates
        cam_x1, cam_y1 = self.world_to_minimap(cam_left, cam_top)
        cam_x2, cam_y2 = self.world_to_minimap(cam_right, cam_bottom)
        
        cam_w = max(1, cam_x2 - cam_x1)
        cam_h = max(1, cam_y2 - cam_y1)
        
        # Draw viewport area and border
        viewport_surf = pygame.Surface((cam_w, cam_h), pygame.SRCALPHA)
        viewport_surf.fill((0, 120, 255, 50))
        self.surface.blit(viewport_surf, (cam_x1, cam_y1))
        pygame.draw.rect(self.surface, (0, 150, 255), (cam_x1, cam_y1, cam_w, cam_h), 2)
    
    def _draw_enemies(self, enemies):
        """Draw enemy positions and directions."""
        for enemy in enemies:
            ex, ey = self.world_to_minimap(enemy.x, enemy.y)
            if not (0 <= ex <= self.width and 0 <= ey <= self.height):
                continue
                
            # Enemy dot with outline
            pygame.draw.circle(self.surface, (100, 0, 0), (ex, ey), 4)
            pygame.draw.circle(self.surface, (255, 0, 0), (ex, ey), 3)
            
            # Direction indicator
            if hasattr(enemy, 'direction'):
                end_x = ex + math.cos(enemy.direction) * 8
                end_y = ey + math.sin(enemy.direction) * 8
                pygame.draw.line(self.surface, (255, 100, 100), 
                               (ex, ey), (int(end_x), int(end_y)), 2)
    
    def _draw_player(self, player):
        """Draw player position and direction."""
        px, py = self.world_to_minimap(player.x, player.y)
        if not (0 <= px <= self.width and 0 <= py <= self.height):
            return
            
        # Player dot with layered circles
        pygame.draw.circle(self.surface, (0, 100, 0), (px, py), 6)
        pygame.draw.circle(self.surface, (0, 255, 0), (px, py), 5)
        pygame.draw.circle(self.surface, (100, 255, 100), (px, py), 3)
        
        # Direction indicator
        direction = getattr(player, 'direction', getattr(player, 'angle', 0))
        end_x = px + math.cos(direction) * 10
        end_y = py + math.sin(direction) * 10
        pygame.draw.line(self.surface, (150, 255, 150), 
                        (px, py), (int(end_x), int(end_y)), 2)
    
    def _draw_title(self):
        """Draw minimap title."""
        try:
            font = pygame.font.Font(None, 20)
            title_text = font.render("MAP", True, (200, 200, 200))
            self.surface.blit(title_text, (5, 5))
        except:
            pass  # Font not available
    
    def handle_click(self, screen_pos, camera=None):
        """Handle mouse clicks for minimap navigation."""
        if not self._visible:
            return False
            
        # Get minimap rectangle
        screen_width = pygame.display.get_surface().get_width()
        minimap_rect = pygame.Rect(
            screen_width - self.width - self.margin,
            self.margin,
            self.width,
            self.height
        )
        
        # Check if click is within minimap
        if minimap_rect.collidepoint(screen_pos):
            # Convert click to world coordinates and move camera
            local_x = screen_pos[0] - minimap_rect.x
            local_y = screen_pos[1] - minimap_rect.y
            world_x, world_y = self.minimap_to_world(local_x, local_y)
            
            if camera:
                camera.x = world_x
                camera.y = world_y
            
            return True
        
        return False
    
    @property
    def visible(self):
        """Get minimap visibility state."""
        return self._visible
    
    @visible.setter
    def visible(self, value):
        """Set minimap visibility state."""
        self._visible = value
    
    def refresh_terrain(self):
        """Mark terrain cache for regeneration."""
        self.cache_dirty = True
