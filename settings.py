# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
GRID_SIZE = 16  # 16x16 grid for map editing
CELL_SIZE = 30
GRID_WIDTH = GRID_SIZE * CELL_SIZE
GRID_HEIGHT = GRID_SIZE * CELL_SIZE
UI_HEIGHT = 100

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Tile types
TILE_TYPES = {
    0: ("Empty", WHITE),
    1: ("Grass", GREEN),
    2: ("Dirt", BROWN),
    3: ("Water", BLUE),
    4: ("Wall", RED),
    5: ("Gold", YELLOW)
}
