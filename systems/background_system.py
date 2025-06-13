import pygame
import math
import random
from settings import *

class BackgroundSystem:
    def __init__(self, world_width=3000, world_height=3000):
        self.world_width = world_width
        self.world_height = world_height
        self.layers = []
        self.setup_background_layers()
    
    def setup_background_layers(self):
        """Setup multiple background layers for parallax effect"""
        # Layer 1: Deep background (slowest)
        self.layers.append({
            'type': 'stars',
            'parallax_factor': 10, #0.1
            'elements': self.generate_stars(100)
        })
        
        # Layer 2: Distant terrain
        self.layers.append({
            'type': 'distant_mountains',
            'parallax_factor': 30, #0.3
            'elements': self.generate_mountains()
        })
        
        # Layer 3: Ground tiles
        self.layers.append({
            'type': 'ground',
            'parallax_factor': 100.0, #1.0
            'elements': self.generate_ground_tiles()
        })
        
        # Layer 4: Foreground details
        self.layers.append({
            'type': 'details',
            'parallax_factor': 100.0, #1.0
            'elements': self.generate_details()
        })
    
    def generate_stars(self, count):
        """Generate stars for deep background"""
        stars = []
        for _ in range(count):
            star = {
                'x': random.randint(-self.world_width, self.world_width * 2),
                'y': random.randint(-self.world_height, self.world_height * 2),
                'size': random.randint(1, 3),
                'brightness': random.randint(100, 255),
                'twinkle_speed': random.uniform(0.5, 2.0),
                'twinkle_offset': random.uniform(0, math.pi * 2)
            }
            stars.append(star)
        return stars
    
    def generate_mountains(self):
        """Generate distant mountain silhouettes"""
        mountains = []
        for i in range(0, self.world_width * 2, 200):
            mountain = {
                'x': i - self.world_width,
                'y': random.randint(100, 300),
                'width': random.randint(150, 300),
                'height': random.randint(200, 400),
                'color': (20, 20, 40)
            }
            mountains.append(mountain)
        return mountains
    
    def generate_ground_tiles(self):
        """Generate ground tiles with variation"""
        tiles = []
        tile_size = 64
        
        for x in range(-self.world_width // tile_size, (self.world_width * 2) // tile_size):
            for y in range(-self.world_height // tile_size, (self.world_height * 2) // tile_size):
                world_x = x * tile_size
                world_y = y * tile_size
                
                # Create varied terrain
                noise_value = self.simple_noise(world_x * 0.01, world_y * 0.01)
                
                if noise_value < -0.3:
                    tile_type = 'water'
                    color = (20, 40, 80)
                elif noise_value < 0.1:
                    tile_type = 'grass'
                    color = (30, 60, 30)
                elif noise_value < 0.4:
                    tile_type = 'dirt'
                    color = (60, 40, 20)
                else:
                    tile_type = 'stone'
                    color = (50, 50, 50)
                
                # Add some random variation
                color = tuple(max(0, min(255, c + random.randint(-10, 10))) for c in color)
                
                tile = {
                    'x': world_x,
                    'y': world_y,
                    'size': tile_size,
                    'type': tile_type,
                    'color': color
                }
                tiles.append(tile)
        
        return tiles
    
    def generate_details(self):
        """Generate decorative details like rocks, plants, etc."""
        details = []
        
        for _ in range(500):
            detail_type = random.choice(['rock', 'plant', 'crystal'])
            
            if detail_type == 'rock':
                detail = {
                    'type': 'rock',
                    'x': random.randint(-self.world_width, self.world_width * 2),
                    'y': random.randint(-self.world_height, self.world_height * 2),
                    'size': random.randint(8, 20),
                    'color': (random.randint(60, 80), random.randint(60, 80), random.randint(60, 80))
                }
            elif detail_type == 'plant':
                detail = {
                    'type': 'plant',
                    'x': random.randint(-self.world_width, self.world_width * 2),
                    'y': random.randint(-self.world_height, self.world_height * 2),
                    'size': random.randint(5, 12),
                    'color': (random.randint(20, 50), random.randint(80, 120), random.randint(20, 50)),
                    'sway_offset': random.uniform(0, math.pi * 2)
                }
            else:  # crystal
                detail = {
                    'type': 'crystal',
                    'x': random.randint(-self.world_width, self.world_width * 2),
                    'y': random.randint(-self.world_height, self.world_height * 2),
                    'size': random.randint(6, 15),
                    'color': (random.randint(100, 200), random.randint(100, 200), random.randint(200, 255)),
                    'glow_phase': random.uniform(0, math.pi * 2)
                }
            
            details.append(detail)
        
        return details
    
    def simple_noise(self, x, y):
        """Simple noise function for terrain generation"""
        return (math.sin(x * 1.5) + math.sin(y * 1.3) + 
                math.sin(x * 0.7 + y * 0.8) * 0.5) / 2.5
    
    def update(self, dt):
        """Update animated background elements"""
        # Update stars twinkling
        for star in self.layers[0]['elements']:
            star['twinkle_offset'] += star['twinkle_speed'] * dt
        
        # Update plant swaying
        for detail in self.layers[3]['elements']:
            if detail['type'] == 'plant':
                detail['sway_offset'] += dt * 2
            elif detail['type'] == 'crystal':
                detail['glow_phase'] += dt * 3
    
    def render(self, screen, camera, current_time):
        """Render all background layers with parallax effect"""
        camera_bounds = camera.get_visible_bounds()
        
        for layer in self.layers:
            if layer['type'] == 'stars':
                self.render_stars(screen, camera, layer, current_time)
            elif layer['type'] == 'distant_mountains':
                self.render_mountains(screen, camera, layer)
            elif layer['type'] == 'ground':
                self.render_ground_tiles(screen, camera, layer, camera_bounds)
            elif layer['type'] == 'details':
                self.render_details(screen, camera, layer, camera_bounds, current_time)
    
    def render_stars(self, screen, camera, layer, current_time):
        """Render twinkling stars"""
        for star in layer['elements']:
            # Apply parallax
            parallax_x = star['x'] * layer['parallax_factor']
            parallax_y = star['y'] * layer['parallax_factor']
            
            screen_x, screen_y = camera.world_to_screen(parallax_x, parallax_y)
            
            # Only render if on screen
            if -50 < screen_x < SCREEN_WIDTH + 50 and -50 < screen_y < SCREEN_HEIGHT + 50:
                # Calculate twinkling brightness
                twinkle = math.sin(star['twinkle_offset']) * 0.3 + 0.7
                brightness = int(star['brightness'] * twinkle)
                
                color = (brightness, brightness, brightness)
                pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), star['size'])
    
    def render_mountains(self, screen, camera, layer):
        """Render distant mountains"""
        for mountain in layer['elements']:
            # Apply parallax
            parallax_x = mountain['x'] * layer['parallax_factor']
            parallax_y = mountain['y'] * layer['parallax_factor']
            
            screen_x, screen_y = camera.world_to_screen(parallax_x, parallax_y)
            
            # Only render if on screen
            if (screen_x + mountain['width'] > 0 and screen_x < SCREEN_WIDTH and
                screen_y + mountain['height'] > 0 and screen_y < SCREEN_HEIGHT):
                
                # Draw mountain as a triangle
                points = [
                    (screen_x, screen_y + mountain['height']),
                    (screen_x + mountain['width'] // 2, screen_y),
                    (screen_x + mountain['width'], screen_y + mountain['height'])
                ]
                pygame.draw.polygon(screen, mountain['color'], points)
    
    def render_ground_tiles(self, screen, camera, layer, camera_bounds):
        """Render ground tiles efficiently"""
        left, top, right, bottom = camera_bounds
        
        for tile in layer['elements']:
            # Only render tiles that are visible
            if (tile['x'] + tile['size'] > left and tile['x'] < right and
                tile['y'] + tile['size'] > top and tile['y'] < bottom):
                
                screen_x, screen_y = camera.world_to_screen(tile['x'], tile['y'])
                size = int(tile['size'] * camera.zoom)
                
                rect = pygame.Rect(screen_x, screen_y, size, size)
                pygame.draw.rect(screen, tile['color'], rect)
                
                # Add border for stone tiles
                if tile['type'] == 'stone':
                    border_color = tuple(max(0, c - 20) for c in tile['color'])
                    pygame.draw.rect(screen, border_color, rect, 1)
    
    def render_details(self, screen, camera, layer, camera_bounds, current_time):
        """Render decorative details"""
        left, top, right, bottom = camera_bounds
        
        for detail in layer['elements']:
            # Only render details that are visible
            if (detail['x'] + detail['size'] > left and detail['x'] < right and
                detail['y'] + detail['size'] > top and detail['y'] < bottom):
                
                screen_x, screen_y = camera.world_to_screen(detail['x'], detail['y'])
                size = int(detail['size'] * camera.zoom)
                
                if detail['type'] == 'rock':
                    pygame.draw.circle(screen, detail['color'], (int(screen_x), int(screen_y)), size)
                    # Add highlight
                    highlight_color = tuple(min(255, c + 30) for c in detail['color'])
                    pygame.draw.circle(screen, highlight_color, (int(screen_x - size//3), int(screen_y - size//3)), size//3)
                
                elif detail['type'] == 'plant':
                    # Swaying plant
                    sway = math.sin(detail['sway_offset']) * 2
                    plant_x = int(screen_x + sway)
                    plant_y = int(screen_y)
                    
                    # Draw stem
                    stem_color = tuple(max(0, c - 30) for c in detail['color'])
                    pygame.draw.line(screen, stem_color, (plant_x, plant_y), (plant_x, plant_y - size), 2)
                    
                    # Draw leaves
                    pygame.draw.circle(screen, detail['color'], (plant_x, plant_y - size), size//2)
                
                elif detail['type'] == 'crystal':
                    # Glowing crystal
                    glow_intensity = (math.sin(detail['glow_phase']) + 1) * 0.5
                    glow_color = tuple(int(c * (0.7 + glow_intensity * 0.3)) for c in detail['color'])
                    
                    # Draw crystal as diamond shape
                    points = [
                        (screen_x, screen_y - size),
                        (screen_x + size//2, screen_y),
                        (screen_x, screen_y + size),
                        (screen_x - size//2, screen_y)
                    ]
                    pygame.draw.polygon(screen, glow_color, points)
                    
                    # Add inner glow
                    inner_points = [
                        (screen_x, screen_y - size//2),
                        (screen_x + size//4, screen_y),
                        (screen_x, screen_y + size//2),
                        (screen_x - size//4, screen_y)
                    ]
                    inner_color = tuple(min(255, c + 50) for c in glow_color)
                    pygame.draw.polygon(screen, inner_color, inner_points)
                
                else:
                    # Simple dot for very small crystals
                    pygame.draw.circle(screen, glow_color, (int(screen_x), int(screen_y)), size)
    
    def get_world_bounds(self):
        """Get the bounds of the world"""
        return (-self.world_width, -self.world_height, self.world_width * 2, self.world_height * 2)
