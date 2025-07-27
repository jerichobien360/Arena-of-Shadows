import pygame
import sqlite3
import sys
import json
from datetime import datetime
from settings import *


# Initialize pygame
pygame.init()


class MapEditor:
    def __init__(self):
        # Map Editor Initialization
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Simple Map Editor")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Database Initialization
        self.init_database()
        
        # Grid data
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.current_tile = 1  # Default to grass
        self.map_name = "untitled"
        
        # UI elements
        self.save_button = pygame.Rect(10, GRID_HEIGHT + 10, 80, 30)
        self.load_button = pygame.Rect(100, GRID_HEIGHT + 10, 80, 30)
        self.clear_button = pygame.Rect(190, GRID_HEIGHT + 10, 80, 30)
        self.name_input = pygame.Rect(280, GRID_HEIGHT + 10, 150, 30)
        
        # Tile selector buttons
        self.tile_buttons = []
        for i, (tile_id, (name, color)) in enumerate(TILE_TYPES.items()):
            x = 10 + (i * 70)
            y = GRID_HEIGHT + 50
            self.tile_buttons.append((pygame.Rect(x, y, 60, 30), tile_id))
        
        # Message
        self.typing = False
        self.message = ""
        self.message_timer = 0

        # Game loop
        self.running = True

    # ====================== Class Method Properties ======================
    # DATABASE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def init_database(self):
        """Initialize SQLite database for storing maps"""
        self.conn = sqlite3.connect('maps.db')
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                grid_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def save_map(self, name):
        """Save current map to database"""
        try:
            grid_json = json.dumps(self.grid)
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO maps (name, grid_data, updated_at)
                VALUES (?, ?, ?)
            ''', (name, grid_json, datetime.now()))
            self.conn.commit()
            self.show_message(f"Map '{name}' saved successfully!", GREEN)
            return True
        except Exception as e:
            self.show_message(f"Error saving map: {str(e)}", RED)
            return False
    
    def load_map(self, name):
        """Load map from database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT grid_data FROM maps WHERE name = ?', (name,))
            result = cursor.fetchone()
            
            if result:
                self.grid = json.loads(result[0])
                self.map_name = name
                self.show_message(f"Map '{name}' loaded successfully!", GREEN)
                return True
            else:
                self.show_message(f"Map '{name}' not found!", RED)
                return False
        except Exception as e:
            self.show_message(f"Error loading map: {str(e)}", RED)
            return False
    
    def get_map_list(self):
        """Get list of saved maps"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT name, created_at FROM maps ORDER BY updated_at DESC')
        return cursor.fetchall()
    
    # MAP ENTITIES >>>>>>>>>>>>>>>>>>>>>>>>>>
    def show_message(self, text, color):
        """Show a temporary message"""
        self.message = text
        self.message_color = color
        self.message_timer = 180  # Show for 3 seconds at 60 FPS
    
    def draw_grid(self):
        """Draw the map grid"""
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                tile_type = self.grid[y][x]
                color = TILE_TYPES[tile_type][1]
                
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 1)
    
    def draw_ui(self):
        """Draw the user interface"""
        # Background for UI area
        ui_rect = pygame.Rect(0, GRID_HEIGHT, WINDOW_WIDTH, UI_HEIGHT)
        pygame.draw.rect(self.screen, LIGHT_GRAY, ui_rect)
        
        # Buttons
        pygame.draw.rect(self.screen, GREEN, self.save_button)
        pygame.draw.rect(self.screen, BLUE, self.load_button)
        pygame.draw.rect(self.screen, RED, self.clear_button)
        pygame.draw.rect(self.screen, WHITE, self.name_input)
        
        # Button text
        save_text = self.font.render("Save", True, BLACK)
        load_text = self.font.render("Load", True, WHITE)
        clear_text = self.font.render("Clear", True, WHITE)
        
        self.screen.blit(save_text, (self.save_button.x + 20, self.save_button.y + 5))
        self.screen.blit(load_text, (self.load_button.x + 20, self.load_button.y + 5))
        self.screen.blit(clear_text, (self.clear_button.x + 15, self.clear_button.y + 5))
        
        # Map name input
        name_text = self.font.render(self.map_name, True, BLACK)
        self.screen.blit(name_text, (self.name_input.x + 5, self.name_input.y + 5))
        
        # Input field border
        border_color = RED if self.typing else BLACK
        pygame.draw.rect(self.screen, border_color, self.name_input, 2)
        
        # Tile selector
        for rect, tile_id in self.tile_buttons:
            color = TILE_TYPES[tile_id][1]
            pygame.draw.rect(self.screen, color, rect)
            if tile_id == self.current_tile:
                pygame.draw.rect(self.screen, BLACK, rect, 3)
            else:
                pygame.draw.rect(self.screen, BLACK, rect, 1)
            
            # Tile name
            tile_name = TILE_TYPES[tile_id][0]
            text = self.small_font.render(tile_name, True, BLACK)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
        
        # Current tile info
        current_info = f"Current Tile: {TILE_TYPES[self.current_tile][0]}"
        info_text = self.font.render(current_info, True, BLACK)
        self.screen.blit(info_text, (450, GRID_HEIGHT + 15))
        
        # Instructions
        instructions = [
            "Left Click: Paint tile",
            "Right Click: Erase (set to empty)",
            "Click tile buttons to select",
            "Enter map name and Save/Load"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, BLACK)
            self.screen.blit(text, (450, GRID_HEIGHT + 40 + i * 15))
        
        # Message display
        if self.message_timer > 0:
            msg_text = self.font.render(self.message, True, self.message_color)
            self.screen.blit(msg_text, (10, 10))
            self.message_timer -= 1
    
    def get_grid_position(self, mouse_pos):
        """Convert mouse position to grid coordinates"""
        x, y = mouse_pos
        if x < GRID_WIDTH and y < GRID_HEIGHT:
            grid_x = x // CELL_SIZE
            grid_y = y // CELL_SIZE
            return grid_x, grid_y
        return None, None
    
    def clear_map(self):
        """Clear the entire map"""
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.show_message("Map cleared!", YELLOW)
    
    def handle_text_input(self, event):
        """Handle text input for map name"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.typing = False
            elif event.key == pygame.K_BACKSPACE:
                self.map_name = self.map_name[:-1]
            else:
                if len(self.map_name) < 20:  # Limit name length
                    self.map_name += event.unicode

    # ====================== Game Loop Properties =========================
    def run(self):
        """Main game loop"""
        while self.running:
            self._handle_event()
            
            self._render()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        self._cleanup()

    def _handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check UI buttons
                if self.save_button.collidepoint(mouse_pos):
                    if self.map_name.strip():
                        self.save_map(self.map_name.strip())
                    else:
                        self.show_message("Please enter a map name!", RED)
                
                elif self.load_button.collidepoint(mouse_pos):
                    if self.map_name.strip():
                        self.load_map(self.map_name.strip())
                    else:
                        self.show_message("Please enter a map name to load!", RED)
                
                elif self.clear_button.collidepoint(mouse_pos):
                    self.clear_map()
                
                elif self.name_input.collidepoint(mouse_pos):
                    self.typing = True
                    self.map_name = ""
                
                else:
                    # Check tile selector buttons
                    for rect, tile_id in self.tile_buttons:
                        if rect.collidepoint(mouse_pos):
                            self.current_tile = tile_id
                            break
                    else:
                        # Grid editing
                        self.typing = False
                        grid_x, grid_y = self.get_grid_position(mouse_pos)
                        if grid_x is not None and grid_y is not None:
                            if event.button == 1:  # Left click - paint
                                self.grid[grid_y][grid_x] = self.current_tile
                            elif event.button == 3:  # Right click - erase
                                self.grid[grid_y][grid_x] = 0
            
            elif event.type == pygame.MOUSEMOTION:
                # Allow painting while dragging
                if pygame.mouse.get_pressed()[0]:  # Left button held
                    mouse_pos = pygame.mouse.get_pos()
                    grid_x, grid_y = self.get_grid_position(mouse_pos)
                    if grid_x is not None and grid_y is not None:
                        self.grid[grid_y][grid_x] = self.current_tile
            
            # Handle text input
            if self.typing:
                self.handle_text_input(event)

    def _cleanup(self):
        # Cleanup
        self.conn.close()
        pygame.quit()
        sys.exit()

    def _render(self):
        # Draw everything
        self.screen.fill(GRAY)
        self.draw_grid()
        self.draw_ui()

# Run the map editor
if __name__ == "__main__":
    editor = MapEditor()
    editor.run()
