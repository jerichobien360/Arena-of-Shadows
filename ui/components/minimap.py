import pygame
import math
import random
 
class MiniMap:
    def __init__(self, world_width, world_height, background_system=None, width=180, height=120, margin=16):
        # World Coordinates
        self.world_width = world_width
        self.world_height = world_height
        
        # Minimap Size
        self.width = width
        self.height = height
        self.margin = margin
        
        # Minimap Base Layout
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Background system integration
        self.background_system = background_system
        self.terrain_cache = None
        self.cache_dirty = True
        
        # Minimap Properties
        self._visible = True
        self._draggable = False
        
        # Scale factors for world-to-minimap conversion
        self.scale_x = self.width / (self.world_width * 2)
        self.scale_y = self.height / (self.world_height * 2)
        
        # Generate terrain cache if background system is provided
        if self.background_system:
            self._generate_terrain_cache()
    
    def _generate_terrain_cache(self):
        """Generate a cached minimap representation of the terrain"""
        if not self.background_system:
            print("DEBUG: No background system!")
            return
            
        print(f"DEBUG: World dimensions: {self.world_width} x {self.world_height}")
        print(f"DEBUG: Minimap dimensions: {self.width} x {self.height}")
        print(f"DEBUG: Scale factors: {self.scale_x}, {self.scale_y}")
        
        # Create a surface for the terrain
        self.terrain_cache = pygame.Surface((self.width, self.height))
        self.terrain_cache.fill((5, 5, 15))  # Very dark background
        
        # Debug: Check how many layers we have
        print(f"DEBUG: Background system has {len(self.background_system.layers)} layers")
        
        # Get ground tiles from background system - USE THE ACTUAL DATA!
        ground_layer = None
        for i, layer in enumerate(self.background_system.layers):
            print(f"DEBUG: Layer {i}: type='{layer['type']}', elements={len(layer['elements'])}")
            if layer['type'] == 'ground':
                ground_layer = layer
                break
        
        if ground_layer:
            print(f"DEBUG: Found ground layer with {len(ground_layer['elements'])} tiles")
            tiles_drawn = 0
            
            # Sample a few tiles to debug
            for i, tile in enumerate(ground_layer['elements'][:10]):  # Check first 10 tiles
                print(f"DEBUG: Tile {i}: x={tile['x']}, y={tile['y']}, size={tile['size']}, color={tile['color']}, type={tile.get('type', 'unknown')}")
                
                # Convert world coordinates to minimap coordinates
                minimap_x = int((tile['x'] + self.world_width) * self.scale_x)
                minimap_y = int((tile['y'] + self.world_height) * self.scale_y)
                minimap_size = max(1, int(tile['size'] * self.scale_x))
                
                print(f"DEBUG: Converted to minimap: x={minimap_x}, y={minimap_y}, size={minimap_size}")
                
                # Only process tiles that fit within minimap bounds
                if 0 <= minimap_x < self.width and 0 <= minimap_y < self.height:
                    tiles_drawn += 1
                    # Use the ACTUAL color from the background system, just make it more visible
                    original_color = tile['color']
                    # Brighten the existing colors for minimap visibility
                    minimap_color = tuple(min(255, max(20, int(c * 2.0))) for c in original_color)
                    
                    print(f"DEBUG: Drawing tile with color {minimap_color}")
                    
                    # Draw tile using the actual size and color data
                    rect = pygame.Rect(minimap_x, minimap_y, minimap_size, minimap_size)
                    pygame.draw.rect(self.terrain_cache, minimap_color, rect)
            
            # Now process all tiles (without debug prints)
            for tile in ground_layer['elements']:
                minimap_x = int((tile['x'] + self.world_width) * self.scale_x)
                minimap_y = int((tile['y'] + self.world_height) * self.scale_y)
                minimap_size = max(1, int(tile['size'] * self.scale_x))
                
                if 0 <= minimap_x < self.width and 0 <= minimap_y < self.height:
                    original_color = tile['color']
                    minimap_color = tuple(min(255, max(20, int(c * 2.0))) for c in original_color)
                    rect = pygame.Rect(minimap_x, minimap_y, minimap_size, minimap_size)
                    pygame.draw.rect(self.terrain_cache, minimap_color, rect)
            
            print(f"DEBUG: Drew {tiles_drawn} tiles on minimap")
        else:
            print("DEBUG: No ground layer found!")
        
        # Use the ACTUAL detail features from background system
        for layer in self.background_system.layers:
            if layer['type'] == 'distant_mountains':
                for mountain in layer['elements']:
                    minimap_x = int((mountain['x'] + self.world_width) * self.scale_x)
                    minimap_y = int((mountain['y'] + self.world_height) * self.scale_y)
                    if 0 <= minimap_x < self.width and 0 <= minimap_y < self.height:
                        # Use the actual mountain color, just brighten it
                        mountain_color = tuple(min(255, max(20, int(c * 2))) for c in mountain['color'])
                        pygame.draw.circle(self.terrain_cache, mountain_color, 
                                         (minimap_x, minimap_y), max(1, int(2 * self.scale_x)))
            
            elif layer['type'] == 'details':
                for detail in layer['elements']:
                    minimap_x = int((detail['x'] + self.world_width) * self.scale_x)
                    minimap_y = int((detail['y'] + self.world_height) * self.scale_y)
                    if 0 <= minimap_x < self.width and 0 <= minimap_y < self.height:
                        # Use the ACTUAL colors from the background system
                        detail_color = tuple(min(255, max(20, int(c * 1.2))) for c in detail['color'])
                        
                        if detail['type'] == 'crystal':
                            pygame.draw.circle(self.terrain_cache, detail_color, 
                                             (minimap_x, minimap_y), 1)
                        elif detail['type'] == 'rock':
                            # Show some rocks, but not all to avoid clutter
                            if hash((detail['x'], detail['y'])) % 10 == 0:  # Show 10% of rocks
                                pygame.draw.circle(self.terrain_cache, detail_color, 
                                                 (minimap_x, minimap_y), 1)
        
        self.cache_dirty = False
    
    def world_to_minimap(self, world_x, world_y):
        """Convert world coordinates to minimap coordinates"""
        minimap_x = int((world_x + self.world_width) * self.scale_x)
        minimap_y = int((world_y + self.world_height) * self.scale_y)
        return minimap_x, minimap_y
    
    def minimap_to_world(self, minimap_x, minimap_y):
        """Convert minimap coordinates to world coordinates"""
        world_x = (minimap_x / self.scale_x) - self.world_width
        world_y = (minimap_y / self.scale_y) - self.world_height
        return world_x, world_y
    
    def draw(self, screen, player, enemies, camera=None):
        # Regenerate terrain cache if needed
        if self.cache_dirty and self.background_system:
            self._generate_terrain_cache()
        
        # Clear minimap
        self.surface.fill((0, 0, 0, 180))  # semi-transparent background
        
        # Draw terrain if available
        if self.terrain_cache:
            self.surface.blit(self.terrain_cache, (0, 0))
        
        # Draw world border
        pygame.draw.rect(self.surface, (100, 100, 100), (0, 0, self.width, self.height), 2)
        
        # Draw grid lines for better orientation (make them more subtle)
        grid_spacing = max(20, min(40, self.width // 8))
        for i in range(grid_spacing, self.width, grid_spacing):
            pygame.draw.line(self.surface, (20, 20, 25), (i, 0), (i, self.height))
        for i in range(grid_spacing, self.height, grid_spacing):
            pygame.draw.line(self.surface, (20, 20, 25), (0, i), (self.width, i))
        
        # Draw camera viewport first (behind other elements)
        if camera:
            # Calculate camera bounds in world space
            cam_left = camera.x - (camera.screen_width / camera.zoom) / 2
            cam_top = camera.y - (camera.screen_height / camera.zoom) / 2
            cam_right = camera.x + (camera.screen_width / camera.zoom) / 2
            cam_bottom = camera.y + (camera.screen_height / camera.zoom) / 2
            
            # Convert to minimap coordinates
            cam_x1, cam_y1 = self.world_to_minimap(cam_left, cam_top)
            cam_x2, cam_y2 = self.world_to_minimap(cam_right, cam_bottom)
            
            cam_w = cam_x2 - cam_x1
            cam_h = cam_y2 - cam_y1
            
            # Draw semi-transparent camera viewport area
            viewport_surf = pygame.Surface((cam_w, cam_h), pygame.SRCALPHA)
            viewport_surf.fill((0, 120, 255, 50))
            self.surface.blit(viewport_surf, (cam_x1, cam_y1))
            
            # Draw camera viewport border
            pygame.draw.rect(self.surface, (0, 150, 255), (cam_x1, cam_y1, cam_w, cam_h), 2)
        
        # Draw enemies
        for enemy in enemies:
            ex, ey = self.world_to_minimap(enemy.x, enemy.y)
            # Draw enemies within the minimap bounds
            if 0 <= ex <= self.width and 0 <= ey <= self.height:
                # Enemy dot with small outline for visibility
                pygame.draw.circle(self.surface, (100, 0, 0), (ex, ey), 4)
                pygame.draw.circle(self.surface, (255, 0, 0), (ex, ey), 3)
                
                # Optional: Add enemy direction indicator
                if hasattr(enemy, 'direction'):
                    end_x = ex + math.cos(enemy.direction) * 8
                    end_y = ey + math.sin(enemy.direction) * 8
                    pygame.draw.line(self.surface, (255, 100, 100), (ex, ey), (int(end_x), int(end_y)), 2)
        
        # Draw player (on top of everything)
        px, py = self.world_to_minimap(player.x, player.y)
        if 0 <= px <= self.width and 0 <= py <= self.height:
            # Player dot with outline for visibility
            pygame.draw.circle(self.surface, (0, 100, 0), (px, py), 6)
            pygame.draw.circle(self.surface, (0, 255, 0), (px, py), 5)
            pygame.draw.circle(self.surface, (100, 255, 100), (px, py), 3)
            
            # Optional: Add player direction indicator
            if hasattr(player, 'direction') or hasattr(player, 'angle'):
                direction = getattr(player, 'direction', getattr(player, 'angle', 0))
                end_x = px + math.cos(direction) * 10
                end_y = py + math.sin(direction) * 10
                pygame.draw.line(self.surface, (150, 255, 150), (px, py), (int(end_x), int(end_y)), 2)
        
        # Add minimap title
        if hasattr(pygame.font, 'Font'):
            try:
                font = pygame.font.Font(None, 20)
                title_text = font.render("MAP", True, (200, 200, 200))
                self.surface.blit(title_text, (5, 5))
            except:
                pass  # Font not available
        
        # Blit minimap to screen (top-right corner by default)
        if self._visible:
            screen.blit(self.surface, (screen.get_width() - self.width - self.margin, self.margin))
    
    def handle_click(self, screen_pos, camera=None):
        """Handle mouse clicks on minimap for navigation"""
        if not self._visible:
            return False
            
        screen_width = pygame.display.get_surface().get_width()
        minimap_rect = pygame.Rect(
            screen_width - self.width - self.margin,
            self.margin,
            self.width,
            self.height
        )
        
        if minimap_rect.collidepoint(screen_pos):
            # Convert click position to minimap local coordinates
            local_x = screen_pos[0] - minimap_rect.x
            local_y = screen_pos[1] - minimap_rect.y
            
            # Convert to world coordinates
            world_x, world_y = self.minimap_to_world(local_x, local_y)
            
            # Update camera position if camera is provided
            if camera:
                camera.x = world_x
                camera.y = world_y
            
            return True
        
        return False
    
    def set_visible(self, visible):
        """Toggle minimap visibility"""
        self._visible = visible
    
    def is_visible(self):
        """Check if minimap is visible"""
        return self._visible
    
    def refresh_terrain(self):
        """Force refresh of terrain cache"""
        self.cache_dirty = True
